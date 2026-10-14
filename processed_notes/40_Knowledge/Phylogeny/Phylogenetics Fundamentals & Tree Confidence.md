---
category: knowledge
tags:
  - phylogeny
  - evolution
  - trees
  - confidence
source_raw: "[[Phylogeny]]"
status: processed
---

# Phylogenetics Fundamentals & Tree Confidence

## 1. Tree Topologies & Distance Methods
- **Operational Taxonomic Unit (OTU):** Terminal leaf nodes representing sequenced isolate genomes.
- **Minimum-Evolution Tree:** A tree that minimizes total branch length across all lineages.
- **Parsimonious Tree:** Minimizes the total number of character-state transitions (mutations).

---

## 2. Estimating Tree Confidence & Branch Support
- **Bootstrapping:** Resamples alignment columns or sketch subsets with replacement to measure the percentage of pseudo-replicates that recover a specific node.
- **Jackknifing:** Resamples subsets without replacement (e.g. dropping $50\%$ of characters).
- High bootstrap support ($>80\%$) indicates stable clade separation.

## Related Notes
- [[Attotree - Fast Tree Construction & Troubleshooting]]
- [[Vertical and Horizontal Gene Transfer]]
