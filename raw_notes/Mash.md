#mash
### In a nutshell
Mash uses the MinHash technique to create "sketches" of sequences,small, representation of sequences
Mash distance, an estimate of the mutation rate between sequences. I is calculated from the fraction of shared k-mers (Jaccard index) between MinHash sketches.

**MinHash sketches**:

1. **Generate k-mers**
2. **Hash each k-mer** to a number
3. **Select the smallest hashes**: Retain the _s_ smallest hash values (the "sketch size")
- **Smaller k values**:
    
    - more divergent sequences (higher sensitivity).
    - May lead to chance matches between unrelated sequences (lower specificity).
- **Larger k values**:
    
    - Provide greater specificity by reducing chance matches.
    - Lose sensitivity for divergent sequences.

Hash using MurmurHash3 for kmer hashing

mash sketch -l leaves_order_path.txt -o ref_sketches_20k -p 12 -s 10000

mash dist 10k/ref_sketches_10k.msh -l m_tuber_path.txt

mash dist reference.txt.msh genome.fa.gz | cut -f3 | xargs | tr ' ' ','

compute_distance_matrix.py leaves_order_with_path.txt.msh s_enterica_queries.txt -l -o output.csv -t 14

`for p in experiments/040_species_independent/random_selection_strategy/tree/part_*.txt; do base=$(basename "$p" .txt); mash sketch -l "$p" -o experiments/040_species_independent/random_selection_strategy/references/"$base" -p 12 -s 10000; done`
mash sketch for multiple files loop