---
raw_tags:
  - genomes
  - species
  - compression
  - phylogenetic
  - isolates
  - tree
  - atb
  - collections
word_count: 1397
char_count: 9881
processed: true
processed_note: \"[[DSB 2025 - Phylogenetic Batching Presentation]]\"
---

Today I will present my work on phylogenetic ordering and batching of million-genome collections for reduced storage and faster retrieval.

Modern sequencing technologies are generating bacterial genomes at an exponential scale. Public databases such as NCBI now contain millions of genomes. Bacterial genomes are highly diverse and complex. 
Over the next decade, collections may reach 10 million genomes, with higher diversity and a larger proportion of metagenome-assembled genomes (MAGs).

At the same time, large curated collections play an essential role in biological research. For example, AllTheBacteria (ATB) contains nearly 2.5 million genomes, while other collections contain hundreds of thousands. 

Major collections include AllTheBacteria, Genome Taxonomy Database (GTDB), proGenomes, and others. A comparative overview shows that some databases contain millions of genomes, such as proGenomes and ATB, whereas others are smaller, such as GTDB in earlier releases or more specialized collections. Data sources vary: some databases include only isolates, whereas others integrate both isolates and metagenome-assembled genomes. A practical consideration is data access. Across databases, only ATB currently supports bulk download of the complete collection in a unified manner.

Each database then defines its own features, such as genome type (isolate or MAG), assembly methodology, data source, and quality metrics. The overall goal is to transform heterogeneous and inconsistent data into high-quality standardized assemblies.

Given the size of these collections, the next question is how to compress them efficiently. This is a well studied problem. There are general-purpose compressors such as gzip or xz, and specialized genome compressors such as AGC or MBGC. There are also higher-level strategies such as phylogenetic compression, which group genomes by evolutionary relationship to improve compressibility.

The main challenge is scalability. In this project, we focused on two questions:

1. How can we efficiently store and transmit millions of bacterial genomes?
    
2. How can we rapidly extract a single genome from a compressed archive?
    

One current solution is phylogenetic compression. This approach uses evolutionary history to guide compression by reordering genomes according to their phylogeny. By increasing local similarity, compressibility improves significantly. Compression ratios can improve by one to two orders of magnitude compared to standard metadata-based ordering combined with general-purpose compression.

Protocols vary depending on the input data type, such as assemblies or k-mer sketches. For example, in ATB, the current protocol groups genomes by species, reorders them phylogenetically, and compresses them with a general-purpose compressor. There are two levels of reordering. First, genomes are batched phylogenetically, usually according to species metadata. Second, within each batch, genomes are reordered according to the phylogenetic tree from left to right. This is the protocol currently used in ATB.

Looking more closely at the first level, batching is currently based on accession order. Accession numbers often correlate with sequencing time, and genomes generated within the same project are frequently phylogenetically related. This heuristic works reasonably well for smaller datasets, where accession order correlates with relatedness. However, at the million-genome scale, this correlation breaks down. Similar genomes become scattered across multiple batches, reducing compression efficiency.

This leads to two limitations. First, reordering based on accession numbers does not necessarily reflect species phylogeny. Second, extracting a single genome from a large compressed archive can be slow, because many compressors require decompressing the entire batch. This is unsuitable for near real-time applications such as search or querying.

We therefore developed a new method. Computing a full phylogenetic tree for millions of genomes is computationally impractical. For example, building a neighbor-joining tree for more than 600,000 genomes, such as a large Salmonella enterica dataset, would take years due to cubic time complexity.

Our solution is to approximate the tree under size constraints. The approach is as follows:

1. Randomly subsample a small set of genomes to form a skeleton set.
    
2. Build a phylogenetic tree from this skeleton using sketching and neighbor joining.
    
3. Place the remaining genomes onto this tree using a nearest-neighbor approach.
    
4. Reorder genomes into fixed-size batches for compression.
    

This retains phylogenetic ordering while keeping computational cost manageable. Related genomes are grouped together into batches instead of being scattered.

The implementation consists of three steps. First, we subsample a percentage of genomes within each species cluster; this percentage is adjustable per cluster. Second, we build a phylogenetic tree from the skeleton set using Mash-based distance estimation and neighbor joining. Third, we place the remaining genomes and reorder all genomes into fixed-size batches for compression.

This approach allows control over runtime through the sampling percentage. For example, for more than 600,000 Salmonella enterica genomes, using approximately 30,000 skeleton genomes required around 15 hours to compute the tree, whereas a full neighbor-joining tree would be infeasible, potentially requiring many years.

Two central challenges arise. First, how should we choose the number of skeleton genomes for large species clusters? Runtime scales cubically with the number of skeleton genomes under neighbor joining. Large species clusters such as Escherichia coli or others impose strong computational constraints. The objective is to use as few skeleton genomes as possible while maintaining high compression performance. Second, species distribution is highly uneven. In ATB, the 10 most common species account for roughly 80% of genomes but only around 4% of compressed size.

To address this imbalance, we divided the collection into major species, minor species, and a no-species category.

We first evaluated the method on ATB. We split the dataset into major, minor, and no-species divisions and compressed them using three low-level compressors: AGC, MBGC, and xz. For major species, which constitute approximately 93.5% of the dataset, we achieved a 75% reduction in compressed size. Across the entire dataset, the new strategy achieved around a 60% reduction relative to the existing state-of-the-art pipeline. Minor species represent less than 7% of genomes but contribute more than half of the compressed size, indicating that rare species are the main compression bottleneck.

We then evaluated genome extraction time. The key hypothesis is that smaller batch sizes enable faster extraction. However, there is a trade-off between compression ratio and access speed.

For a single-species dataset, specifically Salmonella enterica from ATB, larger batch sizes improved compression but increased access time. A clear trade-off exists between compression efficiency and retrieval speed.

For mixed-species datasets, increasing batch size did not improve compression gain but significantly slowed extraction. Therefore, in mixed datasets, larger batches provide no advantage. The practical conclusion is to use smaller batch sizes to ensure faster genome access.

Combining these insights across the whole collection, we used variable batch sizes for major single-species clusters and fixed smaller batch sizes for mixed or minor clusters. Compared to AGC, our approach reduced genome extraction time from approximately 92 seconds to under 0.5 seconds.

We then evaluated applicability to other microbial genome collections. The method is applicable to any isolate microbial genome collection, so we applied it to GTDB. GTDB contains more than 700,000 genomes, spanning approximately 136,000 species, with substantially higher diversity. It includes both isolates and metagenome-assembled genomes. The collection is not currently distributed in compressed form.

In the first experiment, we applied the major–minor species division directly to GTDB, mixing isolates and MAGs. Major species remained highly compressible, whereas minor species were less compressible. The total compressed size was reduced to approximately 200 GB. However, this approach mixes isolates and MAGs, while phylogenetic compression has primarily been evaluated on isolates.

In the second experiment, we separated isolates and MAGs before compression. We used the GTDB-provided phylogenetic tree for reordering. The result was approximately 66–67 GB for isolates and 126 GB for MAGs, for a total of around 190 GB, which is smaller than the previous mixed strategy. Assemblies derived from metagenomes were substantially more difficult to compress.

In conclusion, we presented a skeleton-based phylogenetic approximation method scalable to millions of genomes. We achieved substantial compression gains and reduced genome extraction time to under 0.5 seconds. The method performs effectively on ATB and is also applicable to GTDB. We now provide the GTDB complete collection in compressed form.

Limitations include the absence of performance benchmarking on SSD storage and limited benchmarking for metagenome-assembled genomes, which is ongoing. Future directions include application to even larger databases such as proGenomes and others, as well as development of more advanced batching strategies based on memory constraints or maximum compressed-size constraints.