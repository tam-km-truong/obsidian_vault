# `split_create` (`create -p`) Bug Forensics & Code Audit

## 1. Forensic Analysis of Archive Corruption (`SAMEA5584600` & `SAMEA5168235`)

### Observed Symptoms
During full checksum verification against `atb.metadata.r1.assembly.tsv` (`seqkit sum` / MD5 of uncompressed contigs):
- **`SAMEA5584600`** in `atb.assembly.r1.part003.agc`:
  - Disk FASTA (`SAMEA5584600.fa.gz`): `110` contigs, `4,694,663 bp` total (`seqkit.v0.1_DLS_k0_9424396f7f1f6290e42b7776487cb89c`).
  - AGC extracted (`agc getset`): `110` contigs, `4,720,862 bp` total (`seqkit.v0.1_DLS_k0_30780fd5bb763a769c9130c6759073b1`).
  - Only a single contig differed: `SAMEA5584600.contig00047` (`39,080 bp` in original FASTA vs. `65,279 bp` extracted from AGC).
- **`SAMEA5168235`** in `atb.assembly.r1.part051.agc`:
  - Metadata hash: `seqkit.v0.1_DLS_k0_6add5d30a00e5f9046951e3cd5f60a5b`.
  - AGC extracted hash: `seqkit.v0.1_DLS_k0_c433eeafc4b9019e939a30af0712a5a6`.

### Sequence-Level Breakdown of `SAMEA5584600.contig00047`
Comparing the original `39,080 bp` contig against the `65,279 bp` AGC-extracted contig:
- **Segment 0 (`0..1531`, `1,531 bp`)**: 100% identical prefix, ending with a 31-bp splitter at `1500..1531`.
- **Segment 2+ (`12000..39080` in FASTA, `27,049 bp` after stripping the 31-bp overlap at `12000..12031`)**: 100% identical suffix.
- **Segment 1 (`1500..12031` in FASTA = `10,500 bp` stripped vs. `36,699 bp` stripped in AGC)**:
  - Completely different sequence (`mid_fa in mid_agc == False`), ending with a 31-bp poly-A splitter (`AAGAGACCGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`, canonical 31-mer `0ull = A^31`).
  - During decompression, `CSegment::get(in_group_id, ...)` returned **another genome's segment** from that same segment group instead of `SAMEA5584600`'s delta sequence.

### Root Cause of `in_group_id` Desynchronization
In git commits `1435ea9` through `39491f0` (prior to commit `9c312de1f0`), `split_create` estimated archive size by **partially flushing** (`finish()` / `FlushPartial`) the top dirty segment groups mid-archive before `v_lzp.size() == contigs_in_pack` (`50`).

In `src/common/segment.cpp`, `CSegment::get` computes the pack and intra-pack index using fixed modulo arithmetic:
```cpp
uint32_t part_id = (id_seq - 1) / contigs_in_pack;
uint32_t seq_in_part_id = (id_seq - 1) % contigs_in_pack;
```
Flushing a partial pack (`k < 50` sequences) mid-archive writes a pack with fewer than `50` sequences at `part_id`. Every subsequent segment appended to that `CSegment` group has its `in_group_id` shifted relative to the pack boundaries, causing `CSegment::get` to read from the wrong pack/offset and silently return another sample's sequence from the same segment group.

---

## 2. Code Audit of Current `split-create-mode-with-buffer-size` (`HEAD` = `2f862c24e1`)

Commit `9c312de1f0` replaced partial pack flushing with `CAGCCompressor::GetSimulatedArchiveSize()`. However, an audit of the current codebase identified **5 bugs** that must be fixed before using `create -p` in production:

### Bug 1 (Critical): Broken Worker Barrier in `CAGCCompressor::AddSampleSplit` (`src/core/agc_compressor.cpp:2575-2618`)
In `AddSampleSplit`, the main thread waits for workers before calling `GetSimulatedArchiveSize(no_threads)` using:
```cpp
while (!pq_contigs_desc->IsEmpty()) {
    std::this_thread::sleep_for(std::chrono::milliseconds(1));
}
```
**Why this causes data races and inaccurate size estimates:**
1. `pq_contigs_desc->IsEmpty()` returns `true` the instant the last worker **pops** the last task from `pq_contigs_desc`—**before** the worker processes that task.
2. In adaptive mode (`-a`), workers pop `contig_processing_stage_t::new_splitters` from `pq_contigs_desc` (making `pq_contigs_desc->IsEmpty() == true` immediately), switch `pq_contigs_desc_working = pq_contigs_desc_aux` (`src/core/agc_compressor.cpp:1230`), process all `hard_contigs`, and then run `registration` (`register_segments` + `store_segments`).
3. Even without `-a`, popping `contig_processing_stage_t::registration` empties `pq_contigs_desc` *before* `register_segments` and `store_segments` execute.
4. Consequently, `GetSimulatedArchiveSize(no_threads)` runs **concurrently** with `register_segments` and `store_segments`:
   - **Use-After-Free / Out-of-Bounds Read on `v_segments`**: In `register_segments` (`src/core/agc_compressor.cpp:966-969`), `no_segments += no_new;` is executed before `v_segments.resize(no_segments);`. `GetSimulatedArchiveSize` threads read `no_segments` and index `v_segments[j]` while `v_segments.resize()` reallocates the underlying buffer.
   - **Data Race on `std::shared_ptr<CSegment>`**: In `store_segments` (`src/core/agc_compressor.cpp:1008`), workers assign `v_segments[group_id] = make_shared<CSegment>(...)` without synchronization while `GetSimulatedArchiveSize` reads `v_segments[j]`.
   - **Missed In-Flight Segments**: Segments still in `buffered_seg_part` (not yet drained by `store_segments`) are omitted from `GetSimulatedArchiveSize`.

**Fix:**
Synchronize using a sample completion counter updated at the end of the `registration` stage in `start_compressing_threads` (`src/core/agc_compressor.cpp:1152-1185`), after `register_segments`, `store_segments`, `store_contig_batch`, `FlushOutBuffers()`, and `buffered_seg_part.clear()` have all completed, right before the final `bar.arrive_and_wait()`. Track `submitted_samples` whenever `registration` is pushed to `pq_contigs_desc`, and wait until `completed_samples.load(std::memory_order_acquire) == submitted_samples`.

---

### Bug 2: Unnecessary Disk Flush on Every Sample in `CArchive::GetCurrentOffset` (`src/common/archive.cpp:362-372`)
`AddSampleSplit` calls `GetCurrentArchiveSizeEstimate()` -> `out_archive->GetCurrentOffset()` after **every sample**:
```cpp
size_t CArchive::GetCurrentOffset()
{
    lock_guard<mutex> lck(mtx);
    if (!input_mode && f_out)
        flush_out_buffers();
    return f_offset;
}
```
- `start_compressing_threads` already calls `out_archive->FlushOutBuffers()` at the end of every sample's `registration` barrier (`src/core/agc_compressor.cpp:1159, 1182`).
- Calling `flush_out_buffers()` inside `GetCurrentOffset()` while workers are still active causes mutex contention on `out_archive->mtx` and extra disk writes. Once Bug 1's barrier is fixed, `f_offset` is already flushed at the end of each sample (or any pending buffer sizes in `v_out_buffers` can be summed without flushing to disk).

---

### Bug 3: ZSTD Level & Marker Byte Discrepancy in `CSegment::simulate_store` (`src/common/segment.cpp:579-610`)
- `CSegment::store_in_archive` (`src/common/segment.h:279`) compresses delta packs at ZSTD level `17` and appends a `1`-byte marker (`0` for ZSTD, or falls back to uncompressed data + `1` byte marker if `zstd_size + 1 >= v_tmp.size()`).
- `CSegment::simulate_store` (`src/common/segment.cpp:599`) uses ZSTD level `10` and returns `zstd_ret` directly without clamping to `buffer.size() + 1` or accounting for the `+ 1` marker byte:
  ```cpp
  size_t zstd_ret = ZSTD_compressCCtx(zstd_cctx, v_zstd.data(), zstd_bound, buffer.data(), buffer.size(), 10);
  if (ZSTD_isError(zstd_ret))
      return buffer.size() + 1;
  return (zstd_ret + 1 < buffer.size()) ? (zstd_ret + 1) : (buffer.size() + 1);
  ```

---

### Bug 4: Missing Braces in `CApplication::create_split` (`src/app/main.cpp:148-153`)
In `src/app/main.cpp:148-153`:
```cpp
if (execution_params.verbosity() > 0)
    cerr << "Creating-split mode; currently " << part_name << " with reference " << reference_file << "\n";
    cerr << "Target size: " << execution_params.target_part_size << " bytes.\n";
    if (execution_params.is_strict)
    cerr << "Strict mode on.\n";
```
Missing `{}` braces around the `if (execution_params.verbosity() > 0)` body cause `"Target size: ..."` and `"Strict mode on."` to print on every archive split even when `-v 0`.

---

### Bug 5: Unreachable `verbosity > 3` Condition in `CAGCCompressor::AddSampleSplit` (`src/core/agc_compressor.cpp:2586`)
- `src/app/application.h:70` defines `b_value<uint32_t> verbosity{ 0, 0, 2 };`, clamping `verbosity` to a maximum of `2`.
- Consequently, `if (verbosity > 3)` in `src/core/agc_compressor.cpp:2586` is unreachable dead code. Either change the condition to `if (verbosity >= 2)` or increase the maximum bound in `application.h`.
