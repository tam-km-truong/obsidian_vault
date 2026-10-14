---
category: literature
citekey: "priceFastTreeComputingLarge2009"
title: "FastTree: Computing Large Minimum Evolution Trees with Profiles Instead of a Distance Matrix"
aliases:
  - "FastTree: Computing Large Minimum Evolution Trees with Profiles Instead of a Distance Matrix"
  - "Price et al. (2009)"
  - "@priceFastTreeComputingLarge2009"
authors:
  - "Price, Morgan N"
  - "Dehal, Paramvir S"
  - "Arkin, Adam P"
year: 2009
journal: "Mol. Biol. Evol."
doi: ""
topic: "Phylogenetics & Trees"
tags:
  - literature
  - paper
  - phylogenetics-and-trees
status: unread
---

# FastTree: Computing Large Minimum Evolution Trees with Profiles Instead of a Distance Matrix

- **Authors:** Price et al.
- **Year:** 2009
- **Journal / Venue:** *Mol. Biol. Evol.*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@priceFastTreeComputingLarge2009)

## Abstract
> Gene families are growing rapidly, but standard methods for inferring phylogenies do not scale to alignments with over 10,000 sequences. We present FastTree, a method for constructing large phylogenies and for estimating their reliability. Instead of storing a distance matrix, FastTree stores sequence profiles of internal nodes in the tree. FastTree uses these profiles to implement Neighbor-Joining and uses heuristics to quickly identify candidate joins. FastTree then uses nearest neighbor interchanges to reduce the length of the tree. For an alignment with N sequences, L sites, and a different characters, a distance matrix requires O(N(2)) space and O(N(2)L) time, but FastTree requires just O(NLa + N ) memory and O(N log (N)La) time. To estimate the tree's reliability, FastTree uses local bootstrapping, which gives another 100-fold speedup over a distance matrix. For example, FastTree computed a tree and support values for 158,022 distinct 16S ribosomal RNAs in 17 h and 2.4 GB of memory. Just computing pairwise Jukes-Cantor distances and storing them, without inferring a tree or bootstrapping, would require 17 h and 50 GB of memory. In simulations, FastTree was slightly more accurate than Neighbor-Joining, BIONJ, or FastME; on genuine alignments, FastTree's topologies had higher likelihoods. FastTree is available at http://microbesonline.org/fasttree.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@article{priceFastTreeComputingLarge2009,
  title = {FastTree: Computing Large Minimum Evolution Trees with Profiles Instead of a Distance Matrix},
  author = {Price, Morgan N and Dehal, Paramvir S and Arkin, Adam P},
  year = {2009},
  journal = {Mol. Biol. Evol.},
  doi = {}
}
```
