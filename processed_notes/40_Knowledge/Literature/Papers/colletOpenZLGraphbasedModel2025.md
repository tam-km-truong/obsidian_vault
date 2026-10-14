---
category: literature
citekey: "colletOpenZLGraphbasedModel2025"
title: "OpenZL: A Graph-Based Model for Compression"
aliases:
  - "OpenZL: A Graph-Based Model for Compression"
  - "Collet et al. (2025)"
  - "@colletOpenZLGraphbasedModel2025"
authors:
  - "Collet, Yann"
  - "Terrell, Nick"
  - "Handte, W Felix"
  - "Rozenblit, Danielle"
  - "Zhang, Victor"
  - "Zhang, Kevin"
  - "Goldschlag, Yaelle"
  - "Lee, Jennifer"
  - "Riegel, Daniel"
  - "Angelov, Stan"
  - "Rotem, Nadav"
year: 2025
journal: "arXiv [cs.IR]"
doi: ""
topic: "Sequence Compression"
tags:
  - literature
  - paper
  - sequence-compression
status: unread
---

# OpenZL: A Graph-Based Model for Compression

- **Authors:** Collet et al.
- **Year:** 2025
- **Journal / Venue:** *arXiv [cs.IR]*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@colletOpenZLGraphbasedModel2025)

## Abstract
> Research in general-purpose lossless compression over the last decade has largely found improvements in compression ratio that come at great cost to resource utilization and processing throughput. However, most production workloads require high throughput and low resource utilization, so most research systems have seen little adoption. Instead, real world improvements in compression are increasingly often realized by building application-specific compressors which can exploit knowledge about the structure and semantics of the data being compressed. These systems easily outperform even the best generic compressors, but application-specific compression schemes are not without drawbacks. They are inherently limited in applicability and are difficult to maintain and deploy. We show that these challenges can be overcome with a new way of thinking about compression. We propose the ``graph model'' of compression, a new theoretical framework for representing compression as a directed acyclic graph of modular codecs. This motivates OpenZL, an implementation of this model that compresses data into a self-describing wire format, any configuration of which can be decompressed by a universal decoder. OpenZL's design enables rapid development of tailored compressors with minimal code, its universal decoder eliminates deployment lag, and its investment in a well-vetted standard component library minimizes security risks. Experimental results demonstrate that OpenZL achieves superior compression ratios and speeds compared to state-of-the-art general-purpose compressors on a variety of real-world datasets. Internal deployments at Meta have also shown consistent improvements in size and/or speed, with development timelines reduced from months to days. OpenZL thus represents an advance in practical, scalable, and maintainable data compression for modern data-intensive applications.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- Relates to: [[10_Projects/Research Project & Publication Plan]]

## BibTeX Citation
```bibtex
@article{colletOpenZLGraphbasedModel2025,
  title = {OpenZL: A Graph-Based Model for Compression},
  author = {Collet, Yann and Terrell, Nick and Handte, W Felix and Rozenblit, Danielle and Zhang, Victor and Zhang, Kevin and Goldschlag, Yaelle and Lee, Jennifer and Riegel, Daniel and Angelov, Stan and Rotem, Nadav},
  year = {2025},
  journal = {arXiv [cs.IR]},
  doi = {}
}
```
