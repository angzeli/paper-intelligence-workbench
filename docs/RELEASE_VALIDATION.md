# Release Validation

Use the v3.3 quality gate before release-candidate or dogfooding readiness
claims.

```bash
python scripts/run_quality_gate.py release --out scratch/release_quality_gate.md
```

The generated report is local output. Keep it in ignored `scratch/` unless a
release task explicitly asks for a committed report.

## Manual Smoke Checks

The release gate covers the automated baseline. For release notes, also run a
small set of explicit user-facing checks:

```bash
python -c "import paper_workbench; print(paper_workbench.__version__)"
paperwb --help
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb dashboard --project clean_demo --no-audit-log
```

## Failure Policy

- Fix failing tests, lint checks, type checks, notebook checks, CLI smoke
  checks, and data-safety audits.
- If a failure is environmental, document the exact command, exit code, and why
  it is not a product blocker.
- Do not push, tag, or publish with a failing release gate.
- The build step uses `--no-isolation` so local release validation does not
  require a network-backed build dependency install.
