---
category: knowledge
tags:
  - phylopack
  - seqkit
  - hashing
  - atb
source_raw: "[[PhyloPack preorder ATB]]"
status: processed
---

# PhyloPack & Seqkit Hashing on AllTheBacteria

## Pipeline Commands
```bash
# Compute preorder traversal on major species clusters
phylopack preorder \
    experiments/098_EXPE_GTDB_recompression/data/maj_spc_clusters_full_path/s__Escherichia_coli.txt \
    --cut-threshold 1000 \
    --output ./results/preorder/

# Compute fast MD5 hashing on genome files using seqkit
for f in experiments/075_EXPE_compression_files_validation/data/batches/*.txt; do
    echo -n "$(basename $f) "
    seqkit head -n 1 "$f" | md5sum
done
```

## Related Notes
- [[miniphy2 - Workflow Specifications & CLI]]
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]]
