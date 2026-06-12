# Example Workflow Validation v2.0rc

## Scope

Checked examples include local Python scripts under `examples/`, synthetic data
under `data/`, synthetic drafts, and synthetic projects.

## Validation Status

- `python scripts/smoke_cli_workflow.py --quick`: passed, 14 smoke steps.
- `python scripts/clean_room_install_check.py --quick`: passed, 7 release-check steps.
- Temporary editable install: passed and exposed `paperwb`.
- Temporary workspace init: passed.
- Template create/list/inspect: passed.
- Project validate, doctor, and integrity checks: passed with expected empty-project warnings.
- Example registry validation: passed with expected synthetic duplicate findings.
- Example BibTeX validation: passed with expected synthetic incomplete-entry findings.
- Note template generation: passed.
- Claim extraction: passed and wrote 3 claims.
- Evidence-map and citation-audit report generation: passed.
- Dashboard, rules, import dry-run, export, index rebuild/search, draft audit,
  manuscript QA, writing packet, reading queue, follow-ups, sync plan/apply
  dry-run, and local file audit: passed against synthetic data.

## Safety Boundary

Examples must remain synthetic. They must not include real paper metadata,
copyrighted PDFs, copied paper full text, cloud calls, LLM calls, or publisher
scraping.
