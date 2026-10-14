# Sprint 6: Partition Orchestration Loop & End-to-End Validation

## 1. Goal & Scope
Implement `CApplication::create_split` in `src/app/main.cpp`, driving the outer partition orchestration loop. The coordinator partitions a master collection of genomes across multiple output archives (`archive.part001.agc`, `archive.part002.agc`, ...), assigns the first genome of each part as its local reference, and validates complete roundtrip integrity with AGC's extraction subcommands (`getcol` and `getset`).

---

## 2. Time Estimation
| Activity | Description | Estimated Hours |
| :--- | :--- | :--- |
| **Reading & Concepts** | AGC multi-part reference mechanics, cursor management, archive closure | 1.5 hrs |
| **Implementation** | Implement `create_split()` in `src/app/main.cpp` and dispatch in `main()` | 1.5 hrs |
| **End-to-End Testing** | Compress sample datasets under `-p 500K`, `-p 10M`, `-p 50M` | 1.5 hrs |
| **Integrity Verification** | Validate decompressed FASTAs against original input sequences using SHA-256 | 1.0 hr |
| **Exam & Challenge** | Written conceptual test + partition validator script in `EXAM.md` | 1.0 hr |
| **Total** | | **~6.5 hrs** |

---

## 3. Architecture & Interface Specs

### Driver Loop Implementation (`src/app/main.cpp`)
```cpp
bool CApplication::create_split()
{
    sanitize_input_file_names(execution_params.input_names);

    if (execution_params.input_names.empty())
    {
        cerr << "No input genomes" << endl;
        return false;
    }

    uint32_t part_id = 1;
    size_t input_id = 0;

    while (input_id < execution_params.input_names.size())
    {
        const string part_name = make_part_archive_name(execution_params.out_archive_name, part_id);
        const string reference_file = execution_params.input_names[input_id];

        if (execution_params.verbosity() > 0) {
            cerr << "Creating-split mode; currently " << part_name 
                 << " with reference " << reference_file << "\n";
            cerr << "Target size: " << execution_params.target_part_size << " bytes.\n";
            if (execution_params.is_strict)
                cerr << "Strict mode on.\n";
        }

        CAGCCompressor agc_c;

        bool r = agc_c.Create(
            part_name,
            execution_params.pack_cardinality(),
            execution_params.k(),
            reference_file,
            execution_params.segment_size(),
            execution_params.min_match_length(),
            execution_params.concatenated_genomes,
            execution_params.adaptive_compression,
            execution_params.verbosity(),
            execution_params.no_threads(),
            execution_params.fallback_frac());

        if (!r)
        {
            cerr << "Cannot create archive " << part_name << endl;
            return false;
        }

        // Prepare remaining samples for this part starting at input_id
        vector<pair<string, string>> v_remaining_samples;
        for (size_t i = input_id; i < execution_params.input_names.size(); ++i)
        {
            const string& fn = execution_params.input_names[i];
            string sample_name = std::filesystem::path(fn).stem().string();
            remove_common_suffixes(sample_name);
            v_remaining_samples.emplace_back(sample_name, fn);
        }

        size_t consumed_count = 0;
        if (r)
            consumed_count = agc_c.AddSampleSplit(
                v_remaining_samples, 
                execution_params.no_threads(), 
                execution_params.target_part_size,
                execution_params.is_strict);

        if (execution_params.verbosity() > 0)
            cerr << "Consumed count: " << consumed_count << " genomes.\n";

        if (r && execution_params.store_cmd_line)
            agc_c.AddCmdLine(cmd_line);

        r &= agc_c.Close(execution_params.no_threads());

        if (!r)
        {
            cerr << "Cannot close archive " << part_name << endl;
            return false;
        }

        // Advance cursor by the number of genomes actually stored in this part
        input_id += consumed_count;
        ++part_id;
    }

    return true;
}
```

---

## 4. Multi-Part Architecture Details

```
Input Genomes: [ G0, G1, G2, G3, G4, G5, G6, G7, G8, G9 ]
                 |_________________|    |______________|
                       Part 1                Part 2
               (Ref: G0, Members: G0-G4) (Ref: G5, Members: G5-G9)
```

1. **Self-Contained Partition Archives**:
   Each partition `.agc` file is an independent, valid AGC archive with its own internal directory and reference sequence.
2. **Local Reference Selection**:
   In AGC, the reference genome serves as the foundation for splitters and delta encoding. Setting `reference_file = input_names[input_id]` ensures each part selects its first member as reference with zero external dependencies.
3. **Cursor Progression**:
   `input_id += consumed_count` guarantees every genome is assigned to exactly one archive part without omissions or duplicates.

---

## 5. Step-by-Step Task Checklist

- [ ] **Step 6.1:** Wire `create_split()` into `CApplication::Run` in `src/app/main.cpp`.
- [ ] **Step 6.2:** Implement input file sanitization and empty list validation.
- [ ] **Step 6.3:** Implement outer `while (input_id < input_names.size())` coordinator loop.
- [ ] **Step 6.4:** Configure per-part naming and local reference selection.
- [ ] **Step 6.5:** Invoke `AddSampleSplit` and record `consumed_count`.
- [ ] **Step 6.6:** Advance `input_id` and close each archive cleanly.
- [ ] **Step 6.7:** Verify multi-part extraction and roundtrip identity using `agc getcol` and `diff`.

---

## 6. End-to-End Verification Pipeline

### 1. Partition Compression
```bash
./bin/agc create -p 500K -o test_split.agc toy_ex/*.fa
```
*Expected Output:*
- `test_split.part001.agc`
- `test_split.part002.agc`
- ...

### 2. Archive Inspection
```bash
./bin/agc list test_split.part001.agc
./bin/agc list test_split.part002.agc
```

### 3. Bitwise Roundtrip Decompression
```bash
mkdir -p scratch/decompressed
./bin/agc getcol test_split.part001.agc > scratch/decompressed/part001.fa
# Verify no data loss or corruption
```

---

## 7. Acceptance Criteria

1. Running `agc create -p <size> -o out.agc ...` splits genomes into sequentially numbered part files (`out.part001.agc`, `out.part002.agc`, ...).
2. Every input genome is present in exactly one part archive.
3. Each archive part decompresses cleanly using standard `agc getcol` or `agc getset` without errors.
4. Final archive file sizes stay bounded within target limits.
