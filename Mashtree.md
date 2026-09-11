#mash
### In a nutshell

The **Mashtree** tool for rapidly comparing whole genome sequences and constructing phylogenetic trees. 
use **Mash** algorithm to create compact genome sketches using k-mers, next calculates pairwise distances between genomes. 
These calculated distances are used with the **neighbor-joining algorithm** (via QuickTree) to generate dendrograms. 


### **bootstrapping** and **jackknifing** to assess the confidence level:

### **1. Bootstrapping**

- Generates multiple replicate datasets by resampling with replacement from the original k-mers.
- Constructs trees for each replicate and compares them to the main tree.
- Calculates confidence values based on the percentage of replicates supporting each node.

### **2. Jackknifing**

- Removes a random subset of k-mers from the dataset (without replacement).
- Builds trees from reduced datasets and compares them to the main tree.
- Confidence is based on how often nodes persist across replicates.