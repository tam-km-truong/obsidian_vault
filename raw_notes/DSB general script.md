---
raw_tags:
  - genomes
  - species
  - compression
  - points
  - random
  - access
  - phylogenetic
  - key
word_count: 1435
char_count: 10516
processed: false
---

## 1. Introduction
SLOWW down and breathe
Good morning everyone. My name is Tom, 
Im 2nd years phd student
from GenScale Rennes
and today I will present my current state of my PhD work on phylogenetic ordering and batching of million-genome collections. The objective is to reduce storage requirements while enabling fast extraction of individual genomes from large compressed archives.

**Key points**

- Topic: phylogenetic ordering and batching at million-genome scale
    
- Goal: reduce storage + enable fast random access
    
- Context: large compressed genome archives
    
- Collaboration: Dominic, Pierre, Karen
    

---

## 2. Motivation: Exponential Growth of Genome Data

Modern sequencing technologies are generating bacterial genomes at an exponential rate. Databases such as NCBI have grown from a few hundred thousand genomes ten years ago to nearly three million today, and growth is accelerating. Increasing diversity, together with the growing number of metagenome-assembled genomes (MAGs), further increases complexity.

Curated genome collections play a central role in biological research. Major resources include:

- AllTheBacteria (ATB)
    
- GTDB
    
- GenBank
    

These collections differ in scale and composition. Some contain primarily isolate assemblies, while others increasingly include MAGs. Several already contain millions of genomes; collectively, available bacterial genomes approach ten million.

A key challenge is distribution. Only ATB provides a complete packaged download. Most databases require downloading assemblies individually. At this scale, efficient compression and practical distribution become essential.

**Key points**

- Exponential growth in bacterial genomes
    
- ~3 million genomes currently in NCBI
    
- Increasing diversity and MAG inclusion
    
- Multiple large curated collections (ATB, GTDB, GenBank)
    
- Distribution bottleneck: no unified packaged downloads
    
- Compression and transmission are critical
    

---

## 3. Existing Compression Strategies

Compression is a well-studied problem. General-purpose compressors such as gzip or xz are widely used but not optimized for genomic redundancy.

Specialized tools include:

- MBGC — handles reverse complements and achieves strong compression
    
- AGC — supports fast random genome extraction
    

Higher-level strategies include phylogenetic compression, which reorders genomes according to evolutionary relationships to increase local similarity. This protocol is used in ATB.

The central challenge is scaling these strategies to any large and heterogeneous genome collection.

**Key points**

- General-purpose compressors: not genome-aware
    
- MBGC: strong compression
    
- AGC: fast random access
    
- Phylogenetic compression: reorder by evolutionary proximity
    
- Scalability remains unresolved
    

---

## 4. Research Questions

This work addresses two main questions:

1. How can we efficiently store and transmit millions of bacterial genomes?
    
2. How can we rapidly extract a single genome from a compressed archive (random access)?
    

**Key points**

- Storage efficiency
    
- Transmission efficiency
    
- Random access performance
    

---
Now that we understand the context and the open questions, let’s look at what the current state of the art can do—and where it still struggles.”
## 5. MiniPhy: Current Phylogenetic Compression Strategy

The current implementation of phylogenetic compression is MiniPhy. It performs ordering in two levels:

> “One of the current solutions that partly addresses these problems is phylogenetic compression.  
> It uses the evolutionary history of genomes to guide compression.  
> By reordering genomes along their phylogenetic tree, we increase local compressibility and achieve better compression.  
> This can give a 10- to 100-fold improvement over previous methods.  
> Phy comp is highly general. Different protocols exist for different types of data.  
> One example is Miniphy, i will go into it more after.”  

It works on 2 levels
**Level 1: Phylogenetic batching**

- Cluster genomes by species
    
- Reorder species clusters by accession ID
    This strategy works reasonably well at small scale because accession IDs often correlate with sequencing projects and relatedness
    
- Partition clusters into fixed-size batches
    

**Level 2: Local reordering**

- Infer a phylogenetic tree within each batch
    
- Reorder genomes according to that tree
    

This strategy works reasonably well at small scale because accession IDs often correlate with sequencing projects and relatedness. However, at million-genome scale:

- Accession ID correlates imperfectly with phylogeny
    
- Closely related genomes may fall into different batches
    
- Random access remains slow for large batches
    
- Compressors like MBGC require decompressing entire batches
    

For near real-time applications (e.g., search or curation), near-instant access is required.

**Key points**

- Two-level ordering (species → local tree)
    
- Accession ID used as phylogenetic proxy
    
- Works at small scale
    
- Fails at million-genome scale
    
- Random access bottleneck
    

---

## 6. Method: Approximate Phylogeny via Skeleton Tree

Constructing a full phylogeny for millions of genomes is computationally infeasible. For example, a single species such as _Salmonella enterica_ in NCBI contains hundreds of thousands of genomes. Neighbor joining has cubic complexity and becomes computationally intractable.

### Core idea


Approximate the global phylogeny under size constraints:

3 elementary operations
select the skeleton set
first reordering
nereast neighbor placement


implementation
1. Input: a set of genomes (single or mixed species).
    
2. Randomly subsample a percentage to form a skeleton set (e.g., 5%).
    
3. Infer a phylogeny on the skeleton genomes (using Mash and QuickTree).
    
4. Place remaining genomes onto the skeleton via nearest-neighbor placement.
    
5. Perform local reordering at leaf level.
    
6. Cut the final order into batches of application-specific size.
    

Output: a single optimized global genome order.

**Key points**

- Full tree infeasible at scale
    
- Random skeleton subsampling
    
- Skeleton phylogeny inference
    
- Nearest-neighbor placement
    
- Local refinement
    
- Final batching
    

---

## 7. Parameter Trade-offs

### Skeleton selection

Multiple strategies are possible:

- Random sampling
    
- Chemical or k-mer-based selection
    
- Biological centric (e.g., GTDB taxonomy-based)
    
it is also differnet for different species

Empirically, random sampling performs well.

Key objective:

- Minimize skeleton size (reduce runtime and hardware requirement)
    
- Preserve compression quality
    
on the example we have
Neighbor joining’s cubic complexity makes skeleton size critical.

### Species imbalance

Genome collections are highly skewed. In some datasets, ten species account for ~80% of genomes. Additionally, some genomes have unknown species.

Solution:

- Divide collection into three groups:
    
    - Major species
        
    - Minor species
        
    - Unknown species
        
- Compress each separately
    

**Key points**

- Skeleton size controls runtime and memory
    
- Cubic complexity constraint
    
- Random sampling effective
    
- Strong species imbalance
    
- Three-division strategy
    

---

## 8. Results: Repacking AllTheBacteria (ATB)

so here s the result
the plot: compressed size and different compressor
Dataset:

- Major species: 2.3 million genomes (~93.5%)
    
- Minor + unknown: ~150,000 genomes
    

Compressors evaluated:

- AGC
    
- MBGC
    
- xz
    

Results:

- Major species compressed to <15 GB (~75% reduction)
    
- Entire ATB compressed to ~42 GB (~60% total reduction)
    

**Key points**

- Three-way division
    
- Strong compression improvement
    
- 75% reduction (major species)
    
- 60% overall reduction
    

---

## 9. Random Access Analysis

Task: extract a single genome from a compressed archive.

Two scenarios:

1. Full-batch decompression required
    
2. Native random access (e.g., AGC)
    

### Single-species batches

- Larger batch → better compression
    
- Larger batch → slower access time
    
- Clear compression–latency trade-off
    

### Mixed-species batches

- Compression largely independent of batch size
    
- Larger batch → slower access
    
- No benefit to large batches
    

### Combined strategy

- Large batches for major species (optimize compression)
    
- Smaller fixed batches for minor species (optimize access)
    

Final performance:

- ~0.5 seconds per genome
    
- ~18× faster than previous configuration (~10 seconds)
    

**Key points**

- Trade-off depends on species composition
    
- Single-species: compression vs latency trade-off
    
- Mixed-species: no compression gain from large batches
    
- Final access time ≈ 0.5 s
    
- 18× improvement
    

---

## 10. Application to GTDB

GTDB contains:

- ~750,000 genomes
    
- > 100,000 species
    
- Both isolates and MAGs
    

Two division strategies:

- Major vs minor species
    
- Isolate vs MAG
    

Results:

- Original full download ≈ 2.6 TB (individual assemblies)
    
- Repackaged compressed archive ≈ 200 GB
    

**Key points**

- High diversity dataset
    
- Mixed isolate + MAG
    
- 2.6 TB → 200 GB
    
- Demonstrates generalizability
    

---

## 11. Conclusion

Phylopack provides improved phylogenetic ordering and batching compared to MiniPhy at million-genome scale.

Main outcomes:

- ATB repackaged with ~60% compression gain
    
- Random access reduced to ~0.5 s per genome
    
- GTDB compressed to ~200 GB
    

**Key points**

- Scalable phylogenetic approximation
    
- Improved compression
    
- Significant random access acceleration
    
- Successful application to multiple datasets
    

---

## 12. Limitations and Future Work

Limitations:

- Phylogenetic inference for MAGs remains less accurate
    
- Final compressed archives are not yet fully released
    

Future directions:

- Apply protocol to additional databases such as GenBank
    
- Introduce additional batching constraints:
    
    - Maximum compressed size per batch
        
    - Maximum memory per batch
        

**Key points**

- MAG phylogeny limitations
    
- Archive availability pending
    
- Extend to other large repositories
    
- Add memory and size constraints to batching strategy