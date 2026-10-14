---
category: knowledge
tags:
  - mash
  - minhash
  - sketching
  - kmer
source_raw: "[[Mash]]"
status: processed
---

# Mash & MinHash Sequence Sketching

## In a Nutshell
**Mash** implements the **MinHash** dimensionality reduction technique to compress sequence collections into compact "sketches" (typically 1,000 to 10,000 64-bit integers), enabling ultrafast sequence distance and Jaccard similarity estimation without sequence alignment.

---

## Algorithmic Foundation
1. **K-mer Decomposition:** Slice sequence into overlapping k-mers ($k=21$).
2. **Hashing:** Hash each k-mer to a 64-bit integer using MurmurHash3.
3. **Bottom-s MinHash:** Retain only the $s$ smallest hash values (the "sketch size").
4. **Jaccard Estimation:** 
   $$
   J = \frac{|S_A \cap S_B|}{|S_A \cup S_B|}
   $$
5. **Mash Distance ($D$):** Direct approximation of mutation rate:
   $$
   D = -\frac{1}{k} \ln\left(\frac{2J}{1+J}\right)
   $$

---

## CLI Recipes
```bash
# Create sketch file for an isolate
mash sketch -s 1000 -k 21 -o genome.msh genome.fasta

# Compute distance between two sketches
mash dist genomeA.msh genomeB.msh

# Screen a raw read file against NCBI RefSeq sketch
mash screen refseq.genomes.msh reads.fastq.gz
```

## Related Notes
- [[dashing2 - HyperLogLog Genome Sketching]] – Modern HyperLogLog alternative
- [[Mashtree - Rapid Comparative Genomics]] – Uses Mash for tree building
- [[Jellyfish - Lock-Free K-mer Counting]] – Exact k-mer counter
