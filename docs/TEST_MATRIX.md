# Test Matrix

| Feature | Expected behavior | Tests | CLI/docs coverage | Known gaps |
| --- | --- | --- | --- | --- |
| Package import | `paper_workbench` imports and version metadata is consistent | `tests/test_release_engineering_v0_8.py` | `docs/INSTALLATION.md` | No wheel-install smoke yet |
| CLI entry point | `paperwb` and `python -m paper_workbench.cli` expose help | `tests/test_cli.py`, release smoke script | `docs/cli-reference.md` | No shell-completion tests |
| Registry validation | Missing fields, duplicate DOI/title, and invalid statuses are reported | `tests/test_registry.py`, `tests/test_v0_2_validation.py` | `docs/REGISTRY_SCHEMA.md` | CSV dialect handling is intentionally simple |
| BibTeX validation | Common entry types parse and audit findings are emitted | `tests/test_bibtex.py`, parser edge tests | `docs/BIBTEX_AUDIT.md` | Not a complete BibTeX macro engine |
| Notes and claims | Structured notes parse conservatively with warnings | `tests/test_notes_claims.py`, parser edge tests | `docs/NOTE_FORMAT.md` | Free-form notes are not fully parsed |
| Project profiles | Project paths resolve without breaking legacy `data/` workflow | `tests/test_projects_doctor_exports.py` | `docs/project-profiles.md` | No destructive migration workflow |
| Reports | Markdown reports render from local inputs | report tests, golden report tests | `docs/reports.md`, `docs/REPORT_GALLERY.md` | Historical reports are not all golden-snapshotted |
| Import/export | Local imports are non-destructive and exports are reproducible | `tests/test_import_export_v0_4.py` | `docs/import-export.md` | Ambiguous import conflict UI is basic |
| Indexed search | SQLite cache rebuilds and search falls back where needed | `tests/test_index_v0_5.py` | `docs/local-search.md` | No concurrent index update tests |
| Authoring workbench | Generates planning aids without final prose | `tests/test_authoring_workbench.py` | `docs/authoring-workbench.md` | Readiness scoring remains heuristic |
| Local files | Scans, hashes, links, audits, and preserves user files | `tests/test_local_files_v0_7.py` | `docs/local-files.md` | Optional PDF metadata extraction is future work |
| Notebook validation | Notebooks are valid JSON and portable | `scripts/check_notebooks.py`, release tests | `docs/SITE_MAP.md` | Notebooks are not executed in CI by default |
| Data safety | Tracked files are checked for forbidden artifacts and secrets | `scripts/data_safety_audit.py`, release tests | `docs/safety-and-boundaries.md` | Warnings require human review |
