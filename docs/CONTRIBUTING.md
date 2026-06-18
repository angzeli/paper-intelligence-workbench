# Contributing

Paper Intelligence Workbench is a local-first literature-review evidence tool.
Contributions must preserve user data and keep examples synthetic.

## Local Setup

```bash
python -m pip install -e ".[dev]"
python scripts/run_quality_gate.py --list
```

## Required Checks

For ordinary code changes:

```bash
python -m pytest -q
python scripts/smoke_cli_workflow.py --quick
python scripts/data_safety_audit.py --out scratch/data_safety_audit.md --strict
```

For release, CI, quality tooling, or public CLI changes:

```bash
python scripts/run_quality_gate.py release
```

## Safety Rules

- Do not add copyrighted PDFs or copied paper full text.
- Do not fabricate real paper metadata, claims, citations, quotes, summaries, or conclusions.
- Do not scrape publishers or use cloud/LLM APIs.
- Do not silently overwrite user notes, registry fields, BibTeX files, backups, sync state, or migration targets.
- Keep generated examples synthetic and clearly labelled.
- Keep `.paperwb/`, caches, SQLite indexes, backups, audit logs, and local dogfood outputs out of git.

## Dependency Policy

Runtime dependencies should remain empty unless there is a clear, documented
need. Development-only tools belong in `project.optional-dependencies.dev`.

v3.3 adds ruff and mypy as development tools. Ruff starts with a narrow lint
configuration to avoid broad style churn. Mypy starts with release scripts only;
package-wide typing is future work.
