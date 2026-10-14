---
category: literature
citekey: "ingelsCompressedInvertedIndexes2025"
title: "Compressed Inverted Indexes for Scalable Sequence Similarity"
aliases:
  - "Compressed Inverted Indexes for Scalable Sequence Similarity"
  - "Ingels et al. (2025)"
  - "@ingelsCompressedInvertedIndexes2025"
authors:
  - "Ingels, Florian"
  - "Vandamme, L\'ea"
  - "Girard, Mathilde"
  - "Agret, Cl\'ement"
  - "Cazaux, Bastien"
  - "Limasset, Antoine"
year: 2025
journal: "bioRxiv"
doi: ""
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# Compressed Inverted Indexes for Scalable Sequence Similarity

- **Authors:** Ingels et al.
- **Year:** 2025
- **Journal / Venue:** *bioRxiv*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@ingelsCompressedInvertedIndexes2025)

## Abstract
> Abstract Modern sequencing continues to drive explosive growth of nucleotide sequence archives, pushing MinHash-derived sketching methods to their practical scalability limits. State-of-the-art tools such as Mash, Dashing2, and Bindash2 provide compact sketches and accurate similarity estimates for large collections, yet ultimately rely on forward indexes that materialize sketches as explicit finger-print vectors. As a result, large-scale similarity search and exhaustive collection-versus-collection comparison still incur quadratic resource usage. In this work, we revisit the architecture of sketch-based indexes and provide a novel framework for scalable similarity search over massive sketch collections. Our first contribution is a formal cost model for sketch comparison, within which we prove that inverted indexes on sketch fingerprints, equipped with suitably compressed posting lists, achieve the same asymptotic space complexity as standard forward indexes, thereby eliminating the perceived memory penalty traditionally associated with inverted indexes. Building on this model, we design algorithms for all-vs-all comparison between two inverted indexes whose running times are proportional to the total number of matching sketch positions, leading to output-sensitive optimality and enabling efficient large-scale similarity comparisons. Our second contribution leverages the prevalence of similarity thresholds in downstream applications such as clustering, redundancy filtering, and database search. We introduce two early-pruning schemes: an exact criterion that safely eliminates pairs guaranteed not to reach a target Jaccard similarity, and a probabilistic strategy that exploits partial match statistics to discard pairs unlikely to exceed this threshold. Together, these schemes address both time and memory bottlenecks while maintaining rigorous guarantees on retained high-similarity pairs and providing explicit control of the false-rejection probability for the probabilistic variant. Finally, we instantiate these ideas in Onika, an open-source Rust implementation based on compressed inverted posting lists available at github.com/Malfoy/Onika . Onika incorporates a similarity-aware document reordering strategy that restructures sketch identifiers to further shrink index size and improve locality, particularly for redundant collections. Experiments on large bacterial genome repositories, synthetic low-redundancy benchmarks, and long-read HiFi sequencing datasets demonstrate that Onika matches or improves upon the sketch sizes of leading tools while accelerating large-scale search and collection-versus-collection comparisons by up to several orders of magnitude in low-redundancy regimes, without compromising sensitivity at practically relevant similarity thresholds.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Mash & MinHash Sketching]]
- [[Rust - Syntax & Attribute Cheatsheet]]
- [[dashing2 - HyperLogLog Genome Sketching]]

## BibTeX Citation
```bibtex
@article{ingelsCompressedInvertedIndexes2025,
  title = {Compressed Inverted Indexes for Scalable Sequence Similarity},
  author = {Ingels, Florian and Vandamme, L\'ea and Girard, Mathilde and Agret, Cl\'ement and Cazaux, Bastien and Limasset, Antoine},
  year = {2025},
  journal = {bioRxiv},
  doi = {}
}
```
