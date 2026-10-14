---
raw_tags:
  - agc
  - "gzipped individual genomes"
  - ref
  - mags
  - gtdb_mags_13
  - getcol
  - head
  - compressor
word_count: 85
char_count: 550
processed: true
processed_note: \"[[AGC - Assembled Genomes Compressor]]\"
---

```bash
for f in data/batches/subdir_1/*; do ref=$(head -n 1 $f); echo $f; agc create -a -b 500 -s 1500 -t 25 -v 2 -o results/agc/$(basename $f .txt).agc -i $f $ref; done
```
#compressor 

to extract all and gzipped individual genomes:
```bash
agc getcol mags/gtdb_mags_13.processed.agc -o mags/files/ -g 6 -f -v 2
```