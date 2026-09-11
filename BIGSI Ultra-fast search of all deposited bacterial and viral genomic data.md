Back ground and Context: (2019)
Limitation of existing methods (BLAST)
According to the BIGSI paper, BLAST has two key limitations when applied to large genomic archives:

1. **Scalability**: BLAST cannot efficiently handle the exponentially growing size of global sequence databases, such as the ENA.
2. **Assembly Dependency**: BLAST requires assembled genomes as input and does not perform well with raw sequence reads. This limits its effectiveness for datasets containing mixed or unassembled strains, leading to incomplete results.

These limitations motivated the development of a more scalable and versatile solution like BIGSI.

Datasets:

The datasets used in the BIGSI paper include:

1. **Bacterial and Viral Whole Genome Sequence Data**: A set of 447,833 datasets from the European Nucleotide Archive (ENA), bacteria, viruses, and some eukaryotic parasites.
2. **Plasmids**: A set of 2,827 plasmid sequences used for host-range analysis.
3. **Antimicrobial Resistance Genes**: Over 2,000 sequences from the Comprehensive Antibiotic Resistance Database (CARD).
4. **Mycobacterium tuberculosis Datasets**: 3,480 datasets used for genotyping and validation.

The BIGSI paper compares its method to

Sequence Bloom Tree (SBT) and Split SBT (SSBT): These tools fail to scale effectively with the high diversity and massive volume of microbial datasets, requiring significantly more storage.

- **Storage Efficiency**: Indexed 447,833 datasets in just 1.5 TB, less than 1% of the original 170 TB data size.
- **Query Speed**: Detected antimicrobial resistance genes across the dataset in under 2 seconds.
- **Scalability**: BIGSI supports incremental updates and handles datasets of millions of genomes, scaling linearly in storage needs.
- **Accuracy**: Genotyping concordance exceeded 99.9% compared to other tools.

The **performance metrics** of BIGSI are explained in detail below, highlighting its advantages over previous methods:

### **1. Storage Efficiency**

- BIGSI indexed 447,833 bacterial and viral whole genome datasets into 1.5 TB, which is less than 1% of the original dataset size (170 TB).
- This was achieved using [[Bloom filter | bloom filter-based]] compression to store DNA k-mers (short DNA sequences) efficiently.

### **2. Query Speed**

- Searches were extremely fast; for example, querying for antimicrobial resistance genes across all datasets took under 2 seconds.
- SNP genotyping of 68,269 variants across Mycobacterium tuberculosis datasets took 90 minutes on a single CPU core, yielding a genotyping rate of 46,000 genotypes per second.

### **3. Scalability**

- BIGSI scales linearly with the number of datasets, maintaining high performance even with millions of genomes.
- It supports incremental updates, allowing new datasets to be added without rebuilding the entire index.

### **4. Accuracy**

- SNP genotyping accuracy had a concordance of 99.997% with traditional methods.
- Detection of longer alleles (like Multi Locus Sequence Type alleles) showed over 99.9% agreement compared to high-quality calls from specialized tools.

### **5. Comparisons to Other Methods**

- **Sequence Bloom Tree (SBT)**: Required significantly more storage, up to 132x more during construction, and slower query performance for large databases.
- **Mantis**: Had issues with false positives, segmentation faults, and lacked incremental updating capabilities.

### **6. Practical Demonstrations**

- Identified mobilized colistin resistance (MCR) genes across the dataset faster than previous reports, providing near-instant detection.
- Analyzed plasmid host range and tracked the spread of conjugative elements with high sensitivity and specificity.

These metrics demonstrate BIGSI as a superior tool for indexing and searching vast genomic archives with speed, scalability, and accuracy.\

Tools mentioned 

- **BLAST**: Standard for sequence alignment but lacks scalability and is dependent on assembled genomes.
- **Sequence Bloom Tree (SBT)**: Uses a k-mer index but has significant storage and scalability issues for highly diverse microbial datasets.
- **Split SBT (SSBT)**: An improvement over SBT but still faces limitations in scalability and performance.
- **Mantis**: A compact k-mer indexing tool but has technical issues, including high memory requirements and lack of incremental updating.
