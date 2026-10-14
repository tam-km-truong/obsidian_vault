# Sprint 1 Study Guide: Safe Integer Parsing & Path Formatting

In this sprint, you explore defensive numeric parsing and filesystem string manipulation in C++.

---

## 1. Key Concepts to Understand

### A. Preventing Integer Overflow Before It Happens
When parsing user input into integer types, checking for overflow *after* calculating `value = value * 10 + digit` is **too late**:
- If `value` is signed, overflow triggers **Undefined Behavior (UB)**.
- If `value` is unsigned, overflow wraps around modulo $2^{64}$, yielding a small number that passes checks unnoticed.

To safely prevent overflow in `uint64_t`:
1. **Digit accumulation check**:
   ```cpp
   if (value > (std::numeric_limits<uint64_t>::max() - digit) / 10ull) {
       // Multiplying by 10 and adding digit would overflow!
       return 0; // Or return std::nullopt
   }
   value = value * 10ull + digit;
   ```
2. **Multiplier check**:
   ```cpp
   if (value > std::numeric_limits<uint64_t>::max() / multiplier) {
       // value * multiplier would overflow!
       return 0;
   }
   return value * multiplier;
   ```

### B. Decimal vs Binary Units: The 1000 vs 1024 Decision
In AGC's codebase, `parse_size_with_suffix` uses SI decimal multipliers:
- `1K` = $1,000$ bytes
- `1M` = $1,000,000$ bytes
- `1G` = $1,000,000,000$ bytes
- `1T` = $1,000,000,000,000$ bytes

Why? Disk storage and file sizes reported by modern filesystems (macOS Finder, `ls -lh`, cloud bucket quotas) predominantly follow decimal units.

### C. Manipulating Paths with `std::filesystem::path`
C++17 introduced `<filesystem>`, which provides cross-platform path parsing:
- `path::parent_path()`: Extracts `/data/archives/` from `/data/archives/collection.agc`.
- `path::stem()`: Extracts `collection` from `/data/archives/collection.agc`.
- `path::extension()`: Extracts `.agc` from `/data/archives/collection.agc`.
- `operator/`: Safely concatenates path components with the correct OS separator (`/` or `\\`).

### D. Zero-Padded Integer Streams (`<iomanip>`)
To format filenames such that lexical sorting matches numerical order (`part001`, `part002`, ..., `part010`, ..., `part100`):
```cpp
std::ostringstream oss;
oss << stem << ".part" << std::setw(3) << std::setfill('0') << part_id << extension;
```
- `std::setw(3)`: Sets minimum width to 3 characters.
- `std::setfill('0')`: Fills unused width with character `'0'`.

---

## 2. Recommended Readings & Documentation

1. **cppreference: `std::numeric_limits`**:
   [https://en.cppreference.com/w/cpp/types/numeric_limits](https://en.cppreference.com/w/cpp/types/numeric_limits)
2. **cppreference: `std::filesystem::path`**:
   [https://en.cppreference.com/w/cpp/filesystem/path](https://en.cppreference.com/w/cpp/filesystem/path)
3. **SEI CERT C++ Coding Standard: INT30-CPP (Integer Overflow Prevention)**:
   [https://wiki.sei.cmu.edu/confluence/display/cplusplus/INT30-CPP.+Ensure+that+unsigned+integer+operations+do+not+wrap](https://wiki.sei.cmu.edu/confluence/display/cplusplus/INT30-CPP.+Ensure+that+unsigned+integer+operations+do+not+wrap)

---

## 3. Common Gotchas & Personal Notes

1. **`isdigit` on Signed `char`**:
   Passing a `char` directly to `std::isdigit(c)` without casting to `unsigned char` can trigger undefined behavior if `char` is signed and negative. Always write:
   `isdigit(static_cast<unsigned char>(c))`
2. **Missing Extensions**:
   If the user runs `agc create -p 500M -o my_archive ...` without providing `.agc` in the output name, `path.extension().empty()` is true. Defaulting to `.agc` ensures clean output files.

---

## 4. 10-Minute Mini Practice Exercise

Write a standalone test verifying prefix padding:

```cpp
#include <iostream>
#include <sstream>
#include <iomanip>
#include <filesystem>

std::string formatPart(const std::string& pathStr, int id) {
    std::filesystem::path p(pathStr);
    std::ostringstream oss;
    oss << p.stem().string() << ".part" << std::setw(3) << std::setfill('0') << id << (p.extension().empty() ? ".agc" : p.extension().string());
    if (p.parent_path().empty()) return oss.str();
    return (p.parent_path() / oss.str()).string();
}

int main() {
    std::cout << formatPart("test.agc", 1) << "\n";       // test.part001.agc
    std::cout << formatPart("/tmp/test.agc", 12) << "\n";  // /tmp/test.part012.agc
    std::cout << formatPart("sample", 999) << "\n";       // sample.part999.agc
    return 0;
}
```
