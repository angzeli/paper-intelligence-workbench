# Release Readiness v1.5

## Verdict

Usable for local rule-based validation over synthetic and user-provided project
data, with the same local-first boundaries as the rest of Paper Intelligence
Workbench.

## Features Added

- Added `paper_workbench.rules` for declarative rule loading, validation,
  execution, and Markdown reporting.
- Added `paperwb rules list`, `validate-config`, `run`, `report`, and
  `explain`.
- Added project-specific synthetic `rules.json` examples for
  `zis_photocatalysis` and `finance_reading`.
- Added built-in adapters for registry validation, citation audits,
  evidence-map readiness checks, manuscript QA findings, and workspace-health
  findings.
- Added docs for rule engine behavior, custom rules, built-in adapters, schema,
  and safety boundaries.

## Implemented Rule Types

- `required_field`
- `allowed_values`
- `regex_match`
- `min_count`
- `max_count`
- `contains_tag`
- `missing_note_for_status`
- `claim_strength_threshold`
- `evidence_type_required`
- `citation_key_required`
- `theme_min_papers`
- `theme_min_strong_claims`
- `manuscript_no_unknown_citations`

## Safety Boundary

- Rule files are JSON data only.
- Unsupported condition types are config errors.
- Rule commands do not execute arbitrary Python code.
- Rule commands do not mutate registries, notes, BibTeX files, drafts, themes,
  or project profiles.
- `rules report` writes only the requested Markdown output.
- Existing validators and reports remain available and unchanged.

## Commands Checked

- `paperwb rules --help`
- `paperwb rules list --project zis_photocatalysis --builtins`
- `paperwb rules validate-config --project zis_photocatalysis --strict`
- `paperwb rules run --project zis_photocatalysis`
- `paperwb rules report --project zis_photocatalysis --out reports/rule_report_v1_5.md --force`
- `paperwb rules explain zis.theme.photocorrosion.min_papers --project zis_photocatalysis`

## Tests

Rule-engine coverage was added in `tests/test_rules_v1_5.py` for config
loading, invalid config diagnostics, required fields, allowed values, regex
matching, count rules, tag rules, missing-note rules, citation-key rules, theme
thresholds, claim strength behavior, evidence-type rules, manuscript citation
rules, file-target rules, report rendering, CLI smoke behavior, and no
arbitrary code execution.

Validation performed during the v1.5 implementation:

- `python -m pytest -q` passed.
- `paperwb --help` passed.
- `paperwb rules --help` passed.
- `paperwb rules validate-config --project zis_photocatalysis --strict` passed.
- `paperwb rules validate-config --project finance_reading --strict` passed.
- `paperwb rules run --project zis_photocatalysis --no-builtins` passed with the expected synthetic warnings.
- `paperwb rules run --project finance_reading --no-builtins` passed with no configured-rule findings.
- `python scripts/smoke_cli_workflow.py --quick` passed.
- `python scripts/data_safety_audit.py --strict` completed with 0 errors and known historical warnings.

## Reports Generated

- `reports/rule_report_v1_5.md`
- `reports/rule_config_audit_v1_5.md`
- `reports/project_rules_zis_v1_5.md`
- `reports/release_readiness_v1_5.md`
- `reports/v1_6_recommended_patch_plan.md`

## Known Limitations

- Rule conditions are intentionally limited and do not support arbitrary boolean
  expressions.
- Rule findings are Markdown only in v1.5; CSV/JSON export can be added later if
  users need spreadsheet review.
- Built-in adapters may report findings that also appear in existing report
  commands.
- Manuscript-specific rules run only when a manuscript path is explicitly
  supplied.

## Recommended v1.6 Scope

- Add rule-finding CSV/JSON export.
- Add severity/category filters to reduce noisy reports.
- Add more project-scale rule fixtures before expanding condition types.
- Add report-diff tooling for rule reports and existing generated reports.
