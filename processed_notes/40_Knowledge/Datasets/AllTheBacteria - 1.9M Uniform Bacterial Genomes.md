---
category: knowledge
tags:
  - dataset
  - genomics
  - bacteria
  - gtdb
  - qc
source_raw: "[[Allthebacteria]]"
status: processed
---

# AllTheBacteria: 1.9M Uniformly Processed Bacterial Genomes

## Overview
**AllTheBacteria** is a comprehensive, standardized collection of ~1.9 million bacterial genome assemblies derived from all publicly deposited Illumina sequencing runs in the European Nucleotide Archive (ENA) / SRA as of 2023. It expands upon the earlier **661k dataset** (2018) while enforcing uniform assembly, quality control, and taxonomic annotation.

---

## Core Contributions & Standards
1. **Uniform Assembly Pipeline:** All isolates were assembled using the exact same pipeline (Shovill / SPAdes), eliminating methodological biases across laboratories.
2. **Quality Control (QC) Metrics:**
   - Genome size thresholds: $100\text{ kb} \le \text{size} \le 15\text{ Mb}$.
   - Contig limit: $\le 2,000$ contigs.
   - Assembly N50: $\ge 5,000\text{ bp}$.
   - Taxonomic contamination filtering via CheckM and mash screen.
3. **Standardized GTDB Taxonomy:** Every assembly is classified under Genome Taxonomy Database (GTDB) nomenclature.
4. **Uniform K-mer Sketches:** Precomputed MinHash / Sourmash sketches and search indexes for rapid pangenomic analysis.

---

## Access & Data Formats in Vault
- Raw tarballs are stored by species in `.tar.xz` archives (e.g. `data/atb/by_species/salmonella_enterica/*.tar.xz`).
- Batch extraction and compression pipeline: see [[CLI - xargs & Parallel Processing]].
- Preorder traversal and recompression: see [[DSB 2025 - Phylogenetic Batching Presentation]].

## Related Notes & Datasets
- [[High Quality Genomes - Quality Control Standards]] – QC criteria used in ATB
- [[miniphy2 - Workflow Specifications & CLI]] – Tool benchmarking ATB recompression
- [[AGC - Assembled Genomes Compressor]] – Compressor tested on ATB isolates
