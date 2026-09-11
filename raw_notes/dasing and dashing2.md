The specific command is:  

./dashing2_savx2 sketch -s -N -o ./output/result -F ./data/mycoplasma_pneumoniae__01.txt --cmpout cmp.txt

  

-s/--save-kmers: Save k-mers. This puts the k-mers saved into .kmer files to correspond with the minhash samples.  
  If an output path is specified for dashing2 and --save-kmers is enabled, stacked k-mers will be written to <arg>.kmer64, and names will be written to <arg>.kmer.names.txt

-N/--save-kmercounts: Save k-mer counts for sketches. This puts the k-mer counts saved into .kmercounts.f64 files to correspond with the k-mers.

-o/--outfile: sketches are stacked into a single file and written to <arg>. We need this to output the files.

--cmpout/--distout/--cmp-outfile Compute distances and emit them to <arg>.

  

The output files are binary files.

dashing2 doesnt offer the function to estimate cardinality 
check if dashing2 code give the kmer count somewhere

for dashing, the command line to get the estimation kmer count is:

```shell
./dashing_s128 card -k 31 /data/*.fa 
```