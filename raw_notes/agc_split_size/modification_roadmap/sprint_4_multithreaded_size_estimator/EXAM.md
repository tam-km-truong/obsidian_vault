# Sprint 4 Mastery Checkpoint & Exam

This checkpoint tests your understanding of multi-threaded data reduction, atomic work queues, and CPU cache performance.

---

## Part 1: Written Conceptual Exam

### Question 1: Atomic Scheduling Mechanics
Analyze the following loop:
```cpp
while (true) {
    uint32_t j = id_segment.fetch_add(1);
    if (j >= no_segments)
        break;
    process(j);
}
```
1. Is it possible for two threads to process the same index `j`? Why or why not?
2. When the last segment `no_segments - 1` is claimed, what value does `id_segment` hold after all threads finish? Does this cause an overflow or out-of-bounds error?

---

### Question 2: False Sharing & Memory Bus Saturation
1. What is a CPU cache line, and what is its typical size in modern x86_64 and Apple Silicon ARM CPUs?
2. Explain what happens at the hardware level (MESI / MOESI protocol) when multiple CPU cores frequently execute atomic read-modify-write instructions on the same memory address.

---

### Question 3: Spot the Bug — Concurrency Leak
Identify the severe bug in the following multi-threaded routine:

```cpp
void runWorkers(size_t n_threads) {
    std::vector<std::thread> workers;
    for (size_t i = 0; i < n_threads; ++i) {
        workers.emplace_back([] {
            // Do computation
        });
    }
    // End of function scope
}
```
What happens when `runWorkers()` exits? How must it be resolved?

---

## Part 2: Hands-on Scripting / Coding Challenge

### Objective
In `scratch/sprint4_parallel_scanner.cpp`, implement a multi-threaded parallel byte counter that scans a mock vector of 10,000 segments.

### Requirements
1. Define a `MockSegment` holding a random size between 0 and 100,000 bytes.
2. Implement a function:
   ```cpp
   uint64_t parallelScan(const std::vector<MockSegment>& segments, size_t num_threads);
   ```
3. Use `std::atomic<uint32_t>` to dynamically distribute segment indices among the threads.
4. Each thread must accumulate its partial sum locally before adding to a single global atomic accumulator.
5. Benchmark and assert that the multi-threaded sum matches a single-threaded baseline (`std::accumulate`) with bitwise accuracy.

---

<details>
<summary><b>Click to reveal Answer Key & Grading Rubric</b></summary>

### Part 1 Answers
1. **Atomic Scheduling Mechanics:**
   - No, two threads can never receive the same `j`. `fetch_add(1)` is executed atomically by the hardware memory controller with total sequential consistency; each caller receives the unique previous value before incrementing.
   - When all $N$ threads exit, `id_segment` will equal `no_segments + n_threads - 1` (since each thread increments once past the limit before breaking). This does not cause an out-of-bounds error because the `if (j >= no_segments) break;` guard prevents dereferencing.

2. **False Sharing & Memory Bus Saturation:**
   - A cache line is the smallest unit of data transferred between main memory and CPU L1/L2/L3 caches, typically 64 bytes wide.
   - Under MESI/MOESI cache coherence protocols, an atomic write requires the executing core to broadcast an invalidation signal to all other cores. When multiple cores repeatedly write to the same cache line, the line ping-pongs between core caches ("cache line bouncing"), saturating the interconnect bus and stalling CPU pipelines.

3. **Spot the Bug — Concurrency Leak:**
   - The destructor of `std::thread` checks if the thread object is still *joinable* (`joinable() == true`). If `workers` goes out of scope without having called `.join()` or `.detach()`, `std::terminate()` is invoked, crashing the entire process!
   - *Fix:*
     ```cpp
     for (auto& t : workers) {
         if (t.joinable()) t.join();
     }
     ```

### Part 2 Solution

```cpp
#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <numeric>
#include <chrono>
#include <cassert>

struct MockSegment {
    size_t byte_size;
};

uint64_t parallelScan(const std::vector<MockSegment>& segments, size_t num_threads) {
    std::atomic<uint32_t> next_idx{0};
    std::atomic<uint64_t> total_sum{0};
    std::vector<std::thread> workers;
    workers.reserve(num_threads);

    const size_t total_segs = segments.size();

    for (size_t t = 0; t < num_threads; ++t) {
        workers.emplace_back([&] {
            uint64_t local = 0;
            while (true) {
                uint32_t idx = next_idx.fetch_add(1, std::memory_order_relaxed);
                if (idx >= total_segs) break;
                local += segments[idx].byte_size;
            }
            total_sum.fetch_add(local, std::memory_order_relaxed);
        });
    }

    for (auto& w : workers) {
        if (w.joinable()) w.join();
    }

    return total_sum.load();
}

int main() {
    const size_t COUNT = 10000;
    std::vector<MockSegment> segments(COUNT);
    for (size_t i = 0; i < COUNT; ++i) {
        segments[i].byte_size = (i * 37) % 50000;
    }

    // Baseline single-threaded
    uint64_t baseline = 0;
    for (const auto& s : segments) baseline += s.byte_size;

    // Parallel scan
    uint64_t parallel_result = parallelScan(segments, 4);

    std::cout << "Baseline: " << baseline << " bytes\n";
    std::cout << "Parallel: " << parallel_result << " bytes\n";
    assert(baseline == parallel_result);
    std::cout << "Verification PASSED!\n";
    return 0;
}
```
</details>
