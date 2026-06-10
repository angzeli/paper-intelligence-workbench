# Hostile Maintainer Review v0.5

Date: 2026-06-10

Scope reviewed: package architecture, CLI behavior, project profiles, registry and BibTeX workflows, note parsing, claim extraction, theme mapping, evidence maps, citation audits, import/export workflows, local SQLite search/indexing, tests, docs, notebooks, generated reports, synthetic data, backward compatibility, data safety, and non-destructive behavior.

Validation and probes run during review:

- `python -m pytest -q` passed.
- `python scripts/validate_notebooks.py` passed.
- `python -m paper_workbench.cli --help` passed.
- Indexed-search smoke probes were run against a temporary index under `/private/tmp`.
- Legacy substring search was compared against indexed search.
- Project backup bundle export was probed under `/private/tmp`.
- Zotero import dry-run was probed and its generated report was removed afterward.
- Tracked file listing was inspected for cache databases, PDFs, absolute maintainer paths, and cloud/LLM dependency risk.

## Release Verdict

Do not cut a broad external v0.5 release yet. The repository is substantially stronger than the v0.1-v0.4 line, and no cloud, LLM, publisher-scraping, tracked-PDF, or tracked-cache-database blocker was found. However, v0.5 introduces a local index and user-provided text sidecars, and two data-trust issues are too important to ship as-is:

1. Stale index diagnostics can report a clean index while deleted or omitted local source records remain indexed.
2. Backup bundles omit v0.5 text sidecars, so a user can create a "backup" that silently excludes source material now supported by the tool.

These are not cosmetic. They affect whether a researcher can trust search results and backups.

## Release-Blocking Issues

### RB-1: Stale index diagnostics miss deleted or orphaned indexed records

Files: `paper_workbench/index.py`

Relevant code:

- `index_status()` builds `stored` from the database and only loops over `current_records`.
- It reports current records missing from the index and changed hashes, but never reports indexed records that no longer exist in the current local inputs.
- See `paper_workbench/index.py` around `index_status()` lines 438-478.

Observed behavior:

- A temporary project index for `zis_photocatalysis` was rebuilt with `--include-text`.
- It contained 15 records, including 2 `text` records.
- Running `paperwb index status --project zis_photocatalysis --check-files --index /private/tmp/.../index.sqlite` reported:
  - `text: 2`
  - `No stale-index warnings.`

This is a false sense of safety when the current check set omits or has lost previously indexed records. The same one-way comparison problem applies to deleted registry rows, notes, BibTeX records, themes, and sidecars.

Why this blocks release:

- Indexed search can continue returning deleted note or sidecar content.
- `--strict` can exit cleanly while the cache contains stale records.
- This undermines v0.5's claim of stale-index diagnostics.

Required fix:

- Compare both directions:
  - local-current records missing from index
  - indexed records absent from current local inputs
  - changed hashes
- Report orphaned indexed record IDs and source paths.
- Make `--strict` fail on orphaned/stale indexed records.
- Add tests for deleted note, deleted sidecar, removed registry row, and `--include-text` mismatch cases.

### RB-2: Backup bundles omit v0.5 text sidecars

Files: `paper_workbench/exports.py`, `paper_workbench/cli.py`, docs under `docs/BACKUP_BUNDLES.md` and `docs/EXPORTS.md`

Relevant code:

- `export_bundle()` copies registry, BibTeX, themes, notes, reports, and optional PDFs.
- It has no parameter or path resolution for `text/` sidecar directories.
- See `paper_workbench/exports.py` around `export_bundle()` lines 353-384.

Observed behavior:

- `paperwb export bundle --project zis_photocatalysis --out /private/tmp/.../zis_bundle` produced registry, BibTeX, notes, themes, and reports.
- The bundle did not include `projects/zis_photocatalysis/text/zis_charge_2025.txt` or `projects/zis_photocatalysis/text/zis_stability_2024.txt`.

Why this blocks release:

- v0.5 promotes user-provided text sidecars as local source data for search.
- A backup command that excludes those sidecars is incomplete and can mislead users into thinking a project has been preserved.
- The default no-PDF safety boundary is correct, but sidecar text is not equivalent to PDFs; it is now first-class local input.

Required fix:

- Include sidecars in backup bundles by default when a project/default `text/` directory exists.
- Record sidecar files in `manifest.json`.
- Keep cache databases excluded.
- Keep PDFs excluded unless `--include-pdfs` is explicitly used.
- Add tests proving sidecars are included and `.paperwb/index.sqlite` is not.

## High-Priority Issues

### HP-1: Indexed FTS search does not preserve substring behavior

Files: `paper_workbench/index.py`, `paper_workbench/search.py`, docs under `docs/LOCAL_SEARCH.md`, `docs/SQLITE_INDEX.md`, `README.md`

Observed behavior:

- Legacy search: `paperwb search corrosion --project zis_photocatalysis` returns the photocorrosion paper, note, and claim.
- Indexed search: `paperwb search corrosion --project zis_photocatalysis --indexed --index /private/tmp/.../index.sqlite` returns `No matches.`

Cause:

- `search_index()` uses FTS first and falls back to LIKE only when the FTS table is missing or an FTS query errors.
- It does not fall back when FTS returns zero rows.
- FTS token matching does not behave like the older substring search.
- See `paper_workbench/index.py` around `search_index()`, `_search_with_fts()`, `_search_with_like()`, and `_fts_query()` lines 499-584.

Impact:

- Existing users who switch to `--indexed` lose expected substring matches.
- README/docs say fallback substring search exists, but in common FTS-enabled environments it is not used for zero-result substring queries.

Required fix:

- Either implement transparent substring fallback when FTS returns no rows, or document indexed search as token/prefix-only and update examples.
- Prefer preserving old search semantics for normal non-exact queries.
- Add parity tests comparing old and indexed search for substring cases such as `corrosion` vs `photocorrosion`.

### HP-2: Indexed search reports leak absolute local paths

Files: `paper_workbench/index.py`

Observed behavior:

- An indexed Markdown search export contained:
  - `/Users/liangze/Desktop/paper-intelligence-workbench/projects/zis_photocatalysis/text/zis_stability_2024.txt`

Cause:

- `search_results_markdown()` emits `result.path` as stored.
- `index_status_markdown()` emits the raw index path.
- Project profile paths resolve to absolute paths before indexing.
- See `paper_workbench/index.py` around `search_results_markdown()` and `index_status_markdown()` lines 656-711.

Impact:

- Reports are less portable.
- Shared reports can leak maintainer/user filesystem paths.
- This conflicts with earlier v0.3/v0.4 work to avoid hardcoded absolute paths in generated artifacts.

Required fix:

- Relativize report paths against the workspace root or project root before emitting Markdown.
- Preserve raw paths internally if needed, but do not write absolute user paths into default reports.
- Add tests asserting generated search/status Markdown does not contain the workspace absolute prefix.

### HP-3: v0.5 generated reports are not protected by report regression coverage

Files: `tests/test_golden_reports.py`, `tests/test_index_v0_5.py`, `reports/*v0_5.md`

The existing golden report system covers stress reports, but v0.5 search/index reports are not meaningfully pinned. The new reports most likely to drift or mislead external users are:

- `reports/search_demo_v0_5.md`
- `reports/index_status_v0_5.md`
- `reports/full_text_sidecar_demo_v0_5.md`
- `reports/release_readiness_v0_5.md`

Required fix:

- Add stable regression checks for v0.5 report sections, key counts, no absolute paths, sidecar inclusion/exclusion statements, and expected stale-index warnings.

### HP-4: `paperwb search --indexed` has an unhelpful missing-index error

Files: `paper_workbench/index.py`, `paper_workbench/cli.py`

Observed behavior:

- `paperwb search charge --indexed --index /private/tmp/.../missing.sqlite` exits with:
  - `error: Index not found: /private/tmp/.../missing.sqlite`

Impact:

- The error is technically correct but not actionable for a new external user.

Required fix:

- Include the rebuild command in the error, for example:
  - `Run paperwb index rebuild --project PROJECT --include-text`
- Add a CLI smoke test.

## Medium-Priority Issues

### MP-1: Import dry-run writes a report into the project by default

Files: `paper_workbench/cli.py`

Observed behavior:

- `paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run` correctly avoids registry writes, but it still writes:
  - `projects/zis_photocatalysis/reports/import_zotero_csv.md`

Relevant code:

- `_finish_import()` always reserves and writes the import report, even for `result.dry_run`.
- See `paper_workbench/cli.py` around lines 600-646.

Impact:

- This is not data loss, but it violates the ordinary expectation that dry-run is non-mutating unless an output path is explicitly requested.

Recommended fix:

- Either print the dry-run report to stdout by default, or document that import dry-runs still create audit reports.
- If keeping the file, make the CLI message explicit before writing.

### MP-2: Default legacy `data/` index workflow is confusing

Observed behavior:

- `paperwb index rebuild --include-text --index /private/tmp/.../default_index.sqlite` indexed notes, claims, tags, themes, and one text sidecar, but no papers or BibTeX entries because default paths point to `data/registries/papers.csv` and `data/bibtex/library.bib`, while the rich example files are `example_papers.csv` and `example_library.bib`.

Impact:

- New users experimenting outside project profiles get a partial index without obvious warning.

Recommended fix:

- Emit warnings when registry or BibTeX inputs are empty/missing during index rebuild.
- Improve quickstart examples to use explicit example paths or a project profile.

### MP-3: Malformed or wrong-schema index databases are not handled gracefully

`index_status()` assumes the SQLite file has `records` and `metadata` tables. A user pointing `--index` at the wrong SQLite file will get an opaque low-level SQLite error through the top-level exception handler.

Recommended fix:

- Validate index schema before querying.
- Return a friendly diagnostic and non-zero status under `--strict`.

### MP-4: Sidecar discovery is flat and silent

`build_index_records()` only indexes `*.txt` directly under one text directory. That is defensible for v0.5, but recursive folders are common in real note vaults. The current docs mention sidecars but should more explicitly state the flat-directory limitation.

### MP-5: `index clear` reports success even when no index exists

`clear_index()` returns silently if the file is missing, and the CLI prints `Cleared index records...`. This is not dangerous because it clears only cache records, but it is misleading.

## Low-Priority Polish

- `obsidian_export_summary()` and `bundle_export_summary()` still label summaries as `v0.4`; not harmful, but stale in a v0.5 release train.
- Search-result snippets are useful but do not mark matched terms.
- `records_fts` schema has no migration path beyond a metadata value; acceptable for v0.5 but should be acknowledged.
- The v0.5 release-readiness report says the repo is usable with 100-paper stress fixtures, but the specific index smoke examples use the small `zis_photocatalysis` project.
- The repository has accumulated many generated reports. The report index helps, but external users may struggle to tell canonical current-stage reports from historical stage reports.

## Missing Tests

Add tests for:

- Deleted note, deleted sidecar, removed registry row, and removed BibTeX entry after index rebuild.
- `index status --check-files --strict` failing for orphaned indexed records.
- Bundle export including `text/` sidecars and excluding `.paperwb/`.
- Indexed substring parity with legacy search.
- Search/status Markdown path relativization.
- Missing-index CLI error includes a rebuild suggestion.
- Dry-run import report behavior, whichever behavior is selected.
- Wrong-schema SQLite index file gives a friendly error.
- v0.5 generated report regression sections and no absolute paths.
- Stress-project indexed search against at least one 100-paper synthetic project.

## Documentation Mismatches

- README and SQLite docs describe fallback substring search, but an FTS-enabled index does not fall back to substring matching when FTS returns zero rows.
- Backup bundle docs do not mention that v0.5 sidecar text is excluded.
- Import docs say dry-run reports what would happen, but they do not warn that a report file is written to the project by default.
- v0.5 release readiness overstates scale confidence for the index layer because the indexed workflow probes are mostly small-project examples.
- Full-text sidecar docs correctly say no PDF parsing and synthetic fixtures only; no copyright issue found there.

## CLI Usability Problems

- `paperwb search --indexed` should suggest `paperwb index rebuild` when the index is missing.
- `paperwb index status --check-files` should explain whether text sidecars were included in the staleness check.
- `paperwb index clear` should say when there was no index to clear.
- Import dry-runs should either write only to stdout by default or explicitly announce the report path before mutating `reports/`.
- Project search output and Markdown reports should prefer workspace-relative paths.

## Data-Safety Risks

- Backup bundles currently miss text sidecars.
- Stale indexed sidecar or note content can remain searchable without diagnostics.
- Absolute user paths can leak into shared Markdown search/status reports.
- No tracked copyrighted PDFs were found.
- No tracked SQLite cache database was found.
- No cloud API, LLM API, or publisher-scraping dependency was found in package code or project metadata.
- Existing no-PDF-by-default behavior for bundle export is correct and should be preserved.

## Recommended Fix Sequence

1. Fix stale-index diagnostics with two-way comparison and strict-mode failures.
2. Include text sidecars in backup bundles while still excluding PDFs and cache databases.
3. Restore old substring expectations for indexed search or narrow the documentation honestly.
4. Relativize search and index-status report paths.
5. Add v0.5 report regression tests.
6. Improve missing-index, wrong-index, and `index clear` CLI messages.
7. Decide and document import dry-run report semantics.
8. Add stress-project indexed search smoke coverage.

## Bottom Line

The repository is close, but v0.5 should not be released externally until index freshness and sidecar backup completeness are fixed. The rest can be patched in follow-up hardening without changing the product boundary.
