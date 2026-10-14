---
category: cheatsheet
tags:
  - bash
  - cli
  - genomics
  - fasta
source_raw: "[[Count basepair]]"
status: processed
---

# CLI - Fast Basepair Counting

## Problem
Quickly count total nucleotide basepairs across multiple compressed `.tar.xz` or `.fa.gz` files without writing uncompressed sequence data to disk.

## TL;DR Pipeline
```bash
total=0
for f in ./*.tar.xz; do
    count=$(tar -xOf "$f" | grep -v '^>' | tr -d '\n' | wc -c)
    echo "$count $f"
    total=$((total + count))
done
echo "Total basepairs: $total"
```

## Pipeline Stages Breakdown
1. `tar -xOf "$f"`: Extracts archive contents directly to `stdout` without unpacking files to disk.
2. `grep -v '^>'`: Strips FASTA header lines (lines starting with `>`).
3. `tr -d '\n'`: Deletes newline characters so only raw nucleotide letters (A, C, G, T, N) remain.
4. `wc -c`: Counts bytes/characters, directly yielding the basepair count.

## High-Performance Alternative with seqkit
```bash
seqkit stats *.fa.gz -T | awk '{sum += $5} END {print sum}'
```

## Related Cheatsheets & Tools
- [[CLI - xargs & Parallel Processing]] – Parallelizing archive processing
- [[CLI - Batch Size & Memory Calculation]] – Calculating disk volume and runtime
- [[Allthebacteria]] – Dataset on which basepair counting was performed
