---
category: presentations
conference: DSB (Data Structures in Bioinformatics)
year: 2025
tags:
  - bioinformatics
  - pangenomics
  - compression
  - phylogenetic-trees
  - presentation
source_raw: "[[DSB talk transcript + question]]"
status: processed
---

# DSB 2025: Phylogenetic Ordering and Batching of Million-Genome Collections

## Executive Summary
This presentation introduces an order-preserving, two-stage compression and batching pipeline designed to scale bacterial genomic archives (such as **AllTheBacteria** with 1.9M genomes and **GTDB**). By combining **phylogenetic tree preorder traversal** with **k-mer sketch-based bin packing**, the method maximizes compression ratios while maintaining fast, predictable random access times without requiring global multi-sequence alignment.

---

## Presentation Structure & Core Narrative

### 1. The Million-Genome Storage Problem
- **Context:** Public databases are growing exponentially (NCBI, AllTheBacteria, 661k collection).
- **The Trade-Off:** 
  - Monolithic compression archives (e.g. compressing 100k genomes in a single archive with [[AGC - Assembled Genomes Compressor]] or [[MBGC]]) yield high compression ratios but suffer from slow random access and huge decompression memory requirements.
  - Independent compression (e.g. `gzip` per genome) enables fast retrieval but produces terrible compression ratios due to unexploited cross-genome redundancy.
- **Objective:** Partition $N$ genomes into batches $B_1, B_2, \dots, B_m$ such that total compressed size $\sum S(B_j)$ is minimized while keeping each batch small enough for sub-second random access.

### 2. Why Phylogenetic Ordering?
- Genomic sequences that share a recent common ancestor exhibit high sequence homology and shared k-mer sets.
- By ordering genomes according to a **depth-first preorder traversal** of a phylogenetic tree (constructed via fast distance methods like [[Attotree]] and [[Mash]]), syntenic and identical blocks cluster consecutively along the traversal.
- Order-preserving batching groups evolutionary neighbors together, dramatically reducing the dictionary size required by compressors like AGC and MBGC.

### 3. Two-Stage Pipeline Architecture
1. **Phylogenetic Skeleton:** Construct an approximate phylogenetic tree across the collection using fast k-mer sketches ([[dashing2 - HyperLogLog Genome Sketching]], [[Attotree - Fast Tree Construction & Troubleshooting]]).
2. **Preorder Linearization:** Flatten the tree into an evolutionary 1D sequence of accessions.
3. **Capacity-Constrained Batching (Bin Packing):** Slice the linearized list into batches satisfying maximum uncompressed size and k-mer count limits.

---

## Audience Q&A & Discussion

### Q1: How sensitive is the compression ratio to phylogenetic tree quality?
> **Answer:** Even an approximate tree (e.g. FastME or QuickTree on MinHash distances) captures >90% of the compression gains compared to an exact maximum-likelihood tree, while computing in minutes rather than days. The key benefit comes from separating distant clades, not from resolving micro-branches within clonal isolates.

### Q2: What compressor was used for benchmarking?
> **Answer:** Primary benchmarks used [[AGC - Assembled Genomes Compressor]] and [[MBGC]]. AGC with preorder batching achieved significant space savings over default taxonomic sorting.

### Q3: How does random access scale?
> **Answer:** Because each batch is capped (e.g. 500 MB or 1,000 genomes), pulling a single genome requires decompressing at most one isolated batch rather than scanning an entire species repository.

---

## Related Presentations & Notes
- [[SeqBIM 2025 - Large-Scale Bacterial Genome Storage]] – Follow-up presentation at SeqBIM
- [[Mathematical Formulation - Order-Preserving Batching]] – Formal optimization equations
- [[miniphy2 - Workflow Specifications & CLI]] – Tool implementing this pipeline
- [[Allthebacteria]] – Benchmark dataset evaluated in this talk
- [[AGC - Assembled Genomes Compressor]] – Underlying archive compressor
