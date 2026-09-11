**Syntax**  
_InnerAttribute_ :  
   `#` `!` `[` _Attr_ `]`

_OuterAttribute_ :  
   `#` `[` _Attr_ `]`
   
`#[outer_attribute]` applies to the [item](https://doc.rust-lang.org/stable/reference/items.html) immediately following it. Some examples of items are: a function, a module declaration, a constant, a structure, an enum. Here is an example where attribute `#[derive(Debug)]` applies to the struct `Rectangle`:

```rust
    #[derive(Debug)]
    struct Rectangle {
        width: u32,
        height: u32,
    }
```

- `#![inner_attribute]` applies to the enclosing [item](https://doc.rust-lang.org/stable/reference/items.html) (typically a module or a crate). In other words, this attribute is interpreted as applying to the entire scope in which it's placed. Here is an example where `#![allow(unused_variables)]` applies to the whole crate (if placed in `main.rs`):
    

```rust
#![allow(unused_variables)]

fn main() {
    let x = 3; // This would normally warn about an unused variable.
}
```

___

