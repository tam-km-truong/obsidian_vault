---
category: experiments
tags:
  - atb
  - agc
  - tracking
  - audit
  - benchmarks
source_raw: "[[ATB202603 AGC Recompression Master Tracking]]"
status: processed
---

# ATB 2026-03: AGC Recompression Master Tracking & Audit

## 1. Overview & Objective
Master ledger tracking the recovery of exact batch boundaries from `split_create` `.agc` archives (which passed the 100% completeness check), slicing `global_final_ordering.txt` into identical contiguous batches, and executing clean recompression with `agc create`.

- **Total Assemblies Tracked:** 3,092,278
- **Primary Data Root:** `/scratch/ktruong/data/atb/`
- **Audit Reference:** `raw_notes/agc_split_size/docs/debug_split_create_audit.md`

---

## 2. Tracking Dimensions & Clade Checkpoints
1. **Batch Recovery:** Reconstructing accession boundaries from initial split archives.
2. **Recompression Progress:** Monitoring SLURM array batches across major bacterial orders (*Enterobacterales*, *Mycobacteriales*, *Pseudomonadales*, *Bacillales*).
3. **Checksum Verification:** 100% byte-exact round-trip extraction tests.

---

## 3. Key Observations & Findings
- Standard non-adaptive `agc create` produces consistent archives and circumvents the upstream poly-A corruption bug.
- Compression ratio across 3.1M assemblies exceeds $35\times$ space savings compared to raw FASTAs, while maintaining batch random access.

---

## Related Notes
- [[ATB 2026-03 - AGC Pipeline & Script Architecture Guide]] – Script architecture
- [[AGC - Upstream Poly-A Silent Corruption Bug]] – Root cause of batch recovery requirement
- [[SLURM Jobs - Active Benchmarking & Recompression Runs]] – General SLURM submission templates
