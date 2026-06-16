# Hostile Maintainer Review: Current Repository

Date: 2026-06-16

Scope: standalone release-gate review of Paper Intelligence Workbench v3.1 as if
deciding whether this version is safe for local dogfooding. I inspected package
architecture, CLI behavior, stable versus experimental surface docs, registry
and BibTeX workflows, notes and claims, evidence maps, manuscript/draft QA,
reading sessions, imports/exports, sync/conflict planning, search/indexing,
backup/migration/integrity, rule engine, dashboard, evidence graph, claim
lifecycle, workflow runner, collaboration/review packets, performance and
incremental rebuilds, tests, docs, notebooks, reports, synthetic data,
data-safety boundaries, `.gitignore`, and git status.

## Release Verdict

**Ready for local dogfooding with one high-priority usability fix recommended
before asking users to share support bundles.**

I did not find a release blocker. The package imports as `3.1`, `paperwb
--help` loads, the clean first-run project validates without findings, the full
test suite passes, notebook structure validation passes, the data-safety audit
reports zero errors/warnings, and representative stable plus experimental CLI
workflows completed without tracebacks.

This is not a public-release verdict. The repository is broad, the CLI remains
oversized, historical docs/reports are noisy, and the new support-bundle
workflow has one ambiguous flag combination that should be tightened before
external sharing is encouraged.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead
  4]`; no tracked modifications before writing this report; ignored local
  caches/build outputs/dogfood artifacts were present.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `3.1`.
- `paperwb --help`: passed and listed current command groups, including
  `support`.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`: passed
  with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry
  projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb doctor --project clean_demo --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed with zero
  BibTeX, citation, workspace, rule, manuscript, graph, and claim-review
  findings.
- `paperwb support bundle --project clean_demo --out <tmp> --force`: passed and
  wrote 13 generated diagnostic files.
- Support bundle forbidden-artifact check: no PDFs, SQLite/cache DBs, backup
  archives, or raw `audit.log` files were present in the generated bundle.
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
- `paperwb reading queue --project clean_demo --out <tmp> --force`: passed.
- `paperwb index status --project clean_demo --out <tmp> --force`: passed.
- `paperwb backup list --project clean_demo`: passed and reported no backups.
- `paperwb sync plan --source data/examples/zotero_export.csv --source-type
  zotero-csv --project clean_demo --out <tmp> --json-out <tmp> --force`: passed
  with 3 actions and 0 conflicts.
- `paperwb review-packet create --project clean_demo --theme clean-theme --out
  <tmp> --force`: passed, produced no items, and reported `Includes PDFs:
  false`.
- `paperwb import zotero-csv data/examples/zotero_export.csv --project
  clean_demo --dry-run --report <tmp> --force`: passed with 5 rows read, 3
  imported, 0 updated, 2 skipped, dry-run true.
- `paperwb export report-index --out <tmp> --force`: passed.
- `paperwb integrity check --project clean_demo --strict --out <tmp> --force`:
  passed with 0 errors and 0 warnings.
- `paperwb search clean --project clean_demo`: passed and returned paper, note,
  and claim results.
- `python scripts/check_notebooks.py`: checked 8 notebook files.
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 757
  repository files with 0 errors and 0 warnings.
- `pytest`: 319 passed.

## Release Blockers

None found.

## High-Priority Issues

1. **Support bundle redaction flags are contradictory but not rejected.**

   Evidence: `paperwb support bundle --project clean_demo --safe
   --verbose-local-only --out <tmp> --force` completed successfully and printed
   `Safe mode: false` / `Verbose local-only mode: true`.

   Why it matters: `support` is now documented as a stable diagnostic surface
   and support bundles are the intended path for sharing debug state. If a user
   passes `--safe` explicitly, the command should not silently generate a
   less-redacted bundle because `--verbose-local-only` was also present.

   Recommended fix: make `--safe` and `--verbose-local-only` mutually exclusive
   in argparse, or reject the combination in `cmd_support_bundle` and
   `cmd_support_redact_preview` with a user-facing error. Add a regression test
   that the conflicting flags return exit code 2 and do not write a bundle.

## Medium-Priority Issues

1. **Some v3 docs still read as v3.0rc-era docs after the package moved to
   v3.1.**

   Evidence: `docs/STABLE_SURFACE_V3.md` still opens with "v3.0rc freezes...",
   and `docs/ROADMAP_V3.md` still has "Before v3.0.0" / "After v3.0.0"
   sections despite the current package metadata being `3.1`.

   Impact: not a functional blocker, but a new user trying to understand
   current release status will see mixed v3.0rc and v3.1 language.

2. **The CLI implementation remains the main architecture risk.**

   Evidence: `paper_workbench/cli.py` is about 3,888 lines and owns parser
   setup, path resolution, write preflights, audit events, and dispatch for
   every subsystem.

   Impact: dogfoodable today, but each new command group increases the chance
   of inconsistent flags, safety gates, or output semantics.

3. **The new support-bundle module is useful but already large.**

   Evidence: `paper_workbench/support.py` is about 862 lines and combines data
   models, redaction, diagnostics, Markdown rendering, CSV sample generation,
   bundle writing, and report summaries.

   Impact: acceptable for v3.1, but future support-bundle changes should split
   redaction helpers, bundle assembly, and report rendering only after tests pin
   the current privacy behavior.

4. **Review-packet creation succeeds with an unknown or empty theme selection.**

   Evidence: `paperwb review-packet create --project clean_demo --theme
   clean-theme --out <tmp> --force` exited successfully with `Items: 0`.

   Impact: `review-packet` is experimental, so this is not a blocker. Still,
   a collaborator-facing packet with zero items should probably warn loudly or
   fail under a strict flag.

5. **Historical generated reports remain noisy and partially stale.**

   Evidence: `reports/index.md` now marks v3.1 reports current, but it indexes
   220 Markdown reports spanning v0 through v3.1.

   Impact: useful for provenance, but hostile to a new maintainer looking for
   the actual current release story.

## Low-Priority Polish

- `paperwb --help` lists more than 30 command groups; it is an inventory, not an
  onboarding experience. The docs handle onboarding better than the terminal
  help.
- Several output flags remain inconsistent across workflows: `--out`,
  `--output`, `--report`, `--reports-dir`, `--json-out`, and `--force-report`.
- `validate-bib --strict` still only fails on error-level findings; this is
  documented, but strict-mode expectations vary.
- `support bundle --safe` is accepted even though safe mode is already the
  default. That is harmless alone, but it makes the conflicting verbose case
  more likely.
- Old v2 and lowercase docs remain in the tree for historical/site-source
  reasons and can distract from v3 docs.

## Data-Safety Risks

- No tracked PDFs, copied full text, SQLite/cache DBs, backup archives, audit
  logs, `.paperwb` state, Python caches, `.DS_Store`, `build/`, `dist/`, or
  egg-info artifacts were found by the data-safety audit.
- `.gitignore` covers `.paperwb/`, nested `.paperwb/`, rebuild metadata,
  SQLite/database files, backups, audit logs, scratch/tmp, stress outputs,
  historical hostile-review drafts, and PDFs.
- The generated safe support bundle contained no PDFs, cache DBs, backup
  archives, or raw audit logs.
- Residual risk: tracked historical reports still contain old command evidence
  with local absolute paths. The current data-safety audit allowlists known
  historical cases, so this is not a dogfooding blocker, but it should be
  cleaned before any polished public release.
- Residual risk: `--verbose-local-only` support bundles intentionally preserve
  more metadata. This is acceptable for private debugging but should not be
  shareable by accident.

## Docs Mismatches

- v3 stable/roadmap docs mix v3.0rc phrasing with v3.1 package metadata.
- `docs/REPORT_GALLERY_V3.md` now correctly points at v3.1 reports, but other
  v3 pages are partly release-candidate oriented.
- The stable/experimental split is honest, but users must read
  `docs/STABLE_SURFACE_V3.md` and `docs/EXPERIMENTAL_FEATURES_V3.md`; the CLI
  itself cannot convey all stability nuance.
- Historical docs are extensive and still searchable. They should remain
  available, but current docs should be easier to identify.

## CLI Usability Issues

- `paperwb support bundle --safe --verbose-local-only` silently chooses verbose
  mode. This is the most important current CLI issue.
- `review-packet create --theme <unknown>` can create an empty packet without a
  visible warning.
- `paperwb --help` is too broad for first-run orientation.
- Path/output flag names remain inconsistent across command groups.
- Project path override rejection is good for safety, but still surprises users
  trying to route generated reports outside a project via `--reports-dir`.

## Overengineering Risks

- The repository now includes project templates, dogfood scaffolds, registry and
  BibTeX validation, notes/claims, citation audits, evidence maps, manuscript
  QA, reading sessions, imports/exports, sync planning, search/indexing,
  backup/migration/integrity, rules, dashboard, evidence graph, claim lifecycle,
  workflow recipes, review packets, support bundles, and incremental rebuilds.
- Do not add another major subsystem before real dogfooding. The next work
  should tighten semantics, remove stale wording, and improve tests around
  current surfaces.
- Keep graph exports, claim lifecycle sidecars, workflow recipes, review-packet
  comments, sync apply, indexed search, rebuild metadata, and verbose support
  bundles experimental until real projects prove their contracts.

## Stale Generated Reports

- `reports/index.md` is current for v3.1.
- `reports/hostile_review_latest.md` was stale v3.0rc content before this
  review and is now refreshed.
- Historical v0/v1/v2/v3.0rc reports intentionally remain. They are useful for
  provenance but should not be presented as release guidance.
- Old hostile-review drafts contain absolute-path evidence and should stay
  ignored/archival, not user-facing.

## Missing Tests

- No test currently rejects the conflicting `--safe --verbose-local-only`
  support-bundle flags.
- No test asserts that an unknown `review-packet --theme` warns or fails.
- Notebook checks are structural. That is acceptable for speed, but optional
  notebook execution is not a regular gate.
- There is no single README transcript test that pastes the public quickstart
  end to end.
- Experimental command coverage is broad but not exhaustive; not every
  experimental command has help, happy-path, failure-path, and no-overwrite
  contract tests.

## Recommended Blocker-Fix Sequence

There are no release blockers to fix before local dogfooding.

Recommended high-priority sequence:

1. Reject `paperwb support ... --safe --verbose-local-only` with a clear
   user-facing error.
2. Add regression tests for support-bundle flag exclusivity and no output on
   conflicting redaction modes.
3. Refresh v3 docs that still say v3.0rc/v3.0.0 where the current state is
   v3.1.
4. Add a warning or strict failure path for review packets that select zero
   review items.
5. Defer broad `cli.py` or `support.py` splitting until the stable command
   contracts and support-bundle privacy tests are preserved.
