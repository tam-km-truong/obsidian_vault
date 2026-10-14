---
category: literature
citekey: "kociumakaDefinitiveMeasureRepetitiveness2020"
title: "Towards a Definitive Measure of Repetitiveness"
aliases:
  - "Towards a Definitive Measure of Repetitiveness"
  - "Kociumaka et al. (2020)"
  - "@kociumakaDefinitiveMeasureRepetitiveness2020"
  - "@kociumakaDefinitiveMeasureRepetitiveness2020a"
authors:
  - "Kociumaka, Tomasz"
  - "Navarro, Gonzalo"
  - "Prezza, Nicola"
year: 2020
journal: "LATIN 2020: Theoretical Informatics"
doi: "10.1007/978-3-030-61792-9_17"
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# Towards a Definitive Measure of Repetitiveness

- **Authors:** Kociumaka et al.
- **Year:** 2020
- **Journal / Venue:** *LATIN 2020: Theoretical Informatics*
- **Links:** [DOI](https://doi.org/10.1007/978-3-030-61792-9_17) | [Open in Zotero Desktop](zotero://select/items/@kociumakaDefinitiveMeasureRepetitiveness2020)

## Abstract
> Unlike in statistical compression, where Shannon's entropy is a definitive lower bound, no such clear measure exists for the compressibility of repetitive sequences. Since statistical entropy does not capture repetitiveness, ad-hoc measures like the size z of the Lempel--Ziv parse are frequently used to estimate repetitiveness. Recently, a more principled measure, the size $$\ gamma $$$\gamma$of the smallest string attractor, was introduced. The measure $$\ gamma $$$\gamma$lower bounds all the previous relevant ones (including z), yet length-n strings can be represented and efficiently indexed within space $$O(\ gamma \ log \ frac\textbraceleft n\textbraceright\textbraceleft\ gamma \textbraceright )$$O($\gamma$logn$\gamma$), which also upper bounds most measures (including z). While $$\ gamma $$$\gamma$is certainly a better measure of repetitiveness than z, it is NP-complete to compute, and no $$o(\ gamma \ log n)$$o($\gamma$logn)-space representation of strings is known. In this paper, we study a smaller measure, $$\ delta \ le \ gamma $$$\delta\leq\gamma$, which can be computed in linear time. We show that $$\ delta $$$\delta$better captures the compressibility of repetitive strings. For every length n and every value $$\ delta \ ge 2$$$\delta\geq$2, we construct a string such that $$\ gamma = \ varOmega (\ delta \ log \ frac\textbraceleft n\textbraceright\textbraceleft\ delta \textbraceright )$$$\gamma$=\textohm ($\delta$logn$\delta$). Still, we show a representation of any string S in $$O(\ delta \ log \ frac\textbraceleft n\textbraceright\textbraceleft\ delta \textbraceright )$$O($\delta$logn$\delta$)space that supports direct access to any character S[i] in time $$O(\ log \ frac\textbraceleft n\textbraceright\textbraceleft\ delta \textbraceright )$$O(logn$\delta$)and finds the occ occurrences of any pattern $$P[1\textbraceleft.\,.\textbraceright m]$$P[1..m]in time $$O(m\ log n + occ\ log \textasciicircum\ varepsilon n)$$O(mlogn+occlog$\varepsilon$n)for any constant $$\ varepsilon $>$0$$$\varepsilon>$0. Further, we prove that no $$o(\ delta \ log n)$$o($\delta$logn)-space representation exists: for every length n and every value $$2\ le \ delta \ le n\textasciicircum\textbraceleft 1-\ varepsilon \textbraceright$$2$\leq\delta\leq$n1-$\varepsilon$, we exhibit a string family whose elements can only be encoded in $$\ varOmega (\ delta \ log \ frac\textbraceleft n\textbraceright\textbraceleft\ delta \textbraceright )$$\textohm ($\delta$logn$\delta$)space. We complete our characterization of $$\ delta $$$\delta$by showing that, although $$\ gamma $$$\gamma$, z, and other repetitiveness measures are always $$O(\ delta \ log \ frac\textbraceleft n\textbraceright\textbraceleft\ delta \textbraceright )$$O($\delta$logn$\delta$), for strings of any length n, the smallest context-free grammar can be of size $$\ varOmega (\ delta \ log \textasciicircum 2 n/\ log \ log n)$$\textohm ($\delta$log2n/loglogn). No such separation is known for $$\ gamma $$$\gamma$.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@inproceedings{kociumakaDefinitiveMeasureRepetitiveness2020,
  title = {Towards a Definitive Measure of Repetitiveness},
  author = {Kociumaka, Tomasz and Navarro, Gonzalo and Prezza, Nicola},
  year = {2020},
  journal = {LATIN 2020: Theoretical Informatics},
  doi = {10.1007/978-3-030-61792-9_17}
}
```
