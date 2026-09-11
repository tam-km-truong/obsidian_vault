## 1. Check differences using `grep`

### A. Lines in `file1.txt` **not present** in `file2.txt`

```bash
grep -Fvx -f file2.txt file1.txt
```

### B. Lines in `file2.txt` **not present** in `file1.txt`

```bash
grep -Fvx -f file1.txt file2.txt
```

### C. Symmetric difference (IDs present in only one file)

```bash
grep -Fvx -f file2.txt file1.txt
grep -Fvx -f file1.txt file2.txt
```

(You can redirect outputs if needed.)

---

## 2. Explanation of flags (critical for correctness)

- `-F` : fixed strings (no regex; safer and faster for IDs)
    
- `-x` : match the **entire line only**
    
- `-v` : invert match (show non-matching lines)
    
- `-f file` : patterns come from `file`
    

**Without `-x`, substrings will falsely match.  
Without `-F`, IDs containing regex metacharacters will break matching.**

---

## 3. Short `grep` memo (ID comparison–oriented)

```
grep -Ff patterns.txt file.txt     # keep lines matching any pattern
grep -Fvf patterns.txt file.txt    # exclude lines matching any pattern
grep -Fx pattern file.txt          # exact full-line match
grep -Fvx -f A B                   # lines in B not in A
```

---

## 4. Devil’s advocate / caveats

- **Duplicates**: `grep` does not deduplicate. If files contain repeated IDs, output will reflect that.
    
- **Performance**: For very large files, `comm` or `sort | uniq` may be faster and more semantically correct.
    
- **Hidden whitespace**: Trailing spaces or CRLF will cause false differences.
    
- **Ordering**: Output preserves original order, which may obscure systematic differences.
    

If you want a mathematically cleaner set difference, say so; `grep` is pragmatic, not rigorous.