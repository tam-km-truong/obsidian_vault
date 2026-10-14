---
category: knowledge
tags:
  - ncbi
  - cli
  - datasets
  - download
source_raw: "[[NCBI datasets]]"
status: processed
---

# NCBI Datasets CLI Reference

## Downloading Dehydrated Genome Packages
NCBI Datasets CLI allows batch downloading dehydrated accession packages to save bandwidth before rehydration:

```bash
datasets download genome accession \
    --inputfile gtdb_bac_accession.txt \
    --dehydrated \
    --include genome \
    --exclude cds,rna,protein,gff3
```

### Options
- `--dehydrated`: Downloads only the metadata and fetch-manifest TSV without the large genomic sequence binaries.
- `--include genome`: Requests full genomic FASTA sequences upon rehydration.
- `--exclude ...`: Strips unnecessary CDS and GFF3 files to minimize size.

## Rehydration Command
```bash
datasets rehydrate --directory ./ncbi_dataset/
```

## Related Notes
- [[NCBI RefSeq Assembly Downloads]] – Alternative FTP download method
- [[AllTheBacteria - 1.9M Uniform Bacterial Genomes]] – Public database counterpart
