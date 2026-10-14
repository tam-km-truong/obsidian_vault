# Sprint 1 Mastery Checkpoint & Exam

This checkpoint tests your understanding of arithmetic overflow prevention, C++ filesystem operations, and CLI option validation.

---

## Part 1: Written Conceptual Exam

### Question 1: Unsigned Integer Overflow
Consider the following attempt to parse a number from a string:

```cpp
uint64_t parse(const std::string& s) {
    uint64_t val = 0;
    for (char c : s) {
        val = val * 10 + (c - '0');
    }
    return val;
}
```

1. If the input string is `"18446744073709551616"` ($2^{64}$), what will `val` hold upon return on a 64-bit platform?
2. Why does the C++ standard not flag this as undefined behavior for `uint64_t`?
3. How does AGC's `parse_size_with_suffix` detect this condition before arithmetic wrapping occurs?

---

### Question 2: Filesystem Path Tokenization
Given the input path `base_name = "data/runs/exp1.filtered.agc"`:
1. What does `std::filesystem::path(base_name).stem()` return?
2. What does `std::filesystem::path(base_name).extension()` return?
3. What is the generated part archive name for `part_id = 5`?

---

### Question 3: Spot the Bug — Safe Multiplying
Identify the vulnerability in this size scaling function:

```cpp
uint64_t applyMultiplier(uint64_t base, char unit) {
    uint64_t mult = 1;
    if (unit == 'M') mult = 1000000ULL;
    else if (unit == 'G') mult = 1000000000ULL;
    else if (unit == 'T') mult = 1000000000000ULL;

    return base * mult;
}
```
Explain the failure case when `base = 50000000` and `unit = 'T'`. How must this be fixed?

---

## Part 2: Hands-on Scripting / Coding Challenge

### Objective
In `scratch/sprint1_challenge.cpp`, implement a command-line utility that accepts a base archive name and a target byte string, and prints the generated partition plan for 10 simulated parts.

### Requirements
1. Implement `uint64_t parseSize(std::string_view s)` handling `K`, `M`, `G`, `T` with full overflow checks.
2. Implement `std::string getPartName(std::string_view base, uint32_t part_id)`.
3. If valid, print the part names `part001` through `part010` and the target byte count.
4. If invalid, print an informative error message and return `EXIT_FAILURE`.

---

<details>
<summary><b>Click to reveal Answer Key & Grading Rubric</b></summary>

### Part 1 Answers
1. **Unsigned Integer Overflow:**
   - $2^{64} = 18,446,744,073,709,551,616 \equiv 0 \pmod{2^{64}}$. `val` will silently wrap around to `0`.
   - The C++ standard explicitly defines unsigned integer arithmetic to operate modulo $2^N$ (no undefined behavior for unsigned types, unlike signed integers).
   - In AGC:
     ```cpp
     if (value > (std::numeric_limits<uint64_t>::max() - digit) / 10ull)
         return 0; // Rejected before multiplication
     ```

2. **Filesystem Path Tokenization:**
   - `.stem()` returns `"exp1.filtered"`.
   - `.extension()` returns `".agc"`.
   - Generated part name: `"data/runs/exp1.filtered.part005.agc"`.

3. **Spot the Bug — Safe Multiplying:**
   - `50,000,000 * 1,000,000,000,000 = 50 * 10^{18} = 50,000,000,000,000,000,000 > UINT64_MAX` ($18.44 \times 10^{18}$).
   - This causes unsigned wrapping, returning `13,106,896,170,295,427,072`, which is an unexpected value.
   - *Fix:*
     ```cpp
     if (mult > 0 && base > std::numeric_limits<uint64_t>::max() / mult)
         return 0; // Error / overflow
     return base * mult;
     ```

### Part 2 Solution

```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <filesystem>
#include <sstream>
#include <iomanip>
#include <limits>
#include <cctype>

uint64_t parseSize(std::string_view s) {
    if (s.empty()) return 0;
    uint64_t mult = 1;
    char suffix = s.back();
    std::string digits(s);
    if (!std::isdigit(static_cast<unsigned char>(suffix))) {
        digits.pop_back();
        if (suffix == 'K' || suffix == 'k') mult = 1000ULL;
        else if (suffix == 'M' || suffix == 'm') mult = 1000000ULL;
        else if (suffix == 'G' || suffix == 'g') mult = 1000000000ULL;
        else if (suffix == 'T' || suffix == 't') mult = 1000000000000ULL;
        else return 0;
    }
    if (digits.empty()) return 0;
    uint64_t val = 0;
    for (char c : digits) {
        if (!std::isdigit(static_cast<unsigned char>(c))) return 0;
        uint64_t d = static_cast<uint64_t>(c - '0');
        if (val > (std::numeric_limits<uint64_t>::max() - d) / 10ULL) return 0;
        val = val * 10ULL + d;
    }
    if (val > std::numeric_limits<uint64_t>::max() / mult) return 0;
    return val * mult;
}

std::string getPartName(std::string_view base, uint32_t id) {
    std::filesystem::path p(base);
    std::string stem = p.stem().string();
    std::string ext = p.extension().empty() ? ".agc" : p.extension().string();
    std::ostringstream oss;
    oss << stem << ".part" << std::setw(3) << std::setfill('0') << id << ext;
    if (p.parent_path().empty()) return oss.str();
    return (p.parent_path() / oss.str()).string();
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " <base_archive> <target_size>\n";
        return 1;
    }
    uint64_t bytes = parseSize(argv[2]);
    if (bytes == 0) {
        std::cerr << "Error: Invalid size format or overflow: " << argv[2] << "\n";
        return 1;
    }
    std::cout << "Target Part Size: " << bytes << " bytes\n";
    for (uint32_t i = 1; i <= 10; ++i) {
        std::cout << "  Part " << i << ": " << getPartName(argv[1], i) << "\n";
    }
    return 0;
}
```
</details>
