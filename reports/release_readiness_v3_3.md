# Release Readiness v3.3

## Verdict

Ready for local dogfooding after available local quality checks. Strict release
validation still requires the development-tool environment used by CI.

v3.3 is a maintainability patch. It adds quality tooling, CI hardening, and
release validation structure without changing product workflows.

## Implemented

- Added `scripts/run_quality_gate.py`.
- Added ruff and mypy development dependencies.
- Added ruff, format, and mypy configuration to `pyproject.toml`.
- Updated CI to run the release quality gate on Python 3.10, 3.11, and 3.12.
- Added quality-gate tests.
- Added quality, CI, development workflow, contribution, and release validation docs.
- Updated AGENTS.md with quality-gate requirements for future agents.

## Checks To Run

```bash
python -m pytest -q
python -m mypy scripts --config-file pyproject.toml
python scripts/run_quality_gate.py release
python scripts/validate_notebooks.py
python scripts/check_notebooks.py
python scripts/data_safety_audit.py --out scratch/data_safety_audit.md --strict
paperwb --help
```

## Local Validation Result

The strict release gate remains:

```bash
python scripts/run_quality_gate.py release
```

In this local environment the strict gate cannot complete because Ruff is not
installed and `setuptools.build_meta` is not importable through the local
setuptools chain. The previous `release --allow-missing-tools` path has been
replaced with an explicit diagnostic target:

```bash
python scripts/run_quality_gate.py local-diagnostic
```

The local diagnostic gate passed all available checks and labels skipped
tool-backed steps as diagnostic, not release-ready:

- mypy scripts: pass
- pytest: pass
- CLI smoke workflow: pass
- notebook validation: pass
- data-safety audit: pass
- ruff lint: diagnostic skip locally, installed in CI through `.[dev]`
- ruff format-check: diagnostic skip locally, installed in CI through `.[dev]`
- build distributions: diagnostic skip locally because `setuptools.build_meta` is not
  importable in this environment

## Known Limitations

- Ruff was not installed in the local environment before this patch; CI installs
  it through development extras.
- Build validation uses `--no-isolation` to avoid network-backed dependency
  installation during local release checks.
- `local-diagnostic` output is useful for bootstrap environments but is not a
  strict release-gate pass.
- Ruff rules are intentionally narrow in v3.3.
- Ruff format-check is scoped to the new quality-gate script to avoid broad
  formatting churn.
- Mypy is scoped to release scripts. Package-wide typing remains future work.

## Safety Assessment

The patch adds no runtime dependencies, cloud calls, LLM calls, scraping,
publisher access, PDFs, or real paper metadata. Generated quality outputs belong
in ignored `scratch/` unless explicitly requested as committed release reports.
