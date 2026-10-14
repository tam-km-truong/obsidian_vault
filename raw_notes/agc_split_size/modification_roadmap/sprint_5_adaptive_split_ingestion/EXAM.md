# Sprint 5 Mastery Checkpoint & Exam

This checkpoint tests your understanding of feedback-based runway controllers, queue synchronization barriers, and adaptive thresholding.

---

## Part 1: Written Conceptual Exam

### Question 1: Queue Draining and Pipeline Stalls
In `AddSampleSplit`:
```cpp
while (!pq_contigs_desc->IsEmpty()) {
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}
```
1. Why is this loop required before executing `GetSimulatedArchiveSize`?
2. What would happen to size estimation accuracy if this loop were omitted?
3. What is the purpose of the periodic synchronization barrier every 25 genomes?

---

### Question 2: Mathematical Runway Analysis
Assume:
- `target_part_size` = $100,000,000$ bytes
- `stop_threshold` = $95,000,000$ bytes
- At the previous check ($N=50$ genomes): `last_true_size` = $70,000,000$ bytes
- At the current check ($N=60$ genomes): `true_size` = $85,000,000$ bytes

1. Compute the average compressed bytes added per genome over the last interval.
2. Compute the estimated number of genomes remaining before crossing the stop threshold.
3. What will `strict_check_interval` be set to for the next check if `is_strict = false`?
4. What would it be set to if `is_strict = true`?

---

### Question 3: The 95% Stop Threshold & Metadata Budget
Why does `AddSampleSplit` halt ingestion when `true_size` reaches $95\%$ of `target_part_size` rather than $100\%$? What specific data structures are emitted by AGC during `Close()` that occupy this remaining $5\%$ buffer?

---

## Part 2: Hands-on Scripting / Coding Challenge

### Objective
In `scratch/sprint5_runway_controller.cpp`, build a standalone adaptive feedback controller that simulates ingesting a stream of incoming files with noisy compression sizes and stops cleanly before reaching a 100 MB quota.

### Requirements
1. Define a `RunwayController` class with:
   - `uint64_t target_size;`
   - `uint64_t stop_threshold;`
   - `uint64_t strict_threshold;`
   - `size_t check_interval;`
2. Ingest 200 synthetic genomes (each adding between 500 KB and 3 MB compressed).
3. The controller must:
   - Start in coarse mode (passive checking).
   - Switch to strict mode at 75% target.
   - Adjust `check_interval` using the half-runway formula.
   - Stop ingestion when true size $\ge 95\%$ target.
4. Output a summary table showing step number, true size, check interval, and verify the final size never exceeds 100 MB.

---

<details>
<summary><b>Click to reveal Answer Key & Grading Rubric</b></summary>

### Part 1 Answers
1. **Queue Draining and Pipeline Stalls:**
   - Worker threads process contigs asynchronously from `pq_contigs_desc`. The queue drain loop ensures all contigs that were read from the current FASTA file are fully ingested and routed to their respective `CSegment` buffers before size calculation starts.
   - If omitted, unwritten contigs still waiting in `pq_contigs_desc` would not be counted by `CSegment::estimate_partial_compressed_size`, causing severe underestimation.
   - The periodic 25-genome synchronization barrier prevents unbounded memory growth in the priority queue if the file reader thread is substantially faster than compression worker threads.

2. **Mathematical Runway Analysis:**
   - $\Delta \text{Bytes} = 85,000,000 - 70,000,000 = 15,000,000$ bytes.
   - $\Delta \text{Genomes} = 60 - 50 = 10$ genomes.
   - $\text{Avg Bytes/Genome} = 15,000,000 / 10 = 1,500,000$ bytes/genome.
   - $\text{Remaining Runway} = 95,000,000 - 85,000,000 = 10,000,000$ bytes.
   - $\text{Estimated Genomes Left} = 10,000,000 / 1,500,000 = 6.66 \implies 6$ genomes.
   - If `is_strict = false`: $\text{Next Interval} = \text{clamp}(6 / 2, 2, 100) = \mathbf{3}$ genomes.
   - If `is_strict = true`: $\text{Next Interval} = \text{clamp}(6 / 2, 2, 10) = \mathbf{3}$ genomes.

3. **The 95% Stop Threshold & Metadata Budget:**
   - Reserving 5% ensures the final file does not exceed the target size after archive closure.
   - When `Close()` is called, AGC commits global archive metadata that cannot be flushed incrementally:
     - Global $k$-mer splitters table
     - Sample-to-contig index registry (`CCollection_V3`)
     - Segment partition directory maps
     - Archive header and footer metadata structures.

### Part 2 Solution

```cpp
#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <iomanip>

class RunwayController {
private:
    uint64_t target_size;
    uint64_t stop_threshold;
    uint64_t strict_threshold;
    uint64_t current_size = 0;
    uint64_t last_checked_size = 0;
    size_t genomes_since_check = 0;
    size_t check_interval = 2;
    bool strict_mode = false;
    bool is_strict_param = false;

public:
    RunwayController(uint64_t target, bool strict_param = false)
        : target_size(target),
          stop_threshold((target * 95) / 100),
          strict_threshold((target * 75) / 100),
          is_strict_param(strict_param) {}

    bool feedGenome(uint64_t genome_bytes, size_t genome_idx) {
        current_size += genome_bytes;
        genomes_since_check++;

        bool check = false;
        if (strict_mode) {
            if (genomes_since_check >= check_interval) check = true;
        } else {
            if (current_size >= strict_threshold) check = true;
        }

        if (check) {
            std::cout << "CHECK at genome " << genome_idx 
                      << " | Current Size: " << current_size / 1000000.0 << " MB"
                      << " | Interval: " << check_interval << "\n";

            if (current_size >= stop_threshold) {
                std::cout << ">>> Stop threshold reached (" << current_size << " >= " << stop_threshold << ")! Halting part.\n";
                return false; // Stop ingestion
            }

            if (last_checked_size > 0 && current_size > last_checked_size && genomes_since_check > 0) {
                uint64_t added = current_size - last_checked_size;
                uint64_t avg = added / genomes_since_check;
                if (avg > 0 && current_size < stop_threshold) {
                    uint64_t rem = stop_threshold - current_size;
                    size_t est_left = rem / avg;
                    check_interval = est_left / 2;
                    size_t max_int = is_strict_param ? 10 : 100;
                    check_interval = std::clamp(check_interval, (size_t)2, max_int);
                }
            }

            if (current_size >= strict_threshold && !strict_mode) {
                strict_mode = true;
                std::cout << ">>> Switched to Strict Mode (>= 75%)\n";
            }

            last_checked_size = current_size;
            genomes_since_check = 0;
        }

        return true;
    }

    uint64_t getFinalSize() const { return current_size; }
};

int main() {
    uint64_t TARGET = 100'000'000; // 100 MB
    RunwayController controller(TARGET);

    std::mt19937 rng(1337);
    std::uniform_int_distribution<uint64_t> dist(500'000, 2'500'000); // 0.5 MB to 2.5 MB per genome

    size_t consumed = 0;
    for (size_t i = 1; i <= 200; ++i) {
        uint64_t sz = dist(rng);
        if (!controller.feedGenome(sz, i)) {
            consumed = i;
            break;
        }
    }

    uint64_t final_size = controller.getFinalSize();
    std::cout << "\nIngestion completed! Consumed " << consumed << " genomes.\n";
    std::cout << "Final Size: " << final_size << " bytes (" << (final_size / 1000000.0) << " MB)\n";
    std::cout << "Within Target: " << (final_size <= TARGET ? "YES (PASSED)" : "NO (FAILED)") << "\n";
    return 0;
}
```
</details>
