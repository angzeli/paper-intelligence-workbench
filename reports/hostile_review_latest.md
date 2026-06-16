# Hostile Maintainer Review: Current Repository

Date: 2026-06-16

Scope: standalone release-gate review of Paper Intelligence Workbench v2.5 as if
deciding whether it is safe for local dogfooding. I inspected package
architecture, CLI behavior, stable versus experimental surface docs, registry
and BibTeX workflows, notes and claims, evidence maps, manuscript/draft QA,
reading sessions, imports/exports, sync/conflict planning, search/indexing,
backup/migration/integrity, rule engine, dashboard, evidence graph, claim
lifecycle, workflow runner, collaboration/review packets, performance and
incremental rebuilds, tests, docs, notebooks, reports, synthetic data,
data-safety boundaries, `.gitignore`, and git status.

## Release Verdict

**Ready for cautious local dogfooding after the follow-up blocker-fix pass.**

The repository is broadly healthy: package import works, `paperwb --help`
loads, full pytest passes, notebooks validate structurally, the data-safety
audit reports zero errors/warnings, and representative CLI workflows run without
Python tracebacks. The local-first boundaries are still intact: no tracked PDFs,
SQLite/cache DBs, backup archives, audit logs, `.paperwb` sidecars, or Python
caches were found.

The original review found one release blocker and three high-priority issues.
The follow-up fix pass addressed them without expanding scope: rebuild
recommendations now emit valid project-profile commands, sync JSON output follows
explicit `--out` placement, rebuild write-path docs mention audit logging, and a
minimal clean synthetic project is available for first-run validation. The
detailed findings below are retained as traceability for what was fixed.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead 33]`; only ignored local artifacts before writing this report.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: `2.5`.
- `python -m paper_workbench.cli --help`: passed and listed `rebuild`.
- `python -m paper_workbench.cli validate-registry projects/zis_photocatalysis/registry.csv --strict`: passed with no findings.
- `python -m paper_workbench.cli validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict`: passed with one existing sparse synthetic-entry warning.
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --no-audit-log`: passed and reported expected synthetic evidence gaps.
- `python -m paper_workbench.cli rebuild status --project zis_photocatalysis`: passed and reported all rebuild targets stale because metadata/index are absent.
- `python -m paper_workbench.cli rebuild plan --project zis_photocatalysis`: passed but emitted an invalid `report all` recommendation.
- `python -m paper_workbench.cli report all --project zis_photocatalysis --reports-dir projects/zis_photocatalysis/reports --force`: failed with the expected CLI rejection, proving the rebuild recommendation is invalid.
- `python -m paper_workbench.cli workflow run daily_check --project zis_photocatalysis --dry-run --out <tmp> --force`: passed with expected synthetic fixture errors/warnings.
- `python -m paper_workbench.cli import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --force`: passed, but wrote a default project-local import report.
- `python -m paper_workbench.cli sync plan --project zis_photocatalysis --source data/examples/zotero_export.csv --source-type zotero-csv --out <tmp> --force`: passed, but also wrote default project-local `sync_plan.json`.
- `python -m paper_workbench.cli manuscript qa drafts/synthetic_good_section.md --project zis_photocatalysis --out <tmp> --force`: passed.
- `python -m paper_workbench.cli reading queue --project zis_photocatalysis`: passed.
- `python -m paper_workbench.cli followups list --project zis_photocatalysis`: passed.
- `python -m paper_workbench.cli integrity check --project zis_photocatalysis --out <tmp> --force`: passed with expected synthetic fixture findings.
- `python -m paper_workbench.cli review-packet create --project zis_photocatalysis --theme photocorrosion --out <tmp> --force`: passed and excluded PDFs.
- `python -m paper_workbench.cli workflow list/show`: passed.
- `python -m paper_workbench.cli rules run --project zis_photocatalysis --strict`: returned non-zero with expected synthetic evidence-gap rule findings.
- `python -m paper_workbench.cli graph summary --project zis_photocatalysis`: passed.
- `python scripts/data_safety_audit.py`: checked 706 repository files with 0 errors and 0 warnings.
- `python scripts/validate_notebooks.py`: validated 8 notebooks.
- `python -m pytest -q`: passed.
- `git ls-files` scan found no tracked PDFs, SQLite/cache DBs, backup archives, audit logs, `.paperwb` directories, or Python caches.

## Release Blockers

None remaining after the follow-up fix pass.

Fixed finding:

1. **`rebuild plan` emitted an invalid command for project report rebuilds.**

   Evidence: `paper_workbench/rebuild.py:300` builds this recommendation:
   `paperwb report all --reports-dir projects/zis_photocatalysis/reports --project zis_photocatalysis`.
   The CLI rejects `--project` combined with `--reports-dir` by design, and the
   probe returned: `error: --project cannot be combined with --reports-dir; project profile paths are used instead.`

   Why it matters: v2.5 is specifically about rebuild planning and repeated
   workflow predictability. A generated next action must be executable. This is
   not data-destructive, but it breaks the headline workflow and undermines user
   trust in generated recommendations.

   Fix applied: project-profile rebuild recommendations now use the valid
   `paperwb report all --force --project PROJECT` form and regression tests
   execute the emitted report recommendation.

## High-Priority Issues

All high-priority findings were addressed in the follow-up fix pass. Original
findings are retained below for traceability.

1. **`sync plan --out <path>` still writes a second default JSON file under the project.**

   Evidence: `paper_workbench/cli.py:2192-2196` defaults `json_path` to the
   project reports directory when `--json-out` is omitted, even if `--out`
   points elsewhere. The probe wrote the Markdown report to a temporary path and
   still created `projects/zis_photocatalysis/reports/sync_plan.json`.

   Why it matters: sync planning is explicitly sold as dry-run-first and
   non-destructive. Writing a project-local JSON artifact by default is not data
   loss, but it is surprising file churn and violates the expectation that an
   explicit output path controls where generated artifacts go.

   Fix applied: when `--out` is supplied and `--json-out` is omitted, the JSON
   plan is written beside the Markdown output. The CLI help, sync docs, and
   regression tests now cover this behavior.

2. **`rebuild run` is documented as metadata-only, but CLI audit logging adds another write path.**

   Evidence: `docs/COMMAND_CONTRACTS_V2.md` says `rebuild` writes only
   `.paperwb/rebuild_metadata.json`, while `cmd_rebuild_run` also records an
   audit event through `_record_audit_event`.

   Why it matters: audit logs are ignored and expected elsewhere, so this is not
   unsafe. It is still a contract mismatch in a patch whose purpose is cache and
   write-path clarity.

   Fix applied: rebuild docs now state that `rebuild run` writes rebuild
   metadata and the normal ignored local audit-log event.

3. **There is no green-path bundled project for first-run validation.**

   Evidence: the main bundled `zis_photocatalysis` project intentionally emits
   dashboard, rule, integrity, citation-audit, and rebuild warnings/errors. Docs
   explain the imperfection, but this project remains the dominant example in
   README and smoke workflows.

   Why it matters: the imperfect fixture is good for demos, but new users also
   need one tiny clean project where stable commands return clean results. That
   separates installation confidence from evidence-gap demonstration.

   Fix applied: `projects/clean_demo` is now a minimal clean synthetic project,
   and public quickstarts use it for first-run validation while preserving
   `zis_photocatalysis` as the warning-rich teaching fixture.

## Medium-Priority Issues

1. **`paper_workbench/cli.py` is still too large.**

   The CLI is roughly 3,777 lines and owns parser setup, dispatch, path
   resolution, report writing, workflow glue, and error handling for almost
   every subsystem. It works, but every new command increases review risk.

2. **Several feature modules are doing too much.**

   Large modules such as `workflow.py`, `rules.py`, `authoring.py`, `index.py`,
   `review_packets.py`, `reading.py`, `sync.py`, `graph.py`, `drafts.py`,
   `registry.py`, and `importers.py` combine models, analysis, persistence, and
   Markdown rendering. This is manageable for dogfooding but weak for long-term
   maintainability.

3. **Generated reports are now a navigation burden.**

   `reports/index.md` is useful, but the repo has over 200 Markdown reports,
   including old hostile reviews and historical release artifacts. Search
   results mix current v2.5 guidance with old v0.x/v1.x/v2.0rc findings.

4. **Notebooks lag behind the current feature set.**

   Eight notebooks validate structurally, but newer workflows such as review
   packets, workflow runner, claim lifecycle, evidence graph, dogfood, and
   rebuild are primarily covered by examples/tests/docs rather than notebooks.

5. **Strict-mode semantics remain easy to misunderstand.**

   `validate-bib --strict` exits 0 for warnings. That is defensible if strict
   means "error findings fail", but it is not obvious to CI users.

## Low-Priority Polish

- README is clean but long; the first screen still advertises many advanced
  workflows before the minimum daily workflow becomes obvious.
- `reports/index.md` should probably separate "current examples" from
  "historical audit archaeology" more aggressively.
- The package has no runtime dependencies, which is good, but the amount of
  handwritten Markdown/table rendering is becoming repetitive.
- Some docs still use older lowercase duplicates such as `docs/cli-reference.md`
  beside v2 uppercase references; this is tolerable but noisy.

## Data-Safety Risks

- No tracked PDFs, copied paper full text, SQLite/cache DBs, backup archives,
  audit logs, `.paperwb` cache state, or Python caches were found.
- `.gitignore` covers `.paperwb/`, SQLite files, rebuild metadata, backups,
  audit logs, scratch/tmp, stress outputs, and PDFs.
- The current data-safety audit reports 0 errors and 0 warnings.
- The main residual risk is accidental generated-output churn under tracked
  project report folders, especially `sync plan` default JSON output and dry-run
  import reports.

## Docs Mismatches

- `rebuild` command contracts say metadata-cache-only, but audit logging is an
  additional write path.
- `rebuild plan` recommends a command rejected by CLI path-override rules.
- `sync plan` docs emphasize dry-run planning, but the command writes JSON by
  default unless `--json-out` is explicitly controlled.
- Import docs say dry-run does not write the registry, which is true, but they
  under-emphasize that import reports are still written unless output is
  redirected.

## CLI Usability Issues

- `rebuild plan` generated recommendations are not currently safe to paste and
  run.
- `sync plan --out` controls only the Markdown report, not the JSON plan, which
  is surprising.
- The command surface is very large. The stable/experimental docs help, but
  `paperwb --help` is intimidating for the intended undergraduate/researcher
  persona.
- `rules run --strict` returning non-zero on the default demo project is
  correct but easy to misread as installation failure.

## Overengineering Risks

- The project has accumulated many adjacent systems: graph, lifecycle,
  workflow runner, review packets, rebuild metadata, sync planning, local file
  ingestion, and dashboard actions. Most are local and safe, but there is
  significant cognitive load.
- Avoid adding another broad subsystem before v2.6 architecture cleanup.
- Do not promote rebuild metadata, graph exports, review comments, or workflow
  recipes as stable schemas until real project dogfooding validates them.

## Stale Generated Reports

- `reports/index.md` is current for v2.5.
- Historical reports intentionally remain and include old absolute-path
  examples. The current data-safety audit allowlist keeps release checks clean,
  but maintainers still need to know those old reports are archival, not current
  guidance.
- `reports/hostile_review_latest.md` was stale v2.4 content before this review.

## Missing Tests

- No test appears to assert that every `paperwb rebuild plan` recommended
  project-profile command is executable or at least syntactically allowed.
- No test covers `sync plan --out <tmp>` without `--json-out` to prevent
  unrequested project-local JSON output.
- No clean first-run project test exists for "all stable commands return clean
  findings"; current tests mainly validate that commands work on intentionally
  imperfect fixtures.
- Notebook validation is structural; newer feature examples are not notebook-run
  checked.

## Recommended Blocker-Fix Sequence

1. Fix `rebuild plan` project-profile recommendations so generated commands are
   valid, and add regression coverage.
2. Decide and document/fix `sync plan --out` JSON behavior; add a no-surprise
   output-path test.
3. Align rebuild docs with audit-log behavior or remove audit logging from
   `rebuild run`.
4. Add a clean tiny project for first-use green-path validation.
5. Keep v2.6 focused on CLI decomposition, report-rendering helpers, and public
   versus internal API boundaries.
