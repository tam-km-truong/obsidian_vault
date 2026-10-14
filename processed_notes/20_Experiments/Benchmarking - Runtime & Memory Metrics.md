---
category: experiments
tags:
  - benchmarking
  - runtime
  - memory
  - metrics
source_raw: "[[benchmark runtime]]"
status: processed
---

# Benchmarking: Runtime & Memory Measurement Protocols

## Metrics Tracked
- **Wall-clock Time:** Total elapsed execution time per tool.
- **CPU Time:** User and system CPU seconds across multithreaded runs.
- **Peak Resident Set Size (Max RSS):** Maximum physical RAM allocated during dictionary creation.
- **Average Time Per Accession:** $\frac{\text{Total Time}}{\text{Genome Count}}$.

## Measurement Protocol
```bash
/usr/bin/time -v -o benchmark.log ./miniphy2 compress ...
```

## Related Notes
- [[CLI - General Shell Utilities & Measuring]]
- [[SLURM Jobs - Active Benchmarking & Recompression Runs]]
