---
category: presentations
conference: SeqBIM (Séquences en Bioinformatique, Informatique et Mathématiques)
year: 2025
tags:
  - bioinformatics
  - pangenomics
  - compression
  - presentation
  - seqbim
source_raw: "[[script seqbim 2025]]"
status: processed
---

# SeqBIM 2025: Optimized Phylogenetic Batching for Compressed Genomic Storage

## Executive Summary
Spoken presentation script and slide outline delivered at SeqBIM 2025. Explains the computational algorithms for linearizing large phylogenetic trees and dynamically batching bacterial isolates for archival storage and cloud access.

---

## Slide-by-Slide Script & Key Takeaways

### Slide 1: Title & Introduction
- **Presenter:** Tom Truong (Ph.D. Student, GenScale / INRIA / IRISA).
- **Core Thesis:** How to store and query millions of bacterial genomes sustainably using phylogenetic ordering and dynamic batching.

### Slide 2: The Data Tsunami in Bacterial Genomics
- Highlights the shift from reference genomes to massive isolate collections (e.g., 661k collection, AllTheBacteria with 1.9M assemblies).
- The storage footprint exceeds petabytes if uncompressed, making public dissemination costly.

### Slide 3: The Trade-Off Frontier
- **Independent gzip:** Good access, poor compression ($>10\times$ larger).
- **Monolithic AGC/MBGC:** Excellent compression ($10-50\times$), but querying a single isolate requires high memory and long latency.
- **The Sweet Spot:** Batching along phylogenetic preorders to get monolithic compression ratios with independent retrieval performance.

### Slide 4: Algorithmic Pipeline
1. Sketching genomes with HyperLogLog / MinHash.
2. Distance matrix computation and tree inference using [[Attotree]].
3. Order-preserving bin packing with k-mer thresholding.

### Slide 5: Experimental Results
- Validated across *Salmonella enterica*, *Escherichia coli*, and *Mycobacterium tuberculosis* collections.
- Demonstration of compression ratio improvements of up to $40\%$ over standard alphabetical/accession sorting.

---

## Related Notes & Vault Links
- [[DSB 2025 - Phylogenetic Batching Presentation]] – Earlier talk version at DSB
- [[Mathematical Formulation - Order-Preserving Batching]] – Full mathematical model
- [[Allthebacteria]] – Description of the 1.9M dataset
- [[miniphy2 - Workflow Specifications & CLI]] – Pipeline implementation
