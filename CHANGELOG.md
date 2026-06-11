# Changelog

All notable changes are tracked here for local release planning. This project has not been published to PyPI.

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
