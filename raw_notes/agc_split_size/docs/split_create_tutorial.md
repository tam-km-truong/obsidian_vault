# AGC Split-Create Size Estimation & Architecture Tutorial

This document details the architectural reasoning, trial solutions, and implementation specifics of the `split-create` feature in AGC.

---

## Context and High-Level Overview

The `split-create` feature partitions AGC archives into multiple files based on a predefined byte limit (`target_part_size`). During the file iteration loop, the running archive size must be estimated to determine when to close the current part and open a new one.

The primary issue encountered during implementation was a consistent underestimation of the final archive size by a factor of two to three. The root cause was that size estimation logic (`CArchive::GetCurrentOffset()`) exclusively measured compressed bytes committed to disk, failing to account for a significant "tail" of uncompressed sequence data held in active memory.

---

## AGC Pipeline Implementation Details

The underestimation is a direct result of the application's asynchronous batching architecture:

1. **Segment Groups (`CSegment`)**: The compressor maintains thousands of concurrent segment instances (e.g., ~9,000 active segments for ~2,500 samples). Sequences are delta-encoded and routed to these segments based on their splitters.
2. **Uncompressed Memory Buffers**: Inside each `CSegment`, delta-encoded sequences accumulate as raw, uncompressed bytes within internal vectors (`v_lzp` and `v_raw`).
3. **The Flush Threshold (`contigs_in_pack`)**: A segment compresses its internal vector via ZSTD and forwards it to the `CArchive` only when the vector size reaches the `contigs_in_pack` threshold (batch size, typically 500). Once flushed, the internal vector resets.
4. **Asynchronous Execution**: Because sequence splitters are distributed unevenly, segments reach the 500-sequence limit asynchronously. There is no synchronized global flush during standard execution.
5. **The Memory Tail**: At any given moment during the file loop, thousands of segments hold between 1 and 499 uncompressed sequences. This data is entirely invisible to the physical archive file until the terminal `Close()` routine forces all active segments to flush simultaneously.

---

## Summary of Attempted Solutions

Several approaches were evaluated to estimate the final compressed footprint of the memory tail before `Close()` execution:

1. **Summing Unwritten Memory with Archive Offset**
   * *Implementation*: Calculated the raw byte length of `v_lzp` and `v_raw` across all segments and added it to the archive offset.
   * *Result*: Massive overestimation. This approach incorrectly summed uncompressed memory bytes with compressed disk bytes.

2. **Applying a Static Compression Ratio**
   * *Implementation*: Divided the unwritten memory sum by a static ZSTD compression factor (e.g., 3).
   * *Result*: Inaccurate partitioning. Genomic compression ratios fluctuate significantly based on redundancy; a static heuristic cannot guarantee size compliance.

3. **Modulo Sample Synchronization**
   * *Implementation*: Checked the archive size only when the processed sample count reached a multiple of 500, assuming buffers would be empty.
   * *Result*: Failed. The 500-limit triggers at the individual segment level, not the global sample level.

4. **Dynamic Live-Compression Tracking**
   * *Implementation*: Tracked bytes immediately before and after ZSTD execution using atomic counters (`zstd_in`, `zstd_out`) within `CSegment` to establish a live compression ratio, applying this ratio to the unwritten memory.
   * *Result*: Abandoned in favor of a structural approach that guarantees exact disk measurements.

5. **Static Soft Flushing (50% Filled)**
   * *Implementation*: Flushed segments that were at least half full (e.g., ≥250 items).
   * *Result*: Failed on hyper-variable reference genomes. High splitter density causes thousands of segments to remain mostly empty, meaning almost no segments cross the static threshold, leaving the memory tail hidden until the end.

---

## Final Solution: Non-Destructive Shadow Trial Compression at Checkpoints

The size estimation challenge was resolved using a **Non-Destructive In-Memory Shadow Trial Compression Strategy at Adaptive Checkpoints**.

### Implementation Details

1. **In-Memory Shadow Trial Compression (`GetSimulatedArchiveSize` / `simulate_store`)**:
   * When evaluating archive size, worker threads iterate across all active segments (`v_segments`) holding unwritten sequence data in RAM (`v_lzp` and `v_raw`).
   * For each segment, `CSegment::simulate_store` packs unwritten sequences into a temporary RAM buffer and executes ZSTD compression (`ZSTD_compressCCtx`) using a temporary ZSTD context.
   * The resulting compressed byte count is recorded and summed with the current physical disk offset (`CArchive::GetCurrentOffset()`).
   * The temporary compressed buffer and ZSTD context are immediately discarded without writing to disk or altering segment state.

2. **Adaptive Checkpoint Scheduling (`AddSampleSplit`)**:
   * Passive monitoring runs until the estimated archive size crosses 75% of `target_part_size` (`strict_threshold`).
   * Once crossed, the compressor enters `strict_mode` and evaluates precise simulated size at dynamic checkpoints.
   * The interval between checkpoints adapts dynamically based on average bytes consumed per genome and remaining runway to the target size limit.

3. **95% Part Completion Milestone (`stop_threshold`)**:
   * Sample ingestion for the current archive part stops when the total simulated size reaches 95% of `target_part_size`.
   * The 5% margin safely absorbs global archive metadata (splitters, segment directories, and archive footers) serialized exclusively during `Close()`.

### Advantages

* **Maximized Compression Ratios**: Because segment buffers are not forcibly flushed to disk during checkpoints, sequences remain buffered until reaching full block cardinality (`contigs_in_pack` = 500) or archive completion. This preserves optimal ZSTD dictionary window efficiency.
* **Exact Size Accuracy**: Replaces static compression heuristics with real ZSTD trial compressions, guaranteeing accurate size tracking across highly variable genomic redundancy.

---

## Building on macOS (Apple Silicon M-Series)

To build AGC on macOS (M1/M2/M3/M4):
```bash
gmake CXX="g++-13 -D_Static_assert=static_assert" PLATFORM=m1
```

---

## Detailed Code Changes Reference

Below is the complete function-by-function and file-by-file reference detailing all implementation changes supporting the `split-create` feature across the codebase.

### 1. Application & CLI Parsing Layer

#### File: `src/app/application.h` & `src/app/application.cpp`
* **`CApplication::parse_size_with_suffix`**
  * **Location**: [`src/app/application.cpp:L681-L749`](file:///Users/ktruong/tools/agc-split-size/src/app/application.cpp#L681-L749) | Header: [`src/app/application.h:L122`](file:///Users/ktruong/tools/agc-split-size/src/app/application.h#L122)
  * **Signature**: `uint64_t parse_size_with_suffix(const string& s) const`
  * **Role**: Parses `-p` size option arguments (e.g. `100M`, `2G`, `500K`) into raw 64-bit byte multipliers (`1000`, `1000^2`, `1000^3`, `1000^4`). Returns `0` on invalid syntax.
* **`CApplication::make_part_archive_name`**
  * **Location**: [`src/app/application.cpp:L752-L766`](file:///Users/ktruong/tools/agc-split-size/src/app/application.cpp#L752-L766) | Header: [`src/app/application.h:L123`](file:///Users/ktruong/tools/agc-split-size/src/app/application.h#L123)
  * **Signature**: `string make_part_archive_name(const string& base_name, uint32_t part_id) const`
  * **Role**: Generates output part archive filenames formatted with zero-padded 3+ digit part indices (e.g., `archive.part001.agc`, `archive.part002.agc`).
* **`execution_params.target_part_size` & `execution_params.split_create`**
  * **Location**: [`src/app/application.cpp:L164-L170`](file:///Users/ktruong/tools/agc-split-size/src/app/application.cpp#L164-L170)
  * **Role**: Option parsing flags handling `-p` target size and `-x` strict mode activation.

#### File: `src/app/main.cpp`
* **`CApplication::create_split`**
  * **Location**: [`src/app/main.cpp:L130-L212`](file:///Users/ktruong/tools/agc-split-size/src/app/main.cpp#L130-L212)
  * **Signature**: `bool create_split()`
  * **Role**: High-level driver loop managing multi-part archive generation. Assigns the first genome of each part as its reference, invokes `AddSampleSplit`, and advances the input sample cursor by the consumed genome count.

---

### 2. Ingest & Checkpoint Controller Layer

#### File: `src/core/agc_compressor.h` & `src/core/agc_compressor.cpp`
* **`CAGCCompressor::AddSampleSplit`**
  * **Location**: [`src/core/agc_compressor.cpp:L2449-L2680`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L2449-L2680) | Header: [`src/core/agc_compressor.h:L769`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.h#L769)
  * **Signature**: `size_t AddSampleSplit(const vector<pair<string, string>>& _v_sample_file_name, const uint32_t no_threads, const uint64_t target_part_size, const bool is_strict)`
  * **Role**: Primary sample ingestion controller for split archives. Monitors physical disk usage and simulated shadow buffer sizes, managing queue drains and halting ingestion when the 95% target threshold is reached.
* **`CAGCCompressor::GetCurrentArchiveSizeEstimate`**
  * **Location**: [`src/core/agc_compressor.cpp:L2406-L2412`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L2406-L2412)
  * **Signature**: `uint64_t GetCurrentArchiveSizeEstimate()`
  * **Role**: Queries physical file offset committed to disk via `out_archive->GetCurrentOffset()`.
* **`CAGCCompressor::GetSimulatedArchiveSize`**
  * **Location**: [`src/core/agc_compressor.cpp:L2414-L2447`](file:///Users/ktruong/tools/agc-split-size/src/core/agc_compressor.cpp#L2414-L2447)
  * **Signature**: `uint64_t GetSimulatedArchiveSize(const uint32_t n_t)`
  * **Role**: Multi-threaded shadow compression engine. Spawns `n_t` worker threads to run trial compressions across all active `v_segments`, returning `Disk Offset + Sum(Shadow Sizes)`.

---

### 3. Segment Shadow Trial Compression Layer

#### File: `src/common/segment.h` & `src/common/segment.cpp`
* **`CSegment::estimate_partial_compressed_size`**
  * **Location**: [`src/common/segment.cpp:L611-L623`](file:///Users/ktruong/tools/agc-split-size/src/common/segment.cpp#L611-L623) | Header: [`src/common/segment.h:L340`](file:///Users/ktruong/tools/agc-split-size/src/common/segment.h#L340)
  * **Signature**: `uint32_t estimate_partial_compressed_size(ZSTD_CCtx* zstd_ctx)`
  * **Role**: Thread-safe wrapper locking segment mutex and executing `simulate_store` on active `v_lzp` and `v_raw` contig vectors.
* **`CSegment::simulate_store`**
  * **Location**: [`src/common/segment.cpp:L579-L610`](file:///Users/ktruong/tools/agc-split-size/src/common/segment.cpp#L579-L610)
  * **Signature**: `uint32_t simulate_store(const vector<contig_t>& v_data, ZSTD_CCtx* zstd_ctx)`
  * **Role**: In-memory ZSTD trial compression routine. Packs unwritten contig byte vectors into a temporary RAM buffer, runs `ZSTD_compressCCtx()`, records compressed size, and immediately discards the temporary buffers without altering segment state or writing to disk.
