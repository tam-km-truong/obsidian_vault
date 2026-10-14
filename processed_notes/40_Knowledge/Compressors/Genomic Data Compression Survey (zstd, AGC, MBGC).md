---
category: knowledge
tags:
  - compression
  - zstd
  - agc
  - mbgc
  - survey
source_raw: "[[compressor]]"
status: processed
---

# Genomic Data Compression Survey: Dictionary & Specialized Compressors

## 1. General-Purpose vs Domain-Specific Compression
- **General-Purpose (gzip, zstd, xz):** Work on sliding-window LZ77 / entropy coding. They have small window sizes (e.g., gzip has 32 KB window; zstd defaults to a few MBs). Consequently, they cannot exploit long-range homology across different genomes separated by megabases.
- **Pangenomic Compressors (AGC, MBGC):** Construct global k-mer dictionaries and multi-sequence reference alignments across millions of basepairs.

---

## 2. Sliding Window & Memory Dynamics
- **zstd window size:** Can be enlarged up to `--long=31` (2 GB window) to capture cross-genome repetitions, but requires huge RAM on decompression.
- **Specialized Dictionary Builders:** Create an explicit reference skeleton, encoding target genomes purely as edit scripts (substitutions, insertions, deletions).

---

## 3. Compression Ratio Formula
$$
\text{Compression Ratio} = \frac{\text{Uncompressed Total Bytes}}{\text{Compressed Archive Bytes}}
$$

## Related Notes
- [[AGC - Assembled Genomes Compressor]]
- [[MBGC - Multiple Bacterial Genome Compressor]]
- [[Mathematical Formulation - Order-Preserving Batching]]
