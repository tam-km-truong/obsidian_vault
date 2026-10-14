---
category: literature
citekey: "agretOptimalFingerprintIndexing2021"
title: "Toward Optimal Fingerprint Indexing for Large Scale Genomics"
aliases:
  - "Toward Optimal Fingerprint Indexing for Large Scale Genomics"
  - "Agret et al. (2021)"
  - "@agretOptimalFingerprintIndexing2021"
authors:
  - "Agret, Clement"
  - "Cazaux, Bastien"
  - "Limasset, Antoine"
year: 2021
journal: "bioRxiv"
doi: ""
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# Toward Optimal Fingerprint Indexing for Large Scale Genomics

- **Authors:** Agret et al.
- **Year:** 2021
- **Journal / Venue:** *bioRxiv*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@agretOptimalFingerprintIndexing2021)

## Abstract
> Motivation: To keep up with the scale of genomic databases, several methods rely on local sensitive hashing methods to efficiently find potential matches within large genome collections. Existing solutions rely on Minhash or Hyperloglog fingerprints and require reading the whole index to perform a query. Such solutions can not be considered scalable with the growing amount of documents to index. Results: We present NIQKI, a novel structure using well-designed fingerprints that lead to theoretical and practical query time improvements, outperforming state-of-the-art by orders of magnitude. Our contribution is threefold. First, we generalize the concept of Hyperminhash fingerprints in (h,m)-HMH fingerprints that can be tuned to present the lowest false positive rate given the expected sub-sampling applied. Second, we provide a structure able to index any kind of fingerprints based on inverted indexes that provide optimal queries, namely linear with the size of the output. Third, we implemented these approaches in a tool dubbed NIQKI that can index and calculate pairwise distances for over one million bacterial genomes from GenBank in a matter of days on a small cluster. We show that our approach can be orders of magnitude faster than state-of-the-art with comparable precision. We believe that this approach can lead to tremendous improvement allowing fast query, scaling on extensive genomic databases. Availability and implementation: We wrote the NIQKI index as an open-source C++ library under the AGPL3 license available at https://github.com/Malfoy/ NIQKI. It is designed as a user-friendly tool and comes along with usage sample

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Mash & MinHash Sketching]]
- [[dashing2 - HyperLogLog Genome Sketching]]

## BibTeX Citation
```bibtex
@article{agretOptimalFingerprintIndexing2021,
  title = {Toward Optimal Fingerprint Indexing for Large Scale Genomics},
  author = {Agret, Clement and Cazaux, Bastien and Limasset, Antoine},
  year = {2021},
  journal = {bioRxiv},
  doi = {}
}
```
