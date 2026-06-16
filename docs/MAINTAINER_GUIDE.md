# Maintainer Guide

This repository is a local-first literature-review workbench. Maintenance work
should prioritize preserving user data and stable CLI behavior over adding new
surface area.

## Before Editing

1. Run `git status --short --branch --ignored`.
2. Inspect the affected module and its tests.
3. Check whether the behavior is stable or experimental in
   `docs/STABLE_SURFACE_V2.md` and `docs/EXPERIMENTAL_FEATURES_V2.md`.
4. Prefer focused patches over broad rewrites.

## Safe Refactor Rules

- Preserve command names, flags, exit behavior, and output files unless a
  release blocker requires a change.
- Add behavior-preservation tests before touching shared helpers.
- Reuse `paper_workbench.paths` for path display and containment checks.
- Reuse `paper_workbench.markdown` for new Markdown tables.
- Use `make_validation_finding` for new validation finding wrappers.
- Keep destructive workflows dry-run-first and force-gated.

## Validation Checklist

Run at least:

```bash
python -m pytest -q
python -c "import paper_workbench; print(paper_workbench.__version__)"
paperwb --help
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb dashboard --project clean_demo --no-audit-log
```

When changing reports, regenerate the affected reports and `reports/index.md`.
When changing parsing, imports, migration, backup, or write paths, add
adversarial or failure-path tests.

## What To Defer

- Splitting `cli.py` into many command modules without a separate migration
  plan.
- Replacing dataclasses with a different model layer.
- Introducing plugin execution, shell-command recipes, cloud services, LLM APIs,
  scraping, or heavy UI dependencies.
- Deleting historical reports without a cleanup plan.

