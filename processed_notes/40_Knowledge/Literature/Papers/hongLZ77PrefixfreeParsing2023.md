---
category: literature
citekey: "hongLZ77PrefixfreeParsing2023"
title: "LZ77 via Prefix-Free Parsing"
aliases:
  - "LZ77 via Prefix-Free Parsing"
  - "Hong et al. (2023)"
  - "@hongLZ77PrefixfreeParsing2023"
authors:
  - "Hong, Aaron"
  - "Rossi, Massimiliano"
  - "Boucher, Christina"
year: 2023
journal: "2023 Proceedings of the Symposium on Algorithm Engineering and Experiments (ALENEX)"
doi: ""
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# LZ77 via Prefix-Free Parsing

- **Authors:** Hong et al.
- **Year:** 2023
- **Journal / Venue:** *2023 Proceedings of the Symposium on Algorithm Engineering and Experiments (ALENEX)*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@hongLZ77PrefixfreeParsing2023)

## Abstract
> In this paper, we present an algorithm for constructing the Lempel-Ziv 77 (LZ77) factorization using prefix-free parsing, an algorithm that was first developed as preprocessing algorithm for constructing the Burrows-Wheeler transform and the suffix array for input text. It was then demonstrated that the output of prefix-free parsing can be an effective data structure that emulates a compressed suffix tree (CST). PFP-LZ77 marries this data structure with the algorithm proposed by Karkk\"ainen et al. [CPM 2013]. In particular, we implemented a modification of the primitives used to support CST operations to enable previous smaller value and next smaller value queries on the suffix array of the text. This allow PFP-LZ77 to exploit the repetitiveness of the text, while building the LZ77 parse. We show that PFP-LZ77, SE-KKP, and ReLZ were the only methods capable of scaling to large datasets (e.g., 1024 copies of chromosome 19). And although SE-KKP and ReLZ performed well, SE-KKP was between 2.5 and 5 times slower, and used between 3 and 11 times more memory than PFP-LZ77 for reasonably large datasets (i.e., more than 16 copies of chromosome 19), and ReLZ only generates an LZ77 approximation. Our implementation is available at https://github.com/AaronHong1024/PFP_LZ77.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]]

## BibTeX Citation
```bibtex
@incollection{hongLZ77PrefixfreeParsing2023,
  title = {LZ77 via Prefix-Free Parsing},
  author = {Hong, Aaron and Rossi, Massimiliano and Boucher, Christina},
  year = {2023},
  journal = {2023 Proceedings of the Symposium on Algorithm Engineering and Experiments (ALENEX)},
  doi = {}
}
```
