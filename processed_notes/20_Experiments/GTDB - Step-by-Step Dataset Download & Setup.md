---
category: experiments
tags:
  - gtdb
  - setup
  - ncbi-datasets
source_raw: "[[GTBD experiment step by step]]"
status: processed
---

# GTDB: Step-by-Step Dataset Download & Cluster Setup

## Step-by-Step Protocol
1. **Download Metadata:** Fetch bacterial metadata tables (`bac120_metadata_r220.tsv`) from the GTDB website.
2. **Install NCBI Datasets CLI:**
   ```bash
   conda install -c conda-forge ncbi-datasets-cli
   ```
3. **Extract Accession Lists:** Extract representative accessions per genus and species into individual batch files.
4. **Cluster Transfer:** Stage files on `/scratch/ktruong/data/gtdb/`.
5. **Run Batching Pipeline:** Execute [[miniphy2 - Workflow Specifications & CLI]] to compute preorder partitions.

## Related Notes
- [[NCBI Datasets CLI Reference]]
- [[SLURM Jobs - Active Benchmarking & Recompression Runs]]
