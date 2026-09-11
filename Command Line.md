Add `time` before the command you want to measure. For example: `time ls`.
Move all into 1 folder mv source source source destination
mv ./salmonella_enterica__08/* ./salmonella_enterica__37/* ./salmonella_enterica__38/* ./salmonella_enterica__08_37_38_12k
![[Pasted image 20241211105420.png]]
symlink hard vs soft
```shell
ln -s <path to the file/folder to be linked> <the path of the link to be created>
```

conda info --envs
to view list of environments

**chmod +x filename**

du -ch --block-size=1M  ./* >> files_size.csv
./kmc -k31 -fa genome.fa countkmerstuber01.res ./kmc_tmp_dir

`<(cat *.fa)` is a **process substitution**

```
for d in /home/ktruong/Documents/data/tuberculosis/*; do ./dashing_s128 card -k 31 <(cat $d/*.fa); 
done
```

pigz for gziping is super fast
```
 find data/661k/4602622/ -type f -name '*.fa' -exec pigz -v {} \;
```


du -c -m  $(cat experiments/019_version_2_snakemake_workflow/tmp/datasets_prepend_genome_paths/Salmonella_enterica.full_path.txt) | tail -1 | awk '{print $1}'

`split -n l/10 -d --additional-suffix=.txt input.txt part_`


### This gives you the **outer difference of file1 minus file2** without needing to sort. 

```bash
grep -Fxv -f file2.txt file1.txt > file3.txt
```

### ✅ Explanation:

- `-F`: fixed string match
    
- `-x`: match entire lines
    
- `-v`: invert match (i.e., select lines **not** in file2)
    
- `-f file2.txt`: use file2 as the pattern list

python python_scripts/postprocess_tree.py --standardize --midpoint-outgroup --ladderize --name-internals -l ~/leave/leaves_order.txt -n ~/node/nodes_order.txt ~/tree/tree.nw ~/tree/tree.std.nw


python experiments/034_phylogenetic_placements/compute_distance_matrix.py experiments/034_phylogenetic_placements/small_sample/reference_genomes/tree/leaves_order_with_path.txt.msh experiments/034_phylogenetic_placements/small_sample/query_genomes/s_enterica_queries_10.txt -l