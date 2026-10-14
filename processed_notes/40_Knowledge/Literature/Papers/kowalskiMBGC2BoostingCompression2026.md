---
category: literature
citekey: "kowalskiMBGC2BoostingCompression2026"
title: "MBGC2: Boosting Compression via Efficient Encoding of Approximate Matches in Genome Collections"
aliases:
  - "MBGC2: Boosting Compression via Efficient Encoding of Approximate Matches in Genome Collections"
  - "Kowalski (2026)"
  - "@kowalskiMBGC2BoostingCompression2026"
authors:
  - "Kowalski, Tomasz M"
year: 2026
journal: "Gigascience"
doi: ""
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# MBGC2: Boosting Compression via Efficient Encoding of Approximate Matches in Genome Collections

- **Authors:** Kowalski
- **Year:** 2026
- **Journal / Venue:** *Gigascience*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@kowalskiMBGC2BoostingCompression2026)

## Abstract
> BACKGROUND: FASTA is the primary format for representing DNA, RNA, and protein sequences. While progress has been made, specialized FASTA collection compressors still struggle with practical limitations and inconsistent performance across different datasets, hindering effective storage and transfer of large genomic datasets. RESULTS: We present an enhanced version of the Multiple Bacteria Genome Compressor (MBGC), a high-throughput, in-memory algorithm for compressing genome collections. It relies on information about maximum exact matches in the compressed set to identify possibly long approximate matches. It encodes them even when they partially overlap, boosting the compression ratio by an average of 14% across bacterial datasets, while the reengineered multithreaded decoding speeds up decompression compared to its predecessor by around 40%. The compression ratio improvement is even more pronounced on other collections, reaching 18% for Homo sapiens and up to 55% for Saccharomyces paradoxus. MBGC2 performs consistently across diverse datasets and introduces practical features to ease data management, such as archive appending, repacking, fast content listing, and flexible decompression options. Benchmark tests covering nucleotide-based bacterial, viral, and human genome collections show that MBGC2 combines compression efficiency and processing speed. The tool supports working with single genomes or amino acid collections but does not guarantee such high performance in these cases. CONCLUSIONS: MBGC2 addresses critical limitations in genome collection compression by delivering reliable performance, improved compression ratios, and enhanced usability features. The consistent efficiency across diverse genomic datasets makes it a versatile tool for managing the growing volume of genomic data in research and clinical settings. The balance between compression ratio and speed positions MBGC2 as a practical solution for the storage and transfer of large genomic collections.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]]
- [[MBGC - Multiple Bacterial Genome Compressor]]

## BibTeX Citation
```bibtex
@article{kowalskiMBGC2BoostingCompression2026,
  title = {MBGC2: Boosting Compression via Efficient Encoding of Approximate Matches in Genome Collections},
  author = {Kowalski, Tomasz M},
  year = {2026},
  journal = {Gigascience},
  doi = {}
}
```
