# Hostile Maintainer Review: Current Repository

Date: 2026-06-15

Scope: standalone release-gate review of the current Paper Intelligence
Workbench repository as if deciding whether this version is safe for local
dogfooding. I inspected package architecture, CLI behavior, stable versus
experimental surface docs, registry and BibTeX workflows, notes and claims,
evidence maps, manuscript and draft QA, reading sessions, imports and exports,
sync and conflict planning, search and indexing, backup/migration/integrity,
rule engine, dashboard, evidence graph, claim lifecycle, workflow runner, tests,
docs, notebooks, reports, synthetic data, data-safety boundaries, `.gitignore`,
and git status.

## Release Verdict

**Ready for cautious local dogfooding. Not ready to present as a polished public
stable release without release-hygiene cleanup.**

The core local workflows are functional. The package imports, `paperwb --help`
works, the full test suite passed, notebook structure checks passed, the strict
data-safety audit reported zero errors, and representative stable and
experimental workflows ran without Python tracebacks.

The remaining concerns are not destructive-behavior blockers. They are
release-confidence issues: stale feature-version labels in active command
outputs, a canonical synthetic project that intentionally emits error-level
findings, and a very broad command surface that needs continued consolidation
before a public stable release.

## Validation Performed

- `git status --short --branch`: clean before this report was written; branch
  was `main...origin/main [ahead 19]`.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `2.3`.
- `paperwb --help`: passed and listed the current top-level command surface,
  including `workflow`, `graph`, `claim-review`, and `contradictions`.
- `python -m pytest -q`: passed.
- `python scripts/smoke_cli_workflow.py --quick`: 14 smoke steps, 0 failures.
- `python scripts/check_notebooks.py`: validated and listed 8 notebook titles.
- `python scripts/data_safety_audit.py --out scratch/review_data_safety.md --strict`:
  checked 668 repository files, 0 errors, 7 warnings.
- `python -m paper_workbench.cli workflow list --project zis_photocatalysis`:
  passed and listed built-in plus project-local recipes.
- `python -m paper_workbench.cli workflow run daily_check --project zis_photocatalysis --dry-run --out scratch/review_workflow_daily_check.md --force`:
  passed; dry-run report had expected synthetic fixture findings.
- `python -m paper_workbench.cli graph summary --project zis_photocatalysis`:
  passed and is now labeled `v2.3`.
- `python -m paper_workbench.cli claim-review queue --project zis_photocatalysis --limit 3`:
  passed but still prints a `v2.2` report title.
- `python -m paper_workbench.cli manuscript qa drafts/synthetic_good_section.md --project zis_photocatalysis --out scratch/review_manuscript_qa.md --force`:
  passed.
- `python -m paper_workbench.cli writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/review_writing_packet.md --force`:
  passed.
- `python -m paper_workbench.cli sync plan --project zis_photocatalysis --source data/examples/zotero_export.csv --source-type zotero-csv --out scratch/review_sync_plan.md --json-out scratch/review_sync_plan.json --force`:
  passed.
- `python -m paper_workbench.cli integrity check --project zis_photocatalysis --out scratch/review_integrity.md --force`:
  passed but reported 1 expected error and 5 warnings from the synthetic
  fixture state.

## Release Blockers

None found for local dogfooding.

This verdict does not mean the repository is ready for a polished public stable
release. The project is safe enough to use locally with synthetic and real
user-owned metadata, but it still needs high-priority release-hygiene cleanup.

## High-Priority Issues

1. **Active command outputs still carry old feature-version labels.**

   Evidence: current commands still emit titles such as `Claim Review Queue
   v2.2`, `Terminal Dashboard v1.6`, `Workspace Integrity Report v0.9`, `Local
   Files Audit v0.7`, and `Rule Report v1.5`. The graph workflow has been
   updated to `v2.3`, but other current reports still look historical.

   Why it matters: these commands are live, not archived reports. A new dogfood
   user will reasonably wonder whether they are running stale code.

2. **The canonical synthetic project still produces error-level findings in
   release-check workflows.**

   Evidence: `paperwb workflow run daily_check --project zis_photocatalysis
   --dry-run` reported 3 errors and 19 warnings. `paperwb integrity check
   --project zis_photocatalysis` reported 1 error and 5 warnings. The findings
   are explainable synthetic weak-evidence cases, but they appear in current
   release reports and dashboard/rules workflows.

   Why it matters: a fixture with intentional gaps is useful, but the default
   project used throughout docs and smoke checks should either be clearly marked
   as intentionally imperfect in every relevant workflow, or paired with a clean
   green-path project for first-time validation.

3. **Release-check scripts still include historical orientation.**

   Evidence: `scripts/clean_room_install_check.py` still describes itself as a
   `v1.0-rc` current-environment check and defaults to a `Current-Environment
   Release Check v1.0-rc` title.

   Why it matters: this script is part of the external-user/release-engineering
   surface. Its behavior may still work, but the label undermines confidence in
   v2.3 release validation.

4. **Workflow runner write semantics are safe but need stronger positive
   coverage for write-enabled recipes.**

   Evidence: tests cover recipe loading, invalid shell fields, dry-run behavior,
   report generation, project-local recipes, and conflicting `--dry-run` /
   `--run-writes` flags. There is not yet a dedicated positive test that a
   dry-run-default write recipe such as `pre_backup_check` performs the expected
   write only when `--run-writes` and appropriate force behavior are supplied.

   Why it matters: v2.3 added the workflow runner specifically to coordinate
   write-capable local tasks. The negative safety tests are good; the positive
   guarded-write path should also be locked down.

## Medium-Priority Issues

1. **`paper_workbench/cli.py` remains the main architectural hotspot.**

   It is about 3,400 lines and owns command parsing, dispatch, output handling,
   and adapters for nearly every subsystem. The current test suite keeps it
   working, but future command changes are costly to review.

2. **Several feature modules still combine model, analysis, and Markdown
   rendering.**

   Large modules include `workflow.py`, `rules.py`, `authoring.py`, `index.py`,
   `reading.py`, `sync.py`, `graph.py`, `drafts.py`, `registry.py`, and
   `importers.py`. This is acceptable for a local workbench but raises the cost
   of regression review.

3. **Notebook coverage lags behind the current v2 feature surface.**

   Eight notebooks validate structurally, but newer dogfood, graph, claim
   lifecycle, dashboard, sync, manuscript QA, and workflow-runner flows are
   represented mainly by tests, scripts, docs, and reports rather than notebooks.

4. **The top-level CLI is still intimidating for first-time users.**

   The help epilog now gives a stable/experimental summary, but the command list
   itself is very broad. A technically comfortable new user can proceed, but a
   less patient user may not know where to start without reading docs first.

5. **Historical report volume is high.**

   There are 183 Markdown reports under `reports/`. The index helps, but broad
   searches surface old v0.x/v1.x/v2.0rc reports beside current v2.3 reports.

## Low-Priority Polish

- Some docs intentionally describe feature introduction versions, while active
  commands now need current-release titles. The distinction should be made more
  explicit.
- `integrity` requires a `check` subcommand; top-level help is accurate, but the
  quick mental model `paperwb integrity --project ...` fails.
- Historical reports include valid old absolute-path examples, which trigger
  data-safety warnings.
- Public demo files under `public/demos/v2_0_dogfood_real/` are synthetic and
  safe, but the folder name includes `real`, which remains easy to misread.

## Data-Safety Risks

- Strict audit result: 0 errors, 7 warnings.
- Warnings are historical local-path patterns in old reports and tests:
  `reports/hostile_review_v0_4.md`, `reports/hostile_review_v0_5.md`,
  `reports/release_readiness_v0_3.md`, `reports/release_readiness_v0_6.md`,
  and three tests containing `/private/...` fixtures.
- No tracked PDFs, SQLite databases, `.paperwb` logs, backup archives, `.idea`
  files, or Python cache files were found.
- `public/demos/v2_0_dogfood_real/` is tracked but contains synthetic placeholder
  metadata and explicitly warns not to commit private real plans.
- Ignored local artifacts remain present under `.paperwb/`, `scratch/`, and
  public-demo `.paperwb/` internals; these are ignored and not staged.

## Docs Mismatches

- Current command outputs still include old report titles for claim lifecycle,
  dashboard, integrity, files, backup, migration, and rules.
- `scripts/clean_room_install_check.py` still speaks in v1.0-rc language.
- The v2 docs classify workflow as experimental, but the top-level command list
  cannot mark individual commands directly; users need the epilog or docs.
- Historical docs and reports are useful audit artifacts, but searches for
  current guidance require care.

## CLI Usability Issues

- `paperwb --help` is comprehensive but dense.
- `paperwb integrity --project ...` fails because the command requires
  `paperwb integrity check --project ...`.
- Validation-style commands often return `0` with error-level findings unless
  `--strict` is supplied. This is documented, but it remains a scripting trap.
- Advanced write-capable commands are discoverable from top-level help before a
  user sees the detailed safety docs.

## Overengineering Risks

- The repository now includes registry validation, BibTeX validation, structured
  notes, claim extraction, evidence maps, authoring reports, draft/manuscript
  QA, reading sessions, imports/exports, local files, search/indexing,
  sync/conflict planning, backups, migration, integrity, audit logs, rules,
  dashboard, templates, dogfood scaffolds, evidence graph, claim lifecycle, and
  workflow recipes.
- The next release should prioritize stabilization, release-label cleanup,
  documentation consolidation, and real dogfooding over new major subsystems.
- Avoid adding graph databases, embeddings, cloud sync, web apps, plugin
  marketplaces, semantic contradiction inference, or PDF full-text extraction by
  default.

## Stale Generated Reports

- Current `reports/index.md` correctly identifies `Current v2.3 Release
  Reports`.
- Active report generators still emit several feature-introduction titles:
  v0.7, v0.9, v1.5, v1.6, and v2.2.
- Historical v0.x, v1.x, v2.0, v2.0rc, v2.1, and v2.2 reports should remain as
  audit trail artifacts, but should not be treated as current release guidance.

## Missing Tests

- Positive workflow test for a guarded write path using `--run-writes`.
- Regression test that current active report titles are either package-current
  or explicitly feature-versioned by policy.
- Clean-room install script test that checks current v2 labeling.
- Notebook or script coverage for the v2.3 workflow runner beyond the example
  script and unit/CLI tests.
- Optional green-path synthetic project test where core integrity/rules checks
  produce no error-level findings.

## Recommended Blocker-Fix Sequence

There are no blockers. For the next cleanup pass:

1. Update active report title defaults or document a strict policy for
   feature-versioned titles.
2. Update `scripts/clean_room_install_check.py` to current v2 terminology.
3. Add a positive `--run-writes` workflow test for a guarded write-capable
   recipe.
4. Add or designate a clean green-path synthetic project for first-time smoke
   checks, while keeping `zis_photocatalysis` as an intentionally imperfect
   evidence-review fixture.
5. Add a compact "start here" CLI path in docs and keep the top-level help
   stable/experimental epilog aligned with `docs/STABLE_SURFACE_V2.md`.
