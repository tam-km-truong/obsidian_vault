---
category: literature
citekey: "kempaRootsDictionaryCompression2018"
title: "At the Roots of Dictionary Compression: String Attractors"
aliases:
  - "At the Roots of Dictionary Compression: String Attractors"
  - "Kempa & Prezza (2018)"
  - "@kempaRootsDictionaryCompression2018"
  - "@kempaRootsDictionaryCompression2018a"
authors:
  - "Kempa, Dominik"
  - "Prezza, Nicola"
year: 2018
journal: "Proceedings of the 50th Annual ACM SIGACT Symposium on Theory of Computing"
doi: "10.1145/3188745.3188814"
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# At the Roots of Dictionary Compression: String Attractors

- **Authors:** Kempa & Prezza
- **Year:** 2018
- **Journal / Venue:** *Proceedings of the 50th Annual ACM SIGACT Symposium on Theory of Computing*
- **Links:** [DOI](https://doi.org/10.1145/3188745.3188814) | [Open in Zotero Desktop](zotero://select/items/@kempaRootsDictionaryCompression2018)

## Abstract
> A well-known fact in the field of lossless text compression is that high-order entropy is a weak model when the input contains long repetitions. Motivated by this fact, decades of research have generated myriads of so-called dictionary compressors: algorithms able to reduce the text's size by exploiting its repetitiveness. Lempel-Ziv 77 is one of the most successful and well-known tools of this kind, followed by straight-line programs, run-length Burrows-Wheeler transform, macro schemes, collage systems, and the compact directed acyclic word graph. In this paper, we show that these techniques are different solutions to the same, elegant, combinatorial problem: to find a small set of positions capturing all distinct text's substrings. We call such a set a string attractor. We first show reductions between dictionary compressors and string attractors. This gives the approximation ratios of dictionary compressors with respect to the smallest string attractor and allows us to uncover new asymptotic relations between the output sizes of different dictionary compressors. We then show that the k-attractor problem --- deciding whether a text has a size-t set of positions capturing all substrings of length at most k --- is NP-complete for k$\geq$ 3. This, in particular, includes the full string attractor problem. We provide several approximation techniques for the smallest k-attractor, show that the problem is APX-complete for constant k, and give strong inapproximability results. To conclude, we provide matching lower and upper bounds for the random access problem on string attractors. The upper bound is proved by showing a data structure supporting queries in optimal time. Our data structure is universal: by our reductions to string attractors, it supports random access on any dictionary-compression scheme. In particular, it matches the lower bound also on LZ77, straight-line programs, collage systems, and macro schemes, and therefore essentially closes (at once) the random access problem for all these compressors.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@inproceedings{kempaRootsDictionaryCompression2018,
  title = {At the Roots of Dictionary Compression: String Attractors},
  author = {Kempa, Dominik and Prezza, Nicola},
  year = {2018},
  journal = {Proceedings of the 50th Annual ACM SIGACT Symposium on Theory of Computing},
  doi = {10.1145/3188745.3188814}
}
```
