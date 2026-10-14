---
category: knowledge
tags:
  - mashtree
  - mash
  - phylogeny
  - trees
source_raw: "[[Mashtree]]"
status: processed
---

# Mashtree: Rapid Comparative Genomics & Tree Inference

## In a Nutshell
**Mashtree** builds neighbor-joining phylogenetic trees directly from raw genomic sequences (FASTQ or FASTA) by calculating pairwise distance matrices using **MinHash sketches** via [[Mash & MinHash Sketching|Mash]] and constructing trees with QuickTree.

---

## Core Algorithm
1. Computes a MinHash sketch (default: $s = 10,000$ hashes, $k = 21$) for each genome.
2. Estimates pairwise mutation rates (Mash distances $\approx 1 - \text{ANI}$).
3. Feeds the distance matrix into QuickTree / Neighbor-Joining.

## Advantages & Limitations
- **Speed:** Creates trees for hundreds of bacterial isolates in seconds.
- **Accuracy:** Highly accurate for species-level clustering and clade separation; less reliable for resolving very deep evolutionary branches.

## Related Notes
- [[Mash & MinHash Sketching]] – The underlying MinHash distance algorithm
- [[Attotree - Fast Tree Construction & Troubleshooting]] – Alternative tree inference engine
