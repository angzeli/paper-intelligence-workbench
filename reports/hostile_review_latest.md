# Hostile Maintainer Review: Current Repository

Date: 2026-06-16

Scope: standalone release-gate review of Paper Intelligence Workbench v3.0rc as
if deciding whether this version is safe for local dogfooding. I inspected
package architecture, CLI behavior, stable versus experimental surface docs,
registry and BibTeX workflows, notes and claims, evidence maps,
manuscript/draft QA, reading sessions, imports/exports, sync/conflict planning,
search/indexing, backup/migration/integrity, rule engine, dashboard, evidence
graph, claim lifecycle, workflow runner, collaboration/review packets,
performance and incremental rebuilds, tests, docs, notebooks, reports,
synthetic data, data-safety boundaries, `.gitignore`, and git status.

## Release Verdict

**Ready for local dogfooding as v3.0rc.**

I did not find a release blocker. The package imports as `3.0.0rc1`, `paperwb
--help` loads and points to v3 docs, the clean first-run project validates
without findings, the full test suite passes, notebook structure validation
passes, the data-safety audit reports zero errors/warnings, and representative
stable plus experimental CLI workflows completed without tracebacks.

This is still not a public-release verdict. The project is broad, the CLI is
oversized, historical docs/reports are noisy, and some experimental workflows
still have inconsistent output flags. Those are dogfooding risks, not release
blockers.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead
  45]`; only ignored local artifacts before writing this report.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `3.0.0rc1`.
- `paperwb --help`: passed and listed current command groups.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`: passed
  with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry
  projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed with zero
  BibTeX, citation, workspace, rule, manuscript, graph, and claim-review
  findings.
- `paperwb workflow run release_candidate_check --project clean_demo --dry-run
  --out <tmp> --force`: passed with 7 steps, 0 errors, 0 warnings.
- `paperwb graph summary --project clean_demo --out <tmp> --force`: passed.
- `paperwb rebuild plan --project clean_demo --out <tmp> --force-report`:
  passed.
- `paperwb draft audit drafts/synthetic_photocorrosion_section.md --project
  zis_photocatalysis --out <tmp> --force`: passed.
- `paperwb manuscript qa drafts/synthetic_good_section.md --project
  zis_photocatalysis --out <tmp> --force`: passed.
- `paperwb reading queue --project clean_demo`: passed.
- `paperwb rules report --project clean_demo --out <tmp> --force`: passed.
- `paperwb review-packet create --project clean_demo --theme clean-validation
  --out <tmp> --force`: passed and reported `Includes PDFs: false`.
- `paperwb backup list --project clean_demo`: passed and reported no backups.
- `paperwb sync plan --project zis_photocatalysis --source
  data/examples/zotero_export.csv --source-type zotero-csv --out <tmp>
  --json-out <tmp> --force`: passed with 3 actions and 0 conflicts.
- `paperwb import zotero-csv data/examples/zotero_export.csv --project
  zis_photocatalysis --dry-run --report <tmp> --force`: passed with 5 rows read,
  3 imported, 2 skipped, dry-run true.
- `paperwb files scan --project clean_demo`: passed and listed local note and
  BibTeX files without copying/deleting files.
- `paperwb index status --project clean_demo --check-files`: passed and clearly
  reported the missing rebuildable cache.
- `paperwb claim-review queue --project clean_demo`: passed and reported one
  newly extracted claim needing explicit review.
- `paperwb contradictions report --project clean_demo --out <tmp> --force`:
  passed.
- `python scripts/validate_notebooks.py`: validated 8 notebooks.
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 746
  repository files with 0 errors and 0 warnings.
- `python -m pytest -q`: passed.
- `reports/index.md` matches a freshly generated report index.
- `git ls-files` scan found no tracked PDFs, SQLite/cache DBs, backup archives,
  audit logs, `.paperwb` directories, Python caches, `.DS_Store`, `build/`,
  `dist/`, or egg-info artifacts.

## Release Blockers

None found.

## High-Priority Issues

1. **Import dry-run report output is still too easy to dirty a project.**

   Evidence: `paperwb import zotero-csv ... --project zis_photocatalysis
   --dry-run --out <tmp>` fails because import commands do not support `--out`.
   `--project` plus `--reports-dir <tmp>` also fails because project profiles
   reject path overrides. The correct escape hatch is `--report <tmp>`, which
   works, but README/common examples still show dry-run imports without an
   explicit report path.

   Why it matters: this does not mutate registry rows, so it is not a data-loss
   blocker. It can still write a project-local report during what many users
   interpret as a no-write dry run, creating avoidable working-tree churn in
   dogfooding projects.

   Recommended fix: update public import examples to use `--report
   scratch/import_zotero_dry_run.md --force`, and add a regression test that the
   documented dry-run command writes only the expected report path.

## Medium-Priority Issues

1. **The CLI implementation is still a maintainability hotspot.**

   `paper_workbench/cli.py` is about 3,785 lines and owns argument parsing,
   project path resolution, write preflights, audit events, and dispatch for
   nearly every subsystem. v2.6 helper cleanup helped, but future changes here
   remain high-risk.

2. **Advanced modules still mix models, analysis, persistence, and reporting.**

   `workflow.py` is about 981 lines, `review_packets.py` 775, `sync.py` 754,
   and several other modules remain feature-complete but dense. They are
   dogfoodable, but should not be expanded without extraction tests.

3. **Historical docs and reports are noisy enough to confuse new maintainers.**

   `reports/index.md` now correctly marks v3.0 reports as current, but it
   indexes 215 Markdown reports. Search results still surface v0/v1/v2
   historical findings beside current v3 guidance.

4. **Notebook coverage lags the product surface.**

   Eight notebooks validate structurally, but they cover early workflows only.
   Evidence graph, claim lifecycle, workflow runner, review packet, rebuild,
   and v3 dogfooding workflows are demonstrated by scripts/tests/docs rather
   than notebooks.

5. **The v3 stable surface is honest but still broad for a first-time user.**

   `paperwb --help` is an inventory, not onboarding. The v3 docs solve this
   reasonably, but the CLI itself still presents 30-plus command groups at once.

## Low-Priority Polish

- `dogfood status` prints absolute project roots; harmless locally, but easy to
  accidentally capture into a committed report.
- `index status --check-files` reports `FTS5 enabled: false` when the index is
  missing; that is technically coherent but can read like a capability failure.
- `validate-bib --strict` does not fail on warning-level findings; docs explain
  this, but strict-mode expectations vary.
- Some commands use `--out`, others `--output`, `--report`,
  `--reports-dir`, or `--force-report`; the inconsistency is historical but
  still a usability tax.
- README is clean enough, but the common workflows section still exposes many
  experimental paths before users need them.

## Data-Safety Risks

- No tracked PDFs, copied full text, SQLite/cache DBs, backup archives, audit
  logs, `.paperwb` state, Python caches, `.DS_Store`, `build/`, `dist/`, or
  egg-info artifacts were found.
- `.gitignore` covers `.paperwb/`, nested `.paperwb/`, rebuild metadata,
  SQLite/database files, backups, audit logs, scratch/tmp, stress outputs,
  hostile-review drafts, and PDFs.
- The data-safety audit passed with 746 files checked, 0 errors, and 0 warnings.
- Residual risk is operational: users can still generate local reports, audit
  logs, backups, and caches in project folders. Most are ignored or force-gated,
  but maintainers must continue to inspect `git status --ignored` before
  commits.

## Docs Mismatches

- Public import examples should consistently show `--report scratch/...` for
  dry-run imports. The command help is accurate, but users coming from the
  common workflow examples will not know that `--out` is invalid and
  `--reports-dir` is rejected with `--project`.
- v3 docs are current, but older v2 and lowercase docs remain prominent in the
  tree for historical/site-source reasons. They are not wrong, but they are easy
  to mistake for the current release-candidate path.
- `docs/COMMAND_CONTRACTS_V3.md` labels core `export` as partly stable, but the
  practical distinction between stable core exports and advanced experimental
  outputs is still mostly prose, not command-level subcommand grouping.

## CLI Usability Issues

- Import dry-run output routing is the roughest current UX point.
- `paperwb --help` is long enough that users need the docs to know where to
  start.
- Experimental command groups are correctly labelled, but users can still run
  them without seeing the stability warning unless they read v3 docs.
- Path override rejection with `--project` is good for safety, but it makes
  temporary-output smoke testing less obvious for commands that use
  `--reports-dir` rather than exact output paths.

## Overengineering Risks

- The repository now includes graph analytics, claim lifecycle, contradiction
  tracking, workflow recipes, review packets, rebuild metadata, sync planning,
  file ingestion, dashboard next actions, reading sessions, rules, and
  manuscript QA. All are local-first, but the cognitive load is high.
- Do not add another major subsystem before real dogfooding. The next work
  should reduce friction, clarify docs, and retire or hide confusing historical
  artifacts.
- Keep graph exports, claim lifecycle sidecars, workflow recipes, review-packet
  comments, sync apply, indexed search, and rebuild metadata experimental until
  a real project proves their contracts.

## Stale Generated Reports

- `reports/index.md` is current for v3.0rc.
- `reports/hostile_review_latest.md` was stale v2.6 content before this review
  and is now refreshed.
- Historical reports intentionally remain. Some old ignored hostile-review
  drafts contain absolute-path evidence and should stay ignored archival
  material, not release guidance.
- The v3 report bundle exists and includes release notes, data safety, external
  dogfooding simulation, release readiness, final verdict, and post-v3 roadmap.

## Missing Tests

- No test currently proves the README/common import dry-run command writes only
  to a caller-selected `--report` path.
- CI notebook checks are structural. That is acceptable for speed, but optional
  notebook execution is not a regular gate.
- There is no single "README transcript" test that pastes the public quickstart
  end to end.
- Experimental command coverage is broad but not exhaustive; not every
  experimental command has help, happy-path, failure-path, and no-overwrite
  contract tests.

## Recommended Blocker-Fix Sequence

There are no release blockers to fix before local dogfooding.

Recommended high-priority sequence:

1. Update README/import docs to route dry-run import reports with `--report
   scratch/import_zotero_dry_run.md --force`.
2. Add a regression test for that documented import dry-run path.
3. Add a pasteable README/quickstart transcript test using `clean_demo` and
   temporary outputs.
4. Keep v3.0rc stable/experimental docs as the source of truth and avoid adding
   new subsystems before real dogfooding feedback.
5. Defer any broad `cli.py` split until the v3 stable command contracts are
   explicitly preserved by tests.
