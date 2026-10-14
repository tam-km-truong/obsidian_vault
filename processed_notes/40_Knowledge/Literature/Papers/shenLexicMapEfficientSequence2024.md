---
category: literature
citekey: "shenLexicMapEfficientSequence2024"
title: "LexicMap: Efficient Sequence Alignment against Millions of Prokaryotic Genomes"
aliases:
  - "LexicMap: Efficient Sequence Alignment against Millions of Prokaryotic Genomes"
  - "Shen & Iqbal (2024)"
  - "@shenLexicMapEfficientSequence2024"
authors:
  - "Shen, Wei"
  - "Iqbal, Zamin"
year: 2024
journal: "bioRxiv"
doi: ""
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# LexicMap: Efficient Sequence Alignment against Millions of Prokaryotic Genomes

- **Authors:** Shen & Iqbal
- **Year:** 2024
- **Journal / Venue:** *bioRxiv*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@shenLexicMapEfficientSequence2024)

## Abstract
> AbstractAlignment against a database of genomes is a fundamental operation in bioinformatics, popularized by BLAST. However, the rate at which microbial genomes are sequenced has continued to increase, and there are now datasets in the millions, far beyond the abilities of existing alignment tools. We introduce LexicMap, a nucleotide sequence alignment tool for efficiently querying moderate length sequences ($>$ 500 bp) such as a gene, plasmid or long read against up to millions of prokaryotic genomes. A key innovation is to construct a small set of probek-mers (e.g. n = 40,000) which ``window-cover'' the entire database to be indexed, in the sense that every 500 bp window of every database genome contains multiple seedk-mers each with a shared prefix with one of the probes. Storing these seeds, indexed by the probes with which they agree, in a hierarchical index enables fast and low-memory variable-length seed matching, pseudoalignment, and then full alignment. We show that LexicMap is able to align with higher sensitivity than Blastn as the query divergence drops from 90% to 80% for queries $\geq$ 1 kb, and then benchmark on small (GTDB) and large (AllTheBacteria and Genbank+RefSeq) databases. We show that LexicMap achieves higher sensitivity and speed and lower memory compared to the state-of-the-art approaches. Alignment of a single gene against 2.34 million prokaryotic genomes from GenBank and RefSeq takes 36 seconds (rare gene) to 15 minutes (16S rRNA gene). LexicMap produces output in standard formats including that of BLAST and is available under MIT license athttps://github.com/shenwei356/LexicMap.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]]
- [[GTDB - Step-by-Step Dataset Download & Setup]]

## BibTeX Citation
```bibtex
@article{shenLexicMapEfficientSequence2024,
  title = {LexicMap: Efficient Sequence Alignment against Millions of Prokaryotic Genomes},
  author = {Shen, Wei and Iqbal, Zamin},
  year = {2024},
  journal = {bioRxiv},
  doi = {}
}
```
