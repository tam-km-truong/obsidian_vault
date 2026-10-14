---
category: knowledge
tags:
  - agc
  - compression
  - pangenomics
  - tools
source_raw: "[[AGC]]"
status: processed
---

# AGC: Assembled Genomes Compressor

## Overview
**AGC** (Assembled Genomes Compressor) is a high-performance tool tailored for compressing collections of de novo assembled homologous genomes (pangenomes). It uses reference-guided dictionary compression with variable-length substring sharing.

---

## Practical Batch Invocations

### Creating an Archive from Genome Batches
```bash
for f in data/batches/subdir_1/*; do
    ref=$(head -n 1 $f)
    echo "Compressing batch $f with reference $ref..."
    agc create -a -b 500 -s 50 -i $f -o $(basename $f .txt).agc $ref
done
```

### Key Parameters
- `create`: Build a new compressed archive.
- `-a`: Adaptive reference mode.
- `-b <segment_size>`: Segment size in KB (default: 500).
- `-s <kmer_size>`: Similarity sketch size (default: 50).
- `-i <file_list>`: File of filenames listing input genome fasta paths.
- `$ref`: The accession chosen as the primary anchor reference for the batch.

---

## Extracting File Lists from Archives
If `archives.fof` contains one AGC archive path per line, list all member genomes:
```bash
while IFS= read -r archive; do
    base=$(basename "$archive" .agc)
    agc listset "$archive" > "${base}_list.txt"
done < archives.fof
```

## Related Notes & Compressors
- [[MBGC - Multiple Bacterial Genome Compressor]] – Alternative pangenome compressor
- [[Mathematical Formulation - Order-Preserving Batching]] – Optimization model for batching
- [[CLI - Random Access & Dustbin Batching History]] – Empirical AGC benchmarks
