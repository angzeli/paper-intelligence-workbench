# Hostile Maintainer Review: Current Repository

Date: 2026-06-16

Scope: standalone release-gate review of Paper Intelligence Workbench v2.6 as if
deciding whether this version is safe for local dogfooding. I inspected package
architecture, CLI behavior, stable versus experimental surface docs, registry
and BibTeX workflows, notes and claims, evidence maps, manuscript/draft QA,
reading sessions, imports/exports, sync/conflict planning, search/indexing,
backup/migration/integrity, rule engine, dashboard, evidence graph, claim
lifecycle, workflow runner, collaboration/review packets, performance and
incremental rebuilds, tests, docs, notebooks, reports, synthetic data,
data-safety boundaries, `.gitignore`, and git status.

## Release Verdict

**Ready for cautious local dogfooding as v2.6.**

I did not find a release blocker. The package imports as `2.6`, `paperwb --help`
loads, the clean first-run project validates without findings, the full test
suite passes, notebooks validate and execute with the repository's lightweight
runner, and the data-safety audit reports zero errors/warnings. Representative
stable and experimental CLI workflows completed without tracebacks.

This is still not a polished public release. The product surface is very broad,
the CLI remains oversized, generated reports are noisy, and some dry-run
workflows still create local report artifacts by default. Those are dogfooding
risks, not release blockers.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead 41]`; only ignored local artifacts before writing this report.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: `2.6`.
- `paperwb --help`: passed and listed current command groups.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed with zero BibTeX, citation, workspace, rule, manuscript, and graph findings.
- `paperwb validate-registry projects/zis_photocatalysis/registry.csv --strict`: passed with no findings.
- `paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict`: passed with one expected sparse synthetic-entry warning.
- `paperwb rebuild plan --project zis_photocatalysis`: passed and emitted valid project-profile recommendations.
- `paperwb workflow run daily_check --project zis_photocatalysis --dry-run --out <tmp> --force`: passed with expected synthetic fixture errors/warnings.
- `paperwb sync plan --project zis_photocatalysis --source data/examples/zotero_export.csv --source-type zotero-csv --out <tmp> --force`: passed and wrote JSON beside the explicit Markdown output.
- `paperwb manuscript qa drafts/synthetic_good_section.md --project zis_photocatalysis --out <tmp> --force`: passed.
- `paperwb graph summary --project zis_photocatalysis`: passed.
- `paperwb review-packet create --project zis_photocatalysis --theme photocorrosion --out <tmp> --force`: passed and excluded PDFs.
- `paperwb reading queue --project zis_photocatalysis`: passed.
- `paperwb rules run --project zis_photocatalysis --strict`: returned non-zero with expected synthetic evidence-gap rule findings.
- `paperwb integrity check --project clean_demo --out <tmp> --force`: passed with zero errors/warnings.
- `paperwb backup create --project clean_demo --backups-dir <tmp> --notes review-smoke`: passed and wrote outside the repo.
- `paperwb migrate plan --to-project review_migration_probe --out <tmp> --force`: passed.
- `paperwb search photocorrosion --project zis_photocatalysis`: passed.
- `paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --force`: passed but created a default project-local import report; the temporary review artifact was removed.
- `python scripts/data_safety_audit.py --out <tmp>`: checked 725 repository files with 0 errors and 0 warnings.
- `python scripts/validate_notebooks.py`: validated 8 notebooks.
- `python scripts/validate_notebooks.py --execute`: executed 8 notebooks with the lightweight runner.
- `python -m pytest -q`: passed.
- `git ls-files` scan found no tracked PDFs, SQLite/cache DBs, backup archives, audit logs, `.paperwb` directories, Python caches, `.DS_Store`, `build/`, or `dist/` artifacts.

## Release Blockers

None found.

## High-Priority Issues

None found.

## Medium-Priority Issues

1. **Dry-run import still creates project-local report churn by default.**

   Evidence: `paperwb import zotero-csv ... --project zis_photocatalysis --dry-run --force` wrote
   `projects/zis_photocatalysis/reports/import_zotero_csv.md` when no explicit
   `--report` was supplied.

   Why it matters: this is not data-destructive and does not write registry
   rows, but "dry-run" reads as no project mutation to many users. In a
   dogfooding repo, it can create untracked report files unless users know to
   pass `--report <tmp>` or route reports elsewhere.

   Recommended fix: either document the default report write more prominently in
   import docs and examples, or change dry-run imports to print by default unless
   `--report` or `--reports-dir` is supplied.

2. **`paper_workbench/cli.py` remains a maintainability hotspot.**

   The CLI is still roughly 3,785 lines and coordinates argument parsing,
   project path resolution, write preflights, audit events, report writing, and
   dispatch for nearly every subsystem. v2.6 added useful helper consolidation,
   but this module is still the highest-risk place to make future changes.

3. **Several feature modules still combine too many responsibilities.**

   `workflow.py`, `rules.py`, `authoring.py`, `index.py`, `review_packets.py`,
   `reading.py`, `sync.py`, `graph.py`, `drafts.py`, `registry.py`, and
   `importers.py` mix models, analysis, persistence, and Markdown rendering.
   They are dogfoodable, but future patches should avoid expanding them further
   without extracting stable helper seams.

4. **The v2.6 release bundle lacks a current checked-in data-safety report.**

   A data-safety smoke audit passed during this review, but the current v2.6
   report set includes architecture/refactor/readiness reports, not a
   `reports/data_safety_*_v2_6.md` artifact. That is acceptable for an internal
   architecture patch, but weaker than prior release-candidate bundles.

5. **Report archaeology is now a real usability problem.**

   `reports/index.md` indexes 209 Markdown reports. It correctly separates the
   current v2.6 reports from historical artifacts, but search results still mix
   live guidance with old v0.x/v1.x/v2.0rc findings. New maintainers can easily
   read stale historical output as current status.

## Low-Priority Polish

- `paperwb --help` is intimidating for the target undergraduate/researcher
  persona despite stable/experimental guidance at the bottom.
- README is clean, but still advertises many advanced workflows before the
  minimum daily loop is obvious.
- `dogfood status` prints an absolute project root in terminal output; harmless
  locally, but easy to capture into a committed report by accident.
- `validate-bib --strict` exits 0 for warnings. This is defensible, but CI users
  may expect strict mode to fail on warnings unless docs are explicit.
- Many report modules still carry local `_escape` helpers after v2.6; migrate
  only when touching those reports for other reasons.

## Data-Safety Risks

- No tracked PDFs, copied paper full text, SQLite/cache DBs, backup archives,
  audit logs, `.paperwb` cache state, Python caches, `.DS_Store`, `build/`, or
  `dist/` artifacts were found.
- `.gitignore` covers `.paperwb/`, nested `.paperwb/`, rebuild metadata,
  SQLite/database files, backups, audit logs, scratch/tmp, stress outputs,
  hostile-review drafts, and PDFs.
- The data-safety audit passed with 0 errors and 0 warnings.
- The main residual data-safety risk is accidental local-output churn in tracked
  project folders, especially dry-run import reports or user-captured CLI output
  containing absolute paths.

## Docs Mismatches

- `reports/release_readiness_v2_6.md` says v2.6 is ready assuming tests and
  smoke checks pass. They did pass in this review, but the release-readiness
  report itself was not regenerated after this validation.
- Import docs are technically accurate, but they under-emphasize that dry-run
  import writes a Markdown report by default unless users choose `--report` or
  `--reports-dir`.
- The docs now include v2.6 internal architecture guidance, but the main user
  docs still use v2 naming. That is fine for the v2 line, but v3.0rc should
  create a cleaner `GETTING_STARTED_V3`/surface set instead of stretching v2
  docs further.

## CLI Usability Issues

- Dry-run import report output is surprising because most other "plan" commands
  route explicit outputs more visibly.
- `rules run --strict` returns non-zero on `zis_photocatalysis`, which is
  correct for the intentionally imperfect fixture but still easy to confuse with
  an install failure.
- The command surface is broad enough that `paperwb --help` is better as a
  command inventory than an onboarding path.
- Some commands use `--out`, others use `--output`, others use `--report`; the
  inconsistency is historical and manageable, but it remains a new-user tax.

## Overengineering Risks

- The project now includes many adjacent systems: local graph, claim lifecycle,
  contradiction tracking, workflow runner, review packets, rebuild metadata,
  sync planning, file ingestion, dashboard actions, reading sessions, rules, and
  manuscript QA. All are local-first, but the cognitive load is high.
- Do not add another major subsystem before v3.0rc. The next release should
  classify, freeze, and simplify the surface, not expand it.
- Keep graph exports, claim lifecycle sidecars, workflow recipes, review-packet
  comments, sync apply, and rebuild metadata experimental until real dogfooding
  proves their schemas.

## Stale Generated Reports

- `reports/index.md` is current for v2.6.
- `reports/hostile_review_latest.md` was stale v2.5 content before this review
  and is now refreshed.
- Historical reports intentionally remain. Some old reports contain absolute
  path examples under allowlist; they should be treated as archival evidence, not
  current release guidance.
- No current v2.6 data-safety report is checked in, although the smoke audit
  passed during review.

## Missing Tests

- No test asserts that dry-run import without `--report` avoids project-local
  churn or clearly reports the default output location.
- CI-style notebook validation is structural; optional notebook execution passed
  here but is not clearly part of the regular release gate.
- There is still no automated "README command transcript" test to prove the
  public quickstart remains pasteable end to end.
- Command contract coverage is strong for many groups, but the surface is too
  large to claim every experimental command has a happy path, failure path, and
  non-destructive behavior test.

## Recommended Blocker-Fix Sequence

There are no blockers to fix before local dogfooding.

Recommended next sequence before v3.0rc:

1. Decide whether dry-run imports should default to stdout/no-write or keep
   writing reports; document and test the chosen behavior.
2. Add a pasteable README/quickstart transcript test using `clean_demo` and
   temporary output paths.
3. Generate a v3 release-candidate data-safety report as a checked-in artifact.
4. Freeze stable/experimental/deprecated command groups and schemas for v3.
5. Defer any broad CLI split until v3 command-contract tests are current.
