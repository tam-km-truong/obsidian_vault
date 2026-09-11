---
raw_tags:
  - genomes
  - species
  - compression
  - phylogenetic
  - extraction
  - skeleton
  - phrase
  - percent
word_count: 1708
char_count: 11891
processed: false
---

This work focuses on how we can store and access millions of bacterial genomes efficiently using a method we call phylogenetic batching. The aim is to show why this problem matters, what the current limitations are, and how our approach improves both compression and extraction at very large scale.

**Introduction: Bacterial Data Are Growing Exponentially**

Modern sequencing technologies are generating bacterial genomes at an extraordinary rate. Public resources such as NCBI now contain millions of genomes, and large curated collections play an essential role in organizing and processing them. Collections like the 661k set or the AllTheBacteria collection, which now has almost 2.5 million genomes, show how rapidly the field is expanding. The problem is that bacterial genomes are complex. They are highly diverse, and horizontal gene transfer increases that diversity. All of this makes storing and processing such collections increasingly difficult.

Review of Databases
**Transition:** Let’s start by looking at what microbial genome databases are and how genomes get into them.

**Phrase 1:** These databases collect bacterial and archaeal genomes.  
_(Detail)_ They take either isolate WGS or metagenome-assembled genomes, then run them through a workflow: assembly, quality control for completeness and contamination, taxonomic assignment, and functional annotation.

**Phrase 2:** Each database has its own rules and features.  
_(Detail)_ They differ in genome type, assembly source, quality thresholds, species definitions like ANI clusters or phylogenetic normalization, accessibility, and licensing or institutional policies.

**Transition:** Now let’s break down how the major microbial genome databases compare across key features.

**Phrase 1:** **Size** varies widely.  
_(Detail)_ Some databases have millions of genomes, like ATB and ProGenomes4, while others are smaller, like GTDB or RefSeq.

**Phrase 2:** **Genome types** differ.  
_(Detail)_ Some focus only on isolates, while others include both isolates and MAGs. This affects the diversity and completeness of what’s represented.

**Phrase 3:** **Source and assembly** vary.  
_(Detail)_ Some use raw reads from ENA and reassemble them (like ATB), others take submitter assemblies from GenBank or RefSeq. Assembly methods influence quality and consistency.

**Phrase 4:** **Special features** differ.  
_(Detail)_ Some databases provide metadata, precomputed pangenomes, phylogenetically standardized taxonomy, or indexing tools for fast queries. These add functionality beyond just genome storage.

**Phrase 5:** **Data access** — this is important for practical use.  
_(Detail, slow down here)_ Some databases are easy to download in bulk, like ATB and ProGenomes4, allowing you to grab either the full collection or representative genomes quickly. Others, like GTDB, the 661k collection, or RefSeq, require per-genome downloads, so retrieving large datasets takes more time and effort. Access method can strongly affect how quickly you can work with the data.

**Review of Compression Techniques**
Given these conditions, the next question is how to compress such data in a scalable way. Compression has been widely studied. General-purpose compressors such as XZ and Zstandard work well for many situation. For bacterial genomes, specialized compressors like MBGC, AGC, and Geco3 offer better performance, each with their own advantages, whether it is handling reverse complements, enabling fast extraction, or using neural network models. There are also high-level strategies such as phylogenetic compression which evolutionary groups and reorders genome. However, scaling any of these approaches to millions of genomes remains extremely challenging.

**Key Questions**

This situation leads to two central questions. First, how can we efficiently store and transmit millions of genomes. Second, how can we extract individual genomes quickly from compressed archives. These are the two problems our work aims to address.

**State of the Art: Phylogenetic Compression**

One current solution is phylogenetic compression. This approach uses evolutionary history to guide compression. By reordering genomes according to their phylogeny, local similarity increases, which greatly improves compressibility. This strategy can yield an improvement of one to two orders of magnitude over earlier protocols. It is highly general, with different protocols depending on the type of dataset. A  protocol for assemblies is MiniPhy, which clusters genomes by species, reorders them phylogenetically, and then applies XZ compression.

**How Phylogenetic Compression Works**

Phylogenetic compression typically has two levels of reordering. First is phylogenetic batching, which groups related genomes, generally using species metadata. Second is tree traversal, which arranges genomes in an order that follows the phylogenetic tree from left to right. This is the current protocol used by AllTheBacteria.

**Phylogenetic Batching: A Double-Edged Sword**

In smaller datasets, sequencing time often correlates with relatedness because groups of similar genomes are uploaded together. For large datasets, this correlation doesn't work. Highly similar genomes  arrive at different times and become scattered across many batches. As a result, the impact of phylogenetic compression is reduced, since batches no longer contain closely related genomes.

**Limitations of Current Methods**

Two problems emerge. First, batching may not be consistent with the underlying phylogeny, so compression becomes less efficient. Second, extracting a single genome from a large compressed batch is slow, since many compressors such as XZ and MBGG decompress the whole batch. This makes current systems unsuitable for applications requiring real-time or near–real-time access.

**Methods motivation: Reducing Complexity**

In principle, the ideal solution would be to compute the exact phylogenetic tree for every genome in a species. In practice, this is impossible for very large species. Salmonella alone has around 645,000 genomes, and building a full phylogenetic tree for all of them would require impractical amounts of time. This means we need a way to reduce computational complexity while still retaining enough phylogenetic order to help compression.

**Skeleton Tree Approximation**

To address this, we propose a skeleton tree approximation. The idea is to sample a small set of skeleton genomes, compute a phylogenetic tree for these, and then place the remaining genomes onto that structure. The goal is to produce an approximate phylogenetic ordering that still groups related genomes together before batching. This approach dramatically reduces computational time while preserving ordering quality well enough for compression.

**Implementation Steps**

The method proceeds in three steps. First, we randomly sample a subset of genomes to form the skeleton set. Second, we build a phylogenetic tree on this skeleton using sketching and neighbor joining. Third, we place the remaining genomes onto the leaves of this tree, and then reorder them into batches of fixed size. This gives explicit control over runtime and makes it possible to distribute different species across different machines. For instance, ordering thirty thousand Salmonella genomes can be done overnight, whereas computing a full tree for all 645,000 would require more than a decade.

**Calibrating Skeleton Genomes**

A central challenge is deciding how many skeleton genomes to use. For a species such as E. coli, which has about ninety thousand genomes, using more skeleton genomes improves order, but the cubic cost of neighbor joining quickly becomes too expensive. We therefore need a balance: a skeleton set small enough to be fast but large enough to maintain compression quality.

**Uneven Species Distribution**

Another challenge comes from uneven species distribution. The ten most common species make up about eighty percent of the collection but only four percent of the compressed size. Rare species, although only five percent of the data, take up roughly thirty percent of compressed size. In addition for ATB, many genomes belong to unknown species groups.

**Solution: Separate Compression**

To deal with this, we divide genomes into three divisions: major species, minor species, and unknown species. Each division is processed independently. This improves compression efficiency and makes the uneven distribution manageable.

**Experiment Overview: Skeleton Tree Recompression**

We evaluated the approach on the AllTheBacteria collection. The collection was first divided into major, minor, and unknown species. Major species contained about 2.3 million genomes, and minor plus unknown species contained around 150,000. We then reordered all genomes using the skeleton tree method and compressed them with three different compressors to quantify the improvement.

**Compression Results: Major Species**

For the 2.3 million genomes in major species, we achieved a seventy-five percent reduction in size, storing the entire set in under fifteen gigabytes. These genomes are highly compressible, and the result highlights that the most common species deliver the largest compression gains.

**Global Compression Results**

Across all species combined, we observed about a 60 percent global reduction. Notably, the minor and unknown species, which comprise only a small fraction of the total number of genomes, still account for nearly half of the compressed size. This shows that rare species remain the principle compression killer.

**Random Access: Fast Extraction**

Compression alone is not enough. We also need fast access.
We measured extraction times for several compressors. Some tools, like MBGC and XZ, require decompressing the full batch. Others, like AGC, allow fast random access. Our expectation was that smaller batches should yield faster extraction.

**Single Species Extraction**

In tests on a single-species dataset, larger batches improved compression but slowed extraction. This created a clear trade-off between compression ratio and access time. For a single species, therefore, batch size should be chosen depending on whether compression or speed is more important.

**Diverse Species Extraction**

For mixed-species datasets, larger batches did not improve compression at all, but they did slow extraction substantially. For such datasets, smaller batches are clearly the superior option.

**Whole Collection Extraction**

For the full 661k collection, we used different batch sizes for major species and fixed batch sizes for minor species. Compared to AGC, our approach achieved an eighteen-fold speedup while keeping a similar compressed size. This shows that phylogenetic batching helps both compression and extraction at the scale of entire collections.

application to GTDB
GTDB is different from ATB because of 2 main features genomes type, species diversity
Currently not in compressed form
Results 1:
Division by Major and Minor species

Result 2:
Division by Isolates and MAGs

**Conclusions**

We present a skeleton-tree phylogenetic approximation that scales to millions of genomes. The method achieves around sixty percent global compression gain and reduces extraction time to under half a second per genome, compared to almost ten seconds previously. There are limitations, as results so far are based on the 661k and AllTheBacteria collections, and performance would improve further on SSDs. Future directions include applying the method to even larger databases such as GenBank, GTDB, and Logan-Bact, and developing more advanced batching rules based on maximum compressed size or memory constraints.