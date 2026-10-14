---
category: knowledge
tags:
  - refseq
  - ncbi
  - download
  - bash
source_raw: "[[download from refseq]]"
status: processed
---

# NCBI RefSeq Assembly Downloads

## Fetching Global Assembly Summary
To download the complete bacterial assembly summary table directly from the NCBI GenBank / RefSeq FTP server:

```bash
wget ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt
```

## Parsing FTP Paths with awk
```bash
awk -F'\t' 'NR>2 {print $20}' assembly_summary.txt | while read url; do
    fname=$(basename $url)_genomic.fna.gz
    wget "$url/$fname"
done
```

## Related Notes
- [[NCBI Datasets CLI Reference]] – Modern CLI alternative to raw FTP
- [[Zenodo API Automated Download Pipeline]] – Direct API downloads
