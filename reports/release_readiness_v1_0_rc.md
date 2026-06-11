# Release Readiness v1.0-rc

## Release Verdict

Paper Intelligence Workbench is coherent enough for a local external-user
release candidate. It should not be tagged as v1.0.0 until the maintainers
decide whether to bump package metadata from `0.10.0` and run a true fresh
virtual-environment install outside the development checkout.

## Blockers

- None found in the v1.0-rc validation run.

## High-Priority Issues

- Package metadata still reports `0.10.0`; this is acceptable for an untagged RC
  hardening pass but must be decided before a v1.0.0 tag.
- Historical reports still contain some machine-local absolute-path warnings.
  The current data-safety audit reports zero errors and leaves these historical
  warnings visible.

## Medium-Priority Issues

- BibTeX parsing remains intentionally lightweight.
- Markdown note parsing remains template-oriented.
- Indexed search is a rebuildable local cache and can become stale if users edit
  files without rebuilding.
- The scripted clean-room check uses the current Python environment rather than
  creating a virtual environment automatically.

## Tests And Checks Run

- `python -m pytest -q`: passed, 148 tests collected.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: passed, `0.10.0`.
- `paperwb --help`: passed.
- `python scripts/clean_room_install_check.py --out reports/clean_room_install_check_v1_0_rc.md`: passed, 16 steps, 0 failures.
- `python scripts/smoke_cli_workflow.py --out reports/external_user_simulation_v1_0_rc.md --title "External User Simulation v1.0-rc"`: passed, 18 steps, 0 failures.
- `python scripts/check_notebooks.py`: passed, 8 notebooks checked.
- `python scripts/data_safety_audit.py --out reports/data_safety_v1_0_rc.md --title "Data Safety Audit v1.0-rc" --strict`: passed, 0 errors.

## Documentation Status

- Added API surface inventory.
- Added CLI surface inventory.
- Added command-contract documentation.
- Updated docs index, CLI reference, installation docs, report gallery, roadmap,
  README, AGENTS guidance, and changelog.
- Docs continue to state the local-first boundary, no cloud APIs, no LLM APIs,
  no scraping, no copyrighted examples, no claim fabrication, and evidence
  completeness rather than truth evaluation.

## Packaging Status

- `pyproject.toml` keeps zero runtime dependencies.
- CLI entry point remains `paperwb = paper_workbench.cli:main`.
- Editable install instructions remain documented.
- CI includes tests, notebook checks, smoke workflow, clean-room check, local-file
  smoke paths, data-safety audit, and tracked artifact hygiene.

## External-User Simulation

The external-user simulation exercised help, initialization, registry
validation, BibTeX validation, note-template generation, claim extraction,
evidence-map generation, citation audit, project list/search, file scan, Zotero
dry-run import, writing packet, local indexed search, file audit, Obsidian
export, and report-index export. All steps passed using synthetic data and
temporary outputs.

## Data-Safety Result

The v1.0-rc data-safety audit found zero blocking errors. It still reports 11
historical absolute-path warnings in older reports/tests. No tracked PDFs,
SQLite cache databases, backup archives, audit logs, `.idea`, Python cache files,
or secrets were reported as blocking errors.

## Known Limitations

See [known_limitations_v1_0_rc.md](known_limitations_v1_0_rc.md).

## Recommended Steps Before Tagging v1.0.0

- Decide on package version metadata and update if tagging v1.0.0.
- Run a true fresh virtual-environment install on a separate checkout.
- Review historical absolute-path report warnings.
- Run CI on the release branch.
- Do not publish or push until maintainers explicitly approve.
