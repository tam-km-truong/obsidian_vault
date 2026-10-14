---
category: knowledge
tags:
  - raptor
  - bloom-filter
  - search
  - cmake
source_raw: "[[Raptor]]"
status: processed
---

# Raptor: Hierarchical Interleaved Bloom Filters (HIBF)

## Overview
**Raptor** scales sequence search across millions of genomes by organizing Interleaved Bloom Filters (IBF) into a hierarchical tree topology (HIBF), outperforming flat BIGSI indexes.

---

## Compilation Troubleshooting
- **Error:** `CMake Error at build/_deps/hibf-src/cmake/configuration.cmake:50: HIBF requires OpenMP, but your compiler does not support it.`
- **Cause:** Default Apple Clang on macOS does not bundle OpenMP.
- **Solution:**
  ```bash
  brew install libomp
  cmake -B build -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++
  ```

## Related Notes
- [[BIGSI - Ultra-Fast Indexing of Bacterial & Viral Data]] – Flat predecessor
