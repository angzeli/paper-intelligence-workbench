# Continuous Integration

The GitHub Actions workflow lives at `.github/workflows/ci.yml`.

It runs on push and pull request using Python 3.10, 3.11, and 3.12. The workflow
does not require secrets, network services, cloud APIs, LLM APIs, publisher
scraping, or real paper data.

## CI Steps

1. Check out the repository.
2. Install the package with development extras:

   ```bash
   python -m pip install -e ".[dev]"
   ```

3. Import the package and print the version.
4. Run basic CLI help smoke checks.
5. Run the clean-room install check.
6. Run the v3 release quality gate:

   ```bash
   python scripts/run_quality_gate.py release --out scratch/ci_quality_gate.md
   ```

## What The Gate Covers

- pytest
- ruff lint
- ruff format check for the quality-gate script
- mypy over release scripts
- CLI smoke workflow
- notebook validation
- data-safety audit
- package build without build isolation

If CI fails, fix the underlying issue. Do not mark a failing quality gate as
acceptable without a written release-readiness note explaining the blocker.
