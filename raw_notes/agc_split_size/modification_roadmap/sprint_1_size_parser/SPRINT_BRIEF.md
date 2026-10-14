# Sprint 1: Size String Parser & Parameter Plumbing (`-p <size>` and `-x`)

## 1. Goal & Scope
Implement the CLI parsing logic to accept human-readable size limits (`-p 100M`, `-p 2G`), validate inputs against 64-bit integer overflow, format zero-padded multi-part filenames (`archive.part001.agc`), and plumb parameter state (`target_part_size`, `split_create`, `is_strict`) through `CParams` and `CApplication`.

---

## 2. Time Estimation
| Activity | Description | Estimated Hours |
| :--- | :--- | :--- |
| **Reading & Concepts** | Suffix scaling (K, M, G, T), arithmetic overflow checks, path manipulation | 1.5 hrs |
| **Implementation** | Implement `parse_size_with_suffix`, `make_part_archive_name`, and CLI wiring | 1.5 hrs |
| **Test Writing** | Unit tests for standard prefixes, boundary cases, and string formatting | 1.0 hr |
| **Verification** | Test CLI flag parsing (`agc create -p 500M -o out.agc ...`) | 0.5 hr |
| **Exam & Challenge** | Written conceptual test + hands-on coding challenge in `EXAM.md` | 1.0 hr |
| **Total** | | **~5.5 hrs** |

---

## 3. Architecture & Interface Specs

### Parameter Extensions (`src/app/application.h`)
```cpp
struct CParams
{
    // ... existing parameters ...
    uint64_t target_part_size = 0;   // In bytes
    bool split_create = false;       // Activated when -p is supplied
    bool is_strict = false;          // Activated via -x (caps check interval to <= 10 genomes)
};
```

### Member Function Signatures (`src/app/application.h`)
```cpp
class CApplication
{
    // ...
    uint64_t parse_size_with_suffix(const std::string& s) const;
    std::string make_part_archive_name(const std::string& base_name, uint32_t part_id) const;
    bool create_split();
};
```

### Parser Implementation (`src/app/application.cpp`)
```cpp
uint64_t CApplication::parse_size_with_suffix(const string& s) const
{
    if (s.empty()) return 0;

    uint64_t multiplier = 1;
    string digits = s;
    const char suffix = s.back();

    if (!isdigit(static_cast<unsigned char>(suffix)))
    {
        digits.pop_back();
        switch (suffix)
        {
        case 'K': multiplier = 1000ull; break;
        case 'M': multiplier = 1000ull * 1000ull; break;
        case 'G': multiplier = 1000ull * 1000ull * 1000ull; break;
        case 'T': multiplier = 1000ull * 1000ull * 1000ull * 1000ull; break;
        default:  return 0; // Unknown suffix
        }
    }

    if (digits.empty()) return 0;

    uint64_t value = 0;
    for (char ch : digits)
    {
        if (!isdigit(static_cast<unsigned char>(ch))) return 0;
        const uint64_t digit = static_cast<uint64_t>(ch - '0');
        
        // Overflow check during digit accumulation
        if (value > (numeric_limits<uint64_t>::max() - digit) / 10ull)
            return 0;

        value = value * 10ull + digit;
    }

    // Overflow check during multiplication
    if (value == 0 || value > numeric_limits<uint64_t>::max() / multiplier)
        return 0;

    return value * multiplier;
}
```

### Filename Formatter (`src/app/application.cpp`)
```cpp
string CApplication::make_part_archive_name(const string& base_name, uint32_t part_id) const
{
    filesystem::path base_path(base_name);
    const filesystem::path parent_path = base_path.parent_path();
    const string stem = base_path.stem().string();
    const string extension = base_path.extension().empty() ? ".agc" : base_path.extension().string();

    ostringstream oss;
    oss << stem << ".part" << setw(3) << setfill('0') << part_id << extension;

    if (parent_path.empty())
        return oss.str();

    return (parent_path / oss.str()).string();
}
```

---

## 4. Step-by-Step Task Checklist

- [ ] **Step 1.1:** Add `target_part_size`, `split_create`, and `is_strict` fields to `CParams` in `src/app/application.h`.
- [ ] **Step 1.2:** Declare `parse_size_with_suffix` and `make_part_archive_name` in `CApplication` class.
- [ ] **Step 1.3:** Implement `parse_size_with_suffix` in `src/app/application.cpp` with safe unsigned 64-bit integer overflow protection.
- [ ] **Step 1.4:** Implement `make_part_archive_name` in `src/app/application.cpp` supporting directory paths, custom extensions, and zero-padding.
- [ ] **Step 1.5:** Register `p:` and `x` in `ketopt` argument parsing loop for `create` mode.
- [ ] **Step 1.6:** Add validation logic ensuring `-p` requires `-o` and cannot be combined with concatenated mode (`-c`).
- [ ] **Step 1.7:** Write unit tests verifying parser edge cases and filename generation.

---

## 5. Unit Test Specifications

```cpp
#include "doctest.h"
#include <limits>
#include <cstdint>

// Forward declarations or helper include
uint64_t parse_size_with_suffix(const std::string& s);
std::string make_part_archive_name(const std::string& base_name, uint32_t part_id);

TEST_CASE("SizeParser: Standard Decimal Units") {
    CHECK(parse_size_with_suffix("500") == 500ULL);
    CHECK(parse_size_with_suffix("10K") == 10'000ULL);
    CHECK(parse_size_with_suffix("50M") == 50'000'000ULL);
    CHECK(parse_size_with_suffix("2G") == 2'000'000'000ULL);
    CHECK(parse_size_with_suffix("1T") == 1'000'000'000'000ULL);
}

TEST_CASE("SizeParser: Invalid Formats and Overflows") {
    CHECK(parse_size_with_suffix("") == 0);
    CHECK(parse_size_with_suffix("K") == 0);
    CHECK(parse_size_with_suffix("-50M") == 0);
    CHECK(parse_size_with_suffix("50MB") == 0); // Strict single char suffix
    CHECK(parse_size_with_suffix("abc") == 0);
    
    // Overflow test beyond 64-bit max
    CHECK(parse_size_with_suffix("18446744073709551616") == 0);
    CHECK(parse_size_with_suffix("999999999999999999T") == 0);
}

TEST_CASE("FilenameFormatter: Part Archive Numbering") {
    CHECK(make_part_archive_name("out.agc", 1) == "out.part001.agc");
    CHECK(make_part_archive_name("out.agc", 42) == "out.part042.agc");
    CHECK(make_part_archive_name("out.agc", 1000) == "out.part1000.agc");
    CHECK(make_part_archive_name("/data/archives/collection.agc", 5) == "/data/archives/collection.part005.agc");
    CHECK(make_part_archive_name("raw_archive", 1) == "raw_archive.part001.agc");
}
```

---

## 6. Acceptance Criteria

1. `parse_size_with_suffix` correctly parses valid positive integers with `K`, `M`, `G`, `T` suffixes.
2. Arithmetic overflow checks properly reject numbers exceeding `UINT64_MAX` without undefined behavior.
3. `make_part_archive_name` cleanly preserves directory paths and injects `.part%03d` before the extension.
4. Running `agc create -p 100M input.fa` without `-o` prints `Split create mode requires -o` and cleanly terminates.
