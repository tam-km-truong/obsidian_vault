---
raw_tags:
  - "poly-a splitter corruption"
  - seqkit
  - agc
  - assembly
  - atb
  - exp_dir
  - txt
  - archives
word_count: 6944
char_count: 71405
processed: true
processed_note: "[[ATB 2026-03 - AGC Recompression Master Tracking & Audit]]"
---

# ATB202603 AGC Recompression — Master Tracking

## Overview
- **Goal**: Recover the exact batch boundaries from the `split_create` `.agc` archives (which passed the 100% completeness check), slice `global_final_ordering.txt` into the exact same contiguous batches, and recompress each batch with default `agc create`.
- **Audit Reference**: `/Users/ktruong/tools/agc-split-size/docs/debug_split_create_audit.md`
- **Upstream AGC Bug Debug Note**: [[AGC Upstream Poly-A Splitter Corruption Bug Debug Note]]

## Checklist
- [x] **Step 1**: Extract batch counts and cumulative cutpoints (`separators.tsv`) from `.agc` archives (sorted with `sort -V`)
- [x] **Step 2**: Slice `global_final_ordering.txt` into batch `.txt` files using `separators.tsv`
- [x] **Step 2 bis**: Verify batch files (completeness, zero missing, zero duplicates, exact line-by-line global order match, per-batch counts)
- [x] **Step 3a**: Split batch file paths into 3 File-of-Files (`fof_1.txt`, `fof_2.txt`, `fof_3.txt`) for 3 compute nodes
- [x] **Step 3b**: Run default `agc create` per FOF across the 3 compute nodes
- [x] **Step 4**: Run 100% full dataset audit (`comprehensive_validation.py`) on all 3,092,278 genomes across all 1,129 archives
- [ ] **Step 5**: Recompress the 20 affected archives without `-a` (19 poly-A affected + 1 outdated assembly `part249`)
- [ ] **Step 6**: Validate recompressed 20 archives and construct clean production symlink overlay

---

## Paths
```bash
EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
AGC_DIR="${EXP_DIR}/compression_results/agc_split_size_no_divisions"
GLOBAL_ORDER="${EXP_DIR}/ordering_results/global_final_ordering.txt"

SEPARATORS_TSV="${EXP_DIR}/data/separators.tsv"
BATCH_DIR="${EXP_DIR}/data/batches_to_compress"
```

---

## Step 1: Extract Separators (`separators.tsv`)

For each `.agc` archive in sorted order (`atb.assembly.r1.part000.agc`, `part001.agc`, ...), count the number of genomes via `agc listset` and compute the cumulative genome count (cutpoint):
- **Column 1**: `num_genomes` (number of genomes in that archive)
- **Column 2**: `cumulative_genomes` (1-based inclusive end line / cutpoint in `global_final_ordering.txt`)
- **Column 3**: `batch_name` (archive basename without `.agc`, e.g., `atb.assembly.r1.part000`)

```bash
#!/usr/bin/env bash
set -euo pipefail
shopt -s nullglob

EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
AGC_DIR="${EXP_DIR}/compression_results/agc_split_size_no_divisions"
SEPARATORS_TSV="${EXP_DIR}/data/separators.tsv"

cum=0
: > "$SEPARATORS_TSV"

for agc_file in $(printf "%s\n" "$AGC_DIR"/*.agc | sort -V); do
    batch_name=$(basename "$agc_file" .agc)
    count=$(agc listset "$agc_file" | wc -l | awk '{print $1}')
    cum=$(( cum + count ))
    printf "%d\t%d\t%s\n" "$count" "$cum" "$batch_name" >> "$SEPARATORS_TSV"
done

echo "[DONE] Wrote $(wc -l < "$SEPARATORS_TSV") rows to $SEPARATORS_TSV (Total cumulative genomes: $cum)"
```

> [!TIP]
> **Instant fix if `separators.tsv` was already generated with lexicographical glob order** (no need to re-run `agc listset`):
> ```bash
> sort -k3,3V "$SEPARATORS_TSV" | awk 'BEGIN{OFS="\t"} {cum += $1; $2 = cum; print $1, $2, $3}' > "${SEPARATORS_TSV}.tmp" && mv "${SEPARATORS_TSV}.tmp" "$SEPARATORS_TSV"
> ```

Example `separators.tsv`:
```text
42150	42150	atb.assembly.r1.part000
38910	81060	atb.assembly.r1.part001
45020	126080	atb.assembly.r1.part002
```

---

## Step 2: Cut `global_final_ordering.txt` into Batches Using `separators.tsv`

For each row in `separators.tsv`:
- **Start of cut** (`start_idx`): cumulative cutpoint from the **previous row** (or `0` for the first row; `start_line = prev_cum + 1` in 1-based indexing).
- **End of cut** (`end_idx`): cumulative cutpoint from the **current row** (`col 2`).
- **Output file**: `${BATCH_DIR}/${batch_name}.txt` (same name as the original `.agc` archive).

Single-pass `awk` command (reads the 3M-line `global_final_ordering.txt` only once):

```bash
#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
GLOBAL_ORDER="${EXP_DIR}/ordering_results/global_final_ordering.txt"
SEPARATORS_TSV="${EXP_DIR}/data/separators.tsv"
BATCH_DIR="${EXP_DIR}/data/batches_to_compress"

mkdir -p "$BATCH_DIR"

awk -v out_dir="$BATCH_DIR" '
    # Pass 1: Read separators.tsv (col1=count, col2=cumulative_end, col3=batch_name)
    NR == FNR {
        n_batches++
        end_line[n_batches] = $2
        batch_name[n_batches] = $3
        next
    }
    # Pass 2: Stream global_final_ordering.txt and cut at each cumulative boundary
    FNR == 1 {
        b = 1
        out_file = out_dir "/" batch_name[b] ".txt"
    }
    {
        print $0 > out_file
        if (FNR == end_line[b]) {
            close(out_file)
            b++
            if (b <= n_batches) {
                out_file = out_dir "/" batch_name[b] ".txt"
            }
        }
    }
    END {
        if (FNR != end_line[n_batches]) {
            printf "[ERROR] Line count mismatch: global order has %d lines, last separator is %d\n", FNR, end_line[n_batches] > "/dev/stderr"
            exit 1
        }
        printf "[SUCCESS] Cut %d genomes into %d batch files in %s\n", FNR, n_batches, out_dir
    }
' "$SEPARATORS_TSV" "$GLOBAL_ORDER"
```

---

## Step 2 bis: Verify Batches (Completeness, No Duplicates, Exact Global Order)

Verifies in a single pass (~3 seconds for 3M genomes):
1. **Batch existence & exact per-batch counts**: Every batch in `separators.tsv` exists in `${BATCH_DIR}` and its line count matches Column 1 (`num_genomes`), and its cumulative count matches Column 2 (`cumulative_genomes`). Also checks for any stray/unexpected `.txt` files in `${BATCH_DIR}`.
2. **Zero duplicate genomes**: Tracks every genome accession across all batches and fails immediately if any genome is repeated.
3. **100% Completeness & Exact Global Order**: Streams all batches in natural order (`sort -V`) alongside `global_final_ordering.txt` and asserts a 1-to-1 line-by-line match from line 1 to line $N$ (zero missing, zero out-of-order).

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

EXP_DIR = Path("/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING")
GLOBAL_ORDER = EXP_DIR / "ordering_results/global_final_ordering.txt"
SEPARATORS_TSV = EXP_DIR / "data/separators.tsv"
BATCH_DIR = EXP_DIR / "data/batches_to_compress"


def clean_acc(line: str) -> str:
    return line.strip().split("/")[-1].split(".")[0]


def main():
    # 1. Load expected batches from separators.tsv
    expected_batches = []
    with open(SEPARATORS_TSV) as f:
        for row_idx, line in enumerate(f, 1):
            parts = line.strip().split("\t")
            if not parts or len(parts) < 3:
                continue
            expected_batches.append((int(parts[0]), int(parts[1]), parts[2]))

    if not expected_batches:
        sys.exit(f"[FAIL] No rows found in {SEPARATORS_TSV}")

    # Check for unexpected/extra batch files in BATCH_DIR
    actual_files = {p.stem for p in BATCH_DIR.glob("*.txt")}
    expected_names = {b[2] for b in expected_batches}
    missing_files = expected_names - actual_files
    extra_files = actual_files - expected_names
    if missing_files:
        sys.exit(f"[FAIL] {len(missing_files)} batch files missing from {BATCH_DIR} (e.g. {list(missing_files)[:3]})")
    if extra_files:
        sys.exit(f"[FAIL] {len(extra_files)} unexpected .txt files in {BATCH_DIR} (e.g. {list(extra_files)[:3]})")

    # 2. Stream global_final_ordering.txt and all batch files simultaneously
    seen_accs = set()
    cum_count = 0

    with open(GLOBAL_ORDER) as global_f:
        for exp_count, exp_cum, batch_name in expected_batches:
            batch_path = BATCH_DIR / f"{batch_name}.txt"
            with open(batch_path) as bf:
                batch_lines = [l.strip() for l in bf if l.strip()]

            # Check per-batch count
            if len(batch_lines) != exp_count:
                sys.exit(
                    f"[FAIL] {batch_name}.txt count mismatch: "
                    f"expected {exp_count}, got {len(batch_lines)}"
                )

            # Check line-by-line order against global_final_ordering.txt & check duplicates
            for line_in_batch, b_line in enumerate(batch_lines, 1):
                cum_count += 1
                g_line = global_f.readline().strip()
                if not g_line:
                    sys.exit(
                        f"[FAIL] {batch_name}.txt (global line {cum_count}) exceeds "
                        f"end of {GLOBAL_ORDER.name}!"
                    )
                if b_line != g_line:
                    sys.exit(
                        f"[FAIL] Order mismatch at global line {cum_count} "
                        f"({batch_name}.txt line {line_in_batch}):\n"
                        f"  Batch : {b_line}\n"
                        f"  Global: {g_line}"
                    )

                acc = clean_acc(b_line)
                if acc in seen_accs:
                    sys.exit(
                        f"[FAIL] Duplicate genome '{acc}' found in {batch_name}.txt "
                        f"(global line {cum_count})!"
                    )
                seen_accs.add(acc)

            if cum_count != exp_cum:
                sys.exit(
                    f"[FAIL] Cumulative count mismatch after {batch_name}: "
                    f"expected {exp_cum}, got {cum_count}"
                )

        # Ensure global_final_ordering.txt has no remaining unread lines
        leftover = [l.strip() for l in global_f if l.strip()]
        if leftover:
            sys.exit(
                f"[FAIL] Incomplete cut: {len(leftover)} genomes remaining at the end of "
                f"{GLOBAL_ORDER.name} not present in any batch!"
            )

    print(f"[PASS] Batch count verified      : {len(expected_batches):,} batch files")
    print(f"[PASS] Completeness verified     : {cum_count:,} / {cum_count:,} genomes (0 missing, 0 extra)")
    print(f"[PASS] Uniqueness verified       : {len(seen_accs):,} unique genomes (0 duplicates)")
    print(f"[PASS] Global order verified     : 100% exact line-by-line match with {GLOBAL_ORDER.name}")


if __name__ == "__main__":
    main()
```

---

## Step 3: Default AGC Recompression Across 3 Compute Nodes

### Step 3a: Split Batch Paths into 3 File-of-Files (`fof_1.txt`, `fof_2.txt`, `fof_3.txt`)

```bash
#!/usr/bin/env bash
set -euo pipefail

EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
BATCH_DIR="${EXP_DIR}/data/batches_to_compress"
FOF_DIR="${EXP_DIR}/data/fof"

mkdir -p "$FOF_DIR"
rm -f "$FOF_DIR"/batches_fof_*.txt

# Round-robin distribution across 3 FOFs (balances easy species batches and heavy unknown batches evenly across all 3 nodes)
printf "%s\n" "$BATCH_DIR"/*.txt | sort -V | awk -v dir="$FOF_DIR" '
    {
        idx = ((NR - 1) % 3) + 1
        print $0 > (dir "/batches_fof_" idx ".txt")
    }
'

wc -l "$FOF_DIR"/batches_fof_*.txt
```

---

### Step 3b: Per-Node Compression Script (`run_agc_fof.sh`)

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <batches_fof.txt> [threads=25]" >&2
    exit 1
fi

FOF="$1"
THREAD="${2:-25}"

EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
OUT_DIR="${EXP_DIR}/compression_results/agc_default"

mkdir -p "$OUT_DIR"

while IFS= read -r file || [ -n "$file" ]; do
    [ -z "$file" ] && continue

    base=$(basename "$file" .txt)
    out_agc="${OUT_DIR}/${base}.agc"

    if [ -s "$out_agc" ]; then
        echo "[SKIP] $base.agc already exists"
        continue
    fi

    echo "[COMPRESS] $base (threads=$THREAD)"
    ref=$(head -n 1 "$file")
    agc create -a -b 500 -s 1500 -t "$THREAD" -v 2 -o "$out_agc" -i "$file" "$ref"
done < "$FOF"

echo "[DONE] Completed all batches in $FOF"
```

#### Launch on 3 Compute Nodes:
- **Node 1**: `./run_agc_fof.sh /projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING/data/fof/batches_fof_1.txt 50`
- **Node 2**: `./run_agc_fof.sh /projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING/data/fof/batches_fof_2.txt 50`
- **Node 3**: `./run_agc_fof.sh /projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING/data/fof/batches_fof_3.txt 50`

---

## Step 4: Validation (`comprehensive_validation.py` — Hybrid `getcol` ($\le 3000$) + `getset -p` ($> 3000$))

Simple, race-free, bounded-memory validation strategy:
1. **Step 1/3**: Parallel `agc listset` across all 1,129 `.agc` archives.
2. **Step 2/3**: Verifies 100% inventory completeness (`0` missing, `0` extra, `0` duplicates) against `global_final_ordering.txt` and loads ground-truth `seqkit sum` hashes from `atb.metadata.r1.assembly.tsv`.
3. **Step 3/3 (Hybrid per archive)**:
   - **Archives with $\le 3,000$ genomes**: Extracts the archive synchronously into `/dev/shm` via `agc getcol -o <tmp_dir> -t 40`, runs `seqkit sum -j 40` after `agc getcol` finishes (zero race conditions, $\le 15\text{ GB}$ RAM), and deletes `<tmp_dir>`.
   - **Archives with $> 3,000$ genomes**: Uses zero `/dev/shm` space; runs `20` parallel workers executing `agc getset -p -t 2 "<agc_file>" "<raw_name>" | seqkit sum` (`-p` disables whole-archive RAM prefetching in [`CAGCBasic::load_file_type_info`](file:///Users/ktruong/tools/agc-split-size/src/common/agc_basic.cpp#L56-L59)).
   - Includes automatic archive checkpointing (`validation_done_archives_<dir>.txt`) so interrupted runs resume cleanly.

```python
#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
EXP_DIR = Path("/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING")
INPUT_DIR = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else (EXP_DIR / "compression_results/agc_default")
METADATA = EXP_DIR / "data/atb.metadata.r1.assembly.tsv"
PATH_FILE = EXP_DIR / "ordering_results/global_final_ordering.txt"

FAIL_LOG = EXP_DIR / "data" / f"validation_failures_{INPUT_DIR.name}.tsv"
DONE_LOG = EXP_DIR / "data" / f"validation_done_archives_{INPUT_DIR.name}.txt"
SHM_BASE = Path("/dev/shm") / f"agc_val_{INPUT_DIR.name}_{os.getpid()}"

HASH_COL = 4                  # 1-based column index of seqkit_sum hash in METADATA
THREADS = int(sys.argv[2]) if len(sys.argv) > 2 else 40

GETCOL_MAX_GENOMES = 3000     # Use agc getcol in /dev/shm if archive has <= 3000 genomes
GETSET_WORKERS = 20           # Number of concurrent agc getset workers for > 3000 genome archives
GETSET_THREADS = max(1, THREADS // GETSET_WORKERS)  # Threads per agc getset call (e.g. 2 or 5)
SEQKIT_CHUNK = 500            # Max file args per seqkit sum call in getcol mode


# ==============================================================================
# HELPERS
# ==============================================================================
def natural_key(path: Path):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", path.name)]


def clean_accession(raw_str: str) -> str:
    """Extract bare accession from a path or filename."""
    return raw_str.strip().split("/")[-1].split(".")[0]


def list_archive_samples(agc_file: Path):
    res = subprocess.run(["agc", "listset", str(agc_file)], capture_output=True, text=True, check=True)
    genomes = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    return agc_file, genomes


def verify_single_getset(task):
    """Stream a single sample via agc getset -p | seqkit sum (zero disk/shm usage)."""
    agc_file, raw_name, acc, meta_hash = task
    if not meta_hash:
        return False, acc, agc_file.name, "MISSING_IN_METADATA", ""

    try:
        cmd = f'agc getset -p -t {GETSET_THREADS} "{agc_file}" "{raw_name}" | seqkit sum'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        agc_hash = res.stdout.split()[0]
    except Exception as e:
        return False, acc, agc_file.name, meta_hash, f"CMD_ERROR({e})"

    return (meta_hash == agc_hash), acc, agc_file.name, meta_hash, agc_hash


# ==============================================================================
# MAIN PIPELINE
# ==============================================================================
def main():
    agc_files = sorted(INPUT_DIR.glob("*.agc"), key=natural_key)
    if not agc_files:
        sys.exit(f"[ERROR] No .agc files found in {INPUT_DIR}")

    print(f"[INFO] Target directory : {INPUT_DIR}")
    print(f"[INFO] Failure log      : {FAIL_LOG}")
    print(f"[INFO] Checkpoint log   : {DONE_LOG}")

    # 1. Parallel Inventory of all AGC archives
    print(f"[INFO] Step 1/3: Scanning {len(agc_files)} AGC archives in parallel ({THREADS} threads)...")
    all_agc_accs = set()
    archive_to_raw_names = {}
    duplicate_accs = []

    with ThreadPoolExecutor(max_workers=THREADS) as pool:
        for agc_file, genomes in pool.map(list_archive_samples, agc_files):
            for raw_name in genomes:
                acc = clean_accession(raw_name)
                if acc in all_agc_accs:
                    duplicate_accs.append((acc, agc_file.name))
                all_agc_accs.add(acc)
            archive_to_raw_names[agc_file] = genomes

    # 2. Verify 100% Completeness & Load Metadata Hashes
    print("[INFO] Step 2/3: Checking 100% inventory completeness and loading metadata hashes...")
    with open(PATH_FILE) as f:
        expected_accs = {clean_accession(line) for line in f if line.strip()}

    missing = expected_accs - all_agc_accs
    extra = all_agc_accs - expected_accs

    if missing or extra or duplicate_accs:
        sys.exit(
            f"[FAIL] Inventory mismatch: "
            f"missing={len(missing):,}, extra={len(extra):,}, duplicates={len(duplicate_accs):,}"
        )
    print(f"[PASS] 100% inventory check passed: all {len(expected_accs):,} unique genomes present in AGC.")

    acc_to_meta_hash = {}
    col_idx = HASH_COL - 1
    with open(METADATA) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > col_idx:
                acc = parts[0].strip()
                if acc in all_agc_accs:
                    acc_to_meta_hash[acc] = parts[col_idx].strip()

    # Load checkpoint of already-validated archives if resuming
    completed_archives = set()
    if DONE_LOG.exists():
        with open(DONE_LOG) as f:
            completed_archives = {line.strip() for line in f if line.strip()}

    fail_mode = "a" if completed_archives and FAIL_LOG.exists() else "w"

    # 3. Hybrid Validation
    total = len(all_agc_accs)
    print(
        f"[INFO] Step 3/3: Verifying {total:,} genomes across {len(agc_files)} archives "
        f"(<= {GETCOL_MAX_GENOMES}: getcol in /dev/shm | > {GETCOL_MAX_GENOMES}: {GETSET_WORKERS}x getset -p -t {GETSET_THREADS})..."
    )
    passed = 0
    failed = 0
    done_idx = 0

    with open(FAIL_LOG, fail_mode) as fail_out, open(DONE_LOG, "a") as done_out:
        if fail_mode == "w":
            fail_out.write("accession\tagc_archive\tmetadata_hash\tagc_hash\n")

        for arch_idx, agc_file in enumerate(agc_files, start=1):
            raw_names = archive_to_raw_names[agc_file]
            n_arch = len(raw_names)

            if agc_file.name in completed_archives:
                done_idx += n_arch
                passed += n_arch
                print(f"[SKIP] Archive {arch_idx}/{len(agc_files)} ({agc_file.name}) already verified ({n_arch:,} genomes)", flush=True)
                continue

            # ------------------------------------------------------------------
            # CASE A: Small/Medium Archive (<= 3000 genomes) -> agc getcol
            # ------------------------------------------------------------------
            if n_arch <= GETCOL_MAX_GENOMES:
                tmp_dir = SHM_BASE / agc_file.stem
                shutil.rmtree(tmp_dir, ignore_errors=True)
                tmp_dir.mkdir(parents=True, exist_ok=True)

                try:
                    subprocess.run(
                        ["agc", "getcol", "-o", str(tmp_dir), "-t", str(THREADS), str(agc_file)],
                        capture_output=True, text=True, check=True
                    )

                    fasta_files = [str(p) for p in tmp_dir.iterdir() if p.is_file()]
                    extracted_hashes = {}
                    for i in range(0, len(fasta_files), SEQKIT_CHUNK):
                        chunk = fasta_files[i : i + SEQKIT_CHUNK]
                        res = subprocess.run(
                            ["seqkit", "sum", "-j", str(THREADS)] + chunk,
                            capture_output=True, text=True, check=True
                        )
                        for line in res.stdout.splitlines():
                            if not line.strip():
                                continue
                            h, fpath = line.split(None, 1)
                            extracted_hashes[clean_accession(fpath)] = h

                    for raw_name in raw_names:
                        acc = clean_accession(raw_name)
                        done_idx += 1
                        meta_h = acc_to_meta_hash.get(acc, "MISSING_IN_METADATA")
                        agc_h = extracted_hashes.get(acc, "MISSING_EXTRACTION")

                        if meta_h == agc_h:
                            passed += 1
                        else:
                            failed += 1
                            print(
                                f"[FAIL] Hash mismatch for {acc} in {agc_file.name}:\n"
                                f"       Metadata : {meta_h}\n"
                                f"       AGC      : {agc_h}",
                                file=sys.stderr, flush=True
                            )
                            fail_out.write(f"{acc}\t{agc_file.name}\t{meta_h}\t{agc_h}\n")
                            fail_out.flush()
                finally:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

            # ------------------------------------------------------------------
            # CASE B: Large Archive (> 3000 genomes) -> parallel agc getset -p
            # ------------------------------------------------------------------
            else:
                print(
                    f"[LARGE] Archive {arch_idx}/{len(agc_files)} ({agc_file.name}) has {n_arch:,} genomes "
                    f"-> streaming with {GETSET_WORKERS} workers (agc getset -p -t {GETSET_THREADS})...",
                    flush=True
                )
                tasks = [
                    (agc_file, raw_name, clean_accession(raw_name), acc_to_meta_hash.get(clean_accession(raw_name)))
                    for raw_name in raw_names
                ]
                arch_done = 0
                with ThreadPoolExecutor(max_workers=GETSET_WORKERS) as pool:
                    futures = [pool.submit(verify_single_getset, t) for t in tasks]
                    for fut in as_completed(futures):
                        ok, acc, arch_name, meta_h, agc_h = fut.result()
                        done_idx += 1
                        arch_done += 1
                        if ok:
                            passed += 1
                        else:
                            failed += 1
                            print(
                                f"[FAIL] Hash mismatch for {acc} in {arch_name}:\n"
                                f"       Metadata : {meta_h}\n"
                                f"       AGC      : {agc_h}",
                                file=sys.stderr, flush=True
                            )
                            fail_out.write(f"{acc}\t{arch_name}\t{meta_h}\t{agc_h}\n")
                            fail_out.flush()

                        if arch_done % 1000 == 0 or arch_done == n_arch:
                            print(
                                f"  [LARGE-PROGRESS] {agc_file.name}: {arch_done:,}/{n_arch:,} "
                                f"(total {done_idx:,}/{total:,} | {passed:,} passed, {failed:,} failed)",
                                flush=True
                            )

            done_out.write(f"{agc_file.name}\n")
            done_out.flush()

            print(
                f"[PROGRESS] Archive {arch_idx}/{len(agc_files)} ({agc_file.name}) | "
                f"{done_idx:,}/{total:,} genomes ({passed:,} passed, {failed:,} failed)",
                flush=True
            )

    shutil.rmtree(SHM_BASE, ignore_errors=True)
    print("=" * 66)
    if failed == 0:
        print(f"[SUCCESS] All good in {INPUT_DIR.name}! 100% inventory verified ({len(expected_accs):,} genomes) "
              f"and {passed:,}/{total:,} genomes matched metadata checksums.")
        sys.exit(0)
    else:
        print(f"[ERROR] Validation failed in {INPUT_DIR.name}: {failed:,} failed, {passed:,} passed out of {total:,}. "
              f"See {FAIL_LOG}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

#### Launch Commands:
```bash
EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"

# Clean any leftover /dev/shm files and reset false-positive checkpoint from prior killed run
rm -rf /dev/shm/agc_val_*
rm -f "${EXP_DIR}/data/validation_done_archives_agc_split_size_no_divisions.txt"
rm -f "${EXP_DIR}/data/validation_failures_agc_split_size_no_divisions.tsv"

# 1. Validate agc_split_size_no_divisions
python3 "${EXP_DIR}/script/comprehensive_validation.py" "${EXP_DIR}/compression_results/agc_split_size_no_divisions" 40 \
    > "${EXP_DIR}/data/validation_agc_split_size_no_divisions.log" 2>&1

# 2. Validate agc_default
python3 "${EXP_DIR}/script/comprehensive_validation.py" "${EXP_DIR}/compression_results/agc_default" 40 \
    > "${EXP_DIR}/data/validation_agc_default.log" 2>&1
```

---

## 5. Full 100% Audit Results (All 3,092,278 Genomes Across 1,129 Archives)

Completed on compute node `cl1n047` on 2026-10-13 at 04:02 AM using the hybrid memory-mapped validator (`comprehensive_validation.py`).

### 5.1 Audit Summary Statistics
- **Total Archives**: 1,129
- **Total Assemblies Evaluated**: 3,092,278
- **Genomes Bit-for-Bit Verified**: **3,092,181 / 3,092,278 (99.99686%)**
- **100% Clean Archives**: **1,109 / 1,129 archives (98.23%)**
- **Discrepant Genomes**: **97 genomes** across **20 archives** (1.77% of archives)

---

### 5.2 Root-Cause Breakdown of All 97 Discrepancies

| Category | Genomes | Archives Affected | Underlying Mechanism | Root Cause Classification |
| :--- | :---: | :---: | :--- | :--- |
| **Poly-A Splitter Corruption (Expansion)** | 80 | 18 | `len(agc) > len(fa)` due to Pass 1 segment retention colliding with Pass 2 segments after `A^31` splitter | Upstream AGC Bug (`kmer_dir == 0ull`) |
| **Poly-A Splitter Corruption (Truncation)** | 15 | 8 | `len(agc) < len(fa)` due to Pass 1 segment retention overwriting Pass 2 segments | Upstream AGC Bug (`kmer_dir == 0ull`) |
| **Outdated Metadata Hash** | 1 | 1 (`part249`) | `SAMN16418392`: Archive matches local `set2_2024-08` assembly, but official `r1` assembly has 121 contigs vs 36 contigs | Assembly version mismatch (not AGC bug) |
| **Corrupted Source FASTA** | 1 | 1 (`part199`) | `SAMN50311804`: Source file has 1,434 `\x00` null bytes stripped by AGC's `c > 64` nucleotide filter | Upstream Data Corruption (not AGC bug) |
| **Total** | **97** | **20** | | |

#### Detailed Analysis of Non-AGC Anomalies:

1. **`SAMN50311804` (`part199`)**:
   - Source file: `/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_2026-03/SAMN50311804.fa.gz`
   - FASTA Header: `>SAMN50311804.contig00045 len=45190 cov=46.0 corr=43756 ...`
   - Investigation showed 1,434 literal null bytes (`\x00`) scattered in the sequence text from an interrupted filesystem write.
   - AGC's nucleotide reader (`CGenomeIO::read_contig` in `genome_io.cpp:285`) strictly enforces `if (c > 64)`, discarding `\x00` characters:
     $$45,190\text{ raw bytes} - 1,434\text{ null bytes } (\mathtt{\backslash x00}) = \mathbf{43,756\text{ bp}}$$
   - The sequence preserved by AGC is the exact, valid nucleotide sequence. `seqkit sum` previously included the raw corrupted `\x00` bytes in its hash.

2. **`SAMN16418392` (`part249`)**:
   - `part249.agc` was bit-for-bit identical to `/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_set2_2024-08/SAMN16418392.fa.gz` (hash `c877f341d50002444627cacb164fc842`, 36 contigs, 4,254,738 bp).
   - However, official `r1` on S3 (`https://allthebacteria-assemblies.s3.eu-west-2.amazonaws.com/SAMN16418392.fa.gz`) is the newer/complete assembly (hash `d8229e2491d6d2cf904fc5e74aa5784b`, 121 contigs, 4,637,530 bp).
   - The local file in `set2_2024-08` was an older length-filtered version.

---

### 5.3 Complete Manifest of the 20 Archives to Recompress

- **19 Poly-A Corrupted Batches** (to recompress without `-a`):
  `part003`, `part051`, `part059`, `part170`, `part199`, `part223`, `part257`, `part263`, `part325`, `part435`, `part586`, `part691`, `part851`, `part862`, `part929`, `part995`, `part1008`, `part1021`, `part1042`
- **1 Outdated Assembly Batch** (`part249`):
  Updated `SAMN16418392.fa.gz` with official `r1` assembly before recompressing without `-a`.

---

### 5.4 Complete Ledger of All 97 Discrepant Genomes

| Accession | Archive | Metadata Hash (`atb.metadata.r1.assembly.tsv`) | AGC Extracted Hash (`v1_adaptive`) | Root Cause Category |
| :--- | :--- | :--- | :--- | :--- |
| `SAMEA5584514` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_eb3827f8714eca3324fee050a0d59cb6` | `seqkit.v0.1_DLS_k0_b997be90597bfef363b3a69b0132f282` | Poly-A Splitter Corruption |
| `SAMEA5584600` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_9424396f7f1f6290e42b7776487cb89c` | `seqkit.v0.1_DLS_k0_30780fd5bb763a769c9130c6759073b1` | Poly-A Splitter Corruption (`contig00047` duplicate) |
| `SAMEA5584805` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_b0e9c386df9d9caa26752c6affbe9cd8` | `seqkit.v0.1_DLS_k0_a25e640ede3b99a9063b3da6d4a6bc7d` | Poly-A Splitter Corruption |
| `SAMEA5585239` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_3bca08a90b53a6f1d9dfed191cbd88a1` | `seqkit.v0.1_DLS_k0_2cecd7cf49b9e8e68ddc3a89d6a9100f` | Poly-A Splitter Corruption |
| `SAMEA5607350` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_d6114041cc983108e289091813f0d356` | `seqkit.v0.1_DLS_k0_d0f3484f1d36b89036a2eace30832a23` | Poly-A Splitter Corruption |
| `SAMN30525386` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_7af57b549307236ca15063e49fa229b6` | `seqkit.v0.1_DLS_k0_a31bed4f8a4ed4e575ebb75763ff8906` | Poly-A Splitter Corruption |
| `SAMN36381905` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_4e93b4144326dfd058e69d5a3e621434` | `seqkit.v0.1_DLS_k0_5f3c567c42d6c2789c19e30131653acc` | Poly-A Splitter Corruption |
| `SAMN45299503` | `atb.assembly.r1.part003.agc` | `seqkit.v0.1_DLS_k0_fe4569fa0f4d084a483abbc606418970` | `seqkit.v0.1_DLS_k0_83db0012f41fec4f63251b35fbdf1f09` | Poly-A Splitter Corruption |
| `SAMEA5168152` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_09688d19232b37df411766cb1a6e13bc` | `seqkit.v0.1_DLS_k0_de86deb2021bd0036b9ef21213c20184` | Poly-A Splitter Corruption |
| `SAMEA5168235` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_6add5d30a00e5f9046951e3cd5f60a5b` | `seqkit.v0.1_DLS_k0_c433eeafc4b9019e939a30af0712a5a6` | Poly-A Splitter Corruption (`contig00123` duplicate) |
| `SAMEA5168340` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_602fceb8f080e0b9692fd193e910e19e` | `seqkit.v0.1_DLS_k0_ab932717b9e616e8a92a03c81c010e7e` | Poly-A Splitter Corruption |
| `SAMN00254361` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_c8310b91262ce2c7d7167d5fb9e8585b` | `seqkit.v0.1_DLS_k0_c90af195324614c83bafa50a64920b33` | Poly-A Splitter Corruption |
| `SAMN00254375` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_00ebe78250f86d7acaae7501fb197980` | `seqkit.v0.1_DLS_k0_e38ffaa0b4f3cd4be36cc12bb67e1237` | Poly-A Splitter Corruption |
| `SAMN04145899` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_4771d49acf9ce8678b7907b6c37d27c3` | `seqkit.v0.1_DLS_k0_f877eff24eff6b14d9a6f76eab7ce359` | Poly-A Splitter Corruption |
| `SAMN04432834` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_199cdcb728d2d9a1578741dd927a399c` | `seqkit.v0.1_DLS_k0_2b4cbe728d1feddef2544b6e059986e4` | Poly-A Splitter Corruption |
| `SAMN06233881` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_ff57435da5ddd5212a6dbfa04267d8a6` | `seqkit.v0.1_DLS_k0_f5c80771acf9439e3495206199af05b0` | Poly-A Splitter Corruption |
| `SAMN41386527` | `atb.assembly.r1.part051.agc` | `seqkit.v0.1_DLS_k0_98d9f08c46895fa66921be4cc16b82c2` | `seqkit.v0.1_DLS_k0_e66594274e2396d0a4e3c84a85dc2016` | Poly-A Splitter Corruption |
| `SAMN14613997` | `atb.assembly.r1.part059.agc` | `seqkit.v0.1_DLS_k0_02d0883d7aa979360ca84dcc23109679` | `seqkit.v0.1_DLS_k0_a9195bdb179c3e08b65f2efa9cde7b80` | Poly-A Splitter Corruption |
| `SAMN14613996` | `atb.assembly.r1.part059.agc` | `seqkit.v0.1_DLS_k0_9db1bc3f218eea5fdbc528d70ae23fc0` | `seqkit.v0.1_DLS_k0_ae056f2cb1145ca32520284e363fe4b6` | Poly-A Splitter Corruption |
| `SAMN38380409` | `atb.assembly.r1.part059.agc` | `seqkit.v0.1_DLS_k0_660440fda8b347b30cd8c350dc3dff62` | `seqkit.v0.1_DLS_k0_ab202ea82b97c5c25f6a4184d5974391` | Poly-A Splitter Corruption |
| `SAMN44459156` | `atb.assembly.r1.part059.agc` | `seqkit.v0.1_DLS_k0_5216d5ab760d9dae803873c20600eec2` | `seqkit.v0.1_DLS_k0_3d164bf491d4ee67c38476bfb555a43e` | Poly-A Splitter Corruption |
| `SAMEA788084` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_8969f871e1a116e7a80fc9f7bd5be978` | `seqkit.v0.1_DLS_k0_38bf77a727265454ac3f8e282b9906da` | Poly-A Splitter Corruption |
| `SAMN11156862` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_3a422c7ceb88dd035dfb8c23691a629e` | `seqkit.v0.1_DLS_k0_181f3a5c3bf29cd6f45bb91cc55c5593` | Poly-A Splitter Corruption |
| `SAMN15058883` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_20e2e3214c78ae645fc14de7a97f6cd3` | `seqkit.v0.1_DLS_k0_97017709b7c235649734accd433b85bb` | Poly-A Splitter Corruption |
| `SAMN16124828` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_67fbcffa749ea1645d83b2155a7a8a17` | `seqkit.v0.1_DLS_k0_6918129f0b272c21b117387a8e4334d6` | Poly-A Splitter Corruption |
| `SAMN24595945` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_6c9decced7926375cd5c72254184c6e7` | `seqkit.v0.1_DLS_k0_298ffde93ace530a71c59f7caa1ee5e9` | Poly-A Splitter Corruption |
| `SAMN27568347` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_931a1a78e8d300d118a9be85416ea34d` | `seqkit.v0.1_DLS_k0_1f906104dfb0433f19436881a087566d` | Poly-A Splitter Corruption |
| `SAMN35670649` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_c1bcf8364a0c8038cc38cfd6ef533d14` | `seqkit.v0.1_DLS_k0_fbcb0560922cb682c8f78b6b68d18e51` | Poly-A Splitter Corruption |
| `SAMN35670694` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_c67db368da637f827db9c70960f2bd9f` | `seqkit.v0.1_DLS_k0_f3519b438f90c3bc881bdf6bc9bd9724` | Poly-A Splitter Corruption |
| `SAMN35680156` | `atb.assembly.r1.part170.agc` | `seqkit.v0.1_DLS_k0_faa293c188ad338316b120753d314d5a` | `seqkit.v0.1_DLS_k0_bc752913aeee0e3ff8c44d2863625f7b` | Poly-A Splitter Corruption |
| `SAMN50311804` | `atb.assembly.r1.part199.agc` | `seqkit.v0.1_DLS_k0_23ccdc0348e3f76482bf716e5e4a5bd1` | `seqkit.v0.1_DLS_k0_7832d9dfa1b5c3b1483c27a3898a3863` | Source file has 1,434 `\x00` null bytes stripped by AGC (`c>64`) |
| `SAMEA120483379` | `atb.assembly.r1.part223.agc` | `seqkit.v0.1_DLS_k0_364b537013681209d0394f7f898f4aa0` | `seqkit.v0.1_DLS_k0_15de37fd53523ee998436bd78ce9c7dd` | Poly-A Splitter Corruption |
| `SAMN16418392` | `atb.assembly.r1.part249.agc` | `seqkit.v0.1_DLS_k0_d8229e2491d6d2cf904fc5e74aa5784b` | `seqkit.v0.1_DLS_k0_c877f341d50002444627cacb164fc842` | Old set2 assembly on disk (36 contigs vs 121 in r1) |
| `SAMN14409463` | `atb.assembly.r1.part257.agc` | `seqkit.v0.1_DLS_k0_9a7e89c581a14de11b5265fe942ecf2e` | `seqkit.v0.1_DLS_k0_e34cc5fa18ee2720fc9ee31c0fb3ff5e` | Poly-A Splitter Corruption |
| `SAMN02368922` | `atb.assembly.r1.part263.agc` | `seqkit.v0.1_DLS_k0_e5e35c535870383e3bccf46eb4c69dc9` | `seqkit.v0.1_DLS_k0_735ca944eae163cf6492c06794612d76` | Poly-A Splitter Corruption |
| `SAMN26750229` | `atb.assembly.r1.part263.agc` | `seqkit.v0.1_DLS_k0_b8eede67cf2ed0a120a453505ea45b09` | `seqkit.v0.1_DLS_k0_6fa685230b43154f70c779d1bfa1652a` | Poly-A Splitter Corruption |
| `SAMN20156324` | `atb.assembly.r1.part325.agc` | `seqkit.v0.1_DLS_k0_d57202fe04e7cb47b045a8500a147a35` | `seqkit.v0.1_DLS_k0_403363fe5e04bbbfca9344b8311a59d1` | Poly-A Splitter Corruption |
| `SAMEA1317031` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_ac384cad8af38384103ebe03839a0572` | `seqkit.v0.1_DLS_k0_65a52aec0ec271158e6ba4fd4e8c95ee` | Poly-A Splitter Corruption |
| `SAMEA1317035` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_62fdf62d8419f8c5580a802aad5664b3` | `seqkit.v0.1_DLS_k0_07daee864fc87621d39947dc4be966cc` | Poly-A Splitter Corruption |
| `SAMEA1317050` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_845766b4f1e6b93700504213b5500d64` | `seqkit.v0.1_DLS_k0_750b1b7d4264388fa321921871887d83` | Poly-A Splitter Corruption |
| `SAMEA1317057` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_d0c3b7593b74e5d62dc252a121063b92` | `seqkit.v0.1_DLS_k0_1c05dc4600379ec0b20b4834efbecc60` | Poly-A Splitter Corruption |
| `SAMEA1317074` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_43ca7d8c4a0e9e6bb82732d486ea15e5` | `seqkit.v0.1_DLS_k0_e6df8e2fadb6b2a02a5c327f1084117c` | Poly-A Splitter Corruption |
| `SAMEA1568495` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_6419917db0b75dcdb658c6163a9987d0` | `seqkit.v0.1_DLS_k0_d11db7ecd9bc6eb54c81897dbedd135e` | Poly-A Splitter Corruption |
| `SAMEA1568525` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_abd78dabbe7c80dc500be65dc0424e46` | `seqkit.v0.1_DLS_k0_b9168695ad80a7bf87484ab4f780ef08` | Poly-A Splitter Corruption |
| `SAMEA1568528` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_0fd6fd97f27317d633ffcac658188cff` | `seqkit.v0.1_DLS_k0_5273da07d80db9916dac0e921dc485af` | Poly-A Splitter Corruption |
| `SAMEA1975309` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_eebf544a90420c90b1807f360d4d34ab` | `seqkit.v0.1_DLS_k0_a5b80b17461049aaba09830e7bc4c494` | Poly-A Splitter Corruption |
| `SAMN09533017` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_3794206671c406b05bafbb0ec26631c4` | `seqkit.v0.1_DLS_k0_7b9cb801bdbfd300c745137ff0785ad3` | Poly-A Splitter Corruption |
| `SAMN13910019` | `atb.assembly.r1.part435.agc` | `seqkit.v0.1_DLS_k0_d8aa4ad1c7380068f162e5c79c33cf0d` | `seqkit.v0.1_DLS_k0_991bc45b82a6d0eb1573126a130c2b5a` | Poly-A Splitter Corruption |
| `SAMN37144422` | `atb.assembly.r1.part586.agc` | `seqkit.v0.1_DLS_k0_92f1255192cef26e076cf9e7389a2087` | `seqkit.v0.1_DLS_k0_c91a9b67f6572cbef7d1e8a88b09c77a` | Poly-A Splitter Corruption |
| `SAMN15599328` | `atb.assembly.r1.part691.agc` | `seqkit.v0.1_DLS_k0_1a58b48d6dac852a1a84ea7f285eeeb4` | `seqkit.v0.1_DLS_k0_1c51e94ac34a17d65c7bbd21798258c4` | Poly-A Splitter Corruption |
| `SAMN38338186` | `atb.assembly.r1.part691.agc` | `seqkit.v0.1_DLS_k0_be95096fb50ff41847acfda449535552` | `seqkit.v0.1_DLS_k0_a0933af37b6e7dedb868051828d59287` | Poly-A Splitter Corruption |
| `SAMN38338189` | `atb.assembly.r1.part691.agc` | `seqkit.v0.1_DLS_k0_62ad6b8a43c0ae275dfdf5dd032affee` | `seqkit.v0.1_DLS_k0_79adc5b80e14487ebea3adbd11b4003c` | Poly-A Splitter Corruption |
| `SAMN38338191` | `atb.assembly.r1.part691.agc` | `seqkit.v0.1_DLS_k0_b5c4200982d9ced6e6d484fd14b21860` | `seqkit.v0.1_DLS_k0_de8e20a2cb7c88186238bacea048ca73` | Poly-A Splitter Corruption |
| `SAMN38338195` | `atb.assembly.r1.part691.agc` | `seqkit.v0.1_DLS_k0_d8ef3eba962fab974dfcfc6770a8a38e` | `seqkit.v0.1_DLS_k0_23d464a7712ef98f16ee369248706d31` | Poly-A Splitter Corruption |
| `SAMEA112850281` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_55e2231bcfca0bdb6e32b49d6ed0a0de` | `seqkit.v0.1_DLS_k0_5d1e5f9e54ec975985fda7d7b8d962d4` | Poly-A Splitter Corruption |
| `SAMEA115029126` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_0633036250271585e4e8515c4dd45448` | `seqkit.v0.1_DLS_k0_d25134a2070eec81a148697c0686b933` | Poly-A Splitter Corruption |
| `SAMEA12277416` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_4d38d3d7e8ffc55d428c43ba98f7a7ba` | `seqkit.v0.1_DLS_k0_40e9e19a2df0c9eb733c7391918a9a67` | Poly-A Splitter Corruption |
| `SAMEA12278046` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_a68bce0b64c516b144bdc7f10954b5ac` | `seqkit.v0.1_DLS_k0_7a24b2284fc26ccd31d9fd0e88ca3cca` | Poly-A Splitter Corruption |
| `SAMEA3431742` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_02ec21f12a4c21749767cc20daae5eca` | `seqkit.v0.1_DLS_k0_e8475cb747db029b5685b5eeecb85e97` | Poly-A Splitter Corruption |
| `SAMEA6506537` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_be911ee8740dc94b9c662bb0bddbed96` | `seqkit.v0.1_DLS_k0_0c3965298655f1bf005aba210f49dbdf` | Poly-A Splitter Corruption |
| `SAMEA6534150` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_1a0def237bad58396bab7a02be63c7c2` | `seqkit.v0.1_DLS_k0_1b4777c934c8d744a235e60e13f094f5` | Poly-A Splitter Corruption |
| `SAMEA6534447` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_b7f4abecac689a7400d0acf99c71598e` | `seqkit.v0.1_DLS_k0_38e0715024aef19e22cfba7f3ef16f56` | Poly-A Splitter Corruption |
| `SAMN00102973` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_ca9906273c13dee0f9c31f2153bee4d3` | `seqkit.v0.1_DLS_k0_e0130fb050a3472d550b7fc6c7460630` | Poly-A Splitter Corruption |
| `SAMN11038155` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_cbcc61a73169e1c4ce868fa7c2a92cc4` | `seqkit.v0.1_DLS_k0_1f59ba8cd26f90f841bb4b045bd8fe91` | Poly-A Splitter Corruption |
| `SAMN13672906` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_ba4a72e5712d7734c45d992b0c2bcd66` | `seqkit.v0.1_DLS_k0_d4ff9cef7a7e92fa470950f76775dba7` | Poly-A Splitter Corruption |
| `SAMN22254740` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_4a5205821be2348eaea5567677b492f9` | `seqkit.v0.1_DLS_k0_33f6943d17e8998e40fee04b03491dd8` | Poly-A Splitter Corruption |
| `SAMN22254959` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_c49f485890ce72123e430b5dd8d08873` | `seqkit.v0.1_DLS_k0_4cb5d5794d1418a21eb37910e2d6562c` | Poly-A Splitter Corruption |
| `SAMN22255027` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_af3ed6cc73604e0a2da80b4d77151f20` | `seqkit.v0.1_DLS_k0_1bc680a67bf34be1650314beda405120` | Poly-A Splitter Corruption |
| `SAMN22255128` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_461e7e5a2779ac6e2827e4acf459b327` | `seqkit.v0.1_DLS_k0_ea0635d5cce9c2c1902fc1ed719301f0` | Poly-A Splitter Corruption |
| `SAMN23828994` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_3ab4abb87b32ebd9b5f5cc04355ea66e` | `seqkit.v0.1_DLS_k0_c7f0994fcbfaf11120e8dc819f473e79` | Poly-A Splitter Corruption |
| `SAMN28606669` | `atb.assembly.r1.part851.agc` | `seqkit.v0.1_DLS_k0_7db7931290d6b2fcb00244f6d0492950` | `seqkit.v0.1_DLS_k0_52a796d823d39b3cd5de20e72611cb22` | Poly-A Splitter Corruption |
| `SAMN06330677` | `atb.assembly.r1.part862.agc` | `seqkit.v0.1_DLS_k0_8878807af83bc5e70a84a80352ca54db` | `seqkit.v0.1_DLS_k0_8d00d942bf6bad07029b95a4eafc06f0` | Poly-A Splitter Corruption |
| `SAMN41082490` | `atb.assembly.r1.part929.agc` | `seqkit.v0.1_DLS_k0_8060bfa07cf80266766dd2c2fc6ff1da` | `seqkit.v0.1_DLS_k0_b3aa0416005a6d073324acc34cdf7219` | Poly-A Splitter Corruption |
| `SAMN41082521` | `atb.assembly.r1.part929.agc` | `seqkit.v0.1_DLS_k0_161d30d6ab2a4e978ffcea67774954ba` | `seqkit.v0.1_DLS_k0_e105bf0f17d7585be9f9926faaae8331` | Poly-A Splitter Corruption |
| `SAMN06342717` | `atb.assembly.r1.part995.agc` | `seqkit.v0.1_DLS_k0_b7a4785a2f66cd41e5d03c1d72d5e88e` | `seqkit.v0.1_DLS_k0_28c57dfd1622450ba9dace15c0f40f64` | Poly-A Splitter Corruption |
| `SAMN06342720` | `atb.assembly.r1.part995.agc` | `seqkit.v0.1_DLS_k0_5e0f5a9e19ef72188ea881e7a6869485` | `seqkit.v0.1_DLS_k0_9b86216dcbd6f82a60460efa48cc9448` | Poly-A Splitter Corruption |
| `SAMN08714393` | `atb.assembly.r1.part995.agc` | `seqkit.v0.1_DLS_k0_7bc42b452029b05115f7663a7c704ff2` | `seqkit.v0.1_DLS_k0_72db7f6a0c1417ec7a7138be8db27499` | Poly-A Splitter Corruption |
| `SAMN08714400` | `atb.assembly.r1.part995.agc` | `seqkit.v0.1_DLS_k0_b19ed4c0d1ac5244eca71d5ff6f02bd4` | `seqkit.v0.1_DLS_k0_2de7e7d28ab84aa973892a7ee3021eec` | Poly-A Splitter Corruption |
| `SAMN08714402` | `atb.assembly.r1.part995.agc` | `seqkit.v0.1_DLS_k0_96d3cf7ef53d5ab726f681ff95321ca0` | `seqkit.v0.1_DLS_k0_6899f19799f223c8bd5b2bfd0047bc50` | Poly-A Splitter Corruption |
| `SAMEA1027304` | `atb.assembly.r1.part1008.agc` | `seqkit.v0.1_DLS_k0_4f81e207bb8e092b72af53f8e09faa44` | `seqkit.v0.1_DLS_k0_b0bc1c3b4d9c64d4db87ab9f8d41f606` | Poly-A Splitter Corruption |
| `SAMN06233763` | `atb.assembly.r1.part1008.agc` | `seqkit.v0.1_DLS_k0_f6be1c65c25766e2695e4f3f215f706b` | `seqkit.v0.1_DLS_k0_b28710b5821c1e8ce4b68ba42d08eb31` | Poly-A Splitter Corruption |
| `SAMN35710989` | `atb.assembly.r1.part1008.agc` | `seqkit.v0.1_DLS_k0_9dfa9953f05494bcdf9278a9ed436491` | `seqkit.v0.1_DLS_k0_762811d3cfcea08d6a23efc3efe94550` | Poly-A Splitter Corruption |
| `SAMN37069437` | `atb.assembly.r1.part1008.agc` | `seqkit.v0.1_DLS_k0_2f9b3b122c2cd353ab018e76c3aea5bd` | `seqkit.v0.1_DLS_k0_5e4695e20b2c9801994ecd7044a05350` | Poly-A Splitter Corruption |
| `SAMN40038605` | `atb.assembly.r1.part1008.agc` | `seqkit.v0.1_DLS_k0_b4ba2828aa8b4a38ff2124ac1e5a703c` | `seqkit.v0.1_DLS_k0_e5406b25867916c9e1072d11ebab22da` | Poly-A Splitter Corruption |
| `SAMN42436693` | `atb.assembly.r1.part1008.agc` | `seqkit.v0.1_DLS_k0_9be34d1885a0dacace153385cc92a778` | `seqkit.v0.1_DLS_k0_f82f9c4dd3a88e4746b4fb58c2d2ba86` | Poly-A Splitter Corruption |
| `SAMEA1094360` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_c4902eefe63cc09bc4e861308dd84937` | `seqkit.v0.1_DLS_k0_2fe5174e1c56efe9ae8fd9916f7ce678` | Poly-A Splitter Corruption |
| `SAMEA1398273` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_29c24c041597e7288dfbfe9315630e18` | `seqkit.v0.1_DLS_k0_e3c54b257e2ca6a4b194c8713844e4fa` | Poly-A Splitter Corruption |
| `SAMEA1398288` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_e971b3a94cbcdb6ac4c5a4a64a6b2814` | `seqkit.v0.1_DLS_k0_8534365ba6d84dd2c7cca93ad3ee95b2` | Poly-A Splitter Corruption |
| `SAMEA1559275` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_7fcb27d9d268bf5341145693468640a9` | `seqkit.v0.1_DLS_k0_b14d30ed082965d6fd27d7fc46e963ce` | Poly-A Splitter Corruption |
| `SAMEA1568507` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_6741d524d5f9ee73f65cf49b57055c1d` | `seqkit.v0.1_DLS_k0_2c319832f668b35174abba40634f2c9e` | Poly-A Splitter Corruption |
| `SAMEA1568538` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_4341f3541e45b61b89c2fa47ea23e208` | `seqkit.v0.1_DLS_k0_26eb1bad0c4d71ee6e746f7f7f7f2d6e` | Poly-A Splitter Corruption |
| `SAMEA4555923` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_bb5dd55130a98f5ce6cf27e15ece3607` | `seqkit.v0.1_DLS_k0_0172bca37b9f2cafb56ddef65417f340` | Poly-A Splitter Corruption |
| `SAMN37528854` | `atb.assembly.r1.part1021.agc` | `seqkit.v0.1_DLS_k0_e27ed4c62478f284550a9820bc476090` | `seqkit.v0.1_DLS_k0_421472495ac45cf3f2e2b7c9a64b6c59` | Poly-A Splitter Corruption |
| `SAMEA11761439` | `atb.assembly.r1.part1042.agc` | `seqkit.v0.1_DLS_k0_3ae27e22e8cee7db1b8caa343f94ca32` | `seqkit.v0.1_DLS_k0_b1fd4eb99ea02fa3748bf715a5acbd14` | Poly-A Splitter Corruption |
| `SAMEA5607322` | `atb.assembly.r1.part1042.agc` | `seqkit.v0.1_DLS_k0_db37f98c14da27330b2480cd65160497` | `seqkit.v0.1_DLS_k0_e8091c5390b4fc4677b16c61853e2bbf` | Poly-A Splitter Corruption |
| `SAMN44235814` | `atb.assembly.r1.part1042.agc` | `seqkit.v0.1_DLS_k0_0db00e71a2ddd9a87616c8d19fc963ed` | `seqkit.v0.1_DLS_k0_c7d4f7759666839c6f785526f5acff9c` | Poly-A Splitter Corruption |
| `SAMN51184549` | `atb.assembly.r1.part1042.agc` | `seqkit.v0.1_DLS_k0_43c84e46539da674ca170172080c9c83` | `seqkit.v0.1_DLS_k0_f57793b05f322b81015f1adfcab20dfd` | Poly-A Splitter Corruption |

---

## 6. Modular Recompression & Zero-Breakage Symlink Strategy


To preserve all original runs (for bug reporting and audit reproducibility) and avoid modifying hardcoded paths in existing scripts, use a versioned store with a symlink overlay.

### 6.1 Architecture Overview

```text
experiments/124_EXPE_ATB202603_ORDERING/compression_results/
├── .archive_store/
│   ├── agc_split_size_no_divisions_v1_adaptive/    <-- Original 1,129 archives (untouched backup)
│   ├── agc_split_size_no_divisions_v2_patch/       <-- Only the 20 recompressed archives
│   ├── agc_default_v1_adaptive/                    <-- Original 1,129 archives (untouched backup)
│   └── agc_default_v2_patch/                       <-- Only the 20 recompressed archives
│
├── agc_split_size_no_divisions/                    <-- Active directory containing 1,129 symlinks
│   ├── part001.agc -> ../.archive_store/..._v1_adaptive/part001.agc
│   ├── part003.agc -> ../.archive_store/..._v2_patch/part003.agc   <-- (patched)
│   └── ...
│
└── agc_default/                                    <-- Active directory containing 1,129 symlinks
    ├── part001.agc -> ../.archive_store/..._v1_adaptive/part001.agc
    ├── part003.agc -> ../.archive_store/..._v2_patch/part003.agc   <-- (patched)
    └── ...
```

### 6.2 Step-by-Step Execution Plan

#### Step 1: Update `SAMN16418392` Assembly File
```bash
EXP_DIR="/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING"
TARGET_DIR="/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_set2_2024-08"

cp "${TARGET_DIR}/SAMN16418392.fa.gz" "${TARGET_DIR}/SAMN16418392.fa.gz.bak_old_set2"
cp "${EXP_DIR}/SAMN16418392.fa.gz" "${TARGET_DIR}/SAMN16418392.fa.gz"

# Verify hash
seqkit sum "${TARGET_DIR}/SAMN16418392.fa.gz"
# Output must match: seqkit.v0.1_DLS_k0_d8229e2491d6d2cf904fc5e74aa5784b
```

#### Step 2: Set Up Versioned Archive Store and Baseline Symlinks
```bash
cd "${EXP_DIR}/compression_results"
mkdir -p .archive_store

# Move original folders into v1
mv agc_split_size_no_divisions .archive_store/agc_split_size_no_divisions_v1_adaptive
mv agc_default .archive_store/agc_default_v1_adaptive

# Create patch directories
mkdir -p .archive_store/agc_split_size_no_divisions_v2_patch
mkdir -p .archive_store/agc_default_v2_patch

# Re-create active directory mountpoints
mkdir -p agc_split_size_no_divisions agc_default

# Populate baseline symlinks pointing to v1
for f in .archive_store/agc_split_size_no_divisions_v1_adaptive/*.agc; do
    ln -s "../$f" agc_split_size_no_divisions/
done

for f in .archive_store/agc_default_v1_adaptive/*.agc; do
    ln -s "../$f" agc_default/
done
```

#### Step 3: Write Recompression Batch List (20 Batches)
Create `${EXP_DIR}/data/batches_to_recompress_20.txt`:
```text
atb.assembly.r1.part003
atb.assembly.r1.part051
atb.assembly.r1.part059
atb.assembly.r1.part170
atb.assembly.r1.part199
atb.assembly.r1.part223
atb.assembly.r1.part249
atb.assembly.r1.part257
atb.assembly.r1.part263
atb.assembly.r1.part325
atb.assembly.r1.part435
atb.assembly.r1.part586
atb.assembly.r1.part691
atb.assembly.r1.part851
atb.assembly.r1.part862
atb.assembly.r1.part929
atb.assembly.r1.part995
atb.assembly.r1.part1008
atb.assembly.r1.part1021
atb.assembly.r1.part1042
```

#### Step 4: Run Recompression Without `-a`
Launch recompression for both variants **without `-a`** (using default 60-segment splitting), directing outputs directly to the patch directory:
- For `agc_split_size_no_divisions`: output to `.archive_store/agc_split_size_no_divisions_v2_patch/${batch}.agc`
- For `agc_default`: output to `.archive_store/agc_default_v2_patch/${batch}.agc`

#### Step 5: Switch Symlinks to Patched Archives
```bash
cd "${EXP_DIR}/compression_results"
while read -r batch; do
    ln -sf "../.archive_store/agc_split_size_no_divisions_v2_patch/${batch}.agc" "agc_split_size_no_divisions/${batch}.agc"
    ln -sf "../.archive_store/agc_default_v2_patch/${batch}.agc" "agc_default/${batch}.agc"
done < "${EXP_DIR}/data/batches_to_recompress_20.txt"
```

#### Step 6: Validate Recompressed Archives
Run `comprehensive_validation.py` targeting the 20 batches to ensure 100% pass across all recompressed genomes.

### 6.3 Empirical Audit: Adaptive Segregation Test (`v2_adaptive_clean`)

On 2026-10-14, the 20 cleaned batches + `standalone.agc` (67,642 genomes) were validated with `verify_clean_batches.py`:
- **Overall Result**: 67,606 / 67,642 passed bit-for-bit (99.95%).
- **13 Batches 100% Clean**:
  - `part003` (all 8 original victims cured!)
  - `part199` (8,411 genomes clean)
  - `part223` (2,718 genomes clean)
  - `part249` (3,980 genomes clean with updated `SAMN16418392`)
  - `part257`, `part263`, `part325`, `part586`, `part691`, `part862`, `part929`, `part995`, `part1042`
- **Standalone Archive**: `standalone.agc` passed 96/97 genomes cleanly. The sole failure is `SAMN50311804` (expected, raw FASTA write corruption containing 1,434 null bytes).
- **7 Batches with Secondary Victims (35 genomes total)**:
  - `part051` (1 failure: `SAMN03996952`)
  - `part059` (1 failure: `SAMN38380369`)
  - `part170` (6 failures: `SAMEA5757810`, `SAMEA6144833`, `SAMN11156863`, `SAMN28700481`, `SAMN35670651`, `SAMN37529090`)
  - `part435` (7 failures: `SAMEA1317042`, `SAMEA1317060`, `SAMEA1317062`, `SAMEA1317064`, `SAMEA1317066`, `SAMEA1317071`, `SAMN13910111`)
  - `part851` (7 failures: `SAMEA6124300`, `SAMEA6534298`, `SAMN11463671`, `SAMN12821393`, `SAMN22254653`, `SAMN22254909`, `SAMN22255139`)
  - `part1008` (2 failures: `SAMN04505064`, `SAMN42436694`)
  - `part1021` (11 failures: `SAMEA1094336`, `SAMEA1398296`, `SAMEA1559269`, `SAMEA1559279`, `SAMEA1568547`, `SAMEA4555932`, `SAMEA7461379`, `SAMN01821746`, `SAMN05290090`, `SAMN06212339`, `SAMN18539620`)

**Finding**:
In dense repetitive clades, removing the first wave of victims shifts candidate splitter intervals and infects downstream sister strains ("whack-a-mole" effect).
**Resolution**:
Replaced segregation trial with definitive binary patch (`src/core/kmer.h:450` checking `cur_size != x.cur_size`).

### 6.4 Definitive Remediation: Patched AGC Adaptive Recompression (`v3_patch`)

On 2026-10-14, all 20 affected batches were recompressed using the patched AGC binary (`fix-polya` branch, `src/core/kmer.h` checking `cur_size`) with full adaptive mode (`-a -b 500 -s 1500 -t 40`) and their **original, complete batch files** (zero segregated samples, zero duplicate names).

Target directory:
`/projects/reall/tam/Workspace/experiments/124_EXPE_ATB202603_ORDERING/compression_results/.archive_store/agc_default_v3_patch`

#### Verification Scorecard (`verify_clean_batches.py` across 67,642 genomes)
- **Genomes Evaluated**: 67,642
- **Passed Bit-for-Bit**: 67,641 (99.9985%)
- **Non-Matching**: 1 genome (`SAMN50311804` in `part199`, the known raw source FASTA containing 1,434 literal null bytes, expected).
- **All 20 Archives**: 100% of poly-A homopolymer splitter corruptions eliminated.
- **Archive Sizes**: Maintained optimal high-compression footprint (e.g. `part851` remains ~100 MB instead of ballooning to 1.4 GB).

#### Production Deployment & Persistence Strategy
1. **Experiment Directory Symlinks**:
   - `agc_default/*.agc` points to `../.archive_store/agc_default_v1_adaptive/*.agc` (1,109 clean archives) and `../.archive_store/agc_default_v3_patch/*.agc` (20 patched archives).
2. **Persistent Storage & Public Release**:
   - For long-term persistent storage or sharing (S3, Zenodo, Globus), sync with dereferencing (`--follow-symlinks` / `rsync -L`) to ensure downstream users receive real, self-contained physical `.agc` files without dangling symlinks.

---

## 7. Executive Summary & Technical Post-Mortem

### 7.1 Scope & Objective
Complete recompression and audit of the **AllTheBacteria (ATB) 2026-03** release containing **3,092,278 assemblies** partitioned into **1,129 AGC archives** by taxonomic boundary ordering, achieving 100% bit-for-bit checksum concordance against raw source files while maintaining optimal compression ratios.

### 7.2 Problems Discovered
1. **Full Audit Baseline (`v1_adaptive`)**:
   - 3,092,181 assemblies passed bit-for-bit across 1,109 archives.
   - 97 assemblies failed across 20 archives.
2. **Non-AGC Data Anomalies Cleared**:
   - `SAMN50311804` (`part199`): Raw source file contained 1,434 literal null bytes (`\x00`) from an interrupted filesystem write; AGC stripped them, restoring the true assembly.
   - `SAMN16418392` (`part249`): Stale 36-contig length-filtered assembly replaced with official 121-contig assembly.
3. **Upstream AGC Homopolymer Bug**:
   - The remaining 95 failures across 19 archives stemmed from an upstream bug in `refresh-bio/agc` under adaptive mode (`-a`). Contigs were silently corrupted via length inflation (+tens of kb), length truncation (-884 bp, -60 bp), or internal sequence swapping ($\Delta=0$).

### 7.3 Failed Iterations & Insights
1. **Segregation Attempt (`v2_adaptive_clean` - Whack-a-Mole)**:
   - Extracting the 95 victims into a standalone archive cured 13 archives, but caused 7 stubborn archives to fail with **35 brand-new victim assemblies** that had passed in `v1`.
   - *Cause*: In dense taxonomic clades, sister strains share repetitive junctions. Removing the first wave of victims shifted the candidate splitter window, exposing downstream sister strains to the culprit's homopolymer splitter.
2. **Non-Adaptive Fallback Penalty**:
   - Recompressing without `-a` avoided the bug but caused unacceptable 14x size penalties (e.g. `part851` ballooned from ~100 MB to 1.4 GB) due to unaligned accessory/plasmid contigs.
3. **Homopolymer Reordering to Batch Tail**:
   - Batch analysis revealed that in `part051`, **298 out of 1,174 genomes (25%)** contain $A^{31}/T^{31}$ homopolymers. Moving hundreds of homopolymers to the tail would cause severe cross-infection.

### 7.4 Definitive Engineering Solution (`v3_patch`)
1. **Root Cause**:
   - In `src/core/agc_compressor.cpp:2041`, AGC tests `split_kmer == CKmer(kmer_length, canonical)`.
   - In `src/core/kmer.h:450`, `operator==` only checked `kmer_dir == x.kmer_dir`, omitting `cur_size`.
   - For $A^{31}$, `kmer_dir == 0ull`, matching an uninitialized empty $k$-mer (`0ull == 0ull -> true`), causing AGC to falsely believe 0 splitters were found and re-queue the contig into Pass 2.
2. **Code Patch**:
   - Created clean branch `fix-polya` from `origin/main` in `agc-split-size`.
   - Updated `CKmer::operator==` to check `if (cur_size != x.cur_size) return false;`.
   - Verified on 100-bp Nano MRE (`nano_agc_test.sh` passing bit-for-bit in 0.02s).
3. **Cluster Validation**:
   - Recompressed all 20 archives with the patched binary using original complete batch lists and full `-a`.
   - **Audit Results**: 67,641 / 67,642 passed (99.9985%), with the sole non-match being the known raw null-byte file `SAMN50311804`.
   - Poly-A corruptions: **0 across all 3,092,278 genomes**.
   - Storage footprint: Optimal adaptive compression preserved with zero file size ballooning.

---

## 8. Complete Pipeline Script & Artifact Inventory

The complete codebase of Experiment 124 comprises 32 specialized scripts categorized into 5 operational tiers.

### 8.1 Tier 1: Taxonomic Ordering & Batching (Pre-compression)
Responsible for clustering 3,092,278 assemblies, ordering them by macro/meso phylogeny, and generating the 1,129 contiguous batch files.

| Script | Purpose & Parameters | Input | Output |
| :--- | :--- | :--- | :--- |
| `clustering.sh` | Clusters assemblies by GTDB species and genus boundaries. | ATB Metadata TSV | `data/species_clusters/*.txt` |
| `phylopack_meso_ordering.sh` | Runs meso-level phylogenetic preorder on individual clusters via `phylopack`. | `data/species_clusters/` | `ordering_results/meso/` |
| `refinement.sh` | High-resolution ordering refinement for massive or highly diverse species clades. | `ordering_results/meso/` | `ordering_results/refined/` |
| `representative_phylogeny.sh` | Constructs global macro phylogenetic guide tree across species representatives using `py_attotree`. | Refined species clades | `ordering_results/macro_tree.nwk` |
| `macro_ordering_lexicographically.sh` | Handles residual/unclassified accessions, appending them after known phylogenetic lineages. | Unclassified assemblies | `ordering_results/residual.txt` |
| `batch_global_ordering.sh` | Chains macro tree leaves and intra-clade refined orders into the single canonical order. | Macro tree + Refined clades | `ordering_results/global_final_ordering.txt` (3,092,278 lines) |
| `extract_separators.sh` | Queries existing balanced archives (`agc listset`) to extract exact genome counts and cumulative line cutpoints. | `agc_split_size_no_divisions/*.agc` | `data/separators.tsv` (1,129 rows) |
| `put_batches_fof.sh` | Cuts `global_final_ordering.txt` using `separators.tsv` into 1,129 batch `.txt` files and partitions them into 3 File-of-Files (`fof_1.txt`, `fof_2.txt`, `fof_3.txt`) for 3 cluster nodes. | `separators.tsv` + `global_final_ordering.txt` | `data/batches_to_compress/*.txt`, `data/fof/` |
| `verify_batches.py` | Single-pass validation streaming all batch files alongside `global_final_ordering.txt` (asserts 0 missing, 0 extra, 0 duplicates, line-by-line order match). | `batches_to_compress/` + `global_final_ordering.txt` | Console validation report (~3s runtime) |

### 8.2 Tier 2: Primary Compression Pipelines
Automated execution of `agc create` pipelines across compute nodes and patch tiers.

| Script | Compression Flags | Input | Target Directory | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `run_agc_fof_default.sh` | `agc create -a -b 500 -s 1500 -t 50` | `data/fof/batches_fof_{1,2,3}.txt` | `.archive_store/agc_default_v1_adaptive/` | Initial 1,129 archive run; 1,109 clean, 20 had anomalies. |
| `run_agc_fof_default_clean_adaptive.sh` | `agc create -a -b 500 -s 1500 -t 40` | `batches_cleaned_to_compress/*.txt` | `.archive_store/agc_default_v2_adaptive_clean/` | Trial segregation run (95 victims removed); led to whack-a-mole discovery. |
| `run_agc_fof_default_no_adaptivesh` | `agc create -b 500 -s 1500 -t 40` (no `-a`) | `batches_to_recompress_20.txt` | `.archive_store/agc_default_v2_patch/` | Fixed corruption, but caused 14x size inflation (e.g. part851: 100MB -> 1.4GB). |
| `run_v3_patch.sh` | `agc_patched create -a -b 500 -s 1500 -t 40` | `batches_to_recompress_without_adaptive_mode.txt` | `.archive_store/agc_default_v3_patch/` | **Definitive Production Runner**: Patched AGC binary (`fix-polya`), original complete batch files. 100% clean. |
| `compression_agc_full.sh` | Variable interactive test harness | Single batch `.txt` | `/dev/shm/` or test dirs | Interactive benchmark harness. |
| `extract_clean_batches.sh` | AWK text processing | Original batches + failure TSV | `batches_cleaned_to_compress/` | Extracted the 95 victims into `standalone.txt`. |

### 8.3 Tier 3: Validation & Auditing Engines
High-throughput verification engines extracting sequences and comparing `seqkit sum` hashes directly against metadata ground truth.

| Script | Architecture | Scaling Parameters | Memory Strategy | Checkpointing |
| :--- | :--- | :--- | :--- | :--- |
| `comprehensive_validation.py` | Hybrid `getcol` + streaming `getset -p` | 40 threads, 20 streaming workers | `\le 3000` genomes: `/dev/shm` buffer.<br/>`> 3000` genomes: 0 disk/shm usage via piped memory stream. | Archive-level resume logging (`validation_done_archives_*.txt`), failure log TSV. |
| `verify_agc_folder.py` | Dynamic directory validator | Accepts arbitrary path & thread count | Inherits hybrid memory engine from comprehensive auditor. | Evaluates whatever `.agc` files are present in target directory without requiring global 3M inventory. |
| `agc_validation_smoke_test.py` | Head/tail sampling smoke test | 5 random samples per archive | In-memory `agc getset -p \| seqkit sum` | Fast sanity verification before long validation runs. |

### 8.4 Tier 4: Bug Reproducers & Diagnostic Tools
Suite of diagnostic scripts that bisected, proved, and isolated the upstream AGC adaptive mode bug down to the 100-bp Nano MRE.

| Script | Purpose & Methodology | Key Findings |
| :--- | :--- | :--- |
| `inspect_error_agc.py` | FASTA parser comparing raw `.fa.gz` contigs against AGC-extracted contigs. | Diagnosed contig length inflation (`SAMEA5584600.contig00047`: 39,080 bp -> 63,487 bp). |
| `inspect_v2_error.sh` | Analyzed secondary victims in `v2_adaptive_clean` stubborn batches. | Identified negative diffs (-884 bp, -60 bp) and silent segment swaps ($\Delta=0$, 98.8 kb swapped). |
| `finding_culprit.py` | Scanned batches for candidate culprit genomes preceding victims with $A^{31}/T^{31}$ homopolymers. | Discovered that 298 / 1,174 genomes in `part051` contain homopolymers, proving manual reordering infeasible. |
| `reproduce_bug.sh` | Single-sample extraction test in `part003`. | Established baseline corruption reproduction on `SAMEA5584600`. |
| `reproduce_bug_2.sh` | Multi-genome cohort bisection across all 8 affected genomes in `part003`. | Proved all 8 failures were correlated to an upstream predecessor. |
| `reproduce_bug_3.sh` | Pairwise predecessor testing (`Ref` + Predecessor + `Target`). | Pinpointed the exact culprit to Line 200 (`SAMN48436743`). |
| `minimal_reproducible.sh` | 3-genome reproducer (`Ref` + Line 200 + Line 210) running in 0.5s. | Stripped 35,000 irrelevant genomes down to a 3-genome reproducible unit. |
| `nano_bug_reproduce.sh` | **100-bp Nano MRE**: 100% synthetic 300-byte test (`ref`, `culprit`, `target` of 100 bp each). | Demonstrated silent +19 bp homopolymer duplication in 0.02s on upstream AGC `v3.2.4`. Core regression test for `fix-polya`. |

### 8.5 Tier 5: Operational Helpers & Persistent Release Deployment

| Script | Purpose & Features | Operational Role |
| :--- | :--- | :--- |
| `sync_to_persistent_rel.sh` | **Production Release Syncer**: Synchronizes the 1,129 active symlinked archives into `/projects/reall/tam/data/ATB/Release_1/agc_batches` as **real physical files** (`rsync -avL -P`). Asserts 0 broken symlinks, calculates exact raw byte counts via `wc -c`, computes decimal size (GB in $10^9$ scale), and generates `MANIFEST_AGC_BATCHES.tsv`. | Final deployment script for permanent storage and public release packaging. |
| `restore_path.py` | Accession resolver mapping bare identifiers to absolute paths across historical S3 directories (`set1`, `set2_2024-08`, `2025-05`). | Helper for raw file retrieval. |
| `peak_ressource.sh` | Background daemon logging RAM, `/dev/shm`, and CPU thread utilization. | Proved memory remained strictly bounded $\le 15\text{ GB}$ during validation. |
| `conda_env.sh` | Environment configuration exporting patched binary paths and compiler flags. | Environment standardization. |

---

## 9. Release Notes & Production Data Architecture Specification

### 9.1 Data Release Directory Structure

```text
ATB_2026-03_Release_1/
├── agc_batches/                           <-- 1,129 physical .agc files (zero dangling symlinks)
│   ├── atb.assembly.r1.part000.agc
│   ├── atb.assembly.r1.part001.agc
│   └── ...
│   └── atb.assembly.r1.part1128.agc
│
├── ordering/                              <-- The biological ordering coordinate system
│   ├── atb.ordering.r1.global.txt         <-- Canonical 3,092,278 ordered accessions
│   └── atb.batches.r1.cutpoints.tsv       <-- Cutpoint index (count, cumulative_end, batch_name)
│
├── metadata/                              <-- Checksums & fast accession navigation
│   ├── atb.metadata.r1.assembly.tsv       <-- Full assembly metadata + seqkit sum ground truth
│   ├── atb.batches.r1.manifest.tsv        <-- Archive manifest (size in raw bytes, SHA256)
│   └── atb.assembly_to_batch.r1.tsv       <-- Fast 1-to-1 accession-to-archive lookup table
│
└── README.md                              <-- Quickstart extraction and slicing guide
```

### 9.2 Ordering & Slicing Specifications

The entire batch partition is 100% reproducible from first principles using two companion files:
1. **`atb.ordering.r1.global.txt`**: 3,092,278 lines containing the global phylogenetic traversal computed by `phylopack` and `py_attotree`.
2. **`atb.batches.r1.cutpoints.tsv`**: 1,129 rows specifying the exact boundaries.

#### Standard Single-Pass AWK Slicing Recipe:
Users can slice the monolithic 3M global ordering into the exact 1,129 batch file manifests in ~2 seconds using pure POSIX `awk`:

```bash
awk -v out_dir="./batches" '
    NR == FNR {
        n++; end_line[n] = $2; batch[n] = $3; next
    }
    FNR == 1 { b = 1; out = out_dir "/" batch[b] ".txt" }
    {
        print $0 > out
        if (FNR == end_line[b]) {
            close(out)
            b++
            if (b <= n) out = out_dir "/" batch[b] ".txt"
        }
    }
' atb.batches.r1.cutpoints.tsv atb.ordering.r1.global.txt
```

### 9.3 Fast Accession-to-Batch Resolution (`atb.assembly_to_batch.r1.tsv`)
To allow instant lookup of any accession without querying 1,129 archives or grepping large directories:
```tsv
accession	batch_name	global_index
SAMN00000001	atb.assembly.r1.part000	1
SAMN00000002	atb.assembly.r1.part000	2
...
```

### 9.4 Release Notes: Public User Guide vs. ATB Consortium Technical Dossier

#### A. Public User Guide (Simple & Actionable)
- **Dataset Scope**: 3,092,278 non-redundant assemblies across 1,129 compressed archives.
- **Fidelity**: 100% bit-for-bit identical to official raw source FASTA assemblies.
- **Single Assembly Extraction**:
  ```bash
  agc getset atb.assembly.r1.part003.agc SAMN12345678 > SAMN12345678.fa
  ```
- **Whole Batch Extraction**:
  ```bash
  agc getcol -o ./extracted_batch/ atb.assembly.r1.part003.agc
  ```
- **Recommended Software**: Upstream `refresh-bio/agc >= v3.2.4` with `fix-polya` patch.

#### B. ATB Consortium Technical Dossier (Quality Assurance & Audit Record)
- **100% Comprehensive Audit**: All 3,092,278 genomes were decompressed and checked against ground-truth `seqkit sum` checksums in `atb.metadata.r1.assembly.tsv`.
- **Anomalies Resolved**:
  - `SAMN16418392` (`part249`): Updated outdated 36-contig local file to official 121-contig assembly.
  - `SAMN50311804` (`part199`): Raw source disk file contained 1,434 null bytes (`\x00`) from an interrupted write; AGC automatically stripped them, restoring the valid sequence.
- **Upstream AGC Adaptive Homopolymer Bug (`A^31`)**:
  - Identified root-cause in `kmer.h:450` (`operator==` comparing `kmer_dir` without checking `cur_size`, causing $A^{31}$ to falsely match empty $k$-mer).
  - Submitted 1-line upstream fix on branch `fix-polya`.
  - Recompressed all 20 affected archives (`v3_patch`), achieving 67,641 / 67,642 bit-for-bit concordance with full adaptive compression (zero file size ballooning).
- **Taxonomic & Batch Integrity**: 100% intact. Zero genomes were removed or segregated. All 1,129 archives reflect the exact taxonomic boundaries of the canonical global ordering.








