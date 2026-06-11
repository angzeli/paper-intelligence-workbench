# Hostile Maintainer Review: v1.6 Current Repository

Date: 2026-06-11

Scope: standalone release review of the current repository as if it were about
to be handed to external users. I inspected package metadata, CLI behavior,
project profiles, registry/BibTeX/note/claim workflows, reports, authoring and
manuscript tooling, import/export, sync, local files, indexed search, rules,
dashboard, tests, notebooks, docs, generated reports, synthetic data, CI, and
repo hygiene. No implementation files were modified during inspection.

## Release Verdict

Do not tag this exact tree as a polished external v1.6 release. The core test
suite passes and I did not find an immediate data-loss or cloud/LLM boundary
violation, but the new terminal dashboard has release-quality defects:
non-positive limits succeed, top next actions duplicate the same underlying
problem, and the checked-in dashboard report depends on ignored local audit-log
state. These are not catastrophic, but they are visible to a new user and weaken
the release claim that reports are reproducible from local checked-in inputs.

Verdict: **hold external release until the high-priority dashboard fixes below
land**. Internal/local use remains acceptable.

## Validation Performed

- `python -m pytest -q`: passed, 221 tests.
- `python -m pytest --collect-only -q`: collected 221 tests.
- `python -m paper_workbench.cli --help`: passed; `dashboard` is exposed.
- `python -m paper_workbench.cli dashboard --help`: passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  reported `1.6.0`.
- `python scripts/validate_notebooks.py`: validated 8 notebooks.
- `python scripts/check_notebooks.py`: checked 8 notebooks, no absolute-path
  failures reported.
- `python scripts/data_safety_audit.py --out /private/tmp/paperwb_hostile_v1_6_data_safety.md --strict`:
  passed with 0 errors and 7 historical absolute-path warnings.
- `git ls-files | rg '(\\.pdf$|\\.sqlite$|\\.db$|\\.paperwb/|__pycache__|\\.pytest_cache|^scratch/|^build/|^dist/|\\.egg-info/)'`:
  no tracked forbidden artifacts found.
- Dashboard probes:
  - `paperwb dashboard --project zis_photocatalysis --limit 3`: passed but
    top three actions all point to the same missing-evidence problem through
    different subsystems.
  - `paperwb dashboard --project zis_photocatalysis --limit 0`: passed and
    showed no next actions, queue items, or follow-ups despite known issues.
  - `paperwb dashboard --project zis_photocatalysis --limit -1`: passed and
    emitted a long, sliced result set instead of rejecting invalid input.
  - `paperwb dashboard --project missing_project`: failed cleanly with a useful
    user-facing error and next step.

## Release Blockers

None found that would destroy user data, require network/cloud services, commit
copyrighted content, or make the package unimportable. The current blockers are
release-quality rather than safety-critical.

## High-Priority Issues

1. **Dashboard `--limit` accepts invalid values and silently produces misleading output.**

   Evidence: `paperwb dashboard --project zis_photocatalysis --limit 0` exits
   `0` and prints "No next actions generated" even though the same project has
   missing evidence, weak claims, and follow-ups. `--limit -1` also exits `0`
   and Python slicing returns all-but-last style output. The parser only sets
   `type=int` (`paper_workbench/cli.py`, dashboard parser around lines
   2413-2430), and `cmd_dashboard` forwards the value into audit-log slicing,
   reading queue generation, and dashboard rendering without validation
   (`paper_workbench/cli.py`, lines 1026 and 1041-1057). This is a public CLI
   contract bug. Reject non-positive limits with a clear error, and add tests
   for `0`, negative, and valid positive limits.

2. **Top next actions are not semantically deduplicated, so the dashboard can waste the first screen on one underlying defect.**

   Evidence: `paperwb dashboard --project zis_photocatalysis --limit 3` prints
   three separate high-priority actions for `zis_stability_2024:c1` missing an
   evidence location: workspace health, citation audit, and built-in rule
   findings. `build_next_actions` aggregates health, rule, missing-evidence,
   citation, weak-claim, manuscript, follow-up, and reading items independently
   (`paper_workbench/dashboard.py`, lines 115-242). `_dedupe_actions` only
   deduplicates identical action IDs (`paper_workbench/dashboard.py`, lines
   505-513), so cross-subsystem duplicates survive. This directly weakens the
   v1.6 "next actions" value proposition. Add a semantic dedupe/grouping key
   such as `(related, issue-family)` or collapse duplicate evidence-location
   findings into one action with multiple sources.

3. **Checked-in dashboard reports depend on ignored, mutable audit-log state.**

   Evidence: `cmd_dashboard` always loads recent audit events from
   `.paperwb/audit_log.jsonl` under the selected root (`paper_workbench/cli.py`,
   line 1026). `dashboard_markdown` always renders the "Recent Audit Events"
   section (`paper_workbench/dashboard.py`, lines 294-338, 446-459). The
   committed `reports/dashboard_v1_6.md` contains timestamped local audit-log
   rows from previous maintainer commands, including manuscript and index runs
   with 2026-06-11 timestamps. Because `.paperwb/` is ignored, this report is
   not reproducible from tracked inputs and can drift whenever local commands
   are run. Add a deterministic option such as `--no-audit-log` or
   `--audit-events 0`, use it for release reports, and test that generated
   report snapshots do not depend on ignored local state.

4. **v1.6 dashboard coverage is missing from release-surface docs and smoke scripts.**

   `docs/CLI_SURFACE.md` and `docs/COMMAND_CONTRACTS.md` are still labelled
   v1.5 and do not list `paperwb dashboard`. `docs/REPORT_MATRIX.md` and
   `docs/REPORT_GALLERY.md` cover the older theme dashboard but not the v1.6
   terminal dashboard, next-actions report, or project-health summary. The CI
   workflow runs `paperwb --help` and the generic smoke script, but
   `scripts/smoke_cli_workflow.py` does not exercise `paperwb dashboard`. Tests
   exist in `tests/test_dashboard_v1_6.py`, but the external command contract
   and smoke path lag behind the feature. Update the docs and add the dashboard
   to the smoke workflow after fixing the limit behavior.

## Medium-Priority Issues

1. **Dashboard issue counts double-count findings from adapters.** The v1.6
   dashboard shows workspace health, citation audit, and rule findings as
   separate counts. Built-in rule adapters intentionally wrap some of the same
   findings, so "Rule findings: 8 errors, 16 warnings" can look much worse than
   the underlying project state. This should be explained in the dashboard or
   grouped by source/unique issue.

2. **Default dashboard can look nonsensical in the legacy workspace.** The
   default `paperwb dashboard --limit 3` can show `Papers: 0` while still
   showing notes and claims from legacy example paths. That reflects an empty
   default registry plus checked-in notes, but a new user will read it as
   inconsistent. Add a warning when notes/claims exist but no registry rows are
   loaded.

3. **Report reproducibility is uneven across historical reports.** The
   data-safety audit still reports seven absolute-path warnings in historical
   reports/tests. They are warnings, not errors, but the release story would be
   cleaner if machine-local paths were scrubbed from release-facing reports.

4. **The CLI module remains very large.** `paper_workbench/cli.py` centralizes
   many command groups and now includes dashboard, rules, sync, files, reading,
   backup, manuscript, and import/export wiring. This is still working, but it
   increases the risk that future patches accidentally couple unrelated
   behaviors. Splitting command groups into small parser/handler modules should
   be a post-release maintainability task.

5. **Notebook coverage trails feature growth.** Notebook validation is passing,
   but notebooks stop at v1.0-style authoring/readiness workflows. There is no
   notebook or script specifically demonstrating rules, v1.6 dashboard triage,
   sync, or local-file ingestion end to end. This is not a blocker, but it
   undercuts external onboarding for later features.

## Low-Priority Polish

- Generated dashboard tables use raw boolean strings such as `True` in audit
  event rows; lower-case normalized booleans would read better in Markdown.
- The v1.6 dashboard is plain text only. That is acceptable and dependency-safe,
  but docs should avoid implying it is an interactive TUI.
- Stale ignored build artifacts (`dist/`, `build/`, egg-info) exist locally.
  They are ignored and not tracked, but release maintainers should clean them
  before packaging demonstrations.
- Historical report files make it hard to identify the current release snapshot.
  `reports/index.md` helps, but a future cleanup should archive or prune stale
  release reports before public launch.

## Missing Tests

- `paperwb dashboard --limit 0` and negative-limit failure tests.
- Dashboard semantic next-action dedupe tests for the same claim/finding
  surfaced through health, citation audit, and rules.
- Dashboard Markdown determinism test that proves ignored audit logs do not
  affect checked-in release reports.
- Command-contract tests documenting `paperwb dashboard` help, happy path,
  invalid-limit failure path, overwrite refusal, and project-specific behavior.
- Smoke workflow coverage for `paperwb dashboard --project ... --view
  next-actions`.
- Report-matrix or release-hygiene test ensuring v1.6 dashboard reports are
  listed in report docs.

## Documentation Mismatches

- `docs/CLI_SURFACE.md` says v1.5 and omits `paperwb dashboard`.
- `docs/COMMAND_CONTRACTS.md` says v1.5 and omits dashboard command
  expectations.
- `docs/REPORT_MATRIX.md` omits `reports/dashboard_v1_6.md`,
  `reports/next_actions_v1_6.md`, and
  `reports/project_health_summary_v1_6.md`.
- `docs/REPORT_GALLERY.md` documents theme dashboard only, not the v1.6
  terminal dashboard report family.
- `scripts/smoke_cli_workflow.py` still titles its report "CLI Smoke Workflow
  v0.8" and does not include dashboard smoke steps.

## CLI Usability Problems

- Invalid dashboard limits succeed instead of returning a user-facing error.
- Top next actions can repeat the same fix several times, crowding out useful
  follow-up actions and reading recommendations.
- There is no CLI option to suppress audit-log rows in dashboard Markdown even
  though audit logs are local ignored state and often irrelevant for a release
  report.
- Dashboard rule counts are hard to interpret because built-in rule adapters can
  re-label existing workspace and citation findings.

## Data-Safety Risks

- No tracked PDFs, SQLite caches, `.paperwb` logs, Python caches, build outputs,
  or IDE folders were found.
- No cloud, LLM, publisher-scraping, or copyrighted-content dependency risk was
  found in the inspected commands.
- The main data-safety concern is privacy/reproducibility: `reports/dashboard_v1_6.md`
  includes local audit-log timestamps and command summaries sourced from ignored
  state. That is not a secret leak in the current synthetic repo, but it is a
  bad default for reports a user may commit or share.

## Overengineering Risks

- Dashboard aggregation now spans registry, notes, claims, BibTeX, citation
  audit, workspace health, rules, manuscript QA, reading sessions, follow-ups,
  audit logs, and reports. Without semantic issue grouping it produces more
  noise than signal.
- Built-in rule adapters are useful, but using them inside the dashboard by
  default duplicates other issue sources. The dashboard needs a clearer
  distinction between raw source findings and unique user actions.
- The project has accumulated many generated reports and docs. The release
  should favor a few maintained "current" entry points rather than expecting
  users to browse every historical report.

## Recommended Fix Sequence

1. Validate `paperwb dashboard --limit` as a positive integer and add CLI tests
   for invalid values.
2. Add semantic deduplication/grouping for next actions, then update
   `tests/test_dashboard_v1_6.py` with a regression fixture for repeated
   missing-evidence findings.
3. Add dashboard audit-log control (`--no-audit-log` or equivalent), regenerate
   v1.6 dashboard reports using deterministic tracked inputs, and add a
   determinism test.
4. Update `docs/CLI_SURFACE.md`, `docs/COMMAND_CONTRACTS.md`,
   `docs/REPORT_MATRIX.md`, `docs/REPORT_GALLERY.md`, and
   `scripts/smoke_cli_workflow.py` for v1.6 dashboard behavior.
5. Add dashboard smoke steps to CI through the existing smoke script.
6. After the focused dashboard patch, rerun pytest, notebook checks,
   data-safety audit, `paperwb dashboard` smoke tests, and regenerate the
   release-facing dashboard reports.
