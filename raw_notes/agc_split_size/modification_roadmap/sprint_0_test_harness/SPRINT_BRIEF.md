# Sprint 0: Test Harness Setup & C++20 Toolchain Fundamentals

## 1. Goal & Scope
Set up a clean, isolated unit testing harness for AGC using the lightweight single-header framework [doctest](https://github.com/doctest/doctest). The testing infrastructure must integrate with AGC's GNU Make build system (`makefile` / `refresh.mk`) and compile under C++20 (`-std=c++2a`) without interfering with or altering the release `agc` binary.

---

## 2. Time Estimation
| Activity | Description | Estimated Hours |
| :--- | :--- | :--- |
| **Reading & Concepts** | AGC build system, Makefile targets, C++20 toolchain, Apple Silicon flags | 1.5 hrs |
| **Implementation** | Add `doctest.h`, create `tests/` directory, configure Makefile target | 1.5 hrs |
| **Test Writing** | Write smoke test cases for core AGC types (`CKmer`, `contig_t`) | 1.0 hr |
| **Verification & Debugging** | Build and run under macOS (`PLATFORM=m1`) / Linux x86_64 | 0.5 hr |
| **Exam & Challenge** | Conceptual exam & CLI string validator challenge in `EXAM.md` | 1.0 hr |
| **Total** | | **~5.5 hrs** |

---

## 3. Architecture & Interface Specs

### Directory Layout
```
agc-split-size/
├── makefile                        # AGC main Makefile
├── refresh.mk                      # Build configuration rules
├── tests/
│   ├── doctest.h                   # Single-header test framework
│   ├── test_main.cpp               # Test runner main (DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN)
│   └── test_smoke.cpp              # Initial verification test suite
└── bin/
    ├── agc                         # Production binary
    └── agc_tests                   # Isolated unit test runner
```

### Build Invocation & Platform Flags
AGC compiles with C++20. On macOS (Apple Silicon M1/M2/M3/M4):
```bash
gmake CXX="g++-13 -D_Static_assert=static_assert" PLATFORM=m1 bin/agc_tests
```
On Linux x86_64:
```bash
make bin/agc_tests
```

### Test Target in `makefile`
```makefile
TEST_OBJS = $(OBJ_DIR)/test_main.o $(OBJ_DIR)/test_smoke.o $(OBJ_DIR)/kmer.o

$(BIN_DIR)/agc_tests: $(TEST_OBJS)
	$(CXX) $(CFLAGS) -o $@ $^ $(CLIB)

test: $(BIN_DIR)/agc_tests
	./$(BIN_DIR)/agc_tests
```

---

## 4. Step-by-Step Task Checklist

- [ ] **Step 0.1:** Create `tests/` directory in repository root.
- [ ] **Step 0.2:** Download `doctest.h` into `tests/doctest.h`.
- [ ] **Step 0.3:** Create `tests/test_main.cpp`:
  ```cpp
  #define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN
  #include "doctest.h"
  ```
  *(Keeping runner definition in an isolated compilation unit prevents re-compilation overhead).*
- [ ] **Step 0.4:** Create `tests/test_smoke.cpp` testing environment types, basic AGC structs, and 64-bit word size.
- [ ] **Step 0.5:** Add `agc_tests` and `test` targets to `makefile`.
- [ ] **Step 0.6:** Compile and run test suite:
  ```bash
  gmake PLATFORM=m1 test
  ```

---

## 5. Unit Test Specifications

Create `tests/test_smoke.cpp`:

```cpp
#include "doctest.h"
#include <cstdint>
#include <string>
#include <vector>

TEST_CASE("SmokeTest: Basic C++20 Environment") {
    CHECK(sizeof(uint64_t) == 8);
    CHECK(sizeof(uint32_t) == 4);
    CHECK(sizeof(size_t) == 8);

    // Verify 64-bit pointer architecture
    void* ptr = nullptr;
    CHECK(sizeof(ptr) == 8);
}

TEST_CASE("SmokeTest: Contig Buffer Semantics") {
    using contig_t = std::vector<uint8_t>;
    contig_t ctg = {0, 1, 2, 3}; // 2-bit encoded bases (A, C, G, T)
    
    CHECK(ctg.size() == 4);
    ctg.push_back(0xff); // Splitter delimiter byte used in CSegment
    CHECK(ctg.back() == 0xff);
    CHECK(ctg.size() == 5);
}

TEST_CASE("SmokeTest: doctest Floating Point Tolerances") {
    double estimated_ratio = 0.95;
    CHECK(estimated_ratio == doctest::Approx(0.950001).epsilon(0.001));
}
```

---

## 6. Acceptance Criteria

1. Running `gmake test` compiles `tests/test_main.cpp` and `tests/test_smoke.cpp` into `bin/agc_tests`.
2. The executable runs cleanly and reports all test cases passed (`[doctest] Status: SUCCESS!`).
3. Production binary build `gmake bin/agc` remains completely untouched and unaffected.
