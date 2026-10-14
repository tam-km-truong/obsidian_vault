# Sprint 4: Multi-Threaded Shadow Size Estimator

## 1. Goal & Scope
Implement `CAGCCompressor::GetSimulatedArchiveSize` to rapidly evaluate the compressed size of all unwritten segment buffers across thousands of active segments in parallel. The engine must distribute work across `n_t` threads using lock-free atomic counters, maintain thread-local ZSTD contexts, prevent cache-line bouncing, and combine the unwritten shadow size with `out_archive->GetCurrentOffset()`.

---

## 2. Time Estimation
| Activity | Description | Estimated Hours |
| :--- | :--- | :--- |
| **Reading & Concepts** | Lock-free task distribution, false sharing, thread-local contexts | 1.5 hrs |
| **Implementation** | Implement `GetSimulatedArchiveSize` in `src/core/agc_compressor.cpp` | 1.5 hrs |
| **Benchmarking** | Measure multi-threaded scaling across 1, 4, 8, and 16 threads | 1.0 hr |
| **Profiling** | Verify absence of thread leaks, context leaks, or lock contention | 0.5 hr |
| **Exam & Challenge** | Written conceptual test + parallel reduction challenge in `EXAM.md` | 1.0 hr |
| **Total** | | **~5.5 hrs** |

---

## 3. Architecture & Interface Specs

### Compressor Declaration (`src/core/agc_compressor.h`)
```cpp
class CAGCCompressor
{
    // ...
public:
    uint64_t GetSimulatedArchiveSize(const uint32_t no_threads);
};
```

### Implementation (`src/core/agc_compressor.cpp`)
```cpp
uint64_t CAGCCompressor::GetSimulatedArchiveSize(const uint32_t n_t)
{
    atomic<uint64_t> total_unwritten_compressed{0};
    vector<thread> v_threads;
    v_threads.reserve(n_t);

    atomic<uint32_t> id_segment{0};

    for (uint32_t i = 0; i < n_t; ++i)
    {
        v_threads.emplace_back([&] {
            auto zstd_ctx = ZSTD_createCCtx();
            uint64_t local_sum = 0;

            while (true)
            {
                uint32_t j = id_segment.fetch_add(1);

                if (j >= no_segments)
                    break;

                if (v_segments[j] != nullptr)
                    local_sum += v_segments[j]->estimate_partial_compressed_size(zstd_ctx);
            }

            total_unwritten_compressed += local_sum;
            ZSTD_freeCCtx(zstd_ctx);
        });
    }

    join_threads(v_threads);
    
    return out_archive->GetCurrentOffset() + total_unwritten_compressed.load();
}
```

---

## 4. Concurrency & Performance Design Patterns

```
                                  [ id_segment.fetch_add(1) ]
                                /              |              \
                               v               v               v
                        Thread 0            Thread 1       Thread N-1
                     (owns ZSTD_CCtx)    (owns ZSTD_CCtx) (owns ZSTD_CCtx)
                            |                  |               |
                         Iterates           Iterates        Iterates
                         Segments           Segments        Segments
                            |                  |               |
                       local_sum +=       local_sum +=    local_sum +=
                            \                  |               /
                             \                 |              /
                              v                v             v
                           [ atomic<uint64_t> total_unwritten_compressed ]
                                               +
                                  [ out_archive->GetCurrentOffset() ]
                                               =
                                    TRUE TOTAL ARCHIVE SIZE
```

1. **Lock-Free Atomic Work Dispatching**:
   Rather than partitioning segment indices statically (which leads to straggler threads if some segments have 450 contigs while others have 0), threads dynamically grab the next available segment ID using `id_segment.fetch_add(1)` with perfect load balancing.
2. **Elimination of False Sharing / Cache Bouncing**:
   Threads accumulate partial sizes in a local stack variable (`uint64_t local_sum`). They write to the global atomic `total_unwritten_compressed` **only once** upon thread completion, eliminating inter-core cache line invalidation.
3. **Isolated Thread Contexts**:
   Each worker creates its own `ZSTD_CCtx` via `ZSTD_createCCtx()` upon launch and destroys it via `ZSTD_freeCCtx()` upon exit, avoiding mutex synchronization during compression.

---

## 5. Step-by-Step Task Checklist

- [ ] **Step 4.1:** Declare `uint64_t GetSimulatedArchiveSize(const uint32_t no_threads);` in `src/core/agc_compressor.h`.
- [ ] **Step 4.2:** Implement thread spawning and atomic index scheduling in `src/core/agc_compressor.cpp`.
- [ ] **Step 4.3:** Allocate and safely clean up per-thread `ZSTD_CCtx` instances.
- [ ] **Step 4.4:** Accumulate partial results into local variables before updating the shared atomic total.
- [ ] **Step 4.5:** Join worker threads using AGC's `join_threads(v_threads)` utility.
- [ ] **Step 4.6:** Return the sum of committed disk offset (`out_archive->GetCurrentOffset()`) and total unwritten compressed size.
- [ ] **Step 4.7:** Benchmark execution latency to ensure the check completes in $< 250\text{ ms}$ over 10,000 active segments.

---

## 6. Unit Test Specifications

```cpp
#include "doctest.h"
#include <atomic>
#include <thread>
#include <vector>

TEST_CASE("MultithreadedEstimator: Atomic Work-Stealing Pattern") {
    const size_t NUM_ITEMS = 1000;
    const size_t NUM_THREADS = 4;
    std::atomic<uint32_t> next_id{0};
    std::atomic<uint64_t> total_sum{0};

    std::vector<std::thread> workers;
    for (size_t t = 0; t < NUM_THREADS; ++t) {
        workers.emplace_back([&] {
            uint64_t local = 0;
            while (true) {
                uint32_t idx = next_id.fetch_add(1);
                if (idx >= NUM_ITEMS) break;
                local += idx;
            }
            total_sum += local;
        });
    }

    for (auto& w : workers) w.join();

    // Sum of 0 to 999 = (999 * 1000) / 2 = 499500
    CHECK(total_sum.load() == 499500);
}
```

---

## 7. Acceptance Criteria

1. `GetSimulatedArchiveSize` correctly aggregates shadow compressed bytes across all active `v_segments`.
2. Work distribution scales linearly across available CPU threads without race conditions.
3. Every thread-local `ZSTD_CCtx` is guaranteed to be freed without memory leaks.
4. Total execution time of `GetSimulatedArchiveSize` is negligible relative to overall genome ingestion time.
