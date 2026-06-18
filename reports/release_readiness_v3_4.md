# Release Readiness v3.4

## Verdict

Ready for local dogfooding as a documentation-source and guided-workflow patch.

v3.4 changes documentation structure, cookbook coverage, command-reference
auditing, and generated docs reports. It does not add product features or
change stable CLI behavior.

## Implemented

- Promoted package metadata to `3.4`.
- Added a coherent Markdown docs source structure.
- Added a guided full literature-review walkthrough.
- Added cookbook recipes for common local workflows.
- Added a stronger report gallery.
- Added `scripts/check_docs.py`.
- Added documentation consistency tests.
- Updated README, stable surface, roadmap, report gallery, command reference,
  and changelog.
- Regenerated the report index.

## Checks Run

- `python scripts/check_docs.py`
- `python -m pytest -q`
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`
- `paperwb --help`
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict`
- `paperwb doctor --project clean_demo --strict`
- `paperwb dashboard --project clean_demo --no-audit-log`
- `python scripts/run_quality_gate.py local-diagnostic --out <tmp>`
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 850
  repository files with 0 errors and 0 warnings.

## Known Limitations

- The docs are Markdown source only; no static-site generator is configured.
- Some older flat docs remain for compatibility and historical context.
- Experimental workflow docs may change after real dogfooding.
- Local strict release gate still requires a dev environment with Ruff and a
  working local build backend; diagnostic mode is not a release pass.

## Data-Safety Assessment

- No PDFs, copied paper full text, private paths, real metadata, real claims, or
  external service calls were added.
- New examples use synthetic project names or existing synthetic fixtures.
- Documentation checks reject raw absolute-path patterns in README and docs.

## Recommended v3.5 Scope

- Dogfood the cookbook on a real 10-15 paper project and record friction.
- Decide whether to introduce MkDocs or keep pure Markdown source.
- Add a README quickstart transcript test if the quickstart changes.
- Continue reducing duplicate historical docs only after real users identify
  confusing entry points.
