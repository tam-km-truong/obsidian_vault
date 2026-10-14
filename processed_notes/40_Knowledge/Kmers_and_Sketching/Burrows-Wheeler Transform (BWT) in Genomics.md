---
category: knowledge
tags:
  - bwt
  - algorithms
  - compression
  - indexing
source_raw: "[[Burrow Wheeler Transform]]"
status: processed
---

# Burrows-Wheeler Transform (BWT) in Genomics

## Algorithm Steps
1. Append an end-of-string sentinel symbol `$` (lexicographically smallest).
2. Generate all cyclical rotations of the string.
3. Sort rotations lexicographically.
4. Extract the last column (the BWT output).

## Utility in Genomics
- **Reversibility:** Fully invertible using the LF-mapping property.
- **Clustering:** Groups identical characters together, dramatically improving run-length encoding and compression.
- **FM-Index:** Basis of sequence aligners (BWA, Bowtie) for sub-linear pattern matching.

## Related Notes
- [[Genomic Data Compression Survey (zstd, AGC, MBGC)]]
- [[Jellyfish - Lock-Free K-mer Counting]]
