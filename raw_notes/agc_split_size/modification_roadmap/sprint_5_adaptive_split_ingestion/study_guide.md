# Sprint 5 Study Guide: Feedback Control Systems in Batch Ingestion

In this sprint, you explore how adaptive feedback controllers can bound memory and storage limits in non-deterministic streaming architectures.

---

## 1. Key Concepts to Understand

### A. Queue Drain Dynamics Before Metrics Evaluation
AGC uses a multi-producer multi-consumer bounded priority queue `CBoundedPQueue<task_t> pq_contigs_desc`:
- The main thread reads contigs from FASTA and emplaces tasks into the queue.
- Multiple worker threads pop tasks and route contigs to segment buffers.
- **The Critical Gotcha**: If you inspect segment sizes while the queue still contains 1,000 pending contigs, those pending contigs are completely invisible!
- **The Solution**:
  ```cpp
  while (!pq_contigs_desc->IsEmpty()) {
      std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }
  ```
  Draining the queue ensures every ingested contig has been delta-encoded and settled into its target `CSegment` before size estimation begins.

### B. Adaptive Damping (The "Half-Runway" Rule)
In control theory, sampling a non-linear process requires preventing overshoot while minimizing sampling cost.
- If we check every genome ($N=1$), we execute shadow ZSTD compressions continuously, reducing overall compression throughput.
- If we check every 100 genomes, a batch of large or non-redundant genomes can easily blow past the 95% threshold.
- **The Half-Runway Rule**:
  $$\text{NextCheck} = \frac{\text{RemainingRunway}}{2}$$
  If the model predicts there is room for 40 genomes, we check in 20 genomes. If the next 20 genomes compress as expected, there is room for 20 more, so we check in 10, then 5, then 2.
  This **exponential back-off towards the boundary** guarantees high speed early on and extreme surgical precision near the boundary!

### C. The Strict Flag (`-x` / `is_strict`)
By default, AGC caps the check interval to $\le 100$ genomes.
When the user specifies `-x`:
```cpp
size_t max_interval = is_strict ? 10 : 100;
```
For collections containing highly variable genome sizes (e.g. mix of small viruses and massive eukaryotic chromosomes), `-x` guarantees the controller will re-verify size at least every 10 genomes, preventing unexpected bursts.

### D. The Emergency Brake
What happens if a user sets `-p 50M` and feeds a 500 MB plant chromosome?
Even without the 95% shadow check, committed disk bytes alone will exceed 50 MB:
```cpp
if (naive_size >= target_part_size) {
    if (verbosity > 0)
        cerr << "Absolute target size reached (" << naive_size << " bytes). Finalizing part...\n";
    break;
}
```
This hard ceiling prevents an unbounded archive from forming under extreme input anomalies.

---

## 2. Recommended Readings & Documentation

1. **Karl Johan Åström: Feedback Systems: An Introduction for Scientists and Engineers**:
   Principles of adaptive sampling and setpoint tracking.
2. **AGC Architecture & Priority Queue Internals**:
   Review `src/common/bounded_pqueue.h` in the AGC repository.

---

## 3. Common Gotchas & Personal Notes

1. **Minimum Interval Clamping**:
   Never allow `strict_check_interval` to drop to 0! If `strict_check_interval == 0`, `genomes_since_last_check >= 0` is always true, causing the compressor to freeze in an endless check loop. Clamping to `std::max(2ULL, ...)` ensures progress.
2. **First Genome Exemption**:
   At least one genome must be accepted per archive part, even if it alone exceeds `target_part_size`. Otherwise, the partition loop would enter an infinite loop trying to compress the same oversized genome repeatedly.

---

## 4. 10-Minute Mini Practice Exercise

Write a standalone test simulating the adaptive runway calculator:

```cpp
#include <iostream>
#include <algorithm>

int main() {
    uint64_t stop_threshold = 95'000'000;
    uint64_t true_size = 75'000'000;
    uint64_t last_true_size = 70'000'000;
    size_t genomes_since_last = 5;
    bool is_strict = false;

    uint64_t bytes_added = true_size - last_true_size;
    uint64_t avg_per_genome = bytes_added / genomes_since_last; // 1,000,000 bytes/genome
    uint64_t remaining = stop_threshold - true_size;            // 20,000,000 bytes
    size_t estimated_left = remaining / avg_per_genome;          // 20 genomes

    size_t next_interval = estimated_left / 2;                   // 10 genomes
    size_t max_interval = is_strict ? 10 : 100;

    next_interval = std::clamp(next_interval, (size_t)2, max_interval);

    std::cout << "Avg bytes/genome: " << avg_per_genome << "\n";
    std::cout << "Genomes remaining: " << estimated_left << "\n";
    std::cout << "Next check scheduled in: " << next_interval << " genomes\n";
    return 0;
}
```
