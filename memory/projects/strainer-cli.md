# strainer-cli

**Repo:** https://github.com/WhatsYourWhy/strainer-cli
**Local:** `C:\Users\Justin\strainer-cli`
**Version:** 0.2.0
**License:** MIT

## What It Is
Offline extractive summarizer and keyword tagger for .txt and .md files. Two modes: fast (keyword density, zero deps) and smart (sentence-transformer embeddings). Entirely local, no network.

## History
- Started as FleaHive, renamed to strainer-cli
- v0.1.0: Single Strainer.py script, JSON-only output
- v0.2.0 (2026-04-06): Restructured as proper Python package, human-readable default output, pyproject.toml, pip-installable, 18 tests

## Architecture (v0.2.0)
```
strainer/
  __init__.py    # version, public API exports
  __main__.py    # python -m strainer
  core.py        # clean, summarize, tag, sentence splitting
  cli.py         # CLI parsing, output formatting (human/json/markdown)
pyproject.toml   # pip install, entry points, extras [smart] [dev]
tests/           # 18 tests (clean, summarize, cli)
Drag_Text_Here.bat  # Windows drag-and-drop
```

## What's Next
- GitHub Pages demo: single HTML paste-and-strain page, keyword mode in JS, zero backend
- Stop word list in tag() is biased toward academic papers — consider making configurable
- Git history cleanup consideration (many Codex-generated README commits)
