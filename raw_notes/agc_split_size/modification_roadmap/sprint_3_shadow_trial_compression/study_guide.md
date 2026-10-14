# Sprint 3 Study Guide: In-Memory Compression & The Zstandard C API

In this sprint, you explore low-level buffer management and the Zstandard C API to create non-destructive simulation routines.

---

## 1. Key Concepts to Understand

### A. The Low-Level Zstandard C API
While many libraries provide high-level C++ wrappers, performance-critical genomic tools interface directly with `zstd.h`:
- `ZSTD_CCtx`: Compression context object containing internal state, hash tables, and entropy tables. Allocating a context (`ZSTD_createCCtx`) is expensive; reusing an existing context across multiple compressions is very fast.
- `ZSTD_compressBound(srcSize)`: Calculates the maximum possible compressed size in the worst-case scenario (e.g. incompressible random data). Passing a destination buffer sized to `ZSTD_compressBound(srcSize)` guarantees that compression will never overflow memory.
- `ZSTD_compressCCtx(cctx, dst, dstCap, src, srcSize, compressionLevel)`: Compresses `src` into `dst` using the specified level (1–22). Returns the number of compressed bytes written, or an error code.
- `ZSTD_isError(code)`: Checks if the return code indicates an error (e.g. `dstCap` too small, corrupted input).

```cpp
#include <zstd.h>

ZSTD_CCtx* ctx = ZSTD_createCCtx();
size_t maxDstSize = ZSTD_compressBound(srcSize);
std::vector<uint8_t> dst(maxDstSize);

size_t compressedSize = ZSTD_compressCCtx(ctx, dst.data(), maxDstSize, src.data(), srcSize, 10);
if (ZSTD_isError(compressedSize)) {
    // Handle error
}
ZSTD_freeCCtx(ctx);
```

### B. Contig Concatenation with Delimiters (`0xff`)
In AGC, contigs are 2-bit encoded nucleotide sequences:
- `00` = A, `01` = C, `10` = G, `11` = T.
- The byte `0xff` (`255`) is an invalid nucleotide code used as an out-of-band sentinel to delimit separate contigs inside a packed segment vector.
- When `simulate_store` packs contigs for trial compression, it mimics AGC's exact internal serialization format:
  ```cpp
  for (const auto& d : v_data) {
      copy(d.begin(), d.end(), buffer.begin() + offset);
      offset += d.size();
      buffer[offset++] = 0xff; 
  }
  ```

### C. Non-Destructive Invariance
In software engineering, non-destructive simulation is an essential pattern:
- **State Mutation vs Observation**: A standard flush empties `v_lzp.clear()` and writes blocks to disk.
- **Shadow Simulation**: Copies data to a temporary stack/heap buffer, runs the algorithm, measures output metrics, and lets RAII clean up the scratch buffer. The originating object remains 100% bitwise unchanged.

---

## 2. Recommended Readings & Documentation

1. **Zstandard Official Documentation & Manual**:
   [https://facebook.github.io/zstd/zstd_manual.html](https://facebook.github.io/zstd/zstd_manual.html)
2. **Yann Collet: Zstandard Design Principles**:
   [https://github.com/facebook/zstd](https://github.com/facebook/zstd)
3. **cppreference: `std::copy` & buffer operations**:
   [https://en.cppreference.com/w/cpp/algorithm/copy](https://en.cppreference.com/w/cpp/algorithm/copy)

---

## 3. Common Gotchas & Personal Notes

1. **Reusing `ZSTD_CCtx` Across Threads**:
   `ZSTD_CCtx` is **NOT thread-safe**! Never share a single `ZSTD_CCtx` pointer across concurrent threads. Each worker thread must own its own context.
2. **Level 10 Performance**:
   AGC compresses segment packs at level 10 by default. Testing shadow buffers at level 10 provides an exact byte-for-byte representation of what will eventually be written to disk.
3. **Empty Vector Guard**:
   If `v_data` is empty, `total_size` is 0. Attempting to allocate `vector<uint8_t>(0)` and passing its data pointer to `ZSTD_compressCCtx` can produce warnings or unexpected behavior. Always return `0` early if `v_data.empty()`.

---

## 4. 10-Minute Mini Practice Exercise

Write a standalone test program compressing synthetic contigs with ZSTD:

```cpp
#include <iostream>
#include <vector>
#include <zstd.h>

int main() {
    std::vector<std::vector<uint8_t>> contigs = {
        {0, 1, 2, 3, 0, 1, 2, 3},
        {1, 1, 1, 1, 2, 2, 2, 2},
        {3, 2, 1, 0, 3, 2, 1, 0}
    };
    
    size_t total = 0;
    for (const auto& c : contigs) total += c.size() + 1;
    
    std::vector<uint8_t> buffer(total);
    size_t off = 0;
    for (const auto& c : contigs) {
        std::copy(c.begin(), c.end(), buffer.begin() + off);
        off += c.size();
        buffer[off++] = 0xff;
    }
    
    auto* ctx = ZSTD_createCCtx();
    size_t maxDst = ZSTD_compressBound(buffer.size());
    std::vector<uint8_t> out(maxDst);
    
    size_t cSize = ZSTD_compressCCtx(ctx, out.data(), maxDst, buffer.data(), buffer.size(), 10);
    std::cout << "Raw: " << buffer.size() << " bytes -> ZSTD: " << cSize << " bytes\n";
    
    ZSTD_freeCCtx(ctx);
    return 0;
}
```
Compile with:
```bash
g++-13 -std=c++20 practice.cpp -lzstd -o practice && ./practice
```
