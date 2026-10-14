---
category: knowledge
tags:
  - bigsi
  - bloom-filter
  - search
  - index
source_raw: "[[BIGSI Ultra-fast search of all deposited bacterial and viral genomic data]]"
status: processed
---

# BIGSI: Ultra-Fast Search Across All Deposited Bacterial & Viral Data

## Background & Problem
Existing search tools like BLAST cannot scale to querying arbitrary sequences against millions of raw sequencing datasets.

---

## Core Architecture: Bloofi / Interleaved Bloom Filters
- **Bloom Filters:** Probabilistic data structure testing set membership with zero false negatives and tunable false positives.
- **Interleaved Rows:** Matrix representation where column $j$ is the Bloom filter of dataset $j$, and row $i$ groups the $i$-th bit of all datasets together for SIMD word-level querying.
- Allows testing whether a query sequence (e.g. an antimicrobial resistance gene) exists across 450,000 datasets in seconds.

## Related Notes
- [[Raptor - Hierarchical Interleaved Bloom Filters]] – Next-generation hierarchical extension
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]] – Dataset indexed by BIGSI
