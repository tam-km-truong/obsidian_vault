**lock-free, multithreaded hash table**

Uses open addressing with quadratic probing for collision resolution.
___


Update the hash table concurrently using the <�strong>compare-and-swap (CAS)
- **Comparison**: The value at a memory location is compared with an expected value.
- **Swap**: If the values match, the memory location is updated to a new value.
- **Failure Case**: If the values don’t match, no update occurs, and the operation returns the current value.

___

bit-packing and key compression to reduce memory overhead

**Bit-packing**: Compactly stores data by tightly arranging bits in memory instead of aligning them to word boundaries

**Key compression**: Reduces the storage required for hash table keys by encoding only the necessary information. For example, Jellyfish stores only high bits of the hashed k-mer and deduces the rest based on the hash table's structure and the key’s position.

___

Uses a min-heap for fast sorting and merging of hash tables when memory is insufficient.

a **min-max heap** is a complete [binary tree](https://en.wikipedia.org/wiki/Binary_tree "Binary tree") [data structure](https://en.wikipedia.org/wiki/Data_structure "Data structure") which combines the usefulness of both a [min-heap](https://en.wikipedia.org/wiki/Min-heap "Min-heap") and a [max-heap](https://en.wikipedia.org/wiki/Max-heap "Max-heap"), that is, it provides constant time retrieval and logarithmic time removal of both the minimum and maximum elements in it