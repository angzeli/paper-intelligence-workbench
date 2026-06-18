# Hostile Maintainer Review: Current Repository

Date: 2026-06-18

Scope: standalone release-gate review of Paper Intelligence Workbench v3.4 as
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

**Ready for local dogfooding as v3.4, but not public-release polished.**

I found no release blockers or high-priority defects that should prevent local
dogfooding. The package imports as `3.4`, the full test suite passes, stable
registry and BibTeX validation pass on the clean synthetic project, core
diagnostics are read-only and clean, the v3.4 docs checker passes, notebooks
validate structurally, data-safety checks report zero findings, and
representative experimental workflows completed without mutating user data.

The repo remains large and feature-rich for a single local CLI. The largest
risks are maintainability and expectation management: `paper_workbench/cli.py`
is still oversized, review packets can be generated with zero review items,
strict release validation still needs local dev tooling, and the reports
directory contains a long historical trail that can distract maintainers from
current release evidence.

## Validation Performed

- `git status --short --branch --ignored`: branch `main...origin/main [ahead
  18]`; no tracked modifications before writing this report; ignored local
  caches, build outputs, project caches, backups, and dogfood artifacts were
  present.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `3.4`.
- `paperwb --help`: passed and clearly labels stable starting points versus
  experimental or safety-sensitive workflows.
- `paperwb template --help`, `paperwb dogfood --help`, `paperwb support
  --help`, `paperwb workflow --help`: passed.
- `paperwb validate-registry projects/clean_demo/registry.csv --strict`:
  passed with no findings.
- `paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry
  projects/clean_demo/registry.csv --strict`: passed with no findings.
- `paperwb doctor --project clean_demo --strict`: passed with no findings.
- `paperwb dashboard --project clean_demo --no-audit-log`: passed and reported
  zero BibTeX, citation, workspace, rule, manuscript, graph, and claim-review
  findings.
- `paperwb support bundle --project clean_demo --out <tmp> --force`: passed
  and wrote 13 generated diagnostic files.
- `paperwb compatibility inspect tests/fixtures/workspaces/v0_1_legacy_data`:
  passed and detected a legacy data workflow requiring migration.
- `paperwb compatibility inspect
  tests/fixtures/workspaces/path_traversal_workspace --strict`: failed as
  expected with `project_profile_path_escape`.
- `paperwb graph summary --project clean_demo --out <tmp> --force`: passed.
- `paperwb rebuild plan --project clean_demo --out <tmp> --force-report`:
  passed.
- `paperwb rules report --project clean_demo --out <tmp> --force`: passed.
- `paperwb workflow run daily_check --project clean_demo --dry-run --out
  <tmp> --force`: passed with 5 steps, 0 errors, 0 warnings.
- `paperwb draft audit drafts/synthetic_good_section.md --project clean_demo
  --out <tmp> --force`: passed.
- `paperwb manuscript qa drafts/synthetic_good_section.md --project clean_demo
  --out <tmp> --force`: passed.
- `paperwb import zotero-csv data/examples/zotero_export.csv --project
  clean_demo --dry-run --report <tmp> --force`: passed with 5 rows read, 3
  imported, 0 updated, 2 skipped, dry-run true.
- `paperwb sync plan --source data/examples/zotero_export.csv --source-type
  zotero-csv --project clean_demo --out <tmp> --json-out <tmp> --force`:
  passed with 3 actions and 0 conflicts.
- `paperwb reading queue --project clean_demo --out <tmp> --force`: passed.
- `paperwb review-packet create --project clean_demo --theme clean-theme --out
  <tmp> --force`: passed, produced `Items: 0`, and reported `Includes PDFs:
  false`.
- `python -m pytest -q`: passed.
- `python scripts/check_docs.py`: passed and checked 183 Markdown doc files.
- `python scripts/smoke_cli_workflow.py --quick --out <tmp>`: passed with 14
  smoke steps and 0 failures.
- `python scripts/validate_notebooks.py`: passed and validated 8 notebooks.
- `python scripts/check_notebooks.py`: passed and checked 8 notebooks.
- `python scripts/data_safety_audit.py --out <tmp> --strict`: checked 850
  repository files with 0 errors and 0 warnings.
- `python scripts/run_quality_gate.py local-diagnostic --out <tmp>`: passed
  available checks, skipped missing Ruff lint/format tooling, and skipped build
  distributions because `setuptools.build_meta` is unavailable in this
  interpreter.
- `python scripts/run_quality_gate.py release --out <tmp>`: failed at Ruff
  lint because the local Python module `ruff` is unavailable. This is the
  intended strict behavior.
- Tracked-file hygiene check for PDFs, cache DBs, backup archives, audit logs,
  `.paperwb`, `.idea`, Python caches, build/dist, and egg-info artifacts:
  no tracked matches.

## Release Blockers

None found for local dogfooding.

## High-Priority Issues

None found during this review.

## Medium-Priority Issues

1. **Strict release validation depends on dev tooling that is absent locally.**

   Evidence: `python scripts/run_quality_gate.py release --out <tmp>` fails at
   Ruff lint because Ruff is not installed in the current interpreter.
   `local-diagnostic` handles this honestly by reporting skipped checks.

   Impact: dogfooding is not blocked, but maintainers still need either a dev
   environment with `.[dev]` installed or CI confirmation before calling this a
   strict release candidate.

2. **`paper_workbench/cli.py` remains the main maintainability risk.**

   Evidence: `paper_workbench/cli.py` is 3,936 lines and owns parser setup,
   command dispatch, project/path resolution, output writes, safety flags, and
   audit events across many command groups.

   Impact: current behavior is covered by tests and smokes, but future changes
   can easily create flag drift or inconsistent overwrite behavior unless CLI
   helper extraction continues carefully.

3. **Review-packet creation can produce an empty packet without warning.**

   Evidence: `paperwb review-packet create --project clean_demo --theme
   clean-theme --out <tmp> --force` exited successfully with `Items: 0`.

   Impact: this is experimental and safe, but weak UX. A collaborator could
   receive a formally valid packet with nothing to review. Add a warning,
   `--allow-empty`, or strict-mode failure before promoting review packets.

4. **The report inventory is current but still noisy.**

   Evidence: `reports/index.md` indexes 236 Markdown reports and mixes current
   v3.4 reports with historical v0-v3 release-burn artifacts.

   Impact: provenance is useful, but new maintainers still need a strong route
   to current evidence. The current section helps; the historical volume
   remains distracting.

5. **Docs consistency checks validate presence, not executable accuracy.**

   Evidence: `scripts/check_docs.py` passes, but it checks Markdown links and
   top-level command availability rather than executing every cookbook command
   or validating every subcommand flag combination.

   Impact: the v3.4 docs set is much cleaner, but command examples can still
   drift unless representative transcript tests are added for the most
   important recipes.

## Low-Priority Polish

- `paperwb --help` is necessarily broad and functions more like an inventory
  than a guided workflow.
- Output and safety flags remain inconsistent across command groups: `--out`,
  `--report`, `--reports-dir`, `--json-out`, `--force`, `--force-report`,
  `--dry-run`, and command-specific force names.
- Historical v2 and release-candidate docs are still searchable and can
  distract from v3 docs.
- The Markdown-only docs site source is appropriate, but there is no generated
  navigation artifact or static-site build check.
- Public Python API boundaries are documented, but most modules remain
  importable without private naming.

## Data-Safety Risks

- No tracked PDFs, SQLite/cache DBs, backup archives, audit logs, `.idea`
  files, `.paperwb` state, Python caches, `.DS_Store`, `build/`, `dist/`, or
  egg-info artifacts were found by tracked-file checks.
- `.gitignore` covers `.paperwb/`, nested `.paperwb/`, rebuild metadata,
  SQLite/database files, backups, audit logs, scratch/tmp, stress outputs,
  historical hostile-review drafts, and PDFs.
- The strict data-safety audit checked 850 repository files and reported 0
  errors and 0 warnings.
- The generated safe support bundle contained diagnostic summaries, sanitized
  samples, and manifests; it did not copy PDFs, cache DBs, backup archives, or
  raw audit logs.
- Residual risk: ignored local artifacts are present from dogfooding and smoke
  checks. They are ignored, but release packaging should start from a clean
  clone or rerun the data-safety audit before building artifacts.

## Docs Mismatches

- No blocking current-doc mismatch was found. `README.md`, `docs/index.md`,
  v3 stable/experimental docs, cookbook pages, report gallery, quality-gate
  docs, and command-reference docs are aligned with the inspected CLI surface.
- `reports/hostile_review_latest.md` was stale v3.3 content before this review
  and is now refreshed.
- Historical docs and reports remain extensive. Current users should start with
  `README.md`, `docs/index.md`, `docs/getting-started/index.md`,
  `docs/cookbook/index.md`, `docs/STABLE_SURFACE_V3.md`, and
  `docs/CLI_REFERENCE_V3.md`.

## CLI Usability Issues

- Empty review packets are too easy to create.
- First-run terminal help is broad; the docs carry most onboarding guidance.
- Safety-sensitive commands still use varied names for dry-run, force, and
  output flags.
- Quality-gate terminal summaries are concise; the Markdown report has the
  better explanation of skipped local tooling.
- Compatibility inspection output is useful, but approximate version labels
  should remain documented as heuristic.

## Overengineering Risks

- The repository now includes project templates, dogfood scaffolds, registry
  and BibTeX validation, structured notes and claims, citation audits, evidence
  maps, manuscript QA, reading sessions, imports/exports, sync planning, local
  search/indexing, backup/migration/integrity, rules, dashboard, evidence
  graph, claim lifecycle, workflow recipes, review packets, support bundles,
  compatibility inspection, incremental rebuilds, quality gates, and a docs
  cookbook.
- Do not add another major subsystem before real dogfooding generates concrete
  bugs. v3.5 should focus on tightening existing workflows, reducing CLI
  repetition, and adding transcript tests for core cookbook recipes.
- Keep graph exports, claim lifecycle sidecars, workflow recipes,
  review-packet imports, sync apply, indexed search, rebuild metadata, verbose
  support bundles, and forced migration/restore flows experimental until real
  projects prove their contracts.

## Stale Generated Reports

- `reports/index.md` is current for v3.4 and lists `hostile_review_latest.md`
  as the canonical current review.
- Historical reports are intentionally retained. Their main risk is cognitive
  noise, not incorrect behavior.
- The report index should continue excluding versioned hostile-review drafts
  and should be regenerated whenever new current release reports are added.

## Missing Tests

- Add transcript-style tests for the highest-value cookbook recipes:
  first project, add paper manually, validate metadata, generate note template,
  extract claims, evidence map, citation audit, dashboard, support bundle, and
  compatibility inspection.
- Add a test or CLI contract for empty review-packet behavior.
- Add stricter docs-command tests for subcommand flags used in cookbook pages.
- Notebook checks are structural and metadata-focused; they do not execute the
  notebooks.
- Strict release validation still needs an environment where Ruff and build
  tooling are installed and exercised.

## Recommended Blocker-Fix Sequence

No blocker fix is required before local dogfooding.

Recommended next sequence:

1. Keep v3.4 dogfooding focused on one real local project and record actual
   command friction.
2. Add a warning or `--allow-empty` contract for empty review packets.
3. Add transcript tests for the most important cookbook recipes.
4. Run strict release validation in a prepared dev environment or CI with
   `.[dev]` installed.
5. Continue extracting CLI helper seams only where behavior-preservation tests
   already exist.
6. Avoid new feature subsystems until real dogfooding identifies concrete
   failures.
