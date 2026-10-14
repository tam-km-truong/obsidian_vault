---
category: knowledge
tags:
  - dashing2
  - hyperloglog
  - sketching
  - kmer
source_raw: "[[dasing and dashing2]]"
status: processed
---

# dashing2: Fast Genomic Sketching with HyperLogLog & Set Operations

## Overview
**dashing2** is a fast genomic sketching tool using HyperLogLog (HLL) and BagMinHash sketches. It allows ultra-fast distance matrix estimation and k-mer union computations across millions of genomes.

---

## Key CLI Invocations
```bash
./dashing2_savx2 sketch \
    -s \
    -N \
    -o ./output/result \
    -F ./data/mycoplasma_pneumoniae__01.txt \
    --kmer-size 31 \
    --spacing 10
```

### Options Explained
- `-s`: Sketch mode.
- `-N`: Normalize counts.
- `-o`: Output destination.
- `-F <file_list>`: Read fasta inputs from list.
- `--spacing <N>`: Spaced k-mers for higher sensitivity.

## Related Notes
- [[Mash & MinHash Sketching]] – Classic MinHash comparison
- [[Attotree - Fast Tree Construction & Troubleshooting]] – Uses dashing2 sketches
