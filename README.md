# paper-intelligence-workbench

`paper-intelligence-workbench` is a local-first CLI tool for small academic literature-review projects. It manages paper metadata, structured Markdown notes, user-recorded claims, evidence links, BibTeX validation, project profiles, theme coverage, citation-audit reports, and an optional SQLite search cache without cloud services, publisher scraping, or LLM APIs.

The MVP is designed for projects with roughly 10 to 100 papers where a student or researcher wants to know which papers are read, which claims are supported, which citations are incomplete, and which literature-review themes still need stronger evidence.

v0.3 adds deterministic synthetic stress projects, report-regression snapshots, parser edge fixtures, CLI stress tests, and performance sanity reporting to make the repository easier to evaluate before using it on a real 100-paper review.

v0.4 adds local import/export interoperability for Zotero-style CSV, generic CSV mappings, BibTeX, RIS, Obsidian-friendly Markdown vaults, backup bundles, richer reading lists, project summaries, and report indexes.

v0.5 adds an optional local SQLite search index, FTS5-backed search when available, substring fallback behavior, index diagnostics, and synthetic full-text sidecar fixtures.

v0.6 adds a literature-review authoring workbench with evidence matrices, claim banks, citation banks, paragraph plans, subsection readiness scoring, and writing packets. These are planning aids only; the tool still does not write final prose or invent evidence.

v0.7 adds local document ingestion and metadata reconciliation: file scans, SHA256 hashes, PDF path linking, duplicate-file detection, missing-file reports, and text-sidecar audits. It does not download, scrape, OCR, or summarize documents.

## What It Does

- Maintains a CSV paper registry.
- Generates structured Markdown note templates.
- Parses notes and extracts user-entered claims.
- Validates registry records and BibTeX entries.
- Maps tags to review themes.
- Searches registry rows, note bodies, and claims.
- Builds a local project-aware SQLite index for larger workspaces.
- Indexes optional user-provided plain-text sidecars without parsing PDFs.
- Scans and audits local user-provided files, hashes, missing file references, duplicate files, and text sidecars.
- Generates Markdown reports for inventory, reading status, BibTeX audit, evidence maps, citation audits, missing notes, and weak claims.
- Manages multiple project profiles under `projects/`.
- Runs workspace health diagnostics with `paperwb doctor`.
- Exports claims, registries, reading lists, and theme-specific claim data.
- Generates clearly synthetic stress corpora for local regression testing.
- Imports local Zotero-style CSV, generic CSV, BibTeX, and RIS files into registries with duplicate reports.
- Exports Obsidian-friendly Markdown vaults and local backup bundles.
- Generates theme-specific writing aids from tracked local claims and citations.

## What It Does Not Do

- It does not scrape publishers.
- It does not download or include copyrighted PDFs.
- It does not copy, move, delete, OCR, or summarize user documents.
- It does not replace Zotero or CSL formatting tools.
- It does not fabricate paper metadata, quotes, claims, summaries, or conclusions.
- It does not use cloud services, LLM APIs, or embeddings.
- It does not decide whether a scientific claim is true.
- It does not write polished literature-review prose as if it were user-authored.

## Installation

From the repository root:

```bash
python -m pip install -e ".[test]"
```

The CLI entry point is:

```bash
paperwb --help
```

You can also run it without installing:

```bash
python -m paper_workbench.cli --help
```

In offline or restricted-network environments, `pip` may be unable to fetch build dependencies for editable install. In that case, use the no-install `python -m paper_workbench.cli ...` form from the repository root, or install after local build dependencies such as `setuptools` and `pytest` are available.

## Quickstart

Initialize a workspace:

```bash
paperwb init
```

Validate the synthetic example registry:

```bash
paperwb validate-registry data/registries/example_papers.csv
```

Validate the synthetic example BibTeX library:

```bash
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
```

Extract claims from notes:

```bash
paperwb claims data/notes --output reports/example_claims.csv
```

Generate reports:

```bash
paperwb report inventory --registry data/registries/example_papers.csv --force
paperwb report bibtex-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --force
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --force
```

Run v0.2 diagnostics and a section outline:

```bash
paperwb doctor --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out reports/workspace_health.md --force
paperwb report section-outline --theme photocorrosion --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out reports/photocorrosion_section_outline.md --force
```

## Project Profile Workflow

Project profiles keep independent registry, notes, BibTeX, themes, and reports under `projects/`.

```bash
paperwb project list
paperwb project init demo_review
paperwb project validate zis_photocatalysis
paperwb search photocorrosion --project zis_photocatalysis
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search photocorrosion --project zis_photocatalysis --indexed
paperwb files scan --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --force
paperwb report evidence-map --project zis_photocatalysis --force
paperwb export claims-json --project zis_photocatalysis --out data/processed/zis_claims.json --force
```

The legacy `data/` workflow remains supported.

## v0.3 Stress Workflow

Generate a deterministic synthetic stress project:

```bash
paperwb synthetic generate --project stress_demo --papers 100 --claims 220 --themes 6 --domain zis
```

Run the checked-in stress tests and performance sanity report:

```bash
python -m pytest tests/test_synthetic_stress.py tests/test_cli_stress.py tests/test_golden_reports.py
python scripts/performance_sanity.py --force
```

The checked-in stress projects under `projects/stress_*` are synthetic fixtures only. They intentionally include duplicate metadata, weak claims, missing evidence locations, orphan notes, and unlinked BibTeX entries so validation and reports can be regression-tested.

## v0.4 Import / Export Workflow

Run a dry-run import before writing to a registry:

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --force
paperwb import csv data/examples/generic_papers.csv --mapping data/examples/generic_mapping.json --dry-run --force
paperwb import bibtex data/examples/library_import.bib --dry-run --force
paperwb import ris data/examples/library.ris --dry-run --force
```

Export local writing and backup artifacts:

```bash
paperwb export obsidian --project zis_photocatalysis --out exports/obsidian_zis
paperwb export bundle --project zis_photocatalysis --out exports/zis_bundle
paperwb export reading-list --theme photocorrosion --project zis_photocatalysis --out reports/reading_list_photocorrosion.md --force
```

Imports preserve existing registry rows. `--fill-missing` fills only blank fields on matched records; it does not overwrite non-empty user fields.

## v0.5 Indexed Search Workflow

Build a rebuildable local index:

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index status --project zis_photocatalysis --include-text --check-files
```

Search indexed registry, BibTeX, note, claim, theme, tag, and sidecar records:

```bash
paperwb search "charge separation" --project zis_photocatalysis --indexed
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
paperwb search "charge separation" --project zis_photocatalysis --indexed --out reports/search_charge_separation.md --force
```

The index is a local cache under `.paperwb/` and is ignored by git. Full-text sidecars are plain `.txt` files supplied by the user, such as `projects/zis_photocatalysis/text/PAPER_ID.txt`; the tool does not parse PDFs by default.

## v0.6 Authoring Workflow

Generate local planning aids for a theme:

```bash
paperwb report evidence-matrix --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_evidence_matrix.md --force
paperwb report claim-bank --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_claim_bank.md --force
paperwb report citation-bank --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_citation_bank.md --force
paperwb report paragraph-plan --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_paragraph_plan.md --force
paperwb report subsection-readiness --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_readiness.md --force
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_writing_packet.md --force
```

See [docs/AUTHORING_WORKBENCH.md](docs/AUTHORING_WORKBENCH.md).

## Data Folder Convention

```text
data/
  papers/       # user-provided local references; no copyrighted PDFs are included
  notes/        # structured Markdown paper notes
  bibtex/       # BibTeX libraries
  registries/   # CSV paper registries
  examples/     # synthetic themes and fixtures
reports/        # generated Markdown reports
notebooks/      # lightweight workflow notebooks
docs/           # workflow documentation
projects/       # optional independent review profiles
.paperwb/       # local ignored SQLite cache when indexed search is used
```

## Registry Schema

The registry is a CSV with stable, human-readable `paper_id` values. Core fields include title, authors, year, journal, DOI, URL, local PDF path, BibTeX key, tags, reading status, notes path, dates, priority, and user comments.

See [docs/REGISTRY_SCHEMA.md](docs/REGISTRY_SCHEMA.md).

## Note Format

Notes are Markdown files with fixed headings for metadata, summaries, method notes, claims, evidence, open questions, and follow-up actions. The parser is conservative and returns warnings for incomplete notes rather than crashing.

See [docs/NOTE_FORMAT.md](docs/NOTE_FORMAT.md).

## BibTeX Audit Workflow

The BibTeX parser is lightweight and intentionally does not auto-correct entries. It reports missing fields, duplicate keys or DOIs, invalid years, inconsistent field names, unlinked entries, and registry papers without matching citation keys.

See [docs/BIBTEX_AUDIT.md](docs/BIBTEX_AUDIT.md).

## Claim and Evidence Workflow

Claims come from structured note blocks. Each claim can include evidence type, section/page location, quote or paraphrase, confidence, tags, theme support, and strength. Reports highlight weak claims and missing evidence locations before the user drafts a literature-review section.

## Report Examples

Reports are Markdown files written to `reports/` by default for the legacy `data/` workflow, or to the selected project profile's `reports/` directory when `--project` is used. Existing report and export files are not overwritten unless `--force` is provided.

- `inventory.md`
- `reading_status.md`
- `papers_by_tag.md`
- `bibtex_audit.md`
- `claims_by_theme.md`
- `evidence_map.md`
- `citation_audit.md`
- `missing_notes.md`
- `weak_claims.md`
- `theme_dashboard.md`
- `evidence_matrix.md`
- `claim_bank.md`
- `citation_bank.md`
- `paragraph_plan.md`
- `subsection_readiness.md`

## CLI Reference

```text
paperwb init
paperwb validate-registry data/registries/papers.csv
paperwb validate-bib data/bibtex/library.bib
paperwb add-paper --title "..." --year 2026
paperwb list
paperwb list --tag TAG
paperwb list --status unread
paperwb note-template PAPER_ID
paperwb claims data/notes/
paperwb search QUERY
paperwb search QUERY --indexed
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index status --project zis_photocatalysis --check-files
paperwb index clear --project zis_photocatalysis
paperwb search QUERY --claims
paperwb search QUERY --notes
paperwb report inventory
paperwb report bibtex-audit
paperwb report evidence-map
paperwb report citation-audit
paperwb report reading-status
paperwb report section-outline --theme photocorrosion
paperwb report evidence-matrix --theme photocorrosion
paperwb report claim-bank --theme photocorrosion
paperwb report citation-bank --theme photocorrosion
paperwb report paragraph-plan --theme photocorrosion
paperwb report subsection-readiness --theme photocorrosion
paperwb writing-packet --theme photocorrosion
paperwb doctor
paperwb export claims --out data/processed/claims.csv
paperwb export obsidian --project zis_photocatalysis --out exports/obsidian_zis
paperwb import zotero-csv data/examples/zotero_export.csv --dry-run
paperwb project list
paperwb synthetic generate --project stress_demo --papers 100 --claims 220
paperwb checklist --theme photocorrosion
```

## Limitations

- BibTeX parsing targets common local entries, not every BibTeX edge case.
- Markdown note parsing expects the provided template headings.
- Default search is substring-based; indexed search is opt-in and uses local SQLite with FTS5 plus substring fallback behavior.
- Theme mapping is tag-based only.
- SQLite indexing is a rebuildable cache, not an authoritative database.
- Citation audit checks completeness of user notes, not scientific correctness.

## More Documentation

- [docs/QUICKSTART_EXTERNAL_USER.md](docs/QUICKSTART_EXTERNAL_USER.md)
- [docs/EXAMPLE_LITERATURE_REVIEW_WORKFLOW.md](docs/EXAMPLE_LITERATURE_REVIEW_WORKFLOW.md)
- [docs/REPORT_GALLERY.md](docs/REPORT_GALLERY.md)
- [docs/CLI_WALKTHROUGH.md](docs/CLI_WALKTHROUGH.md)
- [docs/PROJECT_PROFILES.md](docs/PROJECT_PROFILES.md)
- [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md)
- [docs/EVIDENCE_MAPS.md](docs/EVIDENCE_MAPS.md)
- [docs/WORKFLOW_EXAMPLES.md](docs/WORKFLOW_EXAMPLES.md)
- [docs/IMPORTS.md](docs/IMPORTS.md)
- [docs/EXPORTS.md](docs/EXPORTS.md)
- [docs/ZOTERO_WORKFLOW.md](docs/ZOTERO_WORKFLOW.md)
- [docs/OBSIDIAN_EXPORT.md](docs/OBSIDIAN_EXPORT.md)
- [docs/BACKUP_BUNDLES.md](docs/BACKUP_BUNDLES.md)
- [docs/ROUND_TRIP_TESTING.md](docs/ROUND_TRIP_TESTING.md)
- [docs/LOCAL_SEARCH.md](docs/LOCAL_SEARCH.md)
- [docs/SQLITE_INDEX.md](docs/SQLITE_INDEX.md)
- [docs/FULL_TEXT_SIDECARS.md](docs/FULL_TEXT_SIDECARS.md)
- [docs/SEARCH_RANKING.md](docs/SEARCH_RANKING.md)
- [docs/INDEX_MAINTENANCE.md](docs/INDEX_MAINTENANCE.md)
- [docs/SYNTHETIC_CORPUS.md](docs/SYNTHETIC_CORPUS.md)
- [docs/STRESS_TESTING.md](docs/STRESS_TESTING.md)
- [docs/GOLDEN_REPORTS.md](docs/GOLDEN_REPORTS.md)
- [docs/REPORT_REGRESSION_TESTING.md](docs/REPORT_REGRESSION_TESTING.md)
- [docs/CLI_STRESS_WORKFLOWS.md](docs/CLI_STRESS_WORKFLOWS.md)

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for proposed extensions such as optional HTML report export, project profiles, citation-key suggestions, richer dashboards, and checklist workflows.
