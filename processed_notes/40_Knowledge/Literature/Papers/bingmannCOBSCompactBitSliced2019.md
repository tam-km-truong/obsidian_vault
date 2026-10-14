---
category: literature
citekey: "bingmannCOBSCompactBitSliced2019"
title: "COBS: A Compact Bit-Sliced Signature Index"
aliases:
  - "COBS: A Compact Bit-Sliced Signature Index"
  - "Bingmann et al. (2019)"
  - "@bingmannCOBSCompactBitSliced2019"
  - "@bingmannCOBSCompactBitSliced2019a"
authors:
  - "Bingmann, Timo"
  - "Bradley, Phelim"
  - "Gauger, Florian"
  - "Iqbal, Zamin"
year: 2019
journal: "String Processing and Information Retrieval"
doi: "10.1007/978-3-030-32686-9_21"
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# COBS: A Compact Bit-Sliced Signature Index

- **Authors:** Bingmann et al.
- **Year:** 2019
- **Journal / Venue:** *String Processing and Information Retrieval*
- **Links:** [DOI](https://doi.org/10.1007/978-3-030-32686-9_21) | [Open in Zotero Desktop](zotero://select/items/@bingmannCOBSCompactBitSliced2019)

## Abstract
> We present COBS, a COmpact Bit-sliced Signature index, which is a cross-over between an inverted index and Bloom filters. Our target application is to index k-mers of DNA samples or q-grams from text documents and process approximate pattern matching queries on the corpus with a user-chosen coverage threshold. Query results may contain a number of false positives which decreases exponentially with the query length. We compare COBS to seven other index software packages on 100~000 microbial DNA samples. COBS' compact but simple data structure outperforms the other indexes in construction time and query performance with Mantis by Pandey et al. in second place. However, unlike Mantis and other previous work, COBS does not need the complete index in RAM and is thus designed to scale to larger document~sets.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@inproceedings{bingmannCOBSCompactBitSliced2019,
  title = {COBS: A Compact Bit-Sliced Signature Index},
  author = {Bingmann, Timo and Bradley, Phelim and Gauger, Florian and Iqbal, Zamin},
  year = {2019},
  journal = {String Processing and Information Retrieval},
  doi = {10.1007/978-3-030-32686-9_21}
}
```
