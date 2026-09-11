comprehensive dataset of bacterial genomes
addressing issues with inconsistent and inaccessible public genomic data. 
Building on the 2018 "661k" dataset, expands the collection to 1.9 million uniformly processed assemblies, with quality control and taxonomic consistency.

Uniformly processed:
- **Assembly**: Assembled using the same pipeline, avoid variability caused by different tools.
- **Quality Control (QC)**: applied checks like genome size limits, contamination filtering, and completeness metrics
- **Taxonomic Consistency**: annotated with a unified taxonomy, using GTDB standards.

### **Key Contributions**

1. **Scale**: Tripled the genome dataset to include 1,932,812 assemblies.
2. **Efficiency**: Used evolution-informed compression (MiniPhy) to reduce dataset size to 102 GB.
3. **Standardization**: Applied quality criteria like GTDB taxonomy and rigorous QC protocols

### TOOLS:
### **Genome Processing**

1. **Shovill**: Wrapper for SPAdes, used for bacterial genome assembly.
2. **SPAdes**: Genome assembly tool for assembling bacterial sequences.

### **Taxonomic Analysis**

3. **Sylph**: Tool for taxonomic abundance estimation, faster and more memory-efficient than Kraken/Bracken.
4. **TaxonKit**: Used to manage taxonomy data from GTDB.

### **Quality Control**

5. **CheckM2**: Assesses microbial genome completeness and contamination.

### **Compression**

6. **MiniPhy**: Compresses assemblies based on phylogenetic relationships.

### **Search Indexing**

7. **pp-sketchlib**: Creates k-mer-based sketches for sequence similarity searches.


### **high-quality genomes** that meet strict criteria for accuracy and usability. These are:

1. **Size Constraints**: Genome length btwn 100 kb and 15 Mb.
2. **Completeness and Contamination**: At least 90% completeness and less than 5% contamination (assessed with CheckM2).
3. **Species Abundance**: The majority species must represent at least 99% of the reads in the sample.
4. **Structural Metrics**: Assemblies must have no more than 2,000 contigs and an N50 value of at least 5,000.

### DATASET CHARACTERISTICS

- **Number of Species**: The dataset contains genomes from 10,542 species, a significant increase from the 6,997 species in the previous "661k" dataset.
- **Dominant Species**: Highly represented species of clinical interest dominate, with the top 10 species making up 77% of the high-quality genomes.
- **Wide Representation**: This diversity captures rare and common species, enabling comprehensive studies across bacterial lineages and enhancing its utility for evolutionary, clinical, and ecological research.

Top 10 species:

- _Salmonella enterica_
- _Escherichia coli_
- _Mycobacterium tuberculosis_
- _Staphylococcus aureus_
- _Streptococcus pneumoniae_
- _Campylobacter jejuni_
- _Klebsiella pneumoniae_
- _Neisseria gonorrhoeae_
- _Neisseria meningitidis_
- _Streptococcus pyogenes_

S