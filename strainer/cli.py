"""Command-line interface for strainer."""

import json
import os
import re
import sys
from typing import Optional, Sequence

from strainer.core import clean, summarize, tag


def _format_human(
    summary_text: str,
    tags: list,
    original_words: int,
    summary_words: int,
    compression: str,
) -> str:
    """Render a terminal-friendly plain-text report."""
    ruler = "\u2500"  # ─
    width = 48

    lines = [
        f"\u2500\u2500 Summary {ruler * (width - 11)}",
        summary_text,
        "",
        f"\u2500\u2500 Tags {ruler * (width - 8)}",
        " \u00b7 ".join(tags) if tags else "(none)",
        "",
        f"\u2500\u2500 Stats {ruler * (width - 9)}",
        f"{original_words} words \u2192 {summary_words} words ({compression})",
    ]
    return "\n".join(lines)


def main(argv: Sequence[str]) -> int:
    include_anchors = bool(os.getenv("STRAINER_INCLUDE_ANCHORS"))
    args = list(argv[1:])

    # --include-anchors / -a
    if any(flag in args for flag in ("-a", "--include-anchors")):
        include_anchors = True
        args = [arg for arg in args if arg not in ("-a", "--include-anchors")]

    # --json
    output_json = False
    if "--json" in args:
        output_json = True
        args = [arg for arg in args if arg != "--json"]

    # --output-md [path]
    output_md_path: Optional[str] = None
    if "--output-md" in args:
        idx = args.index("--output-md")
        if idx + 1 < len(args) and not args[idx + 1].startswith("-"):
            output_md_path = args[idx + 1]
            del args[idx : idx + 2]
        else:
            output_md_path = ""
            del args[idx]

    # --help / -h
    if any(flag in args for flag in ("-h", "--help")):
        print(_help_text())
        return 0

    # --version
    if "--version" in args:
        from strainer import __version__

        print(f"strainer {__version__}")
        return 0

    if not args:
        print("Usage: strainer <file> [options]", file=sys.stderr)
        print("       strainer --help", file=sys.stderr)
        return 1

    path = args[0]
    try:
        text = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    except Exception as exc:
        if output_json:
            print(json.dumps({"error": str(exc)}))
        else:
            print(f"Error: {exc}", file=sys.stderr)
        return 1

    cleaned_text = clean(text)
    summary_result = summarize(cleaned_text, already_cleaned=True, include_anchors=include_anchors)
    if isinstance(summary_result, dict):
        summary_text = summary_result["text"]
        evidence = {"summary": summary_result.get("anchors", [])}
    else:
        summary_text = summary_result
        evidence = {}

    tag_result = tag(
        summary_text + " " + cleaned_text,
        include_anchors=include_anchors,
        source_text=cleaned_text,
    )
    if isinstance(tag_result, list) and tag_result and isinstance(tag_result[0], dict):
        tags = [entry["tag"] for entry in tag_result]
        evidence["tags"] = tag_result
    else:
        tags = tag_result

    original_words = len(re.findall(r"\w+", text))
    summary_words = len(re.findall(r"\w+", summary_text))
    compression_ratio = summary_words / original_words if original_words else 0
    compression = f"{compression_ratio:.1%}"

    # --- Markdown output ---
    if output_md_path is not None:
        frontmatter_tags = ", ".join(tags)
        markdown_lines = [
            "---",
            f"tags: [{frontmatter_tags}]",
            f"original_words: {original_words}",
            f"summary_words: {summary_words}",
            f'compression: "{compression}"',
            "---",
            "",
            "## Summary",
            summary_text,
        ]
        if include_anchors:
            markdown_lines.extend(
                [
                    "",
                    "## Evidence",
                    "```json",
                    json.dumps(evidence, indent=2, ensure_ascii=False),
                    "```",
                ]
            )
        markdown_output = "\n".join(markdown_lines).strip() + "\n"
        if output_md_path:
            with open(output_md_path, "w", encoding="utf-8") as handle:
                handle.write(markdown_output)
        print(markdown_output, end="")
        return 0

    # --- JSON output ---
    if output_json:
        result = {
            "summary": summary_text,
            "tags": tags,
            "metrics": {
                "original_words": original_words,
                "summary_words": summary_words,
                "compression": compression,
            },
        }
        if include_anchors:
            result["evidence"] = evidence
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    # --- Human-readable output (default) ---
    print(
        _format_human(summary_text, tags, original_words, summary_words, compression)
    )
    return 0


def main_entry() -> None:
    """Entry point for the ``strainer`` console script."""
    sys.exit(main(sys.argv))


def _help_text() -> str:
    return """\
strainer — offline document summarization and tagging

Usage:
  strainer <file>                  Summarize a .txt or .md file
  strainer -                       Read from stdin
  strainer <file> --json           Output as JSON
  strainer <file> --output-md      Output as Obsidian-friendly Markdown
  strainer <file> --output-md out.md   Write Markdown to a file

Options:
  --json                 Machine-readable JSON output
  --output-md [path]     Obsidian-friendly Markdown (optionally to a file)
  -a, --include-anchors  Include source-position evidence for sentences and tags
  -h, --help             Show this help
  --version              Show version

Environment:
  STRAINER_INCLUDE_ANCHORS   Any non-empty value enables evidence anchors
"""
