---
category: cheatsheet
tags:
  - bash
  - cli
  - linux
  - benchmarking
source_raw: "[[Command Line]]"
status: processed
---

# CLI - General Shell Utilities & Measuring

## 1. Benchmarking Runtime & Resource Tracking
Add `time` or use GNU `time` for detailed memory usage:
```bash
# Basic execution time
time ls -la

# Detailed memory & CPU measurement (GNU time)
/usr/bin/time -v python3 script.py
```

## 2. Mass Moving & Batch File Reorganization
```bash
# Move multiple directories or files into a single destination
mv source1 source2 source3 destination/

# Move all matched files into parent or sibling folder
mv ./experiments/075_EXPE_compression_files_validation/data/batches/* ./target/
```

## 3. Parallel Compression with pigz
```bash
# Compress file using 16 threads
pigz -p 16 -f myfile.tar

# Decompress fast
pigz -dc myfile.tar.gz | tar -xf -
```

## 4. Disk Usage & Line Counting
```bash
# Sort subdirectories by size
du -sh * | sort -h

# Fast total line count across all text files
wc -l *.txt | tail -n 1
```

## Related Cheatsheets & Tools
- [[CLI - xargs & Parallel Processing]] – Advanced parallel job orchestration
- [[CLI - Fast Basepair Counting]] – Basepair calculation one-liners
- [[CLI - Batch Size & Memory Calculation]] – Calculating total disk usage across TSVs
