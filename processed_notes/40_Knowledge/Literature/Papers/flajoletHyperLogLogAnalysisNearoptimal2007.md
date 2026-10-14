---
category: literature
citekey: "flajoletHyperLogLogAnalysisNearoptimal2007"
title: "HyperLogLog: The Analysis of a near-Optimal Cardinality Estimation Algorithm"
aliases:
  - "HyperLogLog: The Analysis of a near-Optimal Cardinality Estimation Algorithm"
  - "Flajolet et al. (2007)"
  - "@flajoletHyperLogLogAnalysisNearoptimal2007"
  - "@flajoletHyperLogLogAnalysisNearoptimal2007a"
authors:
  - "Flajolet, Philippe"
  - "Fusy, \'Eric"
  - "Gandouet, Olivier"
  - "Meunier, Fr\'ed\'eric"
year: 2007
journal: "Discrete Mathematics & Theoretical Computer Science"
doi: "10.46298/dmtcs.3545"
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# HyperLogLog: The Analysis of a near-Optimal Cardinality Estimation Algorithm

- **Authors:** Flajolet et al.
- **Year:** 2007
- **Journal / Venue:** *Discrete Mathematics & Theoretical Computer Science*
- **Links:** [DOI](https://doi.org/10.46298/dmtcs.3545) | [Open in Zotero Desktop](zotero://select/items/@flajoletHyperLogLogAnalysisNearoptimal2007)

## Abstract
> This extended abstract describes and analyses a near-optimal probabilistic algorithm, HYPERLOGLOG, dedicated to estimating the number of \ emphdistinct elements (the cardinality) of very large data ensembles. Using an auxiliary memory of m units (typically, "short bytes''), HYPERLOGLOG performs a single pass over the data and produces an estimate of the cardinality such that the relative accuracy (the standard error) is typically about $1.04/\ sqrt\textbraceleft m\textbraceright$. This improves on the best previously known cardinality estimator, LOGLOG, whose accuracy can be matched by consuming only 64% of the original memory. For instance, the new algorithm makes it possible to estimate cardinalities well beyond $10\textasciicircum 9$ with a typical accuracy of 2% while using a memory of only 1.5 kilobytes. The algorithm parallelizes optimally and adapts to the sliding window model.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]]
- [[dashing2 - HyperLogLog Genome Sketching]]

## BibTeX Citation
```bibtex
@article{flajoletHyperLogLogAnalysisNearoptimal2007,
  title = {HyperLogLog: The Analysis of a near-Optimal Cardinality Estimation Algorithm},
  author = {Flajolet, Philippe and Fusy, \'Eric and Gandouet, Olivier and Meunier, Fr\'ed\'eric},
  year = {2007},
  journal = {Discrete Mathematics & Theoretical Computer Science},
  doi = {10.46298/dmtcs.3545}
}
```
