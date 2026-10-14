---
category: cheatsheet
tags:
  - bash
  - hpc
  - experiments
  - agc
source_raw: "[[Command history]]"
status: processed
---

# CLI - Random Access & Dustbin Batching History

## Context & Purpose
Reference log of execution commands used in experiment `086_EXPE_dustbin_tradeoff_ran_access` to evaluate trade-offs between AGC random access speed and compressed archive size across dustbin batches.

## Execution Command Log
```bash
# Run AGC archive creation and benchmark timing across 10k dustbin batches
for f in experiments/086_EXPE_dustbin_tradeoff_ran_access/data/batches/dustbin_b10k*; do
    ref=$(head -n 1 $f)
    galitime -n $(basename $f) agc create -a -b 500 -s 50 -i $f -o $(basename $f).agc $ref
done
```

## Parameters Explained
- `ref=$(head -n 1 $f)`: Sets the first genome accession in the batch as the reference sequence for AGC compression.
- `galitime -n ...`: Benchmarks CPU time and peak RAM usage per batch.
- `-b 500`: AGC segment/block parameter.
- `-s 50`: AGC sketch/k-mer parameter.

## Related Experiments & Tools
- [[AGC - Assembled Genomes Compressor]] – Complete AGC reference & options
- [[SLURM Jobs - Active Benchmarking & Recompression Runs]] – Active benchmark jobs
- [[Mathematical Formulation - Order-Preserving Batching]] – Theoretical batching bounds
