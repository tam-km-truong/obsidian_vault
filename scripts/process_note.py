#!/usr/bin/env python3
"""
Hybrid Note Processor for Obsidian Vault
========================================
Combines deterministic script analysis (triage, archetype classification,
vault link matching, and validation) with LLM synthesis.

Commands:
    inspect <file>       Analyze a raw note, classify its archetype, and find candidate links.
    prompt  <file>       Generate a formatted LLM prompt tailored to the note's archetype.
    save    <file>       Validate and save LLM-generated content to processed_notes/,
                         updating the raw note's status.
    list-pending         List all unprocessed raw notes grouped by archetype.

Usage Examples:
    python3 scripts/process_note.py inspect "raw_notes/xargs.md"
    python3 scripts/process_note.py prompt "raw_notes/xargs.md"
    python3 scripts/process_note.py save --raw "raw_notes/xargs.md" --out "50_Cheatsheets/CLI - xargs & Parallel Processing.md" --file generated.md
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict


ARCHETYPES = {
    "talk_transcript": {
        "folder": "30_Presentations",
        "description": "Conference talk transcripts, presentation slides, meeting minutes, Q&A notes",
        "template": """# {title}

## Executive Summary
[2-3 sentence overview of the presentation and core message]

## Context & Motivation
- **Event / Audience:** [Where was this presented, who attended]
- **Core Problem:** [Why this work was needed]

## Technical Highlights & Key Slides
1. **[Section 1 Title]**: [Key takeaways, methods, figures]
2. **[Section 2 Title]**: [Key takeaways, methods, figures]

## Q&A & Discussion
- **Q:** [Notable question from audience/advisor]
  - **A:** [Summary of response]

## Related Notes
- [[Related Note 1]]
- [[Related Note 2]]
"""
    },
    "cheatsheet": {
        "folder": "50_Cheatsheets",
        "description": "CLI command recipes, tool syntax, programming snippets, HPC workflows",
        "template": """# {title}

## TL;DR One-Liner
```bash
[Most common, highest-value copy-paste command]
```

## Quick Reference / Options
| Flag / Option | Description | Example |
| :--- | :--- | :--- |
| `-[flag]` | [Explanation] | `[command]` |

## Real-World Recipes & HPC Workflows
### 1. [Use Case Title]
```bash
[Real bash / cluster script]
```
- **Explanation:** [Step-by-step breakdown]

## Related Cheatsheets & Tools
- [[Related Tool 1]]
- [[Related Note 2]]
"""
    },
    "math_formulation": {
        "folder": "10_Projects",
        "description": "Mathematical models, optimization problems, bin packing, algorithm proofs",
        "template": """# {title}

## Problem Statement & Objective
[Clear definition of the optimization / mathematical problem]

## Formal Notation
- Let $G = \\{g_1, g_2, \\dots, g_n\\}$: [Definition]
- Let $B_j$: [Definition]

## Mathematical Formulation
$$
[Core optimization equation / objective function]
$$

### Constraints
1. **[Constraint 1]**: [Formal statement and intuition]
2. **[Constraint 2]**: [Formal statement and intuition]

## Algorithmic Implementation & Heuristics
- **Proposed approach:** [e.g. Greedy, First Fit Decreasing, Branch & Bound]
- **Implementation in vault:** [[Related Script or Code]]

## References & Related Notes
- [[Related Note 1]]
"""
    },
    "tool_reference": {
        "folder": "40_Knowledge",
        "description": "Bioinformatics tools, literature recap, datasets, algorithms",
        "template": """# {title}

## Overview
[What the tool/paper/dataset is, author/lab, and primary purpose]

## How It Works (Algorithmic Core)
1. **[Step 1]**: [Explanation of technique, e.g. MinHash sketching, lock-free hash table]
2. **[Step 2]**: [Explanation]

## Practical Usage & CLI Recipes
```bash
[Standard invocation commands]
```

## Pros, Cons & Comparison
- **Strengths:** [Speed, memory efficiency, accuracy]
- **Limitations:** [Constraints, missing features]
- **Compared to:** [[Alternative Tool]]

## References & Vault Connections
- [[Related Note 1]]
"""
    },
    "experiment_log": {
        "folder": "20_Experiments",
        "description": "SLURM benchmarks, parameter sweeps, empirical test records",
        "template": """# {title}

## Objective
[What hypothesis or pipeline was being tested]

## Setup & Parameters
- **Dataset:** [e.g. GTDB, AllTheBacteria]
- **Compute:** [Cluster, threads, memory, SLURM job ID]
- **Script / Command:**
```bash
[Execution command]
```

## Observations & Results
- [Key metric: compression ratio, runtime, memory peak]

## Lessons Learned & Next Steps
- [What worked, what failed, next iteration]

## Related Notes
- [[Related Note 1]]
"""
    }
}


def load_manifest(vault_path: Path):
    manifest_path = vault_path / "scripts" / "raw_notes_manifest.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"notes": {}}


def extract_frontmatter(content: str):
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


def classify_note(raw_path: Path, content: str, manifest_entry: dict) -> str:
    """Classify note into one of the 5 archetypes using heuristics."""
    title_lower = raw_path.stem.lower()
    content_lower = content.lower()
    raw_tags = manifest_entry.get("raw_tags", [])
    raw_tags_str = " ".join(raw_tags).lower()

    # 1. Talk Transcript
    talk_keywords = ["transcript", "talk", "presentation", "seqbim", "dsb", "gdrbim", "slide", "slides", "good morning", "my name is"]
    if any(k in title_lower for k in ["transcript", "talk", "seqbim", "dsb"]) or any(k in content_lower[:400] for k in ["good morning", "presentation transcript", "slides for"]):
        return "talk_transcript"

    # 2. Experiment / Benchmark / Date logs
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw_path.stem) or re.match(r"^(0\d\d|exp|experiment)", title_lower):
        return "experiment_log"
    if "pending jobs" in title_lower or "benchmark" in title_lower or "step by step" in title_lower:
        return "experiment_log"

    # 3. Cheatsheet / CLI (Title check first)
    cli_keywords = ["command", "grep", "sed", "awk", "xargs", "split", "bash", "linux", "backpressure"]
    if any(k in title_lower for k in cli_keywords):
        return "cheatsheet"

    # 4. Math Formulation
    if any(k in title_lower for k in ["formulation", "math", "formulization", "argmin", "bin packing"]):
        return "math_formulation"
    if "\\mathbf" in content or "optimization problem" in content_lower or re.search(r"\$\$.+?\$\$", content, re.DOTALL):
        return "math_formulation"

    # 5. Cheatsheet / CLI by code density
    code_block_count = content.count("```") // 2
    if code_block_count >= 2 and len(content) < 4000:
        return "cheatsheet"

    # 5. Tool Reference / Knowledge base
    tool_names = ["allthebacteria", "agc", "mbgc", "mash", "mashtree", "attotree", "jellyfish", "raptor", "dashing", "rust", "mlflow", "nucleotide identity", "bwt"]
    if any(t in title_lower for t in tool_names) or any(t in raw_tags_str for t in tool_names):
        return "tool_reference"

    return "tool_reference"


def find_candidate_links(raw_path: Path, manifest: dict, top_n: int = 6):
    """Find vault notes that share tags or topics with the current note."""
    current_key = str(raw_path.relative_to(raw_path.parent.parent))
    current_entry = manifest.get("notes", {}).get(current_key, {})
    current_tags = set(current_entry.get("raw_tags", []))

    scores = {}
    for note_path, data in manifest.get("notes", {}).items():
        if note_path == current_key:
            continue
        other_tags = set(data.get("raw_tags", []))
        overlap = len(current_tags.intersection(other_tags))
        if overlap > 0:
            scores[data["title"]] = overlap

    sorted_links = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [f"[[{title}]]" for title, _ in sorted_links]


def build_prompt(raw_path: Path, vault_path: Path) -> str:
    manifest = load_manifest(vault_path)
    current_key = str(raw_path.relative_to(vault_path))
    manifest_entry = manifest.get("notes", {}).get(current_key, {})

    content = raw_path.read_text(encoding="utf-8", errors="ignore")
    _, _, body = extract_frontmatter(content)
    archetype = classify_note(raw_path, body, manifest_entry)
    arch_info = ARCHETYPES[archetype]
    candidate_links = find_candidate_links(raw_path, manifest)

    prompt = f"""### AI Note Distillation Task
You are processing a raw note from an Obsidian vault into a structured, permanent Atomic Note.

**Source Note:** `{raw_path.name}`
**Target Archetype:** `{archetype}` ({arch_info['description']})
**Recommended Destination:** `processed_notes/{arch_info['folder']}/{raw_path.name}`
**Candidate Vault Links:** {", ".join(candidate_links) if candidate_links else "None detected"}

---

### Instructions:
1. Synthesize the raw note body into a polished, structured Obsidian note following the template below.
2. Maintain exact technical integrity: DO NOT modify, break, or truncate real bash scripts, commands, flags, or mathematical equations.
3. Promote 2-4 high-level domain tags to the `tags:` frontmatter (e.g. `bioinformatics`, `pangenomics`, `bash`, `hpc`).
4. Weave relevant candidate wikilinks (`[[Note Name]]`) naturally into the prose and the 'Related Notes' section.
5. Provide the output as a complete Markdown file including YAML frontmatter.

---

### Archetype Template:
{arch_info['template'].format(title=raw_path.stem)}

---

### Raw Note Content:
```markdown
{body.strip()}
```
"""
    return prompt


def save_processed(raw_path: Path, target_rel_path: str, new_content: str, vault_path: Path):
    target_path = vault_path / "processed_notes" / target_rel_path
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Ensure frontmatter references source raw note
    fm_dict, _, body = extract_frontmatter(new_content)
    raw_wikilink = f'"[[{raw_path.stem}]]"'

    # Validate that frontmatter exists, else wrap
    if not new_content.startswith("---\n"):
        header = f"---\nsource_raw: {raw_wikilink}\nstatus: processed\n---\n\n"
        final_content = header + new_content
    else:
        # Inject source_raw if missing
        if "source_raw" not in fm_dict:
            parts = new_content.split("---\n", 2)
            updated_fm = parts[1].strip() + f"\nsource_raw: {raw_wikilink}\nstatus: processed\n"
            final_content = f"---\n{updated_fm}---\n{parts[2]}"
        else:
            final_content = new_content

    # Write processed file
    target_path.write_text(final_content, encoding="utf-8")
    print(f"[SUCCESS] Saved processed note to: {target_path.relative_to(vault_path)}")

    # Update raw note frontmatter
    raw_content = raw_path.read_text(encoding="utf-8", errors="ignore")
    raw_fm, _, raw_body = extract_frontmatter(raw_content)
    if "processed: false" in raw_content:
        raw_content = raw_content.replace("processed: false", "processed: true")
    
    proc_wikilink = f'processed_note: "[[{target_path.stem}]]"'
    if "processed_note:" not in raw_content:
        if raw_content.startswith("---\n"):
            parts = raw_content.split("---\n", 2)
            raw_content = f"---\n{parts[1].strip()}\n{proc_wikilink}\n---\n{parts[2]}"
    raw_path.write_text(raw_content, encoding="utf-8")
    print(f"[UPDATED] Marked raw note as processed: {raw_path.name}")

    # Update manifest
    manifest_path = vault_path / "scripts" / "raw_notes_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        raw_key = str(raw_path.relative_to(vault_path))
        if raw_key in manifest.get("notes", {}):
            manifest["notes"][raw_key]["processed"] = True
            manifest["notes"][raw_key]["processed_note"] = str(target_path.relative_to(vault_path))
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            print(f"[MANIFEST] Updated manifest for {raw_key}")


def main():
    parser = argparse.ArgumentParser(description="Hybrid Note Processor for Obsidian Vault")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # inspect
    p_inspect = subparsers.add_parser("inspect", help="Inspect a raw note and classify its archetype")
    p_inspect.add_argument("file", type=str, help="Path to raw note")

    # prompt
    p_prompt = subparsers.add_parser("prompt", help="Generate an LLM distillation prompt")
    p_prompt.add_argument("file", type=str, help="Path to raw note")

    # save
    p_save = subparsers.add_parser("save", help="Save a processed note and update raw note status")
    p_save.add_argument("--raw", type=str, required=True, help="Path to source raw note")
    p_save.add_argument("--out", type=str, required=True, help="Relative path under processed_notes/")
    p_save.add_argument("--file", type=str, help="File containing processed markdown content")

    # list-pending
    p_list = subparsers.add_parser("list-pending", help="List all pending raw notes by archetype")

    args = parser.parse_args()
    vault_path = Path(__file__).resolve().parent.parent

    if args.command == "inspect":
        raw_path = (vault_path / args.file).resolve() if not Path(args.file).is_absolute() else Path(args.file)
        if not raw_path.exists():
            print(f"[ERROR] File not found: {raw_path}")
            sys.exit(1)
        manifest = load_manifest(vault_path)
        content = raw_path.read_text(encoding="utf-8", errors="ignore")
        raw_key = str(raw_path.relative_to(vault_path))
        entry = manifest.get("notes", {}).get(raw_key, {})
        archetype = classify_note(raw_path, content, entry)
        links = find_candidate_links(raw_path, manifest)
        
        print("=" * 60)
        print(f"File:               {raw_path.name}")
        print(f"Classified Type:    {archetype}")
        print(f"Target Destination: processed_notes/{ARCHETYPES[archetype]['folder']}/{raw_path.name}")
        print(f"Raw Tags:           {entry.get('raw_tags', [])}")
        print(f"Candidate Links:    {', '.join(links) if links else 'None'}")
        print("=" * 60)

    elif args.command == "prompt":
        raw_path = (vault_path / args.file).resolve() if not Path(args.file).is_absolute() else Path(args.file)
        if not raw_path.exists():
            print(f"[ERROR] File not found: {raw_path}")
            sys.exit(1)
        print(build_prompt(raw_path, vault_path))

    elif args.command == "save":
        raw_path = (vault_path / args.raw).resolve() if not Path(args.raw).is_absolute() else Path(args.raw)
        if not raw_path.exists():
            print(f"[ERROR] Raw file not found: {raw_path}")
            sys.exit(1)
        if args.file:
            content = Path(args.file).read_text(encoding="utf-8")
        else:
            content = sys.stdin.read()
        save_processed(raw_path, args.out, content, vault_path)

    elif args.command == "list-pending":
        manifest = load_manifest(vault_path)
        raw_dir = vault_path / "raw_notes"
        pending = defaultdict(list)
        for f in sorted(raw_dir.glob("*.md")):
            raw_key = str(f.relative_to(vault_path))
            entry = manifest.get("notes", {}).get(raw_key, {})
            if not entry.get("processed", False):
                content = f.read_text(encoding="utf-8", errors="ignore")
                arch = classify_note(f, content, entry)
                pending[arch].append(f.name)

        print("=" * 60)
        print(f"Pending Raw Notes ({sum(len(v) for v in pending.values())} total):")
        print("=" * 60)
        for arch, notes in sorted(pending.items()):
            print(f"\n[{arch.upper()}] ({len(notes)} notes):")
            for n in notes[:10]:
                print(f"  - {n}")
            if len(notes) > 10:
                print(f"  ... and {len(notes) - 10} more")


if __name__ == "__main__":
    main()
