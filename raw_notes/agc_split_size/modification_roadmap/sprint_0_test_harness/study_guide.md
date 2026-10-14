# Sprint 0 Study Guide: C++20 Toolchain & Test-Driven Verification

In this sprint, you establish the foundation for modifying and verifying AGC: understanding AGC's high-performance C++20 build pipeline and using modern test frameworks.

---

## 1. Key Concepts to Understand

### A. The C++20 Compilation Model in AGC
AGC is engineered for extreme throughput on modern CPU architectures (SIMD, Radix sort, multi-threading). It uses `-std=c++2a` (C++20).
Key compiler behaviors to keep in mind:
- **Separation of Interface and Implementation**: Headers declare class layouts, sizes, and member functions. Modifying a class member in a header (like adding fields to `CParams` or `CSegment`) causes any compilation unit including that header to recompile.
- **Linkage and Static Assertions**: On modern macOS with Homebrew GCC (e.g. `g++-13`), C11 `_Static_assert` macros from third-party C libraries (like mimalloc or zstd) may collide with C++ keywords. Passing `-D_Static_assert=static_assert` ensures seamless C/C++ cross-compatibility.

### B. Single-Header Test Frameworks (`doctest`)
Unlike heavy frameworks requiring compiled static libraries (such as GoogleTest), `doctest` is distributed as a single header file (`doctest.h`).
- **Compilation Speed**: The macro `#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN` expands to the complete command-line test runner and `main()` function. By putting this in `tests/test_main.cpp` alone, `doctest.h` is only parsed once for the runner.
- **Assertions**:
  - `CHECK(expr)`: Evaluates expression; if false, logs failure but continues execution.
  - `REQUIRE(expr)`: Evaluates expression; if false, aborts current test case immediately.
  - `CHECK_THROWS(expr)`: Verifies that an exception is thrown.

```cpp
// tests/test_main.cpp
#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
#include "doctest.h"
```

```cpp
// tests/test_feature.cpp
#include "doctest.h"
#include "../src/app/application.h"

TEST_CASE("Feature: Basic Math") {
    int x = 10;
    CHECK(x * 2 == 20);
}
```

### C. Makefile Target Organization
In GNU Make:
```makefile
target: prerequisites
	recipe (must start with a TAB character)
```
Using automatic variables:
- `$@`: The file name of the target of the rule.
- `$^`: The names of all the prerequisites, with spaces between them.
- `$<`: The name of the first prerequisite.

---

## 2. Recommended Readings & Documentation

1. **doctest Tutorial and Features**:
   [https://github.com/doctest/doctest/blob/master/doc/markdown/tutorial.md](https://github.com/doctest/doctest/blob/master/doc/markdown/tutorial.md)
2. **GNU Make Manual (Rule Syntax & Pattern Matching)**:
   [https://www.gnu.org/software/make/manual/html_node/Rule-Syntax.html](https://www.gnu.org/software/make/manual/html_node/Rule-Syntax.html)
3. **C++20 Language Features Overview (cppreference)**:
   [https://en.cppreference.com/w/cpp/20](https://en.cppreference.com/w/cpp/20)

---

## 3. Common Gotchas & Personal Notes

1. **Makefile Tabs vs Spaces**:
   A recipe line MUST start with a real `Tab` character (`\t`). If your editor replaces tabs with 4 spaces, `make` will fail with `*** missing separator. Stop.`
2. **Header Pollution in Tests**:
   Keep unit test files focused. Avoid including huge headers like `<windows.h>` or broad umbrella headers unless strictly required by the class under test.
3. **Apple Silicon Architecture**:
   On macOS arm64, AVX2 and AVX-512 instructions are not available natively. Always compile with `PLATFORM=m1` or appropriate non-AVX flags.

---

## 4. 10-Minute Mini Practice Exercise

Create a minimal test file in `tests/test_practice.cpp` with a simple data structure and run it:

```cpp
#include "doctest.h"
#include <string>
#include <algorithm>

std::string reverseString(std::string s) {
    std::reverse(s.begin(), s.end());
    return s;
}

TEST_CASE("Practice: String Reversal") {
    CHECK(reverseString("AGC") == "CGA");
    CHECK(reverseString("") == "");
    CHECK(reverseString("A") == "A");
}
```
Compile and test:
```bash
g++-13 -std=c++20 -I. tests/test_main.cpp tests/test_practice.cpp -o bin/practice_test
./bin/practice_test
```
