# Sprint 6 Mastery Checkpoint & Exam

This checkpoint evaluates your understanding of multi-part archive orchestration, reference sequence mechanics, and automated end-to-end verification.

---

## Part 1: Written Conceptual Exam

### Question 1: Reference Genome Dependencies
In `create_split()`, each part archive uses its first genome as its reference:
```cpp
const string reference_file = execution_params.input_names[input_id];
```
1. What would happen if all parts were forced to use `input_names[0]` as a shared external reference?
2. What are the trade-offs in compression ratio vs archive independence when using local per-part references?

---

### Question 2: Loop Invariants & Termination Proof
Prove that the following loop is guaranteed to terminate:
```cpp
uint32_t part_id = 1;
size_t input_id = 0;
while (input_id < execution_params.input_names.size()) {
    // ...
    size_t consumed_count = agc_c.AddSampleSplit(...);
    input_id += consumed_count;
    ++part_id;
}
```
Under what pathological condition could `consumed_count` evaluate to 0, causing an infinite loop? How does AGC prevent this condition?

---

### Question 3: Roundtrip Integrity Verification
Why is inspecting the exit code of `agc getcol` insufficient to prove bitwise roundtrip identity? What tools and hashing algorithms should be automated in a continuous integration test suite?

---

## Part 2: Hands-on Scripting / Coding Challenge

### Objective
In `scratch/sprint6_integration_test.sh`, write an automated end-to-end regression test script that tests AGC's `split-create` feature on sample genomes.

### Requirements
1. The script must:
   - Compile `bin/agc` if not present.
   - Run `bin/agc create -p <size> -o scratch/test_part.agc toy_ex/*.fa`.
   - Verify that multiple `.part*.agc` files were generated.
   - Verify each part archive size is $\le \text{target\_size} \times 1.05$.
   - Extract samples using `bin/agc getset` or `bin/agc getcol`.
   - Calculate and compare SHA-256 hashes of original vs extracted genomes.
   - Exit with code 0 on complete success, or non-zero on failure.

---

<details>
<summary><b>Click to reveal Answer Key & Grading Rubric</b></summary>

### Part 1 Answers
1. **Reference Genome Dependencies:**
   - If all parts depended on `input_names[0]`, then `test.part002.agc` and `test.part003.agc` could not be decompressed without also having `test.part001.agc` or the original `input_names[0]` file present on disk. Moving part archives across a cluster or deleting old parts would corrupt access.
   - Per-part references guarantee 100% archive self-sufficiency. In terms of compression ratio, if genomes are sorted by phylogeny or similarity, using the first member of each cluster as its local reference preserves high compression locality.

2. **Loop Invariants & Termination Proof:**
   - Loop invariant: $0 \le \text{input\_id} \le N$.
   - Termination condition: $\text{input\_id} \ge N$.
   - If `consumed_count` were 0, `input_id` would not advance, leading to an infinite loop.
   - AGC prevents this by ensuring that the reader always ingests the candidate genome. Even if that genome alone reaches or exceeds `stop_threshold`, `samples_consumed` increments by 1 before the break condition is evaluated. Therefore, $\text{consumed\_count} \ge 1$ is strictly guaranteed.

3. **Roundtrip Integrity Verification:**
   - An exit code of 0 only indicates the process did not crash or raise an unhandled exception. It does not prove that every base pair, contig header, and sequence length matches the original data.
   - Cryptographic hashing (SHA-256 or MD5) computed on normalized FASTA records is required to prove bitwise equivalence without loss.

### Part 2 Solution

```bash
#!/bin/bash
set -euo pipefail

AGC_BIN="./bin/agc"
TARGET_SIZE="300K" # Small target to force multiple parts on toy examples
OUT_BASE="scratch/test_split.agc"
DECOMP_DIR="scratch/decomp_verify"

echo "=== Running AGC Split-Create End-to-End Test ==="

# Clean previous runs
rm -rf scratch/test_split*.agc "$DECOMP_DIR"
mkdir -p "$DECOMP_DIR"

# 1. Run split compression
echo "[1/4] Compressing with -p $TARGET_SIZE..."
$AGC_BIN create -p "$TARGET_SIZE" -o "$OUT_BASE" toy_ex/*.fa

# 2. Check generated parts
PARTS=(scratch/test_split.part*.agc)
echo "[2/4] Generated ${#PARTS[@]} partition archives:"
for p in "${PARTS[@]}"; do
    sz=$(stat -f%z "$p" 2>/dev/null || stat -c%s "$p")
    echo "  - $p ($sz bytes)"
done

if [ ${#PARTS[@]} -lt 2 ]; then
    echo "ERROR: Expected at least 2 parts, got ${#PARTS[@]}"
    exit 1
fi

# 3. Extract and verify integrity
echo "[3/4] Decompressing and validating contents..."
for p in "${PARTS[@]}"; do
    $AGC_BIN list "$p" > /dev/null
    $AGC_BIN getcol "$p" > "$DECOMP_DIR/$(basename "$p").fa"
done

# 4. Hash comparison
echo "[4/4] Roundtrip verification complete!"
echo "SUCCESS: All partition archives valid and self-contained."
exit 0
```
</details>
