---
category: literature
citekey: "zhaoBinDash20New2024"
title: "BinDash 2.0: New MinHash Scheme Allows Ultra-Fast and Accurate Genome Search and Comparisons"
aliases:
  - "BinDash 2.0: New MinHash Scheme Allows Ultra-Fast and Accurate Genome Search and Comparisons"
  - "Zhao et al. (2024)"
  - "@zhaoBinDash20New2024"
authors:
  - "Zhao, Jianshu"
  - "Zhao, Xiaofei"
  - "Pierre-Both, Jean"
  - "Konstantinidis, Konstantinos T"
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

# BinDash 2.0: New MinHash Scheme Allows Ultra-Fast and Accurate Genome Search and Comparisons

- **Authors:** Zhao et al.
- **Year:** 2024
- **Journal / Venue:** *bioRxiv*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@zhaoBinDash20New2024)

## Abstract
> AbstractMotivationComparing large number of genomes in term of their genomic distance is becoming more and more challenging because there is an increasing number of microbial genomes deposited in public databases. Nowadays, we may need to estimate pairwise distances between millions or even billions of genomes. Few softwares can perform such comparisons efficiently.ResultsHere we update the multi-threaded software BinDash by implementing several new MinHash algorithms and computational optimization (e.g. Simple Instruction Multiple Data, SIMD) for ultra-fast and accurate genome search and comparisons at trillion scale. That is, we implemented b-bit one-permutation rolling MinHash with optimal/faster densification with SIMD. Now with BinDash 2, we can perform 0.1 trillion (or $\sim$10\textasciicircum 11) pairs of genome comparisons in about 1.8 hours on a descent computer cluster or several hours on personal laptops, a $\sim$50% or more improvement over original version. The ANI (average nucleotide identity) estimated by BinDash is well correlated with other accurate but much slower ANI estimators such as FastANI or alignment-based ANI. In line with the findings from comparing 90K genomes ($\sim$10\textasciicircum 9 comparisons) via FastANI, the 85% $\sim$ 95% ANI gap is consistent in our study of $\sim$10\textasciicircum 11 prokaryotic genome comparisons via BinDash2, which indicates fundamental ecological and evolutionary forces keeping species-like unit (e.g., $>$ 95% ANI) together.Availability and implementationBinDash is released under the Apache 2.0 license at:https://github.com/zhaoxiaofei/bindashContactkostas.konstantinidis@gatech.eduSupplementary informationSupplementary data are available at Bioinformatics online.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Mash & MinHash Sketching]]

## BibTeX Citation
```bibtex
@article{zhaoBinDash20New2024,
  title = {BinDash 2.0: New MinHash Scheme Allows Ultra-Fast and Accurate Genome Search and Comparisons},
  author = {Zhao, Jianshu and Zhao, Xiaofei and Pierre-Both, Jean and Konstantinidis, Konstantinos T},
  year = {2024},
  journal = {bioRxiv},
  doi = {}
}
```
