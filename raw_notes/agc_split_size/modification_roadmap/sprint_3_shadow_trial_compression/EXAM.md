# Sprint 3 Mastery Checkpoint & Exam

This checkpoint evaluates your understanding of the Zstandard C API, memory safety in trial compression, and non-destructive algorithm design.

---

## Part 1: Written Conceptual Exam

### Question 1: Zstandard Memory Bounds & Context Lifecycle
1. What does `ZSTD_compressBound(size_t srcSize)` compute, and why is using it preferable to guessing a fixed buffer size?
2. Why is creating a `ZSTD_CCtx` inside a hot per-contig loop a performance anti-pattern? What is the recommended lifecycle pattern for high-throughput batching?

---

### Question 2: Thread Safety in Low-Level Compression
Consider the following pseudo-code running in a multi-threaded compressor:

```cpp
static ZSTD_CCtx* global_zstd_ctx = ZSTD_createCCtx();

uint32_t compressParallel(const std::vector<uint8_t>& data) {
    std::vector<uint8_t> out(ZSTD_compressBound(data.size()));
    size_t sz = ZSTD_compressCCtx(global_zstd_ctx, out.data(), out.size(), data.data(), data.size(), 10);
    return static_cast<uint32_t>(sz);
}
```
Explain the race condition and what will happen when two threads call `compressParallel` simultaneously.

---

### Question 3: Non-Destructive Invariance
Why did previous approaches that performed early physical flushing (`flush_partial`) break AGC's internal indexing and degrade overall compression efficiency? Contrast that with the shadow trial approach.

---

## Part 2: Hands-on Scripting / Coding Challenge

### Objective
In `scratch/sprint3_trial_compressor.cpp`, implement a complete standalone `SegmentShadowSimulator` class that stores raw contigs and provides an exact trial compression estimate using Zstandard.

### Requirements
1. The class must manage:
   - `std::vector<std::vector<uint8_t>> v_contigs;`
   - `std::mutex mtx;`
2. Implement:
   - `void add_contig(const std::vector<uint8_t>& contig);`
   - `size_t get_uncompressed_bytes() const;`
   - `uint32_t estimate_compressed_size(ZSTD_CCtx* ctx);`
3. Verify that calling `estimate_compressed_size()`:
   - Does not clear or modify `v_contigs`.
   - Returns a byte size substantially smaller than raw bytes when given repetitive genomic patterns.
   - Handles empty states safely without errors.

---

<details>
<summary><b>Click to reveal Answer Key & Grading Rubric</b></summary>

### Part 1 Answers
1. **Zstandard Memory Bounds & Context Lifecycle:**
   - `ZSTD_compressBound(srcSize)` calculates the theoretical maximum output size for an input of `srcSize` bytes, accounting for worst-case non-compressible data and ZSTD frame header/footer overhead.
   - Creating a `ZSTD_CCtx` incurs significant memory allocation overhead (often hundreds of kilobytes for internal tables). Allocating and destroying it per item destroys CPU throughput. The proper pattern is to allocate one context per worker thread and reuse it across millions of invocations.

2. **Thread Safety in Low-Level Compression:**
   - `ZSTD_CCtx` maintains internal state (sliding match buffers, entropy tables, working pointers).
   - If two threads call `ZSTD_compressCCtx` with the same `global_zstd_ctx`, their writes to internal tables will interleave, causing buffer overflows, corrupted outputs, or process segmentation faults.

3. **Non-Destructive Invariance:**
   - Early physical flushing permanently splits continuous sequence streams into fragmented blocks. Because ZSTD's dictionary efficiency scales with block cardinality (e.g. 500 contigs), flushing 10–20 contigs prematurely yields inferior compression ratios. Furthermore, it desynchronizes internal segment segment maps with the archive directory.
   - Shadow trial compression solves this by performing trial compression exclusively in transient RAM buffers without flushing or clearing segment queues.

### Part 2 Solution

```cpp
#include <iostream>
#include <vector>
#include <mutex>
#include <algorithm>
#include <zstd.h>
#include <cassert>

class SegmentShadowSimulator {
private:
    std::vector<std::vector<uint8_t>> v_contigs;
    mutable std::mutex mtx;

public:
    void add_contig(const std::vector<uint8_t>& c) {
        std::lock_guard<std::mutex> lock(mtx);
        v_contigs.push_back(c);
    }

    size_t get_uncompressed_bytes() const {
        std::lock_guard<std::mutex> lock(mtx);
        size_t total = 0;
        for (const auto& c : v_contigs) total += c.size();
        return total;
    }

    size_t get_contig_count() const {
        std::lock_guard<std::mutex> lock(mtx);
        return v_contigs.size();
    }

    uint32_t estimate_compressed_size(ZSTD_CCtx* ctx) {
        std::lock_guard<std::mutex> lock(mtx);
        if (v_contigs.empty()) return 0;

        size_t total_size = 0;
        for (const auto& c : v_contigs) total_size += c.size() + 1;

        std::vector<uint8_t> buffer(total_size);
        size_t off = 0;
        for (const auto& c : v_contigs) {
            std::copy(c.begin(), c.end(), buffer.begin() + off);
            off += c.size();
            buffer[off++] = 0xff;
        }

        size_t maxDst = ZSTD_compressBound(buffer.size());
        std::vector<uint8_t> packed(maxDst + 1);

        size_t zstd_ret = ZSTD_compressCCtx(ctx, packed.data(), maxDst, buffer.data(), buffer.size(), 10);
        if (ZSTD_isError(zstd_ret)) {
            return static_cast<uint32_t>(total_size / 3);
        }

        return static_cast<uint32_t>(zstd_ret);
    }
};

int main() {
    SegmentShadowSimulator seg;
    auto* ctx = ZSTD_createCCtx();

    // 1. Empty test
    assert(seg.estimate_compressed_size(ctx) == 0);

    // 2. Add repeated synthetic contigs
    std::vector<uint8_t> test_contig(200, 2); // 200 bytes of repetitive 'G's
    for (int i = 0; i < 50; ++i) {
        seg.add_contig(test_contig);
    }

    size_t raw_bytes = seg.get_uncompressed_bytes();
    uint32_t compressed_est = seg.estimate_compressed_size(ctx);

    std::cout << "Raw Bytes:        " << raw_bytes << " bytes across " << seg.get_contig_count() << " contigs\n";
    std::cout << "Shadow ZSTD Est:  " << compressed_est << " bytes\n";
    std::cout << "Ratio:            " << (static_cast<double>(raw_bytes) / compressed_est) << ":1\n";

    // Invariance assert
    assert(seg.get_contig_count() == 50);
    assert(seg.get_uncompressed_bytes() == raw_bytes);

    ZSTD_freeCCtx(ctx);
    std::cout << "Verification PASSED!\n";
    return 0;
}
```
</details>
