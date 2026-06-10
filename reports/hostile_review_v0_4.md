# Hostile Maintainer Review v0.4

Reviewed: 2026-06-10

Scope: standalone release review of the current repository as an external-user release candidate. This review inspected package architecture, CLI behavior, project profiles, registry workflow, BibTeX workflow, note parsing, claim extraction, theme mapping, evidence maps, citation audits, import/export workflows, search, tests, docs, notebooks, generated reports, synthetic data, backward compatibility, and data safety.

Validation performed during review:

- `python -m pytest -q`: 69 passed.
- `python scripts/validate_notebooks.py`: validated 5 notebooks.
- `python -m paper_workbench.cli --help`: CLI help rendered.
- Checked tracked files for common cache artifacts with `git ls-files | rg '(__pycache__|\.pyc$|\.DS_Store|\.pytest_cache|\.ipynb_checkpoints|\.idea)'`; none found.
- Ran targeted probes against imports, bundle export, report index, and inventory report behavior using temporary paths under `/private/tmp`.

## Release Verdict

Do not release v0.4 to external users yet.

The project is broadly coherent and the test suite passes, but the v0.4 import/export layer has at least one release-blocking data-safety bug: an import can write the registry and then fail when writing the import report. That violates the repository's non-destructive workflow promise and creates a bad failure mode for the exact feature v0.4 introduces.

There are also high-priority issues in backup/export semantics and report correctness. These are fixable with a small patch set, but they should be fixed before presenting v0.4 as external-user-ready.

## Release-Blocking Issues

### 1. Imports mutate the registry before confirming the import report can be written

Severity: release blocker

Area: CLI import workflow, data safety

Evidence:

- `paper_workbench/cli.py` saves the registry before writing the import report in `_finish_import`.
- Review probe created an existing `reports/import_zotero_csv.md`, then ran:

```bash
python -m paper_workbench.cli import zotero-csv data/examples/zotero_export.csv --registry /private/tmp/paperwb_review_import/registry.csv --reports-dir /private/tmp/paperwb_review_import/reports
```

Observed behavior:

- CLI printed that it wrote the registry.
- CLI then failed with `error: /private/tmp/paperwb_review_import/reports/import_zotero_csv.md already exists`.
- The registry file existed and contained imported rows.
- The import report remained the previous file content.

Impact:

- A user can receive a non-zero failed import command while the registry has already changed.
- The report that would explain what was imported is not written.
- This breaks dry-run-first/data-safety expectations and makes recovery harder.

Required fix:

- Preflight all output paths before mutating the registry, including the default import report path.
- Prefer writing report and registry to temporary files, then atomically replacing final paths after all writes succeed.
- Add regression tests for report-path collision and default report-path collision for every importer family, at least through a shared import CLI path.

## High-Priority Issues

### 1. Backup bundles and Obsidian vault exports can silently retain stale files under `--force`

Severity: high

Area: export workflows, backup integrity

Evidence:

- `paper_workbench/exports.py` uses `_ensure_export_dir`, which allows writing into an existing non-empty directory when `force=True`.
- `export_bundle` copies current files into that directory and writes a new manifest, but it does not remove stale files.
- Review probe created stale files in the target bundle directory, ran `paperwb export bundle --force`, and observed the stale files still present while `manifest.json` did not include them.

Impact:

- A backup bundle can contain files from previous exports that are not listed in the manifest.
- Users may treat the bundle as authoritative while it contains stale or unrelated content.
- Obsidian vault export has the same directory reuse pattern and can leave old paper pages or indexes behind.

Required fix:

- For directory exports, either refuse non-empty targets even with `--force`, or write to a fresh temporary directory and replace the target.
- If merge behavior is intentionally supported, the manifest and docs must call it a merge, not a clean export.
- Add tests proving stale files are not retained, or that the command fails before writing.

### 2. Generated report index has misleading links and hardcoded absolute path content

Severity: high

Area: report exports, docs usability

Evidence:

- `reports/report_index_v0_4.md` says it indexes `/Users/liangze/Desktop/paper-intelligence-workbench/projects/zis_photocatalysis/reports`.
- The file itself lives under root `reports/`.
- Its links are simple relative links like `bibtex_audit.md`, which resolve relative to root `reports/`, not the indexed project reports directory.
- `paper_workbench/exports.py` renders `Reports directory: {root}` with the path supplied to `report_index_markdown`, so generated reports can include hardcoded absolute local paths.

Impact:

- External users opening the root report index will follow links to the wrong directory.
- The generated report includes machine-specific absolute paths, undermining portability and snapshot stability.

Required fix:

- Write the report index into the reports directory it indexes, or render links relative to the output file.
- Avoid hardcoded absolute paths in committed generated reports unless explicitly requested.
- Add a regression test that validates report-index links from the index file location.

### 3. Inventory report underreports registry validation findings

Severity: high

Area: report correctness

Evidence:

- `paper_workbench/reporting.py` calls `validate_registry(papers)` inside `inventory_report`.
- `validate_registry` only checks `notes_path_missing_file`, `missing_local_pdf_path`, and `included_without_claims` when workspace root and/or claims are passed.
- `cmd_report` already has `paths` and parsed claims, but does not pass them to `inventory_report`.
- Review probe generated an inventory report for `zis_photocatalysis`; the report said `No findings` while richer workspace validation can report path and evidence completeness warnings.

Impact:

- The inventory report gives users a false sense that registry data is clean.
- This is especially problematic because external users will treat reports as audit artifacts before writing literature reviews.

Required fix:

- Let `inventory_report` accept optional `root` and `claims`, or pass precomputed validation findings from CLI.
- Add a test showing inventory includes path-sensitive and claim-sensitive registry findings when run through project mode.

### 4. BibTeX import source-type mapping is inconsistent with BibTeX validation support

Severity: high

Area: BibTeX import workflow

Evidence:

- BibTeX validation supports common entry types including `inproceedings`, `phdthesis`, `mastersthesis`, `misc`, and others.
- `import_bibtex` maps `entry.entry_type` through `_source_type`.
- `SOURCE_TYPE_BY_LABEL` contains `conference paper`, `conference_paper`, and `conference`, but not `inproceedings`.
- As a result, an `@inproceedings` entry imports as `source_type=other` with an unsupported item type warning instead of `conference_paper`.

Impact:

- BibTeX import degrades valid metadata into `other`.
- The importer appears noisier and less trustworthy than the validator for common real-world BibTeX files.

Required fix:

- Add explicit mappings for common BibTeX entry labels: `inproceedings`, `proceedings`, `phdthesis`, `mastersthesis`, `unpublished`, and possibly `manual`/`techreport` where supported.
- Add tests for those mappings.

### 5. Import report collisions are too easy and the default error arrives too late

Severity: high

Area: CLI usability, data safety

Evidence:

- Import reports default to `reports/import_<type>.md`.
- Docs tell users reports are written by default.
- If that default report exists and `--force` is omitted, the command can fail after registry mutation, as described in the release blocker.

Impact:

- Re-running the same import command is a common external-user workflow.
- The current behavior is both surprising and unsafe.

Required fix:

- Preflight the default report path.
- In dry-run mode, consider printing the report to stdout when no explicit report is supplied, or use a timestamped/path-safe default.
- Make the error message state that no registry changes were made after the fix.

## Medium-Priority Issues

### 1. Obsidian export paper filenames can collide

`export_obsidian_vault` writes paper pages as `papers/{_safe_name(paper.paper_id)}.md`. Two distinct paper IDs can sanitize to the same filename, causing overwrite or forced collision behavior. Add collision detection and tests.

### 2. Backup bundle manifest is not strong enough for release-grade backup semantics

The bundle manifest records copied paths but not file sizes, checksums, skipped missing files, or stale files found in the target. If this is presented as a backup, users need clearer integrity signals.

### 3. `--include-pdfs` is correctly opt-in, but the CLI output should be louder

The default excludes PDFs, which is correct. When users explicitly include PDFs, the command should print an explicit warning that only local files the user has rights to copy should be included and should report missing PDF paths.

### 4. Import reports can contain absolute local paths

`import_report` prints `source_path` and `registry_path` exactly as supplied. That is acceptable for local-only ad hoc reports, but committed/generated release examples should avoid absolute paths or normalize them for portability.

### 5. RIS parser limitations are acceptable but under-signaled in CLI output

The RIS parser intentionally handles common tags only and ignores lines it cannot parse. The docs mention limitations, but CLI output does not remind users that RIS import is conservative and should be reviewed.

### 6. Note parsing is still fragile around duplicate headings and label variants

The parser is conservative by design, which is fine. The risk is that users may interpret missing parsed claims as absence of claims rather than parser mismatch. Reports should surface note parsing warnings more prominently.

### 7. Claims collection appears flat-file oriented

The common project notes directories are flat, but future users may organize notes in subdirectories. If recursive notes are not supported, docs should say so. If they are intended to be supported, tests should cover it.

### 8. Root reports directory contains many stale versioned reports

The repository has historical v0.1-v0.4 reports. That is useful for development history but confusing for external users. A release distribution should have an index that clearly distinguishes current reports from archived reports.

## Low-Priority Polish

- Add `paperwb --version`.
- Remove unused imports in modules such as `paper_workbench/importers.py` when touching the file for fixes.
- Consider a machine-readable import report JSON alongside Markdown.
- Add a short "safe retry" paragraph to import docs after the atomic-write fix.
- Make generated report dates optional or normalized where snapshot stability matters.
- Make CLI success output more consistent about exactly which registry, report, and project were used.

## Missing Tests

Required before release:

- Import command does not mutate registry when the import report path already exists.
- Import command does not mutate registry when the default import report path already exists.
- Dry-run import with report collision has no side effects.
- Bundle export with `--force` does not leave stale files, or refuses the non-empty output directory.
- Obsidian export with `--force` does not leave stale paper files, or refuses the non-empty output directory.
- Report index links resolve correctly from the generated index path.
- Inventory report includes root-sensitive `notes_path_missing_file` and `missing_local_pdf_path` warnings.
- Inventory report includes `included_without_claims` when claim context is available.
- BibTeX import maps `inproceedings` to `conference_paper`.
- BibTeX import maps thesis entry types to `thesis`.
- Obsidian export detects sanitized filename collisions.
- Backup bundle manifest test asserts no untracked stale files exist in the bundle.
- CLI smoke test for repeated import commands without `--force`.
- CLI smoke test for `export bundle --include-pdfs` with missing and existing synthetic local files.

Useful but not release-blocking:

- Recursive note-directory behavior, whichever behavior is intended.
- RIS continuation-line fixture.
- Import report path normalization.
- Report-index behavior when reports directory is empty.

## Documentation Mismatches

- `reports/release_readiness_v0_4.md` says imports preserve existing registry rows and emphasizes data safety, but does not mention that import can write the registry before failing to write the report.
- `docs/CLI_REFERENCE.md` says export commands refuse to overwrite existing output files unless `--force`; for directory exports, `--force` currently merges into existing directories and can leave stale files.
- `docs/EXPORTS.md` presents `export obsidian --force` and `export bundle --force` as straightforward workflows without warning that the target directory is not cleaned.
- `reports/report_index_v0_4.md` is itself misleading because it indexes a project reports directory while living in the root reports directory with links that resolve incorrectly.
- Release/readiness docs say v0.4 is usable for local exchange workflows. That should be weakened until atomic import writes and clean directory exports are fixed.

## CLI Usability Problems

- Import failure after registry write is the main CLI flaw. The user sees a failure, but the workspace has changed.
- Re-running an import command defaults to a colliding report path; this is too common to be a sharp edge.
- `export bundle --force` does not communicate whether it replaced, merged, or left existing files alone.
- `export report-index` does not make clear whether links are relative to the indexed reports directory or the output file.
- Project import commands reject path overrides, which is good, but the error messages should include the resolved project paths when a command succeeds.

## Data-Safety Risks

- Non-atomic imports can partially apply changes.
- Directory exports can leave stale files that users mistake for current backup/export contents.
- Generated committed reports can expose absolute local paths.
- `--include-pdfs` is opt-in, but should remain heavily guarded and tested.
- Importers correctly avoid overwriting non-empty fields by default, but that guarantee is undermined if command-level output handling fails after mutation.

No evidence found of cloud APIs, LLM API usage, publisher scraping, copyrighted PDFs, tracked Python cache files, or tracked IDE cache files.

## Recommended Fix Sequence

1. Fix `_finish_import` to preflight report output and make registry/report writes atomic enough that report-write failure cannot mutate the registry.
2. Add import collision regression tests and CLI smoke tests for repeated imports.
3. Fix directory export semantics for bundle and Obsidian vault exports: clean temporary replacement or refuse non-empty directories.
4. Add stale-file regression tests for bundle and Obsidian exports.
5. Fix report index path/link generation and regenerate `reports/report_index_v0_4.md`.
6. Fix inventory report validation plumbing so project reports include root-sensitive and claim-sensitive findings.
7. Add missing BibTeX entry-type mappings for import and tests.
8. Update only the inaccurate docs and release-readiness language after behavior is fixed.
9. Regenerate affected reports.
10. Run full pytest, notebook validation, and representative import/export CLI smoke tests before cutting the release.

