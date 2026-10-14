---
category: experiments
experiment_id: "078"
tags:
  - experiment
  - z-complexity
  - lz77
  - compression
source_raw: "[[078]]"
status: processed
---

# EXP 078: Calculating Number of LZ77 Phrases ($z$)

## Objective
Compute the number of LZ77 parse phrases ($z$) to quantify the repetitive structure and theoretical compressibility limit of genome batches.

## Execution Script
```bash
# Decompress and compute phrase complexity across batches
for f in experiments/078_EXPE_comp_measure_z_2/data/batches/*.txt; do
    echo "Processing $f..."
    python experiments/078_EXPE_comp_measure_z_2/scripts/parse_and_compute.py "$f"
done
```

## Related Experiments & Notes
- [[EXP_075 - Seqkit Hashing and MBGC Validation]]
- [[Genomic Data Compression Survey (zstd, AGC, MBGC)]]
