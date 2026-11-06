---
category: experiments
experiment_id: "126"
tags:
  - experiment
  - phylopack
  - miniphy
  - reordering
  - benchmarks
  - runtime
status: processed
created: 2026-11-06
---

# EXP 126: PhyloPack vs. MiniPhy Reordering Runtime Benchmark (Prototype 02)

## 1. Objective

Benchmark the end-to-end execution time and algorithmic throughput of **PhyloPack** against the **MiniPhy** baseline across the top 9 bacterial species in AllTheBacteria (ATB), assessing the viability of large-scale tree-based reordering for genome compression.

---

## 2. Algorithms Under Comparison

### 2.1 MiniPhy Baseline
- **Strategy**: Fixed batching ($\le 4,000$ genomes/batch).
- **Complexity**: Independent $\mathcal{O}(B^2)$ pairwise distance calculations per batch, where $B = 4000$.
- **Workflow**:
  1. Lexicographical chunking into batches of 4,000 genomes.
  2. Direct sketch extraction via `os.pread` from chunked `.msh` files.
  3. `mash triangle -p 8` on batch sketches.
  4. Neighbor-joining tree inference using `quicktree -in m`.
  5. Ladderized leaf traversal and batch concatenation.

### 2.2 PhyloPack (5-Stage Direct-from-Sketch Algorithm)
- **Strategy**: Representative skeleton backbone + distance argmin placement + windowed refinement.
- **Workflow**:
  1. **Stage 1 (Subsampling)**: Select $k$ skeleton anchors (e.g. 5% cut-point or 100% for $\le 10\text{k}$).
  2. **Stage 2 (Backbone NJ)**: Infer global backbone tree via `mash triangle` + `quicktree` on $k$ anchors.
  3. **Stage 3 (Ladderization)**: Midpoint root and ladderize backbone tree leaves.
  4. **Stage 4 (Query Placement)**: Stream remaining $N - k$ query genomes and assign to nearest skeleton anchor using `mash dist` argmin streaming.
  5. **Stage 5 (Windowed Refinement)**: Sliding-window local NJ tree re-inference (window size = 4,000) to resolve query order within anchor clusters.

---

## 3. Evaluated Species & Datasets (ATB Release Increments)

Tested across releases `2024-08`, `2025-05`, and `2026-03`:
1. *Salmonella enterica* (~644k total genomes)
2. *Escherichia coli* (~520k genomes)
3. *Staphylococcus aureus* (~300k genomes)
4. *Streptococcus pneumoniae* (~170k genomes)
5. *Klebsiella pneumoniae* (~160k genomes)
6. *Mycobacterium tuberculosis* (~130k genomes)
7. *Pseudomonas aeruginosa* (~100k genomes)
8. *Campylobacter jejuni* (~90k genomes)
9. *Streptococcus pyogenes* (~70k genomes)

---

## 4. Key Results & Findings

1. **Throughput Invariance in MiniPhy**:
   - Consistently achieves **~35 genomes/second** across all species and collection sizes because the batch size is clamped to 4,000.
2. **Skeleton Subsampling Efficiency**:
   - Using a 5% skeleton backbone enables tree construction on large datasets (e.g. 100,000 genomes) in 191 seconds for the backbone tree, avoiding the intractable $\mathcal{O}(N^2)$ scaling of a full 100k tree ($5 \times 10^9$ distance pairs).
3. **Bottleneck Shift**:
   - In PhyloPack, the primary time expenditure shifts from matrix calculation to query placement (`mash dist` argmin streaming against $k$ anchors) and local window refinement.

---

## 5. Related Experiments & Documentation
- [[EXP_127 - Salmonella enterica Subsets Scaling and Compression Trajectory]]
- [[PhyloPack preorder ATB]]
- [[miniphy2 workflow requirements]]
