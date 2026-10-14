---
category: cheatsheet
tags:
  - bash
  - cli
  - hpc
  - parallel
source_raw: "[[xargs]]"
status: processed
---

# CLI - xargs & Parallel Processing

## TL;DR One-Liner
Run commands over multiple items in parallel using isolated subshells:
```bash
ls *.tar.xz | xargs -n 1 -P 8 -I{} sh -c 'echo "Processing {}"; pigz -dc {} | process'
```

## Quick Reference / Options
| Flag / Option | Description | Example |
| :--- | :--- | :--- |
| `-P <N>` | Run up to `N` processes concurrently | `xargs -P 8` |
| `-n <max-args>` | Use at most `max-args` arguments per command line | `xargs -n 1` |
| `-I {}` | Replace occurrences of `{}` with input line | `xargs -I {} mv {} dest/` |
| `-0`, `--null` | Input items are terminated by a null character (handles spaces safely) | `find . -name "*.fa" -print0 \| xargs -0 rm` |
| `-d <delim>` | Set custom input delimiter | `xargs -d '\n'` |

## Real-World Recipes & HPC Workflows

### 1. Parallel Batch Extraction & Recompression of Genomic Archives
Extract `.fa` files from `.tar.xz` archives, recompress with `pigz`, and collect in destination directory using isolated temporary folders:

```bash
mkdir -p /scratch/ktruong/data/atb/uncompressed/salmonella_enterica/

ls data/atb/by_species/salmonella_enterica/*.tar.xz | xargs -P 3 -I{} sh -c '
  archive="{}"
  echo "Processing tarball: $archive"
  tmpdir=$(mktemp -d /scratch/ktruong/.tmp/tmp.XXXXXXXXXX)
  
  # Extract and strip top-level directory
  tar -Jxf "$archive" --strip-components=1 -C "$tmpdir"
  
  # Parallel gzip compression
  pigz -f "$tmpdir"/*.fa -p 10
  
  # Move to destination and clean up
  mv "$tmpdir"/*.fa.gz /scratch/ktruong/data/atb/uncompressed/salmonella_enterica/
  rm -rf "$tmpdir"
  echo "$archive completed"
'
```

- **Why `mktemp -d` inside the subshell?** Parallel jobs running concurrently will collide if extracting into a shared directory. Creating an isolated temporary directory per job ensures thread safety and zero filename conflicts.
- **Tuning `-P` and `-p`:** If each job uses `pigz -p 10` threads and `xargs -P 3` runs 3 jobs in parallel, total CPU consumption is $3 \times 10 = 30$ cores. Always ensure $(-P \times -p) \le \text{allocated SLURM CPUs}$.

### 2. Fast Size & Line Calculations with xargs
Used in conjunction with `du` and `awk` to calculate memory footprint across file lists:
```bash
sed 's|^|fasta/|' ls_fasta.txt | xargs -d '\n' du -sb | awk '{total += $1} END {print total}'
```

## Related Cheatsheets & Tools
- [[Command Line]] – General Linux & shell productivity tricks
- [[Fast size calculation]] – Calculating aggregate sizes across batch lists
- [[Count basepair]] – Parallel sequence counting pipelines
- [[Allthebacteria]] – Large-scale bacterial genome dataset processed via these scripts
