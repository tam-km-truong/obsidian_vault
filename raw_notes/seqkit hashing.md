---
raw_tags:
  - txt
  - seqkit
  - pigz
  - sum
  - cat
  - original
  - xargs
  - cut
word_count: 29
char_count: 195
processed: false
---

original 
```bash
for f in experiments/075_EXPE_compression_files_validation/data/batches/*.txt; do echo -n "$(basename $f .txt),"; cat $f | xargs pigz -dc -p 20 | seqkit sum | cut -f 1; done
```