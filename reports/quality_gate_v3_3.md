# Quality Gate Report

This report is generated from local commands only. It does not use cloud services, LLM APIs, or network-only checks.

Steps run: 9
Failures: 0
Skipped optional steps: 3

| Step | Result | Command |
| --- | --- | --- |
| ruff lint | skipped (missing Python module: ruff) | `python -m ruff check paper_workbench scripts tests` |
| ruff format check | skipped (missing Python module: ruff) | `python -m ruff format --check scripts/run_quality_gate.py` |
| mypy scripts | pass | `python -m mypy scripts --config-file pyproject.toml` |
| pytest | pass | `python -m pytest -q` |
| CLI smoke workflow | pass | `python scripts/smoke_cli_workflow.py --quick` |
| validate notebooks | pass | `python scripts/validate_notebooks.py` |
| check notebooks | pass | `python scripts/check_notebooks.py` |
| data safety audit | pass | `python scripts/data_safety_audit.py --out scratch/quality_gate_data_safety.md --strict` |
| build distributions | skipped (missing Python module: setuptools.build_meta) | `python -m build --sdist --wheel --no-isolation` |
