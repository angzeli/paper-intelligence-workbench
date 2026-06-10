# Round-Trip Testing

v0.4 includes tests for import/export round trips.

Covered workflows:

- Zotero CSV -> registry -> validation
- Generic CSV + mapping -> registry
- BibTeX -> registry with duplicate handling
- RIS -> registry with conservative warnings
- Registry/notes/themes -> Obsidian Markdown vault
- Project files -> backup bundle with manifest
- Reading-list Markdown and CSV exports
- CLI import/export smoke tests

Run:

```bash
python -m pytest tests/test_import_export_v0_4.py
```

The fixtures under `data/examples/` are synthetic. They intentionally include duplicates, missing fields, and unmapped columns.
