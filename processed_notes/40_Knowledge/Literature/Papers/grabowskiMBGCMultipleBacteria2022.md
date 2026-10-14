---
category: literature
citekey: "grabowskiMBGCMultipleBacteria2022"
title: "MBGC: Multiple Bacteria Genome Compressor"
aliases:
  - "MBGC: Multiple Bacteria Genome Compressor"
  - "Grabowski & Kowalski (2022)"
  - "@grabowskiMBGCMultipleBacteria2022"
  - "@grabowskiMBGCMultipleBacteria2022a"
authors:
  - "Grabowski, Szymon"
  - "Kowalski, Tomasz M"
year: 2022
journal: "GigaScience"
doi: "10.1093/gigascience/giab099"
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# MBGC: Multiple Bacteria Genome Compressor

- **Authors:** Grabowski & Kowalski
- **Year:** 2022
- **Journal / Venue:** *GigaScience*
- **Links:** [DOI](https://doi.org/10.1093/gigascience/giab099) | [Open in Zotero Desktop](zotero://select/items/@grabowskiMBGCMultipleBacteria2022)

## Abstract
> Genomes within the same species reveal large similarity, exploited by specialized multiple genome compressors. The existing algorithms and tools are however targeted at large, e.g., mammalian, genomes, and their performance on bacteria strains is rather moderate.In this work, we propose MBGC, a specialized genome compressor making use of specific redundancy of bacterial genomes. Its characteristic features are finding both direct and reverse-complemented LZ-matches, as well as a careful management of a reference buffer in a multi-threaded implementation. Our tool is not only compression efficient but also fast. On a collection of 168,311 bacterial genomes, totalling 587 GB, we achieve a compression ratio of approximately a factor of 1,265 and compression (respectively decompression) speed of $\sim$1,580 MB/s (respectively 780\,MB/s) using 8 hardware threads, on a computer with a 14-core/28-thread CPU and a fast SSD, being almost 3~times more succinct and &gt;6~times faster in the compression than the next best competitor.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[MBGC - Multiple Bacterial Genome Compressor]]

## BibTeX Citation
```bibtex
@article{grabowskiMBGCMultipleBacteria2022,
  title = {MBGC: Multiple Bacteria Genome Compressor},
  author = {Grabowski, Szymon and Kowalski, Tomasz M},
  year = {2022},
  journal = {GigaScience},
  doi = {10.1093/gigascience/giab099}
}
```
