# Hostile Maintainer Review: Current Repository

Date: 2026-06-15

Scope: release-gate review of the current repository as if deciding whether it
is safe for local dogfooding and eventual external handoff. I inspected package
metadata, module layout, CLI behavior, stable/experimental docs, registry and
BibTeX workflows, notes and claims, evidence maps, draft/manuscript QA, reading
sessions, import/export, sync planning, search/indexing, backup/migration,
integrity, rule engine, dashboard, evidence graph, tests, docs, notebooks,
reports, synthetic data, data-safety boundaries, `.gitignore`, and git state.

## Release Verdict

**Needs blocker fixes before being treated as a clean dogfooding release.**

The package imports, the CLI entry point works, the full test suite passes, the
notebook checker passes, and representative smoke workflows run. The current
implementation is usable by the maintainer locally.

The repository is not clean enough for a serious dogfooding release because a
tracked public dogfood demo contains real-looking bibliography metadata and PDF
filename-derived starter lists. This conflicts with the repository's own rules
in `AGENTS.md`, which explicitly say not to commit private dogfood reference
paths, real PDF filenames, copied BibTeX metadata, or starter lists derived
from private files. The built-in data-safety audit also reports zero errors
despite this, so the safety tooling does not enforce the stated boundary.

## Validation Performed

- `git status --short --branch`: clean before report creation; branch is ahead
  of origin by local commits.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `2.0`.
- `python -m paper_workbench.cli --help`: passed; 32 top-level command groups.
- `python -m paper_workbench.cli graph --help`: passed.
- `python -m paper_workbench.cli dogfood --help`: passed.
- `python -m paper_workbench.cli dashboard --help`: passed.
- `python -m paper_workbench.cli validate-registry projects/zis_photocatalysis/registry.csv --strict`: passed.
- `python -m paper_workbench.cli validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict`: passed with a warning only.
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --limit 5 --no-audit-log`: passed.
- `python -m paper_workbench.cli graph build --project zis_photocatalysis`: passed.
- Representative evidence-map, manuscript QA, reading queue, and sync-plan
  commands: passed and wrote only ignored `scratch/` outputs.
- `python scripts/check_notebooks.py`: checked 8 notebooks; passed.
- `python scripts/data_safety_audit.py --out '' --strict`: checked 713 files;
  0 errors, 8 warnings.
- `python scripts/smoke_cli_workflow.py`: 21 smoke steps, 0 failures.
- `python scripts/smoke_cli_workflow.py --quick`: 14 smoke steps, 0 failures.
- `python scripts/performance_sanity.py`: failed by default because the default
  report path already exists.
- `python scripts/performance_sanity.py --out scratch/review_performance_sanity.md --force`: passed.
- `pytest`: 259 passed.
- `git ls-files` checks found no tracked PDFs, SQLite databases, `.paperwb`
  files, backup archives, `.idea` files, or Python caches.

## Release Blockers

1. **Tracked public dogfood demo violates the repo's own data-safety boundary.**

   Evidence: `public/demos/v2_0_dogfood_real/` is tracked and contains a
   populated real-project registry, copied BibTeX entries, note filenames, an
   Obsidian export, report outputs, and `reports/fyp_15_paper_plan.md` with
   PDF filename-derived starter shortlist and unmatched PDF filenames. It does
   not contain PDFs or copied paper full text, and its notes are blank, but it
   still includes real-looking paper titles, authors, journals, BibTeX keys,
   and PDF filenames.

   Why this blocks dogfooding release: this directly contradicts the current
   policy in `AGENTS.md` and the product boundary repeated throughout the docs.
   The project says dogfood planning can inspect private local files but must
   not commit copied BibTeX metadata, private filenames, or private starter
   lists. This is the exact scenario those rules were meant to prevent.

2. **The data-safety audit does not detect the most important current risk.**

   Evidence: `python scripts/data_safety_audit.py --out '' --strict` reports
   `0 error(s), 8 warning(s)` while the tracked public demo contains real
   bibliography metadata and filename-derived paper lists. The audit detects
   forbidden file suffixes, caches, secrets, absolute paths, and large text
   sidecars, but not committed real-looking bibliography corpora under a public
   demo path.

   Why this blocks release: maintainers could run the advertised safety audit,
   see zero errors, and assume the repository is clean when it is not clean
   under its own rules.

## High-Priority Issues

1. **Release identity is inconsistent after v2.1 work.**

   The code reports package version `2.0`, while current release reports and
   docs describe v2.1 evidence graph behavior. If the intended release is v2.1,
   metadata and release docs need a clear policy: either keep package metadata
   at `2.0` and describe v2.1 as unreleased/local, or update package metadata
   and changelog coherently.

2. **Command-surface docs disagree about stability.**

   - `docs/CLI_REFERENCE_V2.md` and `docs/EXPERIMENTAL_FEATURES_V2.md` classify
     many workflows as experimental.
   - `docs/CLI_SURFACE.md` still labels advanced imports, sync, index, files,
     reading, manuscripts, rules, backup, migrate, and other workflows as
     stable.
   - `docs/COMMAND_CONTRACTS_V2.md` does not include the new `graph` command
     group.

   This makes it unclear what an external user can rely on.

3. **API-surface docs are stale.**

   `docs/API_SURFACE.md` is still titled v1.8 and does not mention
   `paper_workbench.graph`, even though graph is now a public importable module
   with tests and CLI integration.

4. **The current public demo blurs "synthetic" versus "real" examples.**

   The repo now contains both synthetic fixtures and a real metadata-backed demo
   under `public/`. That is useful for the maintainer but risky for external
   release: a new user cannot tell from the top-level docs which data is safe
   reusable synthetic fixture data and which data came from a private real
   project.

5. **Default performance sanity script fails in a clean-looking working tree.**

   `python scripts/performance_sanity.py` fails unless `--force` or a different
   `--out` path is provided because it defaults to an already committed
   historical report. Release checks should either default to `scratch/`, print
   a clearer command, or require explicit output.

## Medium-Priority Issues

1. **The top-level CLI is too large to maintain comfortably.**

   `paper_workbench/cli.py` is over 3,000 lines and owns command parsing,
   validation, data loading, report writing, audit logging, and many workflow
   adapters. This has not broken tests, but it is now the highest-risk
   maintenance hotspot.

2. **Several feature modules are large enough to need stronger internal
   boundaries.**

   `rules.py`, `index.py`, `reading.py`, `sync.py`, `authoring.py`, and
   `graph.py` are all sizable. The risk is not raw size alone; it is that many
   modules own both data modeling and report formatting, which makes regression
   behavior harder to reason about.

3. **Notebooks lag behind the feature surface.**

   Static notebook validation passes, but only 8 notebooks exist and they stop
   at the v0.6-era workflows. Newer graph, dashboard, sync, reading, dogfood,
   manuscript, and safety workflows are covered by scripts/docs/tests rather
   than notebooks. That is acceptable if documented, but the notebook story is
   no longer representative of the full tool.

4. **Generated reports are numerous and partly stale.**

   There are 167 Markdown reports. Many are historical release artifacts from
   v0.x and v1.x. `reports/index.md` correctly indexes them, but the volume now
   makes release review noisy. A public release should either move historical
   reports into an archive folder or document that `reports/index.md` is the
   entry point.

5. **Graph analytics are correctly experimental but easy to overread.**

   The graph reports state that centrality is a local degree count, not a truth
   or quality score. Keep this warning prominent; graph-based "central paper"
   labels are exactly the sort of output users may misinterpret.

6. **Dashboard output is useful but noisy on the bundled synthetic project.**

   The dashboard correctly surfaces workspace and rule errors in
   `zis_photocatalysis`, but a new user may interpret bundled synthetic errors
   as product breakage. The quickstart should be explicit that these warnings
   are intentional training fixtures.

## Low-Priority Polish

- `docs/API_SURFACE.md` and `docs/CLI_SURFACE.md` still use older release labels
  in titles.
- `scripts/performance_sanity.py --help` says v0.3; the script still works with
  a custom output path, but the label is stale.
- The report index includes `hostile_review_latest.md` as a current v2.1 report,
  which is mechanically reasonable but semantically odd because the hostile
  review is a release-gate artifact rather than a feature report.
- The top-level docs are much cleaner than earlier versions, but there are
  still overlapping pages for CLI reference, CLI surface, command contracts,
  workflows, and getting started.
- Some historical data-safety reports still contain old absolute-path warnings.

## Data-Safety Risks

- **Blocking:** tracked public real dogfood metadata and PDF filenames under
  `public/demos/v2_0_dogfood_real/`.
- **Blocking:** data-safety audit reports zero errors despite the above.
- Ignored local `.paperwb/`, `.pytest_cache/`, `.idea/`, and `scratch/` files
  exist in the working tree but are not tracked.
- No tracked PDFs, SQLite databases, backup archives, or cache directories were
  found.
- No cloud, LLM, scraping, or publisher-bypass runtime dependency was found.

## Docs Mismatches

- `docs/CLI_SURFACE.md` overstates stability compared with
  `docs/CLI_REFERENCE_V2.md` and `docs/EXPERIMENTAL_FEATURES_V2.md`.
- `docs/COMMAND_CONTRACTS_V2.md` omits `graph`.
- `docs/API_SURFACE.md` is stale at v1.8 and omits `paper_workbench.graph`.
- `docs/TEST_MATRIX_V2.md` omits `tests/test_evidence_graph_v2_1.py`.
- The docs say not to commit private dogfood filename lists and copied BibTeX
  metadata, but the tracked public dogfood demo does exactly that.

## CLI Usability Issues

- The command surface is powerful but large: 32 top-level command groups.
- `paperwb --help` is complete but overwhelming for a first-time user.
- `scripts/performance_sanity.py` fails by default because it targets an
  existing committed report.
- The validation commands intentionally return 0 for error-level findings unless
  `--strict` is supplied. This is documented, but it remains a scripting footgun
  for users who expect validation errors to fail by default.

## Overengineering Risks

- The tool now includes registry, notes, claims, authoring, manuscript QA,
  reading sessions, sync, local files, indexing, backups, migrations, rules,
  dashboard, templates, dogfood, and graph. The feature set is broad enough that
  future work should be consolidation, not expansion.
- Avoid adding a graph database, embeddings, semantic matching, plugin
  marketplace, web app, cloud sync, or PDF full-text extraction by default.
- Keep graph analytics, manuscript matching, and dashboard next actions
  transparent and explicitly heuristic.

## Stale Generated Reports

- `reports/data_safety_audit_v0_10.md` is still the default output of
  `scripts/data_safety_audit.py`; current release reviews should avoid
  overwriting historical reports by default.
- `reports/performance_sanity_v0_3.md` is still the default output of
  `scripts/performance_sanity.py`, causing default failure.
- Many historical release reports are valid artifacts but make the `reports/`
  folder hard to scan manually.

## Missing Tests

- A safety test that fails when tracked `public/` demo files contain real
  bibliography metadata, copied BibTeX metadata, PDF filename-derived starter
  lists, or non-synthetic note filenames.
- A data-safety audit test covering the public dogfood metadata policy.
- Command-contract tests asserting `graph` is listed in v2 command contracts and
  test matrix docs.
- A regression test for `scripts/performance_sanity.py` default behavior, or a
  test that the documented invocation uses a non-conflicting output path.
- Optional docs consistency tests that compare stable/experimental command
  classifications across `CLI_SURFACE`, `CLI_REFERENCE_V2`, and
  `EXPERIMENTAL_FEATURES_V2`.

## Recommended Blocker-Fix Sequence

1. **Sanitize or remove the tracked real dogfood demo.**
   Replace `public/demos/v2_0_dogfood_real/` with a synthetic public demo, or
   move the real metadata-backed demo to an ignored private path. Do not keep
   real paper titles, copied BibTeX metadata, PDF filenames, or starter lists in
   tracked files.

2. **Harden the data-safety audit.**
   Add checks for real-looking public dogfood metadata and filename-derived PDF
   lists. Make the current public-demo violation fail before claiming release
   readiness.

3. **Regenerate affected reports.**
   Regenerate `reports/index.md`, a current data-safety report, and any dogfood
   release reports after sanitizing the demo.

4. **Align release identity and surface docs.**
   Decide whether this tree is package version `2.0` with v2.1 experimental
   docs, or an actual v2.1 package. Update `CHANGELOG.md`, `pyproject.toml`,
   `CLI_SURFACE`, `COMMAND_CONTRACTS_V2`, `API_SURFACE`, and `TEST_MATRIX_V2`
   accordingly.

5. **Fix release-script defaults.**
   Make `scripts/performance_sanity.py` default to `scratch/` or require an
   explicit `--out` path so a default release check does not fail due to an
   existing historical report.

6. **Run validation again.**
   Run `pytest`, `python scripts/smoke_cli_workflow.py`, `python
   scripts/check_notebooks.py`, `python scripts/data_safety_audit.py --out ''
   --strict`, and representative `paperwb graph`, dashboard, registry, BibTeX,
   manuscript QA, sync-plan, and backup/integrity commands.

