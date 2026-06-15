# Hostile Maintainer Review: Current Repository

Date: 2026-06-15

Scope: standalone release-gate review of the current Paper Intelligence
Workbench repository as if deciding whether this version is safe for local
dogfooding. I inspected package metadata, architecture, CLI behavior,
stable/experimental docs, registry and BibTeX workflows, notes and claims,
evidence maps, manuscript/draft QA, reading sessions, imports/exports,
sync/conflict planning, search/indexing, backup/migration/integrity, rule
engine, dashboard, evidence graph, claim lifecycle, tests, docs, notebooks,
reports, synthetic data, data-safety boundaries, `.gitignore`, and git state.

## Release Verdict

**Ready for cautious local dogfooding, but not clean enough for an external
release without high-priority documentation and release-hygiene fixes.**

The current repository is materially healthier than the previous hostile review
claimed. The package imports, `paperwb --help` works, full pytest passed,
notebook validation passed, the strict data-safety audit reported zero errors,
and representative stable and experimental workflows ran without crashes.

There are no release blockers from this pass. The main risk is that the project
now has a very broad command surface and a large archive of historical reports,
while several visible labels still point at older release phases. That will
confuse external users even though the local workflows themselves are usable.

## Validation Performed

- `git status --short --branch`: clean before creating this review report;
  branch was `main...origin/main [ahead 13]`.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `2.2`.
- `python -m paper_workbench.cli --help`: passed and listed the current top-level
  command surface, including `graph`, `claim-review`, and `contradictions`.
- `python -m pytest -q`: passed.
- `python scripts/smoke_cli_workflow.py --quick`: 14 smoke steps, 0 failures.
- `python scripts/data_safety_audit.py --strict --out /private/tmp/paperwb_data_safety_review.md`:
  checked 650 repository files, 0 errors, 7 warnings.
- `python scripts/validate_notebooks.py`: validated 8 notebooks.
- `python scripts/check_notebooks.py`: listed 8 notebook titles successfully.
- `python -m paper_workbench.cli validate-registry projects/zis_photocatalysis/registry.csv --strict`:
  passed with no findings.
- `python -m paper_workbench.cli validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict`:
  passed with one expected sparse synthetic BibTeX warning.
- `python -m paper_workbench.cli dashboard --project zis_photocatalysis --limit 3 --no-audit-log`:
  passed.
- `python -m paper_workbench.cli graph summary --project zis_photocatalysis`:
  passed, but printed a stale `v2.1` title.
- `python -m paper_workbench.cli claim-review queue --project zis_photocatalysis --limit 2`:
  passed.
- `python -m paper_workbench.cli manuscript citations drafts/synthetic_good_section.md --project zis_photocatalysis`:
  passed.
- `python -m paper_workbench.cli rules run --project zis_photocatalysis`:
  passed and reported expected synthetic fixture findings.
- Tracked artifact scan found no tracked PDFs, SQLite databases, `.paperwb`
  files, backup archives, `.idea` files, or Python cache files.

## Release Blockers

None found in this pass.

This verdict assumes the target is **local dogfooding**, not a polished public
release. The repository still needs high-priority cleanup before it should be
presented to external users as stable.

## High-Priority Issues

1. **Visible release labels are stale in active commands and scripts.**

   Evidence: `paperwb graph summary --project zis_photocatalysis` prints
   `# Evidence Graph Summary v2.1` while the package reports version `2.2`.
   `paper_workbench/graph.py` also defaults graph report titles to v2.1, and
   `scripts/smoke_cli_workflow.py` still defaults to `CLI Smoke Workflow v2.0rc`.

   Why it matters: users will not know whether the generated report belongs to
   the current release or a historical snapshot. This undermines confidence in
   release-readiness reports even though the command behavior works.

2. **Documentation still has release-state drift around graph and current v2
   workflows.**

   Evidence: `docs/STABLE_SURFACE_V2.md` says "`graph` is experimental in
   v2.1" in a v2.2 repository. Current docs correctly list `graph`,
   `claim-review`, and `contradictions` elsewhere, but the wording is not
   consistently current.

   Why it matters: stable versus experimental boundaries are central to this
   repo's external-user story. Outdated version labels make the boundary look
   accidental rather than intentional.

3. **The data-safety audit default output path is historical and easy to
   misuse.**

   Evidence: running `python scripts/data_safety_audit.py --strict` without an
   explicit `--out` rewrites `reports/data_safety_audit_v0_10.md`. I restored
   that accidental rewrite before creating this report.

   Why it matters: a maintainer following the obvious command can mutate an old
   tracked release report while trying to check current safety. CI avoids this
   with a temporary output path, but the local maintainer path is footgun-prone.

4. **The top-level CLI exposes stable and experimental workflows side by side
   with no status markers.**

   Evidence: `paperwb --help` lists a large command surface covering registry,
   templates, dogfood, import, sync, claims, graph, rules, dashboard, files,
   draft/manuscript QA, reading, backup, migration, export, and synthetic data.
   The command list is complete, but it does not tell a first-time user which
   commands are stable, experimental, or risky.

   Why it matters: the docs carry this classification, but the CLI is the first
   interface many users will see. Users can discover advanced workflows before
   seeing the safety model.

## Medium-Priority Issues

1. **`paper_workbench/cli.py` is the main maintenance hotspot.**

   It is 3,336 lines and owns parsing, dispatch, report writing, output safety,
   and adapters for nearly every subsystem. This has not broken tests, but it
   raises the cost of reviewing future CLI changes.

2. **Several feature modules combine modeling, analysis, and Markdown rendering.**

   Large modules include `rules.py` at 957 lines, `authoring.py` at 799,
   `index.py` at 786, `reading.py` at 764, `sync.py` at 754, `graph.py` at 700,
   `drafts.py` at 700, `registry.py` at 666, and `importers.py` at 661. This is
   survivable for local tooling, but it makes regression ownership blurry.

3. **Generated reports are too numerous for manual release review.**

   There are 174 Markdown reports under `reports/`. Many are legitimate
   historical artifacts, but the folder is now difficult to scan without an
   index. A future public release should archive or clearly separate historical
   burn-cycle reports from current examples.

4. **Notebook coverage lags behind the current feature surface.**

   Notebook JSON validation passes for 8 notebooks, but newer workflows such as
   dogfood onboarding, graph, claim lifecycle, dashboard, sync, and manuscript
   QA are primarily represented by scripts, docs, and tests. That is acceptable
   if documented, but users should not infer that notebooks cover the full v2
   workflow surface.

5. **The bundled synthetic project intentionally reports many warnings.**

   Dashboard, rules, citation audit, and workspace health checks correctly flag
   weak evidence in `zis_photocatalysis`. A new user may read that as product
   breakage unless the quickstart keeps emphasizing that these are training
   fixtures.

## Low-Priority Polish

- Historical v2.0rc reports still mention `2.0.0rc1`; these are valid
  historical artifacts but noisy when searching for current release state.
- `reports/hostile_review_latest.md` was stale before this update and still
  appeared in search results as if it were current.
- The docs have overlapping pages for CLI reference, command contracts, stable
  surface, API surface, workflows, and getting started. This is manageable but
  increases the chance of drift.
- Some report titles remain tied to their feature introduction version rather
  than the current package version.

## Data-Safety Risks

- Strict data-safety audit result: 0 errors, 7 warnings.
- The 7 warnings are local absolute-path patterns in historical reports and
  tests, including `/private/...` examples used by hygiene checks.
- No tracked PDFs, cache databases, backup archives, `.paperwb` logs, `.idea`
  files, or Python caches were found.
- The public dogfood demo appears synthetic/public after the v2.0 cleanup, but
  this boundary should stay guarded because dogfood planning can inspect private
  local reference folders.
- No cloud, LLM, publisher scraping, OCR, or PDF full-text extraction dependency
  was found.

## Docs Mismatches

- `docs/STABLE_SURFACE_V2.md` references graph as experimental "in v2.1" rather
  than the current v2 line.
- Graph report defaults still emit v2.1 titles from `paper_workbench/graph.py`.
- Smoke workflow report defaults still say v2.0rc.
- Data-safety audit default output still targets a v0.10 report.
- Historical release-readiness reports are not stale in the archival sense, but
  they appear in broad `rg` searches and can look like current instructions.

## CLI Usability Issues

- `paperwb --help` is comprehensive but intimidating for a first-time user.
- Stable and experimental commands are not labeled in top-level help.
- Advanced write-capable groups such as `sync`, `backup`, `migrate`,
  `claim-review`, and `contradictions` are discoverable without the safety
  context shown in docs.
- Validation commands require `--strict` for nonzero exits on findings; this is
  documented but remains a scripting trap.

## Overengineering Risks

- The project already includes registry validation, BibTeX checks, note parsing,
  claim extraction, evidence maps, authoring reports, draft/manuscript QA,
  reading sessions, local file workflows, imports/exports, sync planning,
  search/indexing, backup/migration/integrity, rules, dashboard, templates,
  dogfood scaffolds, evidence graph, and claim lifecycle.
- Future work should favor consolidation, docs alignment, and dogfooding over
  new major subsystems.
- Avoid adding graph databases, embeddings, semantic contradiction inference,
  cloud sync, plugin marketplaces, web apps, or PDF full-text extraction by
  default.

## Stale Generated Reports

- `reports/data_safety_audit_v0_10.md` is still used as the default output of
  the current data-safety script.
- Graph summary/report defaults still title generated output as v2.1.
- Smoke workflow defaults still title generated output as v2.0rc.
- Historical v0.x, v1.x, v2.0rc, and v2.1 reports remain useful as audit trail
  artifacts but should not be treated as current release guidance.

## Missing Tests

- A regression test that the default data-safety audit does not rewrite a
  historical release report, or that docs always invoke it with a scratch/temp
  output.
- A regression test that active report generators do not emit stale release
  labels for the current package line, unless intentionally version-pinned.
- A docs consistency check comparing command stability across
  `STABLE_SURFACE_V2`, `CLI_REFERENCE_V2`, `COMMAND_CONTRACTS_V2`, and top-level
  CLI help.
- A first-user smoke test that asserts top-level help points users toward
  stable starting commands before advanced experimental workflows.

## Recommended Blocker-Fix Sequence

1. No blocker fix is required before local dogfooding.
2. Fix high-priority release-label drift: graph report titles, smoke workflow
   default title, and the `docs/STABLE_SURFACE_V2.md` graph wording.
3. Change `scripts/data_safety_audit.py` default output behavior so local manual
   use does not rewrite a historical v0.10 report, or document a scratch output
   path everywhere.
4. Improve top-level CLI help text or add a `paperwb workflows`/`paperwb
   getting-started` style pointer so users see stable starting paths before
   advanced commands.
5. Add the missing release-hygiene regression tests listed above.
6. Defer broad architecture refactors until after real dogfooding produces
   evidence about which workflows are actually used.
