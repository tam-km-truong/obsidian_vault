# Sprint 4 Study Guide: Lock-Free Dispatching & False Sharing Avoidance

In this sprint, you study multi-threaded reduction patterns, CPU cache coherency, and lock-free load balancing.

---

## 1. Key Concepts to Understand

### A. Dynamic Load Balancing with `fetch_add`
When processing thousands of segments with varying workloads:
- **Static Partitioning**: Thread 0 gets segments $0 \dots 2499$, Thread 1 gets $2500 \dots 4999$, etc. If Thread 0 happens to get heavy segments with 400 contigs each, while Thread 1 gets empty segments, Thread 1 sits idle while Thread 0 becomes a bottleneck.
- **Dynamic Work Stealing / Dispatching**:
  ```cpp
  uint32_t j = id_segment.fetch_add(1);
  if (j >= no_segments) break;
  ```
  `fetch_add` is an atomic CPU instruction (`LOCK XADD` on x86, `LDADD` on ARM64) that completes in nanoseconds. Threads dynamically grab the next available segment index. Faster threads naturally process more segments, ensuring 100% CPU utilization until the entire collection is drained.

### B. The Cache Coherency Trap: False Sharing vs Local Reduction
Consider what happens if each thread directly writes to a shared atomic variable on every segment:
```cpp
// DANGEROUS / HIGH CONTENTION:
while (true) {
    uint32_t j = id_segment.fetch_add(1);
    if (j >= no_segments) break;
    // WRITING TO SHARED ATOMIC EVERY ITERATION:
    total_unwritten_compressed += seg->estimate(...);
}
```
- Every time a CPU core executes `total_unwritten_compressed += ...`, it must acquire exclusive ownership of the cache line (typically 64 bytes) holding `total_unwritten_compressed`.
- The cache line is forcibly invalidated across all other CPU cores (**Cache Line Bouncing** / **False Sharing**), stalling memory pipelines and destroying multi-threaded performance.

**The Solution (Thread-Local Reduction)**:
```cpp
uint64_t local_sum = 0; // Stack variable: local to CPU core's L1 cache
while (true) {
    uint32_t j = id_segment.fetch_add(1);
    if (j >= no_segments) break;
    local_sum += seg->estimate(...); // Zero cross-core bus traffic!
}
total_unwritten_compressed += local_sum; // Exactly one atomic write per thread!
```

### C. Resource Cleanliness in Multi-Threading
When spawning worker threads directly (via `std::thread`):
- Any dynamically allocated per-thread resources (such as `ZSTD_CCtx*`) must be freed before the thread routine returns.
- Using RAII or explicit cleanup before thread exit guarantees zero memory leaks across thousands of size evaluation checkpoints.

---

## 2. Recommended Readings & Documentation

1. **Fedya's Guide to False Sharing & Cache Contention**:
   [https://mechanical-sympathy.blogspot.com/2011/07/false-sharing.html](https://mechanical-sympathy.blogspot.com/2011/07/false-sharing.html)
2. **cppreference: `std::atomic::fetch_add`**:
   [https://en.cppreference.com/w/cpp/atomic/atomic/fetch_add](https://en.cppreference.com/w/cpp/atomic/atomic/fetch_add)
3. **Herb Sutter: Effective Concurrency (Eliminate False Sharing)**:
   [http://www.gotw.ca/publications/concurrency-ddj.htm](http://www.gotw.ca/publications/concurrency-ddj.htm)

---

## 3. Common Gotchas & Personal Notes

1. **`atomic::load()` on Read**:
   When reading the final atomic total, call `total_unwritten_compressed.load()` explicitly to make the memory synchronization intent clear to readers.
2. **Segment Nullability**:
   In AGC, `v_segments` may contain null pointers for uninitialized splitter buckets. Always check `if (v_segments[j] != nullptr)` before dereferencing.

---

## 4. 10-Minute Mini Practice Exercise

Benchmark the speed difference between shared atomic updates vs local reduction:

```cpp
#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>

const size_t ITERS = 50'000'000;
const size_t THREADS = 4;

void testContended() {
    std::atomic<uint64_t> sum{0};
    auto t1 = std::chrono::high_resolution_clock::now();
    std::vector<std::thread> v;
    for (size_t t = 0; t < THREADS; ++t) {
        v.emplace_back([&] {
            for (size_t i = 0; i < ITERS / THREADS; ++i) sum++;
        });
    }
    for (auto& t : v) t.join();
    auto t2 = std::chrono::high_resolution_clock::now();
    std::cout << "Contended: " << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << " ms\n";
}

void testLocal() {
    std::atomic<uint64_t> sum{0};
    auto t1 = std::chrono::high_resolution_clock::now();
    std::vector<std::thread> v;
    for (size_t t = 0; t < THREADS; ++t) {
        v.emplace_back([&] {
            uint64_t local = 0;
            for (size_t i = 0; i < ITERS / THREADS; ++i) local++;
            sum += local;
        });
    }
    for (auto& t : v) t.join();
    auto t2 = std::chrono::high_resolution_clock::now();
    std::cout << "Local reduction: " << std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << " ms\n";
}

int main() {
    testContended();
    testLocal();
    return 0;
}
```
Observe how the local reduction version runs over $10\times$ to $50\times$ faster!
