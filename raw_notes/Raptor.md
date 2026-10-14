---
raw_tags:
  - build
  - "hibf requires openmp"
  - "recent call first"
  - "cmake error"
  - "your compiler"
  - "call stack"
  - hibf_config_error
  - support
word_count: 64
char_count: 591
processed: true
processed_note: \"[[Raptor - Hierarchical Interleaved Bloom Filters]]\"
---

CMake Error at build/_deps/hibf-src/cmake/configuration.cmake:50 (message):

    HIBF requires OpenMP, but your compiler does not support it.

Call Stack (most recent call first):

  build/_deps/hibf-src/cmake/configuration.cmake:151 (hibf_config_error)

  build/_deps/hibf-src/CMakeLists.txt:26 (include)