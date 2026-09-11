```bash
for f in experiments/086_EXPE_dustbin_tradeoff_ran_access/data/batches/dustbin_b10k*; do ref=$(head -n 1 $f); galitime -n $(basename $f) -l stdout "agc create -a -b 500 -s 1500 -t 25 -v 2 -o experiments/086_EXPE_dustbin_tradeoff_ran_access/misc/$(basename $f .txt).agc -i $f $ref"; done > experiments/086_EXPE_dustbin_tradeoff_ran_access/galitime_log_10000.txt
```