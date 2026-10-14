---
category: literature
citekey: "girardOReOOptimizingRead2025"
title: "OReO: Optimizing Read Order for Practical Compression"
aliases:
  - "OReO: Optimizing Read Order for Practical Compression"
  - "Girard et al. (2025)"
  - "@girardOReOOptimizingRead2025"
  - "@girardOReOOptimizingRead2025a"
authors:
  - "Girard, Mathilde"
  - "Vandamme, L\'ea"
  - "Cazaux, Bastien"
  - "Limasset, Antoine"
year: 2025
journal: "Bioinformatics Advances"
doi: "10.1093/bioadv/vbaf128"
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# OReO: Optimizing Read Order for Practical Compression

- **Authors:** Girard et al.
- **Year:** 2025
- **Journal / Venue:** *Bioinformatics Advances*
- **Links:** [DOI](https://doi.org/10.1093/bioadv/vbaf128) | [Open in Zotero Desktop](zotero://select/items/@girardOReOOptimizingRead2025)

## Abstract
> Recent advances in high-throughput and third-generation sequencing technologies have created significant challenges in storing and managing the rapidly growing volume of read datasets. Although more than 50 specialized compression tools have been developed, employing methods such as reference-based approaches, customized generic compressors, and read reordering, many users still rely on common generic compressors (e.g., gzip, zstd, xz) for convenience, portability, and reliability, despite their low compression ratios. Here, we introduce OReO, a simple read-reordering framework that achieves high compression performance without requiring specialized software for decompression. By grouping overlapping reads together before applying generic compressors, OReO exploits inherent redundancies in sequencing data and achieves compression ratios on par with state-of-the-art tools. Moreover, because it relies only on standard decompressors, OReO avoids the need for dedicated installations and maintenance, removing a key barrier to practical adoption. We evaluated OReO on both ONT and HiFi genomic and metagenomic datasets of varying sizes and complexities. Our results demonstrate that OReO provides substantial compression gains with comparable resource usage and outperforms dedicated methods in decompression speed. We propose that future compression strategies should focus on reordering as a means to let generic compression tools fully exploit data redundancy, offering an efficient, sustainable, and user-friendly solution to the growing challenges of sequencing data storage. The OReO code is open source and available at github.com/girunivlille/oreo.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@article{girardOReOOptimizingRead2025,
  title = {OReO: Optimizing Read Order for Practical Compression},
  author = {Girard, Mathilde and Vandamme, L\'ea and Cazaux, Bastien and Limasset, Antoine},
  year = {2025},
  journal = {Bioinformatics Advances},
  doi = {10.1093/bioadv/vbaf128}
}
```
