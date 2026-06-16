# Final Release Verdict v3.0rc

## Verdict

Ready for local dogfooding as v3.0rc.

This is not a publish/tag verdict. It is a local release-candidate verdict for
using Paper Intelligence Workbench on a real literature-review project with
manual, user-verified metadata and notes.

## First Real Use Case

Use an FYP-style photocatalysis literature review with 10-15 papers:

1. Create an empty dogfooding scaffold.
2. Add verified metadata manually or through reviewed dry-run import reports.
3. Generate note templates.
4. Read papers and write structured notes manually.
5. Extract claims.
6. Generate evidence maps, citation audits, dashboards, and checklists.
7. Back up before sync, migration, restore, or large import operations.

## Stable Commands

`init`, `project`, `template`, `dogfood`, `validate-registry`, `validate-bib`,
`add-paper`, `list`, `note-template`, `claims`, core `report`, `checklist`,
`doctor`, and `dashboard`.

## Experimental Commands

`workflow`, `review-packet`, `sync`, `index`, `rebuild`, `files`, `draft`,
`manuscript`, `reading`, `followups`, `backup`, `migrate`, `audit-log`,
`integrity`, `rules`, `graph`, `claim-review`, `contradictions`, advanced
`export`, `import`, `writing-packet`, and `synthetic`.

## Known Limitations

- Advanced QA and graph workflows are heuristic.
- The workflow runner is useful but recipe schemas are not frozen.
- `paper_workbench/cli.py` remains large.
- Generated reports and docs from historical release cycles are noisy.
- Large real projects should use cache hygiene and report cleanup.

## Maintenance Workflow

Run:

```bash
python -m pytest -q
python -c "import paper_workbench; print(paper_workbench.__version__)"
paperwb --help
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb dashboard --project clean_demo --no-audit-log
python scripts/validate_notebooks.py
python scripts/data_safety_audit.py --strict
```

Inspect `git status --short --ignored` before committing.

## Before Public Release

- Complete one real private dogfood pass.
- Decide whether to keep all historical reports in the public tree.
- Keep experimental commands clearly labelled.
- Do not tag v3.0.0 until report index, docs, tests, notebook checks, and
  data-safety checks are current.
