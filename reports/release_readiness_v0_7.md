# Release Readiness v0.7

## Summary

v0.7 adds local document ingestion and metadata reconciliation. The release remains local-first and does not download, scrape, OCR, use cloud APIs, use LLM APIs, or include copyrighted PDFs.

## Features Added

- Local file scanner for `pdf`, `txt`, `md`, `bib`, `ris`, and `csv` files.
- Local file registry CSV with paper ID, file ID, relative path, file type, size, SHA256, sidecar path, and advisory metadata status.
- `paperwb files` command group for scan, status, link, unlink, audit, hash, and sidecar workflows.
- Non-destructive file linking that stores relative paths where possible.
- File-registry writes that merge fresh scan output with existing `files.csv` rows so curated notes are preserved.
- Duplicate-file detection by SHA256.
- Duplicate registry `local_pdf_path` detection when multiple papers point to the same local file.
- Missing `local_pdf_path` detection.
- File audit reconciliation against existing `files.csv` records, including missing files, records outside scan folders, and hash mismatches.
- Text sidecar audit and search/index compatibility through the existing `index rebuild --include-text` workflow.
- PDF metadata boundary documentation. v0.7 does not parse PDF text or treat extracted metadata as authoritative.

## Reports Generated

- `reports/local_files_audit_v0_7.md`
- `reports/duplicate_files_v0_7.md`
- `reports/missing_files_v0_7.md`
- `reports/text_sidecars_v0_7.md`

## Validation Performed

- Added focused tests for scanning, hashing, duplicates, duplicate registry file paths, missing files, file registry save/load, file-registry merge preservation, file-registry reconciliation, audit-output preflight, safer unlinking, sidecar discovery, CLI smoke paths, and tracked-PDF policy.
- `python -m pytest -q` passed.
- `python scripts/validate_notebooks.py` passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"` returned `0.7.0`.
- `python -m paper_workbench.cli --help` passed.
- `python -m paper_workbench.cli files --help` passed.
- `paperwb files scan`, `files status`, `files sidecars`, `files audit`, and `files hash` smoke paths passed on synthetic fixtures.
- `python examples/local_file_audit_workflow.py` passed.
- Tracked PDF scan found no tracked PDFs.
- Tracked cache scan found no tracked `.paperwb`, SQLite, Python cache, `.DS_Store`, `.pytest_cache`, notebook checkpoint, or `.idea` artifacts.

## Data Safety Assessment

- File commands do not delete user files.
- File commands do not copy files unless a future explicit copy option is added.
- `files scan` is read-only unless `--write-registry` is supplied.
- `files scan --write-registry` merges with existing `files.csv` records instead of replacing curated rows wholesale.
- `files audit` preflights all report output paths before writing any report, avoiding partial audit snapshots on overwrite errors.
- `files unlink` clears `local_pdf_path` only when at least one matching file-registry row was removed.
- PDF links refuse to replace an existing registry `local_pdf_path` unless `--force` is supplied.
- `.gitignore` ignores `*.pdf`.
- Examples and tests use synthetic text and temporary placeholder files only.

## Known Limitations

- PDF metadata extraction is not implemented.
- The scanner audits file organization, not whether a file is scientifically correct.
- Text sidecar discovery remains simple and filename-based.
- The local file registry is a CSV sidecar, not a database.

## Verdict

The v0.7 local-file ingestion MVP is usable for small literature-review projects that want to reconcile registry rows, notes, BibTeX files, text sidecars, and local document paths.
