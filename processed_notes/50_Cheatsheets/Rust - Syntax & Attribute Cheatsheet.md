---
category: cheatsheet
tags:
  - rust
  - programming
  - syntax
source_raw: "[[Rust]]"
status: processed
---

# Rust - Syntax & Attribute Cheatsheet

## Attribute Syntax Overview
Rust attributes provide metadata annotations to crates, modules, structs, and functions.

```rust
// Inner Attribute (applies to enclosing item, e.g. the whole module or crate)
#![inner_attribute]

// Outer Attribute (applies to the item immediately following it)
#[outer_attribute]
```

## Common Outer Attributes

### 1. Derive Macros
Automatically generates trait implementations for structs and enums:
```rust
#[derive(Debug, Clone, PartialEq)]
struct Rectangle {
    width: u32,
    height: u32,
}
```

### 2. Conditional Compilation
```rust
#[cfg(target_os = "linux")]
fn linux_only_optimization() {
    // Linux-specific system calls
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
```

### 3. Compiler Warnings & Lints
```rust
#[allow(dead_code)]
fn unused_helper() {}

#[inline(always)]
fn fast_hash_calculation(kmer: u64) -> u64 {
    kmer.rotate_left(5)
}
```

## Related Cheatsheets & Tools
- [[CLI - General Shell Utilities & Measuring]] – Shell and compilation recipes
- [[miniphy2 - Workflow Specifications & CLI]] – High-performance tools implemented in Rust
