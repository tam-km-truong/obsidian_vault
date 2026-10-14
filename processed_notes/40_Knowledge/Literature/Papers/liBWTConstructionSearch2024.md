---
category: literature
citekey: "liBWTConstructionSearch2024"
title: "BWT Construction and Search at the Terabase Scale"
aliases:
  - "BWT Construction and Search at the Terabase Scale"
  - "Li (2024)"
  - "@liBWTConstructionSearch2024"
authors:
  - "Li, Heng"
year: 2024
journal: "Bioinformatics"
doi: ""
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# BWT Construction and Search at the Terabase Scale

- **Authors:** Li
- **Year:** 2024
- **Journal / Venue:** *Bioinformatics*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@liBWTConstructionSearch2024)

## Abstract
> MOTIVATION: Burrows-Wheeler Transform (BWT) is a common component in full-text indices. Initially developed for data compression, it is particularly powerful for encoding redundant sequences such as pangenome data. However, BWT construction is resource intensive and hard to be parallelized, and many methods for querying large full-text indices only report exact matches or their simple extensions. These limitations have hampered the biological applications of full-text indices. RESULTS: We developed ropebwt3 for efficient BWT construction and query. Ropebwt3 indexed 320 assembled human genomes in 65 h and indexed 7.3 terabases of commonly studied bacterial assemblies in 26 days. This was achieved using up to 170 gigabytes of memory at the peak without working disk space. Ropebwt3 can find maximal exact matches and inexact alignments under affine-gap penalties, and can retrieve similar local haplotypes matching a query sequence. It demonstrates the feasibility of full-text indexing at the terabase scale. AVAILABILITY AND IMPLEMENTATION: https://github.com/lh3/ropebwt3.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Burrows-Wheeler Transform (BWT) in Genomics]]

## BibTeX Citation
```bibtex
@article{liBWTConstructionSearch2024,
  title = {BWT Construction and Search at the Terabase Scale},
  author = {Li, Heng},
  year = {2024},
  journal = {Bioinformatics},
  doi = {}
}
```
