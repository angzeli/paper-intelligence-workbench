# Hostile Maintainer Review: Current Repository

Date: 2026-06-16

Scope: standalone release-gate review of Paper Intelligence Workbench v3.2 as
if deciding whether this version is safe for local dogfooding. I inspected
package architecture, CLI behavior, stable versus experimental surface docs,
registry and BibTeX workflows, notes and claims, evidence maps,
manuscript/draft QA, reading sessions, imports/exports, sync/conflict
planning, search/indexing, backup/migration/integrity, rule engine, dashboard,
evidence graph, claim lifecycle, workflow runner, collaboration/review packets,
performance/incremental rebuilds, compatibility/migration behavior, tests,
docs, notebooks, reports, synthetic data, data-safety boundaries, `.gitignore`,
and git status.

## Release Verdict

**Ready for local dogfooding as v3.2. Not ready to call polished public-release
quality without further CLI/report hygiene.**

I found no release blockers and no high-priority issues that should stop local
dogfooding. The package imports as `3.2`, the stable v3 help surface loads, the
clean synthetic project validates, v3.2 compatibility inspection detects legacy
and malicious workspace shapes, support-bundle redaction mode conflicts now fail
loudly, notebook structure validation passes, the strict data-safety audit
passes, and the full test suite passes.

The remaining risks are maintainability and usability risks, not data-loss
blockers: the CLI is very large, several experimental workflows still have
soft/awkward failure modes, historical generated reports are noisy, and some
smoke workflows can leave ignored `.paperwb/` artifacts when run directly
against fixture directories.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead
  8]`; no tracked modifications before writing this report; ignored local
  caches/build outputs/dogfood artifacts were present.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `3.2`.
- `paperwb --help`: passed and listed stable starting points plus experimental
  and safety-sensitive command groups.
- `paperwb compatibility --help`: passed.
- `paperwb support bundle --help`: passed and shows `--safe |
  --verbose-local-only` as a mutually exclusive choice.
- `paperwb review-packet --help`: passed.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`: passed
  with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry
  projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb doctor --project clean_demo --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed and reported
  zero BibTeX, citation, workspace, rule, manuscript, graph, and claim-review
  findings.
- `paperwb support bundle --project clean_demo --out <tmp> --force`: passed and
  wrote 13 generated diagnostic files.
- `paperwb support bundle --project clean_demo --safe --verbose-local-only
  --out <tmp>`: rejected with argparse exit code 2.
- `paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data`:
  passed and detected a legacy data workflow requiring migration.
- `paperwb compatibility inspect tests/fixtures/workspaces/path_traversal_workspace
  --strict`: failed as expected with `project_profile_path_escape`.
- `paperwb migrate run --root tests/fixtures/workspaces/v0_1_legacy_data
  --to-project migrated_review --dry-run --out <tmp> --force-report`: passed.
- `paperwb compatibility report tests/fixtures/workspaces/extra_columns_registry
  --out <tmp> --force`: passed.
- `paperwb workflow run daily_check --project clean_demo --dry-run --out <tmp>
  --force`: passed with 5 steps, 0 errors, 0 warnings.
- `paperwb graph summary --project clean_demo --out <tmp> --force`: passed.
- `paperwb rebuild plan --project clean_demo --out <tmp> --force-report`:
  passed.
- `paperwb rules report --project clean_demo --out <tmp> --force`: passed.
- `paperwb draft audit drafts/synthetic_good_section.md --project clean_demo
  --out <tmp> --force`: passed.
- `paperwb manuscript qa drafts/synthetic_good_section.md --project clean_demo
  --out <tmp> --force`: passed.
- `paperwb review-packet create --project clean_demo --theme clean-theme --out
  <tmp> --force`: passed, produced `Items: 0`, and reported `Includes PDFs:
  false`.
- `paperwb search clean --project clean_demo`: passed and returned paper, note,
  and claim results.
- `paperwb index status --project clean_demo --out <tmp> --force`: passed.
- `paperwb sync plan --source data/examples/zotero_export.csv --source-type
  zotero-csv --project clean_demo --out <tmp> --json-out <tmp> --force`:
  passed with 3 actions and 0 conflicts.
- `paperwb import zotero-csv data/examples/zotero_export.csv --project
  clean_demo --dry-run --report <tmp> --force`: passed with 5 rows read, 3
  imported, 0 updated, 2 skipped, dry-run true.
- `paperwb integrity check --project clean_demo --strict --out <tmp> --force`:
  passed with 0 errors and 0 warnings.
- `paperwb compatibility matrix`: passed and printed v3.2 matrix entries.
- `paperwb dogfood status --project clean_demo`: passed.
- `paperwb note-template clean_demo_2026 --project clean_demo --out <tmp>
  --force`: passed.
- `paperwb claims --project clean_demo --out <tmp> --force`: passed and wrote 1
  claim.
- `python scripts/check_notebooks.py`: checked 8 notebook files.
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 821
  repository files with 0 errors and 0 warnings.
- `pytest`: 330 passed.

## Release Blockers

None found.

## High-Priority Issues

None found.

The high-priority support-bundle issue from the previous stale review is fixed:
`--safe` and `--verbose-local-only` are now mutually exclusive and the
conflicting invocation exits with code 2 before writing a bundle.

## Medium-Priority Issues

1. **`paper_workbench/cli.py` remains the primary maintainability risk.**

   Evidence: `paper_workbench/cli.py` is 3,936 lines and owns parser setup,
   command dispatch, safety prompts, path handling, output writes, and audit
   events across more than 30 command groups.

   Impact: current behavior is covered by tests and smoke checks, but future
   commands are likely to repeat flag, path, or overwrite semantics unless CLI
   helpers continue to be extracted carefully.

2. **New compatibility code is useful but already broad.**

   Evidence: `paper_workbench/compatibility.py` is 535 lines and combines
   workspace detection, path-containment checks, schema heuristics, report
   rendering, and compatibility matrix policy.

   Impact: acceptable for v3.2, but future compatibility behavior should be
   split only after command-contract tests pin current outputs. Approximate
   version detection should stay documented as heuristic, not authoritative.

3. **Review-packet creation still succeeds with an empty selection.**

   Evidence: `paperwb review-packet create --project clean_demo --theme
   clean-theme --out <tmp> --force` exited successfully with `Items: 0`.

   Impact: this is experimental and does not modify evidence, so it is not a
   blocker. It can still waste collaborator time by producing a formally valid
   packet with no review items. Add a warning, `--allow-empty`, or strict-mode
   failure before promoting review packets.

4. **Generated report inventory is noisy and slightly stale.**

   Evidence: `reports/index.md` identifies v3.2 current reports, but the
   reports directory contains more Markdown files than its indexed-count line
   reports, and historical reports span v0 through v3.2.

   Impact: provenance is useful, but maintainers and new users still need a
   clearer route to current release evidence. Keep historical reports, but
   regenerate the index when reports are added and consider archiving old
   release-burn artifacts outside the first-page view.

5. **Fixture smoke commands can leave ignored local state inside fixture
   directories.**

   Evidence: after a migration dry-run against a fixture path, git status showed
   an ignored `tests/fixtures/workspaces/v0_1_legacy_data/.paperwb/` artifact.

   Impact: `.gitignore` prevents accidental staging, so this is not a data
   safety blocker. It is still annoying for maintainer reviews. Future smoke
   docs should prefer copying fixtures to `/private/tmp` before commands that
   may write audit/cache state.

## Low-Priority Polish

- `paperwb --help` is an inventory, not an onboarding guide. The v3 docs do the
  real onboarding work.
- Output flags remain inconsistent across workflows: `--out`, `--report`,
  `--reports-dir`, `--json-out`, `--force`, and `--force-report`.
- `validate-bib --strict` fails on error-level findings only. This is
  documented, but strict-mode expectations vary by user.
- Historical v2 and lowercase docs remain searchable and can distract from v3
  docs.
- The public Python surface is intentionally small, but many modules remain
  importable without private naming; docs should continue emphasizing CLI and
  schemas as the stable API.

## Data-Safety Risks

- No tracked PDFs, SQLite/cache DBs, backup archives, audit logs, `.idea`
  files, `.paperwb` state, Python caches, `.DS_Store`, `build/`, `dist/`, or
  egg-info artifacts were found by `git ls-files` checks.
- `.gitignore` covers `.paperwb/`, nested `.paperwb/`, rebuild metadata,
  SQLite/database files, backups, audit logs, scratch/tmp, stress outputs,
  historical hostile-review drafts, and PDFs.
- The strict data-safety audit checked 821 repository files and reported 0
  errors and 0 warnings.
- The generated safe support bundle contained only diagnostic summaries,
  sanitized samples, and manifests; no PDFs, cache DBs, backup archives, or raw
  audit logs were present.
- The historical fixture `extra_columns_registry` deliberately contains a
  synthetic unsafe `local_pdf_path` string (`../outside/private.pdf`) to test
  preservation and path-risk detection. It is not an actual committed PDF.
- Residual risk: local ignored artifacts are present in the working tree from
  dogfooding and smoke checks. They are ignored, but release packaging should
  start from a clean clone or run a hygiene check first.

## Docs Mismatches

- v3 stable and experimental docs are aligned with package `3.2` and current
  compatibility behavior.
- `docs/ROADMAP_V3.md` intentionally includes a v3.1 section and v3.2 work; no
  blocking stale release-candidate wording was found in the current v3 docs.
- `reports/index.md` is current in section labeling but has a stale indexed
  count versus files on disk.
- The docs correctly say compatibility inspection is read-only except explicit
  report output, but maintainer smoke commands can still create ignored audit
  state under `.paperwb/` when run directly against fixture paths.
- Historical docs and reports remain extensive. Current users should start with
  `README.md`, `docs/GETTING_STARTED_V3.md`, `docs/STABLE_SURFACE_V3.md`,
  `docs/CLI_REFERENCE_V3.md`, and `docs/COMPATIBILITY_MATRIX_V3.md`.

## CLI Usability Issues

- Empty review packets are too easy to create.
- First-run terminal help is too broad to function as a guided workflow.
- Some safety-sensitive commands use different names for dry-run, force, and
  output flags.
- Compatibility inspection output is concise and useful, but users may read
  approximate-version labels as definitive unless docs keep calling them
  heuristics.
- Project-root/path override safeguards are good for safety, but still surprise
  users trying to send outputs outside project-local reports.

## Overengineering Risks

- The repository now includes project templates, dogfood scaffolds, registry and
  BibTeX validation, structured notes and claims, citation audits, evidence
  maps, manuscript QA, reading sessions, imports/exports, sync planning, local
  search/indexing, backup/migration/integrity, rules, dashboard, evidence
  graph, claim lifecycle, workflow recipes, review packets, support bundles,
  incremental rebuilds, and compatibility inspection.
- Do not add another major subsystem before real dogfooding generates concrete
  bugs. The next patches should tighten current contracts, reduce CLI
  repetition, and improve current workflow ergonomics.
- Keep graph exports, claim lifecycle sidecars, workflow recipes,
  review-packet comments, sync apply, indexed search, rebuild metadata, verbose
  support bundles, and forced migration/restore flows experimental until real
  projects prove their contracts.

## Stale Generated Reports

- `reports/hostile_review_latest.md` was stale v3.1 content before this review
  and is now refreshed.
- `reports/index.md` labels current v3.2 reports, but its indexed count is
  stale against the current reports directory.
- Historical v0/v1/v2/v3.0rc/v3.1 reports intentionally remain. They are useful
  for provenance but should not be presented as current release guidance.
- Ignored historical hostile-review drafts remain excluded by `.gitignore` and
  should stay archival.

## Missing Tests

- No test currently asserts that empty review-packet selections warn, fail, or
  require an explicit `--allow-empty`.
- There is no single README transcript test that executes the public quickstart
  exactly as written.
- Notebook checks are structural. That is reasonable for speed, but advertised
  notebooks are not executed as a normal release gate.
- Compatibility fixture tests are good for v3.2, but future schema changes
  should add fixtures before changing migration behavior.
- Experimental command coverage is broad but not exhaustive; not every
  experimental command has help, happy-path, failure-path, and no-overwrite
  contract tests.

## Recommended Blocker-Fix Sequence

There are no release blockers or high-priority issues to fix before local
dogfooding.

Recommended next sequence:

1. Add an explicit warning or strict failure for `review-packet create` when
   filters select zero items.
2. Regenerate `reports/index.md` after this review and decide whether old
   release-burn reports should be archived outside the main report index.
3. Add a README quickstart transcript smoke test.
4. Update maintainer smoke docs to run fixture migration checks on `/private/tmp`
   copies instead of fixture directories.
5. Keep splitting CLI helpers only where behavior is already pinned by command
   tests; do not do a large CLI rewrite before more real dogfooding.
