---
raw_tags:
  - workflow
  - non-zero
  - exit
  - attotree
  - tree
  - order
  - txt
  - post-processing
word_count: 90
char_count: 1221
processed: false
---

post-processing
python python_scripts/postprocess_tree.py --standardize --midpoint-outgroup --ladderize --name-internals -l leaves_order.txt -n nodes_order.txt

RuleException:

CalledProcessError in file "/projects/reall/tam/tools/miniphy2/workflow/Snakefile", line 49:

Command 'set -euo pipefail;  attotree -L /scratch/ktruong/Workspace/experiments/079_EXPE_atbHQ_recompression/data/batches_hq/staphylococcus_aureus_005.txt -o workflow/tmp/trees/staphylococcus_aureus_005.nw -t 5' returned non-zero exit status 1.

[Wed Oct 29 11:12:30 2025]

Error in rule compute_tree:

    message: None

    jobid: 1482

    input: /scratch/ktruong/Workspace/experiments/079_EXPE_atbHQ_recompression/data/batches_hq/staphylococcus_aureus_005.txt

    output: workflow/tmp/trees/staphylococcus_aureus_005.nw

    shell:

        attotree -L /scratch/ktruong/Workspace/experiments/079_EXPE_atbHQ_recompression/data/batches_hq/staphylococcus_aureus_005.txt -o workflow/tmp/trees/staphylococcus_aureus_005.nw -t 5

        (command exited with non-zero exit code)