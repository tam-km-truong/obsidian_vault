# Sprint 0 Mastery Checkpoint & Exam

This checkpoint verifies your understanding of the C++20 compilation model, GNU Make build mechanics, and unit test frameworks.

---

## Part 1: Written Conceptual Exam

### Question 1: Compilation Units & One Definition Rule (ODR)
Explain why defining `#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN` in multiple `.cpp` files causes a linker error. What does the One Definition Rule (ODR) state regarding non-inline function definitions in C++?

---

### Question 2: Spot the Bug — Build Recipe
Examine the following snippet from a GNU Makefile:

```makefile
test_runner: tests/test_main.o tests/test_smoke.o
    $(CXX) -o test_runner $^ -lzstd
```

1. If the recipe above fails with `*** missing separator. Stop.`, what is the most likely whitespace defect?
2. What do automatic variables `$@` and `$^` represent in a GNU Make recipe?
3. Rewrite the rule using modern best practices and automatic variables.

---

### Question 3: Assertions in Test Frameworks
In `doctest`, what is the runtime difference between `CHECK(condition)` and `REQUIRE(condition)`? Under what circumstances is `REQUIRE` mandatory to prevent undefined behavior or memory access crashes in a unit test?

---

## Part 2: Hands-on Scripting / Coding Challenge

### Objective
Create a standalone verification program in `scratch/test_harness_challenge.cpp` that implements a custom mini-test framework without third-party dependencies.

### Requirements
1. Implement macros `ASSERT_EQUAL(actual, expected)` and `ASSERT_TRUE(expr)` that print:
   - File name and line number on failure (`__FILE__`, `__LINE__`).
   - The failing expression string.
   - Return non-zero exit code if any assertion fails.
2. Implement and test a function `bool isDnaValid(std::string_view seq)` which returns `true` if and only if `seq` contains valid uppercase/lowercase DNA characters (`A`, `C`, `G`, `T`, `N`).
3. Add a `main()` function running at least 5 test assertions.

---

<details>
<summary><b>Click to reveal Answer Key & Grading Rubric</b></summary>

### Part 1 Answers
1. **Compilation Units & ODR:**
   - `#define DOCTEST_CONFIG_IMPLEMENT_WITH_MAIN` emits the actual definition of `int main(int, char**)` and the doctest test registry engine.
   - If included in multiple `.cpp` translation units, each translation unit will define the identical symbol `main()`.
   - When the linker attempts to merge object files into an executable, it encounters duplicate symbol definitions, violating the One Definition Rule (ODR) and triggering a link error (`duplicate symbol _main`).

2. **Spot the Bug — Build Recipe:**
   - *Whitespace Defect:* The command line begins with spaces instead of an ASCII Tab (`\t`).
   - *Variables:* `$@` is the target (`test_runner`), and `$^` is the complete list of prerequisites (`tests/test_main.o tests/test_smoke.o`).
   - *Rewritten rule:*
     ```makefile
     test_runner: tests/test_main.o tests/test_smoke.o
     	$(CXX) $(LDFLAGS) -o $@ $^ $(LIBS) -lzstd
     ```

3. **Assertions:**
   - `CHECK(cond)` records the failure if false, but execution continues down the remainder of the test body.
   - `REQUIRE(cond)` aborts the test function immediately upon failure (using an internal exception or early return).
   - `REQUIRE` is mandatory when checking pointer nullability or container bounds before dereferencing:
     ```cpp
     REQUIRE(ptr != nullptr);
     CHECK(ptr->value == 42); // If we used CHECK on ptr, a null ptr would cause a SEGV here!
     ```

### Part 2 Solution

```cpp
#include <iostream>
#include <string_view>
#include <ccstdlib>

#define ASSERT_TRUE(expr) \
    if (!(expr)) { \
        std::cerr << "FAIL [" << __FILE__ << ":" << __LINE__ << "]: " #expr " is false!\n"; \
        g_failures++; \
    } else { \
        std::cout << "PASS: " #expr "\n"; \
    }

static int g_failures = 0;

bool isDnaValid(std::string_view seq) {
    for (char c : seq) {
        char u = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
        if (u != 'A' && u != 'C' && u != 'G' && u != 'T' && u != 'N')
            return false;
    }
    return true;
}

int main() {
    ASSERT_TRUE(isDnaValid("ACGTN"));
    ASSERT_TRUE(isDnaValid("acgtn"));
    ASSERT_TRUE(isDnaValid(""));
    ASSERT_TRUE(!isDnaValid("ACGTX"));
    ASSERT_TRUE(!isDnaValid("1234"));

    if (g_failures > 0) {
        std::cerr << "Total failures: " << g_failures << "\n";
        return EXIT_FAILURE;
    }
    std::cout << "All assertions passed successfully!\n";
    return EXIT_SUCCESS;
}
```
</details>
