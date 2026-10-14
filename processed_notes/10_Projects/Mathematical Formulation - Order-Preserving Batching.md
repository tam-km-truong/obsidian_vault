---
category: projects
tags:
  - math
  - optimization
  - pangenomics
  - compression
  - bin-packing
source_raw: "[[Formulation batching]]"
status: processed
---

# Mathematical Formulation: Order-Preserving Genome Batching

## 1. Problem Overview & Objective
Given a massive collection of $N$ bacterial genomes that has been linearized according to a phylogenetic tree traversal (e.g. depth-first preorder traversal from [[Attotree]]), partition the sequence into contiguous, order-preserving batches $B_1, B_2, \dots, B_m$ such that the **total compressed collection size is minimized** while satisfying uncompressed size, genome count, and distinct k-mer constraints for fast random access.

---

## 2. Mathematical Formalization

### Notation & Variables
- Let $\mathcal{G} = \{g_1, g_2, \dots, g_N\}$ be the sequence of genomes arranged in phylogenetic preorder.
- A partition of size $m$ is defined by cut-point indices $0 = i_0 < i_1 < i_2 < \dots < i_m = N$, where the $j$-th batch is:
  $$B_j = \{g_{i_{j-1}+1}, g_{i_{j-1}+2}, \dots, g_{i_j}\}$$
- $S(B_j)$: The compressed size function of batch $B_j$ (e.g. using [[AGC - Assembled Genomes Compressor]] or [[MBGC]]).
- $U(g)$: Uncompressed size in bytes of genome $g$.
- $K(g)$: Distinct k-mer sketch (e.g. HyperLogLog or MinHash) of genome $g$.

### Optimization Objective
$$
\min_{m, \{i_j\}} \sum_{j=1}^m S(B_j)
$$

### Operational Constraints
1. **Contiguous Order Preservation:** Each batch $B_j$ contains strictly consecutive genomes along the phylogenetic preorder to maximize cross-genome dictionary sharing.
2. **Batch Uncompressed Capacity Limit ($C_{\max}$):**
   $$
   \sum_{g \in B_j} U(g) \le C_{\max} \quad \forall j \in \{1, \dots, m\}
   $$
3. **Distinct k-mer Capacity Limit ($K_{\max}$):**
   $$
   \left| \bigcup_{g \in B_j} K(g) \right| \le K_{\max} \quad \forall j \in \{1, \dots, m\}
   $$
4. **Maximum Batch Cardinality ($N_{\max}$):**
   $$
   |B_j| \le N_{\max} \quad \forall j \in \{1, \dots, m\}
   $$

---

## 3. Subadditivity & Theoretical Properties
Compressors such as AGC and MBGC exhibit subadditivity for homologous genomes:
$$
S(B_a \cup B_b) \le S(B_a) + S(B_b)
$$
However, because decompression time and random access memory scale with batch size, unconstrained batch growth degrades query latency. The optimal partition defines the Pareto frontier between aggregate archive footprint and query speed.

---

## 4. Algorithmic Solvers in Vault
1. **Dynamic Programming:** Yields the exact optimal partition in $O(N^2)$ time (or $O(N \cdot N_{\max})$ with bounded window search).
2. **Greedy First-Fit Decreasing:** Implemented in [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode|bin packing heuristic]].
3. **Pipeline Engine:** Packaged in [[miniphy2 - Workflow Specifications & CLI]].

## Related Projects & Notes
- [[Algorithm - Bin Packing & Preorder Pipeline Pseudocode]] – Concrete procedural algorithms
- [[miniphy2 - Workflow Specifications & CLI]] – CLI tool executing this formulation
- [[DSB 2025 - Phylogenetic Batching Presentation]] – Conference slides detailing this model
- [[Data Pipeline - Argmin Grouping on Large TSV]] – Matrix minimization workflow
