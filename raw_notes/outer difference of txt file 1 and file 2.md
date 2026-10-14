---
raw_tags:
  - file2
  - match
  - txt
  - file1
  - "outer difference"
  - "without needing"
  - "fixed string"
  - minus
word_count: 104
char_count: 774
processed: true
processed_note: \"[[CLI - Set Difference of Text Files]]\"
---

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