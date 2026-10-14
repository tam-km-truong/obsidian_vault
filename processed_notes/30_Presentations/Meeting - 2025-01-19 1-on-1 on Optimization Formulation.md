---
category: presentations
tags:
  - meeting
  - research
  - planning
  - gtdb
source_raw: "[[1v1 Meeting 19 jan]]"
status: processed
---

# Meeting Notes: 2025-01-19 (1-on-1 on Optimization Formulation)

## Key Discussion Points
- **Dataset Expansion:** Transition from isolate-only subsets to the full [[GTBD experiment step by step|GTDB dataset]] to test cross-genus scalability.
- **Project Naming:** Evaluated working titles for the compression tool (e.g. *Phylord*, *PhyloPack*, leading to [[miniphy2 - Workflow Specifications & CLI|miniphy2]]).
- **Problem Formalization:** Formulate the batching problem as a constrained optimization problem (order-preserving bin packing) rather than purely heuristic clustering.

## Action Items
1. Formalize the objective function: minimize $\sum S(B_j)$ subject to $|B_j| \le C$.
2. Implement prototype in Python / Snakemake to benchmark GTDB representative species.

## Related Notes
- [[Meeting - 2025-09-01 Slide Preparation & Batching Formulation]]
- [[Mathematical Formulation - Order-Preserving Batching]]
