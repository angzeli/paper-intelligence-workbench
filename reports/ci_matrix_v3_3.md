# CI Matrix v3.3

## Python Matrix

CI runs on:

- Python 3.10
- Python 3.11
- Python 3.12

## Workflow

The GitHub Actions workflow installs the package with development extras and
runs the v3.3 release quality gate:

```bash
python scripts/run_quality_gate.py release --out scratch/ci_quality_gate.md
```

## Checks Covered

- package import and version print
- CLI help smoke check
- clean-room install check
- ruff lint
- ruff format check
- mypy over release scripts
- pytest
- quick CLI smoke workflow
- notebook validation
- data-safety audit
- source and wheel build without build isolation

## Safety Boundary

CI requires no secrets and does not use cloud APIs, LLM APIs, publisher
scraping, PDFs, or real paper data.
