---
category: knowledge
tags:
  - mbgc
  - compression
  - pangenomics
  - tools
source_raw: "[[MBGC]]"
status: processed
---

# MBGC: Multiple Bacterial Genome Compressor

## Overview
**MBGC** is an ultrafast compressor specifically optimized for large collections of bacterial genomes of the same species. It achieves compression ratios comparable to or better than AGC while often exhibiting faster decompression and lower memory requirements.

---

## CLI Execution Recipe
```bash
for f in data/batches/subdir_1/*; do
    echo "Running MBGC on $f..."
    mbgc c -m 3 -t 25 $f results/mbgc/$(basename $f .txt).mbgc
done
```

### Key Options
- `c`: Compress mode.
- `-m <level>`: Compression mode (1=fast, 2=balanced, 3=maximum compression).
- `-t <threads>`: Number of parallel worker threads (e.g. `-t 25`).
- `$f`: Text file listing fasta files to include in the batch.

## Comparison: MBGC vs AGC
| Feature | MBGC | AGC |
| :--- | :--- | :--- |
| **Compression Ratio** | Extremely high on clonal isolates | High on divergent species |
| **Compression Speed** | Very fast multithreaded | Moderate |
| **Random Access** | Batch-level | Sub-sequence and contig-level |

## Related Notes
- [[AGC - Assembled Genomes Compressor]] – Contig-level random access compressor
- [[Mathematical Formulation - Order-Preserving Batching]] – Optimization formulation
