# Sprint 6 Study Guide: Multi-Part Archive Partitioning & Data Verification

In this sprint, you explore outer coordinator loops, reference genome selection, and roundtrip data validation.

---

## 1. Key Concepts to Understand

### A. Independent Archive Part Design
Why does each part archive in AGC have its own independent reference sequence?
- **Self-Sufficiency**: If an archive part required external dictionary files or a shared reference from another archive, moving or deleting an earlier part would render subsequent parts unreadable.
- **Independent Parallel Querying**: Cloud workers can stream, index, or extract contigs from `collection.part042.agc` without mounting or downloading parts 001 through 041.

### B. Reference Genome Selection in AGC
In AGC:
```cpp
const string reference_file = execution_params.input_names[input_id];
```
The reference genome is the structural anchor of the entire archive:
- Its $k$-mers determine the splitters.
- All subsequent genomes in that part are delta-encoded (via LZP and context matching) against this reference and each other.
- Setting the first member of the partition as reference ensures optimal compression locality for genomes grouped together.

### C. Cursor Slicing and Termination Guarantees
```cpp
size_t input_id = 0;
while (input_id < execution_params.input_names.size()) {
    // ...
    input_id += consumed_count;
    ++part_id;
}
```
For this loop to be provably non-terminating / deadlock-free:
1. `consumed_count` must be $\ge 1$ on every iteration.
2. Even if a single genome is larger than `target_part_size`, `AddSampleSplit` admits that genome into its own partition and returns `consumed_count = 1`.
3. Thus `input_id` is strictly monotonic increasing, guaranteeing loop termination in at most $N$ iterations.

### D. End-to-End Bitwise Verification (Roundtripping)
A compression tool is only as good as its decompression fidelity.
To formally verify roundtrip equality:
```bash
# 1. Compress with partitioning
agc create -p 10M -o test.agc genomes/*.fa

# 2. Extract every sample from each part
agc getcol test.part001.agc > extracted_part1.fa
agc getcol test.part002.agc > extracted_part2.fa

# 3. Verify exact bitwise matching
diff -u original.fa extracted.fa
```

---

## 2. Recommended Readings & Documentation

1. **POSIX File Verification & Checksum Best Practices**:
   Using `sha256sum` or `md5sum` for pipeline verification.
2. **Genomic Archive Standards (CRAM, AGC, MBGC)**:
   Comparative analysis of reference-based vs reference-free multi-part archiving.

---

## 3. Common Gotchas & Personal Notes

1. **Suffix Stripping**:
   When reading input sample files (e.g. `sample1.fa.gz`), AGC calls `remove_common_suffixes(sample_name)` so the internal identifier in the archive becomes `sample1`.
2. **Command Line Preservation**:
   Calling `agc_c.AddCmdLine(cmd_line)` stores the exact CLI invocation inside the archive header for provenance and reproducibility.

---

## 4. 10-Minute Mini Practice Exercise

Write a small script verifying that two directory trees of FASTA files match byte-for-byte:

```bash
#!/bin/bash
set -euo pipefail

ORIG_DIR="toy_ex"
DECOMP_DIR="scratch/decompressed"

echo "Checking SHA256 hashes..."
for f in "$ORIG_DIR"/*.fa; do
    base=$(basename "$f")
    orig_hash=$(shasum -a 256 "$f" | awk '{print $1}')
    if [ -f "$DECOMP_DIR/$base" ]; then
        decomp_hash=$(shasum -a 256 "$DECOMP_DIR/$base" | awk '{print $1}')
        if [ "$orig_hash" == "$decomp_hash" ]; then
            echo "MATCH: $base"
        else
            echo "MISMATCH: $base!"
            exit 1
        fi
    fi
done
echo "All verified successfully!"
```
