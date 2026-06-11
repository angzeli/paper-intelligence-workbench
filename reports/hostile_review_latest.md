# Hostile Maintainer Review: Latest v0.7 State

## Release Verdict

**Verdict: do not ship v0.7 broadly until the release blockers below are fixed.**

The repository is substantially useful and the local-first boundary is still intact. I found no tracked PDFs, no tracked SQLite/cache artifacts, no cloud/LLM dependencies, and no publisher scraping code. The test suite and notebook JSON validation pass, and the major CLI paths I sampled are functional.

That said, the new v0.7 local-file ingestion surface has two release-blocking defects: multi-file audit output is not atomic, and the scanner fails to detect the explicit case where the same local file path is linked to multiple registry papers. These are not cosmetic problems; they undermine the safety and reconciliation guarantees that v0.7 advertises.

Validation performed during review:

- `python -m pytest -q` passed.
- `python scripts/validate_notebooks.py` passed.
- `python -m paper_workbench.cli --help` passed.
- `python -m paper_workbench.cli files --help` passed.
- `python -m paper_workbench.cli validate-registry data/registries/example_papers.csv` passed with expected synthetic findings.
- `python -m paper_workbench.cli validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv` passed with expected synthetic findings.
- `python -m paper_workbench.cli project list` passed.
- `python -m paper_workbench.cli files scan --project zis_photocatalysis` passed.
- `python -m paper_workbench.cli files audit --project zis_photocatalysis --reports-dir /private/tmp/paperwb_review_files --force` passed.
- `python -m paper_workbench.cli import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --report /private/tmp/paperwb_review_import.md --force` passed.
- `python -m paper_workbench.cli report evidence-matrix --project zis_photocatalysis --theme charge-separation --out /private/tmp/paperwb_review_matrix.md --force` passed.
- `python -m paper_workbench.cli export report-index --out /private/tmp/paperwb_review_index.md --force` passed.
- `python -m paper_workbench.cli index rebuild --project zis_photocatalysis --include-text --index /private/tmp/paperwb_review_index.sqlite` passed and reported FTS5 availability.
- `python -m paper_workbench.cli search photocorrosion --project zis_photocatalysis --indexed --text --index /private/tmp/paperwb_review_index.sqlite` passed.
- `python -m paper_workbench.cli writing-packet --project zis_photocatalysis --theme photocorrosion --out /private/tmp/paperwb_review_packet.md --force` passed.
- `python examples/local_file_audit_workflow.py` passed.
- Tracked-file hygiene scan found no tracked `.paperwb/`, SQLite DBs, Python caches, `.DS_Store`, `.idea`, notebook checkpoints, or PDFs.

## Release Blockers

1. **`files audit` can leave partial report output after a failed overwrite check.**

   `cmd_files_audit` writes each audit report sequentially with `write_text`. If an earlier target is writable and a later target already exists, the command exits with an error after leaving the earlier generated files behind. I reproduced this by pre-creating `duplicate_files_v0_7.md`: the command returned code 2, preserved the old duplicate report, but still created `local_files_audit_v0_7.md`.

   Relevant code: `paper_workbench/cli.py` lines 506-519.

   Risk: users see a failed command but get a partially refreshed audit set. This is misleading for a data-safety report and breaks the expectation that generated reports are reproducible snapshots.

   Required fix: preflight every target path before writing any audit report, or render to temporary files and atomically move them only after all overwrite checks pass. Add a CLI regression test proving an existing later report prevents all writes unless `--force` is set.

2. **`files scan` does not detect one local file path linked to multiple registry papers.**

   `_paper_path_map` stores `relative_path -> paper_id` in a plain dict, so duplicate `local_pdf_path` values silently overwrite earlier paper IDs. A registry with `paper_a` and `paper_b` both pointing to `papers/same.pdf` produces one `linked_registry_path` record for `paper_b`, zero warnings, and zero duplicates.

   Relevant code: `paper_workbench/files.py` lines 141-147 and 193-253.

   Risk: v0.7 explicitly promises detection of the same PDF linked to multiple papers. The current scanner misses that reconciliation failure, which can lead users to believe their local-file registry is clean when it is not.

   Required fix: track `relative_path -> list[paper_id]`, preserve all linked paper IDs in diagnostics, and emit a warning such as `Local file path linked to multiple papers: papers/same.pdf -> paper_a, paper_b`. Add a unit test for duplicate registry `local_pdf_path` values.

## High-Priority Issues

1. **CI does not run any local-file CLI smoke tests.**

   `.github/workflows/ci.yml` runs pytest, notebook validation, import, CLI help, and tracked-artifact hygiene, but it does not smoke `paperwb files --help`, `files scan`, or `files audit`. v0.7's headline feature is local file ingestion; CI should exercise at least one non-destructive local-file workflow.

2. **`files scan` and `files status` hide warning details from the terminal.**

   `cmd_files_status` prints only `Warnings: N`. `cmd_files_scan` prints records but not warning text. Users must generate a full audit report to learn why a scan is suspicious.

   Relevant code: `paper_workbench/cli.py` lines 482-504.

   Risk: missing folders, large files, sidecars without matching papers, duplicate hashes, and malformed link states are too easy to miss in day-to-day CLI use.

   Fix: print warning lines after the summary for scan/status, while keeping existing output shape intact enough for tests.

3. **`files unlink PAPER_ID` can clear registry metadata even when no file-registry records were removed.**

   `unlink_file_from_paper` removes file-registry rows and then clears `local_pdf_path` for the paper if `clear_pdf` is true. If the file registry contains zero rows for that paper, the command still clears the registry field.

   Relevant code: `paper_workbench/files.py` lines 310-327 and `paper_workbench/cli.py` lines 540-552.

   Risk: users may intend to remove a file-registry link but accidentally erase a manually curated `local_pdf_path`. This is not destructive to the file itself, but it is a metadata mutation that should be more explicit.

   Fix: either clear `local_pdf_path` only when a file-registry row was removed or print a clear warning when only registry metadata changed. Preserve `--keep-pdf-path`.

4. **Forced file-registry writes can discard curated file-registry notes.**

   `files scan --write-registry --force` saves only the current scan result. If an existing `files.csv` includes curated `notes`, custom metadata, or records for temporarily unavailable files, those rows are replaced by the scan snapshot.

   Relevant code: `paper_workbench/cli.py` lines 482-488 and `paper_workbench/files.py` lines 108-137.

   Risk: this is a data-loss vector for the local file registry itself. The command is guarded by `--force`, but users may reasonably expect force to permit overwriting the output file, not to discard manually enriched rows.

   Fix: document this behavior prominently or implement merge preservation for matching `paper_id + relative_path` records. At minimum, add a test that captures the current behavior so it is not accidental.

5. **Local-file audit reports do not reconcile against existing `files.csv` records.**

   `files audit` is primarily a live scan. `files status` counts file-registry records, but the audit reports do not list stale `files.csv` rows, missing files referenced only by `files.csv`, or registry-file records whose hashes no longer match.

   Risk: users can have a stale local-file registry and still get a clean-looking scan report if the stale path is not represented in `paper.local_pdf_path`.

   Fix: include a file-registry reconciliation section in the audit, or clearly rename the reports as live-scan reports and add a separate registry reconciliation report.

## Medium-Priority Issues

1. **Top-level text-sidecar semantics are easy to misunderstand.**

   The sidecar report says only top-level `.txt` sidecars are audited, while the scanner uses recursive directory traversal and then only marks files whose parent directory name is exactly `text` as sidecars. Nested text files under `text/subdir/` are scanned as normal `.txt` files but not reported as sidecars.

   Fix: document this precisely or make sidecar detection intentionally recursive by project policy.

2. **`files audit --project ... --reports-dir ...` allows an output override unlike most project report commands.**

   This is not unsafe by itself, but it is inconsistent with the stricter project-path override checks used elsewhere. Users can accidentally generate project audit reports into the root `reports/` directory.

3. **Stale ignored review artifacts are still visible in the workspace.**

   `reports/hostile_review_v0_2.md` is ignored but still present locally. It will not be staged by normal `git add`, but users browsing the folder directly can confuse it with current review material.

4. **`reports/index.md` under-emphasizes authoring reports after v0.7.**

   The index marks v0.6 authoring reports as historical even though authoring remains a core feature. This is an information architecture problem, not a functional bug.

5. **Generated reports can include absolute roots when custom paths are used.**

   The default committed reports use relative roots, but custom audit/index reports can include absolute paths. That is acceptable for local diagnostics but should remain out of committed example reports.

## Low-Priority Polish

- `files scan` output is tabular but has no header row, making it less friendly for first-time users.
- `files sidecars` only lists sidecars; it does not show unmatched nested text files that users may have expected to count.
- `files hash` has no friendly error handling for missing paths; the raw exception is acceptable for developers but rough for external users.
- The reports directory is crowded with versioned release artifacts. This is useful historically but intimidating for new users.
- The CLI now has many report/export modes under one parser. Help text is serviceable, but examples are more important than the generated argparse output.

## Missing Tests

- Regression test for `files audit` all-or-nothing overwrite preflight.
- Unit test for duplicate registry `local_pdf_path` values pointing to the same file.
- CLI smoke test for `paperwb files --help`.
- CLI smoke test for `paperwb files scan --project zis_photocatalysis`.
- CLI smoke test for `paperwb files audit` writing all four reports.
- Test for `files unlink` behavior when zero file-registry rows are removed but `local_pdf_path` exists.
- Test documenting whether `files scan --write-registry --force` preserves or replaces curated file-registry notes.
- Test for nested `.txt` sidecar semantics.
- Audit test that existing `files.csv` records are reconciled or explicitly ignored.
- CI assertion that no tracked PDFs, text sidecar full-text fixtures, cache DBs, or notebook checkpoints are present.

## Documentation Mismatches

- `docs/TEXT_SIDECARS.md` and `docs/LOCAL_FILES.md` need sharper wording around top-level `.txt` sidecars versus recursively scanned text files.
- `docs/FILE_AUDIT.md` describes the audit as a local-file audit, but the implementation is closer to a live folder scan plus registry `local_pdf_path` check. It does not fully audit stale `files.csv` records.
- `README.md` mentions file scanning and local file audits, but it does not warn that `files scan --write-registry --force` replaces the file registry output.
- The report index does not clearly separate current user-facing reports from historical release-readiness artifacts.

## CLI Usability Problems

- `files scan` and `files status` suppress warning details.
- `files audit` can partially write outputs before failing.
- `files unlink` does not tell the user whether `local_pdf_path` metadata was cleared.
- `files scan --write-registry --force` does not warn that existing file-registry rows may be replaced.
- `files audit` has no single-report mode, so a collision on any one output currently affects a four-report command.

## Data-Safety Risks

- No tracked PDFs, no tracked full-text copyrighted sidecars, no cloud/LLM APIs, and no scraping code were found.
- The largest data-safety problem is metadata/report safety, not file deletion: `files unlink` can clear registry metadata, `files scan --write-registry --force` can replace curated `files.csv` rows, and `files audit` can leave partial report snapshots.
- Backup bundle behavior remains conservative: PDFs are not included by default.
- The SQLite index remains a rebuildable cache and is ignored locally.

## Overengineering Risks

- Local-file ingestion should stay a reconciliation layer, not a document management system. Avoid adding copying/moving/deleting workflows without very explicit safety gates.
- Optional PDF metadata should remain explicitly non-authoritative. Do not allow extracted metadata to overwrite user registry metadata silently.
- Search/indexing should remain a rebuildable local cache, not a source of truth.
- Authoring reports should remain planning aids. Do not drift into generated polished literature-review prose.

## Recommended Fix Sequence

1. Make `files audit` preflight all output paths before writing any report; add the regression test.
2. Detect duplicate registry `local_pdf_path` values pointing to the same local file; add the regression test.
3. Add `paperwb files --help`, `files scan`, and `files audit` smoke coverage to CI or pytest.
4. Print local-file warning details in `files scan` and `files status`.
5. Tighten `files unlink` semantics or at least report when registry metadata is cleared without row removal.
6. Decide whether `files scan --write-registry --force` should merge curated records or document that it replaces them.
7. Clarify top-level sidecar semantics in docs and tests.
8. Extend file audit reports to reconcile existing `files.csv` records, or rename/document the reports as live-scan reports.
9. Refresh `reports/index.md` so current authoring and v0.7 file reports are easy for external users to identify.
