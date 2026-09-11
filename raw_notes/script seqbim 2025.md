---
raw_tags:
  - slide
  - pause
  - species
  - genomes
  - compression
  - phylogenetic
  - skeleton
  - extraction
word_count: 1749
char_count: 11066
processed: false
---

# **Revised Script with Transitions**

---

## **Slide 1 – Title Slide**

**Title:** Optimized Phylogenetic Batching for Compression of Million Genome Collections

> “Hi everyone, my name is Tom. I just started my second year of my phd I am working with [Name], [Name], and [Name], who are my supervisors.  
> Today I will talk about how we can store and access millions of bacterial genomes efficiently using a method we call phylogenetic batching.”  
> _(Pause for 2–3 seconds)_

---

## **Slide 3 – Introduction: Bacterial Data are Growing Exponentially**

> “Let’s start with the context.  
> With modern sequencing technologies, bacterial genome data are growing very fast. Public databases like NCBI now hold millions of genomes.  
> The state-of-the-art collections help organize and process these genomes. They are vital for bioinformatics research.  
> For example, the 661k collection contains 661,000 genomes, and version 3 of the AllTheBacteria collection contains almost 2.5 million genomes.  
> However, bacterial genomes are complex. They are very diverse, and their diversity is increased by horizontal gene transfer.  
> This makes storing and processing them challenging.”  
> _(Pause for audience to absorb)_

---
transition for data to compression
## **Slide 4 – Review of Compression Techniques**

> “Compression is a widely studied problem.  
> We have general compressors like XZ or Zstandard.  
> And we have specialized compressors for bacterial genomes, such as MBGC, which handles reverse complements and gives good compression ratios, AGC, which allows fast extraction, and Geco3, which uses a neural network model.  
> We also have high-level approaches like phylogenetic compression.  
> But scaling these methods to millions of genomes remains very difficult.”  
> _(Pause, nod to audience)_

---

## **Slide 5 – Key Questions**

> “This brings us to two key questions:  
> First, how can we efficiently store and transmit millions of bacterial genomes?  
> Second, how can we extract individual genomes quickly from compressed archives?  
> These are the two problems our work aims to solve.”  
> _(Pause, make eye contact)_

---

### **Transition (Slide 5 → Slide 6)**

> “Now that we understand the context and the open questions, let’s look at what the current state of the art can do—and where it still struggles.”

---

## **Slide 6 – State of the Art: Phylogenetic Compression**

> “One of the current solutions that partly addresses these problems is phylogenetic compression.  
> It uses the evolutionary history of genomes to guide compression.  
> By reordering genomes along their phylogenetic tree, we increase local compressibility and achieve better compression.  
> This can give a 10- to 100-fold improvement over previous methods.  
> Phy comp is highly general. Different protocols exist for different types of data.  
> One example is Miniphy, which uses species clustering, phylogenetic reordering, and XZ compression.”  
> _(Pause, gesture to figure if available)_

---

## **Slide 7 – How Phylogenetic Compression Works**

> “Phylogenetic compression has two levels of reordering:  
> First, phylogenetic batching, which groups genomes by relatedness.  
> Second, tree-traversal ordering, which arranges genomes from left to right along the phylogenetic tree.  
> This is how the current state-of-the-art method works on large bacterial collections.”  
> _(Short pause for emphasis)_

---

### **Transition (Slide 7 → Slide 8)**

> “Now that we see the high-level idea, let’s look at one specific part of the method—batching—and why it becomes a challenge at large scale.”

---

## **Slide 8 – Phylogenetic Batching: A Double-Edged Sword**

> “Sequencing data are often uploaded together. For small collections, sorting by sequencing time can group related genomes.  
> But for large collections, this approach does not scale. Related genomes are split across many batches.  
> This reduces the power of phylogenetic compression and limits the compression gain.”  
> _(Pause for audience to connect the idea)_

---

### **Transition (Slide 8 → Slide 9)**

> “These issues lead directly to two major limitations in current methods.”

---

## **Slide 9 – Limitations of Current Methods**

> “Two key limitations stand out:  
> First, batching may not be consistent with the species phylogeny, so compression becomes less efficient.  
> Second, extracting a single genome from a large compressed batch is slow.  
> This makes current approaches unsuitable for real-time applications.”  
> _(Pause, look around)_

---

### **Transition (Slide 9 → Slide 11)**

> “To address these limitations, we need new methods.  
> Let’s now move into our approach.”

---

## **Slide 11 – Methods: Reducing Complexity**

> “Ideally, we would compute the exact phylogenetic tree for every genome in a species.  
> But this is impossible for very large species.  
> For example, Salmonella has around 645,000 genomes.  
> Computing a full phylogenetic tree for this size would take far too long.  
> So we need to reduce the computational complexity.”  
> _(Pause for effect)_


---
“To do this, we use an approximation.”
## **Slide 12 – Skeleton Tree Approximation**

> “We propos an approximation called a skeleton tree.  
> intrisically, we sample a small set of skeleton genomes.  
> Then we build a phylogenetic tree approximation order for these skeleton genomes and the remaining genomes.  
> The goal is to group related genomes together before batching.  
> This reduces computation time dramatically while keeping good ordering quality.”  
> _(Pause to let audience visualize)_

---

## **Slide 13 – Implementation Steps**

> “Our method has three steps:
> 
> 1. Randomly sample a percentage of genomes to create the skeleton set.
>     
> 2. Build a phylogenetic tree on the skeleton using sketching and neighbor joining.
>     
> 3. Place the remaining genomes onto the leaves of this tree, then reorder them into batches of fixed size.
>     
> 
> This approach gives us control over runtime. It also lets us run different species groups on different machines.  
> For example, ordering 30,000 Salmonella genomes can be done overnight.  
> A full phylogenetic tree for 645,000 genomes would take around 16 years.”  
> _(Pause, smile)_

---

## **Slide 14 – Calibrating Skeleton Genomes**

> “A key challenge is choosing how many skeleton genomes to use.  
> For example, E. coli has 90,000 genomes.  
> Using more skeleton genomes improves the structure, but neighbor joining has cubic cost, so it becomes expensive.  
> We need a balance: a small skeleton set that still gives good compression.”  
> _(Pause, gesture to figure)_

---

## **Slide 15 – Uneven Species Distribution**

> “Another challenge is uneven species distribution.  
> The 10 most common species make up around 80% of the collection but only 4% of compressed size.  
> Rare species, although only 5% of the data, take up about 30% of compressed size.  
> We also have many unknown species in the ATB collection.  
> Our method needs to handle this uneven structure.”  
> _(Pause for emphasis)_

---

## **Slide 16 – Solution: Separate Compression**

> “Our solution is to divide genomes into three divisions: major species, minor species, and unknown species.  
> Each division is processed separately.  
> This improves compression efficiency and handles the uneven distribution problem.”  
> _(Pause, nod slowly)_

---

### **Transition (Slide 16 → Slide 18)**

> “With the method defined, let’s now look at the results, starting with compression.”

---

## **Slide 18 – Experiment Overview: Skeleton Tree Recompression**

> “We tested our approach on the ATB collection.  
> The collection was divided into major species, minor species, and unknown species.  
> Major species had 2.3 million genomes. Minor and unknown species had about 150,000.  
> We reordered these genomes using the skeleton tree method and compressed them with three compressors.  
> Our goal was to measure the compression improvement.”  
> _(Pause)_

---

## **Slide 19 – Compression Results: Major Species**

> The first bar is the ATB collection as distributed, and the next 3 bars is the results of our approach
> “For the 2.3 million genomes in major species, we achieved 75% reduction, storing everything under 15 gigabytes.  
> These genomes are extremely compressible.  
> Key takeaway: common species give the biggest compression gain.”  
> _(Pause)_

---

## **Slide 20 – Global Compression Results**

> “Across all species, we saw about 60% global compression reduction.  
> noticebly, the 6.5% that belong to minor and unknown species still account for almost half of the compressed size.  
> This shows that rare species are harder to compress.”  
> _(Pause)_

---

### **Transition (Slide 20 → Slide 22)**

> “Compression is one side of the story.  
> The other side is extraction speed—how fast we can access genomes.”

---

## **Slide 22 – Random Access: Fast Extraction**

> “We tested extraction time.  
> Some compressors like MBGC and XZ require decompressing the whole batch.  
> Others like AGC allow random access.  
> Our hypothesis is simple: smaller batches should give faster extraction.”  
> _(Pause)_

---

## **Slide 23 – Single Species Extraction**

> Here I tested with MBGC and AGC, MBGC give much better compression but much slower access time, while AGC is the clear winner over all in term of access speed across different batch sizes
> “For a single species dataset, larger batches give better compression but slower extraction.  
> So there is a trade-off between batch size and speed.  
> Takeaway: for single species, choose batch size based on the goal—compression or access speed.”  
> _(Pause briefly)_

---

## **Slide 24 – Diverse Species Extraction**

> “For mixed species datasets, larger batches do not improve compression.  
> But they do make extraction much slower.  
> So for mixed species collections, smaller batches are clearly better.”  
> _(Pause, emphasize small batches)_

---

## **Slide 25 – Whole Collection Extraction**

> “For the full 661k collection, we used different  batch sizes for major but fixed batch sizes of minor species.  
> Compared to AGC, our approach is 18 times faster while keeping similar compressed size.  
> Key takeaway: phylogenetic batching improves both compression and extraction speed at collection scale.”  
> _(Pause)_

---

## **Slide 26 – Conclusions**

> “To summarize:
> 
> 1. We propose a skeleton-tree phylogenetic approximation that scales to millions of genomes.
>     
> 2. We achieve about 60% global compression gain.
>     
> 3. Extraction time is reduced to under 0.5 seconds per genome, compared to almost 10 seconds before.
>     
> 
> Limitations: results are tested on the 661k and ATB collections, and would be faster on SSDs.  
Future plans include applying this to larger databases like GenBank, GTDB, and Logan-Bact, and exploring more advanced batching rules based on maximum compressed size or memory limits.
> Thank you very much for your attention.”  