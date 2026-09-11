Here's a formal description of your general **optimization problem** for splitting a set of genomes $G = \{g_1, g_2, \dots, g_n\}$ into batches $\{b_1, b_2, \dots, b_m\}$, considering **compression and uncompressed sizes**:

---

### **Sets and Inputs**

* $G = \{g_1, g_2, \dots, g_n\}$: set of genomes
* $m$: maximum number of batches
* $u$: upper bound on uncompressed size of a batch
* $c$: upper bound on compressed size of a batch
* $e$: upper bound on number of genomes in a batch

### **Decision Variables**

* $x_{ij} \in \{0, 1\}$: 1 if genome $g_i$ is assigned to batch $b_j$, 0 otherwise
* $y_j \in \{0, 1\}$: 1 if batch $b_j$ is used, 0 otherwise

### **Functions**

* $U(b_j) = f_{\text{uncompressed}}(\text{ordered } \{g_i : x_{ij} = 1\})$: uncompressed size of batch $b_j$
* $C(b_j) = f_{\text{compressed}}(\text{ordered } \{g_i : x_{ij} = 1\})$: compressed size of batch $b_j$

---

## **Objective**

Choose **one** of the two objectives:

### 1. Minimize total compressed size:

$$
\min \sum_{j=1}^m C(b_j) \cdot y_j
$$

### 2. Minimize the number of batches used:

$$
\min \sum_{j=1}^m y_j
$$

---

## **Constraints**

1. **Each genome is assigned to exactly one batch**:

$$
\sum_{j=1}^m x_{ij} = 1 \quad \forall i \in \{1, \dots, n\}
$$

2. **Batch size bounds**:

   * Uncompressed size:

     $$
     U(b_j) \leq u \cdot y_j \quad \forall j \in \{1, \dots, m\}
     $$
   * Compressed size:

     $$
     C(b_j) \leq c \cdot y_j \quad \forall j \in \{1, \dots, m\}
     $$
   * Maximum number of genomes:

     $$
     \sum_{i=1}^n x_{ij} \leq e \cdot y_j \quad \forall j \in \{1, \dots, m\}
     $$

3. **Linking usage variable**:

$$
x_{ij} \leq y_j \quad \forall i,j
$$

---

This formulation assumes that **ordering matters** for compression, so $U$ and $C$ are applied to **ordered subsets**, although the ordering mechanism is not yet encoded into the model and might require either a fixed heuristic or a combinatorial extension (e.g., permutations as variables) if you want to optimize order too.

Let me know if you’d like a **specific instance implemented in code**, or if you want to explore **ordering optimization** as well.

Absolutely! Let's compare the two objective functions to clarify their **meaning**, **impact**, and **when to use them**:

---

## 🎯 Objective 1: Minimize Total Compressed Size

$$
\min \sum_{j=1}^{n} C(b_j) \cdot y_j
$$

### ✅ Meaning:

* You want to **use as many batches as needed**, **as long as** the total **compressed size** is minimized.
* The optimization will group genomes **based on how well they compress together**, even if it means using more batches.

### 📌 Use when:

* You care most about **saving disk space**.
* You expect that **similar genomes compress well together**, and you're willing to split up batches to improve compression.
* You're planning to **store or transmit** the data efficiently.

### 🔁 Behavior:

* Will likely **create many small batches** of similar genomes.
* May prefer **more batches** if that results in better compression efficiency.

---

## 🎯 Objective 2: Minimize Number of Batches

$$
\min \sum_{j=1}^{n} y_j
$$

### ✅ Meaning:

* You want to **use the fewest number of batches possible**, regardless of how well the genomes compress together.

### 📌 Use when:

* You care about **logistical or operational simplicity**:

  * Fewer batches to process.
  * Fewer I/O operations.
  * Easier batch management or fewer metadata files.
* You're constrained by **external factors**, like a fixed number of jobs or parallel pipelines.

### 🔁 Behavior:

* Will try to **pack batches as full as possible**, respecting constraints (e.g., compressed size ≤ $c$, uncompressed size ≤ $u$, etc.).
* May include **dissimilar genomes** in the same batch, even if it hurts compression, to reduce batch count.

---

## 📊 Summary Table

| Objective        | Minimize `∑ C(bj)`            | Minimize `∑ yj`              |
| ---------------- | ----------------------------- | ---------------------------- |
| Focus            | Compression efficiency        | Number of groups             |
| Encourages       | Grouping similar genomes      | Grouping as many as allowed  |
| Tends to produce | More but smaller batches      | Fewer, larger batches        |
| Good for         | Storage, transmission savings | Simple processing pipelines  |
| May tolerate     | More batches                  | Lower compression efficiency |

---

### 🔧 Hybrid Option

As mentioned before, you can combine both:

$$
\min \alpha \sum_{j=1}^{n} C(b_j) \cdot y_j + \beta \sum_{j=1}^{n} y_j
$$

Where you tune $\alpha$, $\beta$ depending on whether you care more about **compression** or **batch count**.

Let me know your main goal (e.g., optimizing disk usage or simplifying workflows), and I can help choose or tune the right objective!
\Yes! Here's your objective function written **with proper parentheses** for clarity:

$$
\min \left( \alpha \sum_{j=1}^{m} C(b_j) \cdot y_j + \beta \sum_{j=1}^{m} y_j \right)
$$

This makes it clear that the **entire expression** is the objective to be minimized.

Let me know if you want it in plain text, LaTeX code, or programming syntax (e.g. Pyomo, CVXPY, etc.).
