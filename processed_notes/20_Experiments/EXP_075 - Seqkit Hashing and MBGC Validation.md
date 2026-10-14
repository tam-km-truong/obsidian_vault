---
category: experiments
experiment_id: "075"
tags:
  - experiment
  - mbgc
  - seqkit
  - hashing
source_raw: "[[075 seqkit hashing]]"
status: processed
---

# EXP 075: Seqkit Hashing and MBGC Compression Validation

## Objective
Verify integrity and compute file hashes for genome batches in `072_EXPE_random_access_genomes` prior to MBGC recompression benchmarking.

## Pipeline Command
```bash
# Hash reference genomes across random-access batches
for f in experiments/072_EXPE_random_access_genomes/data/batches/*; do
    echo $(basename $f)
    ref=$(head -n 1 $f | cut -d',' -f1)
    seqkit grep -p "$ref" "$f" | md5sum
done
```

## Related Experiments & Tools
- [[MBGC - Multiple Bacterial Genome Compressor]]
- [[EXP_078 - Phrase Complexity (z) Computation]]
