# Sprint 2 Mastery Checkpoint & Exam

This checkpoint tests your architectural understanding of asynchronous batching pipelines, thread-safe resource querying, and pipeline buffer dynamics.

---

## Part 1: Written Conceptual Exam

### Question 1: Thread-Safe Metrics & Lock Contention
In `CArchive::GetCurrentOffset()`, why is `lock_guard<mutex> lck(mtx)` used instead of an atomic read of `f_offset`?
```cpp
size_t CArchive::GetCurrentOffset()
{
    lock_guard<mutex> lck(mtx);
    if (input_mode) return 0;
    flush_out_buffers();
    return f_offset;
}
```
What side effect does `flush_out_buffers()` produce, and why must it be executed under the lock?

---

### Question 2: The Memory Tail Under Non-Uniform Distributions
Suppose an AGC compression job runs on 1,000 bacterial genomes with 10,000 segment groups.
1. If sequence splitters are non-uniformly distributed (Zipfian distribution where 5% of segments receive 80% of all contigs), how does this affect the memory tail compared to a uniform distribution?
2. Why does a static soft flush (e.g. flushing segments with $\ge 250$ contigs) fail to solve the underestimation problem on hyper-variable genomes?

---

### Question 3: Spot the Flaw — Static Ratio Estimation
A developer suggests estimating final size using:
```cpp
uint64_t est = disk_offset + (raw_uncompressed_bytes_in_ram / 3.0);
```
Give two concrete genomic scenarios where this formula will either drastically overshoot or undershoot the partition threshold by $> 50\%$.

---

## Part 2: Hands-on Scripting / Coding Challenge

### Objective
Write a simulation script in `scratch/sprint2_tail_sim.cpp` simulating $N$ segments receiving items according to a power-law distribution.

### Requirements
1. Create a `Segment` struct holding a vector of unwritten items and a total count of flushed items.
2. Simulate $K = 50,000$ incoming items distributed across $M = 2,000$ segments using non-uniform hashing.
3. Flush segments to a simulated disk count whenever a segment hits $B = 100$ items.
4. Calculate and display:
   - Total items committed to disk
   - Total items pending in RAM
   - The ratio of pending-to-committed items
   - The error percentage if one assumes disk items equals total items.

---

<details>
<summary><b>Click to reveal Answer Key & Grading Rubric</b></summary>

### Part 1 Answers
1. **Thread-Safe Metrics & Lock Contention:**
   - `f_offset` is updated when `flush_out_buffers()` writes data to disk. Reading `f_offset` without locking would be a data race while other threads append data.
   - Crucially, `flush_out_buffers()` actually drains pending in-memory stream buffers into `f_offset`. If not executed under `mtx`, another thread could be modifying the buffer concurrently, causing heap corruption or partial writes.

2. **The Memory Tail Under Non-Uniform Distributions:**
   - Under a Zipfian distribution, the vast majority of segments receive very few contigs (e.g. 5 to 50 contigs).
   - If a static threshold like $\ge 250$ contigs is used for soft flushing, the long tail of 95% of segments NEVER reach 250 contigs!
   - Consequently, those thousands of segments never flush during execution, keeping their data trapped in RAM until `Close()`.

3. **Spot the Flaw — Static Ratio Estimation:**
   - *Scenario A (Clonal / Highly Redundant isolates)*: Genomes of identical *E. coli* strains have compression ratios exceeding 25:1. Dividing raw bytes by 3 overestimates the tail size by $> 800\%$, prematurely aborting the archive when it is only 20% full.
   - *Scenario B (Divergent Metagenomic Reads / Non-Redundant)*: Metagenomic samples or hypervariable plasmid DNA have low compression ratios (~1.3:1). Dividing by 3 underestimates the tail by $> 50\%$, causing the final file to massively overshoot the user's partition limit.

### Part 2 Solution

```cpp
#include <iostream>
#include <vector>
#include <random>
#include <iomanip>

struct Segment {
    size_t in_ram = 0;
    size_t flushed = 0;
};

int main() {
    const size_t NUM_SEGMENTS = 2000;
    const size_t TOTAL_ITEMS = 50000;
    const size_t BATCH_LIMIT = 100;

    std::vector<Segment> segments(NUM_SEGMENTS);

    // Exponential distribution to model power-law / non-uniform splitter density
    std::mt19937 rng(42);
    std::exponential_distribution<double> dist(3.5);

    for (size_t i = 0; i < TOTAL_ITEMS; ++i) {
        double r = dist(rng);
        size_t seg_id = static_cast<size_t>(r * NUM_SEGMENTS) % NUM_SEGMENTS;

        segments[seg_id].in_ram++;
        if (segments[seg_id].in_ram >= BATCH_LIMIT) {
            segments[seg_id].flushed += segments[seg_id].in_ram;
            segments[seg_id].in_ram = 0;
        }
    }

    size_t total_flushed = 0;
    size_t total_in_ram = 0;
    for (const auto& s : segments) {
        total_flushed += s.flushed;
        total_in_ram += s.in_ram;
    }

    std::cout << "--- Memory Tail Simulation Results ---\n";
    std::cout << "Total items processed: " << TOTAL_ITEMS << "\n";
    std::cout << "Committed to disk:     " << total_flushed << " (" << (total_flushed * 100.0 / TOTAL_ITEMS) << "%)\n";
    std::cout << "Hidden in RAM tail:    " << total_in_ram << " (" << (total_in_ram * 100.0 / TOTAL_ITEMS) << "%)\n";
    std::cout << "Naive Underestimation: " << std::fixed << std::setprecision(2) 
              << (static_cast<double>(TOTAL_ITEMS) / total_flushed) << "x\n";

    return 0;
}
```
</details>
