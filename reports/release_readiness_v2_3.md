# v2.3 Release Readiness

Status: ready for local dogfooding after validation.

## Features Added

- Added a declarative local workflow runner.
- Added built-in recipes for daily checks, weekly review, pre-writing checks, pre-manuscript checks, pre-backup checks, external-user demos, and release-candidate checks.
- Added project-local workflow recipe loading from `projects/<project>/workflows/*.json`.
- Added workflow validation that rejects unknown step types and shell/Python execution fields.
- Added workflow run reports with per-step status, outputs, warnings, and errors.

## Commands Checked

- `paperwb workflow list`
- `paperwb workflow show daily_check`
- `paperwb workflow run daily_check --project zis_photocatalysis --dry-run`
- `paperwb workflow run pre_writing_check --project zis_photocatalysis --theme photocorrosion --dry-run`
- `paperwb workflow validate projects/zis_photocatalysis/workflows/daily_check.json --strict`

## Safety Assessment

- Workflow JSON is declarative only.
- Workflow recipes cannot execute arbitrary shell commands.
- Workflow recipes cannot execute arbitrary Python code.
- Dry-run is supported for every built-in step.
- Recipes that default to dry-run require `--run-writes` before step writes are allowed from the CLI.
- Existing outputs are refused unless `--force` is supplied.

## Generated Reports

- `reports/workflow_daily_check_v2_3.md`
- `reports/workflow_weekly_review_v2_3.md`
- `reports/workflow_pre_writing_check_v2_3.md`
- `reports/workflow_release_candidate_check_v2_3.md`

## Known Limitations

- Workflow steps are intentionally coarse-grained adapters around existing local features.
- Project-specific recipes can configure step order and outputs, but cannot define arbitrary custom logic.
- Some recipe results surface existing synthetic-project warnings; those warnings are not automatically fixed by the runner.

## Recommended v2.4 Scope

- Add workflow result comparison across runs.
- Add richer recipe examples for real dogfooding projects.
- Add optional recipe presets for stable-only workflows.
- Keep custom logic declarative and avoid shell execution.
