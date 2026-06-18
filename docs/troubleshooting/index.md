# Troubleshooting

Start with read-only diagnostics. Do not copy project folders or run migration
commands until you know what is wrong.

## Basic Checks

```bash
python -c "import paper_workbench; print(paper_workbench.__version__)"
paperwb --help
paperwb doctor --project clean_demo --strict
paperwb dashboard --project clean_demo --no-audit-log
```

## Validate Data

```bash
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
```

## Inspect Project Health

```bash
paperwb integrity check --project clean_demo --out scratch/integrity.md --force
paperwb rebuild plan --project clean_demo --out scratch/rebuild_plan.md --force-report
paperwb rules report --project clean_demo --out scratch/rules.md --force
```

## Create A Sanitized Support Bundle

```bash
paperwb support redact-preview --project clean_demo
paperwb support bundle --project clean_demo --out scratch/clean_demo_support_bundle
```

Support bundles are safe by default. They should not include PDFs, full notes,
full drafts, raw audit logs, cache databases, backup archives, or private
comments.

## Common Problems

| Symptom | Likely cause | Next step |
| --- | --- | --- |
| `paperwb` command not found | Package not installed in the active environment | Run `python -m pip install -e ".[test]"` or use `python -m paper_workbench.cli` from the repo root. |
| Strict registry validation fails | Missing required fields, duplicate IDs, or invalid status values | Open the reported CSV row and fix metadata manually. |
| BibTeX audit finds unknown keys | Registry and BibTeX keys are out of sync | Update the registry row or BibTeX entry; do not invent keys. |
| Claims output is empty | Notes do not contain structured claim sections | Use `paperwb note-template` and write claims manually after reading. |
| Draft QA flags weak evidence | Paragraph matching is heuristic | Treat it as a checklist for manual review, not a truth judgment. |
| Release gate fails on Ruff/build tooling | Development tools are missing locally | Install `.[dev]` or run `local-diagnostic` only as a bootstrap check. |

## More Help

- [Error Message Guide](../ERROR_MESSAGE_GUIDE.md)
- [Recovering From Bad Data](../RECOVERING_FROM_BAD_DATA.md)
- [Workspace Integrity](../WORKSPACE_INTEGRITY.md)
- [Support Bundles](../SUPPORT_BUNDLES.md)
- [Compatibility Matrix v3](../COMPATIBILITY_MATRIX_V3.md)
