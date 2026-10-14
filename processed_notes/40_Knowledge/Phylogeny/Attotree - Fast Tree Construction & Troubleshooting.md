---
category: knowledge
tags:
  - attotree
  - phylogeny
  - distance-methods
  - snakemake
source_raw: "[[Attotree]]"
status: processed
---

# Attotree: Rapid Phylogenetic Tree Construction & Post-Processing

## Overview
**Attotree** estimates neighbor-joining phylogenetic trees directly from raw genome FASTA files using rapid sketching (Mash / dashing2) to compute pairwise Jaccard/ANI distances without sequence alignment.

---

## Tree Post-Processing Pipeline
Raw output Newick trees often require ladderization, outgroup rooting, and internal node labeling before computing preorder traversals:

```bash
python python_scripts/postprocess_tree.py \
    --standardize \
    --midpoint-outgroup \
    --ladderize \
    --name-internals \
    --leaves_order order.txt \
    --input tree.nwk \
    --output processed_tree.nwk
```

### Post-Processing Steps
1. `--standardize`: Cleans non-standard Newick branch symbols and whitespace.
2. `--midpoint-outgroup`: Roots the tree at the midpoint of the longest path.
3. `--ladderize`: Orders children nodes deterministically by clade size.
4. `--name-internals`: Assigns unique IDs to internal ancestral nodes.
5. `--leaves_order`: Dumps the exact 1D linearized leaf traversal.

---

## Snakemake Error Resolution
- **Error:** `CalledProcessError: Command '... attotree ...' returned non-zero exit status 1`
- **Cause:** Corrupt or empty FASTA files in input batch, or Newick file parser rejecting special characters in leaf names.
- **Solution:** Sanitize accession strings, removing spaces and semicolons before passing to Attotree.

## Related Notes
- [[Mashtree - Rapid Comparative Genomics]] – Alternative neighbor-joining tool
- [[Phylogenetics Fundamentals & Tree Confidence]] – Theoretical concepts
- [[miniphy2 - Workflow Specifications & CLI]] – Uses Attotree internally
