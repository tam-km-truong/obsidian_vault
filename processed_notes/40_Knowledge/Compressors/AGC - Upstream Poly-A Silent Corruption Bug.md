---
category: knowledge
tags:
  - agc
  - bug
  - compression
  - corruption
  - c-plus-plus
source_raw: "[[AGC Upstream Poly-A Splitter Corruption Bug Debug Note]]"
status: processed
---

# AGC Upstream Bug: Silent Contig Corruption via A^k Splitter & CKmer Matcher

## Executive Summary
In October 2026, an upstream bug was uncovered in `refresh-bio/agc` (reproducible across `v3.2.2`, `v3.2.4`, and `agc-split-size`) that causes **silent data corruption** during adaptive compression mode (`-a`). Suffixes of contigs with long homopolymers are falsely matched, leading to truncated or scrambled contigs without throwing non-zero exit codes.

---

## 1. Bug Anatomy & Root Cause

### Trigger Condition
- Invoking AGC with adaptive mode: `agc create -a ...`
- Contigs containing long poly-A sequences ($A^k$ where $k \ge \text{kmer_length}$).

### Code-Level Fault: `CKmer::operator==`
In `src/core/kmer.h` and the adaptive segment partitioner:
- The k-mer equality operator treats degenerate homopolymeric bit representations as identical when evaluating split points.
- The adaptive splitter mistakenly reuses an existing reference block offset for non-identical sequences.
- Upon decompression (`agc getcol`), the extracted FASTA sequence diverges from the input MD5 checksum, but AGC returns exit code `0`.

---

## 2. Impact on ATB 2026-03 Dataset
- Out of 3,092,278 assemblies, batches processed with `split_create -a` required thorough verification.
- A 100% completeness audit was conducted across all recompressed archives.

---

## 3. Workaround & Fix Protocol
1. **Upstream Patch:** Guard `CKmer::operator==` to ensure exact bitmask comparisons across boundary words.
2. **Operational Workaround:** Pre-slice contiguous batches using `global_final_ordering.txt` and run standard non-adaptive `agc create` (avoiding `-a` on homopolymer-dense clades).
3. **Automated Verification:** Every generated `.agc` archive must be verified using `agc getcol` streamed into `md5sum` against the original assembly manifest.

---

## Related Notes & Documentation
- [[ATB 2026-03 - AGC Pipeline & Script Architecture Guide]] – The 32-script pipeline implementing this fix
- [[ATB 2026-03 - AGC Recompression Master Tracking & Audit]] – Production recovery and audit ledger
- [[AGC - Assembled Genomes Compressor]] – General AGC usage and options
