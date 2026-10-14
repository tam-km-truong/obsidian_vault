---
category: cheatsheet
tags:
  - bash
  - linux
  - cli
source_raw: "[[Advanced linux]]"
status: processed
---

# CLI - Advanced Linux One-Liners

## 1. Inspecting File Formats & Encoding
```bash
# Determine actual file format (independent of extension)
file myfile

# Check MIME type and encoding
file -i myfile.txt
```

## 2. Slicing & Context Matching with grep
```bash
# Search inverted case-insensitive count
grep -ivcr "pattern" file.fa

# Extract matches with surrounding context
grep -A 3 "Error" slurm.log    # 3 lines After
grep -B 2 "Error" slurm.log    # 2 lines Before
grep -C 2 "Error" slurm.log    # 2 lines Context (before and after)
```

## 3. Removing Duplicates and Consecutive Lines
```bash
# Remove adjacent duplicates
uniq file.txt

# Count frequencies of sorted items
sort file.txt | uniq -c | sort -nr
```

## 4. Relational Joins on Tabular Files
```bash
# Join two sorted files on common key (column 1)
join -t $'\t' -1 1 -2 1 sorted_file1.tsv sorted_file2.tsv
```

## Related Cheatsheets & Tools
- [[CLI - Pattern Matching & Difference Checking (grep)]] – Dedicated grep reference
- [[CLI - Stream Editor (sed) Recipes]] – Stream editing and substitution
- [[CLI - General Shell Utilities & Measuring]] – General productivity tools
