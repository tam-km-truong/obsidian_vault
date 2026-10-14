---
category: knowledge
tags:
  - zenodo
  - api
  - curl
  - jq
source_raw: "[[download from zenodo single line]]"
status: processed
---

# Zenodo API Automated Download Pipeline

## Single-Line Automated Downloader
Directly stream record metadata via Zenodo REST API, extract file keys and download URLs with `jq`, and download sequentially:

```bash
curl -s https://zenodo.org/api/records/10229555 | \
    jq -j '.files[] | "\(.key);\(.links.self)\n"' | \
    while IFS=";" read -r name url; do
        echo "Downloading $name from $url..."
        curl -o "$name" "$url"
    done
```

## Related Cheatsheets
- [[CLI - Stream Editor (sed) Recipes]] – Text parsing and stream modification
- [[CLI - xargs & Parallel Processing]] – Accelerating downloads with parallel threads
