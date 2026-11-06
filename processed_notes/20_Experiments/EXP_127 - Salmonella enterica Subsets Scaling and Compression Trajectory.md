---
category: experiments
experiment_id: "127"
tags:
  - experiment
  - senterica
  - scaling
  - phylopack
  - miniphy
  - agc
  - compression
  - reordering
status: processed
created: 2026-11-06
---

# EXP 127: *Salmonella enterica* Empirical Scale Trajectory & Batched AGC Compression

## 1. Executive Summary & Objective

This experiment evaluates the empirical storage scaling trajectory $S(N)$ for *Salmonella enterica* across five collection scales:
$$N \in \{4\text{k}, 10\text{k}, 25\text{k}, 50\text{k}, 100\text{k}\}$$

The core objectives are:
1. **Eliminate Prefix Selection Bias / Data Point Mixing**: Rather than slicing arbitrary prefixes from a pre-computed 700k global tree traversal (which produces artificially homogeneous clades compressing at ~3 KB/genome), sample each scale $N$ independently and chronologically by natural INSDC accession order (`SAMN`/`SAMEA`), ordering each scale from scratch.
2. **Benchmark Ordering Algorithms**: Compare **MiniPhy** (fixed 4,000-genome batches) against **PhyloPack**:
   - Small scales ($N \le 10\text{k}$): Full NJ (`cut_point = 1.0`, 100% skeleton), ladderized tree traversal.
   - Large scales ($N \ge 25\text{k}$): 5% skeleton anchors (`cut_point = 0.05`), backbone NJ tree, `mash dist` argmin query placement, and 4,000-genome windowed NJ refinement.
3. **Capture Microsecond Stage Timings**: Log wall-clock runtimes and throughput across all stages (sketches, pairwise triangle, NJ tree, ladderization, placement, refinement).
4. **Stage Batched AGC Compression**: Partition ordered accessions into non-overlapping 4,000-genome batches (98 batches total across both methods and 5 scales), resolve Genouest cluster FASTA paths against `global_final_ordering.txt.gz`, and stage for node-level concurrent execution on AVX2 hardware (`cl1n047`).

---

## 2. Experimental Design & Methodology

### 2.1 Chronological Sampling & Sketch Verification
- **Accession Chronology**: INSDC accession numbers increment monotonically over time and track biological release dates.
- **Coverage Audit**: The complete *S. enterica* metadata contains 644,731 genomes. To guarantee 100% sketch availability, accessions were cross-referenced against `sketch_index.sqlite` (`figures/supplementary/fig_distance_landscape/data/sketch_index.sqlite`).
- **Filtered Missing**: 909 unsketched accessions were removed prior to slicing.
- **Extracted Subsets**:
  - `senterica_4000.txt` (4,000 genomes)
  - `senterica_10000.txt` (10,000 genomes)
  - `senterica_25000.txt` (25,000 genomes)
  - `senterica_50000.txt` (50,000 genomes)
  - `senterica_100000.txt` (100,000 genomes)

### 2.2 Algorithm Implementations
- **MiniPhy Baseline**:
  - Splits accessions into sequential batches of $\le 4,000$ genomes.
  - For each batch: extracts sketches from local chunk files via `os.pread`, executes `mash triangle -p 8`, infers NJ tree via `quicktree -in m`, and traverses ladderized leaves.
  - Final ordering is the sequential concatenation of batch orderings.
- **PhyloPack**:
  - For $N \le 10\text{k}$: Full NJ on all $N$ genomes (`cut_point = 1.0`), ladderized leaf traversal. Query placement and windowed refinement are bypassed.
  - For $N \ge 25\text{k}$: Subsamples 5% skeleton anchors (`cut_point = 0.05`), infers backbone NJ tree, places remaining 95% queries via SIMD `mash dist` streaming, and refines ordering in sliding windows of 4,000 genomes using local NJ trees.

---

## 3. Empirical Ordering Results & Timing Breakdown

All ordering runs were executed locally with 8 threads. The exact stage timings from `scale_ordering_timings_summary.tsv` are documented below:

| Method | Strategy | Scale ($N$) | Total Time (s) | Throughput (gen/s) | Backbone NJ (s) | Placement (s) | Refinement (s) | Skeleton / Query Genomes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MiniPhy** | 4k-batch NJ | 4,000 | 114.43 s | 35.0 | — | — | — | 1 batch |
| **PhyloPack** | Full NJ | 4,000 | 115.15 s | 34.7 | 115.09 s | 0.00 s | 0.00 s | 4,000 / 0 |
| **MiniPhy** | 4k-batch NJ | 10,000 | 259.91 s | 38.5 | — | — | — | 3 batches |
| **PhyloPack** | Full NJ | 10,000 | 821.09 s | 12.2 | 820.93 s | 0.00 s | 0.00 s | 10,000 / 0 |
| **MiniPhy** | 4k-batch NJ | 25,000 | 711.90 s | 35.1 | — | — | — | 7 batches |
| **PhyloPack** | 5% Skel + Refine | 25,000 | 1,112.00 s | 22.5 | 11.71 s | 421.62 s | 678.55 s | 1,250 / 23,750 |
| **MiniPhy** | 4k-batch NJ | 50,000 | 1,427.06 s | 35.0 | — | — | — | 13 batches |
| **PhyloPack** | 5% Skel + Refine | 50,000 | 3,070.50 s | 16.3 | 45.58 s | 1,652.11 s | 1,372.60 s | 2,500 / 47,500 |
| **MiniPhy** | 4k-batch NJ | 100,000 | 2,954.31 s | 33.8 | — | — | — | 25 batches |
| **PhyloPack** | 5% Skel + Refine | 100,000 | 9,640.69 s | 10.4 | 191.31 s | 6,634.18 s | 2,814.56 s | 5,000 / 95,000 |

### Key Observations
1. **MiniPhy Constant Throughput**: MiniPhy maintains a virtually constant throughput of ~34–38 genomes/second across all scales due to its independent $\mathcal{O}(B^2)$ 4k-batch partitioning ($B = 4000$).
2. **PhyloPack $\mathcal{O}(N^2)$ vs $\mathcal{O}(k \cdot N)$ Crossover**:
   - At $N = 4\text{k}$, Full NJ is identical in runtime to MiniPhy (~115 s).
   - At $N = 10\text{k}$, Full NJ scaling ($10000^2 / 2 = 50\text{M}$ distance pairs) drops throughput to 12.2 genomes/s (821 s).
   - At $N \ge 25\text{k}$, the 5% skeleton strategy drastically reduces tree inference time (e.g. 1,250 anchors solved in 11.7 s; 5,000 anchors solved in 191 s). The dominant runtime shifts to query placement (`mash dist` argmin against anchors) and local windowed refinement.

---

## 4. Cluster Staging & Path Resolution

### 4.1 Path Mapping Reconciliation
Cluster FASTA paths were mapped using `global_final_ordering.txt.gz` (3,092,278 indexed entries on Genouest).
- **Audit**: 100,000 / 100,000 accessions matched (0 missing).
- Paths point to active Genouest volumes:
  `/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_set2_2024-08/...`
  `/projects/reall/tam/data/ATB/Uncompressed/Uncompressed_2025-05/...`

### 4.2 Staged Batch Hierarchy
- **4k**: 1 batch × 2 methods = 2 batches
- **10k**: 3 batches × 2 methods = 6 batches
- **25k**: 7 batches × 2 methods = 14 batches
- **50k**: 13 batches × 2 methods = 26 batches
- **100k**: 25 batches × 2 methods = 50 batches
- **Total**: **98 batches** staged under `127_EXPE_senterica_subsets_compression.tar.gz` (1.33 MB).

### 4.3 Node-Level Concurrency Architecture
- Direct compute node execution on Genouest AVX2 node (`cl1n047`) bypassing SLURM queue instability.
- `xargs -P 4` dispatches 4 parallel workers, each allocating 20 threads to `agc create -t 20` (80 cores total).
- Independent per-batch output files (`batch_XXXX.agc` and `batch_XXXX.tsv`) prevent race conditions.
- Expected runtime reduced from 4.5 hours (sequential) to **~60–75 minutes**.

---

## 5. Deployment Commands

### 5.1 SCP to Genouest Workspace
```bash
scp scratch/prototype_07_senterica_subsets_compression/output/staging_cluster/127_EXPE_senterica_subsets_compression.tar.gz \
    "$genouestID":/projects/reall/tam/Workspace/experiments/
```

### 5.2 Compute Node Execution
```bash
# 1. Connect directly to the AVX2 node
ssh cl1n047

# 2. Navigate to experiment directory and unpack
cd /projects/reall/tam/Workspace/experiments/
tar -xzf 127_EXPE_senterica_subsets_compression.tar.gz
cd 127_EXPE_senterica_subsets_compression

# 3. Activate conda environment manually
conda activate ktruong

# 4. Launch concurrent compression benchmark
bash scripts/run_node_concurrent.sh 4 20
```

### 5.3 Outputs Generated
- Per-batch archives: `output_agc/{miniphy,phylopack}/scale_XXXX/batch_YYYY.agc`
- Batch summary: `output_agc/batches_compression_summary.tsv`
- Cumulative storage per scale: `output_agc/scale_cumulative_storage_summary.tsv`

---

## 6. Related Experiments & Documentation
- [[EXP_126 - PhyloPack vs MiniPhy Reordering Runtime Benchmark]]
- [[PhyloPack preorder ATB]]
- [[miniphy2 workflow requirements]]
