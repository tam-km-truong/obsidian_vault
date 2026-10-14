#!/usr/bin/env python3
"""
Zotero Bibliography Syncer & Obsidian Dashboard Generator
==========================================================
Parses a BibTeX library exported from Zotero (e.g. zotero_library.bib),
deduplicates entries, cross-references with existing vault knowledge notes,
and generates:
  1. A master Literature Dashboard:
     processed_notes/40_Knowledge/Literature/Zotero Bibliography Dashboard.md
  2. Individual structured Literature Notes:
     processed_notes/40_Knowledge/Literature/Papers/<citekey>.md

Usage:
    python3 scripts/sync_zotero_bib.py
    python3 scripts/sync_zotero_bib.py --bib zotero_library.bib --dashboard-only
    python3 scripts/sync_zotero_bib.py --help
"""

import argparse
import glob
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers & Cleaning
# ---------------------------------------------------------------------------

def clean_latex(text: str) -> str:
    """Strip LaTeX formatting commands and outer braces from text."""
    if not text:
        return ""
    t = text
    # Clean common LaTeX commands
    t = t.replace(r"\textbar", "|")
    t = t.replace(r"\&", "&")
    t = t.replace(r"\%", "%")
    t = t.replace(r"\_", "_")
    t = t.replace(r"\$", "$")
    t = t.replace(r"\textbackslash", "\\")
    t = t.replace(r"\hyphen", "-")
    t = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", t)
    t = t.replace("{", "").replace("}", "")
    # Collapse multiple whitespace
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def parse_authors(author_str: str):
    """Parse BibTeX author string into a list of formatted author names and a short citation."""
    if not author_str:
        return [], "Unknown"
    
    clean_str = clean_latex(author_str)
    raw_authors = [a.strip() for a in clean_str.split(" and ") if a.strip()]
    parsed = []
    
    for a in raw_authors:
        if "," in a:
            parts = a.split(",", 1)
            last = parts[0].strip()
            first = parts[1].strip()
            parsed.append(f"{last}, {first}")
        else:
            parsed.append(a)
            
    if not parsed:
        short = "Unknown"
    elif len(parsed) == 1:
        first_last = parsed[0].split(",")[0]
        short = first_last
    elif len(parsed) == 2:
        short = f"{parsed[0].split(',')[0]} & {parsed[1].split(',')[0]}"
    else:
        short = f"{parsed[0].split(',')[0]} et al."
        
    return parsed, short


def categorize_paper(title: str, abstract: str, keywords: str) -> str:
    """Categorize paper into vault-aligned research domains."""
    blob = f"{title} {abstract} {keywords}".lower()
    
    if any(k in blob for k in ["k-mer", "kmer", "sketch", "minhash", "hyperloglog", "dashing", "jellyfish", "bloom filter", "minimizer", "syncmer", "niqki"]):
        return "Sketching & K-mers"
    elif any(k in blob for k in ["compress", "mbgc", "agc", "bwt", "burrows-wheeler", "phrase complexity", "storage", "gzip", "zstd", "decompress"]):
        return "Sequence Compression"
    elif any(k in blob for k in ["phylogen", "mashtree", "attotree", "tree", "species tree", "phylogroup", "evolutionary", "lineage", "phylopack"]):
        return "Phylogenetics & Trees"
    elif any(k in blob for k in ["escherichia", "allthebacteria", "gtdb", "bacterial", "pangenome", "refseq", "genbank", "isolate", "microbiome"]):
        return "Bacterial Genomics & Datasets"
    elif any(k in blob for k in ["bin packing", "optimization", "partitioning", "sparse matrix", "argmin", "algorithm", "heuristic", "graph", "out-of-core"]):
        return "Algorithms & Optimization"
    elif any(k in blob for k in ["neural", "machine learning", "deep learning", "inference", "feature selection"]):
        return "Machine Learning & Theory"
    else:
        return "Bioinformatics & Genomics"


# ---------------------------------------------------------------------------
# BibTeX Parsing
# ---------------------------------------------------------------------------

def parse_bib_fields(body: str) -> dict:
    """Parse key=value pairs handling balanced braces and quotes."""
    fields = {}
    pos = 0
    n = len(body)
    
    while pos < n:
        m = re.compile(r"([a-zA-Z_0-9-]+)\s*=\s*").search(body, pos)
        if not m:
            break
        key = m.group(1).lower()
        val_start = m.end()
        if val_start >= n:
            break
            
        char = body[val_start]
        if char == "{":
            depth = 1
            curr = val_start + 1
            while curr < n and depth > 0:
                if body[curr] == "{":
                    depth += 1
                elif body[curr] == "}":
                    depth -= 1
                curr += 1
            val = body[val_start + 1 : curr - 1]
            pos = curr
        elif char == "\"":
            curr = val_start + 1
            while curr < n:
                if body[curr] == "\"" and body[curr - 1] != "\\":
                    break
                curr += 1
            val = body[val_start + 1 : curr]
            pos = curr + 1
        else:
            m_end = re.compile(r"[,}\n\r]").search(body, val_start)
            if m_end:
                val = body[val_start : m_end.start()]
                pos = m_end.start()
            else:
                val = body[val_start:]
                pos = n
        fields[key] = val.strip()
        
    return fields


def parse_bibtex_file(filepath: Path) -> list:
    """Reads and parses an entire BibTeX file into a list of clean entry dicts."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    pattern = re.compile(r"@(\w+)\s*\{\s*([^,]+),", re.MULTILINE)
    matches = list(pattern.finditer(content))
    entries = []

    for i, m in enumerate(matches):
        entry_type = m.group(1).lower()
        citekey = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[start:end]
        
        fields = parse_bib_fields(body)
        title = clean_latex(fields.get("title", fields.get("shorttitle", "Untitled")))
        authors_list, authors_short = parse_authors(fields.get("author", ""))
        
        # Clean year
        raw_year = fields.get("year", "")
        year_m = re.search(r"\b(19\d\d|20\d\d)\b", raw_year)
        year = int(year_m.group(1)) if year_m else None
        
        journal = clean_latex(fields.get("journal", fields.get("booktitle", fields.get("publisher", ""))))
        doi = clean_latex(fields.get("doi", ""))
        abstract = clean_latex(fields.get("abstract", ""))
        keywords = clean_latex(fields.get("keywords", ""))
        url = clean_latex(fields.get("url", fields.get("howpublished", "")))
        
        topic = categorize_paper(title, abstract, keywords)
        
        entries.append({
            "citekey": citekey,
            "type": entry_type,
            "title": title,
            "authors_list": authors_list,
            "authors_short": authors_short,
            "year": year,
            "journal": journal,
            "doi": doi,
            "abstract": abstract,
            "keywords": keywords,
            "url": url,
            "topic": topic,
            "raw_fields": fields
        })

    return entries


def deduplicate_entries(entries: list) -> list:
    """Group entries by normalized title and pick the richest one while preserving aliases."""
    grouped = defaultdict(list)
    for e in entries:
        norm_title = re.sub(r"[^a-zA-Z0-9]", "", e["title"].lower())
        if not norm_title or len(norm_title) < 8:
            norm_title = e["citekey"]
        grouped[norm_title].append(e)

    deduped = []
    for norm_title, group in grouped.items():
        if len(group) == 1:
            primary = group[0]
            primary["aliases"] = []
            deduped.append(primary)
        else:
            # Score each entry by completeness
            def score(item):
                s = 0
                if item["abstract"]: s += 10
                if item["doi"]: s += 5
                if item["journal"]: s += 3
                if item["year"]: s += 2
                if not item["citekey"].endswith("a"): s += 1
                return s

            group.sort(key=score, reverse=True)
            primary = group[0]
            aliases = [g["citekey"] for g in group[1:]]
            primary["aliases"] = aliases
            deduped.append(primary)

    # Sort primarily by Year (descending), then First Author
    deduped.sort(key=lambda x: (x["year"] or 0, x["authors_short"]), reverse=True)
    return deduped


# ---------------------------------------------------------------------------
# Vault Cross-Referencing
# ---------------------------------------------------------------------------

def index_vault_notes(vault_root: Path) -> dict:
    """Scan processed_notes to find existing concept notes for automatic linking."""
    concept_map = {}
    processed_dir = vault_root / "processed_notes"
    if not processed_dir.exists():
        return {}

    for md_file in processed_dir.glob("**/*.md"):
        if "Daily_Logs" in md_file.parts or "Literature" in md_file.parts:
            continue
        stem = md_file.stem
        concept_map[stem.lower()] = stem
        
        if " - " in stem:
            prefix = stem.split(" - ")[0].strip()
            concept_map[prefix.lower()] = stem

    return concept_map


def find_vault_connections(paper: dict, concept_map: dict) -> list:
    """Find vault notes mentioned in paper title or abstract."""
    blob = f"{paper['title']} {paper['abstract']}".lower()
    connections = set()

    # High-signal domain keyword mappings
    domain_shortcuts = {
        "agc": "AGC - Assembled Genomes Compressor",
        "mbgc": "MBGC - Multiple Bacterial Genome Compressor",
        "mash": "Mash & MinHash Sketching",
        "minhash": "Mash & MinHash Sketching",
        "dashing": "dashing2 - HyperLogLog Genome Sketching",
        "dashing2": "dashing2 - HyperLogLog Genome Sketching",
        "jellyfish": "Jellyfish - Lock-Free K-mer Counting",
        "bwt": "Burrows-Wheeler Transform (BWT) in Genomics",
        "raptor": "Raptor - Hierarchical Interleaved Bloom Filters",
        "allthebacteria": "AllTheBacteria - 1.9M Uniform Bacterial Genomes",
        "gtdb": "GTDB - Step-by-Step Dataset Download & Setup",
        "bin packing": "Algorithm - Bin Packing & Preorder Pipeline Pseudocode",
        "batching": "Mathematical Formulation - Order-Preserving Batching",
        "attotree": "Attotree - Fast Tree Construction & Troubleshooting",
        "mashtree": "Mashtree - Rapid Comparative Genomics",
        "seqkit": "EXP_075 - Seqkit Hashing and MBGC Validation",
        "hyperloglog": "dashing2 - HyperLogLog Genome Sketching",
        "phylopack": "PhyloPack & Seqkit Hashing on ATB",
    }

    for term, target_note in domain_shortcuts.items():
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, blob):
            connections.add(target_note)

    for term, target_note in concept_map.items():
        if len(term) < 4:
            continue
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, blob):
            connections.add(target_note)

    return sorted(list(connections))


# ---------------------------------------------------------------------------
# Markdown Generators
# ---------------------------------------------------------------------------

def generate_paper_note(paper: dict, vault_connections: list) -> str:
    """Generate structured markdown note for an individual paper."""
    citekey = paper["citekey"]
    title = paper["title"]
    year_str = str(paper["year"]) if paper["year"] else "n.d."
    zotero_link = f"zotero://select/items/@{citekey}"

    # Build YAML aliases
    aliases = [f'"{title}"', f'"{paper["authors_short"]} ({year_str})"', f'"@{citekey}"']
    for a in paper.get("aliases", []):
        aliases.append(f'"@{a}"')

    # Build YAML authors
    authors_yaml = "\n".join([f'  - "{a}"' for a in paper["authors_list"][:15]])
    if len(paper["authors_list"]) > 15:
        authors_yaml += '\n  - "... and others"'

    tags = ["literature", "paper", paper["topic"].lower().replace(" ", "-").replace("&", "and")]

    content = f"""---
category: literature
citekey: "{citekey}"
title: "{title}"
aliases:
{chr(10).join(f"  - {a}" for a in aliases)}
authors:
{authors_yaml}
year: {paper['year'] or 'null'}
journal: "{paper['journal']}"
doi: "{paper['doi']}"
topic: "{paper['topic']}"
tags:
{chr(10).join(f"  - {t}" for t in tags)}
status: unread
---

# {title}

- **Authors:** {paper['authors_short']}
- **Year:** {year_str}
- **Journal / Venue:** *{paper['journal'] or 'Preprint / Misc'}*
- **Links:** """
    
    if paper["doi"]:
        content += f"[DOI](https://doi.org/{paper['doi']}) | "
    if paper["url"]:
        content += f"[Web Link]({paper['url']}) | "
    content += f"[Open in Zotero Desktop]({zotero_link})\n\n"

    # Abstract Section
    content += "## Abstract\n"
    if paper["abstract"]:
        content += f"> {paper['abstract']}\n\n"
    else:
        content += "*No abstract available in Zotero metadata.*\n\n"

    # Algorithmic & Methodological Notes Section
    content += """## Algorithmic & Methodological Notes
- **Core Problem:** 
- **Methodology / Technique:** 
- **Benchmarks & Scale:** 

## Relevance to Our Projects & Vault Connections
"""
    if vault_connections:
        for conn in vault_connections[:8]:
            content += f"- [[{conn}]]\n"
    else:
        content += "- Relates to: [[10_Projects/Research Project & Publication Plan]]\n"

    # BibTeX Citation
    content += f"""
## BibTeX Citation
```bibtex
@{paper['type']}{{{citekey},
  title = {{{paper['title']}}},
  author = {{{' and '.join(paper['authors_list'])}}},
  year = {{{paper['year'] or ''}}},
  journal = {{{paper['journal']}}},
  doi = {{{paper['doi']}}}
}}
```
"""
    return content


def generate_dashboard_note(deduped_papers: list, total_raw: int) -> str:
    """Generate the Master Literature Dashboard note."""
    now_str = datetime.now().strftime("%Y-%m-%d")
    
    # Topic breakdown
    topic_counts = Counter(p["topic"] for p in deduped_papers)
    year_counts = Counter(p["year"] for p in deduped_papers if p["year"])
    with_abstracts = sum(1 for p in deduped_papers if p["abstract"])
    with_dois = sum(1 for p in deduped_papers if p["doi"])

    sorted_years = sorted(year_counts.keys(), reverse=True)
    recent_years = [y for y in sorted_years if y >= 2020]

    md = f"""---
category: dashboard
tags:
  - dashboard
  - literature
  - zotero
  - bibliography
last_synced: "{now_str}"
---

# Zotero Bibliography Dashboard

> [!INFO] **Library Overview**
> - **Total Raw Entries:** {total_raw} | **Unique Papers:** {len(deduped_papers)}
> - **Papers with Abstracts:** {with_abstracts} ({int(with_abstracts/len(deduped_papers)*100)}%)
> - **Papers with DOI:** {with_dois}
> - **Last Synced:** {now_str}
> - **Data Source:** `zotero_library.bib`

---

## Research Domain Distribution
| Domain / Topic | Paper Count | Quick Filter Anchor |
| :--- | :--- | :--- |
"""
    for topic, cnt in topic_counts.most_common():
        anchor = topic.lower().replace(" ", "-").replace("&", "")
        md += f"| **{topic}** | {cnt} | [Jump to {topic}](#{anchor}) |\n"

    md += """
---

## Timeline (2020–Present)
"""
    timeline_str = " • ".join([f"**{y}:** {year_counts[y]} papers" for y in recent_years])
    md += f"{timeline_str}\n\n---\n"

    # Group papers by Topic
    by_topic = defaultdict(list)
    for p in deduped_papers:
        by_topic[p["topic"]].append(p)

    for topic, cnt in topic_counts.most_common():
        papers_in_topic = by_topic[topic]
        anchor = topic.lower().replace(" ", "-").replace("&", "")
        md += f"\n## {topic}\n\n"
        md += f"*Total: {len(papers_in_topic)} papers*\n\n"
        md += "| Year | Paper / Literature Note | First Author | Journal / Venue | Zotero |\n"
        md += "| :---: | :--- | :--- | :--- | :---: |\n"

        for p in papers_in_topic:
            year_val = p["year"] if p["year"] else "n.d."
            # Link to individual note
            note_link = f"[[{p['citekey']}|{p['title']}]]"
            zotero_btn = f"[Open](zotero://select/items/@{p['citekey']})"
            venue = p["journal"] if p["journal"] else ("Preprint" if "biorxiv" in p.get("url","").lower() or "arxiv" in p.get("url","").lower() else "—")
            if len(venue) > 30:
                venue = venue[:28] + "…"
                
            md += f"| {year_val} | {note_link} | {p['authors_short']} | {venue} | {zotero_btn} |\n"

    md += """
---

## Complete Bibliography (Chronological)

<details>
<summary>Click to expand all papers sorted by year</summary>

| Year | Citekey | Title | Authors | Zotero |
| :---: | :--- | :--- | :--- | :---: |\n"""

    for p in deduped_papers:
        year_val = p["year"] if p["year"] else "n.d."
        note_link = f"[[{p['citekey']}]]"
        title_disp = p['title'].replace("|", "-")
        if len(title_disp) > 75:
            title_disp = title_disp[:72] + "…"
        zotero_btn = f"[Open](zotero://select/items/@{p['citekey']})"
        md += f"| {year_val} | {note_link} | {title_disp} | {p['authors_short']} | {zotero_btn} |\n"

    md += """
</details>

---

## How to Sync & Update
1. In Zotero: Right-click library $\\to$ **Export Library** $\\to$ `zotero_library.bib` (Check **"Keep updated"**).
2. Run script in terminal:
   ```bash
   python3 scripts/sync_zotero_bib.py
   ```
"""
    return md


# ---------------------------------------------------------------------------
# Main Execution Flow
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Sync Zotero BibTeX export with Obsidian Vault")
    parser.add_argument("--bib", default="zotero_library.bib", help="Path to exported BibTeX file")
    parser.add_argument("--dashboard-only", action="store_true", help="Only rebuild dashboard, do not write paper notes")
    parser.add_argument("--force", action="store_true", help="Overwrite existing paper notes")
    args = parser.parse_args()

    vault_root = Path(__file__).resolve().parent.parent
    bib_path = vault_root / args.bib

    if not bib_path.exists():
        print(f"Error: BibTeX file not found at {bib_path}")
        print("Please export your Zotero library as 'zotero_library.bib' in the vault root.")
        sys.exit(1)

    print(f"[*] Parsing {bib_path.name}...")
    raw_entries = parse_bibtex_file(bib_path)
    print(f"    Found {len(raw_entries)} raw entries.")

    deduped = deduplicate_entries(raw_entries)
    print(f"    After deduplication: {len(deduped)} unique papers.")

    # Target directories
    lit_dir = vault_root / "processed_notes" / "40_Knowledge" / "Literature"
    papers_dir = lit_dir / "Papers"
    papers_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate Master Dashboard Note
    dashboard_path = lit_dir / "Zotero Bibliography Dashboard.md"
    print(f"[*] Generating Dashboard: {dashboard_path.relative_to(vault_root)}")
    dashboard_content = generate_dashboard_note(deduped, len(raw_entries))
    dashboard_path.write_text(dashboard_content, encoding="utf-8")

    # 2. Generate Individual Paper Notes
    if not args.dashboard_only:
        print("[*] Indexing vault concept notes for auto-linking...")
        concept_map = index_vault_notes(vault_root)
        print(f"    Indexed {len(concept_map)} vault concepts.")

        written = 0
        skipped = 0
        for paper in deduped:
            note_file = papers_dir / f"{paper['citekey']}.md"
            if note_file.exists() and not args.force:
                skipped += 1
                continue
            
            conns = find_vault_connections(paper, concept_map)
            note_content = generate_paper_note(paper, conns)
            note_file.write_text(note_content, encoding="utf-8")
            written += 1

        print(f"[+] Complete! Written: {written} new paper notes, Skipped (already exist): {skipped}.")
    else:
        print("[+] Dashboard generated (skipped paper notes as requested).")

    print("\nSummary:")
    print(f"  - Dashboard: processed_notes/40_Knowledge/Literature/Zotero Bibliography Dashboard.md")
    print(f"  - Literature Notes: processed_notes/40_Knowledge/Literature/Papers/ ({len(deduped)} total)")


if __name__ == "__main__":
    main()
