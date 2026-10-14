---
category: literature
citekey: "sindelarSharingawareAlgorithmsVirtual2011"
title: "Sharing-Aware Algorithms for Virtual Machine Colocation"
aliases:
  - "Sharing-Aware Algorithms for Virtual Machine Colocation"
  - "Sindelar et al. (2011)"
  - "@sindelarSharingawareAlgorithmsVirtual2011"
authors:
  - "Sindelar, Michael"
  - "Sitaraman, Ramesh K"
  - "Shenoy, Prashant"
year: 2011
journal: "Proceedings of the Twenty-Third Annual ACM Symposium on Parallelism in Algorithms and Architectures"
doi: ""
topic: "Phylogenetics & Trees"
tags:
  - literature
  - paper
  - phylogenetics-and-trees
status: unread
---

# Sharing-Aware Algorithms for Virtual Machine Colocation

- **Authors:** Sindelar et al.
- **Year:** 2011
- **Journal / Venue:** *Proceedings of the Twenty-Third Annual ACM Symposium on Parallelism in Algorithms and Architectures*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@sindelarSharingawareAlgorithmsVirtual2011)

## Abstract
> Virtualization technology enables multiple virtual machines (VMs) to run on a single physical server. VMs that run on the same physical server can share memory pages that have identical content, thereby reducing the overall memory requirements on the server. We develop sharing-aware algorithms that can colocate VMs with similar page content on the same physical server to optimize the benefits of inter-VM sharing. We show that inter-VM sharing occurs in a largely hierarchical fashion, where the sharing can be attributed to VM's running the same OS platform, OS version, software libraries, or applications. We propose two hierarchical sharing models: a tree model and a more general cluster-tree model. Using a set of VM traces, we show that up to 67% percent of the inter-VM sharing is captured by the tree model and up to 82% is captured by the cluster-tree model. Next, we study two problem variants of critical interest to a virtualization service provider: the VM Maximization problem that determines the most profitable subset of the VMs that can be packed into the given set of servers, and the VM packing problem that determines the smallest set of servers that can accommodate a set of VMs. While both variants are NP-hard, we show that both admit provably good approximation schemes in the hierarchical sharing models. We show that VM maximization for the tree and cluster-tree models can be approximated in polytime to within a (1 - 1/e) factor of optimal. Further, we show that VM packing can be approximated in polytime to within a factor of O(log n) of optimal for cluster-trees and to within a factor of 3 of optimal for trees, where n is the number of VMs. Finally, we evaluate our VM packing algorithm for the tree sharing model on real-world VM traces and show that our algorithm can exploit most of the available inter-VM sharing to achieve a 32% to 50% reduction in servers and a 25% to 57% reduction in memory footprint compared to sharing-oblivious algorithms.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]]

## BibTeX Citation
```bibtex
@inproceedings{sindelarSharingawareAlgorithmsVirtual2011,
  title = {Sharing-Aware Algorithms for Virtual Machine Colocation},
  author = {Sindelar, Michael and Sitaraman, Ramesh K and Shenoy, Prashant},
  year = {2011},
  journal = {Proceedings of the Twenty-Third Annual ACM Symposium on Parallelism in Algorithms and Architectures},
  doi = {}
}
```
