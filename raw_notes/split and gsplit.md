To **split a text file into 6 parts by line**, you can use:

```bash
split -n l/6 input.txt part_
```

- `-n l/6`: split by **lines** into 6 files of approximately equal size
    
- `input.txt`: your input file
    
- `part_`: prefix for output files (e.g., `part_aa`, `part_ab`, ...)
    

---

### 🔹 TL;DR Tutorial: `split` command

#### 📌 **Syntax**

```bash
split [OPTION]... [INPUT [PREFIX]]
```

#### 📘 **Common options**

| Option                     | Meaning                                           |
| -------------------------- | ------------------------------------------------- |
| `-l N`                     | Split every **N lines** (e.g., `-l 1000`)         |
| `-n l/N`                   | Split input into **N files by lines**             |
| `-n r/N`                   | Split input into **N files round-robin**          |
| `-d`                       | Use numeric suffixes (e.g., `part_00`, `part_01`) |
| `--additional-suffix=.txt` | Add suffix to each file                           |
| -a N                       | add N digits                                      |

#### 🧪 **Examples**

- Split every 1000 lines:
    
    ```bash
    split -l 1000 input.txt chunk_
    ```
    
- Split into 4 equal parts by lines:
    
    ```bash
    split -n l/4 input.txt chunk_
    ```
    
- Split into files with numeric suffix and `.txt` extension:
    
    ```bash
	split -n l/4 -d --additional-suffix=.txt input.txt chunk_
    ```

 Split into files cut at 4000 line and 2 digits with numeric suffix and `.txt` extension:
    
    
```bash
	gsplit -l 4000 -d -a 2 --additional-suffix=.txt input.txt batches/batch_
```
    
