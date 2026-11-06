# How to Put All the World's Genomes on a Laptop: Sketching, Clustering, Ordering, Cutting, and Multithreading

How do you take 15 Terabytes of messy bacterial DNA (3+ million genomes) and fit it on a laptop so anyone can search it in 1 second? 

You sketch them at high resolution ($s = 10,000$), group them by sequence instead of arbitrary species names, sort them by family, cut them smartly on the peaks, and run it across all CPU cores.

---

## 1. The Core Idea: Why Order Matters

If you compress files in random order, the compressor has to relearn everything on every file. It stays huge.

If you sort genomes along their evolutionary tree:
- Neighbor genomes share 99% of the exact same DNA letters.
- The compressor only saves the tiny differences.

**What happens:**
- **Raw DNA (FASTA)**: 15,000 GB $\to$ **115 GB** in AGC (>120x smaller).
- **Sketches (MinHash)**: 250 GB $\to$ **6.5 GB** in zstd (38x smaller).
- Sorting by family shrinks *every* biological format automatically.

---

## 2. Multithreading: The Kitchen Setup

If you process 3 million genomes one-by-one, it takes **3.5 days**. With 40 CPU cores, it takes **2 hours**.

**How our Python script does it:**
- **Manager (Thread 0)**: Dumps 2,000 genome jobs on the counter.
- **20 Cooks (Workers 1–20)**: Each cook grabs a job and runs `agc | seqkit`.
- **40 Burners (CPU Cores)**: Each cook uses 2 CPU cores. All 40 cores stay pinned at 100%.

**Why Python doesn't lag:**
Python drops its lock (GIL) the millisecond it runs `subprocess.run()`. The real work runs in fast C++ and Go. The Python worker literally goes to sleep (0% CPU) until the OS wakes it up with the answer.

---

## 3. The Landscape: Never Cut in the Valley

Neighbor distance across 3.09 million genomes shows two areas:
1. **The Flatland (0 to 2.7M)**: Distance is almost zero. Millions of identical hospital isolates. They compress tightly (~10–30 KB each).
2. **The Mountain (2.7M to 3.09M)**: Distance jumps to 0.5–1.0. Rare, weird environmental bugs. They compress poorly.

**The Golden Cutting Rule (Topological Snapping):**
- Never cut in the valleys. A valley is a family of identical genomes. If you cut it in half, you force the next archive to re-store the whole genome reference from scratch. You waste storage.
- Always cut on the peaks. If you need a cut near genome 750,000, check the neighborhood, find the spike where genomes are already different, and cut there. You lose zero compression sharing.

---

## 4. Throwing Away "Species" (MinHash LSH Banding)

### Letting the Data Decide Instead of Humans
Human taxonomy (species names) isn't necessarily bad, but **someone has to arbitrarily decide where to draw the boundary**—and we don't want to make that choice. We let the DNA data decide for itself.

For example: two genomes might have different official species names, but because of massive **horizontal gene transfer** (shared plasmids, phages, or mobile elements), they share huge blocks of identical sequence. For compression, putting them next to each other is much better than forcing them into separate species folders just because of a label.

### How LSH Banding Works at High Resolution
To keep high biological quality, each genome gets a high-resolution sketch of **$s = 10,000$ hashes** (MinHash):
1. Slice the 10,000 numbers into **500 bands** of **20 numbers** each.
2. Throw each band into a hash bucket.
3. If two genomes share **even ONE bucket**, they are grouped together.

**The Result:**
- If two genomes are nearly identical, math guarantees they collide into the same bucket with **>99.99% probability**.
- If two genomes are unrelated, the chance they share a 20-number band is **~0%**.
- It creates natural sequence clusters in **~30 seconds** using pure integer hashing. Zero distance math, zero manual threshold guessing, and it automatically groups genomes that share horizontal sequence.

---

## 5. Tree Inference: The Only Slow Step (Per-Cluster 20k Skeletons)

- Sketching is fast ($O(N)$).
- Placement is fast ($O(1)$ lookup).
- Compression is fast ($O(N)$ parallel).
- **Tree building (Neighbor Joining)** is slow: it scales quadratically ($O(K^2)$).

**The Fix: Cap at $K \le 20,000$ per cluster, run in parallel.**
- Never build a single giant tree on all 3 million genomes.
- If we capped globally at 20k, a massive clade like *Salmonella* (400,000 genomes) would only get 2,500 skeleton anchors (too coarse).
- Instead, the 20,000 budget is **per-cluster**:
  - Small clades (< 20,000 genomes): 100% of their genomes become the tree.
  - Giant clades (> 20,000 genomes): Capped at 20,000 skeleton anchors.
- **Embarrassingly parallel**: Each cluster builds its independent tree simultaneously across CPU cores with zero cross-talk. Total wall-clock time is bounded by the largest single cluster (~15 mins).

---

## 6. Complete Step-by-Step Complexity Breakdown

| Step | Complexity | Time (3M Genomes) | How It Works | Why This Complexity? |
| :--- | :---: | :---: | :--- | :--- |
| **1. High-Res Sketching** | $\mathcal{O}(N \cdot L)$ | ~15 mins | Streams DNA through a rolling 31-mer window, keeping the $s = 10,000$ smallest hashes. | Reads every letter of all $N$ genomes once. $L$ is genome length (~5 Mbp). Strictly linear. |
| **2. Coarse Grouping (LSH Banding)** | $\mathcal{O}(N \cdot b)$ | **~30 secs** | Partitions 10,000 hashes into $b=100$ bands via `hash % b`, drops genome IDs into buckets. | Pure integer hashing in RAM. No distance math. Automatically captures HGT. |
| **3. Macro Root Tree** | $\mathcal{O}(C^2)$ | **~5 secs** | Builds tiny guide tree on $C \approx 1,000$ cluster roots. | Orders the macro-clusters relative to each other ($E. coli \to Salmonella \to Staph$). |
| **4. Cluster Skeleton Trees** | $\mathcal{O}(K_{\max}^2)$ | **~15 mins** | Builds independent skeleton trees ($K \le 20,000$ per cluster) in parallel across CPU cores. | Embarrassingly parallel. Wall-clock time is bounded by the largest single cluster. |
| **5. Tree Linearization** | $\mathcal{O}(K)$ | **~2 secs** | Midpoint roots and ladderizes each cluster tree, then reads leaves in preorder. | Flattens 2D tree branching into a 1D highway line. |
| **6. Genome Placement** | $\mathcal{O}(N)$ | **~2 mins** | Uses an in-memory inverted hash index to attach follower genomes to nearest skeleton anchor. | Hash lookup is $\mathcal{O}(1)$ average per hash. Fast RAM lookup. |
| **7. Partition Snapping** | $\mathcal{O}(\log S)$ | **< 0.01 sec** | Takes coarse steps near target cut, spots distance spike, zooms in with fine steps. | Never cut in valleys. Always cut on peaks. Tested ~600 distance pairs total. |
| **8. AGC Compression** | $\mathcal{O}(N)$ | **~6–8 hours** | Cuts stream into 1,129 balanced ~100 MB batches and compresses on cluster. | Each genome is read, split into chunks, and compressed once. Divided across 3 compute nodes. |
| **9. Full Audit Verification** | $\mathcal{O}(N)$ | **~3–4 hours** | 20 workers stream `agc getset \| seqkit sum` and compare hashes to metadata. | Decompresses every genome once in parallel memory streams. Gives 100% mathematical proof. |
| **10. Querying (Whole Genome)** | $\mathcal{O}(\text{batches})$ | **< 2 secs** | Sketches query, checks against 6.5 GB local index, finds matching 100 MB batch, pulls via AGC. | Tests query against small batch signatures, pulls 1 single archive file. Runs on any laptop. |
| **11. Querying (Single Gene / SNP)** | $\mathcal{O}(k\text{-mers})$ | **< 5 secs** | Splits gene into 31-mers, checks presence across batch Bloom filters (COBS/Fulgor). | Bit-vector intersection directly probes whether $k$-mers exist in the color matrix. |

---

## 7. The Implementation Architecture: Decoupling Brain from Muscle

### You Don't Need the FASTAs to Order the World
All algorithmic phases that determine data organization run 100% on the **6.5 GB sketch archive** (`all_sketches_compressed.tar`):
- **Brain (Geometry Engine on Laptop):**
  - Input: 6.5 GB sketch archive.
  - Operation: LSH Banding $\to$ Macro Tree $\to$ Parallel Cluster Skeletons $\to$ Follower Placement $\to$ Peak Snapping.
  - Hardware: Any machine with 16 GB RAM. Zero network I/O, runs in ~15–20 minutes.
  - Output: `ordered_manifest.tsv` (30 MB text file specifying exact 1D order and peak cut lines).
- **Muscle (Cluster Workers):**
  - Input: `ordered_manifest.tsv` + raw FASTAs.
  - Operation: Dumb streaming. Read assemblies in the exact order of the TSV and pipe to `agc create`.
  - Zero distance calculations, zero tree logic on the cluster.

### Bypassing the `attotree` Bottleneck
`attotree` is a wrapper script that re-sketches raw FASTAs with Mash before calling `quicktree`. Because sketches already exist:
- **Never call `attotree`**: It wastes CPU re-reading FASTAs.
- **Direct Sketch-to-Tree Pipeline**:
  ```bash
  mash triangle skeleton.msh > dist.phylip
  quicktree -in m dist.phylip > tree.nwk
  ```
  `mash triangle` outputs the PHYLIP distance matrix directly from precomputed sketches in seconds, and `quicktree` converts it to Newick tree immediately.

### Empirical Validation from Prototype
Testing on synthetic genomes with 3 clades and a shared 15 kb mobile plasmid:
1. **Modular Banding Required**: In bottom-$s$ MinHash, insertion/deletion shifts array indices. Slicing hashes by `hash % b` solves this and recovers the theoretical S-curve ($P = 1 - (1 - J^r)^b$).
2. **Automatic HGT Grouping**: At $b=300, r=2$, divergent species sharing a plasmid collided into 5 shared buckets and grouped together without taxonomic labels, with 0 false positives on control clades.
3. **Safe Bucket Boundaries**: Max bucket size was strictly bounded ($\le 13$ genomes), staying well within the quadratic tree inference limit.

---

### The Final Formula
$$\text{Total Runtime} = \underbrace{\mathcal{O}(N)}_{\text{Sketch}} + \underbrace{\mathcal{O}(K_{\max}^2)}_{\text{Parallel Skeletons}} + \underbrace{\mathcal{O}(N)}_{\text{Place}} + \underbrace{\mathcal{O}(N)}_{\text{Compress}} = \mathbf{\mathcal{O}(N)}$$

The quadratic tree step is permanently locked to $K_{\max} \le 20,000$ per cluster and distributed across CPU cores. Everything else is linear. That is why this scales to 100 million genomes without breaking.
