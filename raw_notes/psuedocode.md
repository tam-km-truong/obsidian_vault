---
raw_tags:
  - size
  - generate
  - phase
  - finalplacementorder
  - stats
  - batch
  - placement
  - tree
word_count: 175
char_count: 1486
processed: false
---

PROCEDURE RunPreorderPipeline(Arguments):
    // 1. Setup
    CREATE TemporaryDirectory
    
    // 2. Splitting Phase (run_split)
    IF SplittingScheme IS "nth-accession" AND nth IS NULL: THROW Error
    IF SplittingScheme IS "custom" AND custom_ref IS NULL: THROW Error
    
    Split InputGenomes into:
        - ReferenceGenomes (Skeleton)
        - RemainingGenomes
    BASED ON (cut_point, splitting_scheme, etc.)
    
    // 3. Tree Building Phase (run_attotree)
    GENERATE Phylogeny using ReferenceGenomes
    CALCULATE LeafOrder and NodeOrder from the tree
    USING (K-mer size k, Sketch size s-reference, Method m)
    
    // 4. Placement Phase (run_placement)
    PLACE RemainingGenomes into the LeafOrder of the skeleton tree
    GENERATE FinalPlacementOrder
    USING (Sketch size s-placement, k-mer size k)

    // 5. Batching (cut the order into batches of fixed size)
	 CUT FinalPlacementOrder into Batches
    GENERATE Batches of size 
    USING (batch size)

    // 5. Local inference (reorder genome within batch using local phylogeny)
	 FOR EACH BATCH:
		 GENERATE Phylogeny using all n genome in batch
		 generate batch order
    USING (K-mer size k, Sketch size s-reference, Method m)

    // 7. Finalize
    COPY FinalPlacementOrder TO OutputPath
    
    IF StatisticsEnabled:
        CONCATENATE [split_stats, tree_stats, placement_stats] 
        INTO MergedStatFile (JSON or CSV)
    
    IF NOT DebugMode:
        DELETE TemporaryDirectory
END PROCEDURE