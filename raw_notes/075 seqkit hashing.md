---
raw_tags:
  - mbgc
  - seqkit
  - experiments
  - dls
  - dustbin
  - sum
  - cut
  - basename
word_count: 54
char_count: 469
processed: false
---

dustbin__005_0,seqkit.v0.1_DLS_k0_d901a6f26ea11ed68c223056aefabe50

```bash
for f in experiments/072_EXPE_random_access_genomes/data/mbgc/*.mbgc; do echo -n "$(basename $f .mbgc),"; mbgc d -t 25 $f - | seqkit sum | cut -f 1; done > experiments/075_EXPE_compression_files_validation/results/hashes_batches_mbgc.csv
```