---
category: literature
citekey: "salsonCREMSACompressedIndexing2025"
title: "CREMSA: Compressed Indexing of (Ultra) Large Multiple Sequence Alignments"
aliases:
  - "CREMSA: Compressed Indexing of (Ultra) Large Multiple Sequence Alignments"
  - "Salson et al. (2025)"
  - "@salsonCREMSACompressedIndexing2025"
authors:
  - "Salson, Mika\"el"
  - "Boddaert, Arthur"
  - "Gueye, Awa Bousso"
  - "Bulteau, Laurent"
  - "Hernandez-Courbevoie, Yohan"
  - "Marchet, Camille"
  - "Pan, Nan"
  - "Will, Sebastian"
  - "Ponty, Yann"
year: 2025
journal: "Bioinformatics"
doi: ""
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# CREMSA: Compressed Indexing of (Ultra) Large Multiple Sequence Alignments

- **Authors:** Salson et al.
- **Year:** 2025
- **Journal / Venue:** *Bioinformatics*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@salsonCREMSACompressedIndexing2025)

## Abstract
> MOTIVATION: Recent viral outbreaks motivate the systematic collection of pathogenic genomes in order to accelerate their study and monitor the apparition/spread of variants. Due to their limited length and temporal proximity of their sequencing, viral genomes are usually organized, and analyzed as oversized Multiple Sequence Alignments (MSAs). Such MSAs are largely ungapped, and mostly homogeneous on a column-wise level but not at a sequential level due to local variations, hindering the performances of sequential compression algorithms. RESULTS: In order to enable an efficient handling of MSAs, including subsequent statistical analyses, we introduce CREMSA (Column-wise Run-length Encoding for MSAs), a new index that builds on sparse bitvector representations to compress an existing or streamed MSA, all the while allowing for an expressive set of accelerated requests to query the alignment without prior decompression. Using CREMSA, a 65 GB MSA consisting of 1.9M SARS-CoV 2 genomes could be compressed into 22 MB using less than half a gigabyte of main memory, while executing access requests in the order of 100 ns. Such a speed up enables a comprehensive analysis of covariation over this very large MSA. We further assess the impact of the sequence ordering on the compressibility of MSAs and propose a resorting strategy that, despite the proven NP-hardness of an optimal sort, induces greatly increased compression ratios at a marginal computational cost. AVAILABILITY AND IMPLEMENTATION: CREMSA is freely accessible at https://gitlab.univ-lille.fr/cremsa/cremsa. The Snakemake workflow for the benchmarks is available at: https://gitlab.univ-lille.fr/cremsa/bench. The data used in the paper is on Zenodo at https://zenodo.org/records/14698859 and https://zenodo.org/records/15100011.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@article{salsonCREMSACompressedIndexing2025,
  title = {CREMSA: Compressed Indexing of (Ultra) Large Multiple Sequence Alignments},
  author = {Salson, Mika\"el and Boddaert, Arthur and Gueye, Awa Bousso and Bulteau, Laurent and Hernandez-Courbevoie, Yohan and Marchet, Camille and Pan, Nan and Will, Sebastian and Ponty, Yann},
  year = {2025},
  journal = {Bioinformatics},
  doi = {}
}
```
