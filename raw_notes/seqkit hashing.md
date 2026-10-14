---
raw_tags:
  - "xargs pigz"
  - txt
  - seqkit
  - cat
  - original
  - experiments
  - cut
  - basename
word_count: 62
char_count: 411
processed: true
processed_note: \"[[PhyloPack & Seqkit Hashing on ATB]]\"
---

original 
```bash
for f in experiments/075_EXPE_compression_files_validation/data/batches/*.txt; do echo -n "$(basename $f .txt),"; cat $f | xargs pigz -dc -p 20 | seqkit sum | cut -f 1; done
```