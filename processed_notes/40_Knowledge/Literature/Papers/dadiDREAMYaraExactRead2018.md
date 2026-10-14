---
category: literature
citekey: "dadiDREAMYaraExactRead2018"
title: "DREAM-Yara: An Exact Read Mapper for Very Large Databases with Short Update Time"
aliases:
  - "DREAM-Yara: An Exact Read Mapper for Very Large Databases with Short Update Time"
  - "Dadi et al. (2018)"
  - "@dadiDREAMYaraExactRead2018"
  - "@dadiDREAMYaraExactRead2018a"
authors:
  - "Dadi, Temesgen Hailemariam"
  - "Siragusa, Enrico"
  - "Piro, Vitor C"
  - "Andrusch, Andreas"
  - "Seiler, Enrico"
  - "Renard, Bernhard Y"
  - "Reinert, Knut"
year: 2018
journal: "Bioinformatics"
doi: "10.1093/bioinformatics/bty567"
topic: "Sketching & K-mers"
tags:
  - literature
  - paper
  - sketching-and-k-mers
status: unread
---

# DREAM-Yara: An Exact Read Mapper for Very Large Databases with Short Update Time

- **Authors:** Dadi et al.
- **Year:** 2018
- **Journal / Venue:** *Bioinformatics*
- **Links:** [DOI](https://doi.org/10.1093/bioinformatics/bty567) | [Open in Zotero Desktop](zotero://select/items/@dadiDREAMYaraExactRead2018)

## Abstract
> Mapping-based approaches have become limited in their application to very large sets of references since computing an FM-index for very large databases (e.g. &gt;10 GB) has become a bottleneck. This affects many analyses that need such index as an essential step for approximate matching of the NGS reads to reference databases. For instance, in typical metagenomics analysis, the size of the reference sequences has become prohibitive to compute a single full-text index on standard machines. Even on large memory machines, computing such index takes about 1 day of computing time. As a result, updates of indices are rarely performed. Hence, it is desirable to create an alternative way of indexing while preserving fast search times.To solve the index construction and update problem we propose the DREAM (Dynamic seaRchablE pArallel coMpressed index) framework and provide an implementation. The main contributions are the introduction of an approximate search distributor via a novel use of Bloom filters. We combine several Bloom filters to form an interleaved Bloom filter and use this new data structure to quickly exclude reads for parts of the databases where they cannot match. This allows us to keep the databases in several indices which can be easily rebuilt if parts are updated while maintaining a fast search time. The second main contribution is an implementation of DREAM-Yara a distributed version of a fully sensitive read mapper under the DREAM framework.https://gitlab.com/pirovc/dream_yara/

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@article{dadiDREAMYaraExactRead2018,
  title = {DREAM-Yara: An Exact Read Mapper for Very Large Databases with Short Update Time},
  author = {Dadi, Temesgen Hailemariam and Siragusa, Enrico and Piro, Vitor C and Andrusch, Andreas and Seiler, Enrico and Renard, Bernhard Y and Reinert, Knut},
  year = {2018},
  journal = {Bioinformatics},
  doi = {10.1093/bioinformatics/bty567}
}
```
