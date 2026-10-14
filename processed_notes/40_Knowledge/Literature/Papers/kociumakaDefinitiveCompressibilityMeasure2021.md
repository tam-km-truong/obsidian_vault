---
category: literature
citekey: "kociumakaDefinitiveCompressibilityMeasure2021"
title: "Towards a Definitive Compressibility Measure for Repetitive Sequences"
aliases:
  - "Towards a Definitive Compressibility Measure for Repetitive Sequences"
  - "Kociumaka et al. (2021)"
  - "@kociumakaDefinitiveCompressibilityMeasure2021"
  - "@kociumakaDefinitiveCompressibilityMeasure2021a"
authors:
  - "Kociumaka, Tomasz"
  - "Navarro, Gonzalo"
  - "Prezza, Nicola"
year: 2021
journal: "arXiv"
doi: "10.48550/arXiv.1910.02151"
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# Towards a Definitive Compressibility Measure for Repetitive Sequences

- **Authors:** Kociumaka et al.
- **Year:** 2021
- **Journal / Venue:** *arXiv*
- **Links:** [DOI](https://doi.org/10.48550/arXiv.1910.02151) | [Open in Zotero Desktop](zotero://select/items/@kociumakaDefinitiveCompressibilityMeasure2021)

## Abstract
> Unlike in statistical compression, where Shannon's entropy is a definitive lower bound, no such clear measure exists for the compressibility of repetitive sequences. Since statistical entropy does not capture repetitiveness, ad-hoc measures like the size $z$ of the Lempel--Ziv parse are frequently used to estimate it. The size $b \ le z$ of the smallest bidirectional macro scheme captures better what can be achieved via copy-paste processes, though it is NP-complete to compute and it is not monotonic upon symbol appends. Recently, a more principled measure, the size $\ gamma$ of the smallest string \ emph\textbraceleft attractor\textbraceright, was introduced. The measure $\ gamma \ le b$ lower bounds all the previous relevant ones, yet length-$n$ strings can be represented and efficiently indexed within space $O(\ gamma\ log\ frac\textbraceleft n\textbraceright\textbraceleft\ gamma\textbraceright )$, which also upper bounds most measures. While $\ gamma$ is certainly a better measure of repetitiveness than $b$, it is also NP-complete to compute and not monotonic, and it is unknown if one can always represent a string in $o(\ gamma\ log n)$ space. In this paper, we study an even smaller measure, $\ delta \ le \ gamma$, which can be computed in linear time, is monotonic, and allows encoding every string in $O(\ delta\ log\ frac\textbraceleft n\textbraceright\textbraceleft\ delta\textbraceright )$ space because $z = O(\ delta\ log\ frac\textbraceleft n\textbraceright\textbraceleft\ delta\textbraceright )$. We show that $\ delta$ better captures the compressibility of repetitive strings. Concretely, we show that (1) $\ delta$ can be strictly smaller than $\ gamma$, by up to a logarithmic factor; (2) there are string families needing $\ Omega(\ delta\ log\ frac\textbraceleft n\textbraceright\textbraceleft\ delta\textbraceright )$ space to be encoded, so this space is optimal for every $n$ and $\ delta$; (3) one can build run-length context-free grammars of size $O(\ delta\ log\ frac\textbraceleft n\textbraceright\textbraceleft\ delta\textbraceright )$, whereas the smallest (non-run-length) grammar can be up to $\ Theta(\ log n/\ log\ log n)$ times larger; and (4) within $O(\ delta\ log\ frac\textbraceleft n\textbraceright\textbraceleft\ delta\textbraceright )$ space we can not only...

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@misc{kociumakaDefinitiveCompressibilityMeasure2021,
  title = {Towards a Definitive Compressibility Measure for Repetitive Sequences},
  author = {Kociumaka, Tomasz and Navarro, Gonzalo and Prezza, Nicola},
  year = {2021},
  journal = {arXiv},
  doi = {10.48550/arXiv.1910.02151}
}
```
