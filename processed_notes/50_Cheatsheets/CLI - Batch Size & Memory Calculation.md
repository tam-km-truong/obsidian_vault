---
category: cheatsheet
tags:
  - bash
  - cli
  - awk
  - hpc
source_raw: "[[Fast size calculation]]"
status: processed
---

# CLI - Batch Size & Memory Calculation

## Problem
Given a large list of FASTA file paths, calculate cumulative disk size, track processing speed in real-time, and compute remaining time estimation (ETA) for large-scale pangenome batching.

## Production Script (xargs + du + awk)
```bash
sed 's|^|fasta/|' ls_fasta.txt | xargs -d '\n' du -sb | awk -v total=715000 '
BEGIN {
    start_time = systime();
}
{
    sum += $1
    count++
    if (count % 1000 == 0) {
        now = systime()
        elapsed = now - start_time
        rate = count / (elapsed > 0 ? elapsed : 1)
        remaining = total - count
        eta = (rate > 0) ? int(remaining / rate) : 0
        printf("Processed %d / %d (%.2f%%) | Sum: %.2f GB | Rate: %.1f files/s | ETA: %d s\n",
               count, total, (count/total)*100, sum / (1024^3), rate, eta)
    }
}
END {
    printf("FINAL: Processed %d files | Total Size: %.2f GB\n", count, sum / (1024^3))
}'
```

## Key Mechanisms
- `sed 's|^|fasta/|'`: Prepend the relative directory prefix to accessions in `ls_fasta.txt`.
- `xargs -d '\n' du -sb`: Batches file paths into `du -sb` (apparent byte size) efficiently without spawning one process per file.
- `awk systime()`: Built-in timestamp calculation for estimating rolling throughput and ETA without external monitoring daemons.

## Related Cheatsheets & Tools
- [[CLI - Stream Editor (sed) Recipes]] – Text prepending and filtering
- [[CLI - xargs & Parallel Processing]] – High-throughput pipeline batching
- [[Mathematical Formulation - Order-Preserving Batching]] – Optimization of batch bin sizes
