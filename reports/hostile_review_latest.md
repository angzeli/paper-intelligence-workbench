# Hostile Maintainer Review: Current Repository

Date: 2026-06-18

Scope: standalone release-gate review of Paper Intelligence Workbench v3.5 as
if deciding whether this version is safe for local dogfooding. I inspected
package architecture, CLI behavior, stable versus experimental surface docs,
registry and BibTeX workflows, notes and claims, evidence maps,
manuscript/draft QA, reading sessions, imports/exports, sync/conflict
planning, search/indexing, backup/migration/integrity, rule engine,
dashboard, evidence graph, claim lifecycle, workflow runner,
collaboration/review packets, performance/incremental rebuilds, support
bundles, compatibility/migration behavior, private external workspaces, tests,
docs, notebooks, reports, synthetic data, data-safety boundaries,
`.gitignore`, and git status.

## Release Verdict

**Ready for local dogfooding as v3.5, but not ready to call public-release
polished.**

I found no release blocker that should stop local dogfooding. The package
imports as `3.5`, the full test suite passes, stable registry and BibTeX
validation pass on the clean synthetic project, docs and notebooks validate,
the data-safety audit reports zero findings, and representative stable and
experimental smoke commands run without unexpected writes.

The main risk is no longer basic functionality. The main risk is operational
discipline around a large CLI surface. The project has many subsystems, a
4,000-line CLI dispatcher, hundreds of generated reports, and now a private
external-workspace adapter. That adapter is useful, but one part of its output
still exposes absolute external workspace paths unless the user keeps the
report local. That should be fixed before recommending external-mode reports
to less careful users.

## Validation Performed

- `git status --short --branch --ignored`: branch was `main...origin/main
  [ahead 3]`; no tracked modifications before writing this report; ignored
  local caches, build output, project caches, backups, and local demo artifacts
  were present.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `3.5`.
- `paperwb --help`: passed and labels stable starting points versus
  experimental or safety-sensitive workflows.
- Help checks passed for representative groups: `project`, `template`,
  `external`, `support`, `report`, `sync`, `backup`, `rebuild`,
  `review-packet`, and `rules`.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`:
  passed with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry
  projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed and reported
  zero BibTeX, citation, workspace, rule, manuscript, graph, and claim-review
  findings.
- `paperwb support doctor --project clean_demo`: passed and redacted project
  paths.
- `paperwb compatibility matrix`: passed and documented historical workspace
  support.
- `paperwb workflow list`: passed and listed built-in recipes.
- `paperwb claims projects/clean_demo/notes --output <tmp>`: first refused an
  existing output, then passed with a fresh output path. The refusal is correct
  overwrite protection.
- `paperwb report evidence-map --project clean_demo --out <tmp> --force`:
  passed.
- `paperwb manuscript qa drafts/synthetic_good_section.md --project
  zis_photocatalysis --out <tmp> --force`: passed.
- `paperwb external list`: passed with no registered external workspaces in
  this clone.
- `python -m pytest -q`: passed.
- `python scripts/check_docs.py`: passed and checked 187 Markdown doc files.
- `python scripts/validate_notebooks.py`: passed and validated 8 notebooks.
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 860
  repository files with 0 errors and 0 warnings.
- `python scripts/run_quality_gate.py local-diagnostic --out <tmp>`: passed
  available checks: mypy scripts, pytest, CLI smoke workflow, notebook
  validation, notebook metadata checks, and data-safety audit. Ruff
  lint/format and distribution build checks were skipped because the relevant
  modules were not installed in this interpreter.

## Release Blockers

None found for local dogfooding.

## High-Priority Issues

1. **External workspace validation output can expose private absolute paths if
   written into tracked reports.**

   Evidence: `paper_workbench/external.py` renders external validation reports
   with the registered workspace path and finding sources. The local config is
   correctly ignored, and support bundles redact paths by default, but
   `paperwb external validate NAME --out reports/example.md` can still create
   a tracked Markdown report containing the private external path.

   Impact: this does not leak anything in the current repository, and it does
   not copy PDFs, notes, drafts, or BibTeX into the repo. It is still a
   high-priority privacy footgun because v3.5 explicitly exists to support
   private real-project dogfooding.

   Required fix before broader user recommendation: redact external paths by
   default in external validation and external run summaries, add an explicit
   `--show-paths` or `--verbose-local-only` escape hatch, and add tests that
   `--out reports/...` does not contain private absolute paths by default.

## Medium-Priority Issues

1. **Strict release validation depends on dev tooling that may be absent
   locally.**

   Evidence: local diagnostic quality gate skipped Ruff lint/format and build
   distribution checks because those modules were unavailable. CI installs
   `.[dev]`, so this is not a functional dogfooding blocker.

   Impact: maintainers need CI or an explicit dev install before calling a
   release gate strict. Local dogfooding can continue.

2. **`paper_workbench/cli.py` remains the main maintainability risk.**

   Evidence: `paper_workbench/cli.py` is 4,041 lines and still owns parser
   setup, command dispatch, project/path resolution, output writes, force
   flags, and audit behavior for many command groups.

   Impact: current tests cover the behavior, but future changes can easily
   introduce flag drift, inconsistent overwrite rules, or missed command
   contracts.

3. **Docs-command checking is useful but shallow.**

   Evidence: `scripts/check_docs.py` validates links, absolute-path hygiene,
   and top-level command names, but it does not execute cookbook commands or
   validate subcommand flags in examples.

   Impact: the docs are much cleaner than earlier releases, but cookbook drift
   is still possible.

4. **The reports directory is current but heavy.**

   Evidence: `reports/index.md` indexes 240 Markdown reports. It correctly
   identifies current v3.5 reports, but the historical report volume remains
   high.

   Impact: useful provenance, noisy maintainer experience. New users should
   not browse the reports directory unaided.

5. **Experimental subsystems are numerous enough to blur product focus.**

   Evidence: experimental surfaces include sync, indexed search, local files,
   manuscript QA, reading sessions, rules, graph exports, claim lifecycle,
   workflow recipes, review packets, rebuilds, backup/restore/migration, and
   synthetic generation.

   Impact: all are local-first and tested, but maintainers should avoid
   promoting them as stable until real dogfooding proves the contracts.

## Low-Priority Polish

- `paperwb --help` is comprehensive but too broad to be a guided first-run
  experience.
- Output and safety flags are still not fully uniform across groups:
  `--out`, `--report`, `--reports-dir`, `--json-out`, `--force`,
  `--force-report`, and workflow-specific dry-run flags.
- Historical v2 and early v3 docs remain useful for provenance but can distract
  from the v3 entry path.
- Public Python API boundaries are documented, but internal modules remain
  importable without private naming.
- Notebook validation is structural by default; full execution remains a
  manual or selective check.

## Data-Safety Risks

- Current tracked data-safety audit: 860 files checked, 0 errors, 0 warnings.
- No tracked PDFs, SQLite/cache DBs, backup archives, raw audit logs, `.idea`
  files, `.paperwb` state, Python caches, `.DS_Store`, `build/`, `dist/`, or
  egg-info artifacts were found in committed file checks.
- `.gitignore` covers `.paperwb-local/`, `.paperwb/`, nested `.paperwb/`,
  SQLite/database files, rebuild metadata, backups, audit logs, scratch/tmp,
  stress outputs, historical hostile-review drafts, and PDFs.
- The tracked public dogfood demo uses placeholder filenames, placeholder
  BibTeX keys, and synthetic registry rows. I did not find committed private
  filenames or real BibTeX metadata in that demo.
- Residual risk: ignored local artifacts are present from dogfooding and smoke
  checks. They are ignored, but release packaging should be done from a clean
  clone or after rerunning the data-safety audit.
- High-priority residual risk: external validation reports are not path-redacted
  by default if a user writes them to a tracked location.

## Docs Mismatches

- No blocking mismatch found in current v3 docs. `README.md`, `docs/index.md`,
  `docs/STABLE_SURFACE_V3.md`, `docs/EXPERIMENTAL_FEATURES_V3.md`,
  `docs/CLI_REFERENCE_V3.md`, `docs/PRIVATE_DOGFOODING.md`,
  `docs/EXTERNAL_WORKSPACES.md`, and `docs/LOCAL_ONLY_CONFIG.md` match the
  inspected CLI surface.
- One safety wording gap: private external workspace docs correctly state that
  config is ignored and support bundles are redacted, but they should warn more
  explicitly that ordinary external validation reports currently include the
  registered external path.
- `reports/hostile_review_latest.md` was stale v3.4 content before this review
  and is now refreshed.

## CLI Usability Issues

- The first-run command inventory is large. The docs carry the guided
  onboarding burden.
- External workspace validation needs safer default redaction for output
  reports.
- Safety-sensitive commands still use varied flag names for force, dry-run, and
  output destination.
- Experimental commands are well labelled, but users can still discover them
  before understanding the stable path.

## Overengineering Risks

- The repository now includes project templates, dogfood scaffolds, external
  workspace adapters, registry and BibTeX validation, structured notes and
  claims, citation audits, evidence maps, manuscript QA, reading sessions,
  imports/exports, sync planning, local search/indexing, backup/migration/
  integrity, rules, dashboard, evidence graph, claim lifecycle, workflow
  recipes, review packets, support bundles, compatibility inspection,
  incremental rebuilds, quality gates, and a docs cookbook.
- Do not add another major subsystem before real private dogfooding produces
  concrete bugs.
- v3.6 should tighten existing safety contracts, especially external workspace
  redaction and command transcript testing.

## Stale Generated Reports

- `reports/index.md` is current for v3.5 and lists `hostile_review_latest.md`
  as a current report.
- Historical reports are intentionally retained. Their main risk is cognitive
  noise, not current incorrectness.
- Continue regenerating `reports/index.md` whenever current release reports
  are added.

## Missing Tests

- Add tests that external validation and external run report outputs redact
  registered workspace paths by default.
- Add a regression test for the explicit opt-in path-revealing mode once it
  exists.
- Add transcript-style tests for the highest-value cookbook recipes:
  first project, manual paper addition, metadata validation, note template,
  claim extraction, evidence map, citation audit, dashboard, support bundle,
  external workspace registration, and compatibility inspection.
- Add stricter docs-command tests for subcommand flags used in cookbook pages.
- Add a test or clear CLI contract for empty review-packet behavior.
- Notebook checks are structural by default; selective execution coverage
  remains thin.

## Recommended Blocker-Fix Sequence

No release blocker fix is required before local dogfooding.

Recommended next sequence:

1. Fix the high-priority external-workspace path redaction issue.
2. Add tests proving external reports do not leak private paths by default.
3. Update private dogfooding docs to distinguish redacted diagnostic outputs
   from local-only verbose outputs.
4. Add transcript tests for the most important stable cookbook recipes.
5. Keep v3.6 focused on tightening existing contracts, not adding features.

## Post-Review Fix Status

The high-priority external-workspace path redaction issue identified in this
review has been fixed in the follow-up patch. External validation reports and
external run summaries now redact private local paths by default, and
`--show-paths` is the explicit local-only opt-in. Regression coverage was added
in `tests/test_external_v3_5.py`.
