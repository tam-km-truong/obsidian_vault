# Sprint 3: Non-Destructive In-Memory Shadow Trial Compression

## 1. Goal & Scope
Implement an in-memory shadow trial compression mechanism inside `CSegment` via `simulate_store` and `estimate_partial_compressed_size`. This function must compress unwritten contig buffers (`v_lzp` and `v_raw`) using ZSTD without altering segment state, without breaking internal AGC index pointers, and without performing any disk I/O.

---

## 2. Time Estimation
| Activity | Description | Estimated Hours |
| :--- | :--- | :--- |
| **Reading & Concepts** | ZSTD C API (`compressCCtx`, `compressBound`), thread safety in `CSegment` | 1.5 hrs |
| **Implementation** | Write `CSegment::simulate_store` and `estimate_partial_compressed_size` | 1.5 hrs |
| **Test Writing** | Unit tests verifying non-destructive behavior and compression accuracy | 1.0 hr |
| **Benchmarking** | Measure CPU overhead of shadow compression on 10,000 simulated contigs | 0.5 hr |
| **Exam & Challenge** | Written conceptual test + ZSTD scratch compressor challenge in `EXAM.md` | 1.0 hr |
| **Total** | | **~5.5 hrs** |

---

## 3. Architecture & Interface Specs

### Declarations in `src/common/segment.h`
```cpp
class CSegment
{
    // ...
public:
    uint32_t estimate_partial_compressed_size(ZSTD_CCtx* zstd_ctx);

private:
    uint32_t simulate_store(const vector<contig_t>& v_data, ZSTD_CCtx* zstd_ctx);
};
```

### Implementation in `src/common/segment.cpp`
```cpp
uint32_t CSegment::simulate_store(const vector<contig_t>& v_data, ZSTD_CCtx* zstd_ctx)
{
    size_t total_size = 0;
    for (const auto& d : v_data) 
        total_size += d.size() + 1;

    if (total_size == 0) return 0; // Safety against empty vectors

    vector<uint8_t> buffer(total_size);
    size_t offset = 0;
    for (const auto& d : v_data) 
    {
        copy(d.begin(), d.end(), buffer.begin() + offset);
        offset += d.size();
        buffer[offset++] = 0xff; // AGC contig boundary delimiter
    }

    size_t a_size = ZSTD_compressBound(buffer.size());
    vector<uint8_t> packed(a_size + 1);

    // Compress at level 10 to simulate AGC pack compression
    size_t zstd_ret = ZSTD_compressCCtx(zstd_ctx, packed.data(), a_size, buffer.data(), buffer.size(), 10);
    
    // Fallback in case of compression error to prevent size corruption
    if (ZSTD_isError(zstd_ret)) {
        cerr << "ZSTD error" << endl;
        return (uint32_t)(total_size / 3);
    }
    
    return (uint32_t)zstd_ret;
}

uint32_t CSegment::estimate_partial_compressed_size(ZSTD_CCtx* zstd_ctx)
{
    lock_guard<mutex> lck(mtx);
    uint32_t size = 0;
    
    if (!v_lzp.empty()) 
        size += simulate_store(v_lzp, zstd_ctx);
    
    if (!v_raw.empty()) 
        size += simulate_store(v_raw, zstd_ctx);
        
    return size;
}
```

---

## 4. Key Engineering Rationale: Why Forced Flushing Failed

During initial trials, the author attempted to force segments to write partial batches to disk early (`flush_partial`, `flush_soft`). This caused three catastrophic failures:
1. **Severely Degraded Compression Ratio**: ZSTD achieves high compression by building dynamic dictionaries across full batches (`contigs_in_pack = 500`). Prematurely flushing fragments of 5–20 contigs destroys dictionary history, bloating the final archive.
2. **Broken AGC Internal Index Structures**: Prematurely committed segment parts desynchronized segment sequence maps, collection descriptors, and random-access query indices.
3. **Severe Thread Stalls**: Halting workers to flush 9,000 segments to physical disk caused massive I/O serialization bottlenecks.

**The Shadow Trial Solution**:
`simulate_store` uses temporary scratch RAM (`vector<uint8_t> packed`), obtains the exact ZSTD compressed byte count, and immediately frees the scratch memory.
- **Segment vectors `v_lzp` and `v_raw` remain intact in RAM.**
- **No disk I/O occurs.**
- **No internal AGC state or indices are modified.**

---

## 5. Step-by-Step Task Checklist

- [ ] **Step 3.1:** Declare `estimate_partial_compressed_size` and `simulate_store` in `src/common/segment.h`.
- [ ] **Step 3.2:** Implement `simulate_store` in `src/common/segment.cpp` packing contigs with `0xff` delimiter.
- [ ] **Step 3.3:** Use `ZSTD_compressBound` to allocate exact destination capacity safely.
- [ ] **Step 3.4:** Execute `ZSTD_compressCCtx` with reusable context `zstd_ctx`.
- [ ] **Step 3.5:** Implement error detection with `ZSTD_isError` and 3:1 safety fallback.
- [ ] **Step 3.6:** Implement `estimate_partial_compressed_size` guarding `v_lzp` and `v_raw` under `mtx`.
- [ ] **Step 3.7:** Write unit tests verifying that invoking `estimate_partial_compressed_size` leaves `v_lzp` and `v_raw` completely unchanged.

---

## 6. Unit Test Specifications

```cpp
#include "doctest.h"
#include <zstd.h>
#include "../src/common/segment.h"

TEST_CASE("ShadowTrial: Non-Destructive Invariance") {
    CSegment seg;
    auto* ctx = ZSTD_createCCtx();

    // 1. Initial empty state
    CHECK(seg.estimate_partial_compressed_size(ctx) == 0);

    // 2. Add mock contigs into segment (requires friend or test method)
    // Verify estimated size > 0
    // Verify after call that segment size and contents are bitwise identical

    ZSTD_freeCCtx(ctx);
}

TEST_CASE("ShadowTrial: Compression Error Fallback") {
    // Verify that empty or degenerate inputs do not crash or throw exceptions
    auto* ctx = ZSTD_createCCtx();
    // Verify fallback ratio on error
    ZSTD_freeCCtx(ctx);
}
```

---

## 7. Acceptance Criteria

1. `simulate_store` returns exact ZSTD compressed bytes for uncompressed contig vectors.
2. The function is strictly non-destructive: contig counts, buffer capacities, and internal segment flags are completely unmodified after execution.
3. Thread safety is guaranteed via `lock_guard<mutex> lck(mtx)` in `estimate_partial_compressed_size`.
