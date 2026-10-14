---
category: cheatsheet
tags:
  - bash
  - cli
  - split
  - hpc
source_raw: "[[split and gsplit]]"
status: processed
---

# CLI - File Splitting (split & gsplit)

## TL;DR One-Liners
```bash
# Split file into exactly 6 equal line-chunks with numeric suffixes
split -n l/6 -d -a 2 input.txt part_

# Split by exact line count (e.g., 10,000 lines per batch)
split -l 10000 -d input.txt batch_
```

## Quick Reference / Options
| Flag | Description | Example |
| :--- | :--- | :--- |
| `-n l/<N>` | Split into `N` chunks without splitting individual lines | `split -n l/10 file.txt` |
| `-l <N>` | Split every `N` lines | `split -l 5000 file.txt` |
| `-d` | Use numeric suffixes (`00`, `01`, `02`) instead of alphabetical | `split -d file.txt chunk_` |
| `-a <N>` | Length of suffix digits (default 2, e.g. `00..99`) | `split -a 3 file.txt chunk_` |
| `--additional-suffix=<ext>` | Append extension to split output files | `--additional-suffix=.txt` |

## macOS vs Linux (`gsplit` vs `split`)
macOS ships with BSD `split`, which does not support `-n l/N` or `--additional-suffix`. Install GNU coreutils:
```bash
brew install coreutils
# Use gsplit instead of split
gsplit -n l/6 -d --additional-suffix=.txt input.txt batch_
```

## Real-World SLURM & Batching Use Cases in Vault
When partitioning large collections of bacterial genomes (e.g. GTDB, AllTheBacteria) across array jobs:
```bash
# Partition 100,000 genome accessions into 10 SLURM array task inputs
gsplit -n l/10 -d -a 2 --additional-suffix=.txt accessions.txt slurm_batch_
```

## Related Cheatsheets & Tools
- [[CLI - xargs & Parallel Processing]] – Feeding split batches into parallel workers
- [[CLI - Batch Size & Memory Calculation]] – Calculating volume before splitting
- [[Mathematical Formulation - Order-Preserving Batching]] – The mathematical formulation behind optimal batch partitioning
