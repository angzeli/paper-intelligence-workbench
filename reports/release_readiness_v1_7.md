# Release Readiness v1.7

Date: 2026-06-11

## Verdict

v1.7 is usable as a local project-template and dogfooding release after the
validation listed below. Templates are empty scaffolds and do not include real
paper metadata, copyrighted content, or fabricated claims.

## Features Added

- `paperwb template list`
- `paperwb template inspect TEMPLATE`
- `paperwb template create TEMPLATE --project PROJECT`
- Photocatalysis, finance/valuation, ML methods, and generic templates.
- Template-generated themes, rule examples, note scaffolds, report checklists,
  manuscript QA checklists, reading queue config, and dashboard expectations.
- Dogfooding example script for creating a project from a template in a
  temporary workspace.

## Templates Added

- `photocatalysis`: FYP-style photocatalysis literature-review scaffold.
- `finance`: finance/valuation reading scaffold with explicit no-investment-advice boundary.
- `ml-methods`: machine-learning methodology reading scaffold.
- `generic`: domain-neutral literature-review scaffold.

## Validation Run

- `python -m pytest -q`
- `python -m pytest tests/test_templates_v1_7.py tests/test_release_engineering_v0_8.py tests/test_release_hygiene.py -q`
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`
- `python -m paper_workbench.cli --help`
- `python -m paper_workbench.cli template --help`
- `python -m paper_workbench.cli template list`
- `python -m paper_workbench.cli template inspect photocatalysis`
- `python -m paper_workbench.cli template create photocatalysis --project TEMPLATE_DEMO --root <tmp>`
- `paperwb doctor --project TEMPLATE_DEMO` from the temporary workspace.
- `paperwb dashboard --project TEMPLATE_DEMO --no-audit-log` from the temporary workspace.
- `paperwb rules validate-config --project TEMPLATE_DEMO --strict` from the temporary workspace.
- `paperwb report evidence-map --project TEMPLATE_DEMO --out projects/TEMPLATE_DEMO/reports/evidence_map.md --force` from the temporary workspace.
- `python examples/create_project_from_template.py`
- `python scripts/smoke_cli_workflow.py --quick --out <tmp>/paperwb_smoke_v1_7.md`

## Docs Updated

- `docs/PROJECT_TEMPLATES.md`
- `docs/PHOTOCATALYSIS_TEMPLATE.md`
- `docs/FINANCE_TEMPLATE.md`
- `docs/ML_METHODS_TEMPLATE.md`
- `docs/DOGFOODING_WORKFLOW.md`
- CLI, roadmap, report-gallery, matrix, README, changelog, and AGENTS docs.

## Real-use Readiness

The templates make it faster to start a real project, but they intentionally do
not import or invent papers. A user must still add verified metadata, BibTeX,
notes, and claims.

## Limitations

- v1.7 does not update existing projects from newer template versions.
- There is no template diff or migration workflow yet.
- The finance template is organizational only and does not provide investment advice.
- The templates are intentionally generic; users should customize themes and
  rules for their actual research question.

## Recommended v1.8 Scope

- Add `paperwb template diff` or a non-destructive template update plan.
- Add optional user-defined template JSON files.
- Add dashboard filters for theme, tag, status, and priority.
- Add report-regression checks for template overview reports.
