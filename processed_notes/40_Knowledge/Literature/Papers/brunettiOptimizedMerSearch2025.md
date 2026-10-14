---
category: literature
citekey: "brunettiOptimizedMerSearch2025"
title: "Optimized k -Mer Search across Millions of Bacterial Genomes on Laptops"
aliases:
  - "Optimized k -Mer Search across Millions of Bacterial Genomes on Laptops"
  - "Brunetti & B\v rinda (2025)"
  - "@brunettiOptimizedMerSearch2025"
authors:
  - "Brunetti, Francesca"
  - "B\v rinda, Karel"
year: 2025
journal: "bioRxiv"
doi: ""
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# Optimized k -Mer Search across Millions of Bacterial Genomes on Laptops

- **Authors:** Brunetti & B\v rinda
- **Year:** 2025
- **Journal / Venue:** *bioRxiv*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@brunettiOptimizedMerSearch2025)

## Abstract
> ABSTRACT Comprehensive bacterial collections have reached millions of genomes, opening new opportunities for point-of-care diagnostics and epidemiological surveillance. However, local real-time search over such collections on commodity hardware remains difficult. Currently, only LexicMap and Phylign enable local search and alignment at such a scale; among them, only Phylign is designed to run on laptops, via a subindex approach informed by phylogenetic compression. However, Phylign's performance deteriorates on long and divergent queries because it uses COBS as a k -mer-based prefilter before alignment with Minimap2. Meanwhile, recent k -mer indexes such as Fulgor and Themisto have emerged, but there is no practical methodology for selecting, combining, and parameterizing them for phylogenetically partitioned million-genome search under constraints. Here, we develop an end-to-end methodology for k -mer matching in phylogenetically compressed bacterial collections. We formalize a matching strategy defined by matching mode, query type, and reference characteristics, and use this to shortlist candidate indexes and benchmark them under space--time trade-offs. As a case study, we address plasmid search over AllTheBacteria, compare multiple index types, and identify configurations optimizing the Pareto frontier of space and speed. Guided by these results, we implement a phylogenetically compressed variant of Fulgor, integrate it into Phylign, and obtain Phylign-Fulgor, a laptop-ready pipeline for million-genome search. On the 661k collection, Phylign-Fulgor makes the prefiltering step $\sim$4 faster than Phylign-COBS at the cost of a 1.2 larger index. On AllTheBacteria, its k -mer filter is 20\texttimes --300 faster in real time than LexicMap's alignment-based search and uses $\sim$20 smaller disk space. The full Phylign-Fulgor workflow including Minimap2 alignments is slower than LexicMap for a single plasmid but competitive or faster for batched plasmid queries. Phylign-Fulgor has comparable matching sensitivity to LexicMap, is less sensitive at the alignment level, but always stays within a laptop RAM budget ($\sim$5\texttimes --20 lower memory than LexicMap).

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]]

## BibTeX Citation
```bibtex
@article{brunettiOptimizedMerSearch2025,
  title = {Optimized k -Mer Search across Millions of Bacterial Genomes on Laptops},
  author = {Brunetti, Francesca and B\v rinda, Karel},
  year = {2025},
  journal = {bioRxiv},
  doi = {}
}
```
