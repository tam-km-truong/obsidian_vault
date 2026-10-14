---
raw_tags:
  - archives
  - archive
  - fof
  - genome_to_archive
  - archive_001
  - base
  - "will contain"
  - "same5555555 archive_002"
word_count: 105
char_count: 835
processed: true
processed_note: \"[[AGC - Assembled Genomes Compressor]]\"
---

If `archives.fof` contains one archive path per line:

```bash
while IFS= read -r archive; do
    base=$(basename "$archive" .agc)
    agc listset "$archive" | awk -v a="$base" '{print $1, a}'
done < archives.fof > genome_to_archive.txt
```

For example, if `archives.fof` contains:

```text
/path/to/archive_001.agc
/path/to/archive_002.agc
/path/to/archive_003.agc
```

then `genome_to_archive.txt` will contain:

```text
SAME1019231 archive_001
SAMD1293812 archive_001
...
SAME5555555 archive_002
...
```

This streams everything into a single output file, so it's efficient even for many archives.