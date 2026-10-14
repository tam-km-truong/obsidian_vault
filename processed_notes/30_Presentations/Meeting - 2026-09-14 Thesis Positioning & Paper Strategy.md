---
category: presentations
tags:
  - meeting
  - thesis
  - strategy
  - publication
source_raw: "[[Meeting review 14 09 2026]]"
status: processed
---

# Meeting Notes: 2026-09-14 (Thesis Positioning & Paper Strategy)

## 1. Meeting Overview
Review meeting addressing thesis architecture, project boundaries, and publication strategy.

Three core dimensions discussed:
1. **High-Level Strategy & Thesis Positioning**
2. **Administrative & Manuscript Timeline**
3. **Current Engineering State (ATB / REALL)**

---

## 2. Strategic Positioning & Decisions

### Thesis Positioning
- **Between REALL & ATB:** Position the algorithmic and batching framework clearly between the REALL project infrastructure and the AllTheBacteria (ATB) application. Ensure tools are decoupled and modular so external bioinformatics consortia can adopt them independently.
- **Role of Compression Tooling:** The custom compression tooling (`agc-split-size`, `miniphy2`) is an engineering enabler, but the scientific thesis rests on **phylogenetic batching theory, order preservation, and access trade-offs**. Avoid getting sidetracked by raw C++ compressor benchmarks at the expense of the core biological story.

### Manuscript Strategy (Paper 1)
- **Angle:** Application-centric, orthogonal to the primary ATB data paper.
- **Narrative Focus:** Focus on enabling scalable, petabyte-scale bacterial pangenomics for end users.
- **Action Plan:** Polish the narrative, finalize the Pareto access-vs-compression figures, and prepare the draft.

---

## Related Notes
- [[Research Project & Publication Plan]] – General publication roadmap
- [[Meeting - 2025-01-19 1-on-1 on Optimization Formulation]] – Earlier advisor meeting
- [[ATB 2026-03 - AGC Pipeline & Script Architecture Guide]] – Pipeline implementation
