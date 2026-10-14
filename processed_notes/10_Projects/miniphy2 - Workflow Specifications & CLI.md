---
category: projects
tags:
  - miniphy2
  - snakemake
  - rust
  - cli
  - hpc
source_raw: "[[miniphy2]]"
status: processed
---

# miniphy2: Workflow Specifications & CLI Reference

## 1. Project Background
- **Tool Name:** `miniphy2` (formerly referenced under working names *Phylord* and *PhyloPack*).
- **Core Role:** Scalable pipeline for phylogenetic tree-based batching and compression of million-genome collections.

---

## 2. CLI Command Syntax

```bash
./miniphy2 compress \
    --output <path_to_output_archive> \
    --list <input_accession_list.txt> \
    --compression <xz|agc|mbgc> \
    --batch-size <size_in_mb> \
    --threads 16
```

### Options & Parameters
- `--output`: Path to generated compressed archive or directory of batches.
- `--list`: Input text file containing one genome file path or accession per line.
- `--compression`: Compression engine (`xz`, `agc`, `mbgc`).
- `--threads`: Parallel CPU worker allocation.

---

## 3. Snakemake Pipeline Dependencies
The automated batching pipeline requires:
- `snakemake` ($\ge 7.0$)
- `ete3` (Tree topology traversal and ladderization)
- `attotree` (Rapid distance-matrix and neighbor-joining tree inference)
- `xopen` (High-performance compressed streaming I/O)

### Standard Execution Command
```bash
snakemake --snakefile workflow/Snakefile \
    --config input_dir=/scratch/ktruong/data/atb/recompressed/ \
    --cores 32 \
    --use-conda
```

---

## 4. SLURM Troubleshooting & Common Failures
- **Error:** `RuleException in rule compress_batch: Command returned non-zero exit status 1.`
- **Cause 1 - Memory Exhaustion:** Large batches exceeding allocated SLURM node RAM during MBGC/AGC dictionary construction.
  - *Fix:* Reduce `--batch-size` or increase `#SBATCH --mem=64G`.
- **Cause 2 - Broken File Paths:** Relative paths in `accessions.txt` missing prefix.
  - *Fix:* Ensure absolute paths or prepending via `sed` (see [[CLI - Stream Editor (sed) Recipes]]).

---

## Related Notes & Experiments
- [[Mathematical Formulation - Order-Preserving Batching]] – Optimization model
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]] – Underlying bin packing code
- [[SLURM Jobs - Active Benchmarking & Recompression Runs]] – Live SLURM job commands
- [[AGC - Assembled Genomes Compressor]] – Downstream compression engine
