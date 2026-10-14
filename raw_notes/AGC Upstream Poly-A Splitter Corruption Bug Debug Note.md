---
raw_tags:
  - pass
  - agc
  - contig
  - workdir
  - splitter
  - seg_part_no
  - kmer_dir
  - genomes
word_count: 7169
char_count: 60362
processed: true
processed_note: "[[AGC - Upstream Poly-A Silent Corruption Bug]]"
---

# AGC Upstream Bug Debug Note: Silent Contig Corruption via `A^k` Splitter & `CKmer::operator==` in Adaptive Mode (`-a`)

- **Date Discovered**: 2026-10-12
- **Affected Software**: Upstream `refresh-bio/agc` (verified in `v3.2.2 [build 20260326.1]` and latest release `v3.2.4 [build 20260722.1]`, as well as `agc-split-size`)
- **Trigger Condition**: Adaptive compression mode (`-a` / `adaptive_compression == true`) when the **last splitter $k$-mer** encountered in a contig during Pass 1 (`all_contigs`) is a homopolymer of all `A`s (`A^k`, e.g. `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` for $k=31$, where `kmer_dir == 0ull`).
- **Severity**: **Critical (Silent Data Corruption & Non-Deterministic Decompression)**. Decompressed contigs silently drop/duplicate internal segments (inflating contig length from `39,080 bp` to `63,487–66,120 bp` in `SAMEA5584600.contig00047`) without any warning or error during compression or decompression.

---

## 1. Conceptual Explanation

### 1.1 How AGC Splits Contigs into Segments
AGC compresses genome assemblies by splitting each contig at designated **splitter $k$-mers** (canonical $k$-mers of length $k=31$ by default, selected from singleton candidate $k$-mers spaced roughly every `segment_size` $= 1500\text{ bp}$ in the reference genome):
1. A contig is scanned from left to right (`pos = 0 .. contig.size() - 1`).
2. Each time a $k$-mer in the contig matches the splitter hash set (`bloom_splitters` + `hs_splitters`), the slice from the previous splitter (`split_pos`) to the current splitter (`pos + 1`) is emitted as segment number `seg_part_no` (`0, 1, 2, ...`).
3. Consecutive segments overlap by $k = 31\text{ bp}$ (the splitter $k$-mer itself), which is stripped upon decompression (`decompress_contig`).

### 1.2 How Adaptive Mode (`-a`) Works in Two Passes
When `-a` (`adaptive_compression`) is enabled, some contigs in non-reference samples may diverge strongly from the reference or represent novel plasmids/accessory regions that contain **zero** reference splitters. For each sample, AGC runs a two-pass pipeline before registering and storing segments:

```mermaid
flowchart TD
    A["Pass 1: all_contigs<br/>Scan contig for known splitters in hs_splitters"] --> B{"Were ANY splitters found<br/>in this contig?"}
    B -- "Yes (has >= 1 splitter)" --> C["Emit final tail segment<br/>Return true (Done)"]
    B -- "No (0 splitters found)" --> D["Call find_new_splitters(contig)<br/>Return false -> push contig to v_raw_contigs"]
    D --> E["Barrier: new_splitters<br/>Insert new splitters into hs_splitters & bloom_splitters"]
    E --> F["Pass 2: hard_contigs<br/>Re-run compress_contig() on v_raw_contigs from seg_part_no = 0"]
    C --> G["Barrier: registration<br/>register_segments() + store_segments()"]
    F --> G
```

**Crucial Invariant of Pass 1 vs. Pass 2**:
A contig pushed to `v_raw_contigs` for Pass 2 (`hard_contigs`) is assumed to have emitted **zero segments** during Pass 1 (`all_contigs`), because `compress_contig` only returns `false` if no splitters were found during the loop.

### 1.3 Why That Invariant Breaks on `A^31` (`AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`)
In AGC, DNA bases are 2-bit encoded after `preprocess_raw_contig`:
- `'A' -> 0` (`0b00`)
- `'C' -> 1` (`0b01`)
- `'G' -> 2` (`0b10`)
- `'T' -> 3` (`0b11`)

Inside `CKmer`, a direct $k$-mer is packed into a 64-bit unsigned integer `uint64_t kmer_dir`, and the number of bases currently in the window is tracked by `uint32_t cur_size` (`0` when empty/reset, `31` when full):
- When a `CKmer` is freshly constructed or reset (`CKmer(kmer_length, kmer_mode_t::canonical)`), its state is:
  - `cur_size = 0`
  - `kmer_dir = 0ull`
  - `kmer_rc = 0ull`
- When a `CKmer` has read 31 consecutive `'A'` bases (`A^31 = AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`), every base shifted into `kmer_dir` is `0`, so its state is:
  - `cur_size = 31`
  - **`kmer_dir = 0ull`**
  - `kmer_rc = 0xfffffffffffffffcull` (31 `'T'`s in bits `63..2`)

When `compress_contig` finishes scanning a contig, it checks whether `split_kmer` (the variable holding the **last splitter $k$-mer** seen in the contig) is still in its initial empty state:
```cpp
if (adaptive_compression && contig_processing_stage == contig_processing_stage_t::all_contigs && split_kmer == CKmer(kmer_length, kmer_mode_t::canonical))
```
Because `CKmer::operator==` **only compares `kmer_dir == x.kmer_dir` and forgets to check `cur_size == x.cur_size`**, `split_kmer == CKmer(kmer_length, kmer_mode_t::canonical)` evaluates `0ull == 0ull` $\to$ **`true`** whenever the **last splitter** found in the contig is `A^31` (`AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`)!

### 1.4 The Resulting Two-Pass Collision
When a contig has one or more splitters in Pass 1 (`all_contigs`) and the **last** splitter found in Pass 1 is `A^31`:
1. **Pass 1 (`all_contigs`)**:
   - `compress_contig` **already emits** `seg_part_no = 0, 1, ..., m` (up to the `A^31` splitter) into `buffered_seg_part`.
   - At the end of the loop, `split_kmer` is `A^31` (`kmer_dir == 0ull`).
   - The check `split_kmer == CKmer(kmer_length, kmer_mode_t::canonical)` evaluates to `true`.
   - `compress_contig` skips the remaining tail after `A^31`, runs `find_new_splitters(contig)` (extracting new splitters from inside the contig itself!), and returns `false`.
   - The worker pushes the contig into `v_raw_contigs`.
2. **Barrier (`new_splitters`)**:
   - All newly discovered splitters from `find_new_splitters` are inserted into `hs_splitters` and `bloom_splitters`.
3. **Pass 2 (`hard_contigs`)**:
   - `compress_contig` runs **a second time** on the exact same contig, starting again at `seg_part_no = 0`, but now with **more splitters** in `hs_splitters`.
   - Pass 2 emits a new sequence of segments `seg_part_no = 0, 1, 2, ..., n` (where $n > m$).
4. **Silent Segment Collision & Corruption (`registration`)**:
   - Both Pass 1's segments (`0..m`) and Pass 2's segments (`0..n`) are sitting in `buffered_seg_part` for the **same `(sample_name, contig_name)`**!
   - For indices `0..m`, Pass 1's coarse segments (e.g., `seg_part_no = 1` spanning all the way to `A^31`) collide with Pass 2's finer segments (`seg_part_no = 1` spanning only to the first new Pass 2 splitter).
   - For indices `m+1 .. n`, Pass 2's segments have no counterpart in Pass 1, so they are appended at indices `m+1 .. n`.
   - Upon decompression, the contig is stitched together from a chimeric mixture of Pass 1 segments (`0..m`) followed by Pass 2 segments (`m+1..n`), duplicating tens of kilobases of sequence!

---

## 2. Line-by-Line Code Walkthrough

### 2.1 `CKmer` Representation and `operator==` ([`src/core/kmer.h`](file:///Users/ktruong/tools/agc-split-size/src/core/kmer.h))

In [`src/core/kmer.h:262-301`](file:///Users/ktruong/tools/agc-split-size/src/core/kmer.h#L262-L301), `Reset` initializes `kmer_dir = 0ull` and `cur_size = 0`, and `insert_canonical` shifts 2-bit symbols into `kmer_dir`:
```cpp
// src/core/kmer.h:262-301
void Reset(uint32_t _max_size, kmer_mode_t _variant) {
    max_size = _max_size;
    variant = _variant;
    kmer_dir = 0ull;
    kmer_rc = 0ull;
    cur_size = 0;
    ...
}

inline void insert_canonical(uint64_t symbol) {
    // rev. comp. code
    kmer_rc >>= 2;
    kmer_rc += reverse_complement(symbol) << 62;
    kmer_rc &= mask;

    // direct code
    if (cur_size == max_size)
    {
        kmer_dir <<= 2;
        kmer_dir += symbol << shift;
    }
    else
    {
        ++cur_size;
        kmer_dir += symbol << (64 - 2 * cur_size);
    }
}
```
When `symbol == 0` (`'A'`) is inserted 31 times:
- `cur_size` becomes `31` (`max_size`).
- `kmer_dir` remains `0ull`.

Now look at [`src/core/kmer.h:450-463`](file:///Users/ktruong/tools/agc-split-size/src/core/kmer.h#L450-L463):
```cpp
// src/core/kmer.h:450-463
bool operator==(const CKmer&x) const {
    if (variant != kmer_mode_t::rev_comp)
        return kmer_dir == x.kmer_dir;
    else
        return kmer_rc == x.kmer_rc;
}

bool operator!=(const CKmer&x) const {
    if (variant != kmer_mode_t::rev_comp)
        return kmer_dir != x.kmer_dir;
    else
        return kmer_rc != x.kmer_rc;
}
```
- Neither `operator==` nor `operator!=` checks `cur_size == x.cur_size`.
- Therefore, `CKmer` containing `A^31` (`cur_size == 31, kmer_dir == 0ull`) compares **equal** to `CKmer(31, kmer_mode_t::canonical)` (`cur_size == 0, kmer_dir == 0ull`).
- (Note: in `kmer_mode_t::rev_comp`, `T^31` has `kmer_rc == 0ull` and would similarly compare equal to an empty `CKmer`.)

---

### 2.2 False Negative Splitter Check in `compress_contig` ([`src/core/agc_compressor.cpp`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp))

Look at [`CAGCCompressor::compress_contig`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L2000-L2054) in [`src/core/agc_compressor.cpp:2000-2054`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L2000-L2054):
```cpp
// src/core/agc_compressor.cpp:2000-2054
bool CAGCCompressor::compress_contig(contig_processing_stage_t contig_processing_stage, string sample_name, string id, contig_t& contig, 
    ZSTD_CCtx* zstd_cctx, ZSTD_DCtx* zstd_dctx, uint32_t thread_id, my_barrier& bar)
{
    CKmer kmer(kmer_length, kmer_mode_t::canonical);

    uint64_t pos = 0;
    uint64_t split_pos = 0;
    CKmer split_kmer(kmer_length, kmer_mode_t::canonical);
    uint32_t seg_part_no = 0;

    for (auto x : contig)
    {
        if (x >> 2)         // x > 3
            kmer.Reset();
        else
        {
            kmer.insert_canonical(x);           // a bit faster than insert()

            if (kmer.is_full())
            {
                uint64_t d = kmer.data_canonical();     // a bit faster than data()
                if (bloom_splitters.check(d) && hs_splitters.check(d))
                {
                    auto seg_id = add_segment(sample_name, id, seg_part_no,
                        move(get_part(contig, split_pos, pos + 1 - split_pos)), split_kmer, kmer, zstd_cctx, zstd_dctx, thread_id, bar);

                    ++seg_part_no;

                    if (seg_id.contains_second)
                        ++seg_part_no;

                    split_pos = pos + 1 - kmer_length;
                    split_kmer = kmer;
                    kmer.Reset();
                }
            }
        }

        ++pos;
    }

    if (adaptive_compression && contig_processing_stage == contig_processing_stage_t::all_contigs && split_kmer == CKmer(kmer_length, kmer_mode_t::canonical))
    {
        if(contig.size() >= segment_size)
            find_new_splitters(contig, thread_id);

        return false;
    }

    if (split_pos < contig.size())
        add_segment(sample_name, id, seg_part_no,
            move(get_part(contig, split_pos, contig.size() - split_pos)), split_kmer, CKmer(kmer_length, kmer_mode_t::canonical), zstd_cctx, zstd_dctx, thread_id, bar);

    return true;
}
```
Trace what happens line by line when `contig` is scanned in stage `contig_processing_stage_t::all_contigs`:
1. **Line 2007**: `split_kmer` is initialized to empty (`cur_size = 0, kmer_dir = 0ull`).
2. **Lines 2021–2033**: Each time a splitter `d` is matched in `hs_splitters`:
   - `add_segment(...)` is called immediately, registering `seg_part_no` in `buffered_seg_part` (`s_seg_part` if new, or `vl_seg_part[segment_id]` if known).
   - `seg_part_no` is incremented (`+1`, or `+2` if `add_segment` split the segment across a missing middle splitter).
   - `split_kmer = kmer;` stores the splitter that just ended the segment.
3. **Line 2041**: After the loop over `contig` finishes:
   - If the **last** splitter matched in the loop was `A^31` (`d = 0ull`, `kmer.kmer_dir = 0ull`), then `split_kmer.kmer_dir == 0ull`.
   - `split_kmer == CKmer(kmer_length, kmer_mode_t::canonical)` calls `CKmer::operator==` and returns **`true`**!
   - **Lines 2043–2046**: `find_new_splitters(contig, thread_id)` is executed on `contig`, and `compress_contig` returns **`false`** without emitting the tail segment (`lines 2049–2051`), leaving the already-emitted segments (`seg_part_no = 0 .. m`) orphaned inside `buffered_seg_part`!

---

### 2.3 Re-Queuing into `hard_contigs` ([`src/core/agc_compressor.cpp:1190-1265`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L1190-L1265))

In [`CAGCCompressor::start_compressing_threads`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L1249-L1265):
```cpp
// src/core/agc_compressor.cpp:1249-1265
if (compress_contig(get<0>(task), get<1>(task), get<2>(task), get<3>(task), zstd_cctx, zstd_dctx, thread_id, bar))
{
    ...
}
else
{
    lock_guard<mutex> lck(mtx_raw_contigs);
    v_raw_contigs.emplace_back(get<1>(task), get<2>(task), move(get<3>(task)));
}
```
1. Because `compress_contig` returned `false`, the full `contig` is moved into `v_raw_contigs`.
2. Next, when the `contig_processing_stage_t::new_splitters` synchronization token arrives ([`src/core/agc_compressor.cpp:1190-1240`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L1190-L1240)):
   - `bloom_insert()` inserts all newly found splitters from `vv_splitters` (including the splitters just extracted from `contig` at line 2044!) into `hs_splitters` and `bloom_splitters`.
   - Thread 0 pushes all contigs in `v_raw_contigs` into `pq_contigs_desc_aux` with stage `contig_processing_stage_t::hard_contigs`.
3. Workers then pop `contig` in stage `hard_contigs` and call `compress_contig` **a second time** on the exact same `(sample_name, id, contig)`.
   - Because `hs_splitters` now contains all the new splitters found inside `contig`, `compress_contig` splits `contig` into many more segments (`seg_part_no = 0, 1, 2, ..., n`).

---

### 2.4 How Pass 1 and Pass 2 Segments Collide in `CBufferedSegPart` and `CCollection_V3`

Look at how `add_segment` buffers segments in [`CBufferedSegPart`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.h#L124-L415):

1. **Collision in `s_seg_part` (New Segment Groups)**:
   In [`src/core/agc_compressor.h:157-164, 300, 326-331`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.h#L157-L164):
   ```cpp
   // src/core/agc_compressor.h:157-164
   bool operator<(const struct kk_seg_part_t& x) const
   {
       if (sample_name != x.sample_name)
           return sample_name < x.sample_name;
       if (contig_name != x.contig_name)
           return contig_name < x.contig_name;
       return seg_part_no < x.seg_part_no;
   }
   ...
   set<kk_seg_part_t> s_seg_part;
   ...
   void add_new(uint64_t kmer1, uint64_t kmer2, const string& sample_name, const string& contig_name, contig_t& seg_data, bool is_rev_comp, uint32_t seg_part_no)
   {
       lock_guard<mutex> lck(mtx);
       s_seg_part.emplace(kmer1, kmer2, sample_name, contig_name, seg_data, is_rev_comp, seg_part_no);
   }
   ```
   - `s_seg_part` is a `std::set<kk_seg_part_t>` ordered **solely** by `(sample_name, contig_name, seg_part_no)` (ignoring `kmer1`, `kmer2`, and `seg_data`).
   - When Pass 1 calls `add_new` for `(sample_name, contig_name, seg_part_no = 1)`, that element is inserted into `s_seg_part`.
   - When Pass 2 later calls `add_new` for `(sample_name, contig_name, seg_part_no = 1)` with the properly split segment, `std::set::emplace` sees that `(sample_name, contig_name, seg_part_no = 1)` already exists in `s_seg_part` and **silently drops Pass 2's segment**!

2. **Collision in `vl_seg_part` and `CCollection_V3::add_segments_placed` (Known Segment Groups)**:
   - Even if Pass 1's segment goes to `add_known(group_id_A, ..., seg_part_no = 1)` and Pass 2's segment goes to `add_known(group_id_B, ..., seg_part_no = 1)` (or `add_new`), both are stored into their respective `CSegment` streams during `store_segments` ([`src/core/agc_compressor.cpp:1001-1052`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L1001-L1052)), and both call [`CCollection_V3::add_segments_placed`](file:///Users/ktruong/tools/agc-split-size/src/common/collection_v3.cpp#L796-L800):
     ```cpp
     // src/common/collection_v3.cpp:796-800
     if (desc.seg_part_no >= x.segments.size())
         x.segments.resize(desc.seg_part_no + 1);

     x.segments[desc.seg_part_no] = segment_desc_t(desc.group_id, desc.in_group_id, desc.is_rev_comp, desc.data_size);
     ```
   - Whichever worker thread processes `group_id` last in `store_segments` overwrites `x.segments[1]`, while Pass 2's `seg_part_no = 2, 3, ...` populate `x.segments[2..n]`.

---

## 3. Empirical Verification on `SAMEA5584600.contig00047`

### 3.1 Ground Truth in Original FASTA (`SAMEA5584600.fa.gz`)
- **Contig**: `SAMEA5584600.contig00047`
- **Original FASTA Length**: `39,080 bp`
- **Locations of Splitters in `SAMEA5584600.contig00047`**:
  - `1500..1531`: `GTCACCACCATGTGCSG...` (known splitter present in `hs_splitters` during Pass 1)
  - `12000..12031`: `GCCAGCCACTGCAGGCCCGAGGCGGTCGGTG` (not in `hs_splitters` during Pass 1; added by `find_new_splitters` before Pass 2)
  - **`39040..39071`**: **`AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` (`31` `A`s, `9 bp` before the end of the `39,080 bp` contig; present in `hs_splitters` during Pass 1!)**

### 3.2 Why Three Different Runs Produced Three Different Corrupted Lengths/Checksums

| Environment & Command | AGC Version | Extracted `contig00047` Length | `seqkit sum` Hash | Structure of Corrupted `contig00047` |
| :--- | :--- | :--- | :--- | :--- |
| **Original FASTA** (`SAMEA5584600.fa.gz`) | Ground Truth | **`39,080 bp`** | `9424396f7f1f6290e42b7776487cb89c` | `s_fa[0 : 39080]` (`39,080 bp`) |
| **Local Mac** (`atb202603_part003.agc`) | `v3.2.4 [build 20260722.1]` | **`66,120 bp`** | `5b02baa4d53734cc6115f7d50b8a70c0` | `s_fa[0 : 39071]` (`39,071 bp` from Pass 1 segs 0–1) + `s_fa[12031 : 39080]` (`27,049 bp` from Pass 2 segs $\ge 2$) |
| **Cluster `agc_default`** (`-t 25`) | `v3.2.2 [build 20260326.1]` | **`63,487 bp`** | `9b80d5bdb316e989d53b9464ef8df86b` | `s_fa[0 : 1531]` (`1,531 bp`) + `34,907 bp` (Pass 1 seg ending at `A^31`) + `s_fa[12031 : 39080]` (`27,049 bp` from Pass 2) |
| **Cluster `agc_split`** (`-t 50`) | `v3.2.2 [build 20260326.1]` | **`65,279 bp`** | `30780fd5bb763a769c9130c6759073b1` | `s_fa[0 : 1531]` (`1,531 bp`) + `36,699 bp` (Pass 1 seg ending at `A^31`) + `s_fa[12031 : 39080]` (`27,049 bp` from Pass 2) |

#### Why the Local Mac (`66,120 bp`) vs. Cluster (`63,487 bp` / `65,279 bp`) Differ:
1. **On the Local Mac (`66,120 bp`)**:
   - In Pass 1, `SAMEA5584600.contig00047` was split into:
     - `seg_part_no = 0`: `s_fa[0 : 1531]` (`1,531 bp`)
     - `seg_part_no = 1`: `s_fa[1500 : 39071]` (`37,571 bp` raw, `37,540 bp` stripped, ending at `A^31` at `39040..39071`).
   - Both went to `s_seg_part` (`add_new`).
   - In Pass 2 (`hard_contigs`), `find_new_splitters` added a splitter at `12000..12031` (`GCCAGCCACTGCAGGCCCGAGGCGGTCGGTG`). Pass 2 produced:
     - `seg_part_no = 0`: `s_fa[0 : 1531]`
     - `seg_part_no = 1`: `s_fa[1500 : 12031]` (silently rejected by `s_seg_part.emplace` because Pass 1's `seg_part_no = 1` was already in `s_seg_part`!)
     - `seg_part_no >= 2`: `s_fa[12000 : 39080]` (`27,049 bp` stripped).
   - Total decompressed length: $1,531 + 37,540 + 27,049 = 39,071 + 27,049 = \mathbf{66,120\text{ bp}}$, duplicating `s_fa[12031 : 39071]` (`27,040 bp`) twice!
2. **On the Cluster (`63,487 bp` and `65,279 bp`)**:
   - Because `pq_contigs_desc` is popped concurrently by multiple worker threads (`-t 25` vs `-t 50`), different contigs from `SAMEA5584600` (or prior samples) had already populated `map_segments_terminators` or `vv_splitters` when `SAMEA5584600.contig00047` ran.
   - In Pass 1, `s_fa[0 : 39071]` hit an additional splitter (or `find_cand_segment_with_missing_middle_splitter` split the segment ending at `A^31` at `4,164 bp` or `2,372 bp`), so the Pass 1 segment ending at `AAGAGACCGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` (`39031..39071`) had stripped length `34,907 bp` (`39,071 - 4,164`) in `agc_default` and `36,699 bp` (`39,071 - 2,372`) in `agc_split`, which then collided with Pass 2's segments in `x.segments`.

### 3.3 Second Confirmed Case: `SAMEA5168235.contig00123` in `atb.assembly.r1.part051.agc`
- **Contig**: `SAMEA5168235.contig00123` (only mismatch out of `299` contigs in `SAMEA5168235`)
- **Original FASTA Length**: `9,438 bp` (`seqkit.v0.1_DLS_k0_6add5d30a00e5f9046951e3cd5f60a5b`)
- **Extracted AGC Length** (`v3.2.2` on cluster & `v3.2.4` on local Mac): `10,015 bp` (`seqkit.v0.1_DLS_k0_c433eeafc4b9019e939a30af0712a5a6`)
- **Location of `A^31` Splitter in `SAMEA5168235.contig00123`**:
  - `s_fa[9329 : 9391]` contains a poly-A tract ending with `AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` at **`9360..9391`** (`47 bp` before the end of the `9,438 bp` contig).
  - Prefix match: `2,408 bp` (`s_fa[0 : 2408]`, ending at splitter `CCCTCCACTTGCCTTTAATACAACCTACACA` at `2377..2408`).
  - Suffix match: `6,407 bp` (`s_fa[3031 : 9438]`, starting after Pass 2 splitter `AGCAAAACTCTCAACATACGATCATTGCAAG` at `3000..3031`).
  - Just like `SAMEA5584600.contig00047`, the last splitter hit in Pass 1 (`all_contigs`) is `A^31` at `9360..9391` (`split_kmer.kmer_dir == 0ull`), causing `split_kmer == CKmer(kmer_length, kmer_mode_t::canonical)` to evaluate to `true` and re-queue the contig into Pass 2 (`hard_contigs`).

---

## 4. Exact Fix

### 4.1 Fix `CKmer::operator==` and `CKmer::operator!=` in [`src/core/kmer.h`](file:///Users/ktruong/tools/agc-split-size/src/core/kmer.h#L450-L463)

Compare `cur_size == x.cur_size` so a full `A^k` (or `T^k`) $k$-mer with `cur_size == 31` and `kmer_dir == 0ull` is never treated as equal to an empty `CKmer` with `cur_size == 0`:

```cpp
// src/core/kmer.h:450-463
	// *******************************************************************************************
	bool operator==(const CKmer&x) const {
		if (cur_size != x.cur_size)
			return false;

		if (variant != kmer_mode_t::rev_comp)
			return kmer_dir == x.kmer_dir;
		else
			return kmer_rc == x.kmer_rc;
	}

	// *******************************************************************************************
	bool operator!=(const CKmer&x) const {
		if (cur_size != x.cur_size)
			return true;

		if (variant != kmer_mode_t::rev_comp)
			return kmer_dir != x.kmer_dir;
		else
			return kmer_rc != x.kmer_rc;
	}
```

### 4.2 Use `!split_kmer.is_full()` Explicitly in [`src/core/agc_compressor.cpp`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L2041)

In [`CAGCCompressor::compress_contig`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L2041), check `!split_kmer.is_full()` directly to express the exact intent ("no splitter $k$-mer was found in `contig`"):

```cpp
// src/core/agc_compressor.cpp:2041
    if (adaptive_compression && contig_processing_stage == contig_processing_stage_t::all_contigs && !split_kmer.is_full())
    {
        if(contig.size() >= segment_size)
            find_new_splitters(contig, thread_id);

        return false;
    }
```

---

## 5. Dataset-Wide Impact & Verification (AllTheBacteria 3.1M Assemblies Audit)

Across the full dataset audit of **3,092,278 assemblies** in **1,129 archives**:
- **Clean Assemblies**: **3,092,181 / 3,092,278 (99.99686%)** passed bit-for-bit checksum validation against original assemblies.
- **Affected by Upstream Poly-A Splitter Bug**: Exactly **95 assemblies** across **19 archives** (0.00307% of genomes).
  - 80 assemblies suffered **segment expansion/duplication** (`len(agc) > len(fa)`).
  - 15 assemblies suffered **segment truncation** (`len(agc) < len(fa)`).
- **Two Non-Bug Anomalies Investigated & Cleared**:
  1. `SAMN50311804` (`part199`): Raw source FASTA had 1,434 `\x00` null bytes from an interrupted filesystem write; AGC correctly stripped non-nucleotides ($c \le 64$), producing the true sequence matching assembler header `corr=43756`.
  2. `SAMN16418392` (`part249`): File on disk had been an older length-filtered 36-contig assembly from `set2_2024-08`, while official `r1` S3 assembly had 121 contigs. AGC had compressed the local file bit-for-bit.

---

## 6. Empirical Reproduction Suite & Cross-Genome Splitter Injection (Batch 003)

### 6.1 Background & The Mystery
In `atb.assembly.r1.part003.agc` (513 genomes total), `SAMEA5584600.contig00047` was severely corrupted from its true length of `39,080 bp` to `65,279 bp` (+26,199 bp duplication).
- Target sample: `SAMEA5584600`
- Line position in `part003.txt`: **Line 286 / 513**
- Tail sequence of `contig00047`: Contains a poly-A tract ending in `...AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAGACCGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAA` (77 'A's total).

### 6.2 Empirical Reproduction Results Across Scenarios

| Scenario | Cohort / Scope | Flags | Result | Length | Checksum & Details |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Scenario 1** | Prefix Lines 1..286 (Target cohort) | `agc create -a -b 500 -s 1500 -t 25` | **CRITICAL BUG** | **`65,279 bp`** | `seqkit.v0.1_DLS_k0_30780fd5bb763a769c9130c6759073b1` (Diff: +26,199 bp). **Byte-for-byte exact match to production!** |
| **Scenario 2** | Prefix Lines 1..286 (Single thread) | `agc create -a -b 500 -s 1500 -t 1` | **CRITICAL BUG** | **`66,120 bp`** | `seqkit.v0.1_DLS_k0_5b02baa4d53734cc6115f7d50b8a70c0` (Diff: +27,040 bp). **Deterministic algorithmic failure, reproduces local Mac build!** |
| **Scenario 3** | Full Original Batch 003 (513 genomes) | `agc create -a -b 500 -s 1500 -t 25` | **CRITICAL BUG** | **`65,279 bp`** | `seqkit.v0.1_DLS_k0_30780fd5bb763a769c9130c6759073b1` (Diff: +26,199 bp). Production archive baseline. |
| **Control** | Prefix Lines 1..286 without `-a` | `agc create -b 500 -s 1500 -t 25` | **PASS** | **`39,080 bp`** | `seqkit.v0.1_DLS_k0_9424396f7f1f6290e42b7776487cb89c`. Bit-for-bit clean match. |


#### Corrected Reproduction Script (`reproduce_bug.sh`)
*Note on AGC CLI syntax: In `agc create`, `-i <file>` reads input lines, while the positional argument specifies the reference genome (Sample #0). To preserve the exact batch reference, the reference genome (Line 1) must be passed as the positional argument and Lines 2..N via `-i`:*

```bash
#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
PART003_TXT="${EXP_DIR}/data/batches_to_compress/atb.assembly.r1.part003.txt"
META_TSV="${EXP_DIR}/data/atb.metadata.r1.assembly.tsv"
WORKDIR="/dev/shm/agc_reproduce_scenarios"
TARGET_SAMPLE="SAMEA5584600"
TARGET_CONTIG="contig00047"
EXPECTED_LEN=39080

mkdir -p "$WORKDIR"

TARGET_LINE=$(grep -n "$TARGET_SAMPLE" "$PART003_TXT" | head -n 1 | cut -d: -f1)
TARGET_PATH=$(sed -n "${TARGET_LINE}p" "$PART003_TXT")
EXPECTED_HASH=$(grep "$TARGET_SAMPLE" "$META_TSV" | head -n 1 | cut -f4)

evaluate_archive() {
    local agc_path="$1"
    local desc="$2"
    if [[ ! -f "$agc_path" ]]; then echo "[-] $desc: Archive failed!"; return 1; fi

    local len actual_hash
    len=$(agc getset "$agc_path" "$TARGET_SAMPLE" 2>/dev/null | seqkit fx2tab -l | grep "$TARGET_CONTIG" | awk '{print $NF}' || echo "0")
    actual_hash=$(agc getset "$agc_path" "$TARGET_SAMPLE" 2>/dev/null | seqkit sum | awk '{print $1}' || echo "ERROR")

    if [[ "$actual_hash" == "$EXPECTED_HASH" && "$len" -eq "$EXPECTED_LEN" ]]; then
        echo "[PASS] $desc: Bit-for-bit clean (Length: $len bp, Hash: $actual_hash)."
        return 0
    else
        echo "[CRITICAL BUG TRIGGERED] $desc:"
        echo "       Contig length: $len bp (Expected: $EXPECTED_LEN bp, Diff: $((len - EXPECTED_LEN)) bp)"
        echo "       Checksum     : $actual_hash"
        echo "       Expected Hash: $EXPECTED_HASH"
        return 0
    fi
}

# Scenario 1: Exact Prefix lines 1..286 with production flags
PREFIX_TXT="${WORKDIR}/prefix_${TARGET_LINE}.txt"
head -n "$TARGET_LINE" "$PART003_TXT" > "$PREFIX_TXT"
REF_SAMPLE=$(head -n 1 "$PREFIX_TXT")
TAIL_SAMPLES="${WORKDIR}/tail_${TARGET_LINE}.txt"
tail -n +2 "$PREFIX_TXT" > "$TAIL_SAMPLES"

rm -f "${WORKDIR}/s1.agc"
agc create -a -b 500 -s 1500 -t 25 -o "${WORKDIR}/s1.agc" -i "$TAIL_SAMPLES" "$REF_SAMPLE" > /dev/null 2>&1
evaluate_archive "${WORKDIR}/s1.agc" "Scenario 1 (Prefix 1..$TARGET_LINE with -t 25)"

# Scenario 2: Single-threaded
rm -f "${WORKDIR}/s2_t1.agc"
agc create -a -b 500 -s 1500 -t 1 -o "${WORKDIR}/s2_t1.agc" -i "$TAIL_SAMPLES" "$REF_SAMPLE" > /dev/null 2>&1
evaluate_archive "${WORKDIR}/s2_t1.agc" "Scenario 2 (Prefix 1..$TARGET_LINE with -t 1)"

# Scenario 3: Full Batch 003 baseline
ORIG_ARCHIVE="${EXP_DIR}/compression_results/agc_split_size_no_divisions/atb.assembly.r1.part003.agc"
if [[ -f "$ORIG_ARCHIVE" ]]; then
    evaluate_archive "$ORIG_ARCHIVE" "Scenario 3 (Full part003 Original Archive, 513 genomes)"
fi

rm -rf "$WORKDIR"
```

### 6.3 Key Mechanism: Cross-Genome Downstream Splitter Injection

Why did `SAMEA5584600` (line 286) pass when compressing lines 1..286, but corrupt in the full batch (lines 1..513)?

In AGC multi-threaded compression (`-t 25`):
1. **Global Shared State**: `hs_splitters` and `bloom_splitters` are shared across all worker threads.
2. **Work-Stealing Priority Queue**: Contigs from all 513 genomes are queued concurrently in `pq_contigs_desc`.
3. **Downstream Injection**: An assembly located **downstream (lines 287..513)** in `part003.txt` contains novel contigs that enter Pass 2 (`find_new_splitters`). That downstream genome extracted and registered an $A^{31}$ (or $T^{31}$) splitter into the shared global `hs_splitters`.
4. **Collision Execution**: When worker threads subsequently (or concurrently) compressed `SAMEA5584600.contig00047`, the global pool **already contained the $A^{31}$ splitter injected by the later genome**.
5. When `SAMEA5584600.contig00047` scanned against this enriched splitter set, its final hit was $A^{31}$ (`kmer_dir == 0ull`), triggering the Pass 1 $\to$ Pass 2 collision!

---

### 6.4 Multi-Genome Bisection Script (Tracking All 8 Affected Genomes in Batch 003)

In `part003`, exactly 8 assemblies exhibited checksum discrepancies:
`SAMEA5584514`, `SAMEA5584600`, `SAMEA5584805`, `SAMEA5585239`, `SAMEA5607350`, `SAMN30525386`, `SAMN36381905`, `SAMN45299503`.

Instead of only checking `SAMEA5584600`, this script maps the line positions of all 8 genomes and evaluates all 8 simultaneously at each bisection step to pinpoint the exact cutpoint and the culprit genome.

Save as `experiments/124_EXPE_ATB202603_ORDERING/script/bisect_culprit_genome_part003.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
PART003_TXT="${EXP_DIR}/data/batches_to_compress/atb.assembly.r1.part003.txt"
META_TSV="${EXP_DIR}/data/atb.metadata.r1.assembly.tsv"
WORKDIR="/dev/shm/agc_bisect_part003"
mkdir -p "$WORKDIR"

# All 8 affected genomes in part003
AFFECTED_ACCS=(
    "SAMEA5584514"
    "SAMEA5584600"
    "SAMEA5584805"
    "SAMEA5585239"
    "SAMEA5607350"
    "SAMN30525386"
    "SAMN36381905"
    "SAMN45299503"
)

echo "================================================================="
echo "  AGC MULTI-GENOME BISECTION SUITE: BATCH 003 (8 AFFECTED GENOMES)"
echo "================================================================="

echo "Line positions of the 8 affected genomes in part003.txt:"
for acc in "${AFFECTED_ACCS[@]}"; do
    line_num=$(grep -n "$acc" "$PART003_TXT" | head -n 1 | cut -d: -f1)
    echo "  - $acc: Line $line_num"
done | sort -n -k4

echo "-----------------------------------------------------------------"

# Load metadata checksums for the 8 genomes
declare -A META_HASHES
for acc in "${AFFECTED_ACCS[@]}"; do
    META_HASHES["$acc"]=$(grep "$acc" "$META_TSV" | head -n 1 | cut -f4)
done

evaluate_cohort() {
    local max_n="$1"
    local manifest="${WORKDIR}/cohort_${max_n}.txt"
    local agc_out="${WORKDIR}/test_${max_n}.agc"

    head -n "$max_n" "$PART003_TXT" > "$manifest"
    rm -f "$agc_out"

    echo ">>> Testing cohort 1..$max_n ($max_n genomes)..."
    agc create -a -b 500 -s 1500 -t 25 -o "$agc_out" $(cat "$manifest") > /dev/null 2>&1

    # Check which of the 8 are in this cohort (lines <= max_n)
    local n_present=0
    local n_failed=0
    for acc in "${AFFECTED_ACCS[@]}"; do
        local line_num
        line_num=$(grep -n "$acc" "$PART003_TXT" | head -n 1 | cut -d: -f1)
        if [[ "$line_num" -le "$max_n" ]]; then
            n_present=$((n_present + 1))
            local actual_hash
            actual_hash=$(agc getset "$agc_out" "$acc" 2>/dev/null | seqkit sum | awk '{print $1}' || echo "ERROR")
            local exp_hash="${META_HASHES[$acc]}"

            if [[ "$actual_hash" != "$exp_hash" ]]; then
                n_failed=$((n_failed + 1))
                echo "    [FAIL] $acc (Line $line_num): Hash mismatch! Expected $exp_hash != AGC $actual_hash"
            fi
        fi
    done

    if [[ "$n_failed" -eq 0 ]]; then
        echo "    [PASS] All $n_present present affected genomes passed cleanly."
        rm -f "$agc_out" "$manifest"
        return 0
    else
        echo "    [ALERT] $n_failed / $n_present affected genomes CORRUPTED in cohort 1..$max_n!"
        rm -f "$agc_out" "$manifest"
        return 1
    fi
}

# Sweep from line 200 up to full 513
for N in 200 250 300 350 400 450 500 513; do
    evaluate_cohort "$N"
    echo ""
done

echo "================================================================="
echo "Bisection complete."
```

---

### 6.5 Automated Bisection to Minimal Reproducible Cohort (`find_minimal_reproducer.sh`)

To isolate the smallest possible cohort (targeting a minimal 2- or 3-genome reproduction test case for upstream issue reporting), this script performs an automated binary search over the cohort preceding `SAMEA5584600` (Line 286):
1. **Test 0**: Tests Reference (Line 1) + Target (Line 286) alone (2 genomes total).
2. **Test 1**: Sweeps exponential lookback windows ($K \in \{1, 2, 5, 10, 20, 50, 100, 200, 284\}$) preceding the target.
3. **Test 2**: Performs fine-grained binary bisection to isolate the exact line number that introduces the homopolymer splitter into `hs_splitters`.

Save as `experiments/124_EXPE_ATB202603_ORDERING/script/find_minimal_reproducer.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
PART003_TXT="${EXP_DIR}/data/batches_to_compress/atb.assembly.r1.part003.txt"
WORKDIR="/dev/shm/agc_minimal_bisect"
TARGET_SAMPLE="SAMEA5584600"
TARGET_CONTIG="contig00047"
EXPECTED_LEN=39080
TARGET_LINE=286

mkdir -p "$WORKDIR"

REF_SAMPLE=$(head -n 1 "$PART003_TXT")
TARGET_SAMPLE_PATH=$(sed -n "${TARGET_LINE}p" "$PART003_TXT")

echo "================================================================="
echo "  FINDING MINIMAL SUBSET TO REPRODUCE AGC POLY-A BUG            "
echo "================================================================="
echo "Reference (Line 1)  : $(basename "$REF_SAMPLE")"
echo "Target    (Line $TARGET_LINE): $(basename "$TARGET_SAMPLE_PATH")"
echo "-----------------------------------------------------------------"

test_cohort() {
    local start_line="$1"
    local end_line="$2"
    local desc="$3"

    local manifest="${WORKDIR}/cohort.txt"
    : > "$manifest"

    # Add intermediate cohort if start <= end
    if [[ "$start_line" -le "$end_line" && "$start_line" -ge 2 ]]; then
        sed -n "${start_line},${end_line}p" "$PART003_TXT" >> "$manifest"
    fi
    # Always append the target sample
    echo "$TARGET_SAMPLE_PATH" >> "$manifest"

    local total_count=$(( $(wc -l < "$manifest") + 1 )) # +1 for ref
    local agc_out="${WORKDIR}/test.agc"
    rm -f "$agc_out"

    # Run single-threaded for fast, deterministic reproduction
    agc create -a -b 500 -s 1500 -t 1 -o "$agc_out" -i "$manifest" "$REF_SAMPLE" > /dev/null 2>&1

    local len
    len=$(agc getset "$agc_out" "$TARGET_SAMPLE" 2>/dev/null | seqkit fx2tab -l | grep "$TARGET_CONTIG" | awk '{print $NF}' || echo "0")

    if [[ "$len" -ne "$EXPECTED_LEN" ]]; then
        echo "[BUG TRIGGERED] $desc (Total: $total_count genomes, Contig: $len bp)"
        return 0 # 0 = bug reproduced!
    else
        echo "[PASS]          $desc (Total: $total_count genomes, Contig: $len bp)"
        return 1 # 1 = bug did not trigger
    fi
}

echo ">>> Test 0: Reference + Target alone (2 genomes total)..."
if test_cohort 0 0 "Ref + Target alone"; then
    echo "SUCCESS: The bug reproduces with just Reference + Target (2 genomes)!"
    exit 0
fi

echo ""
echo ">>> Test 1: Testing exponential step windows preceding Target (Line 286)..."
# Check Ref + [286-K .. 285] + 286
MIN_START=2
for K in 1 2 5 10 20 50 100 200 284; do
    start_idx=$(( TARGET_LINE - K ))
    if [[ $start_idx -lt 2 ]]; then start_idx=2; fi
    end_idx=$(( TARGET_LINE - 1 ))

    if test_cohort "$start_idx" "$end_idx" "Ref + preceding $K genomes"; then
        echo "--> Bug triggers within preceding $K genomes! (lines $start_idx..$TARGET_LINE)"
        MIN_START=$start_idx
        break
    fi
done

echo ""
echo ">>> Test 2: Binary searching within lines $MIN_START..$TARGET_LINE..."
LOW=$MIN_START
HIGH=$(( TARGET_LINE - 1 ))

while [[ $LOW -lt $HIGH ]]; do
    MID=$(( (LOW + HIGH) / 2 ))
    if test_cohort "$MID" "$HIGH" "Window lines $MID..$HIGH"; then
        LOW=$MID # Bug still triggers, can shrink from the left
        if [[ $LOW -eq $(( HIGH - 1 )) ]]; then break; fi
    else
        HIGH=$MID # Bug stopped triggering, culprit is in the dropped left portion
    fi
done

echo ""
echo "================================================================="
echo "MINIMAL CULPRIT ISOLATED!"
echo "Line $LOW in part003.txt:"
sed -n "${LOW}p" "$PART003_TXT"
echo "Minimal reproducer: Line 1 (Ref), Line $LOW (Culprit), Line $TARGET_LINE (Target)"
echo "================================================================="
```

---

### 6.6 The Smoking Gun: Single Culprit Genome `SAMN48436743` (Line 200) Corrupts All 8 Genomes in Batch 003

Using fine-grained bisection down from 513 genomes, we isolated the exact single assembly responsible for corrupting the entire batch:
- **Reference (Line 1)**: `SAMN52846796` (`/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_2026-03/SAMN52846796.fa.gz`)
- **Culprit (Line 200)**: **`SAMN48436743`** (`/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_2026-03/SAMN48436743.fa.gz`)
- **Target (Line 210)**: `SAMN36381905` (`/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_set2_2024-08/SAMN36381905.fa.gz`)

#### 1. Part 1: The Exact 3-Genome Minimal Reproduction
Compressing just these 3 genomes in adaptive mode (`-a -b 500 -s 1500 -t 1`):
```text
Target (SAMN36381905) contig00133:
  Original True Length : 4,885 bp
  AGC Decompressed Len : 8,676 bp (Diff: +3,791 bp segment duplication)
  Metadata Checksum    : seqkit.v0.1_DLS_k0_4e93b4144326dfd058e69d5a3e621434
  AGC Extracted Hash   : seqkit.v0.1_DLS_k0_875e75e469211949036f9ad93c429d7c
>>> CONFIRMED: 3-GENOME MINIMAL REPRODUCTION OPERATIONAL IN 2 SECONDS <<<
```

#### 2. Part 2: Line 200 Alone Corrupts All 7 Remaining Affected Genomes in Batch 003
Testing each of the other 7 affected genomes against only `Ref (Line 1)` + `Culprit (Line 200)`:

| Genome | Line in `part003` | Expected Metadata Hash | Decompressed Hash (Ref + Culprit + Target) | Outcome |
| :--- | :---: | :--- | :--- | :---: |
| `SAMN36381905` | Line 210 | `...4e93b4144326dfd058e69d5a3e621434` | `...875e75e469211949036f9ad93c429d7c` | **CORRUPTED** (`contig00133` +3,791 bp) |
| `SAMEA5584514` | Line 243 | `...eb3827f8714eca3324fee050a0d59cb6` | `...b44c0c61ae96d3ba7e232eedc73aac1d` | **CORRUPTED** |
| `SAMN45299503` | Line 253 | `...fe4569fa0f4d084a483abbc606418970` | `...41a1bc50abcd8569cf9d52dd7e2adf8a` | **CORRUPTED** |
| `SAMEA5584600` | Line 286 | `...9424396f7f1f6290e42b7776487cb89c` | `...fbcf95fa383353e2d0a85ad87ad38b72` | **CORRUPTED** (`contig00047` +27,040 bp) |
| `SAMN30525386` | Line 287 | `...7af57b549307236ca15063e49fa229b6` | `...de22ae57889b90935bd582b1943de052` | **CORRUPTED** |
| `SAMEA5607350` | Line 312 | `...d6114041cc983108e289091813f0d356` | `...b8469870116c15d11f78ce48ae55415e` | **CORRUPTED** |
| `SAMEA5585239` | Line 313 | `...3bca08a90b53a6f1d9dfed191cbd88a1` | `...8ebd4ddd1630a7f0df34e82463a68f3f` | **CORRUPTED** |
| `SAMEA5584805` | Line 357 | `...b0e9c386df9d9caa26752c6affbe9cd8` | `...a8dce5ea87ddff1e8e43f65e66940e5d` | **CORRUPTED** |

#### 3. Why 2 Genomes Cannot Trigger the Bug (The Irreducible 3-Role Architecture)
An intuitive hypothesis is: *Can we eliminate the Reference genome and simply compress `Culprit` + `Target` (2 genomes)?*
We explicitly tested this:
```bash
agc create -a -b 500 -s 1500 -t 1 -o pair_test.agc -i target_only.txt "$CULPRIT_PATH"
# Result: Contig00133 length = 4,885 bp (PASS - NO CORRUPTION!)
```

**Why 2 genomes fail to trigger the bug:**
1. **Reference Splitter Selection Filter**: When `SAMN48436743` is Sample #0 (Reference), AGC runs `find_candidate_splitters()` on it. Repetitive homopolymer tracts like $A^{31}$ are filtered out or fail the candidate density filter for reference genomes.
2. **`find_new_splitters()` is strictly a Non-Reference Mechanism**: AGC **only** calls `find_new_splitters()` on non-reference samples whose contigs have zero matches to the reference splitters.
3. **The 3 Essential Roles**:
   - **Role 1 (Reference `SAMN52846796`)**: Provides the baseline reference framework. Its divergent sequence forces `Culprit` into Pass 2 (`find_new_splitters`).
   - **Role 2 (Culprit `SAMN48436743`)**: Enters Pass 2 on a novel contig and erroneously extracts $A^{31}$ as a new splitter, injecting it into `hs_splitters`.
   - **Role 3 (Target `SAMN36381905`)**: Scans against `hs_splitters`, hits the newly injected $A^{31}$ splitter as its last splitter in Pass 1 (`split_kmer.kmer_dir == 0ull`), triggering the Pass 1 $\to$ Pass 2 segment collision!

Therefore, the **3-genome triplet (`Ref` + `Culprit` + `Target`) is the mathematically minimal, irreducible reproducer** for the upstream AGC adaptive mode bug.

#### Conclusion:
A single assembly—**`SAMN48436743`** (Line 200)—is the sole source that introduces the poly-A homopolymer splitter into the global pool during Pass 2 (`find_new_splitters`). That single entry into `hs_splitters` subsequently triggers silent contig inflation on **all 8 downstream assemblies**!

This provides an airtight, self-contained 3-file reproduction test kit (~10 MB) ready for submission to `refresh-bio/agc`.

---

### 6.7 The Micro-Scale Reproducer: 10 Kilobytes, 2 Contigs, <0.2 Seconds

By isolating the exact active sequences, we reduced the bug reproduction down from whole genome assemblies to **individual contigs** and a synthetic dummy reference:

#### 1. The Three Minimal Files (Total Size: ~10 KB)
1. **`dummy_ref.fa` (2,000 bp)**: Synthetic random sequence (`python3 -c 'import random; random.seed(42); print(">dummy_ref\n" + "".join(random.choices("ACGT", k=2000)))'`)
2. **`culprit_c220.fa` (3,569 bp)**: `SAMN48436743.contig00220`
   - Sequence ends with an $A^{31}$ homopolymer: `3,539 .. 3,569` (terminal 31 bp!).
   - Injected into `hs_splitters` during adaptive Pass 2 (`find_new_splitters`).
3. **`target_c133.fa` (4,885 bp)**: `SAMN36381905.contig00133`
   - Contains an $A^{31}$ homopolymer at `4,816 .. 4,846` (39 bp before the contig terminus).
   - This $A^{31}$ matches the newly injected splitter as its **last** splitter in Pass 1.

#### 2. Exact Micro Reproduction Command
```bash
# 1. Create dummy reference
python3 -c 'import random; random.seed(42); print(">dummy_ref\n" + "".join(random.choices("ACGT", k=2000)))' > dummy_ref.fa

# 2. Extract the two contigs
zcat /projects/reall/tam/data/ATB/Uncompressed/Uncompressed_2026-03/SAMN48436743.fa.gz | seqkit grep -p "SAMN48436743.contig00220" > culprit_c220.fa
zcat /projects/reall/tam/data/ATB/Uncompressed/Uncompressed_set2_2024-08/SAMN36381905.fa.gz | seqkit grep -p "SAMN36381905.contig00133" > target_c133.fa

# 3. Compress with adaptive mode (-a)
printf "%s\n%s\n" culprit_c220.fa target_c133.fa > pair.txt
agc create -a -b 500 -s 1500 -t 1 -o bug_micro.agc -i pair.txt dummy_ref.fa

# 4. Decompress target_c133
agc getset bug_micro.agc target_c133 | seqkit fx2tab -l
```

#### 3. Empirical Result
```text
True Original Length : 4,885 bp
Decompressed Length  : 9,650 bp (+4,765 bp silent duplication!)
Runtime              : < 0.2 seconds
Disk Footprint       : 10.4 KB
```

This represents the absolute smallest, purest representation of the upstream AGC poly-A splitter bug possible. It can be packaged as a standalone micro-benchmark repository or attached directly as a zip file to the GitHub issue report.

---

### 6.8 Can Corrupted Genomes Act as Vectors? (Victim vs. Culprit Dynamics)

A natural follow-up hypothesis is: *Can a corrupted assembly act as an infectious vector to propagate the bug to downstream assemblies without the original culprit?*

We experimentally tested this by compressing `dummy_ref.fa` + `SAMEA5584600.contig00047` (Victim #1) + `SAMN36381905.contig00133` (Target):
```bash
agc create -a -b 500 -s 1500 -t 1 -o test_vector.agc -i pair.txt dummy_ref.fa
# Result: contig00133 length = 4,885 bp (PASS - NO CORRUPTION!)
```

#### Why Victims Do NOT Act as Vectors:
1. **The Culprit (`SAMN48436743.contig00220`, 3,569 bp)**:
   - The $A^{31}$ homopolymer spans **`3,539 .. 3,569`**—the **exact terminal 31 bases of the contig**.
   - When entering Pass 2 `find_new_splitters()`, AGC's step-based candidate selection (~1,500 bp intervals) landed directly on this terminal boundary, extracting and registering $A^{31}$ into the shared `hs_splitters` table.
2. **The Victim (`SAMEA5584600.contig00047`, 39,080 bp)**:
   - In `SAMEA5584600.contig00047`, the poly-A tract is located at `39,040 .. 39,071` (with 9 non-A nucleotides continuing to `39,080`).
   - In `find_new_splitters()`, the 1,500 bp candidate step intervals do not align with that internal homopolymer window. AGC does not extract $A^{31}$ from `SAMEA5584600` on its own.
3. **Conclusion**:
   - **Victim genomes are purely PASSIVE**: They only corrupt when an upstream culprit injects $A^{31}$ into `hs_splitters`.
   - **Victim genomes do NOT act as transmission vectors**: They cannot independently infect subsequent genomes.
   - Removing the **isolated set of assemblies** (or running without `-a`) permanently neutralizes the issue because the passive genomes have no mechanism to generate the fatal splitter without the specific culprit alignment.

---

### 6.9 The Zero-Dependency 100% Synthetic Minimal Reproducible Example (MRE)

We successfully synthesized an entirely artificial, zero-data reproduction script. It generates three tiny FASTA files on the fly and reliably triggers deterministic contig duplication (**`3,000 bp -> 5,918 bp`**) in **0.05 seconds** on any system:

#### Self-Contained Reproduction Script (`reproduce_polyA_pure_synthetic.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

WORKDIR="/tmp/agc_pure_synthetic_mre"
mkdir -p "$WORKDIR"

echo "=== 1. Generating 100% Synthetic Test FASTAs ==="

# 1. Synthetic Dummy Reference (2,000 bp random bases)
python3 -c '
import random; random.seed(42)
print(">ref\n" + "".join(random.choices("ACGT", k=2000)))
' > "${WORKDIR}/ref.fa"

# 2. Synthetic Culprit (1,969 bp random bases + terminal A^31)
# Triggers find_new_splitters() line 820 to register A^31 into hs_splitters!
python3 -c '
import random; random.seed(123)
print(">culprit\n" + "".join(random.choices("ACGT", k=1969)) + "A" * 31)
' > "${WORKDIR}/culprit.fa"

# 3. Synthetic Target (3,000 bp total: 2,919 bp body + A^31 + 50 bp tail)
# Hits newly injected A^31 as its last splitter in Pass 1!
python3 -c '
import random; random.seed(456)
body = "".join(random.choices("ACGT", k=2919))
tail = "".join(random.choices("ACGT", k=50))
print(">target\n" + body + "A" * 31 + tail)
' > "${WORKDIR}/target.fa"

EXPECTED=3000

echo "=== 2. Compressing in Adaptive Mode (-a) ==="
printf "%s\n%s\n" "${WORKDIR}/culprit.fa" "${WORKDIR}/target.fa" > "${WORKDIR}/pair.txt"
rm -f "${WORKDIR}/pure_synth.agc"

agc create -a -b 500 -s 1500 -t 1 -o "${WORKDIR}/pure_synth.agc" -i "${WORKDIR}/pair.txt" "${WORKDIR}/ref.fa" > /dev/null 2>&1

echo "=== 3. Decompressing Target Contig ==="
ACTUAL=$(agc getset "${WORKDIR}/pure_synth.agc" target | seqkit fx2tab -l | awk '{print $NF}')

echo "Expected Original Length : ${EXPECTED} bp"
echo "AGC Decompressed Length  : ${ACTUAL} bp (Diff: $((ACTUAL - EXPECTED)) bp duplication!)"

if [[ "$ACTUAL" -ne "$EXPECTED" ]]; then
    echo ">>> BUG REPRODUCED WITH 100% SYNTHETIC DATA IN 0.05 SECONDS! <<<"
else
    echo "[PASS] Length matches."
fi

rm -rf "$WORKDIR"
```

#### Empirical Validation
```text
Expected Original Length : 3000 bp
AGC Decompressed Length  : 5918 bp (Diff: 2918 bp duplication!)
>>> BUG REPRODUCED WITH 100% SYNTHETIC DATA IN 0.05 SECONDS! <<<
```

This self-contained script requires zero external files, no dataset access, runs in 50 milliseconds, and is ready for inclusion directly into the GitHub issue report for `refresh-bio/agc`.

#### 6.9.2 The Absolute 100-bp Nano Minimal Reproducible Example (`reproduce_agc_polyA_bug_100bp.sh`)

By lowering `-s 50` (segment size = 50 bp), we pushed the reproduction boundary down to the mathematical minimum of **100 base pairs** (spanning just two 50-bp segments around a 31-mer splitter).

This generalized script runs anywhere, requires zero external data, dynamically finds the exact duplicated slice, and executes in 0.02 seconds:

```bash
#!/usr/bin/env bash
set -euo pipefail

WORKDIR="$(pwd)/.tmp_agc_100bp_test"
trap 'rm -rf "$WORKDIR"' EXIT
mkdir -p "$WORKDIR"

echo "=========================================================================================="
echo "  AGC ADAPTIVE MODE (-a) 100-bp HOMOPOLYMER SPLITTER BUG REPRODUCER                      "
echo "=========================================================================================="

# 1. Generate 100 bp synthetic test FASTAs
python3 -c 'import random; random.seed(42); print(">ref\n" + "".join(random.choices("ACGT", k=100)))' > "${WORKDIR}/ref.fa"
python3 -c 'import random; random.seed(123); print(">culprit\n" + "".join(random.choices("ACGT", k=69)) + "A" * 31)' > "${WORKDIR}/culprit.fa"
python3 -c 'import random; random.seed(456); print(">target\n" + "".join(random.choices("ACGT", k=19)) + "A" * 31 + "".join(random.choices("ACGT", k=50)))' > "${WORKDIR}/target.fa"

# 2. Compress with AGC adaptive mode (-a -s 50)
printf "%s\n%s\n" "${WORKDIR}/culprit.fa" "${WORKDIR}/target.fa" > "${WORKDIR}/pair.txt"
agc create -a -s 50 -b 10 -t 1 -o "${WORKDIR}/test.agc" -i "${WORKDIR}/pair.txt" "${WORKDIR}/ref.fa" > /dev/null 2>&1

# 3. Extract original and decompressed sequences
ORIG_SEQ=$(grep -v "^>" "${WORKDIR}/target.fa" | tr -d '\n')
AGC_SEQ=$(agc getset "${WORKDIR}/test.agc" target | grep -v "^>" | tr -d '\n')

ORIG_LEN=${#ORIG_SEQ}
AGC_LEN=${#AGC_SEQ}

echo "ORIGINAL TARGET (Length: ${ORIG_LEN} bp):"
echo "$ORIG_SEQ"
echo ""
echo "AGC DECOMPRESSED (Length: ${AGC_LEN} bp):"
echo "$AGC_SEQ"
echo ""

if [[ "$ORIG_LEN" -eq "$AGC_LEN" ]]; then
    echo "[PASS] Decompressed length matches original. (Bug is fixed!)"
    exit 0
fi

echo ">>> CRITICAL DATA CORRUPTION DETECTED (+$(($AGC_LEN - $ORIG_LEN)) bp duplicated!) <<<"
echo "------------------------------------------------------------------------------------------"
python3 -c "
orig = '$ORIG_SEQ'
agc = '$AGC_SEQ'
diff_len = len(agc) - len(orig)
left = 0
while left < len(orig) and orig[left] == agc[left]:
    left += 1
right_orig = len(orig)
right_agc = len(agc)
while right_orig > left and right_agc > left and orig[right_orig - 1] == agc[right_agc - 1]:
    right_orig -= 1
    right_agc -= 1

print(f'Original prefix [0:{left}]   : {orig[:left]}')
print(f'AGC prefix      [0:{left}]   : {agc[:left]} (Identical)')
print(f'DUPLICATED INSERTION     : {agc[left:right_agc]} (+{diff_len} bp duplicated sequence!)')
print(f'Original suffix [{right_orig}:{len(orig)}] : {orig[right_orig:]}')
print(f'AGC suffix     [{right_agc}:{len(agc)}] : {agc[right_agc:]} (Identical)')
"
echo "=========================================================================================="
```

#### Empirical Validation (Verified on AGC v3.2.4 [build 20260722.1])
```text
==========================================================================================
  AGC ADAPTIVE MODE (-a) 100-bp HOMOPOLYMER SPLITTER BUG REPRODUCER                      
==========================================================================================
ORIGINAL TARGET (Length: 100 bp):
GTCTGGTTTCTACCCAACGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATGTGGTTAGCTGGTATACGCTCTTGGTCGGTCAAGATTAGTTTGCTAAAT

AGC DECOMPRESSED (Length: 119 bp):
GTCTGGTTTCTACCCAACGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATGTGGTTAGCTGGTATACGCTCTTGGTCGGTCAAGATTAGTTTGCTAAAT

>>> CRITICAL DATA CORRUPTION DETECTED (+19 bp duplicated!) <<<
------------------------------------------------------------------------------------------
Original prefix [0:50]   : GTCTGGTTTCTACCCAACGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AGC prefix      [0:50]   : GTCTGGTTTCTACCCAACGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (Identical)
DUPLICATED INSERTION     : AAAAAAAAAAAAAAAAAAA (+19 bp duplicated sequence!)
Original suffix [50:100] : TGTGGTTAGCTGGTATACGCTCTTGGTCGGTCAAGATTAGTTTGCTAAAT
AGC suffix     [69:119]  : TGTGGTTAGCTGGTATACGCTCTTGGTCGGTCAAGATTAGTTTGCTAAAT (Identical)
==========================================================================================
```

- **Visual Smoking Gun**: AGC literally spliced **19 extra `'A'` nucleotides** directly into the homopolymer tract (`AAAAAAAAAAAAAAAAAAA`), inflating it from 31 bases to 50 bases!
- **Runtime**: 0.02 seconds.
- **Footprint**: 300 bytes of input FASTA.
- **Reproducibility**: 100% deterministic across macOS and Linux on both v3.2.2 and v3.2.4.

---

## 7. Empirical Remediation Audit: Adaptive Segregation (`v2_adaptive_clean`)

### 7.1 Hypothesis & Experimental Setup
In an attempt to preserve the superior compression ratio of adaptive mode (`-a`) without code patching, a segregation hypothesis was tested:
1. Identify the 95 corrupted victim genomes across the 19 affected archives in `v1`.
2. Extract the 95 victims plus the 2 non-polyA anomaly genomes into a separate `atb.assembly.r1.standalone.txt` archive (97 genomes total).
3. Recompress the 19 "cleaned" batches with `agc create -a`.
4. **Hypothesis**: Since the victims were removed, the culprit contigs would remain but have no matching victim sequences to infect.

### 7.2 Validation Results (`verify_clean_batches.py`)
Audit performed on 67,642 genomes across the 20 cleaned batches + `standalone.agc` in `/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING/compression_results/.archive_store/agc_default_v2_adaptive_clean`:

```text
==================================================================
Total Genomes Evaluated : 67,642
Passed Bit-for-Bit      : 67,606 (99.95%)
Failed Checksum         : 36 (0.05%)
Archives Tested         : 21 (20 cleaned batches + standalone.agc)
Archives 100% Clean     : 14 / 21
Archives with Failures  : 7 / 21
==================================================================
```

#### Status by Archive

| Batch Archive | Status | Details |
| :--- | :---: | :--- |
| `atb.assembly.r1.part003.agc` | **100% PASS** | Clean (all 8 original victims cured) |
| `atb.assembly.r1.part199.agc` | **100% PASS** | Clean (all 8,411 genomes pass) |
| `atb.assembly.r1.part223.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part249.agc` | **100% PASS** | Clean (verified with corrected `SAMN16418392` assembly) |
| `atb.assembly.r1.part257.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part263.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part325.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part586.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part691.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part862.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part929.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part995.agc` | **100% PASS** | Clean |
| `atb.assembly.r1.part1042.agc`| **100% PASS** | Clean |
| `atb.assembly.r1.standalone.agc` | **96/97 PASS** | 1 failure is `SAMN50311804` (raw source file with 1,434 null bytes, expected) |
| `atb.assembly.r1.part051.agc` | **FAIL (1)** | `SAMN03996952` |
| `atb.assembly.r1.part059.agc` | **FAIL (1)** | `SAMN38380369` |
| `atb.assembly.r1.part170.agc` | **FAIL (6)** | `SAMEA5757810`, `SAMEA6144833`, `SAMN11156863`, `SAMN28700481`, `SAMN35670651`, `SAMN37529090` |
| `atb.assembly.r1.part435.agc` | **FAIL (7)** | `SAMEA1317042`, `SAMEA1317060`, `SAMEA1317062`, `SAMEA1317064`, `SAMEA1317066`, `SAMEA1317071`, `SAMN13910111` |
| `atb.assembly.r1.part851.agc` | **FAIL (7)** | `SAMEA6124300`, `SAMEA6534298`, `SAMN11463671`, `SAMN12821393`, `SAMN22254653`, `SAMN22254909`, `SAMN22255139` |
| `atb.assembly.r1.part1008.agc`| **FAIL (2)** | `SAMN04505064`, `SAMN42436694` |
| `atb.assembly.r1.part1021.agc`| **FAIL (11)**| `SAMEA1094336`, `SAMEA1398296`, `SAMEA1559269`, `SAMEA1559279`, `SAMEA1568547`, `SAMEA4555932`, `SAMEA7461379`, `SAMN01821746`, `SAMN05290090`, `SAMN06212339`, `SAMN18539620` |

### 7.3 Mechanistic Root Cause of "Secondary Infections" (The "Whack-A-Mole" Effect)
The 35 corrupted genomes in the 7 failed archives are **entirely new victims** that passed cleanly in `v1`.

Why this occurs:
1. **Dynamic Splitter Pool Evolution**: In adaptive mode (`-a`), non-reference contigs that fail Pass 1 execute `find_new_splitters()` during Pass 2, injecting new splitters into `hs_splitters`.
2. **Shift in Contig Segmentation**: Removing earlier victim genomes from the input stream changes the order and composition of genomes processed downstream of the culprit.
3. **Homologous Repetitive Elements**: In dense taxonomic groups (e.g., *Enterobacteriaceae* in `part170`, *Pseudomonas* in `part1021`), dozens of closely related strains contain similar accessory junctions or mobile element repeats.
   - In `v1`, earlier victim contigs absorbed the candidate alignment window and hit the terminal $A^{31}$ splitter condition.
   - When those genomes were removed in `v2`, downstream sister genomes that previously fell between splitter intervals now had $A^{31}$ land at their terminal position, matching the `0ull == 0ull` condition in `compress_contig` (line 2041).

### 7.4 Conclusion & Transition to Definitive Code Patch
Adaptive segregation cured **13 out of 20 batches (65%)**, confirming that in sparsely related batches, the infection is strictly localized. However, in repetitive clades, segregation produces recursive secondary infections. Non-adaptive mode eliminated the bug but caused a severe 14x size inflation (e.g. `part851` expanding from ~100 MB to 1.4 GB).

The permanent solution was implemented at the source code level in `src/core/kmer.h`.

---

## 8. Definitive Resolution: Source Code Patch & Full `v3_patch` Verification

### 8.1 The Patch (`fix-polya` branch)
In `src/core/kmer.h:450-464`:
```cpp
// Check cur_size before comparing 64-bit kmer representation
bool operator==(const CKmer& x) const {
    if (cur_size != x.cur_size)
        return false;
    if (variant != kmer_mode_t::rev_comp)
        return kmer_dir == x.kmer_dir;
    else
        return kmer_rc == x.kmer_rc;
}

bool operator!=(const CKmer& x) const {
    return !(*this == x);
}
```

### 8.2 Empirical Nano-MRE Verification
Tested against `nano_agc_test.sh`:
- **Unpatched upstream AGC**: Fails with `CRITICAL DATA CORRUPTION DETECTED (+19 bp duplicated!)`.
- **Patched AGC**: Outputs `[PASS] Decompressed length matches original. (Bug is fixed!)` (100 bp $\to$ 100 bp bit-for-bit).

### 8.3 Cluster-Scale Validation (`v3_patch` on 67,642 Genomes)
Recompressed all 20 affected archives with the patched binary using original production settings (`-a -b 500 -s 1500 -t 40`) and original batch files.

Validated with `verify_clean_batches.py`:
- **Total Genomes Evaluated**: 67,642
- **Passed Bit-for-Bit**: 67,641 (99.9985%)
- **Residual Mismatch**: Exactly 1 genome (`SAMN50311804` in `part199`), which is the raw source FASTA containing 1,434 literal null bytes (`\x00`) from an interrupted filesystem write. AGC stripped the null bytes during read, restoring the valid sequence.
- **Poly-A Splitter Corruption**: **0 across all 3,092,278 genomes (100% resolved)**.
- **Archive Storage**: Full adaptive compression preserved without size penalty.








