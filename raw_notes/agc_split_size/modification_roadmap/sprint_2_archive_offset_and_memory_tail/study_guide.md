# Sprint 2 Study Guide: Stream Offsets & The Asynchronous Memory Tail

In this sprint, you examine why simple I/O metrics fail in complex multi-threaded compression pipelines.

---

## 1. Key Concepts to Understand

### A. Thread-Safe I/O Querying in `CArchive`
In multi-threaded C++ applications, multiple worker threads may append compressed chunks simultaneously to an archive stream.
```cpp
size_t CArchive::GetCurrentOffset()
{
    lock_guard<mutex> lck(mtx);
    if (input_mode) return 0;
    flush_out_buffers();
    return f_offset;
}
```
- `std::lock_guard<std::mutex>`: Acquires the mutex on creation and releases it automatically upon exiting the scope (RAII), preventing data races with worker threads calling `AddPartBuffered`.
- `flush_out_buffers()`: Writes any partially filled user-space output buffers to the OS file descriptor so `f_offset` accurately reflects the file pointer.

### B. The Asynchronous Memory Tail Anatomy
Why does committed disk size diverge from true archive size?
Consider an archive with $S = 5,000$ active segments and `contigs_in_pack` $B = 500$:
- Each segment $i$ maintains in RAM:
  - `v_lzp`: Vector of LZP-matched delta contigs
  - `v_raw`: Vector of literal contigs
- If segments receive contigs according to a uniform distribution, the average number of uncompressed contigs sitting in segment $i$ at any random step is:
  $$\mathbb{E}[N_i] \approx \frac{B}{2} = 250 \text{ contigs}$$
- Across 5,000 segments, the total number of uncompressed contigs hidden in RAM is:
  $$5,000 \times 250 = 1,250,000 \text{ contigs!}$$
- At an average contig length of 1,000 bp, this represents over **1.25 Gigabytes** of sequence data entirely invisible to `CArchive::GetCurrentOffset()`.

### C. Analysis of Attempted Naive Solutions
Why simple heuristics failed during AGC development:
1. **Summing Raw Uncompressed RAM + Disk Offset**:
   - `Uncompressed RAM` $\approx 1.25\text{ GB}$.
   - Adding raw uncompressed bytes directly to compressed disk bytes overestimates total size by 5x-10x because genomic sequence compresses significantly under ZSTD.
2. **Dividing by a Static Heuristic Ratio (e.g. 3.0x)**:
   - Genomes from identical strains have compression ratios of 20x to 50x.
   - Genomes from divergent species or highly mutated plasmids have ratios of 1.5x to 2.5x.
   - A static divider fails catastrophically on heterogeneous datasets.
3. **Modulo-500 Sample Checks**:
   - Genomes do not map 1:1 to segments; splitters distribute contigs across thousands of segments. Processing 500 samples does NOT mean segments are empty!

---

## 2. Recommended Readings & Documentation

1. **AGC Publication (Bioinformatics 2023)**:
   *AGC: Compact representation of assembled genomes with fast queries and updates.*
   [https://doi.org/10.1093/bioinformatics/btad097](https://doi.org/10.1093/bioinformatics/btad097)
2. **cppreference: `std::lock_guard`**:
   [https://en.cppreference.com/w/cpp/thread/lock_guard](https://en.cppreference.com/w/cpp/thread/lock_guard)
3. **Bufferbloat & Asynchronous Pipeline Queuing Theory**:
   Understanding how in-flight queues mask pipeline volume.

---

## 3. Common Gotchas & Personal Notes

1. **`flush_out_buffers()` vs `fsync()`**:
   `flush_out_buffers()` drains AGC's internal memory buffers into the C library / OS page cache. It does NOT invoke expensive disk hardware synchronization (`fsync()`), keeping query latency minimal.
2. **Deadlocks**:
   Never call `GetCurrentOffset()` while holding an inner segment mutex, as `CArchive` methods acquire `mtx`. Always maintain a strict lock hierarchy.

---

## 4. 10-Minute Mini Practice Exercise

Simulate the unwritten memory tail problem with a toy bucket accumulator:

```cpp
#include <iostream>
#include <vector>
#include <numeric>

struct ToySegment {
    std::vector<int> buffer;
    size_t flushed_bytes = 0;
    
    void add(int item) {
        buffer.push_back(item);
        if (buffer.size() >= 10) { // Batch size 10
            flushed_bytes += buffer.size() * sizeof(int);
            buffer.clear();
        }
    }
};

int main() {
    std::vector<ToySegment> segments(100);
    for (int i = 0; i < 450; ++i) {
        segments[i % 100].add(i);
    }
    
    size_t committed = 0, unwritten_items = 0;
    for (const auto& seg : segments) {
        committed += seg.flushed_bytes;
        unwritten_items += seg.buffer.size();
    }
    
    std::cout << "Committed disk bytes: " << committed << "\n";
    std::cout << "Unwritten items in RAM: " << unwritten_items << " items\n";
    return 0;
}
```
Notice how `unwritten_items` holds almost the entire dataset when items are distributed across many segments!
