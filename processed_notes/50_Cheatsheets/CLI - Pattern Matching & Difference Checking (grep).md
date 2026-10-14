---
category: cheatsheet
tags:
  - bash
  - cli
  - grep
  - set-operations
source_raw: "[[grep memo]]"
status: processed
---

# CLI - Pattern Matching & Difference Checking (grep)

## TL;DR One-Liners
```bash
# Fast outer difference: Lines in file1.txt NOT present in file2.txt (no sorting required)
grep -Fvx -f file2.txt file1.txt

# Search fixed patterns from an ID list in compressed fasta
pigz -dc all_sequences.fa.gz | grep -F -f target_ids.txt
```

## Quick Reference / Flags
| Flag | Description | Purpose |
| :--- | :--- | :--- |
| `-F` | `--fixed-strings` | Treats pattern as literal string (disables regex for speed) |
| `-x` | `--line-regexp` | Matches only whole lines |
| `-v` | `--invert-match` | Selects non-matching lines (negation) |
| `-f <file>` | `--file=<file>` | Read search patterns from a file, one per line |
| `-c` | `--count` | Suppress normal output; print count of matching lines |
| `-i` | `--ignore-case` | Case-insensitive matching |
| `-A <N>`, `-B <N>`, `-C <N>` | Context lines | Print N lines After, Before, or Context around match |

## Real-World HPC & Bioinformatics Recipes in Vault

### 1. Set Difference Between Genomic ID Lists (File 1 Minus File 2)
Fast difference without needing `sort` or `comm`:
```bash
# Find accessions present in file1.txt that are absent from file2.txt
grep -Fxv -f file2.txt file1.txt > unique_to_file1.txt
```
- **Why this works:** `-f file2.txt` loads patterns from file2; `-F` treats them as fixed strings; `-x` forces full-line matching; `-v` inverts to keep only lines not found in file2.

### 2. Extracting Specific IDs from Tabular / FASTA Headers
```bash
# Grep exact matching headers from list of IDs
grep -F -f candidate_accessions.txt gtdb_metadata.tsv > selected_metadata.tsv
```

### 3. Counting Inverted Headers in FASTA
```bash
# Count basepairs while excluding headers
tar -xOf archive.tar.xz | grep -v '^>' | tr -d '\n' | wc -c
```

## Related Cheatsheets & Tools
- [[CLI - Set Difference of Text Files]] – Dedicated guide to file subtraction
- [[CLI - Fast Basepair Counting]] – Using grep to strip FASTA headers
- [[CLI - Stream Editor (sed) Recipes]] – Line editing after matching
