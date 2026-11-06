# Mash LSH Band Clustering — Project Master Tracking (ROM)

> ### Abstract
> **High-throughput sequence clustering of planetary-scale bacterial genomic repositories requires bypassing all-vs-all distance matrices ($\mathcal{O}(N^2)$) and taxonomic human boundaries that fail under heavy horizontal gene transfer (HGT). This project establishes a production-grade, mono-functional Locality-Sensitive Hashing (LSH) banding pipeline to cluster 3,092,278 AllTheBacteria (ATB) 2026-03 assemblies using precomputed high-resolution MinHash sketches ($s = 10,000$ hashes, $k = 21$, MurmurHash3_x64_128).**
> 
> By partitioning sketch integers across $b$ modular hash bands (`hash % b`), the engine groups homologous genomes and mobile genetic elements into sequence-defined macro clusters in seconds via pure integer collisions with zero pairwise distance calculations. The codebase strictly adheres to single-responsibility (mono-function) component design, standard Python `src`-layout, and dual automated/manual verification gates. This document serves as the master Read-Only Memory (ROM) and persistent project ledger tracking architecture, execution milestones, mathematical invariants, and validation benchmarks.

---

## 1. Project Metadata & Environment

- **Repository Path**: `/Users/ktruong/tools/mash_lsh_band_clustering`
- **Data Source**: `/Users/ktruong/data/AllTheBacteria/ATB202603_Sketches/sketches/`
  - Cap'n Proto Schema: `MinHash.capnp`
  - Sketch Chunks: `chunk_sketches/` (~1,549 chunks, 2,000 sketches/chunk, $s=10,000$, MurmurHash3_x64_128, $k=21$)
  - SQLite Index: `sketch_index.sqlite`
- **Related Vault Notes**:
  - [[LSH Banding Graph Theoretical Framework & Edge Generation]]
  - [[How to Put All the World's Genomes on a Laptop — Sketching, Clustering, Ordering, Cutting, and Multithreading]]
  - [[ATB202603 AGC Recompression Master Tracking]]
  - [[ATB202603 AGC Pipeline Workflow & Script Architecture]]

---

## 2. Architectural Guidelines & Repository Layout

Development is strictly governed by [`AGENT.md`](file:///Users/ktruong/tools/mash_lsh_band_clustering/AGENT.md):
1. **Mono-Function Design**: Every core script, module, or CLI tool has a single responsibility.
2. **Directory Separation**:
   - `src/mash_lsh_band_clustering/cores/`: Core single-purpose modules (importable and CLI-executable).
   - `tests/unit/`: Automated unit tests testing invariants, edge cases, and empty/degenerate conditions.
   - `tests/manual/`: Standalone integration/performance scripts with human-readable CLI outputs.
3. **Mandatory Testing Gates**: All code modifications require passing automated tests and reporting results. Test suites are immutable unless explicitly instructed.

```text
mash_lsh_band_clustering/
├── src/
│   └── mash_lsh_band_clustering/
│       ├── __init__.py
│       └── cores/                    # Single-purpose CLI/importable modules
│           ├── __init__.py
│           ├── sketch_reader.py      # Sub-task 1: Ingestion only
│           ├── lsh_bander.py         # Sub-task 2: Pure mathematical hashing
│           ├── bucket_indexer.py     # Sub-task 3: Inverted collision index
│           ├── cluster_builder.py    # Sub-task 4: DSU connected components
│           └── export_clusters.py    # Sub-task 5: Manifest & stats export
├── tests/
│   ├── unit/                         # Automated unit tests (pytest)
│   └── manual/                       # Manual verification & benchmarks
├── pyproject.toml
├── .gitignore
├── README.md
└── AGENT.md
```

---

## 3. Mathematical Foundations: Modular LSH Banding

In standard bottom-$s$ MinHash sketches, insertions/deletions shift the relative indices of identical hashes within the sorted list. Standard positional slicing (slicing array index $[i : i+r]$) loses collision sensitivity under indels.

### 3.1 Modular Band Partitioning
Hashes are partitioned into $b$ distinct bands using integer modulus:
$$\text{band\_id} = h \pmod b$$
Within each band, the set of hashes forms the band signature or is combined into $r$-row sub-signatures.

### 3.2 Collision Probability (S-Curve)
For two genomes with Jaccard sequence similarity $J$:
$$P(\text{at least one shared bucket}) = 1 - (1 - J^r)^b$$
- For high-identity relatives ($J \ge 0.95$): $P \approx 1.0$ (guaranteed collision).
- For divergent species ($J < 0.10$): $P \approx 0.0$ (zero spurious collisions).
- Automatically clusters genomes sharing high-copy mobile elements/plasmids (HGT) without species labels.

---

## 4. Master Implementation Checklist & Milestones

- [x] **Milestone 0: Project Initialization & Standards Setup**
  - [x] Create project repository (`mash_lsh_band_clustering`) on `main` branch.
  - [x] Author [`AGENT.md`](file:///Users/ktruong/tools/mash_lsh_band_clustering/AGENT.md) defining single-responsibility, testing gates, and directory layout.
  - [x] Configure `.gitignore` to protect guidelines and exclude caches/builds.
  - [x] Establish standard Python `src`-layout with `tests/unit/` and `tests/manual/`.
  - [x] Create Obsidian Master Tracking ROM note.

- [x] **Milestone 1: Sub-Task 1 — Ingestion (`sketch_reader.py`)**
  - [x] Implement `src/mash_lsh_band_clustering/cores/sketch_reader.py` with standalone schema `schema/MinHash.capnp` (zero C++ compile dependencies; dual-engine Cap'n Proto binary reader with `mash info -d` fallback).
  - [x] Invariants Enforced: Accession canonicalization (`clean_accession`), strictly $s=10,000$ hashes/genome, 64-bit unsigned integers (`0 <= h < 2^64`), sorted order.
  - [x] Author `tests/unit/test_sketch_reader.py`: 5 automated tests passing in 0.076s (path edge cases, file missing, real chunk assertions).
  - [x] Author `tests/manual/run_sketch_reader.py`: Side-by-side ground-truth comparison against `mash info -t` and `mash info -d` confirming 100% bit-for-bit parity across all hashes.
  - [x] Performance: 160.1 sketches/sec (1.6M hashes/sec), 0.79 MB peak memory across 2,000 genomes.

- [x] **Milestone 2: Sub-Task 2 — Hashing (`lsh_bander.py`)**
  - [x] Implement `src/mash_lsh_band_clustering/cores/lsh_bander.py`: Pure mathematical transformer partitioning hashes via modular routing `(h ^ seed) % b_bands` into 64-bit Blake2b bucket signatures (`<I2Q`).
  - [x] Indel Shift Invariance: Solves bottom-$s$ MinHash index-shifting; identical hashes route to identical modular bands regardless of array offset.
  - [x] Piped Generator Integration (`stream_and_band`): Chains Task 1 directly into Task 2, discarding raw 80 KB hashes immediately per genome (bounded memory footprint).
  - [x] Author `tests/unit/test_lsh_bander.py`: 7 automated tests passing (determinism, parameter checks, S-curve bounds, indel shift resilience, integration stream). Total test suite: 12/12 passing in 0.129s.
  - [x] Author `tests/manual/run_lsh_bander.py`: Biological ground-truth verified via official `mash dist`:
    - Pair `SAMD00412582` vs `SAMD00029179`: Collided in 99 / 100 LSH buckets.
    - Official `mash dist`: Distance = `0.00059426` with `9755/10000` shared MinHash hashes (100% biological agreement).
    - Performance: 100.2 genomes/sec, 18.84 MB peak memory across 2,000 genomes.

- [ ] **Milestone 3: Sub-Task 3 — Inverted Index (`bucket_indexer.py`)**
  - [x] Theoretical Framework established: [[LSH Banding Graph Theoretical Framework & Edge Generation]] (hypergraph duality, Erdős-Rényi percolation mitigation, hybrid clique/spanning-star expansion).
  - [ ] Implement `cores/bucket_indexer.py` (tracks collisions; outputs edge list `(genome_A, genome_B, shared_count)` with hybrid expansion).
  - [ ] Author `tests/unit/test_bucket_indexer.py` (collision fidelity, bucket deduplication, hub pruning).
  - [ ] Author `tests/manual/run_bucket_indexer.py` (memory footprint under 10k–100k genomes).

- [ ] **Milestone 4: Sub-Task 4 — Graph Clustering (`cluster_builder.py`)**
  - [ ] Implement `cores/cluster_builder.py` (Disjoint-Set Union / connected components with thresholding).
  - [ ] Author `tests/unit/test_cluster_builder.py` (transitivity, isolated singletons, bounded component sizes).
  - [ ] Author `tests/manual/run_cluster_builder.py` (cluster size histogram on sample data).

- [ ] **Milestone 5: Sub-Task 5 — Presentation & Export (`export_clusters.py`)**
  - [ ] Implement `cores/export_clusters.py` (serializes TSV manifests, cutpoint hints, summary telemetry).
  - [ ] Author `tests/unit/test_export_clusters.py` (format assertions, 1-to-1 accession coverage).
  - [ ] Author `tests/manual/run_export_clusters.py` (human-readable validation output).

- [ ] **Milestone 6: Planetary Scale Benchmark (Full ATB 2026-03)**
  - [ ] Stream all 1,549 sketch chunks (3,092,278 genomes).
  - [ ] Verify runtime ($< 5\text{ minutes}$ target), RAM bounded ($\le 16\text{ GB}$).
  - [ ] Evaluate cluster concordance against official ATB 2026-03 cutpoints.

---

## 5. Changelog & Project Chronology

| Timestamp | Scope | Action & Outcome | Author |
| :--- | :--- | :--- | :--- |
| **2026-10-17 02:15** | Architecture | Initialized repo, added `AGENT.md`, `.gitignore`, standard `src` layout. | AI Pair Programmer |
| **2026-10-17 02:18** | Data Verification | Inspected `/Users/ktruong/data/AllTheBacteria/ATB202603_Sketches/sketches/`; confirmed `chunk_sketches/` (.msh, $s=10000$). | AI Pair Programmer |
| **2026-10-17 02:22** | Documentation | Created Project Master Tracking ROM note in Obsidian. | AI Pair Programmer |
| **2026-10-17 02:57** | Sub-Task 1 (Ingestion) | Implemented `sketch_reader.py` (Cap'n Proto binary parser); 5/5 unit tests passed; verified 100% bit-for-bit parity with `mash info -d`. | AI Pair Programmer |
| **2026-10-17 14:13** | Sub-Task 2 (Banding) | Implemented `lsh_bander.py` (modular Blake2b hashing); 12/12 unit tests passed; biological ground-truth validated with `mash dist` (99/100 shared buckets at dist=0.00059). | AI Pair Programmer |
| **2026-10-17 14:16** | ROM Ledger Update | Updated Master Tracking with extensive implementation details, telemetry, and test outputs for Milestones 1 and 2. | AI Pair Programmer |
| **2026-10-17 16:27** | Graph Theory Framework | Created `[[LSH Banding Graph Theoretical Framework & Edge Generation]]` detailing hypergraph clique vs star expansions and percolation mitigation. | AI Pair Programmer |

