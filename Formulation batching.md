Below is the **order‑preserving, collection‑level** formulation that uses the **batch‑wise compressed size** as the denominator of your ratio—recognizing that

$$
\text{Compressed}_{\mathrm{whole}}(C)\;<\;\sum_{j} \text{Compressed}(B_j)
$$

since cutting breaks the global compression context.

---

## 1. Notation & Data

* **Input sequence** of $n$ genomes in fixed order:

  $$
    G = [\,g_1,\dots,g_n\,].
  $$
* **Uncompressed sizes**:
  $u_i = $ size of $g_i$.
* **Batch compressed size**:
  For any contiguous block $B_j = [g_{p},\ldots,g_{q}]$,

  $$
    C(B_j)
    = \text{compressed size of concatenating }g_p,\dots,g_q.
  $$
* **Total uncompressed** of the collection (constant):

  $$
    U_{\rm tot}
    = \sum_{i=1}^n u_i.
  $$

---

## 2. Decision: Contiguous Segmentation

We choose a segmentation into $k$ batches by indices

$$
0 = b_0 < b_1 < \cdots < b_{k-1} < b_k = n,
$$

so that batch $j$ is

$$
B_j = [\,g_{b_{j-1}+1},\dots,g_{b_j}\,].
$$

---

## 3. Objective: Collection‑Level Compression Ratio

Define the **effective compressed size under batching** as

$$
\text{Compressed}_{\rm batched}(C)
= \sum_{j=1}^{k} C(B_j).
$$

Then the **overall compression ratio** is

$$
\mathrm{CR}(C)
\;=\;
\frac{\text{Uncompressed}(C)}{\text{Compressed}_{\rm batched}(C)}
\;=\;
\frac{U_{\rm tot}}{\;\sum_{j=1}^{k} C(B_j)\;}.
$$

Because
$\;C\bigl([g_1,\dots,g_n]\bigr)<\sum_j C(B_j)$,
we know $\mathrm{CR}(C)\le U_{\rm tot}/C_{\rm whole}$; batching can only degrade the maximal ratio, but it’s required for downstream constraints.

---

## 4. Equivalent (and Simpler) Minimization

Since $U_{\rm tot}$ is constant,

$$
\max \frac{U_{\rm tot}}{\sum_j C(B_j)}
\quad\equiv\quad
\min \sum_{j=1}^{k} C(B_j).
$$

Optionally you can **penalize** the number of batches to discourage trivial singleton splits:

$$
\min_{\,k,b_1,\dots}\quad
\sum_{j=1}^{k} C(B_j)\;+\;\lambda\,k,
\quad \lambda>0.
$$

---

## 5. Constraints

1. **Contiguity**
   $\;0=b_0< b_1<\cdots<b_k=n.$

2. **Batch‑specific** (to be instantiated per use‑case), e.g.:

   * $\sum_{i=b_{j-1}+1}^{b_j}u_i\le U_{\max}$
   * All $g\in B_j$ from same species
   * $\lvert B_j\rvert \le N_{\max}$
   * etc.

---

## 6. Solution Approaches

* **Dynamic Programming** ( $O(n^2)$ ) for the pure contiguous problem.
* **ILP** with binary “cut‐after” variables $y_i$, plus big‑M or piecewise linearization of each $C(B_j)$.
* **Heuristic/Greedy** for large $n$, using sliding windows and local refinements.

---

Let me know if you’d like a detailed **DP recurrence**, an **ILP sketch**, or a **Python prototype** (e.g.\ with PuLP) next!

Here it is with all displayed formulas wrapped in `$$`:

---

## 1. Inputs & Parameters

* **Genome sequence**
  $G = [g_1, g_2, \dots, g_n]$

* **Uncompressed sizes**
  $u_i > 0,\quad i=1,\dots,n$

* **Compressed‐size function**
  For any contiguous batch $B\subseteq G$:

  $$
    C(B)\;=\;\text{compressed size of concatenating the genomes in }B.
  $$

* **Optional batch limits**

  * $U_{\max}$: maximum total uncompressed size per batch
  * $N_{\max}$: maximum number of genomes per batch
  * $\mathcal{P}(B)$: predicate enforcing biological/semantic rules on $B$

---

## 2. Decision Variables

* Number of batches:
  $k \in \{1,2,\dots,n\}$

* Breakpoints:

  $$
    \mathbf{b} = (b_0, b_1, \dots, b_k),
    \quad
    0 = b_0 < b_1 < \cdots < b_k = n
  $$

* Batches defined by $\mathbf{b}$:

  $$
    B_j = [\,g_{b_{j-1}+1},\dots,g_{b_j}\,],
    \quad j = 1,\dots,k.
  $$

---

## 3. Derived Quantities

* **Total uncompressed size**

  $$
    U_{\rm tot} = \sum_{i=1}^n u_i
  $$

* **Total compressed size under batching**

  $$
    Z(\mathbf{b}) = \sum_{j=1}^k C(B_j)
  $$

* **Compression ratio**

  $$
    \mathrm{CR}(\mathbf{b})
    = \frac{U_{\rm tot}}{Z(\mathbf{b})}
  $$

---

## 4. Objective Function

1. **Maximize compression ratio**

   $$
     \max_{\mathbf{b}}\;
     \mathrm{CR}(\mathbf{b})
     = 
     \max_{\mathbf{b}}\;
     \frac{U_{\rm tot}}{\sum_{j=1}^k C(B_j)}.
   $$

2. **Equivalent: Minimize total compressed size**

   $$
     \min_{\mathbf{b}}\;
     Z(\mathbf{b})
     =
     \min_{\mathbf{b}}\;
     \sum_{j=1}^k C(B_j).
   $$

3. **Approximate: Minimize number of batches**
   (assumes splitting overhead grows with $k$)

   $$
     \min_{\mathbf{b}}\; k
     \quad\text{or}\quad
     \min_{\mathbf{b}}\;
     \Bigl(\sum_{j=1}^k C(B_j)\Bigr) + \lambda\,k,
     \quad
     \lambda \ge 0.
   $$

---

## 5. Constraints

1. **Contiguity**

   $$
     0 = b_0 < b_1 < \cdots < b_k = n.
   $$

2. **Size limit (optional)**

   $$
     \sum_{i=b_{j-1}+1}^{b_j} u_i \;\le\; U_{\max},
     \quad j=1,\dots,k.
   $$

3. **Cardinality limit (optional)**

   $$
     b_j - b_{j-1} \;\le\; N_{\max},
     \quad j=1,\dots,k.
   $$

4. **Biological/semantic predicate (optional)**

   $$
     \mathcal{P}(B_j) = \text{true},
     \quad j=1,\dots,k.
   $$

---
Certainly. Below is a formal presentation of the **Order-Preserving Batching for Compression Optimization** problem at the **collection level**, structured clearly with inputs, variables, constraints, and the objective.

---

## **Problem: Optimal Genome Batching to Maximize Compression Ratio**

---

### **Inputs**

Let:

* $G = [g_1, g_2, \dots, g_n]$: a fixed sequence of genomes.
* $u_i \in \mathbb{R}_{>0}$: uncompressed size of genome $g_i$, for $i = 1, \dots, n$.
* $C(\cdot)$: a function that computes the compressed size of a **contiguous** batch of genomes. For any interval $B = [g_p, \dots, g_q]$, $C(B) \in \mathbb{R}_{>0}$ is the compressed size of concatenating $g_p$ to $g_q$ in that order.

---

### **Decision Variables**

* $k \in \mathbb{N}$: number of batches.
* $\mathbf{b} = (b_0, b_1, \dots, b_k)$: indices such that:

  * $0 = b_0 < b_1 < \dots < b_k = n$
  * Defines batches:
    $B_j = [g_{b_{j-1}+1}, \dots, g_{b_j}]$, for $j = 1, \dots, k$

---

### **Derived Quantities**

* **Total uncompressed size**:

  $$
  U_{\mathrm{tot}} = \sum_{i=1}^n u_i \quad \text{(constant)}
  $$

* **Total compressed size under batching**:

  $$
  Z(\mathbf{b}) = \sum_{j=1}^k C(B_j)
  $$

* **Overall compression ratio (batch-aware)**:

  $$
  \mathrm{CR}(C) = \frac{U_{\mathrm{tot}}}{Z(\mathbf{b})}
  $$

---

### **Objective Function**

We want to **maximize the compression ratio** or equivalently **minimize the total compressed size** (since $U_{\mathrm{tot}}$ is fixed):

$$
\min_{\mathbf{b}} \quad Z(\mathbf{b}) = \sum_{j=1}^{k} C(B_j)
$$

Optionally, to penalize excessive splitting (i.e. encourage fewer batches), introduce a regularization term:

$$
\min_{\mathbf{b}} \quad \sum_{j=1}^{k} C(B_j) + \lambda \cdot k
\quad \text{for some } \lambda > 0
$$

---

### **Constraints**

1. **Contiguity of batches** (enforces input order preservation):

   $$
   0 = b_0 < b_1 < \dots < b_k = n
   $$

2. **Application-specific batch constraints** (to be instantiated per use case):
   For each batch $B_j = [g_{b_{j-1}+1}, \dots, g_{b_j}]$, we may require:

   * Size constraint:

     $$
     \sum_{i = b_{j-1}+1}^{b_j} u_i \le U_{\max}
     $$
   * Cardinality constraint:

     $$
     b_j - b_{j-1} \le N_{\max}
     $$
   * Semantic constraint: all genomes in $B_j$ belong to the same species, clade, etc.

---

### **Output**

* The optimal number of batches $k^*$
* The optimal breakpoints $\mathbf{b}^* = (b_0, b_1, \dots, b_{k^*})$
* Induced segmentation: $\mathcal{B}^* = \{B_1^*, \dots, B_{k^*}^*\}$

---

### **Remarks**

* **Why batches degrade compression:**

  $$
  C([g_1, \dots, g_n]) < \sum_{j=1}^k C(B_j)
  $$

  because compressors (e.g. LZ77-based) benefit from long-range redundancy which is lost when splitting.

* **Optimization goal**: minimize the redundancy loss caused by batching while satisfying downstream constraints.

---

Would you like this translated into a dynamic programming recurrence or ILP formulation?


Certainly! Let's walk through this more carefully and precisely.

---

## **Restating the Optimization Problem**

We are given a fixed sequence of genomes $G = [g_1, g_2, \dots, g_n]$, and we want to **split it into contiguous batches** $B_1, B_2, \dots, B_k$, in such a way that we:

* **maximize the compression ratio**:

  $$
  \text{Compression Ratio} = \frac{U_{\text{tot}}}{\sum_{j=1}^{k} C(B_j)}
  $$
* or equivalently (since $U_{\text{tot}}$ is constant), **minimize the total compressed size**:

  $$
  \sum_{j=1}^{k} C(B_j)
  $$

---

## **What is $\mathbf{b} = (b_0, b_1, \dots, b_k)$?**

These are the **boundary indices** that define how the genome sequence is split into batches.

### **Properties of the indices:**

* $0 = b_0 < b_1 < b_2 < \dots < b_k = n$
* There are $k$ batches, and these boundaries define where each batch starts and ends.
* They enforce that:

  * The first batch starts after position $b_0 = 0$
  * The last batch ends at position $b_k = n$, which is the end of the input
  * All genomes appear in order, without duplication or omission.

---

## **How are batches defined from $\mathbf{b}$?**

For each $j = 1, \dots, k$, define the batch $B_j$ as:

$$
B_j = [g_{b_{j-1}+1}, \dots, g_{b_j}]
$$

### **Example:**

Let’s say $n = 10$, and you pick breakpoints:

$$
\mathbf{b} = (0, 3, 6, 10)
$$

Then:

* $B_1 = [g_1, g_2, g_3]$
* $B_2 = [g_4, g_5, g_6]$
* $B_3 = [g_7, g_8, g_9, g_{10}]$

This defines $k = 3$ batches that **preserve the order** of the original genome sequence.

---

## **Objective Function (Two Forms)**

### **1. Maximize Compression Ratio**

$$
\max_{\mathbf{b}} \quad \frac{U_{\text{tot}}}{\sum_{j=1}^k C(B_j)}
$$

where:

* $U_{\text{tot}} = \sum_{i=1}^n u_i$ is the total uncompressed size.
* $C(B_j)$ is the compressed size of batch $B_j$, computed by compressing the genomes in that batch together in order.

### **2. Equivalent: Minimize Total Compressed Size**

$$
\min_{\mathbf{b}} \quad \sum_{j=1}^k C(B_j)
$$

This version is simpler to work with, since the objective is a sum, and the constant $U_{\text{tot}}$ can be ignored for optimization purposes.

---

## **Summary of Key Concepts**

| Concept                                 | Meaning                                                            |
| --------------------------------------- | ------------------------------------------------------------------ |
| $g_i$                                   | The $i$-th genome in the fixed order                               |
| $u_i$                                   | Uncompressed size of genome $g_i$                                  |
| $\mathbf{b} = (b_0, \dots, b_k)$        | Indices where batch boundaries occur ($0 = b_0 < \dots < b_k = n$) |
| $B_j = [g_{b_{j-1}+1}, \dots, g_{b_j}]$ | The $j$-th batch defined by the boundary indices                   |
| $C(B_j)$                                | Compressed size of batch $B_j$                                     |
| Objective (max)                         | $\frac{U_{\text{tot}}}{\sum_j C(B_j)}$                             |
| Objective (min, equivalent)             | $\sum_j C(B_j)$                                                    |

---

Would you like me to go through an example with actual numbers or show how to express this in code or optimization variables?


Excellent point.

If we assume that:

* $C_{\text{opt}} = C(G)$: the compressed size of the **entire collection** $G = [g_1, \dots, g_n]$ as a single batch — this is the **best achievable** compression (i.e., the theoretical optimum),
* And that **compression is subadditive**:

  $$
  \sum_{j=1}^{k} C(B_j) \ge C(G)
  $$

  with equality only when $k = 1$,

Then minimizing $\sum_{j=1}^k C(B_j)$ can be approximated or reduced to **minimizing the number of batches** $k$, **under constraints**.

---

### 🔒 **Key Insight (your idea):**

> Since compression quality degrades when splitting the data, and since $C(G)$ is fixed and minimal, we approximate:
>
> $$
> \sum_{j=1}^k C(B_j) \approx C(G) + \text{overhead}(k)
> $$
>
> and then we can model:
>
> $$
> \min_{\mathbf{b}} \quad k
> $$

So instead of directly minimizing total compressed size, we minimize the number of batches **while satisfying all constraints** — this becomes a constrained segmentation problem.

---

## ✅ **Formal Reduction**

### **Given**

* $G = [g_1, \dots, g_n]$: ordered genomes
* $C(G)$: compressed size of the full sequence — a lower bound
* Application constraints (e.g. max size per batch, number of genomes, species homogeneity)

---

### **Decision Variables**

Same as before:
$\mathbf{b} = (b_0, b_1, \dots, b_k)$ with $0 = b_0 < \dots < b_k = n$

---

### **Objective**

$$
\min \quad k
$$

---

### **Subject to constraints on each batch $B_j = [g_{b_{j-1}+1}, \dots, g_{b_j}]$:**

1. **Size constraint** (optional):

   $$
   \sum_{i = b_{j-1}+1}^{b_j} u_i \leq U_{\max}
   $$

2. **Cardinality constraint** (optional):

   $$
   b_j - b_{j-1} \leq N_{\max}
   $$

3. **Semantic constraint** (optional): genomes in $B_j$ satisfy some biological rule (same species, clade, etc.)

---

### ✅ **Resulting Model**

You end up with a **constrained segmentation problem**, where the goal is to split the genome list into the **fewest possible contiguous batches**, while respecting the application-dependent rules.

This model:

* Is simple and efficient to solve with dynamic programming or greedy heuristics.
* Uses the theoretical optimal compression $C(G)$ as a baseline.
* Avoids directly estimating $C(B_j)$ if that's expensive or unavailable.

---

Would you like the dynamic programming formulation for this minimum batching problem next?


Certainly. Here's a complete and **clean reformulation** of the problem, written formally and clearly.

---

# 📘 Formal Optimization Problem – Batch-Aware Genome Compression

## 🧬 **Context**

In bioinformatics, we are given a **collection of genomes** $G = [g_1, g_2, \dots, g_n]$, stored in a **fixed input order** (e.g., accession number or phylogenetic order). We aim to split this collection into **contiguous batches** to maximize compression performance, subject to application-dependent constraints.

---

## 📥 **Inputs**

* $G = [g_1, g_2, \dots, g_n]$: sequence of genomes (in fixed order)
* $u_i \in \mathbb{R}^+$: uncompressed size of genome $g_i$
* $C(G)$: compressed size of the entire collection when stored as a single file
* $C(B)$: function that returns the compressed size of a batch $B \subseteq G$
* Optional constraints:

  * $U_{\max}$: max uncompressed size per batch
  * $N_{\max}$: max number of genomes per batch
  * $\mathcal{P}(B)$: predicate enforcing biological constraints on a batch (e.g., species homogeneity)

---

## 🔍 **Decision Variables**

* Integer $k$: number of batches
* Breakpoints $\mathbf{b} = (b_0, b_1, \dots, b_k)$ where:

  $$
  0 = b_0 < b_1 < \dots < b_k = n
  $$
* Each batch $B_j$ is defined as:

  $$
  B_j = [g_{b_{j-1}+1}, \dots, g_{b_j}] \quad \text{for } j = 1, \dots, k
  $$

---

## 🎯 **Objective Function**

### Option 1: Maximize Compression Ratio

Let the total uncompressed size be:

$$
U_{\text{tot}} = \sum_{i=1}^n u_i
$$

Then:

$$
\max_{\mathbf{b}} \quad \frac{U_{\text{tot}}}{\sum_{j=1}^{k} C(B_j)}
$$

### Option 2 (Equivalent): Minimize Total Compressed Size

$$
\min_{\mathbf{b}} \quad \sum_{j=1}^{k} C(B_j)
$$

### Option 3 (Approximate): Minimize Number of Batches $k$

If we assume:

$$
\sum_{j=1}^k C(B_j) \approx C(G) + \text{overhead}(k)
$$

Then we simplify to:

$$
\min_{\mathbf{b}} \quad k
$$

---

## 📎 **Constraints (per batch $B_j$)**

These are general and can be instantiated depending on the use case:

1. **Contiguity constraint** (always enforced):

   $$
   B_j = [g_{b_{j-1}+1}, \dots, g_{b_j}]
   $$

   i.e., genomes must appear in input order.

2. **Size constraint (optional):**

   $$
   \sum_{i = b_{j-1}+1}^{b_j} u_i \leq U_{\max}
   $$

3. **Cardinality constraint (optional):**

   $$
   b_j - b_{j-1} \leq N_{\max}
   $$

4. **Biological constraint (optional):**

   $$
   \mathcal{P}(B_j) = \text{true} \quad \text{(e.g., same species)}
   $$

---

## 🧩 **Summary**

| Symbol / Variable       | Meaning                                           |
| ----------------------- | ------------------------------------------------- |
| $G = [g_1, \dots, g_n]$ | Genome collection in fixed order                  |
| $u_i$                   | Uncompressed size of genome $g_i$                 |
| $C(B_j)$                | Compressed size of batch $B_j$                    |
| $\mathbf{b}$            | Breakpoints defining the batches                  |
| $B_j$                   | Batch of genomes (a contiguous subsequence)       |
| $k$                     | Number of batches                                 |
| Objective               | Maximize compression ratio or minimize total size |
| Constraints             | Control batch size, count, biological rules, etc. |

---

Would you like to continue with:

* Examples?
* Instantiating the constraints for a specific use case?
* A dynamic programming algorithm to solve this?


Great — you're aiming for a **binary integer programming (BIP)** formulation using assignment variables $x_{ij}$. Below is a formal optimization problem written in this style.

---

# 📘 Formal Optimization Problem with Assignment Variables

## 🧬 **Context**

We are given an **ordered list of genomes** $G = [g_1, g_2, \dots, g_n]$, and want to partition them into **contiguous batches** $B_1, \dots, B_k$, such that we **maximize compression efficiency** (via minimizing number of batches or estimated total compressed size), while satisfying constraints.

---

## 📥 **Inputs**

* $n$: number of genomes
* $m$: upper bound on number of batches (can be set to $n$ in worst case)
* $u_i \in \mathbb{R}^+$: uncompressed size of genome $g_i$
* $U_{\max}$: max uncompressed size per batch (optional)
* $N_{\max}$: max number of genomes per batch (optional)

---

## 🔢 **Variables**

Let:

$$
x_{ij} \in \{0,1\} \quad \text{for } i = 1, \dots, n; \quad j = 1, \dots, m
$$

Where:

$$
x_{ij} = \begin{cases} 1 & \text{if genome } g_i \text{ is assigned to batch } B_j \\ 0 & \text{otherwise} \end{cases}
$$

We also define:

* $y_j \in \{0,1\}$: indicator whether batch $B_j$ is used

  $$
  y_j = 
  \begin{cases}
  1 & \text{if } \exists i \text{ such that } x_{ij} = 1 \\
  0 & \text{otherwise}
  \end{cases}
  $$

---

## 🎯 **Objective**

### Option A: Minimize number of batches

$$
\min \sum_{j=1}^{m} y_j
$$

### Option B (if compressed size per batch $C_j$ is known/estimable):

$$
\min \sum_{j=1}^{m} C_j y_j
$$

---

## 📎 **Constraints**

### 1. **Each genome must be assigned to exactly one batch**:

$$
\sum_{j=1}^{m} x_{ij} = 1 \quad \forall i \in \{1, \dots, n\}
$$

---

### 2. **Link $x_{ij}$ and $y_j$**:

$$
x_{ij} \le y_j \quad \forall i,j
$$

→ A batch is activated if any genome is assigned to it.

---

### 3. **Contiguity constraint (very important)**

Genomes must appear **contiguously** in each batch. This constraint is subtle. One way is to enforce that, for each batch $B_j$, if $x_{ij} = 1$ and $x_{i'j} = 1$, then all genomes between $g_i$ and $g_{i'}$ must also be in $B_j$.

This can be modeled with:

$$
x_{(i-1)j} - x_{ij} + x_{(i+1)j} \ge 0 \quad \forall j, \forall i \in \{2, \dots, n-1\}
$$

This prevents “holes” in batch assignments.

---

### 4. **Batch size constraints (optional)**

#### a. Total uncompressed size per batch:

$$
\sum_{i=1}^{n} u_i x_{ij} \le U_{\max} \quad \forall j
$$

#### b. Number of genomes per batch:

$$
\sum_{i=1}^{n} x_{ij} \le N_{\max} \quad \forall j
$$

---

## 🧩 **Summary**

| Symbol      | Meaning                                  |
| ----------- | ---------------------------------------- |
| $x_{ij}$    | Genome $g_i$ assigned to batch $B_j$     |
| $y_j$       | Indicator whether batch $B_j$ is used    |
| Objective   | Minimize total number of used batches    |
| Constraints | Assignment, contiguity, and batch limits |

---

Would you like this written in standard mathematical programming syntax (e.g. for input to a solver), or would you like to explore a dynamic programming formulation instead?

Great! Let’s formulate a **general optimization model** for **batching genomes** in a way that maximizes compression efficiency, with application-specific constraints left abstract for now.

---

## ✅ **Problem Overview**

> **Goal**: Split a collection of genomes into batches to **maximize compression ratio** (or minimize compressed size), subject to **batch-level constraints** that can vary by application.

---

## ✅ **Notation**

### **Sets**

* $G = \{g_1, g_2, \dots, g_n\}$: Set of genomes.
* $B = \{b_1, b_2, \dots, b_k\}$: Set of batches (number of batches can be fixed or optimized).

### **Parameters**

* $s_{ij} \in \mathbb{R}_{\ge 0}$: Estimated compression saving when placing genome $g_i$ in batch $b_j$.

  * (or negative cost: $c_{ij}$, compressed size if genome $g_i$ is placed in batch $b_j$)
* $C_j$: Constraints specific to batch $b_j$ (e.g., max number of genomes, species homogeneity, size limits, etc.)

---

### **Decision Variables**

* $x_{ij} \in \{0, 1\}$:

  $$
  x_{ij} =
    \begin{cases}
      1 & \text{if genome } g_i \text{ is assigned to batch } b_j \\
      0 & \text{otherwise}
    \end{cases}
  $$

---

## ✅ **Objective Function**

To **maximize overall compression gain** (or minimize compressed size):

* **Maximize**:

  $$
  \sum_{i=1}^{n} \sum_{j=1}^{k} s_{ij} \cdot x_{ij}
  $$

  or
  **Minimize**:

  $$
  \sum_{i=1}^{n} \sum_{j=1}^{k} c_{ij} \cdot x_{ij}
  $$

---

## ✅ **Constraints**

1. **Each genome must be assigned to exactly one batch**:

   $$
   \sum_{j=1}^{k} x_{ij} = 1 \quad \forall i \in \{1, \dots, n\}
   $$

2. **Batch-specific constraints** (abstract for now):

   $$
   x_{*j} \in C_j \quad \forall j \in \{1, \dots, k\}
   $$

   Where $C_j$ can represent:

   * Max number of genomes in a batch
   * Total uncompressed size
   * Species homogeneity
   * etc.

---

## ✅ **Model Summary**

**Given:**

* A set of genomes $G$
* A fixed or variable number of batches $B$
* Estimated compression gains $s_{ij}$
* Application-specific batch constraints $C_j$

**Find:**

* An assignment $x_{ij} \in \{0, 1\}$

**To:**

* Maximize $\sum_{i,j} s_{ij} x_{ij}$

**Subject to:**

* Each genome assigned to one batch
* Batch-specific constraints $C_j$

---

## ✅ **Next Steps**

Depending on the **application**, we can instantiate constraints such as:

| Use Case                   | Constraint Example                                            |
| -------------------------- | ------------------------------------------------------------- |
| Species-wise processing    | All genomes in batch must be from same species                |
| Parallel computing         | Each batch has size ≤ memory limit                            |
| Streaming                  | Max total uncompressed size per batch                         |
| Compression-aware grouping | Genomes in a batch must be similar (based on sketch distance) |

---

Would you like me to express this in **pseudo-code**, **Python (e.g., with `Pyomo` or `PuLP`)**, or add a **specific use case**?

Below is the **order‑preserving, collection‑level** formulation that uses the **batch‑wise compressed size** as the denominator of your ratio—recognizing that

$$
\text{Compressed}_{\mathrm{whole}}(C)\;<\;\sum_{j} \text{Compressed}(B_j)
$$

since cutting breaks the global compression context.

---

## 1. Notation & Data

* **Input sequence** of $n$ genomes in fixed order:

  $$
    G = [\,g_1,\dots,g_n\,].
  $$
* **Uncompressed sizes**:
  $u_i = $ size of $g_i$.
* **Batch compressed size**:
  For any contiguous block $B_j = [g_{p},\ldots,g_{q}]$,

  $$
    C(B_j)
    = \text{compressed size of concatenating }g_p,\dots,g_q.
  $$
* **Total uncompressed** of the collection (constant):

  $$
    U_{\rm tot}
    = \sum_{i=1}^n u_i.
  $$

---

## 2. Decision: Contiguous Segmentation

We choose a segmentation into $k$ batches by indices

$$
0 = b_0 < b_1 < \cdots < b_{k-1} < b_k = n,
$$

so that batch $j$ is

$$
B_j = [\,g_{b_{j-1}+1},\dots,g_{b_j}\,].
$$

---

## 3. Objective: Collection‑Level Compression Ratio

Define the **effective compressed size under batching** as

$$
\text{Compressed}_{\rm batched}(C)
= \sum_{j=1}^{k} C(B_j).
$$

Then the **overall compression ratio** is

$$
\mathrm{CR}(C)\;=\;\frac{\text{Uncompressed}(C)}{\text{Compressed}_{\rm batched}(C)}\;=\;\frac{U_{\rm tot}}{\;\sum_{j=1}^{k} C(B_j)\;}.
$$

Because
$\;C\bigl([g_1,\dots,g_n]\bigr)<\sum_j C(B_j)$,
we know $\mathrm{CR}(C)\le U_{\rm tot}/C_{\rm whole}$; batching can only degrade the maximal ratio, but it’s required for downstream constraints.

---

## 4. Equivalent (and Simpler) Minimization

Since $U_{\rm tot}$ is constant,

$$
\max \frac{U_{\rm tot}}{\sum_j C(B_j)}
\quad\equiv\quad
\min \sum_{j=1}^{k} C(B_j).
$$

Optionally you can **penalize** the number of batches to discourage trivial singleton splits:

$$
\min_{\,k,b_1,\dots}\quad
\sum_{j=1}^{k} C(B_j)\;+\;\lambda\,k,
\quad \lambda>0.
$$

---

## 5. Constraints

1. **Contiguity**
   $\;0=b_0< b_1<\cdots<b_k=n.$

2. **Batch‑specific** (to be instantiated per use‑case), e.g.:

   * $\sum_{i=b_{j-1}+1}^{b_j}u_i\le U_{\max}$
   * All $g\in B_j$ from same species
   * $\lvert B_j\rvert \le N_{\max}$
   * etc.

---

## 6. Solution Approaches

* **Dynamic Programming** ( $O(n^2)$ ) for the pure contiguous problem.
* **ILP** with binary “cut‐after” variables $y_i$, plus big‑M or piecewise linearization of each $C(B_j)$.
* **Heuristic/Greedy** for large $n$, using sliding windows and local refinements.

---

Let me know if you’d like a detailed **DP recurrence**, an **ILP sketch**, or a **Python prototype** (e.g.\ with PuLP) next!
