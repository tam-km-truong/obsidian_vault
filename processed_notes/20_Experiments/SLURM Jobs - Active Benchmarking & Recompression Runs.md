---
category: experiments
tags:
  - slurm
  - hpc
  - snakemake
  - benchmarks
source_raw: "[[My pending jobs]]"
status: processed
---

# SLURM Jobs: Active Benchmarking & Recompression Runs

## Active Slurm Job Submissions

### 1. Mycobacterium tuberculosis Recompression
```bash
snakemake --snakefile workflow/Snakefile \
    --config input_dir=/scratch/ktruong/data/atb/recompressed/mycobacterium_tuberculosis/ \
    --cores 32 --use-conda
```

### 2. Phylopacking Escherichia coli Reference Set
```bash
phylopack preorder \
    /scratch/ktruong/data/gtdb/s__Escherichia_coli.txt \
    --sketch-size 10000 \
    --output-dir results/ecoli_reorder/
```

### 3. Fixed Fraction Batching Parameter Sweep
Evaluates compression ratio variance across fixed fractional bin capacities ($1\%$, $5\%$, $10\%$, $25\%$ of clade size).

## Related Experiments & Tools
- [[miniphy2 - Workflow Specifications & CLI]]
- [[Mathematical Formulation - Order-Preserving Batching]]
