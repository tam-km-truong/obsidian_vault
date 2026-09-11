# Presentation Transcript (Polished)

Good morning everyone. I am very happy to be here.

I am a second-year PhD student at GenScale team from Inria Rennes. My supervisors are Dominic, Pierre, and Karen. Pierre is here today.

Today, I will present the current state of my PhD work. The topic is improving phylogenetic ordering and matching of million-genome collections. The objective is to reduce storage requirements and enable faster genome retrieval.

---

## Context

Modern sequencing technologies are generating bacterial genomes at an exponential rate.

Here is a snapshot of the National Center for Biotechnology Information (NCBI) database from last year. Ten years ago, there were approximately 100,000 genomes in the database. When I checked last week, the number had surpassed 3 million genomes.

In addition to NCBI, there are many curated databases central to microbiome research. Examples include:

- AllTheBacteria
    
- Genome Taxonomy Database (GTDB)
    
- 661k
    
- RefSeq
    

These databases differ in size and composition. Some contain only isolate assemblies. More recently, there is an increasing number of MAGs (metagenome-assembled genomes). Together, including other collections not listed here, we already exceed 10 million genomes.

The main challenge is distribution. For most databases, users must download genomes individually.

---

## Existing Compression Techniques

Genome compression is a well-studied problem.

General-purpose compressors (e.g., gzip, xz) are not specialized for microbial data.

Specialized tools include:

- MBGC — handles repetitive components effectively.
    
- AGC — supports fast genome extraction.
    
- Phylogenetic compression — reorders genomes based on evolutionary relationships to enhance compressibility.
    

Phylogenetic compression can achieve one to two orders of magnitude improvement over prior protocols using gzip.

An implementation for assemblies is MiniPhy.

The key challenge is scalable packaging of microbial genome collections at the million-genome scale.

---

## Research Questions

1. How can we efficiently store and transmit millions of bacterial genomes?
    
2. From a compressed archive, how can we extract a single genome efficiently?
    

---

## Current State of the Art

The key principle of phylogenetic compression is:

- Reorder genomes according to evolutionary relationships.
    
- Improve local similarity.
    
- Increase compression efficiency.
    

### Two-Level Reordering

1. **Species clustering**
    
    - Cluster genomes into species.
        
    - Within each species, reorder by accession ID.
        
    - Accession ID correlates with similarity in small datasets.
        
2. **Batch partitioning**
    
    - Partition clusters into batches.
        
    - Infer phylogenetic trees within batches.
        
    - Reorder genomes according to the tree.
        

---

## Limitations

- Accession-based batching is not fully consistent with species phylogeny.
    
- Similar genomes may appear in different batches.
    
- Random access is slow.
    

For example:

- With AGC, extracting 1 genome takes approximately 9 seconds.
    
- With xz-based compression, extraction can take significantly longer.
    

This is because entire batches must be decompressed before extracting a genome.

We aim for near-instant retrieval suitable for real-time applications (e.g., search and query).

---

# Proposed Method

Ideally, we would infer a phylogeny for the entire collection. However, this is computationally infeasible.

Example:

- In the AllTheBacteria collection, the species _Salmonella enterica_ contains approximately 650,000 genomes.
    
- Neighbor joining has cubic complexity.
    
- This becomes computationally intractable.
    

### Strategy: Approximate Topology Under Size Constraints

### Input

- A set of genomes (typically from the same species, but possibly mixed).
    

### Step 1: Skeleton Selection

- Randomly subsample genomes.
    
- Adjustable per species (e.g., 5% for large species).
    

### Step 2: Three Elementary Operations

1. Phylogenetic inference on skeleton genomes.
    
2. Nearest-neighbor placement for remaining genomes.
    
3. Partitioning into batches.
    

### Output

A single linear ordering of genomes.

---

## Implementation

Implemented in PhyloPack.

Details:

- Skeleton tree inferred using:
    
    - Mash
        
    - Quicktree: Neighbor joining
        
- Placement:
    
    - Mash-based distance and neighbor placement.
        
- Partitioning:
    
    - Fixed-size batches depending on application.
        

---

## Skeleton Selection Question

How many genomes should be sampled?

Trade-off:

- More skeleton genomes → better compression, but cubic cost increases.
    
- Fewer skeleton genomes → faster runtime, potentially reduced compression.
    

Example:

- 90,000 genomes.
    
- Increasing skeleton size increases computational cost significantly.
    

---

## Species Distribution Issue

Species distribution is highly uneven.

In the 61K collection:

- Top 10 species comprise over 80% of genomes.
    

Solution:

Divide into:

- Major species
    
- Minor species
    
- Unknown species
    

Compress separately.

---

# Results

## Compression (AllTheBacteria Collection)

- Major species: ~2.2 million genomes (93.5%)
    
- Minor + unknown: ~150,000 genomes
    

Using AGC with the new ordering:

- Major species reduced to under 15 GB (~75% reduction).
    
- Including minor + unknown species: ~60% reduction overall.
    

Important observation:

Although minor + unknown species represent ~7% of genomes, they account for over half of the compressed size.

---

## Random Access Trade-Off

Goal: Extract a single genome.

Two approaches:

1. Full decompression (MBGC, xz).
    
2. Random access (AGC).
    

Observation:

- Larger batches → better compression, slower access.
    
- Smaller batches → faster access, worse compression.
    

### Single-Species Batches

Trend is expected:

- Larger batch → better compression, slower access.
    

### Mixed-Species Batches

Behavior differs:

- Increasing batch size does not significantly improve compression.
    
- Access time becomes much slower.
    

Conclusion:

Large batches are not beneficial for mixed-species data.

---

## Whole Collection Strategy

- Large batches for single-species clusters.
    
- Fixed small batches (1,000 genomes) for mixed species.
    

Result:

- Random access ≈ 0.5 seconds per genome.
    
- ~80× faster than AGC without phylogenetic batching.
    

---

# GTDB Compression

Dataset:

- Genome Taxonomy Database (GTDB)
    
- ~715,000 genomes
    
- ~136,000 species
    
- Includes isolates and MAGs.
    

Two-level division:

1. Major/minor species.
    
2. Isolates vs metagenomes.
    

Result:

- Reduced from ~2.6 TB (individual downloads) to ~200 GB compressed archive.
    

---

# Differences from MiniPhy

Two key changes:

1. MiniPhy uses accession ID sorting as first-level approximation.
    
2. New method uses skeleton phylogeny at species scale.
    

Additional calibration across multiple compressors.

---

# Questions & Answers

**Q: At the lowest level, is this just gzip or xz on batches?**  
Yes. The lowest level is a standard compressor applied to batches. Different compressors (xz, AGC, etc.) can be substituted.

**Q: Have you tested BWT-based compressors?**  
Not yet. I am aware of BWT-based approaches but have not benchmarked them.

**Q: Can this be applied to more complex genomes?**  
Currently focused on microbial genomes. Not yet evaluated on complex eukaryotic genomes.

**Q: How is this different from the talk last time from Karel?**  
Main difference: MiniPhy uses accession-based ordering.  
The new method performs skeleton-based phylogenetic ordering across the full species cluster.

**Q: What is the runtime?**  
Compression is done once.

On a cluster or local machine:

- ~25,000 genomes can be processed overnight.
    
- Main bottleneck: phylogenetic inference.
    
- Largest species cluster (e.g., _Salmonella enterica_) dominates runtime.
    

Parallelization across species clusters is possible.

---

# Conclusion

- Improved phylogenetic ordering and batching at million-genome scale.
    
- ~60% compression reduction on AllTheBacteria.
    
- ~0.5 second random access (vs ~10 seconds previously).
    
- GTDB compressed to ~200 GB.
    
- Work in progress.
    

Future directions:

- Apply to additional databases.
    
- More refined batch constraints (compressed size limits, memory bounds).
    
- Further evaluation on MAG-heavy collections.