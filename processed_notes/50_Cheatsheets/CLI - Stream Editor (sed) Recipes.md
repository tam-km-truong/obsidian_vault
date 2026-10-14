---
category: cheatsheet
tags:
  - bash
  - cli
  - sed
  - text-processing
source_raw: "[[sed command]]"
status: processed
---

# CLI - Stream Editor (sed) Recipes

## TL;DR One-Liner
```bash
# In-place regex substitution across file list
sed -i 's|old_pattern|new_pattern|g' file.txt
```

## Quick Reference / Flags
| Flag / Option | Description | Example |
| :--- | :--- | :--- |
| `-i` / `-i ''` | In-place edit (macOS requires `-i ''` or `gsed -i`) | `sed -i 's/foo/bar/' file.txt` |
| `-e` | Execute multiple expressions in one pass | `sed -e 's/a/b/' -e 's/c/d/'` |
| `s/regex/replacement/g` | Substitute all occurrences on each line | `sed 's/[0-9]/X/g'` |
| `p`, `-n` | Suppress auto-print, print only matching lines | `sed -n 's/pattern/&/p'` |

## Real-World HPC & Bioinformatics Recipes in Vault

### 1. Removing File Extensions (.txt, .hll)
```bash
# Strip .txt extension from filenames
sed 's/\.txt$//' file_list.txt

# Strip .hll extension
sed 's/\.hll$//' sketches.txt
```

### 2. Prepending & Appending Path Prefixes / Suffixes
```bash
# Prepend directory path to every filename
sed 's|^|fasta/|' ls_fasta.txt

# Append line numbers or suffix
sed 's|$|.tar.xz|' accessions.txt
```

### 3. Extracting and Trimming Line Ranges
```bash
# Remove first N lines (skip header)
sed '1,10d' input.tsv

# Print only lines 100 to 150
sed -n '100,150p' large_file.txt
```

### 4. Replacing Tab Separators and Whitespace
```bash
# Convert tabs to commas
sed 's/\t/,/g' table.tsv

# Collapse multiple spaces into single tab
sed 's/  */\t/g' unformatted.txt
```

## Related Cheatsheets & Tools
- [[CLI - xargs & Parallel Processing]] – Used with sed in pipeline batching
- [[CLI - Pattern Matching & Difference Checking (grep)]] – Filtering before stream editing
- [[CLI - Batch Size & Memory Calculation]] – Real workflow combining sed, xargs, and awk
