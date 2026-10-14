---
category: experiments
experiment_id: "071"
tags:
  - experiment
  - compressibility
  - benchmarks
source_raw: "[[EXP 071]]"
status: processed
---

# EXP 071: Compressibility Measures Test

## Objective
Test compressibility metric extraction across experimental batch subsets, standardizing cluster paths.

## Execution Command
```bash
for f in experiments/071_EXPE_compressibility_measures_test/data/batches/*; do
    echo "Batch: $f"
    sed 's|/projects/reall/tam/|/scratch/ktruong/|' "$f" | xargs -d '\n' cat > merged_batch.fa
done
```

## Related Experiments
- [[EXP_075 - Seqkit Hashing and MBGC Validation]]
- [[EXP_078 - Phrase Complexity (z) Computation]]
