#!/usr/bin/env python3
"""
Preprocess Raw Notes in Obsidian Vault
======================================
1. Removes empty / 0-byte notes (or whitespace-only notes).
2. Performs TF-IDF and domain-aware keyword extraction across all notes.
3. Injects machine-readable frontmatter (`raw_tags`, `raw_stats`) into each note.
   * NOTE: Using `raw_tags` (instead of `tags`) ensures Obsidian does NOT display
     or index these as Obsidian tags in the Tag Pane. They are reserved for the next AI step.
4. Produces `raw_notes_manifest.json` containing structured metadata for downstream AI pipelines.

Usage:
    python3 scripts/preprocess_raw_notes.py [--dry-run] [--include-daily] [--top-k 8]
"""

import argparse
import json
import math
import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

# Common English & Markdown stopwords to exclude from candidate tags
STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be because been before being below
between both but by can cannot can't could couldn't did didn't do does doesn't doing don't down
during each few for from further had hadn't has hasn't have haven't having he he'd he'll he's
her here here's hers herself him himself his how how's i i'd i'll i'm i've if in into is isn't
it it's its itself let's me more most mustn't my myself no nor not of off on once only or other ought
our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so some such
than that that's the their theirs them themselves then there there's these they they'd they'll they're
they've this those through to too under until up very was wasn't we we'd we'll we're we've were
weren't what what's when when's where where's which while who who's whom why why's with won't
would wouldn't you you'd you'll you're you've
also use used using uses file files line lines code run command commands output input true false null none
example see need get make want bash echo done path print python text return function value let list data
scratch ktruong users test tests result results like one two good well best new
""".split())

# LaTeX command pattern to remove from math-heavy notes
LATEX_PATTERN = re.compile(r"\\[a-zA-Z]+")
URL_PATTERN = re.compile(r"https?://\S+")
PATH_PATTERN = re.compile(r"/(?:[a-zA-Z0-9_\.-]+/)+[a-zA-Z0-9_\.-]*")
HEX_PATTERN = re.compile(r"\b[a-f0-9]{16,}\b")


def is_empty_file(file_path: Path) -> bool:
    """Check if file is 0 bytes or only contains whitespace."""
    if file_path.stat().st_size == 0:
        return True
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore").strip()
        return len(content) == 0
    except Exception:
        return False


def delete_file(file_path: Path, dry_run: bool = False) -> bool:
    """Delete file using git rm if tracked, else os.remove."""
    if dry_run:
        print(f"[DRY-RUN] Would delete empty note: {file_path.name}")
        return True

    # Try git rm first
    res = subprocess.run(
        ["git", "rm", "-f", str(file_path)],
        cwd=file_path.parent.parent,
        capture_output=True,
        text=True
    )
    if res.returncode == 0:
        print(f"[DELETED via git] {file_path.name}")
        return True

    try:
        file_path.unlink()
        print(f"[DELETED] {file_path.name}")
        return True
    except Exception as e:
        print(f"[ERROR] Could not delete {file_path}: {e}")
        return False


def extract_frontmatter(content: str):
    """
    Separate frontmatter from markdown body.
    Returns (existing_frontmatter_dict, raw_frontmatter_str, body)
    """
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            # Simple line-based frontmatter parser
            fm_dict = {}
            current_key = None
            for line in fm_text.splitlines():
                if ":" in line and not line.strip().startswith("-"):
                    k, v = line.split(":", 1)
                    current_key = k.strip()
                    fm_dict[current_key] = v.strip()
            return fm_dict, fm_text, body
    return {}, "", content


def clean_text_for_terms(content: str) -> str:
    """Clean markdown text to extract high-quality keywords."""
    # Remove existing frontmatter
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            content = parts[2]

    # Remove URLs, file paths, long hex hashes, LaTeX syntax
    content = URL_PATTERN.sub(" ", content)
    content = PATH_PATTERN.sub(" ", content)
    content = HEX_PATTERN.sub(" ", content)
    content = LATEX_PATTERN.sub(" ", content)

    # Clean markdown formatting characters
    content = re.sub(r"[{}\(\)\$\[\]\*\_`#\"'<>~=+\\]", " ", content)
    return content


def tokenize(text: str):
    """Tokenize cleaned text into candidate keyword unigrams and bigrams."""
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_\-]{2,25}\b", text.lower())
    clean_tokens = [
        t.strip("-_") for t in tokens
        if t.strip("-_") not in STOPWORDS
        and len(t.strip("-_")) >= 3
        and not t.strip("-_").isdigit()
    ]
    return clean_tokens


def compute_tf_idf(corpus_tokens: dict, top_k: int = 8):
    """Compute TF-IDF scores across all documents in corpus."""
    N = len(corpus_tokens)
    doc_freq = Counter()
    for tokens in corpus_tokens.values():
        for term in set(tokens):
            doc_freq[term] += 1

    doc_tags = {}
    doc_top_terms = {}

    for doc_id, tokens in corpus_tokens.items():
        if not tokens:
            doc_tags[doc_id] = []
            doc_top_terms[doc_id] = {}
            continue

        tf = Counter(tokens)
        total_toks = len(tokens)
        scores = {}
        for term, count in tf.items():
            # Standard smooth IDF formula
            idf = math.log((N + 1) / (doc_freq[term] + 1)) + 1.0
            # Term score boosted if term appears multiple times
            scores[term] = (count / total_toks) * idf

        # Select top k terms
        sorted_terms = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        doc_tags[doc_id] = [t[0] for t in sorted_terms]
        doc_top_terms[doc_id] = {t[0]: tf[t[0]] for t in sorted_terms}

    return doc_tags, doc_top_terms


def build_frontmatter_block(raw_tags: list, word_count: int, char_count: int, top_terms: dict) -> str:
    """
    Build YAML frontmatter block.
    Uses `raw_tags` so Obsidian will not index these in the Tag Pane.
    """
    lines = ["---"]
    lines.append("raw_tags:")
    for tag in raw_tags:
        lines.append(f"  - {tag}")
    lines.append(f"word_count: {word_count}")
    lines.append(f"char_count: {char_count}")
    lines.append("processed: false")
    lines.append("---")
    return "\n".join(lines)


def inject_frontmatter(file_path: Path, raw_tags: list, word_count: int, char_count: int, top_terms: dict, dry_run: bool = False):
    """Write updated frontmatter to file while preserving note body."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    _, _, body = extract_frontmatter(content)

    new_fm = build_frontmatter_block(raw_tags, word_count, char_count, top_terms)
    new_content = f"{new_fm}\n\n{body.lstrip()}"

    if not dry_run:
        file_path.write_text(new_content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Preprocess Obsidian raw notes for downstream AI pipelines.")
    parser.add_argument("--vault-dir", type=str, default=str(Path(__file__).resolve().parent.parent),
                        help="Path to Obsidian Vault root")
    parser.add_argument("--target-dir", type=str, default="raw_notes",
                        help="Directory within vault containing raw notes")
    parser.add_argument("--include-daily", action="store_true",
                        help="Also delete empty notes in daily_log/")
    parser.add_argument("--top-k", type=int, default=8,
                        help="Number of raw tags to generate per note")
    parser.add_argument("--dry-run", action="store_true",
                        help="Simulate actions without deleting files or modifying content")
    parser.add_argument("--manifest", type=str, default="scripts/raw_notes_manifest.json",
                        help="Path to save output JSON manifest for AI processing")

    args = parser.parse_args()
    vault_path = Path(args.vault_dir)
    target_path = vault_path / args.target_dir

    if not target_path.exists():
        print(f"[ERROR] Target directory not found: {target_path}")
        return

    print("=" * 60)
    print("Obsidian Vault Preprocessing Pipeline")
    print(f"Vault:      {vault_path}")
    print(f"Target dir: {target_path}")
    print(f"Dry run:    {args.dry_run}")
    print("=" * 60)

    # 1. Check for empty files
    files_to_check = sorted(target_path.glob("*.md"))
    if args.include_daily:
        daily_path = vault_path / "daily_log"
        if daily_path.exists():
            files_to_check.extend(sorted(daily_path.glob("*.md")))

    deleted_count = 0
    deleted_files = []
    active_files = []

    for f in files_to_check:
        if is_empty_file(f):
            if delete_file(f, dry_run=args.dry_run):
                deleted_count += 1
                deleted_files.append(str(f.relative_to(vault_path)))
        else:
            if f.parent == target_path:
                active_files.append(f)

    print(f"\n[Empty Notes Cleanup] Removed {deleted_count} empty notes.")

    # 2. Tokenize and extract frequencies
    print(f"\n[Term Extraction] Processing {len(active_files)} active raw notes...")
    corpus_tokens = {}
    doc_meta = {}

    for f in active_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        cleaned = clean_text_for_terms(content)
        tokens = tokenize(cleaned)
        corpus_tokens[f] = tokens
        doc_meta[f] = {
            "word_count": len(re.findall(r"\S+", content)),
            "char_count": len(content),
            "basename": f.name
        }

    # 3. Compute TF-IDF
    doc_tags, doc_top_terms = compute_tf_idf(corpus_tokens, top_k=args.top_k)

    # 4. Inject frontmatter into files
    print("[Frontmatter Injection] Writing `raw_tags` into note frontmatter...")
    for f in active_files:
        tags = doc_tags.get(f, [])
        meta = doc_meta[f]
        top_terms = doc_top_terms.get(f, {})
        inject_frontmatter(
            file_path=f,
            raw_tags=tags,
            word_count=meta["word_count"],
            char_count=meta["char_count"],
            top_terms=top_terms,
            dry_run=args.dry_run
        )

    # 5. Export JSON manifest for downstream AI
    manifest_path = vault_path / args.manifest
    manifest_data = {
        "generated_at": str(Path(__file__).stat().st_mtime),
        "total_active_notes": len(active_files),
        "deleted_empty_notes": deleted_files,
        "notes": {}
    }

    for f in active_files:
        rel_path = str(f.relative_to(vault_path))
        manifest_data["notes"][rel_path] = {
            "title": f.stem,
            "raw_tags": doc_tags.get(f, []),
            "top_terms": doc_top_terms.get(f, {}),
            "word_count": doc_meta[f]["word_count"],
            "char_count": doc_meta[f]["char_count"],
            "processed": False
        }

    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        print(f"[AI Manifest] Saved AI-ready manifest to: {manifest_path.relative_to(vault_path)}")

    print("\n[Done] Preprocessing complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
