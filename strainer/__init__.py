"""Strainer — offline document summarization and tagging."""

__version__ = "0.2.0"

from strainer.core import clean, split_sentences, summarize, tag

__all__ = ["clean", "split_sentences", "summarize", "tag", "__version__"]
