---
category: projects
tags:
  - algorithms
  - bin-packing
  - pseudocode
  - python
source_raw: "[[pseudo code bin packing]]"
status: processed
---

# Algorithm: Bin Packing & Preorder Pipeline Pseudocode

## 1. End-to-End Pipeline Overview
Linearizes phylogenetic tree topologies and partitions genomes into constrained batches based on distinct k-mer volume and byte capacity.

---

## 2. High-Level Pipeline Procedure (`RunPreorderPipeline`)

```text
PROCEDURE RunPreorderPipeline(Arguments):
    // 1. Setup & Workspace Isolation
    CREATE TemporaryDirectory

    // 2. Splitting Phase (Optional: if input exceeds single-tree scaling)
    IF Arguments.RequiresSplitting THEN
        subsets = RunSplit(Arguments.InputGenomes, Arguments.SplitThreshold)
    ELSE
        subsets = [Arguments.InputGenomes]
    END IF

    // 3. Tree Inference & Linearization
    FOR EACH subset IN subsets DO
        sketches = GenerateKmerSketches(subset, k=31, s=1000)
        tree = InferPhylogeneticTree(sketches, method="FastME") // via Attotree
        preorder_list = TraversePreorder(tree.Root)
        
        // 4. Order-Preserving Bin Packing
        batches = PackPreorderGenomes(preorder_list, Arguments.MaxKmers, Arguments.MaxBytes)
        WriteBatchFiles(batches, Arguments.OutputDir)
    END FOR
    
    CLEANUP TemporaryDirectory
END PROCEDURE
```

---

## 3. Order-Preserving Bin Packing (`PackPreorderGenomes`)

```python
def pack_preorder_genomes(genomes_in_preorder, kmer_threshold=700_000_000, max_bytes=500_000_000):
    """
    Greedy order-preserving bin packing along phylogenetic traversal.
    """
    bins = []
    current_bin = []
    current_kmer_union = set()
    current_bytes = 0

    for genome in genomes_in_preorder:
        genome_kmers = genome.get_sketch() # e.g. MinHash or HyperLogLog
        projected_kmers = len(current_kmer_union.union(genome_kmers))
        projected_bytes = current_bytes + genome.byte_size

        if current_bin and (projected_kmers > kmer_threshold or projected_bytes > max_bytes):
            # Finalize current batch and start new one
            bins.append(current_bin)
            current_bin = [genome]
            current_kmer_union = set(genome_kmers)
            current_bytes = genome.byte_size
        else:
            current_bin.append(genome)
            current_kmer_union.update(genome_kmers)
            current_bytes = projected_bytes

    if current_bin:
        bins.append(current_bin)

    return bins
```

---

## Related Projects & Tools
- [[Mathematical Formulation - Order-Preserving Batching]] – Formal optimization proofs
- [[miniphy2 - Workflow Specifications & CLI]] – Production implementation of this pseudocode
- [[Attotree - Fast Tree Construction & Troubleshooting]] – Engine used for phylogenetic tree inference
