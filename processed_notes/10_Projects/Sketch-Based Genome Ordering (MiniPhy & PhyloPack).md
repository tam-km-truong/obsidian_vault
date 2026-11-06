---
category: projects
tags:
  - ordering
  - miniphy
  - phylopack
  - sketches
  - mash
  - quicktree
  - python
  - architecture
source_raw: "[[miniphy2]]"
status: processed
created: 2026-11-06
---

# Sketch-Based Genome Ordering: MiniPhy & PhyloPack Architecture

## 1. Overview & Location

The standalone, modularized sketch-based ordering engine is located in the repository under:
`ordering/`

It packages the complete toolset required to:
1. **Generate MinHash Sketches**: In parallel chunks across million-genome FASTA collections (`ordering/cores/sketch_generator.py`).
2. **Index Sketches**: Build sub-millisecond SQLite indices (`sketch_index.sqlite`) with byte offsets for zero-copy random access (`ordering/cores/sketch_indexer.py`).
3. **Execute MiniPhy**: Fixed-batch Neighbor-Joining ordering with constant $\sim 35\text{ genomes/s}$ throughput (`ordering/run_miniphy.py`).
4. **Execute PhyloPack**: 5-stage scalable direct-from-sketch phylogenetic ordering using representative skeleton backbones and SIMD query placement (`ordering/run_phylopack.py`).

---

## 2. Package Architecture & Layout

```
ordering/
├── README.md                          # Definitive technical guide & reuse documentation
├── config.yaml                        # Central YAML configuration (paths, binaries, parameters)
├── config.py                          # Python loader resolving absolute paths against repo root
├── run_miniphy.py                     # Standalone CLI entrypoint for MiniPhy
├── run_phylopack.py                   # Standalone CLI entrypoint for PhyloPack
├── cores/
│   ├── extract_subset_msh.py          # Zero-copy sketch extraction via os.pread & Cap'n Proto
│   ├── split_accessions.py            # Stage 1: Skeleton subsampling (random, uniform, full NJ)
│   ├── infer_tree_quicktree.py        # Stage 2: mash triangle + quicktree NJ inference
│   ├── traverse_tree_leaves.py        # Stage 3: ETE3 midpoint root + ascending ladderize
│   ├── place_queries_on_skeleton.py   # Stage 4: Streaming mash dist argmin placement
│   ├── refine_ordering_windows.py     # Stage 5: Sliding-window local NJ refinement
│   ├── sketch_generator.py            # Parallel Mash chunk sketching from genome paths
│   ├── sketch_indexer.py              # SQLite sketch index builder (sketch_index.sqlite)
│   └── msh_reader.py                  # Low-level pycapnp reader for .msh binary files
├── unit_test/                         # 13 automated unit tests (100% passing in ~1.2s)
└── manual_test/
    └── test_ordering_pipeline.sh     # Rapid smoke/manual verification test
```

---

## 3. Configuration Setup (`config.yaml`)

Configuration is declared in `ordering/config.yaml` and loaded via `from ordering.config import load_ordering_config`:

```yaml
paths:
  # Base directory containing sketches, Cap'n Proto schema, and SQLite index
  data_dir: "figures/supplementary/fig_distance_landscape/data"
  # SQLite index mapping accessions to chunk byte offsets
  db_path: "figures/supplementary/fig_distance_landscape/data/sketch_index.sqlite"
  # Cap'n Proto MinHash schema for binary sketch serialization
  capnp_schema: "figures/supplementary/fig_distance_landscape/data/MinHash.capnp"
  # Directory holding chunked .msh sketch files
  chunk_sketches_dir: "figures/supplementary/fig_distance_landscape/data/chunk_sketches"
  # Reference dictionary for full cluster FASTA paths (Genouest)
  cluster_paths_gz: "scratch/prototype_07_senterica_subsets_compression/global_final_ordering.txt.gz"

binaries:
  mash: "mash"
  quicktree: "quicktree"
  agc: "agc"

defaults:
  sketch_size: 10000
  kmer_size: 21
  threads: 8
  miniphy_batch_size: 4000
  phylopack_cut_point: 0.05
  phylopack_window_size: 4000
  phylopack_min_refine_size: 10000
```

---

## 4. Workflows & Command Reference

### 4.1 Sketch Generation & Indexing
```bash
# 1. Parallel Sketching (Chunks of 10,000 genomes, 25 threads)
python ordering/cores/sketch_generator.py \
    -i file_list.all.latest.tsv \
    -o data/sketches \
    -s 10000 -k 21 -c 10000 -t 25

# 2. Build or Update SQLite Offset Index
python ordering/cores/sketch_indexer.py \
    -d data/sketches \
    --db data/sketches/sketch_index.sqlite \
    -t 8
```

### 4.2 MiniPhy Ordering
```bash
python ordering/run_miniphy.py \
    -i accessions.txt \
    -o output/miniphy_run \
    -b 4000 \
    -t 8
```

### 4.3 PhyloPack Ordering (5-Stage Algorithm)
```bash
# For <= 10k genomes (Full NJ):
python ordering/run_phylopack.py \
    -i accessions_10k.txt \
    -o output/phylopack_10k.txt \
    -c 1.0 \
    --no-refine \
    -t 8

# For >= 25k genomes (5% Skeleton Backbone + Placement + Refinement):
python ordering/run_phylopack.py \
    -i accessions_50k.txt \
    -o output/phylopack_50k.txt \
    -c 0.05 \
    -w 4000 \
    -t 8
```

---

## 5. Algorithmic Comparison Summary

| Metric | MiniPhy (`run_miniphy.py`) | PhyloPack (`run_phylopack.py`) |
| :--- | :--- | :--- |
| **Strategy** | Fixed batching ($\le 4,000$ genomes) | Global backbone + argmin placement + refinement |
| **Complexity** | Linear in collection size: $\mathcal{O}\left(\frac{N}{B} \cdot B^2\right)$ | $\mathcal{O}(k^2 + (N-k) \cdot k + \frac{N}{W} \cdot W^2)$ |
| **Throughput** | Constant: $\sim 35\text{ genomes/s}$ | $10–35\text{ genomes/s}$ (depends on scale & $k$) |
| **Best Used For** | Fast incremental batching without global dependencies | Global species-level phylogenetic ordering & maximum AGC compression |

---

## 6. Related Experiments
- [[EXP_127 - Salmonella enterica Subsets Scaling and Compression Trajectory]]
- [[EXP_126 - PhyloPack vs MiniPhy Reordering Runtime Benchmark]]
- [[miniphy2 - Workflow Specifications & CLI]]
