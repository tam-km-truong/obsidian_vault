
## 1. **Initial Problem Setup**

- Goal: Find the argmin (index of minimum value) for each row in a huge TSV file (up to 100GB).
    
- Discussed solutions with `numpy`, `pandas`, Python, Bash/`awk`.
    
- Online/streaming approach preferred due to file size.
    

---

## 2. **TSV File Format and Headers**

- TSV format example:
    
    ```
    #query  col1  col2  col3 ...
    row1    0.032 0.024 0.045
    row2    0.054 0.010 0.030
    ...
    ```
    
- Header stored separately as a text file with one column name per line.
    
- Remove header from the big TSV to simplify processing.
    

---

## 3. **Parallel Processing and Chunking**

- Workflow:
    
    1. Remove header.
        
    2. Split file by number of cores (not line counts).
        
    3. Run `awk` on each chunk in parallel.
        
    4. Concatenate results.
        
- Use `xargs` for parallel execution.
    
- Use `mktemp` for temp directories, and cleanup with:
    
    ```bash
    cleanup() {
        rm -rf "$TMPDIR"
    }
    trap cleanup EXIT
    ```
    
- Use `set -euo pipefail` in bash for safe scripting.
    
- Minimal `awk` script to find argmin index per row:
    
    ```bash
    cat > "$AWK_SCRIPT" << 'EOF'
    {
        min = $2;
        idx = 0;
        for (i = 3; i <= NF; i++) {
            if ($i < min) {
                min = $i;
                idx = i - 2;
            }
        }
        print idx
    }
    EOF
    ```
    

---

## 4. **Simplified Single-Threaded Bash+awk Script**

Minimal working version (single core):

```bash
#!/bin/bash
set -euo pipefail

INPUT=$1
OUTPUT=${2:--}

tail -n +2 "$INPUT" | awk '{
    min = $2; idx = 0;
    for (i = 3; i <= NF; i++) {
        if ($i < min) {
            min = $i;
            idx = i - 2;
        }
    }
    print idx
}' > "$OUTPUT"
```

---

## 5. **Grouping Rows by Argmin Column in Python**

Python example grouping rows by their argmin column index:

```python
from collections import defaultdict

row_names = [...]       # list of row names (strings)
col_names = [...]       # list of column names (strings)
argmin_indices = [...]  # list of argmin indices (int), zero-based

groups = defaultdict(list)

for row_name, idx in zip(row_names, argmin_indices):
    col_name = col_names[idx]
    groups[col_name].append(row_name)

for col, rows in groups.items():
    print(f"{col}: {rows}")
```

---

## 6. **Calling Bash `awk` from Python**

Example of running `awk` with Python’s `subprocess`:

```python
import subprocess

awk_script = r'''
BEGIN { FS="\t" }
NR > 1 {
    min = $2;
    idx = 0;
    for (i = 3; i <= NF; i++) {
        if ($i < min) {
            min = $i;
            idx = i - 2;
        }
    }
    print idx;
}
'''

result = subprocess.run(
    ["awk", awk_script],
    stdin=open("distances.tsv"),
    capture_output=True,
    text=True,
    check=True
)

argmin_indices = [int(i) for i in result.stdout.strip().split('\n')]
```

---

## 7. **Scalability Considerations**

- 100M lines with ~10 char each line → ~1GB text per file (row names, column names).
    
- Memory needed for storing all row/column names and argmin indices is reasonable on modern hardware.
    
- However, grouping 100M rows into 10,000 groups and holding all groups in memory is risky.
    
- Opening one output file per group simultaneously is problematic due to OS limits (~1024 open files typical).
    

---

## 8. **Streaming Groupby with LRU Cache to Handle File Handles**

Python streaming grouping approach that limits the number of open files:

```python
import subprocess
from collections import OrderedDict

DISTANCE_FILE = "distances.tsv"
ROW_NAMES_FILE = "rows.txt"
COL_NAMES_FILE = "columns.txt"
MAX_OPEN_FILES = 100  # tune based on OS limits

# Load column names
with open(COL_NAMES_FILE) as f:
    col_names = [line.strip() for line in f]

# Open row names file
row_file = open(ROW_NAMES_FILE)

# Run awk as subprocess for argmin indices
awk_script = '''
{
    min = $1; idx = 0;
    for (i = 2; i <= NF; i++) {
        if ($i < min) {
            min = $i;
            idx = i;
        }
    }
    print idx
}
'''

proc = subprocess.Popen(
    ["awk", awk_script],
    stdin=open(DISTANCE_FILE),
    stdout=subprocess.PIPE,
    text=True
)

# LRU cache for open file handles
open_files = OrderedDict()

def get_file_handle(group_name):
    if group_name in open_files:
        # Move to end to mark as recently used
        open_files.move_to_end(group_name)
        return open_files[group_name]
    # Open new file
    if len(open_files) >= MAX_OPEN_FILES:
        # Close least recently used file
        old_group, fh = open_files.popitem(last=False)
        fh.close()
    fh = open(f"grouped_{group_name}.txt", "a")
    open_files[group_name] = fh
    return fh

try:
    for row_name in row_file:
        row_name = row_name.strip()
        idx_str = proc.stdout.readline()
        if not idx_str:
            break
        idx = int(idx_str.strip()) - 1  # awk index is 1-based
        group = col_names[idx]
        fh = get_file_handle(group)
        fh.write(row_name + "\n")
finally:
    # Close all files and clean up
    for fh in open_files.values():
        fh.close()
    row_file.close()
    proc.stdout.close()
    proc.wait()
```

---

## 9. **Summary**

- Efficiently computing per-row argmin on huge files is best done with streaming tools like `awk`.
    
- Processing in chunks and/or streaming avoids memory overload.
    
- Grouping large datasets with many groups requires careful file handle management.
    
- An LRU cache for file handles in Python solves the "too many open files" problem.
    
- This workflow scales well to 100 million rows on modern hardware, provided disk I/O and memory are sufficient.
    

