---
category: literature
citekey: "tanOnlineBinPacking2024"
title: "Online Bin Packing with Load-Balancing"
aliases:
  - "Online Bin Packing with Load-Balancing"
  - "Tan et al. (2024)"
  - "@tanOnlineBinPacking2024"
  - "@tanOnlineBinPacking2024a"
authors:
  - "Tan, Zheng"
  - "Qin, Hanzhang"
  - "Chen, Yan"
  - "Liu, Lindong"
  - "Yu, Yugang"
year: 2024
journal: "Social Science Research Network"
doi: "10.2139/ssrn.4989464"
topic: "Algorithms & Optimization"
tags:
  - literature
  - paper
  - algorithms-and-optimization
status: unread
---

# Online Bin Packing with Load-Balancing

- **Authors:** Tan et al.
- **Year:** 2024
- **Journal / Venue:** *Social Science Research Network*
- **Links:** [DOI](https://doi.org/10.2139/ssrn.4989464) | [Open in Zotero Desktop](zotero://select/items/@tanOnlineBinPacking2024)

## Abstract
> Bin packing problem is a fundamental problem in computer science and combinatorial optimization and has been studied extensively due to its wide application in inventory management, resource allocation, shipping logistics and machine scheduling problems, etc. In the simplest online setup, a sequence of T items arrive one at a time, and each item must be placed into one of the available bins upon arrival. The sizes and the sequences of the items are unknown beforehand, but the sizes of the items are revealed upon arrival. Usually, the sizes are drawn i.i.d. from some unknown distribution, and the goal is usually to minimize the number of bins used. Additionally, the load-balancing objective is prominent in similar practical scenarios such as last-mile delivery and cloud computing. We consider an online bin packing problem with load-balancing constraints. We find that the constraints on both bin capacity and the maximum number of bins necessitate more sophisticated approaches. This paper presents a novel framework using a level-based LP formulation to optimize a customized loss function integrating both objectives: reduce excess bins and achieve load-balancing. We propose algorithms for two cases: small-size items and general-size items. For small-size items, we propose an online algorithm, PD-exp-B, that achieves near-optimal solutions. Our proposed PD-exp-B has a competitive ratio asymptotically converging to 1 + f ($\eta$) where $\eta$ upper bounds the item size, and f is a linear function depending on the item size distribution. For general-size items, our Rounding-and-Repacking algorithm is an asymptotic fully polynomial time approximation scheme (AFPTAS) with limited repacking and excess use of bins.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]]

## BibTeX Citation
```bibtex
@misc{tanOnlineBinPacking2024,
  title = {Online Bin Packing with Load-Balancing},
  author = {Tan, Zheng and Qin, Hanzhang and Chen, Yan and Liu, Lindong and Yu, Yugang},
  year = {2024},
  journal = {Social Science Research Network},
  doi = {10.2139/ssrn.4989464}
}
```
