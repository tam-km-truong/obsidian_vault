---
category: literature
citekey: "amestoyComputingInverseEntries2012"
title: "On Computing Inverse Entries of a Sparse Matrix in an Out-of-Core Environment"
aliases:
  - "On Computing Inverse Entries of a Sparse Matrix in an Out-of-Core Environment"
  - "Amestoy et al. (2012)"
  - "@amestoyComputingInverseEntries2012"
authors:
  - "Amestoy, Patrick R"
  - "Duff, Iain S"
  - "L'Excellent, Jean-Yves"
  - "Robert, Yves"
  - "Rouet, Fran\c cois-Henry"
  - "U\c car, Bora"
year: 2012
journal: "SIAM J. Sci. Comput."
doi: ""
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# On Computing Inverse Entries of a Sparse Matrix in an Out-of-Core Environment

- **Authors:** Amestoy et al.
- **Year:** 2012
- **Journal / Venue:** *SIAM J. Sci. Comput.*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@amestoyComputingInverseEntries2012)

## Abstract
> The inverse of an irreducible sparse matrix is structurally full, so that it is impractical to think of computing or storing it. However, there are several applications where a subset of the entries of the inverse is required. Given a factorization of the sparse matrix held in out-of-core storage, we show how to compute such a subset e ciently, by accessing only parts of the factors. When there are many inverse entries to compute, we need to guarantee that the overall computation scheme has reasonable memory requirements, while minimizing the cost of loading the factors. This leads to a partitioning problem that we prove is NP-complete. We also show that we cannot get a close approximation to the optimal solution in polynomial time. We thus need to develop heuristic algorithms, and we propose: (i) a lower bound on the cost of an optimum solution; (ii) an exact algorithm for a particular case; (iii) two other heuristics for a more general case; and (iv) hypergraph partitioning models for the most general setting. We illustrate the performance of our algorithms in practice using the MUMPS software package on a set of real-life problems as well as some standard test matrices. We show that our techniques can improve the execution time by a factor of 50. Key words. Sparse matrices, direct methods for linear systems and matrix inversion, multifrontal method, graphs and hypergraphs.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]]

## BibTeX Citation
```bibtex
@article{amestoyComputingInverseEntries2012,
  title = {On Computing Inverse Entries of a Sparse Matrix in an Out-of-Core Environment},
  author = {Amestoy, Patrick R and Duff, Iain S and L'Excellent, Jean-Yves and Robert, Yves and Rouet, Fran\c cois-Henry and U\c car, Bora},
  year = {2012},
  journal = {SIAM J. Sci. Comput.},
  doi = {}
}
```
