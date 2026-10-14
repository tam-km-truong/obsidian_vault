---
category: literature
citekey: "yuHyperMinHashMinHashLogLog2019"
title: "HyperMinHash: MinHash in LogLog Space"
aliases:
  - "HyperMinHash: MinHash in LogLog Space"
  - "Yu & Weber (2019)"
  - "@yuHyperMinHashMinHashLogLog2019"
  - "@yuHyperMinHashMinHashLogLog2019a"
authors:
  - "Yu, Yun William"
  - "Weber, Griffin M."
year: 2019
journal: "arXiv"
doi: "10.48550/arXiv.1710.08436"
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# HyperMinHash: MinHash in LogLog Space

- **Authors:** Yu & Weber
- **Year:** 2019
- **Journal / Venue:** *arXiv*
- **Links:** [DOI](https://doi.org/10.48550/arXiv.1710.08436) | [Open in Zotero Desktop](zotero://select/items/@yuHyperMinHashMinHashLogLog2019)

## Abstract
> In this extended abstract, we describe and analyze a lossy compression of MinHash from buckets of size $O(\ log n)$ to buckets of size $O(\ log\ log n)$ by encoding using floating-point notation. This new compressed sketch, which we call HyperMinHash, as we build off a HyperLogLog scaffold, can be used as a drop-in replacement of MinHash. Unlike comparable Jaccard index fingerprinting algorithms in sub-logarithmic space (such as b-bit MinHash), HyperMinHash retains MinHash's features of streaming updates, unions, and cardinality estimation. For a multiplicative approximation error $1+ \ epsilon$ on a Jaccard index $ t $, given a random oracle, HyperMinHash needs $O\ left(\ epsilon\textasciicircum\textbraceleft -2 \ left( \ log\ log n + \ log \ frac\textbraceleft 1\textbraceright t \ epsilon \ right)\ right)$ space. HyperMinHash allows estimating Jaccard indices of 0.01 for set cardinalities on the order of $10\textasciicircum\textbraceleft 19\textbraceright$ with relative error of around 10\% using 64KiB of memory; MinHash can only estimate Jaccard indices for cardinalities of $10\textasciicircum\textbraceleft 10\textbraceright$ with the same memory consumption.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Mash & MinHash Sketching]]
- [[dashing2 - HyperLogLog Genome Sketching]]

## BibTeX Citation
```bibtex
@misc{yuHyperMinHashMinHashLogLog2019,
  title = {HyperMinHash: MinHash in LogLog Space},
  author = {Yu, Yun William and Weber, Griffin M.},
  year = {2019},
  journal = {arXiv},
  doi = {10.48550/arXiv.1710.08436}
}
```
