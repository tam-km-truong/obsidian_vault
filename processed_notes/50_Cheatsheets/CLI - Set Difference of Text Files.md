---
category: cheatsheet
tags:
  - bash
  - cli
  - grep
  - set-operations
source_raw: "[[outer difference of txt file 1 and file 2]]"
status: processed
---

# CLI - Set Difference of Text Files

## Problem
Given two unsorted text files (`file1.txt` and `file2.txt`), extract all lines that exist in `file1.txt` but **do not exist** in `file2.txt`, **without needing to sort either file**.

## TL;DR One-Liner
```bash
grep -Fxv -f file2.txt file1.txt
```

## Technical Breakdown
- `-F` (`--fixed-strings`): Treats lines in `file2.txt` as plain strings rather than regular expressions. This prevents special characters (`.`, `*`, `[`, `]`, `+`) from breaking regex parsing and offers significant speedups.
- `-x` (`--line-regexp`): Matches only whole lines rather than partial substring hits.
- `-v` (`--invert-match`): Inverts the match, returning only lines from `file1.txt` that failed to match anything in `file2.txt`.
- `-f file2.txt`: Uses `file2.txt` as the reference filter dictionary.

## Benchmark vs `comm`
| Method | Requires Sorted Input? | In-Memory Footprint | Speed on 1M Lines |
| :--- | :--- | :--- | :--- |
| `grep -Fxv -f file2 file1` | **No** | Stores `file2` pattern list in RAM | Very fast for moderate lists |
| `comm -23 <(sort f1) <(sort f2)` | **Yes** | Low streaming RAM | Slower due to disk/sort overhead |

## Related Notes
- [[CLI - Pattern Matching & Difference Checking (grep)]] – Full grep options reference
- [[CLI - Stream Editor (sed) Recipes]] – Modifying lines in batch
