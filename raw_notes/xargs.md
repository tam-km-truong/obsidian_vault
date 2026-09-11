# TLDR

mkdir -p output

ls data/atb/by_species/salmonella_enterica/*.tar.xz | xargs -P 3 -I{} sh -c '
echo "processing tarball {}"
tmpdir=$(mktemp -d /scratch/ktruong/.tmp/tmp.XXXXXXXXXX)
echo "extracting {} into $tmpdir"
tar -Jxf {} --strip-components=1 -C $tmpdir
echo "gzipping .fa file from {}"
pigz -f $tmpdir/*.fa -p 10
echo "moving to destination and rm tmpdir"
mv $tmpdir/*.fa.gz /scratch/ktruong/data/atb/uncompressed/salmonella_enterica/
rm -r $tmpdir
echo "{} done"
'

---

# Summary

This process extracts `.fa` files from multiple `.tar.xz` archives, compresses them with `pigz` (parallel gzip), and moves all compressed files into a single output directory. It uses `xargs` to process up to 35 archives in parallel, each handled inside its own temporary folder to avoid conflicts. Verbose output shows progress for easy monitoring.

---

# Tutorial: Extract and Compress `.fa` Files from Multiple `.tar.xz` Archives Using Parallel Processing

This tutorial explains how to efficiently extract `.fa` files from multiple `.tar.xz` archives, compress them with `pigz`, and collect them in one folder, using your CPU cores in parallel.

---

## Prerequisites

- Linux or macOS terminal
    
- `tar` with `.xz` support
    
- `pigz` (parallel gzip) installed
    
- n CPU cores (or adjust parallel jobs accordingly)
    
- Shell (bash or zsh)
    

---

## Step 1: Prepare the output directory

```bash
mkdir -p output
```

Creates the `output` folder to store compressed files.

---

## Step 2: Run the parallel extraction and compression command

```bash
ls *.tar.xz | xargs -n 1 -P 35 -I{} sh -c '
  echo "Processing archive: {}"
  tmpdir=$(mktemp -d)
  echo "Extracting {} into $tmpdir"
  tar -Jxf "{}" --strip-components=1 -C "$tmpdir" --verbose
  echo "Compressing .fa files in $tmpdir"
  pigz -v -f "$tmpdir"/*.fa
  echo "Moving compressed files to output/"
  mv "$tmpdir"/*.fa.gz output/
  rm -r "$tmpdir"
  echo "Finished processing {}"
'
```

---

### Explanation:

- `ls *.tar.xz` lists all `.tar.xz` archive files.
    
- `xargs -n 1 -P 35 -I{}` runs commands on each file, **one file at a time**, but up to **35 commands in parallel**.
    
- `sh -c '...'` runs a shell script with multiple commands per archive.
    
- A temporary directory is created for safe extraction.
    
- `tar -Jxf` extracts the archive contents, stripping the top-level folder.
    
- `pigz` compresses all `.fa` files in the temp folder, using all CPU cores.
    
- Compressed files are moved to the `output` folder.
    
- Temporary files are cleaned up.
    

---

## Step 3: Verify results

Check your `output/` folder:

```bash
ls output/*.fa.gz
```

You should see all `.fa` files compressed and ready for further use.

---

## Notes

- Adjust `-P 35` according to your CPU cores.
    
- This workflow avoids conflicts by isolating each archive extraction in its own temp folder.
    
- Verbose flags help track progress in the terminal.
    

---

Feel free to customize or ask for an extended version with error handling or logging!