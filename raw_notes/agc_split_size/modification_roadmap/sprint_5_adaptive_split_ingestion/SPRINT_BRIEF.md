# Sprint 5: Adaptive Split Ingestion & Checkpoint Controller

## 1. Goal & Scope
Implement `CAGCCompressor::AddSampleSplit`, the core algorithmic controller governing partitioned compression in AGC. The controller orchestrates multi-genome ingestion, periodic queue synchronization, two-stage threshold detection (75% strict threshold, 95% stop threshold), dynamic runway calculation, and emergency braking.

---

## 2. Time Estimation
| Activity | Description | Estimated Hours |
| :--- | :--- | :--- |
| **Reading & Concepts** | AGC queue pipelines (`CBoundedPQueue`), feedback loop control, dynamic runway | 2.0 hrs |
| **Implementation** | Implement `CAGCCompressor::AddSampleSplit` in `src/core/agc_compressor.cpp` | 2.0 hrs |
| **Edge-Case Tuning** | Verify strict mode bounds (`-x`), minimum intervals, and single-genome overflow | 1.0 hr |
| **Exam & Challenge** | Written conceptual test + feedback controller simulator in `EXAM.md` | 1.0 hr |
| **Total** | | **~6.0 hrs** |

---

## 3. Architecture & Interface Specs

### Compressor Header Declaration (`src/core/agc_compressor.h`)
```cpp
class CAGCCompressor
{
    // ...
public:
    size_t AddSampleSplit(
        const vector<pair<string, string>>& _v_sample_file_name,
        const uint32_t no_threads,
        const uint64_t target_part_size,
        const bool is_strict);
};
```

### Ingestion & Control Logic (`src/core/agc_compressor.cpp`)
```cpp
size_t CAGCCompressor::AddSampleSplit(
    const vector<pair<string, string>>& _v_sample_file_name,
    const uint32_t no_threads,
    const uint64_t target_part_size,
    const bool is_strict)
{
    // 1. Thread and queue setup
    // ... setup pq_contigs_desc and start_compressing_threads ...

    // Threshold definitions
    uint64_t stop_threshold = (target_part_size * 95) / 100;     // 95% target
    uint64_t strict_threshold = (target_part_size * 75) / 100;   // 75% target
    uint64_t buffer_offset = (target_part_size * 40) / 100;      // Initial seed offset

    size_t strict_check_interval = 2; // Dynamic interval
    uint64_t last_true_size = 0;
    bool strict_mode = false;
    size_t genomes_since_last_check = 0;
    size_t samples_consumed = 0;

    for (const auto& current_sf : _v_sample_file_name)
    {
        // Ingest contigs from genome file into pq_contigs_desc
        // ...
        samples_consumed++;
        genomes_since_last_check++;

        // 1. Periodic Synchronization: Prevent raw data backlog every 25 genomes
        if (samples_consumed % 25 == 0)
        {
            while (!pq_contigs_desc->IsEmpty())
                std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }

        uint64_t naive_size = GetCurrentArchiveSizeEstimate();
        bool run_check = false;

        // 2. Determine if size check is required
        if (strict_mode)
        {
            if (genomes_since_last_check >= strict_check_interval)
                run_check = true;
        }
        else
        {
            if (naive_size + buffer_offset >= strict_threshold)
                run_check = true;
        }

        // 3. Execute precise check
        if (run_check)
        {
            // Drain worker queue completely so all contigs reach segment buffers
            while (!pq_contigs_desc->IsEmpty())
                std::this_thread::sleep_for(std::chrono::milliseconds(10));

            naive_size = GetCurrentArchiveSizeEstimate();
            uint64_t true_size = GetSimulatedArchiveSize(no_threads);

            // Final Stop Condition (95% reached)
            if (true_size >= stop_threshold)
            {
                if (verbosity > 0)
                    cerr << "Stop threshold reached (" << true_size << " bytes). Finalizing part...\n";
                break;
            }

            // Adaptive Interval Calculation
            if (last_true_size > 0 && true_size > last_true_size && genomes_since_last_check > 0)
            {
                uint64_t bytes_added = true_size - last_true_size;
                uint64_t avg_bytes_per_genome = bytes_added / genomes_since_last_check;

                if (avg_bytes_per_genome > 0 && true_size < stop_threshold)
                {
                    uint64_t bytes_remaining = stop_threshold - true_size;
                    size_t estimated_genomes_left = bytes_remaining / avg_bytes_per_genome;

                    // Set next check halfway to target
                    strict_check_interval = estimated_genomes_left / 2;
                    size_t max_interval = is_strict ? 10 : 100;

                    if (strict_check_interval < 2) strict_check_interval = 2;
                    if (strict_check_interval > max_interval) strict_check_interval = max_interval;
                }
            }

            // Activate strict mode once 75% is crossed
            if (true_size >= strict_threshold && !strict_mode)
                strict_mode = true;

            buffer_offset = (true_size > naive_size) ? (true_size - naive_size) : 0;
            last_true_size = true_size;
            genomes_since_last_check = 0;
        }

        // 4. Absolute Emergency Brake
        if (naive_size >= target_part_size)
            break;
    }

    // Tear down threads and finalize worker queue
    // ...
    return samples_consumed;
}
```

---

## 4. Control Theory: The Adaptive Runway Mechanism

```
0%                                  75%                  95%      100%
|------------------------------------|--------------------|--------|
           PASSIVE PHASE                   STRICT PHASE     CLOSE() TARGET
        (naive + buffer_offset)           (Adaptive Trial) (Metadata)
```

1. **Passive Phase (0% to 75%)**:
   - Zero simulation overhead. Workers run at peak multi-core speed.
   - Initial offset seed ($40\%$) triggers the first check safely around ~35-40% of physical capacity to calibrate the true compression ratio.
2. **Strict Phase (75% to 95%)**:
   - Switched to active checkpoints.
   - Uses empirical run rate:
     $$\text{Rate} = \frac{\Delta \text{TrueSize}}{\Delta \text{Genomes}}$$
     $$\text{Runway} = \frac{\text{StopThreshold} - \text{TrueSize}}{\text{Rate}}$$
     $$\text{NextInterval} = \text{clamp}\left(\frac{\text{Runway}}{2}, 2, \text{MaxInterval}\right)$$
   - Halving the runway ensures the compressor will never overshoot even if the incoming genome batch is twice as large or less redundant than preceding genomes.
3. **The 95% Stop Threshold**:
   - Why stop at 95% instead of 100%?
   - During `Close()`, AGC serializes the archive metadata: $k$-mer splitters, contig index registries, sample names, and footer structures.
   - Reserving 5% guaranteed runway absorbs this terminal metadata payload without exceeding the user's quota.

---

## 5. Step-by-Step Task Checklist

- [ ] **Step 5.1:** Declare `AddSampleSplit` in `src/core/agc_compressor.h`.
- [ ] **Step 5.2:** Implement worker thread startup and priority queue initialization.
- [ ] **Step 5.3:** Add periodic synchronization barrier every 25 genomes (`pq_contigs_desc->IsEmpty()`).
- [ ] **Step 5.4:** Implement two-stage threshold detection (75% strict threshold, 95% stop threshold).
- [ ] **Step 5.5:** Add queue drain loop before running `GetSimulatedArchiveSize`.
- [ ] **Step 5.6:** Implement adaptive runway interval calculation clamped to `[2, max_interval]`.
- [ ] **Step 5.7:** Add emergency brake when `naive_size >= target_part_size`.
- [ ] **Step 5.8:** Return exact count of `samples_consumed`.

---

## 6. Acceptance Criteria

1. Ingestion cleanly halts when true simulated size reaches 95% of `target_part_size`.
2. Overshooting beyond `target_part_size` on final on-disk archive after `Close()` is prevented across benchmark datasets.
3. If an input collection contains only 1 genome that is larger than the target, `AddSampleSplit` consumes that genome and finishes without an infinite loop.
4. When `-x` (strict mode) is enabled, checkpoint intervals are strictly bounded to $\le 10$ genomes.
