# Hostile Maintainer Review: Current Repository

Date: 2026-06-22 14:19:33 CST

Scope: standalone release-gate review of the current Paper Intelligence
Workbench repository as if deciding whether this version is safe for local
dogfooding. I inspected package architecture, CLI behavior, stable versus
experimental surface docs, registry and BibTeX workflows, notes and claims,
evidence maps, manuscript/draft QA, reading sessions, imports/exports,
sync/conflict planning, search/indexing, backup/migration/integrity, rule
engine, dashboard, evidence graph, claim lifecycle, workflow runner,
collaboration/review packets, performance/incremental rebuilds, tests, docs,
notebooks, reports, synthetic data, data-safety boundaries, `.gitignore`, and
git status.

## Release Verdict

**Ready for private local dogfooding, not ready for a public push or tag from
this worktree.**

The product surface is dogfoodable: package import works, the CLI loads, full
pytest passes, docs and notebooks validate structurally, the data-safety audit
reports zero findings, and representative stable/safety-sensitive workflows run
without unsafe writes.

The blocker is release hygiene, not core functionality. The worktree contains
pre-existing tracked modifications in source, test, and notebook files. Even
though tests pass, a public release or tag should not be cut from a dirty tree
whose unrelated changes are not reviewed, committed, or intentionally reverted.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead
  6]`; tracked modifications are present in `notebooks/04_project_profiles_workflow.ipynb`,
  several `paper_workbench/*.py` modules, and several tests.
- `git diff --stat`: 11 pre-existing modified files, 190 insertions and 194
  deletions, mostly import cleanup plus one notebook diff.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `3.5`.
- `paperwb --help`: passed and labels stable starting points versus
  experimental or safety-sensitive workflows.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`:
  passed with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry
  projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed and reported
  zero validation, citation, rule, manuscript, graph, and claim-review
  findings.
- `paperwb list --project clean_demo`: passed.
- `paperwb note-template clean_demo_2026 --project clean_demo`: correctly
  refused to overwrite the existing clean-demo note.
- `paperwb report evidence-map --project clean_demo --out <tmp> --force`:
  passed.
- `paperwb support redact-preview --project clean_demo`: passed and redacted
  titles, paths, claim text, quotes/paraphrases, and local PDF paths.
- `paperwb support bundle --project clean_demo --out <tmp> --force`: passed;
  generated 13 diagnostic files and no PDFs, databases, archives, or raw audit
  logs.
- `paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data`:
  passed.
- `paperwb workflow list`: passed.
- `paperwb sync plan --project clean_demo --source data/examples/zotero_export.csv
  --source-type zotero-csv --out <tmp> --json-out <tmp> --strict`: passed with
  3 actions and 0 conflicts.
- `python scripts/check_docs.py`: passed, 188 Markdown files checked.
- `python scripts/validate_notebooks.py`: passed, 8 notebooks validated.
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 866
  repository files with 0 errors and 0 warnings.
- Tracked unsafe-artifact scan for PDFs, cache DBs, backups, audit logs,
  Python caches, `.paperwb`, `.idea`, `.DS_Store`, and build outputs: no
  tracked matches.
- `python -m pytest -q`: passed.
- `python scripts/run_quality_gate.py local-diagnostic --out <tmp>`: passed
  available checks. Ruff lint, Ruff format, and distribution build were
  skipped because optional dev/build modules were not installed in this
  interpreter.

## Release Blockers

1. **Dirty tracked worktree blocks public push, release tag, or public release
   candidate.**

   Current tracked modifications exist in:

   - `notebooks/04_project_profiles_workflow.ipynb`
   - `paper_workbench/cli.py`
   - `paper_workbench/graph.py`
   - `paper_workbench/importers.py`
   - `paper_workbench/index.py`
   - `paper_workbench/migration.py`
   - `paper_workbench/projects.py`
   - `paper_workbench/workflow.py`
   - `tests/test_cli_stress.py`
   - `tests/test_golden_reports.py`
   - `tests/test_v0_2_validation.py`

   The diffs appear to be small import cleanup plus notebook churn, but they
   are still tracked source/test/notebook changes outside this review report.
   They must be reviewed and either committed intentionally or removed before
   public push/tag decisions.

## High-Priority Issues

1. **Version story is confusing for a public audience.**

   Package metadata is `3.5`, current readiness reports include v3.5 and
   v3.0rc2 labels, and the README explains this. That is workable for private
   dogfooding, but confusing for an external public push unless the maintainer
   states clearly whether the release line is `3.5` or `v3.0rc2`.

2. **The `note-template` first-use path is safe but awkward.**

   The clean demo already has a note, so `paperwb note-template
   clean_demo_2026 --project clean_demo` refuses to overwrite it. The refusal
   is correct, but public docs and cookbook examples should steer new users to
   either an empty dogfood project or an explicit `--output scratch/...` path
   when demonstrating note-template generation.

3. **Strict release validation was not completed locally.**

   `local-diagnostic` passed, but Ruff lint/format and build checks were
   skipped because optional dev/build tooling was not installed. CI installs
   `.[dev]`, so this is not a product blocker. It is a high-priority release
   process issue before any tag or public push claim.

## Medium-Priority Issues

1. **`paper_workbench/cli.py` remains a high-change-risk module.**

   The CLI file is 4,046 lines and owns parser setup, command dispatch, output
   preflight, project resolution, safety flags, and many workflow-specific
   behaviors. Tests currently protect it, but future changes can easily create
   inconsistent force/dry-run/output behavior.

2. **Reports directory is historically useful but noisy.**

   `reports/index.md` now indexes 245 Markdown reports. The report policy is
   documented, but old v0/v1/v2/v3 reports remain in the root reports folder.
   This is defensible provenance, but it is not a clean public landing
   experience.

3. **v3.0rc2 reports are classified as historical by the generated report
   index.**

   The report-index generator keys off semantic version-like report names and
   treats v3.5 as current. The v3.0rc2 cleanup reports are present but listed
   under historical reports. This is technically consistent, but it reinforces
   the version-label confusion.

4. **Docs-command validation is useful but shallow.**

   `scripts/check_docs.py` catches links, absolute-path hygiene, and top-level
   command names. It does not execute full cookbook recipes or validate every
   subcommand flag sequence.

5. **Experimental surface is still very broad.**

   Sync, indexed search, local file sidecars, manuscript QA, reading sessions,
   rules, graph exports, claim lifecycle, workflows, review packets,
   incremental rebuilds, backups, migrations, and compatibility tools all
   exist. They are local-first and tested, but the product can look larger than
   its stable dogfooding core.

## Low-Priority Polish

- `paperwb --help` is comprehensive but too large for first-run orientation.
- Safety-sensitive flags are not fully uniform across command groups
  (`--out`, `--output`, `--report`, `--json-out`, `--force`,
  `--force-report`, `--dry-run`, `--run-writes`).
- Public Python API boundaries are documented, but most internal modules remain
  importable by name.
- Notebook validation is structural by default; full execution is selective.
- Historical docs remain useful but make the docs tree feel dense.

## Data-Safety Risks

- Current tracked data-safety audit: 866 files checked, 0 errors, 0 warnings.
- No tracked PDFs, SQLite/cache DBs, backup archives, raw audit logs, `.idea`
  files, `.paperwb` state, Python caches, `.DS_Store`, `build/`, `dist/`,
  scratch output, or egg-info artifacts were found by the tracked-file scan.
- `.gitignore` covers `.paperwb-local/`, `.paperwb/`, nested `.paperwb/`,
  rebuild metadata, SQLite/database files, backups, audit logs, scratch/tmp,
  stress outputs, historical hostile-review drafts, and PDFs.
- Ignored local artifacts are present, including caches, project `.paperwb`
  folders, backups, build output, `.DS_Store`, and local public-demo cache
  folders. They are ignored, but public packaging should happen from a clean
  clone or after another data-safety audit.
- Support bundle smoke output contained generated diagnostic files only. It did
  not include PDFs, databases, backup archives, raw audit logs, private paths,
  claim bodies, or quote text.
- Residual data-safety risk is user behavior: verbose/local-only outputs,
  external workspace reports with `--show-paths`, or support bundles generated
  outside safe mode must never be committed.

## Docs Mismatches

- No broken doc links were found by `scripts/check_docs.py`.
- README now has a clear public entry point, but the `3.5` package version plus
  `v3.0rc2` cleanup label can confuse external users.
- `docs/CLI_REFERENCE_V3.md` includes a stable `note-template` example that is
  not safe to run literally against `clean_demo` without an alternate output
  path because the note already exists.
- Historical docs and reports are intentionally retained; they should not be
  presented as the current user journey.

## CLI Usability Issues

- New users need the README/docs path because the raw CLI surface is too large
  to infer a workflow from `paperwb --help`.
- `note-template` overwrite protection is correct, but the failure message is
  terse and does not suggest `--output scratch/...` or using an empty project.
- Experimental commands are discoverable from top-level help before users read
  the stable/experimental boundary docs.
- Output flags vary across groups and can be hard to remember.

## Overengineering Risks

- The repository now contains enough subsystems to behave like a small local
  research operating system: registry/BibTeX, notes/claims, reports, authoring,
  manuscript QA, reading sessions, import/export, sync, search, backup,
  migration, rules, dashboard, evidence graph, lifecycle tracking, workflow
  runner, review packets, support bundles, compatibility, rebuilds, external
  workspaces, quality gates, and a docs cookbook.
- Do not add another major feature until the first private real project
  produces concrete bug reports.
- Near-term effort should focus on command-contract hardening, docs execution
  tests, report archiving, and resolving the dirty worktree.

## Stale Generated Reports

- `reports/index.md` is generated and current for v3.5, with 245 Markdown
  reports indexed.
- Historical reports are intentionally retained and useful for provenance.
- Old release-readiness and hostile-review reports should stay out of the main
  first-run path.
- The v3.0rc2 artifact policy and archive plan are present, but no archive move
  has been performed.

## Missing Tests

- Add an executable docs/cookbook smoke test for the first-run path, including
  a non-overwriting note-template example.
- Add a clean-worktree release gate or script check that fails public-release
  validation when tracked source/test/notebook files are dirty.
- Add stricter command-example validation for subcommand flags in cookbook
  pages.
- Add a report-index test or docs note covering rc-style labels such as
  `v3_0_rc2`.
- Add selective notebook execution coverage for the most important notebooks.
- Add one strict local release-gate check in environments with `.[dev]`
  installed, so skipped Ruff/build steps cannot be mistaken for a release pass.

## Recommended Blocker-Fix Sequence

1. Resolve the dirty tracked files: review, commit intentionally, or revert
   with user approval.
2. Rerun `python -m pytest -q`.
3. Rerun `python scripts/run_quality_gate.py release --out scratch/release_quality_gate.md`
   in an environment with `.[dev]` installed.
4. Fix the `note-template` documentation/usability issue by using an empty
   project or `--output scratch/...` in public examples.
5. Decide and document whether the public release identity is `3.5` or
   `v3.0rc2`.
6. Regenerate `reports/index.md` if any release reports change.
7. Rerun `python scripts/data_safety_audit.py --out scratch/data_safety.md --strict`
   before any public push or tag.
