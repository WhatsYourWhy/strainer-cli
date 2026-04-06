# strainer-cli

Offline document summarization and tagging for text and Markdown.

**strainer-cli** turns `.txt` and `.md` files into extractive summaries, keyword tags, and compression metrics — entirely offline, with zero dependencies in fast mode.

---

## Quick start

```bash
pip install .            # or just run directly — no install required
strainer my_notes.md
```

Output:

```
── Summary ─────────────────────────────────────
We observed three colonies near the edge of the
meadow during the late afternoon survey.

── Tags ────────────────────────────────────────
colonies · meadow · honeybee · survey · observed

── Stats ───────────────────────────────────────
21 words → 11 words (52.4%)
```

No network, no API keys, no accounts.

---

## Installation

Requires **Python 3.10+**.

### Fast mode (default)

```bash
pip install .
```

Or run without installing:

```bash
python -m strainer my_notes.md
```

### Smart mode (optional)

Install with embedding support for higher-quality sentence ranking:

```bash
pip install ".[smart]"
```

This pulls in `sentence-transformers`, `torch`, and `numpy`. If these aren't available, strainer falls back to fast mode automatically.

---

## CLI usage

```
strainer <file>                    Summarize a file (human-readable output)
strainer -                         Read from stdin
strainer <file> --json             Machine-readable JSON output
strainer <file> --output-md        Obsidian-friendly Markdown
strainer <file> --output-md out.md Write Markdown to a file
```

### Options

| Flag | Effect |
| ---- | ------ |
| `--json` | Output as JSON instead of human-readable text |
| `--output-md [path]` | Obsidian-friendly Markdown (to stdout or a file) |
| `-a`, `--include-anchors` | Include source-position evidence for sentences and tags |
| `-h`, `--help` | Show help |
| `--version` | Show version |

### Environment variable

Set `STRAINER_INCLUDE_ANCHORS` to any non-empty value to always include evidence anchors.

---

## Output formats

### Human-readable (default)

```
── Summary ─────────────────────────────────────
Top-ranked sentences from the source.

── Tags ────────────────────────────────────────
keyword · tags · inferred · from · text

── Stats ───────────────────────────────────────
150 words → 32 words (21.3%)
```

### JSON (`--json`)

```json
{
  "summary": "Top-ranked sentences from the source.",
  "tags": ["keyword", "tags", "inferred", "from", "text"],
  "metrics": {
    "original_words": 150,
    "summary_words": 32,
    "compression": "21.3%"
  }
}
```

### Markdown (`--output-md`)

Obsidian-compatible frontmatter with summary body — useful for piping into vaults and note systems.

---

## How it works

strainer-cli supports two ranking modes. The output is the same for both.

| Mode | Dependencies | Ranking | Speed |
| ---- | ------------ | ------- | ----- |
| **Fast** | None | Keyword-density ranking | Faster, lightweight |
| **Smart** | `sentence-transformers`, `torch`, `numpy` | Embedding-based cosine similarity | Slower, higher quality |

Before analysis, strainer strips Markdown noise: frontmatter, links, images, formatting artifacts, and reference sections. This keeps summaries focused on content, not syntax.

---

## Examples

```bash
# Basic summary
strainer my_notes.md

# JSON for scripting
strainer my_notes.md --json

# Pipe from another command
cat article.txt | strainer -

# Write Obsidian-friendly Markdown
strainer my_notes.md --output-md summary.md

# Include evidence anchors (sentence source positions)
strainer my_notes.md --json --include-anchors
```

### Windows drag & drop

Keep `Drag_Text_Here.bat` in the same folder as the project. Drag any `.txt` or `.md` file onto it.

---

## When to use strainer-cli vs an LLM API

Choose **strainer-cli** when data must stay on your machine, you need deterministic outputs, or you're feeding summaries into scripts, search, or local agents.

Choose an **LLM API** when you need abstractive rewriting, style adaptation, or reasoning over content.

---

## Development

```bash
pip install ".[dev]"
pytest
```

---

## License

MIT License. See [`LICENSE`](LICENSE).
