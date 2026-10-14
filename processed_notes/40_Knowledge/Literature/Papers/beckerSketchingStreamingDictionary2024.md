---
category: literature
citekey: "beckerSketchingStreamingDictionary2024"
title: "Sketching and Streaming for Dictionary Compression"
aliases:
  - "Sketching and Streaming for Dictionary Compression"
  - "Becker et al. (2024)"
  - "@beckerSketchingStreamingDictionary2024"
authors:
  - "Becker, Ruben"
  - "Canton, Matteo"
  - "Cenzato, Davide"
  - "Kim, Sung-Hwan"
  - "Kodric, Bojana"
  - "Prezza, Nicola"
year: 2024
journal: "2024 Data Compression Conference (DCC)"
doi: ""
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# Sketching and Streaming for Dictionary Compression

- **Authors:** Becker et al.
- **Year:** 2024
- **Journal / Venue:** *2024 Data Compression Conference (DCC)*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@beckerSketchingStreamingDictionary2024)

## Abstract
> We initiate the study of sub-linear sketching and streaming techniques for estimating the output size of common dictionary compressors such as Lempel-Ziv '77, the run-length Burrows-Wheeler transform, and grammar compression. To this end, we focus on a measure that has recently gained much attention in the information-theoretic community and which approximates up to a polylogarithmic multiplicative factor the output sizes of those compressors: the normalized substring complexity function $\delta$. As a matter of fact, $\delta$ itself is a very accurate measure of compressibility: it is monotone under concatenation, invariant under reversals and alphabet permutations, sub-additive, and asymptotically tight (in terms of worst-case entropy) for representing strings, up to polylogarithmic factors.We present a data sketch of O($\varepsilon-$3 log n + $\varepsilon-$1 log2 n) words that allows computing a multiplicative (1 $\varepsilon$)-approximation of $\delta$ with high probability, where n is the string length. The sketches of two strings S1,S2 can be merged in O($\varepsilon-$1 log2 n) time to yield the sketch of S1,S2, speeding up the computation of Normalized Compression Distances (NCD). If random access is available on the input, our sketch can be updated in O($\varepsilon-$1 log2 n) time for each character right-extension of the string. This yields a polylogarithmic-space algorithm for approximating $\delta$, improving exponentially over the working space of the state-of-the-art algorithms running in nearly-linear time. Motivated by the fact that random access is not always available on the input data, we then present a streaming algorithm computing our sketch in O(\ sqrt n \ cdot \l og n) working space and O($\varepsilon-$1 log2 n) worst-case delay per character. We show that an implementation of our streaming algorithm can estimate $\delta$ on a dataset of 189GB with a throughput of 203MB per minute while using only 5MB of RAM, and that our sketch speeds up the computation of all-pairs NCD distances by one order of magnitude, with applications to phylogenetic tree reconstruction.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]]

## BibTeX Citation
```bibtex
@inproceedings{beckerSketchingStreamingDictionary2024,
  title = {Sketching and Streaming for Dictionary Compression},
  author = {Becker, Ruben and Canton, Matteo and Cenzato, Davide and Kim, Sung-Hwan and Kodric, Bojana and Prezza, Nicola},
  year = {2024},
  journal = {2024 Data Compression Conference (DCC)},
  doi = {}
}
```
