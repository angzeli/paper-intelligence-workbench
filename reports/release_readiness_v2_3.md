# v2.3 Release Readiness

Status: ready for local dogfooding after validation.

## Features Added

- Added a declarative local workflow runner.
- Added built-in recipes for daily checks, weekly review, pre-writing checks, pre-manuscript checks, pre-backup checks, external-user demos, and release-candidate checks.
- Added project-local workflow recipe loading from `projects/<project>/workflows/*.json`.
- Added workflow validation that rejects unknown step types and shell/Python execution fields.
- Added workflow run reports with per-step status, outputs, warnings, and errors.
- Applied release-hygiene fixes after hostile review: active report titles now use the package version, the clean-room check uses current v2 wording, and workflow reports surface project descriptions.

## Commands Checked

- `paperwb workflow list`
- `paperwb workflow show daily_check`
- `paperwb workflow run daily_check --project zis_photocatalysis --dry-run`
- `paperwb workflow run pre_writing_check --project zis_photocatalysis --theme photocorrosion --dry-run`
- `paperwb workflow validate projects/zis_photocatalysis/workflows/daily_check.json --strict`
- `paperwb workflow run pre_backup_check --project <synthetic-project> --run-writes --force` covered by regression tests.

## Safety Assessment

- Workflow JSON is declarative only.
- Workflow recipes cannot execute arbitrary shell commands.
- Workflow recipes cannot execute arbitrary Python code.
- Dry-run is supported for every built-in step.
- Recipes that default to dry-run require `--run-writes` before step writes are allowed from the CLI.
- Existing outputs are refused unless `--force` is supplied.
- Project descriptions are included in workflow reports so intentionally imperfect synthetic fixtures are labelled before findings are interpreted.

## Generated Reports

- `reports/workflow_daily_check_v2_3.md`
- `reports/workflow_weekly_review_v2_3.md`
- `reports/workflow_pre_writing_check_v2_3.md`
- `reports/workflow_release_candidate_check_v2_3.md`
- `reports/claim_review_queue_v2_3.md`
- `reports/dashboard_v2_3.md`
- `reports/workspace_integrity_v2_3.md`
- `reports/rule_report_v2_3.md`
- `reports/local_files_audit_v2_3.md`
- `reports/duplicate_files_v2_3.md`
- `reports/missing_files_v2_3.md`
- `reports/text_sidecars_v2_3.md`
- `reports/migration_plan_v2_3.md`
- `reports/backup_manifest_demo_v2_3.md`
- `reports/restore_dry_run_v2_3.md`

## Known Limitations

- Workflow steps are intentionally coarse-grained adapters around existing local features.
- Project-specific recipes can configure step order and outputs, but cannot define arbitrary custom logic.
- The `zis_photocatalysis` fixture intentionally surfaces evidence-gap, weak-claim, and citation-audit findings for dogfooding; workflow reports now label that fixture explicitly.

## Recommended v2.4 Scope

- Add workflow result comparison across runs.
- Add richer recipe examples for real dogfooding projects.
- Add optional recipe presets for stable-only workflows.
- Keep custom logic declarative and avoid shell execution.
