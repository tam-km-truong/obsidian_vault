---
raw_tags:
  - mbgc
  - basename
  - txt
  - compressor
word_count: 63
char_count: 424
processed: true
processed_note: \"[[MBGC - Multiple Bacterial Genome Compressor]]\"
---

```bash
for f in data/batches/subdir_1/*; do echo $f; mbgc c -m 3 -t 25 $f results/mbgc/$(basename $f .txt).mbgc; done
```
#compressor


for f in data/batches/subdir_1/*; do echo $f; mbgc c -m 3 -t 25 $f results/mbgc/$(basename $f .txt).mbgc; done