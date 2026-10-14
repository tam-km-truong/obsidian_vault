---
category: knowledge
tags:
  - genouest
  - galaxy
  - assembly
  - annotation
source_raw: "[[GenOuest Formation Assemblage et annotation de genome]]"
status: processed
---

# GenOuest: Genome Assembly & Annotation Workflow

## Context & Training Overview
Training modules delivered at GenOuest / Galaxy Training Network on de novo bacterial genome assembly, assembly evaluation, and structural annotation.

## Standard Bacterial Assembly Stack
1. **Raw Read Quality Control:** FastQC, Trimmomatic / fastp.
2. **De Novo Assembly:** Unicycler, SPAdes (De Bruijn Graph approach).
3. **Assembly Assessment:** QUAST (contig counts, N50, L50, GC content), CheckM (completeness and contamination).
4. **Prokaryotic Annotation:** Prokka, Bakta (CDS, tRNA, rRNA identification).

## Related Notes
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]] – Scaled application of uniform assembly
- [[High Quality Genomes - Quality Control Standards]] – QC criteria
