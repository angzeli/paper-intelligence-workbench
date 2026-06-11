# Rule Safety

The rule engine is intentionally not a plugin runtime.

Safety guarantees:

- Rule files are JSON data only.
- Rule files cannot execute Python code.
- Rule commands do not modify registry rows, notes, drafts, BibTeX files, or
  project profiles.
- `paperwb rules report` writes only the requested Markdown report.
- Unsupported condition types fail validation.
- Existing validators remain available and unchanged.

Do not put secrets, API keys, or private manuscript text into rule files.

The engine is local-only and uses no cloud APIs, no LLM APIs, and no publisher
scraping.

