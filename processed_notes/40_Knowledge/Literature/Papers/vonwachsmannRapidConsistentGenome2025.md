---
category: literature
citekey: "vonwachsmannRapidConsistentGenome2025"
title: "Rapid and Consistent Genome Clustering at the Scale of Millions of MAGs and Isolates"
aliases:
  - "Rapid and Consistent Genome Clustering at the Scale of Millions of MAGs and Isolates"
  - "von Wachsmann et al. (2025)"
  - "@vonwachsmannRapidConsistentGenome2025"
authors:
  - "von Wachsmann, Johanna"
  - "Lorenz, Leonie"
  - "Russell, Matt"
  - "Gurbich, Tatiana"
  - "Rodriguez-Bouza, Victor"
  - "Horsfield, Samuel"
  - "Lees, John A"
  - "Finn, Robert D"
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

# Rapid and Consistent Genome Clustering at the Scale of Millions of MAGs and Isolates

- **Authors:** von Wachsmann et al.
- **Year:** 2025
- **Journal / Venue:** *bioRxiv*
- **Links:** [Open in Zotero Desktop](zotero://select/items/@vonwachsmannRapidConsistentGenome2025)

## Abstract
> Abstract Bacterial genome databases now exceed 7 million assemblies; however, the massive redundancy and limited scalability of existing tools create bottlenecks for large-scale analyses. Current clustering methods struggle beyond a few thousand genomes, making database-wide organisation computationally infeasible. Here, we present gemsparcl, a tool that clusters bacterial genomes at species-level resolution over 400 faster than existing methods. We developed sketchlib.rust, implementing one-permutation MinHash with densification in binned sketches to accelerate all-versus-all comparisons. Combined with distance correction of incomplete metagenome-assembled genomes (MAGs) for accurate distance estimation and network-based quality filtering to edges, gemsparcl clusters genomes into biologically coherent species-level groups. We clustered 2.2 million bacterial genomes (1.86 million isolates and 360,000 MAGs) into 15,837 species-level genomic cohesive units (GCUs) in 12 hours using 32 cores and less than 64GB of memory. The method achieves 99.8% species purity on high-quality isolates while maintaining accuracy across mixed-quality datasets. This advance enables routine database maintenance for resources like MGnify, as well as reference-free microbiome analysis across millions of genomes, and database-wide metagenomics studies that were previously impossible due to computational constraints. Gemsparcl transforms bacterial genome organisation from a months-long challenge requiring high-performance computing into an overnight analysis on standard hardware.

## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
- [[Mash & MinHash Sketching]]
- [[Rust - Syntax & Attribute Cheatsheet]]

## BibTeX Citation
```bibtex
@article{vonwachsmannRapidConsistentGenome2025,
  title = {Rapid and Consistent Genome Clustering at the Scale of Millions of MAGs and Isolates},
  author = {von Wachsmann, Johanna and Lorenz, Leonie and Russell, Matt and Gurbich, Tatiana and Rodriguez-Bouza, Victor and Horsfield, Samuel and Lees, John A and Finn, Robert D},
  year = {2025},
  journal = {bioRxiv},
  doi = {}
}
```
