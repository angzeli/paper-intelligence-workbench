# Hostile Maintainer Review: Current Repository

Date: 2026-06-18

Scope: standalone release-gate review of Paper Intelligence Workbench v3.3 as
if deciding whether this version is safe for local dogfooding. I inspected
package architecture, CLI behavior, stable versus experimental surface docs,
registry and BibTeX workflows, notes and claims, evidence maps,
manuscript/draft QA, reading sessions, imports/exports, sync/conflict planning,
search/indexing, backup/migration/integrity, rule engine, dashboard, evidence
graph, claim lifecycle, workflow runner, collaboration/review packets,
performance/incremental rebuilds, compatibility/migration behavior, support
bundles, quality gates, tests, docs, notebooks, reports, synthetic data,
data-safety boundaries, `.gitignore`, and git status.

## Release Verdict

**Ready for local dogfooding, but not ready to claim strict v3.3 release
validation from this local environment.**

I found no product release blockers that should prevent local dogfooding. The
package imports as `3.3`, the full test suite passes, stable registry/BibTeX
validation works on the clean synthetic project, read-only diagnostics behave
as expected, support bundles are safe by default, compatibility inspection
detects historical and malicious workspace shapes, notebook checks pass, and
the strict data-safety audit reports no tracked findings.

The major concern is release-process integrity: the documented strict quality
gate cannot run to completion in this interpreter because Ruff is missing and
the local build backend import fails. The repository records a v3.3 quality-gate
report using `--allow-missing-tools`, which is transparent, but it is not the
same thing as a strict release gate. That is a high-priority release-readiness
issue, not a data-loss blocker.

Post-review fix status: addressed in the follow-up pass by adding an explicit
`local-diagnostic` target, rejecting `release --allow-missing-tools`, and
regenerating the v3.3 quality/readiness reports so skipped tool-backed checks
are not described as a strict release-gate pass.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead
  13]`; no tracked modifications before writing this report; ignored local
  caches, build outputs, project caches, backups, and dogfood artifacts were
  present.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `3.3`.
- `paperwb --help`: passed.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`:
  passed with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry
  projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb doctor --project clean_demo --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed and reported
  zero BibTeX, citation, workspace, rule, manuscript, graph, and claim-review
  findings.
- `paperwb integrity check --project clean_demo --strict --out <tmp> --force`:
  passed with 0 errors and 0 warnings.
- `paperwb support bundle --project clean_demo --out <tmp> --force`: passed
  and wrote 13 generated diagnostic files.
- `paperwb support bundle --project clean_demo --safe --verbose-local-only
  --out <tmp>`: rejected with argparse exit code 2.
- `paperwb support redact-preview --project clean_demo --out <tmp> --force`:
  passed.
- `paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data`:
  passed and detected a legacy data workflow requiring migration.
- `paperwb compatibility inspect
  tests/fixtures/workspaces/path_traversal_workspace --strict`: failed as
  expected with `project_profile_path_escape`.
- `paperwb graph summary --project clean_demo --out <tmp> --force`: passed.
- `paperwb rebuild plan --project clean_demo --out <tmp> --force-report`:
  passed.
- `paperwb rules report --project clean_demo --out <tmp> --force`: passed.
- `paperwb workflow list`: passed and listed the built-in recipes.
- `paperwb workflow run daily_check --project clean_demo --dry-run --out
  <tmp> --force`: passed with 5 steps, 0 errors, 0 warnings.
- `paperwb draft audit drafts/synthetic_good_section.md --project clean_demo
  --out <tmp> --force`: passed.
- `paperwb manuscript qa drafts/synthetic_good_section.md --project clean_demo
  --out <tmp> --force`: passed.
- `paperwb sync plan --source data/examples/zotero_export.csv --source-type
  zotero-csv --project clean_demo --out <tmp> --json-out <tmp> --force`:
  passed with 3 actions and 0 conflicts.
- `paperwb import zotero-csv data/examples/zotero_export.csv --project
  clean_demo --dry-run --report <tmp> --force`: passed with 5 rows read, 3
  imported, 0 updated, 2 skipped, dry-run true.
- `paperwb review-packet create --project clean_demo --theme clean-theme --out
  <tmp> --force`: passed, produced `Items: 0`, and reported `Includes PDFs:
  false`.
- `python -m pytest -q`: passed.
- `python -m mypy scripts --config-file pyproject.toml`: passed.
- `python scripts/smoke_cli_workflow.py --quick --out <tmp>`: passed with 14
  steps and 0 failures.
- `python scripts/validate_notebooks.py`: passed and validated 8 notebooks.
- `python scripts/check_notebooks.py`: passed and checked 8 notebooks.
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 833
  repository files with 0 errors and 0 warnings.
- `python scripts/run_quality_gate.py release --out <tmp>`: failed at Ruff
  lint because the Python module `ruff` is unavailable locally.
- `python scripts/run_quality_gate.py release --allow-missing-tools --out
  <tmp>`: passed with 3 skipped steps: Ruff lint, Ruff format check, and build
  distributions.
- `python -m ruff --version`: failed because Ruff is not installed in the
  current interpreter.
- `python -c "import setuptools.build_meta"`: failed because the local
  setuptools import chain cannot import `backports.tarfile`.

## Release Blockers

None found for local dogfooding.

## High-Priority Issues

1. **The strict v3.3 quality gate is not locally enforceable in the current
   environment.**

   Evidence: `python scripts/run_quality_gate.py release --out <tmp>` fails on
   the first step with `missing Python module: ruff`. The build preflight also
   fails because `setuptools.build_meta` cannot import `backports.tarfile` in
   this interpreter. The checked-in `reports/quality_gate_v3_3.md` and the
   local rerun with `--allow-missing-tools` both skip Ruff lint, Ruff format
   check, and distribution build while still exiting successfully.

   Impact: product dogfooding can proceed, but maintainers cannot honestly
   claim a strict local v3.3 release validation from this environment. CI may
   install `.[dev]` and pass, but the local release-readiness docs say the
   strict gate should be used for release validation.

   Recommended fix: make the local release-gate contract explicit. Either make
   the dev bootstrap path reliable enough that `python scripts/run_quality_gate.py
   release` passes locally, or split the commands into a strict CI/release gate
   and a clearly named bootstrap diagnostic gate. Keep `--allow-missing-tools`
   out of release-verdict language unless the skipped steps are explicitly
   called non-blocking.

   Post-review status: fixed by splitting skipped-tool runs into
   `local-diagnostic` and rejecting `release --allow-missing-tools`. The strict
   release gate still requires Ruff/build tooling to be available locally or in
   CI.

## Medium-Priority Issues

1. **`docs/STABLE_SURFACE_V3.md` still describes the stable surface as v3.2.**

   Evidence: the file begins with `v3.2 keeps the stable dogfooding surface...`
   while `pyproject.toml`, `paper_workbench.__version__`, and current reports
   identify the repo as v3.3.

   Impact: this is not a runtime failure, but it undermines the stable-surface
   freeze that v3 docs are supposed to provide.

2. **`paper_workbench/cli.py` remains the largest maintainability risk.**

   Evidence: `paper_workbench/cli.py` is 3,936 lines and owns parser setup,
   command dispatch, path handling, output writes, safety flags, and audit
   events across many command groups.

   Impact: behavior is covered by tests and smoke checks, but future changes
   are likely to repeat flag, overwrite, and project-resolution semantics
   unless CLI helpers keep being extracted carefully.

3. **Review-packet creation succeeds with an empty selection.**

   Evidence: `paperwb review-packet create --project clean_demo --theme
   clean-theme --out <tmp> --force` exited successfully with `Items: 0`.

   Impact: this is experimental and does not modify evidence, but it can create
   a formally valid packet that contains nothing useful for a collaborator. Add
   a warning, `--allow-empty`, or strict-mode failure before promoting review
   packets.

4. **The quality-gate skip mode can be mistaken for release validation.**

   Evidence: `--allow-missing-tools` skips missing lint, format, and build
   checks and still exits 0. The generated report records those skips, but the
   successful exit code is easy to misuse in automation.

   Impact: this is acceptable for bootstrap diagnostics, but dangerous if used
   as the release command. CI should continue running strict checks without
   this flag.

5. **Generated report inventory remains noisy.**

   Evidence: `reports/index.md` indexes 231 Markdown reports and keeps current
   v3.3 reports alongside historical v0-v3 release-burn artifacts.

   Impact: provenance is valuable, but new maintainers still need a clearer
   first-page route to current evidence. Avoid deleting history, but keep the
   report index current and consider grouping historical reports more strongly.

## Low-Priority Polish

- `paperwb --help` is an inventory, not a guided workflow. The docs carry the
  onboarding burden.
- Output flags remain inconsistent across command groups: `--out`, `--report`,
  `--reports-dir`, `--json-out`, `--force`, and `--force-report`.
- Historical v2 and release-candidate docs are still searchable and can
  distract from the v3 docs.
- `run_quality_gate.py` terminal summaries are concise; the Markdown report has
  the better explanation. Users who do not open the report may miss the exact
  remediation.
- Public Python API boundaries are documented, but most modules remain
  importable without private naming.

## Data-Safety Risks

- No tracked PDFs, SQLite/cache DBs, backup archives, audit logs, `.idea`
  files, `.paperwb` state, Python caches, `.DS_Store`, `build/`, `dist/`, or
  egg-info artifacts were found by tracked-file checks.
- `.gitignore` covers `.paperwb/`, nested `.paperwb/`, rebuild metadata,
  SQLite/database files, backups, audit logs, scratch/tmp, stress outputs,
  historical hostile-review drafts, and PDFs.
- The strict data-safety audit checked 833 repository files and reported 0
  errors and 0 warnings.
- The generated safe support bundle contained diagnostic summaries, sanitized
  samples, and manifests; it did not copy PDFs, cache DBs, backup archives, or
  raw audit logs.
- Residual risk: ignored local artifacts are present from dogfooding and smoke
  checks. They are ignored, but release packaging should start from a clean
  clone or run the data-safety audit before building artifacts.

## Docs Mismatches

- `docs/STABLE_SURFACE_V3.md` has stale v3.2 wording.
- `docs/QUALITY_GATE.md` and `docs/RELEASE_VALIDATION.md` correctly tell
  maintainers to use the strict release gate, but `reports/quality_gate_v3_3.md`
  records a skipped-tool run. The mismatch is transparent but should be
  resolved before calling v3.3 release-ready.
- `reports/hostile_review_latest.md` was stale v3.2 content before this review
  and is now refreshed.
- Historical docs and reports remain extensive. Current users should start with
  `README.md`, `docs/GETTING_STARTED_V3.md`, `docs/STABLE_SURFACE_V3.md`,
  `docs/CLI_REFERENCE_V3.md`, and `docs/QUALITY_GATE.md`.

## CLI Usability Issues

- Empty review packets are too easy to create.
- First-run terminal help is too broad to function as a guided workflow.
- Safety-sensitive commands use different names for dry-run, force, and output
  flags.
- Quality-gate failures are precise in the Markdown report, but the terminal
  summary is terse.
- Compatibility inspection output is useful, but approximate version labels
  need to stay documented as heuristic.

## Overengineering Risks

- The repository now includes project templates, dogfood scaffolds, registry and
  BibTeX validation, structured notes and claims, citation audits, evidence
  maps, manuscript QA, reading sessions, imports/exports, sync planning, local
  search/indexing, backup/migration/integrity, rules, dashboard, evidence graph,
  claim lifecycle, workflow recipes, review packets, support bundles,
  compatibility inspection, incremental rebuilds, and a quality gate.
- Do not add another major subsystem before real dogfooding generates concrete
  bugs. The next work should tighten contracts, reduce CLI repetition, and
  improve current workflow ergonomics.
- Keep graph exports, claim lifecycle sidecars, workflow recipes,
  review-packet imports, sync apply, indexed search, rebuild metadata, verbose
  support bundles, and forced migration/restore flows experimental until real
  projects prove their contracts.

## Stale Generated Reports

- `reports/hostile_review_latest.md` was stale v3.2 content before this review.
- `reports/quality_gate_v3_3.md` is current but should not be read as a strict
  gate pass because it skipped missing tools.
- Historical v0/v1/v2/v3.0rc/v3.1/v3.2 reports intentionally remain. They are
  useful for provenance but should not be treated as current release guidance.
- Ignored historical hostile-review drafts remain excluded by `.gitignore` and
  should stay archival.

## Missing Tests

- No test asserts that v3 stable-surface docs use the current package version
  label.
- No test asserts that empty review-packet selections warn, fail, or require an
  explicit `--allow-empty`.
- There is no single README transcript test that executes the public quickstart
  exactly as written.
- Notebook checks are structural. That is reasonable for speed, but advertised
  notebooks are not executed as a normal release gate.
- The quality-gate script has integration coverage through smoke use, but no
  focused test around skipped-tool semantics versus strict release semantics.

## Recommended Blocker-Fix Sequence

There are no product release blockers before local dogfooding.

Recommended next sequence:

1. Fix the high-priority release-process issue: make strict local quality-gate
   validation installable and enforceable, or rename/document skipped-tool mode
   so it cannot be mistaken for release readiness.
2. Update `docs/STABLE_SURFACE_V3.md` from v3.2 wording to v3.3 and add a small
   regression check that v3 surface docs match the package version line.
3. Add a warning or explicit `--allow-empty` flow for empty review packets.
4. Add a README quickstart transcript smoke test.
5. Keep splitting CLI helpers only where behavior is already pinned by command
   tests; do not do a large CLI rewrite before more real dogfooding.
