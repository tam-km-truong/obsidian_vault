---
raw_tags:
  - cluster
  - txt
  - preorder
  - cut-point
  - statistic
  - debug
  - phylopack
  - experiments
word_count: 65
char_count: 847
processed: false
---

phylopack preorder experiments/098_EXPE_GTDB_recompression/data/maj_spc_clusters_full_path/s__Escherichia_coli.txt --cut-point 0.4 -o experiments/098_EXPE_GTDB_recompression/data/skeleton_phylogenies/s__Escherichia_coli/s__Escherichia_coli_preordered.txt -v --statistic --debug

```
for cluster in /projects/reall/tam/data/ATB/fof_clusters_path/*.txt; do echo $cluster; phylopack preorder $cluster --cut-point 0.05 -t 96 --max-skeleton-genomes 20000 --min-skeleton-genomes 10000 -o /projects/reall/tam/Workspace/experiments/119_EXPE_RECOMPRESSION_ATB202505/intermediate_files/$(basename $cluster .txt)/$(basename $cluster .txt)_global_ordered.txt -v --statistic --debug; done
```