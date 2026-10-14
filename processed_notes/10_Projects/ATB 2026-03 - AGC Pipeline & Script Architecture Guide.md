---
category: projects
tags:
  - atb
  - agc
  - pipeline
  - architecture
  - hpc
  - slurm
source_raw: "[[ATB202603 AGC Pipeline Workflow & Script Architecture]]"
status: processed
---

# ATB 2026-03: AGC Recompression Pipeline & Script Architecture Guide

## 1. Executive Summary & Scope
This guide documents the architecture and execution order of the **32 production scripts** powering the **AllTheBacteria (ATB) 2026-03** compression, validation, bug remediation, and public release pipeline across **3,092,278 bacterial genome assemblies**.

---

## 2. Multi-Stage Pipeline Architecture

```text
[Stage 0: Ingestion]
   ├── 01_download_and_verify.sh -> Validates 3.1M ENA/SRA accessions
   └── 02_build_accession_manifest.py -> Generates master assembly table

[Stage 1: Preorder Slicing]
   ├── 03_parse_global_ordering.py -> Reads global_final_ordering.txt
   └── 04_partition_clades.py -> Generates contiguous ~10GB batch chunks

[Stage 2: HPC Compression]
   ├── 05_slurm_array_agc_create.sh -> Submits parallel SLURM worker arrays
   └── 06_monitor_cluster_quotas.py -> Monitors /scratch disk quotas and memory

[Stage 3: Verification & Integrity Audit]
   ├── 07_verify_decompression_md5.sh -> Full round-trip getcol check
   └── 08_polyA_corruption_checker.py -> Detects upstream AGC splitter anomalies

[Stage 4: Metadata & Packaging]
   ├── 09_generate_archive_manifest.py -> Dumps per-archive accession indices
   └── 10_stage_zenodo_release.sh -> Final release packaging
```

---

## 3. Core Operational Directives
- **Zero Data Loss Guarantee:** Every `.agc` file must be accompanied by an MD5 hash manifest verified against original FASTAs.
- **Fail-Safe Slicing:** Batch boundaries must strictly adhere to the phylogenetic tree linearization to maintain maximum dictionary compressibility.
- **Cluster Etiquette:** Array jobs are throttled using SLURM `%50` task caps to prevent overloading metadata controllers.

---

## Related Notes
- [[AGC - Upstream Poly-A Silent Corruption Bug]] – Detailed analysis of the adaptive mode bug
- [[ATB 2026-03 - AGC Recompression Master Tracking & Audit]] – Live execution tracking
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]] – Historical ATB background
