---
category: knowledge
tags:
  - jellyfish
  - kmer
  - hash-table
  - algorithms
source_raw: "[[JellyFish paper]]"
status: processed
---

# Jellyfish: Lock-Free Multithreaded K-mer Counting

## In a Nutshell
**Jellyfish** is an ultrafast, memory-efficient k-mer counter based on a **lock-free, multithreaded hash table** utilizing open addressing with quadratic probing and compare-and-swap (CAS) CPU primitives.

---

## Architectural Core
1. **Lock-Free Concurrency:** Uses hardware atomic `compare-and-swap` (CAS) so worker threads update k-mer frequencies concurrently without mutex locks.
2. **Bit-Packed Encoding:** Dynamically encodes k-mers and counts to avoid wasting memory on fixed-width 64-bit integer fields.
3. **External Memory Sorting:** When memory limits are reached, slices are flushed to disk and merged via a min-heap.

---

## CLI Invocations
```bash
# Count 31-mers using 16 threads and 10GB hash table
jellyfish count -m 31 -s 10G -t 16 -C -o output.jf input.fasta

# Export histogram
jellyfish histo output.jf > kmer_hist.txt
```

## Troubleshooting Notes
- *Issue:* Compilation failure from source on modern macOS/GCC.
  - *Fix:* Use precompiled conda binary: `conda install -c bioconda jellyfish`.

## Related Notes
- [[Mash & MinHash Sketching]] – Approximate sketch counting
- [[Burrows-Wheeler Transform (BWT) in Genomics]] – Alternative indexing
