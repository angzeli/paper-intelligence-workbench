# Final Project Handoff: Paper Intelligence Workbench

Date: 2026-06-11
Stage: v1.1 post-review handoff

## Project Purpose

Paper Intelligence Workbench is a local-first command-line workbench for small academic literature-review projects. It helps a researcher manage paper metadata, structured reading notes, user-entered claims, evidence locations, BibTeX entries, themes, reports, authoring aids, local file references, backups, and workspace audits without cloud services, LLM APIs, publisher scraping, or copyrighted example documents.

The project is best understood as a local evidence-completeness and literature-review preparation system. It does not decide whether a scientific claim is true.

## Actual Use Case

The practical use case is a student or researcher managing roughly 10 to 100 papers for a literature-review chapter or subsection. The tool helps answer:

- Which papers are in the project, and which have been read?
- Which papers have structured notes?
- Which user-entered claims are supported by which notes and evidence locations?
- Which claims are weak, missing page/section evidence, or supported only by review statements?
- Which BibTeX records are incomplete or unlinked?
- Which themes are ready for writing, and which need more evidence?
- Which reports, citation banks, or writing packets can support a literature-review outline?

For first real use, start with one bounded review topic, one project profile, 20 to 40 papers, and only user-owned notes and bibliography records.

## Current Architecture

The package is a standard-library-heavy Python CLI with zero runtime dependencies declared in `pyproject.toml`. The stable user interface is `paperwb`; documented local file formats are the other stable interface.

Core modules:

- `paper_workbench.schema`: dataclasses and controlled vocabularies.
- `paper_workbench.registry`: CSV registry load/save, normalization, validation, filtering, and paper append.
- `paper_workbench.bibtex`: lightweight BibTeX parser and validator.
- `paper_workbench.notes`: structured Markdown note template generation and conservative note parsing.
- `paper_workbench.claims`: claim collection and CSV export.
- `paper_workbench.tags`: tag normalization and theme mapping.
- `paper_workbench.reporting`: Markdown report generation helpers.
- `paper_workbench.audit`: citation-readiness checks.
- `paper_workbench.authoring`: evidence matrices, claim banks, citation banks, paragraph plans, readiness scoring, and writing packets.
- `paper_workbench.projects`: project-profile path resolution under `projects/`.
- `paper_workbench.importers`: Zotero-style CSV, generic CSV, BibTeX, and RIS import workflows.
- `paper_workbench.exports`: registry, claims, reading-list, Obsidian-style, bundle, project summary, and report-index exports.
- `paper_workbench.index`: local SQLite search cache and indexed search.
- `paper_workbench.files`: local file registry, hashes, sidecars, missing-file and duplicate-file audits.
- `paper_workbench.integrity`: workspace and project consistency checks.
- `paper_workbench.backups`: local backup snapshots and restore planning.
- `paper_workbench.migration`: non-destructive legacy `data/` to project-profile migration planning/copying.
- `paper_workbench.auditlog`: ignored local JSONL audit log.
- `paper_workbench.synthetic`: deterministic synthetic stress project generation.
- `paper_workbench.drafts`: Markdown draft parsing, citation extraction, paragraph evidence matching, and revision checklist reports.
- `paper_workbench.errors` and `paper_workbench.safety`: diagnostic formatting and tracked-file data-safety checks.
- `paper_workbench.cli`: argparse command surface. It is large and should be refactored only after release blockers are cleared.

Authoritative user data remains local CSV, Markdown, BibTeX, RIS, JSON, and optional user-provided text sidecars. SQLite indexes, audit logs, reports, and backups are local derived or safety artifacts.

## Implemented Features By Version

- v0.1: MVP package, registry workflow, BibTeX validation, note templates, claim extraction, reports, synthetic examples, tests, docs, and release-readiness report.
- v0.2: project profiles, stronger registry/BibTeX/note validation, workspace doctor, evidence maps, section outlines, export basics, and richer docs.
- v0.3: synthetic stress corpus generator, stress projects, golden report regression checks, parser edge fixtures, CLI stress tests, performance sanity reporting, and stress docs.
- v0.4: interoperability workflows for Zotero-style CSV, generic CSV mappings, BibTeX import, RIS import, Obsidian-style export, bundle export, reading-list exports, and round-trip tests.
- v0.5: project-aware local SQLite search index, optional FTS5 use with fallback behavior, text sidecar indexing, stale-index diagnostics, search reports, and indexed workflow docs.
- v0.6: authoring workbench with evidence matrix, claim bank, citation bank, paragraph planner, subsection readiness score, and writing packet. These are planning aids only.
- v0.7: local file scanner, file registry, SHA256 hashing, file link/unlink, duplicate/missing file reports, sidecar audits, and local-file workflow docs.
- v0.8: packaging hardening, CI workflow, documentation-site-style Markdown pages, smoke scripts, notebook validation, data-safety audit, test/report/data-safety matrices, and external-user onboarding.
- v0.9: workspace integrity model, audit log, backup snapshots, restore planning, non-destructive legacy migration workflow, safe-write documentation, and migration/safety simulation.
- v0.10: adversarial fixture library, error taxonomy, malformed data tests, CLI failure-path coverage, warning snapshots, and recovery docs.
- v1.0-rc: API and CLI surface inventories, command-contract docs/tests, clean-room/current-environment release checks, release report index, external-user simulation, data-safety report, and final release-readiness reports.
- v1.1: draft citation auditor and manuscript evidence checker for local Markdown drafts, plus targeted post-review fixes for report-all write safety, v1.1 surface docs, local-file rollback, and draft citation ordering.

## CLI Command Map

Top-level commands:

- `paperwb init`: create local workbench folders.
- `paperwb project init/list/validate`: manage project profiles.
- `paperwb validate-registry`: validate paper registry CSV and optionally export JSON.
- `paperwb validate-bib`: validate local BibTeX and registry linkage.
- `paperwb import zotero-csv/csv/bibtex/ris`: import local bibliography sources.
- `paperwb add-paper`: append one manual paper row.
- `paperwb list`: list and filter registry rows.
- `paperwb note-template`: create a structured Markdown note template.
- `paperwb claims`: extract user-entered claims from structured notes.
- `paperwb search`: run substring search or indexed search with `--indexed`.
- `paperwb index rebuild/status/clear`: manage local SQLite search cache.
- `paperwb files scan/status/link/unlink/audit/hash/sidecars`: inspect and reconcile local user-provided files.
- `paperwb report ...`: generate inventory, reading-status, tag, BibTeX, claims, evidence, citation, missing-notes, weak-claims, dashboard, workspace-health, section-outline, and authoring reports.
- `paperwb writing-packet`: generate a combined theme-specific writing planning packet.
- `paperwb checklist`: generate a theme review checklist.
- `paperwb draft parse/citations/audit/checklist/evidence-matrix`: audit Markdown drafts against local citation keys and tracked evidence without rewriting prose.
- `paperwb doctor`: run workspace health diagnostics.
- `paperwb integrity check`: run read-only workspace integrity checks.
- `paperwb audit-log show/clear`: inspect or explicitly clear ignored local audit logs.
- `paperwb backup create/list/inspect/plan-restore/restore`: create and inspect local snapshots; restore defaults to dry-run unless forced.
- `paperwb migrate plan/run`: plan or copy legacy `data/` workflow into a project profile.
- `paperwb export ...`: export claims, registry JSON, reading lists, Obsidian vaults, bundles, project summaries, and report indexes.
- `paperwb synthetic generate`: generate deterministic synthetic stress projects.

Important current CLI caveat: `paperwb report all` now preflights all output paths before writing and rejects `--out`; use `--reports-dir` for multi-report output. `paperwb audit-log clear` without `--force` now returns a clean user-facing error.

## Data Model Summary

Primary dataclasses in `paper_workbench.schema`:

- `Paper`: registry row with metadata, DOI, local file path, BibTeX key, tags, reading status, notes path, project fields, review inclusion fields, and user comment.
- `Author`: parsed/display forms for author names.
- `BibTeXEntry`: parsed BibTeX entry, raw fields, source path, and parse warnings.
- `PaperNote`: structured note fields, tags, claims, questions, follow-ups, warnings, and source path.
- `Claim`: user-entered claim, paper link, evidence type, section/page, confidence, tags, quote/paraphrase, theme, strength, and note file.
- `EvidenceLink`: claim-to-paper evidence pointer.
- `Tag` and `ProjectTheme`: tag descriptions and theme definitions with minimum coverage expectations.
- `ProjectProfile`: local project root and paths for registry, BibTeX, notes, themes, and reports.
- `LocalFileRecord`: local file path, type, size, hash, linked status, sidecar path, and metadata status.
- `CitationAuditFinding` and `ValidationFinding`: structured validation/audit diagnostics.

Controlled vocabularies include reading status, claim strength, evidence type, and source type.

## Report Types

Core literature-review reports:

- Inventory
- Reading status
- Papers by tag
- BibTeX audit
- Claims by theme
- Evidence map
- Citation audit
- Missing notes
- Weak claims
- Theme dashboard
- Missing evidence
- Workspace health
- Section outline

Authoring reports:

- Evidence matrix
- Claim bank
- Citation bank
- Paragraph plan
- Subsection readiness
- Writing packet
- Theme checklist

Interoperability and safety reports:

- Import reports
- Obsidian export summary
- Bundle export summary
- Search result report
- Index status report
- Local files audit
- Duplicate files
- Missing files
- Text sidecars
- Workspace integrity
- Backup manifest
- Restore dry-run
- Migration plan
- Audit log demo
- Data-safety audit

Release and quality reports:

- Stress reports
- Performance sanity
- Golden report references
- Adversarial test summary
- Error taxonomy
- Failure-mode matrix
- Release readiness reports
- Hostile maintainer reviews
- External-user simulations
- Report indexes

## Test Suite Summary

The current test collection reports 167 tests across:

- registry validation and duplicate detection;
- BibTeX parser and validation behavior;
- structured note parsing and claim extraction;
- tag/theme/search/report/citation audit behavior;
- project profiles, doctor, and export workflows;
- v0.2 validation hardening;
- synthetic stress generation and CLI stress commands;
- golden report regression checks;
- parser edge fixtures;
- v0.4 import/export workflows;
- v0.5 indexed search;
- v0.6 authoring workbench;
- v0.7 local file workflows;
- v0.8 release engineering and hygiene;
- v0.9 integrity, backup, migration, and audit-log workflows;
- v0.10 adversarial data and failure-path coverage;
- v1.0-rc command-contract coverage;
- v1.1 draft audit, report-all write safety, report-index, and post-review regression coverage.

Release scripts include:

- `scripts/smoke_cli_workflow.py`
- `scripts/check_notebooks.py`
- `scripts/validate_notebooks.py`
- `scripts/data_safety_audit.py`
- `scripts/clean_room_install_check.py`
- `scripts/performance_sanity.py`

CI runs Python 3.10, 3.11, and 3.12, installs `.[dev]`, runs tests, notebook checks, CLI smoke tests, build, local-file smoke checks, data-safety audit, and tracked artifact hygiene.

## Known Limitations

- The latest hostile review should be read as the pre-fix risk register; the targeted post-review pass fixed its release-blocking and high-priority findings except for broader architectural polish.
- Package build now succeeds after installing declared development extras, but setuptools emits license metadata deprecation warnings that should be cleaned up before the 2027 deadline.
- BibTeX parsing is intentionally lightweight and does not implement a full BibTeX macro engine.
- Markdown note parsing is conservative and template-oriented.
- Markdown draft parsing is conservative and does not fully handle complex tables, footnotes, comments, or every citation processor syntax.
- Indexed search is lexical/local and can become stale until rebuilt.
- Authoring readiness scores measure local evidence-tracking completeness, not truth.
- The tool does not parse full PDF text by default and does not perform OCR.
- Historical reports contain warning-class absolute-path findings.
- The documentation set has overlap between older uppercase reference pages and docs-site-style lowercase pages.

## What Should Not Be Expanded Further

Do not add these before the release blocker and high-priority safety issues are fixed:

- New authoring features.
- LLM-generated summaries, prose, citations, claims, or quote extraction.
- Publisher scraping, metadata lookup, PDF downloading, or OCR.
- Cloud sync or hosted web app behavior.
- Heavy database migrations that replace CSV/Markdown/BibTeX as authoritative files.
- More broad import/export formats unless a real user need is validated.
- More report types unless existing report semantics are made cleaner and less overlapping.
- A broad stable Python API beyond the documented file formats and small stable helper set.

## Recommended Maintenance Workflow

For any change:

1. Start with `git status --short --branch --ignored=matching`.
2. Read `AGENTS.md`.
3. Keep changes scoped and non-destructive.
4. Add or update tests for parser, validator, importer, exporter, report, write-path, and CLI behavior changes.
5. Run `python -m pytest -q`.
6. Run representative CLI smoke checks, at minimum `paperwb --help` and the command area touched.
7. Run notebook and data-safety checks before release-candidate changes.
8. Do not commit `.paperwb/`, caches, backup archives, exports, scratch outputs, real PDFs, or copyrighted full text.
9. Update docs only where behavior actually changed.
10. Regenerate affected reports after changes that alter output.
11. Run a hostile maintainer review before any public release tag.

For release work:

1. Fix the latest hostile-review release blocker first.
2. Fix high-priority write-path and docs safety issues.
3. Run the full CI matrix.
4. Run a true fresh virtual-environment install outside the development checkout.
5. Run the external-user simulation using only README/docs commands.
6. Confirm no push, tag, or publication happens until explicitly approved.

## Recommended First Real Use Case

Use a single project profile for a small, bounded literature-review subsection:

- Project: one topic such as photocorrosion mechanisms in a specific material family.
- Size: 20 to 40 papers.
- Inputs: user-created registry CSV, user-owned BibTeX export, and manually written structured notes.
- Workflow: initialize project, import or add papers, validate registry/BibTeX, create note templates, enter claims with evidence locations, generate evidence map and citation audit, then generate a writing packet.
- Safety: run `integrity check` and `backup create` before bulk edits or migration.

Avoid using the full stress corpus workflow as a first user workflow; it is for maintainers and regression testing.

## v1.0 Release Readiness Verdict

**Not ready to tag v1.0.0 yet.**

The codebase is feature-complete enough for a serious local release candidate, but the latest hostile review identifies one release blocker and several high-priority safety/usability issues. Treat the v1.0-rc cycle as successful from a scope and architecture standpoint, but not as final-release-ready until:

- `audit-log clear` no-force behavior returns a clean user-facing error;
- `report all` preflights output paths and handles `--out` explicitly;
- docs examples stop encouraging writes to tracked report files;
- local file link/unlink partial-write behavior has regression coverage;
- build and install checks are verified in CI or a true clean environment;
- affected release-readiness and data-safety reports are regenerated.

## Future Roadmap

Useful next work is mostly maintenance:

- v1.0.0: release-blocker and high-priority safety fixes only.
- v1.0.x: bug fixes, parser warning improvements, report clarity, import preview quality.
- v1.1: optional local HTML report export or report diff tooling if real users ask for it.
- Longer term: keep the project local-first and resist cloud, scraping, and LLM expansion.
