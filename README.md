# paper-intelligence-workbench

`paper-intelligence-workbench` is a local-first CLI tool for small academic literature-review projects. It manages paper metadata, structured Markdown notes, user-recorded claims, evidence links, BibTeX validation, project profiles, theme coverage, and citation-audit reports without cloud services, publisher scraping, databases, or LLM APIs.

The MVP is designed for projects with roughly 10 to 100 papers where a student or researcher wants to know which papers are read, which claims are supported, which citations are incomplete, and which literature-review themes still need stronger evidence.

## What It Does

- Maintains a CSV paper registry.
- Generates structured Markdown note templates.
- Parses notes and extracts user-entered claims.
- Validates registry records and BibTeX entries.
- Maps tags to review themes.
- Searches registry rows, note bodies, and claims.
- Generates Markdown reports for inventory, reading status, BibTeX audit, evidence maps, citation audits, missing notes, and weak claims.
- Manages multiple project profiles under `projects/`.
- Runs workspace health diagnostics with `paperwb doctor`.
- Exports claims, registries, reading lists, and theme-specific claim data.

## What It Does Not Do

- It does not scrape publishers.
- It does not download or include copyrighted PDFs.
- It does not replace Zotero or CSL formatting tools.
- It does not fabricate paper metadata, quotes, claims, summaries, or conclusions.
- It does not use cloud services, LLM APIs, or embeddings.
- It does not decide whether a scientific claim is true.

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
paperwb report evidence-map --project zis_photocatalysis --force
paperwb export claims-json --project zis_photocatalysis --out data/processed/zis_claims.json --force
```

The legacy `data/` workflow remains supported.

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
paperwb search QUERY --claims
paperwb search QUERY --notes
paperwb report inventory
paperwb report bibtex-audit
paperwb report evidence-map
paperwb report citation-audit
paperwb report reading-status
paperwb report section-outline --theme photocorrosion
paperwb doctor
paperwb export claims --out data/processed/claims.csv
paperwb project list
paperwb checklist --theme photocorrosion
```

## Limitations

- BibTeX parsing targets common local entries, not every BibTeX edge case.
- Markdown note parsing expects the provided template headings.
- Search is substring-based only.
- Theme mapping is tag-based only.
- No SQLite backend is included in v0.2.
- Citation audit checks completeness of user notes, not scientific correctness.

## More Documentation

- [docs/PROJECT_PROFILES.md](docs/PROJECT_PROFILES.md)
- [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md)
- [docs/EVIDENCE_MAPS.md](docs/EVIDENCE_MAPS.md)
- [docs/WORKFLOW_EXAMPLES.md](docs/WORKFLOW_EXAMPLES.md)

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for proposed extensions such as optional HTML report export, project profiles, citation-key suggestions, richer dashboards, and checklist workflows.
