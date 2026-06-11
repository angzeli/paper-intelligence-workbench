# Changelog

All notable changes are tracked here for local release planning. This project has not been published to PyPI.

## v1.7.0 - Project Templates and Dogfooding

- Added `paperwb template list/inspect/create` for reusable project scaffolds.
- Added photocatalysis, finance/valuation, ML methods, and generic literature-review templates.
- Generated empty project structures with themes, rules, note templates, report checklists, manuscript QA checklists, reading queue config, and dashboard expectations.
- Kept templates synthetic, local-only, non-destructive, and free of real paper metadata, investment advice, and copyrighted content.

## v1.6.0 - Terminal Dashboard

- Added `paperwb dashboard` for dependency-free terminal summaries of project health, evidence gaps, reading queues, follow-ups, rule findings, manuscript QA warnings, and recent audit events.
- Added Markdown dashboard, next-action, and project-health summary exports.
- Added explainable next-action generation without automatically running commands or modifying user data.
- Kept the dashboard local-only and read-only except for explicit `--out` report writes.

## v1.5.0 - Local Rule Engine

- Added `paperwb rules` commands for listing, validating, running, reporting, and explaining local declarative validation rules.
- Added safe JSON rule configs for project-specific registry, claim, theme, and manuscript checks.
- Added built-in rule adapters for registry validation, citation audits, evidence-map readiness, manuscript QA, and workspace health findings.
- Kept rule execution local and declarative: no arbitrary Python execution, no cloud APIs, no LLM APIs, and no user-data mutation.

## v1.4.0 - Manuscript Citation QA

- Added `paperwb manuscript` commands for parsing, citation coverage, reviewer-style QA, revision checklists, citation context tables, paragraph evidence tables, and claim-to-draft traceability.
- Added synthetic manuscript drafts covering good support, unknown citations, overconfident wording, review-only support, and claim mismatch cases.
- Kept manuscript workflows audit-only: no final-prose rewriting, no fabricated citations, no fabricated claims, and no scientific truth judgment.

## v1.3.0 - Sync Planning and Conflict Resolution

- Added local `paperwb sync` planning for Zotero-style CSV, generic CSV, BibTeX, and RIS sources.
- Added JSON sync plans, conflict reports, dry-run apply reports, and safe registry applies for creates and blank-field fills.
- Added conservative note and Obsidian vault round-trip conflict detection without auto-merging user notes.
- Kept sync local-first: no cloud APIs, no scraping, no silent overwrites, and forced applies create backups by default.

## v1.2.0 - Reading Session Workflow

- Added local reading queue generation based on registry priority, reading status, notes, claims, and theme gaps.
- Added `paperwb reading start/finish/status/review` for local session logs, safe note-template integration, status updates, and weekly reading reviews.
- Added `paperwb followups list/export/done` for note and session follow-up actions without editing source notes.
- Added v1.2 reading workflow docs, tests, synthetic session fixture, reports, and release-readiness planning.

## v1.1.0 - Draft Citation Auditor

- Added Markdown draft parsing and citation-key extraction.
- Added draft citation coverage, paragraph evidence matching, revision checklist, and paragraph evidence matrix reports.
- Kept draft workflows audit-only: no citation fabrication, claim fabrication, or final-prose rewriting.

## v1.0-rc - Release Candidate Hardening

- Added API and CLI surface inventories that mark stable, experimental, and internal surfaces.
- Added command-contract documentation and release-candidate tests for help output, safe writes, dry-run imports, and common failure paths.
- Added a local current-environment release check script that exercises package import, CLI help, temporary workspace initialization, project creation, validation, reports, indexed search, integrity checks, and notebook structure checks.
- Added v1.0-rc release reports for current-environment checks, external-user simulation, data safety, limitations, release notes, and post-v1.0 roadmap planning.
- Kept the release candidate local-first, unpublished, untagged, and free of cloud, LLM, scraping, or copyrighted example content.

## v0.10.0 - Adversarial Testing

- Added adversarial synthetic fixtures for malformed registries, BibTeX, notes, imports, projects, backups, audit logs, sidecars, and local paths.
- Added error taxonomy and error-message guidance.
- Hardened CLI failure paths so normal bad inputs produce actionable errors without Python tracebacks.
- Added v0.10 release-readiness, failure-mode, and adversarial summary reports.

## v0.9.0 - Data Integrity

- Added workspace integrity checks, local audit logs, backup snapshots, non-destructive restore planning, and migration planning.
- Added safe-write documentation and workflow examples.
- Added v0.9 release-readiness, migration, backup, restore, and audit-log reports.

## v0.8.0 - External Release Engineering

- Hardened package metadata and aligned package version metadata.
- Added release-oriented CLI smoke workflow, notebook checker, and data-safety audit scripts.
- Added documentation-site source pages and external-user onboarding docs.
- Added test, CLI behavior, report, and data-safety matrices.
- Added v0.8 release notes, release-readiness report, external-user simulation report, and v0.9 patch plan.
- Kept runtime dependencies at zero and all workflows local-first.

## v0.7.0 - Local Document Ingestion

- Added local file scanning, hashing, file registry CSVs, linking, unlinking, and local-file audit reports.
- Added text-sidecar discovery and local-file safety documentation.
- Hardened file audits to avoid partial report writes and to reconcile existing `files.csv` records.

## v0.6.0 - Authoring Workbench

- Added evidence matrices, claim banks, citation banks, paragraph plans, subsection readiness reports, and writing packets.
- Kept generated writing artifacts as planning aids only, not final literature-review prose.

## v0.5.0 - Local Search Index

- Added a rebuildable local SQLite index with FTS5 when available and a fallback search path.
- Added indexed search reports, sidecar indexing, and index diagnostics.

## v0.4.0 - Import / Export Interoperability

- Added local importers for Zotero-style CSV, generic CSV mappings, BibTeX, and RIS.
- Added Obsidian vault export, backup bundles, reading-list exports, and report indexes.

## v0.3.0 - Stress Corpus and Regression Checks

- Added deterministic synthetic stress projects, parser edge fixtures, golden report checks, and performance sanity reporting.

## v0.2.0 - Project Profiles and Report Hardening

- Added project profiles, stronger registry/BibTeX validation, richer evidence maps, citation audits, exports, and external-user docs.

## v0.1.0 - MVP

- Added the initial local-first registry, BibTeX validation, note parsing, claim extraction, reports, CLI, examples, tests, and documentation.
