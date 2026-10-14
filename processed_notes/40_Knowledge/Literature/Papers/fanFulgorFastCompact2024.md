---
category: literature
citekey: "fanFulgorFastCompact2024"
title: "Fulgor: A Fast and Compact k-Mer Index for Large-Scale Matching and Color Queries"
aliases:
  - "Fulgor: A Fast and Compact k-Mer Index for Large-Scale Matching and Color Queries"
  - "Fan et al. (2024)"
  - "@fanFulgorFastCompact2024"
authors:
  - "Fan, Jason"
  - "Khan, Jamshed"
  - "Singh, Noor Pratap"
  - "Pibiri, Giulio Ermanno"
  - "Patro, Rob"
year: 2024
journal: "Algorithms Mol. Biol."
doi: ""
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# Fulgor: A Fast and Compact k-Mer Index for Large-Scale Matching and Color Queries

- **Authors:** Fan et al.
- **Year:** 2024
- **Journal / Venue:** *Algorithms Mol. Biol.*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@fanFulgorFastCompact2024)

## Abstract
> The problem of sequence identification or matching-determining the subset of reference sequences from a given collection that are likely to contain a short, queried nucleotide sequence-is relevant for many important tasks in Computational Biology, such as metagenomics and pangenome analysis. Due to the complex nature of such analyses and the large scale of the reference collections a resource-efficient solution to this problem is of utmost importance. This poses the threefold challenge of representing the reference collection with a data structure that is efficient to query, has light memory usage, and scales well to large collections. To solve this problem, we describe an efficient colored de Bruijn graph index, arising as the combination of a k-mer dictionary with a compressed inverted index. The proposed index takes full advantage of the fact that unitigs in the colored compacted de Bruijn graph are monochromatic (i.e., all k-mers in a unitig have the same set of references of origin, or color). Specifically, the unitigs are kept in the dictionary in color order, thereby allowing for the encoding of the map from k-mers to their colors in as little as 1 + o(1) bits per unitig. Hence, one color per unitig is stored in the index with almost no space/time overhead. By combining this property with simple but effective compression methods for integer lists, the index achieves very small space. We implement these methods in a tool called Fulgor, and conduct an extensive experimental analysis to demonstrate the improvement of our tool over previous solutions. For example, compared to Themisto-the strongest competitor in terms of index space vs. query time trade-off-Fulgor requires significantly less space (up to 43% less space for a collection of 150,000 Salmonella enterica genomes), is at least twice as fast for color queries, and is 2-6[Formula: see text] faster to construct.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@article{fanFulgorFastCompact2024,
  title = {Fulgor: A Fast and Compact k-Mer Index for Large-Scale Matching and Color Queries},
  author = {Fan, Jason and Khan, Jamshed and Singh, Noor Pratap and Pibiri, Giulio Ermanno and Patro, Rob},
  year = {2024},
  journal = {Algorithms Mol. Biol.},
  doi = {}
}
```
