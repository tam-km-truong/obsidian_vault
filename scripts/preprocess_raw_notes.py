#!/usr/bin/env python3
"""
Preprocess Raw Notes in Obsidian Vault (with k-mer / n-gram term extraction)
===========================================================================
1. Removes empty / 0-byte notes (or whitespace-only notes).
2. Performs k-mer / n-gram (k = 1, 2, 3) TF-IDF extraction:
   - Captures unigrams, bigrams, and trigrams (e.g., "genome compression", "hash table", "random access").
   - Intelligently filters stopwords, CLI flags, LaTeX math symbols, and URL/path noise.
   - Performs phrase deduplication so sub-phrases do not redundantly consume tag slots.
3. Injects machine-readable frontmatter (`raw_tags`, `raw_stats`) into each note.
   * NOTE: Using `raw_tags` (instead of `tags`) ensures Obsidian does NOT display
     or index these as Obsidian tags in the Tag Pane. They are reserved for the next AI step.
4. Produces `raw_notes_manifest.json` containing structured metadata for downstream AI pipelines.

Usage:
    python3 scripts/preprocess_raw_notes.py [--dry-run] [--top-k 8] [--max-k 3]
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
scratch ktruong users test tests result results like one two good well best new thing things
set pipefail non-zero status exit returned pasted image png jpg
""".split())

# LaTeX math keywords to clean out from math-heavy notes
LATEX_STOPWORDS = {
    "mathbf", "mathcal", "quad", "qquad", "dots", "cdots", "ddots", "sum", "prod",
    "frac", "sqrt", "text", "textbf", "textit", "left", "right", "begin", "end",
    "align", "equation", "alpha", "beta", "gamma", "delta", "epsilon", "theta",
    "lambda", "sigma", "omega", "times", "le", "ge", "ne", "notin", "cup", "cap",
    "subset", "subseteq", "infty", "tot", "argmin"
}

URL_PATTERN = re.compile(r"https?://\S+")
IMAGE_PATTERN = re.compile(r"!\s*\[\[.*?\]\]")
MD_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\([^)]+\)")
PATH_PATTERN = re.compile(r"/(?:[a-zA-Z0-9_\.-]+/)+[a-zA-Z0-9_\.-]*")
HEX_PATTERN = re.compile(r"\b[a-f0-9]{16,}\b")
CLI_FLAG_PATTERN = re.compile(r"\s+--?[a-zA-Z0-9_\-]+")
LATEX_PATTERN = re.compile(r"\\[a-zA-Z]+")


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
            fm_dict = {}
            for line in fm_text.splitlines():
                if ":" in line and not line.strip().startswith("-"):
                    k, v = line.split(":", 1)
                    fm_dict[k.strip()] = v.strip()
            return fm_dict, fm_text, body
    return {}, "", content


def clean_text(content: str) -> str:
    """Clean markdown text to remove code/path artifacts, URLs, and formatting."""
    # Remove existing frontmatter
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            content = parts[2]

    content = IMAGE_PATTERN.sub(" ", content)
    content = MD_LINK_PATTERN.sub(r"\1", content)
    content = URL_PATTERN.sub(" ", content)
    content = CLI_FLAG_PATTERN.sub(" ", content)
    content = PATH_PATTERN.sub(" ", content)
    content = HEX_PATTERN.sub(" ", content)
    content = LATEX_PATTERN.sub(" ", content)
    return content


def extract_ngrams(content: str, max_k: int = 3):
    """
    Extract n-grams (k = 1..max_k words) respecting phrase boundaries.
    Prevents n-grams from spanning across punctuation, code blocks, or lines.
    """
    cleaned = clean_text(content)
    # Split by clause / punctuation delimiters
    chunks = re.split(r"[\n\r\.\,\;\:\!\?\(\)\[\]\{\}\"\'\`\|\#\*\<\>\=\+\\\/]", cleaned)
    doc_terms = []

    for chunk in chunks:
        raw_words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_\-]{1,25}\b", chunk.lower())
        raw_words = [w.strip("-_") for w in raw_words if len(w.strip("-_")) >= 2]
        if not raw_words:
            continue

        clean_words = []
        for w in raw_words:
            if w in LATEX_STOPWORDS or w in STOPWORDS:
                clean_words.append(None)
            elif re.match(r"^[a-z]_[a-z0-9]$", w):
                clean_words.append(None)
            elif w.isdigit() or len(w) < 3:
                clean_words.append(None)
            else:
                clean_words.append(w)

        # Extract contiguous sequences of valid content words
        current_seq = []
        for w in clean_words:
            if w is not None:
                current_seq.append(w)
            else:
                if current_seq:
                    seq_len = len(current_seq)
                    for k in range(1, min(max_k, seq_len) + 1):
                        for i in range(seq_len - k + 1):
                            ngram = " ".join(current_seq[i:i+k])
                            doc_terms.append(ngram)
                    current_seq = []
        if current_seq:
            seq_len = len(current_seq)
            for k in range(1, min(max_k, seq_len) + 1):
                for i in range(seq_len - k + 1):
                    ngram = " ".join(current_seq[i:i+k])
                    doc_terms.append(ngram)

    return doc_terms


def compute_tf_idf(corpus_tokens: dict, top_k: int = 8):
    """
    Compute TF-IDF for n-grams and select non-redundant top candidate tags.
    """
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
            k = len(term.split())
            # Standard smooth IDF formula
            idf = math.log((N + 1) / (doc_freq[term] + 1)) + 1.0
            # Boost multi-word phrases so informative bigrams/trigrams can compete with high-frequency unigrams
            phrase_boost = 1.0 + (k - 1) * 0.45
            scores[term] = (count / total_toks) * idf * phrase_boost

        # Rank candidates by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Select top k tags while avoiding redundant sub-phrases
        selected = []
        for term, score in ranked:
            words = set(term.split())
            is_redundant = False
            for s in selected:
                s_words = set(s.split())
                # If candidate is a sub-phrase or contains existing tag completely
                if words.issubset(s_words) or s_words.issubset(words):
                    is_redundant = True
                    break
            if not is_redundant:
                selected.append(term)
            if len(selected) >= top_k:
                break

        doc_tags[doc_id] = selected
        doc_top_terms[doc_id] = {t: tf[t] for t in selected}

    return doc_tags, doc_top_terms


def build_frontmatter_block(raw_tags: list, word_count: int, char_count: int, existing_fm: dict = None) -> str:
    """
    Build YAML frontmatter block with raw_tags and basic stats.
    Preserves existing processed status and processed_note if present.
    """
    lines = ["---"]
    lines.append("raw_tags:")
    for tag in raw_tags:
        if " " in tag or ":" in tag or "-" in tag:
            lines.append(f'  - "{tag}"')
        else:
            lines.append(f"  - {tag}")
    lines.append(f"word_count: {word_count}")
    lines.append(f"char_count: {char_count}")

    is_processed = False
    if existing_fm and str(existing_fm.get("processed", "false")).lower() == "true":
        is_processed = True
    lines.append(f"processed: {'true' if is_processed else 'false'}")

    if existing_fm and "processed_note" in existing_fm:
        val = existing_fm["processed_note"].strip().strip('"').strip("'")
        lines.append(f'processed_note: "{val}"')

    lines.append("---")
    return "\n".join(lines)


def inject_frontmatter(file_path: Path, raw_tags: list, word_count: int, char_count: int, dry_run: bool = False):
    """Write updated frontmatter to file while preserving note body and existing status."""
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    existing_fm, _, body = extract_frontmatter(content)

    new_fm = build_frontmatter_block(raw_tags, word_count, char_count, existing_fm=existing_fm)
    new_content = f"{new_fm}\n\n{body.lstrip()}"

    if not dry_run:
        file_path.write_text(new_content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Preprocess Obsidian raw notes with k-mer/n-gram (k=1,2,3) TF-IDF.")
    parser.add_argument("--vault-dir", type=str, default=str(Path(__file__).resolve().parent.parent),
                        help="Path to Obsidian Vault root")
    parser.add_argument("--target-dir", type=str, default="raw_notes",
                        help="Directory within vault containing raw notes")
    parser.add_argument("--top-k", type=int, default=8,
                        help="Number of raw tags to generate per note")
    parser.add_argument("--max-k", type=int, default=3,
                        help="Maximum k-mer word length (1=unigram, 2=bigram, 3=trigram)")
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

    print("=" * 65)
    print(f"Obsidian Vault Preprocessing Pipeline (k-mers: 1..{args.max_k})")
    print(f"Vault:      {vault_path}")
    print(f"Target dir: {target_path}")
    print(f"Max k:      {args.max_k} (unigrams, bigrams, trigrams)")
    print(f"Top tags:   {args.top_k}")
    print(f"Dry run:    {args.dry_run}")
    print("=" * 65)

    # 1. Check for empty files
    files_to_check = sorted(target_path.glob("*.md"))
    deleted_count = 0
    deleted_files = []
    active_files = []

    for f in files_to_check:
        if is_empty_file(f):
            if delete_file(f, dry_run=args.dry_run):
                deleted_count += 1
                deleted_files.append(str(f.relative_to(vault_path)))
        else:
            active_files.append(f)

    if deleted_count > 0:
        print(f"\n[Empty Notes Cleanup] Removed {deleted_count} empty notes.")
    else:
        print("\n[Empty Notes Cleanup] No empty notes found.")

    # 2. Tokenize and extract k-mers
    print(f"\n[Term Extraction] Extracting k-mers (1..{args.max_k}) across {len(active_files)} active notes...")
    corpus_tokens = {}
    doc_meta = {}

    for f in active_files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        tokens = extract_ngrams(content, max_k=args.max_k)
        corpus_tokens[f] = tokens
        doc_meta[f] = {
            "word_count": len(re.findall(r"\S+", content)),
            "char_count": len(content),
            "basename": f.name
        }

    # 3. Compute TF-IDF
    doc_tags, doc_top_terms = compute_tf_idf(corpus_tokens, top_k=args.top_k)

    # 4. Inject frontmatter into files
    print("[Frontmatter Injection] Updating `raw_tags` in note frontmatter...")
    for f in active_files:
        tags = doc_tags.get(f, [])
        meta = doc_meta[f]
        inject_frontmatter(
            file_path=f,
            raw_tags=tags,
            word_count=meta["word_count"],
            char_count=meta["char_count"],
            dry_run=args.dry_run
        )

    # 5. Export JSON manifest for downstream AI
    manifest_path = vault_path / args.manifest
    manifest_data = {
        "max_k": args.max_k,
        "total_active_notes": len(active_files),
        "deleted_empty_notes": deleted_files,
        "notes": {}
    }

    for f in active_files:
        rel_path = str(f.relative_to(vault_path))
        tags = doc_tags.get(f, [])
        k_breakdown = Counter([len(t.split()) for t in tags])
        manifest_data["notes"][rel_path] = {
            "title": f.stem,
            "raw_tags": tags,
            "k_distribution": {f"{k}_words": v for k, v in sorted(k_breakdown.items())},
            "term_frequencies": doc_top_terms.get(f, {}),
            "word_count": doc_meta[f]["word_count"],
            "char_count": doc_meta[f]["char_count"],
            "processed": False
        }

    if not args.dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
        print(f"[AI Manifest] Saved updated AI-ready manifest to: {manifest_path.relative_to(vault_path)}")

    print("\n[Done] Multi-word k-mer preprocessing complete.")
    print("=" * 65)


if __name__ == "__main__":
    main()
