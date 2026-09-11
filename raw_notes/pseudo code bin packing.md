bins = []  # list of bins, each bin is a list of genomes
kmer_threshold = MAX_KMERS_PER_BIN  # e.g., 700,000,000

for genome in genome_order:
    placed = False

    for bin in bins:
        # Estimate current distinct k-mers in bin + new genome
        estimated_kmers = estimate_kmers(bin + [genome])

        if estimated_kmers <= kmer_threshold:
            bin.append(genome)
            placed = True
            break  # placed in first fitting bin

    if not placed:
        # Create a new bin for this genome
        bins.append([genome])


Input:

    An ordered list of genomes G=[g1,g2,…,gn]G=[g1​,g2​,…,gn​]
    A maximum distinct k-mer threshold TT
Output:
    A list of genome bins B=[B1,B2,…,Bm]B=[B1​,B2​,…,Bm​]

Procedure:

    Initialize an empty list of bins: B←[]B←[]

    for each genome g∈Gg∈G:
     a. placed ←← False
     b. for each bin Bi∈BBi​∈B:
      i. Estimate the number of distinct k-mers in Bi∪{g}Bi​∪{g} using Dashing
      ii. if the estimate ≤T≤T:
       - Add gg to BiBi​
       - Set placed ←← True
       - break
     c. if not placed:
      - Create a new bin Bnew←{g}Bnew​←{g}
      - Append BnewBnew​ to BB

Return: BB