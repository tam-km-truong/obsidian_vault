---
category: knowledge
tags:
  - genomics
  - quality-control
  - qc
  - criteria
source_raw: "[[High Quality Genomes]]"
status: processed
---

# High Quality Genomes: Quality Control Standards

## Standard Criteria for High-Quality Bacterial Assemblies
Assemblies accepted into high-quality benchmark subsets (e.g. AllTheBacteria HQ, GTDB representative sets) must satisfy:

| Metric | Required Threshold | Rationale |
| :--- | :--- | :--- |
| **Genome Size** | $100\text{ kb} \le \text{Size} \le 15\text{ Mb}$ | Excludes truncated reads or poly-microbial co-assemblies |
| **Contig Count** | $\le 2,000$ contigs | Avoids fragmented, uninformative short contig assemblies |
| **N50 Statistic** | $\ge 5,000\text{ bp}$ | Ensures sufficient contiguity for gene identification |
| **Taxonomic Purity** | Majority species $>99\%$ abundance | Filters out chimeric or contaminated isolate sequencing runs |

## Related Notes
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]] – Applies these thresholds
- [[NCBI Datasets CLI Reference]] – Fetching filtered metadata
