# Sprint 2: Physical Archive Offset Tracking & The Hidden Memory Tail Problem

## 1. Goal & Scope
Implement thread-safe physical disk offset tracking in `CArchive` via `GetCurrentOffset()` and `CAGCCompressor::GetCurrentArchiveSizeEstimate()`. Analyze why naive physical disk tracking fails under AGC's asynchronous batching architecture, underestimating final archive size by a factor of 2x to 3x due to uncompressed contig buffers buffered in RAM.

---

## 2. Time Estimation
| Activity | Description | Estimated Hours |
| :--- | :--- | :--- |
| **Reading & Concepts** | AGC internal streaming architecture, `CArchive`, `CSegment`, batching | 2.0 hrs |
| **Implementation** | Add `CArchive::GetCurrentOffset()` and `CAGCCompressor::GetCurrentArchiveSizeEstimate()` | 1.0 hr |
| **Analysis & Experimentation** | Measure committed disk offset vs final size on multi-genome datasets | 1.5 hrs |
| **Exam & Challenge** | Written conceptual test + memory buffer simulation challenge in `EXAM.md` | 1.0 hr |
| **Total** | | **~5.5 hrs** |

---

## 3. Architecture & Interface Specs

### The Physical Offset Query (`src/common/archive.h` & `src/common/archive.cpp`)
```cpp
// src/common/archive.h
class CArchive
{
    // ...
public:
    size_t GetCurrentOffset();
};
```

```cpp
// src/common/archive.cpp
size_t CArchive::GetCurrentOffset()
{
    lock_guard<mutex> lck(mtx);

    if (input_mode)
        return 0;

    // Flush any pending file stream write buffers to OS file descriptor
    flush_out_buffers();

    return f_offset;
}
```

### Compressor-Level Wrapper (`src/core/agc_compressor.h` & `src/core/agc_compressor.cpp`)
```cpp
// src/core/agc_compressor.h
class CAGCCompressor
{
public:
    uint64_t GetCurrentArchiveSizeEstimate();
};
```

```cpp
// src/core/agc_compressor.cpp
uint64_t CAGCCompressor::GetCurrentArchiveSizeEstimate()
{
    if (!out_archive)
        return 0;

    return static_cast<uint64_t>(out_archive->GetCurrentOffset());
}
```

---

## 4. The Underestimation Crisis: Architectural Breakdown

```
========================= AGC INGESTION TIMELINE =========================

Genome Stream ----> Contig Splitter ----> [CSegment 0] [CSegment 1] ... [CSegment 8999]
                                                |            |                |
                                            (120 ctgs)   (480 ctgs)       (35 ctgs)
                                                |            |                |
                                            [  RAM  ]    [  RAM  ]        [  RAM  ]
                                                \            |                /
                                                 =============================
                                                               |
                                            When segment reaches 500 contigs:
                                            ZSTD Compress & Flush to Disk
                                                               |
                                                               v
                                                      [ PHYSICAL DISK ]
                                                 (CArchive::GetCurrentOffset)
```

1. **Thousands of Active Segments**: AGC splits genomes into contigs routed to ~9,000 segment groups based on $k$-mer splitters.
2. **The 500-Contig Threshold (`contigs_in_pack`)**: A segment compresses its internal contig vectors (`v_lzp` and `v_raw`) via ZSTD and flushes them to disk *only* when the vector size reaches 500.
3. **The Invisible Tail**: At any point during ingestion, thousands of segments each hold between 1 and 499 uncompressed contigs in RAM.
4. **The End-of-Archive Spike**: When `Close()` is called, all 9,000 segments simultaneously flush their partial batches, instantly doubling or tripling physical file size.

---

## 5. Step-by-Step Task Checklist

- [ ] **Step 2.1:** Declare `size_t GetCurrentOffset();` in `src/common/archive.h`.
- [ ] **Step 2.2:** Implement `GetCurrentOffset()` in `src/common/archive.cpp` ensuring `mtx` mutex acquisition and `flush_out_buffers()` invocation.
- [ ] **Step 2.3:** Declare `uint64_t GetCurrentArchiveSizeEstimate();` in `src/core/agc_compressor.h`.
- [ ] **Step 2.4:** Implement `GetCurrentArchiveSizeEstimate()` in `src/core/agc_compressor.cpp`.
- [ ] **Step 2.5:** Run an experimental compression test logging `GetCurrentArchiveSizeEstimate()` after each sample and comparing against the final on-disk file size.
- [ ] **Step 2.6:** Document the observed underestimation delta across 10, 50, and 200 genomes.

---

## 6. Unit Test & Verification Specifications

```cpp
#include "doctest.h"
#include "../src/common/archive.h"

TEST_CASE("Archive: Offset Monotonicity") {
    CArchive archive;
    // When archive is not open or in input mode, offset returns 0
    CHECK(archive.GetCurrentOffset() == 0);
}
```

### Empirical Verification Test
Run compression on sample genomes:
```bash
./bin/agc create -v 2 out.agc toy_ex/*.fa
```
Observe the discrepancy:
- During ingestion of last genome: reported disk offset = ~4.2 MB.
- After `Close()` finishes: final file size on disk = ~11.8 MB (a 2.8x underestimation!).

---

## 7. Acceptance Criteria

1. `CArchive::GetCurrentOffset()` correctly returns the committed byte offset `f_offset` under concurrent thread access.
2. `GetCurrentArchiveSizeEstimate()` safely returns 0 if `out_archive` is null.
3. The root cause of archive size underestimation (the asynchronous uncompressed RAM tail across `v_segments`) is mathematically and empirically documented.
