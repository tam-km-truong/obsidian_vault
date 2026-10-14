---
category: knowledge
tags:
  - ani
  - orthology
  - genomics
  - evolution
source_raw: "[[Average nucleotide identity]]"
status: processed
---

# Average Nucleotide Identity (ANI) & Orthology

## 1. Orthology vs Paralogy
- **Orthologs:** Genes in different species that evolved from a common ancestral gene via **speciation**. Identified by bidirectional best hits (BBH).
- **Paralogs:** Genes related by **duplication events** within a genome.

---

## 2. Average Nucleotide Identity (ANI)
- Measures global sequence conservation across shared orthologous genes.
- **Species Boundary:** $95\%$ to $96\%$ ANI corresponds to the classical $70\%$ DNA-DNA hybridization threshold for defining prokaryotic species.

## Related Notes
- [[Mash & MinHash Sketching]] – Mash distance estimates $1 - \text{ANI}$
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]] – Species clusters grouped at $95\%$ ANI
