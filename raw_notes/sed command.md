You're using `sed` effectively for string editing in text processing! Here's a breakdown of each command you listed and a **TL;DR-style** summary you can refer to for future `sed` use:

---

### ✅ 1. Prepend a path to each line (macOS style)

```bash
sed -i '' 's/^/\/projects\/reall\/tam\/data\/661k\/uncompressed_fastas\//' input.txt
```

- **`-i ''`**: in-place editing (macOS)
    
- **`s/^/.../`**: add content to the beginning of each line
    
- Slashes in the path must be escaped: `\/`
    /projects/reall/tam/data/661k/uncompressed_fastas/
---

### ✅ 2. Remove `.txt` from lines

```bash
sed 's/\.txt//g' file.txt
```

- **`g`** = global: remove every `.txt` in each line
    
- Useful to strip extensions
    

---

### ✅ 3. Add prefix and suffix in one `sed`

```bash
sed -i '' 's|^|/Users/ktruong/data/661k/hll_sketches_661k/|; s|$|.fa.gz.w.31.spacing.10.hll|' yourfile.txt
```

- **`s|^|...|`** = prepend
    
- **`s|$|...|`** = append
    
- Uses `|` instead of `/` as delimiter to avoid escaping slashes
    

---

### ✅ 4. Complex `tail` + `sed` + `grep` pipeline

```bash
tail -n 1 *_card.txt | \
sed 's/^==>.*<==//;s/^[ \t]*//' | \
grep -v '^$' | \
sed 's/\.hll//g' | \
sed 's/\dashing_results\///g' > distinct_kmers_count
```

This pipeline does the following:

1. `tail -n 1 *_card.txt`: Get the last line of each file
    
2. `sed 's/^==>.*<==//'`: Remove header lines like `==> filename.txt <==`
    
3. `sed 's/^[ \t]*//'`: Trim leading spaces or tabs
    
4. `grep -v '^$'`: Remove empty lines
    
5. `sed 's/\.hll//g'`: Remove `.hll` extensions
    
6. `sed 's/\dashing_results\///g'`: Remove path prefix
    

---

### 🧠 TL;DR: Most useful `sed` patterns

|Goal|Command example|
|---|---|
|Prepend text|`sed 's/^/prefix_/'`|
|Append text|`sed 's/$/_suffix/'`|
|Remove extension|`sed 's/\.ext//g'`|
|Replace text|`sed 's/old/new/g'`|
|Use alternate delimiter|`sed 's|
|Edit in-place (macOS)|`sed -i '' 's/.../.../' file.txt`|
|Multiple replacements|`sed 's/A/B/; s/C/D/'`|
|Chain with `grep`/`tail`|Use `|

Let me know if you want to wrap these in a shell script or apply them to folders/files dynamically.
Sure! Here's a cleaner and more formal version of that expression:

$$
C(b_j) = \text{size}(\text{compress}(b_j))
$$

### Alternatives:

* If you want a more mathematical look:

  $$
  C(b_j) = \left| \text{compress}(b_j) \right|
  $$

  where $|\cdot|$ denotes the size (e.g. in bytes or bits).

* If you define `compress` as a function:

  $$
  \text{compress}: \mathcal{P}(G) \to \{0,1\}^*
  $$

  then:

  $$
  C(b_j) = \text{length}(\text{compress}(b_j))
  $$

for f in /projects/reall/tam/data/ATB_experiments/048_s_enterica_skeleton_strat/batches/subdir_*/*.txt; do sed -i 's|^|/projects/reall/tam/data/ATB/Uncompressed/s_enterica/original_batches|' $f; done