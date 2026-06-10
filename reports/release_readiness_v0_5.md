# Release Readiness v0.5

Date: 2026-06-10

## Summary

v0.5 adds an optional local search/indexing layer for larger literature-review workspaces. It remains local-first: no cloud APIs, no LLM APIs, no publisher scraping, no PDF parsing by default, and no copyrighted text fixtures.

## Implemented Index Features

- Local SQLite search cache using Python standard-library `sqlite3`.
- FTS5-backed retrieval when available.
- Fallback table-scan substring retrieval when FTS5 is unavailable.
- Project-aware index records.
- Rebuildable index cache under `.paperwb/`.
- Registry, BibTeX, note, claim, theme, tag, and optional text-sidecar indexing.
- Indexed search result ranking with source type, matched field, score, snippet, and path.
- Markdown search-result export.
- Index status report with record counts, last rebuild time, FTS status, and stale-index diagnostics.
- Index clear command for the selected project/default workflow.

## SQLite / FTS Availability

FTS5 was available in the validation environment, and indexed smoke tests reported `FTS5 enabled: true`. The backend still keeps a fallback path and tests search behavior after the FTS table is removed.

## Sidecar Text Boundary

The tool indexes only user-provided `.txt` sidecars when `--include-text` is used. It does not parse PDFs by default. Checked-in sidecars under `data/text/` and `projects/zis_photocatalysis/text/` are synthetic fixtures.

## CLI Commands Checked

- `paperwb index rebuild --project zis_photocatalysis --include-text`
- `paperwb index status --project zis_photocatalysis --include-text --check-files`
- `paperwb index clear --project zis_photocatalysis`
- `paperwb search "charge separation" --project zis_photocatalysis --indexed`
- `paperwb search observations --project zis_photocatalysis --indexed --text`
- legacy `paperwb search photocorrosion --project zis_photocatalysis`

## Generated Reports

- `reports/search_demo_v0_5.md`
- `reports/index_status_v0_5.md`
- `reports/full_text_sidecar_demo_v0_5.md`
- `reports/release_readiness_v0_5.md`
- `reports/v0_6_recommended_patch_plan.md`

## Cache-file Safety

- `.paperwb/` cache directories are ignored by git.
- No SQLite cache files should be committed.
- The SQLite index is a derived cache, not an authoritative source of registry, note, claim, BibTeX, theme, or sidecar data.

## Tests Run

- `python -m pytest tests/test_index_v0_5.py -q`: passed during implementation.
- `python -m pytest -q`: passed.
- `python scripts/validate_notebooks.py`: validated 5 notebooks.
- Representative CLI smoke tests for package import, `paperwb --help`, index rebuild, index status, indexed search, old substring search, sidecar search, and Markdown search export passed.

## Known Limitations

- Ranking is intentionally simple and lexical.
- Snippets do not highlight matched terms.
- Index status compares content hashes only when `--check-files` is provided.
- Sidecar discovery is flat: `text/PAPER_ID.txt`.
- The index does not watch files in the background.
- The index is not a replacement for a citation manager, note database, or semantic search engine.

## v0.6 Recommended Scope

Focus v0.6 on field filters, better snippets, report/search diffing, cache metadata polish, optional recursive sidecar discovery, and safer UI around stale-index repair. Avoid embeddings and remote semantic search unless the project boundary changes.

## Usability Assessment

v0.5 is usable for local indexed search across a small-to-medium literature-review project, including 100-paper synthetic stress fixtures, as long as users understand that `.paperwb/index.sqlite` is a rebuildable cache.
