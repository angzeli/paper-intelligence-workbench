# Hostile Maintainer Review: v1.7 Current Repository

Date: 2026-06-11

Scope: standalone release review of the current repository as if it were about
to be handed to external users. I inspected package metadata, CLI behavior,
project profiles, registry/BibTeX/note/claim workflows, reports, authoring and
manuscript tooling, import/export, sync, local files, indexed search, rule
engine, dashboard, v1.7 project templates, tests, notebooks, docs, generated
reports, synthetic data, CI/release scripts, and repo hygiene. No implementation
files were modified during inspection.

## Release Verdict

Do not tag this exact tree as a polished external v1.7 release yet. The package
imports, full pytest suite passes, CLI smoke workflow passes, notebook JSON
checks pass, and I did not find a tracked PDF/cache/SQLite artifact or a
cloud/LLM/scraping dependency. The new template feature is useful and mostly
non-destructive.

However, the v1.7 template release has visible release-quality defects:
finance, ML-methods, and generic templates produce contradictory theme coverage
thresholds between their generated `themes.json` metadata and their generated
`rules.json` rules; the current report index misclassifies v1.7 template
overview reports as legacy unversioned reports; and stale ignored package
artifacts for version `1.1.0` remain in the local workspace. These are not
data-loss bugs, but they are the kind of issues an external user or maintainer
will hit immediately when dogfooding the new template workflow.

Verdict: **hold external v1.7 release until the high-priority template and
release-index fixes below land**. Internal/local use remains acceptable.

## Validation Performed

- `git status --short`: clean before report creation.
- `python -m pytest -q`: passed, 233 tests.
- `python scripts/smoke_cli_workflow.py --quick --out <tmp>/paperwb_hostile_review_smoke_v1_7.md`: passed, 14 steps.
- `python scripts/data_safety_audit.py --out <tmp>/paperwb_hostile_review_data_safety_v1_7.md --strict`: passed with 0 errors and 8 historical absolute-path warnings.
- `python scripts/check_notebooks.py`: checked 8 notebooks.
- `python scripts/clean_room_install_check.py --quick --out <tmp>/paperwb_hostile_clean_room_v1_7.md`: passed, 7 steps.
- `python -m paper_workbench.cli --help`: passed; `template` is exposed.
- `python -m paper_workbench.cli template --help`: passed.
- `python -m paper_workbench.cli template list`: passed; four templates are listed.
- `python -m paper_workbench.cli template inspect photocatalysis`: passed.
- `python -m paper_workbench.cli template inspect finance`: passed.
- `python -m paper_workbench.cli template create finance --project review_finance --root <tmp>`: passed.
- `paperwb rules validate-config --project` on all four generated template projects: passed.
- `paperwb doctor`, `dashboard`, and `rules run` on generated template projects: passed but exposed threshold inconsistencies.
- `python -m paper_workbench.cli validate-registry data/registries/example_papers.csv`: passed with expected synthetic duplicate warnings/errors.
- `python -m paper_workbench.cli validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv`: passed with expected synthetic BibTeX warnings/errors.
- `git ls-files "*.pdf" "*.sqlite" "*.db" ".paperwb/*" "*/.paperwb/*" "__pycache__/*" "*/__pycache__/*" ".pytest_cache/*" "build/*" "dist/*" "*.egg-info/*"`: no tracked forbidden artifacts found.

## Release Blockers

None found that would destroy user data, require network/cloud services, commit
copyrighted content, make the package unimportable, or break the CLI entry
point. The release should still be held for the high-priority v1.7 defects
below because they directly affect the newly advertised template workflow.

## High-Priority Issues

1. **Generated template theme thresholds contradict generated rule thresholds.**

   Evidence: a direct check of `paper_workbench.templates` reports mismatches
   for every finance theme, every ML-methods theme, and the generic
   `future-work` theme. Example output:

   - `finance` themes have `min_papers=3` in `themes.json` but generated
     `finance.*.min_papers` rules require `2`.
   - `ml-methods` themes have `min_papers=3` in `themes.json` but generated
     `ml.*.min_papers` rules require `2`.
   - `generic.future-work` has `min_papers=1` in `themes.json` but the generated
     custom rule requires `2`.

   User-visible impact: `paperwb doctor --project review_finance` reports
   `target is 3` for theme papers, while `paperwb rules run --project
   review_finance` also reports `finance.valuation.min_papers ... target is 2`.
   The dashboard then mixes both thresholds. This undermines the central v1.7
   promise that templates create clear onboarding expectations. Make theme
   metadata and custom rule thresholds agree, then add a test that every
   built-in template has matching `theme.min_papers` and `theme_min_papers`
   rule values.

2. **The report index is stale/misleading for the new v1.7 reports.**

   Evidence: `reports/index.md` has a "Current v1.7 Release Reports" section,
   but it only lists `dogfooding_workflow_v1_7.md`,
   `hostile_review_latest.md`, and `release_readiness_v1_7.md`. The required
   v1.7 reports `template_photocatalysis_overview.md`,
   `template_finance_overview.md`, and `template_ml_methods_overview.md` are
   instead listed under "Legacy Unversioned Reports." They are unversioned by
   filename because the task required those exact names, but they are not
   legacy. Update report-index generation or the checked-in index so current
   template overview reports appear in the current v1.7 release section. Add a
   release-hygiene test for that classification.

3. **Stale ignored build artifacts can confuse a maintainer preparing release artifacts.**

   Evidence: the filesystem contains ignored local build artifacts:
   `dist/paper_intelligence_workbench-1.1.0-py3-none-any.whl`,
   `dist/paper_intelligence_workbench-1.1.0.tar.gz`, `build/`, and
   `paper_intelligence_workbench.egg-info/`, while `pyproject.toml` and
   `paper_workbench.__version__` are `1.7.0`. These files are ignored and not
   tracked, so an external clone is clean. But in this release workspace, a
   maintainer could easily upload or inspect stale `1.1.0` artifacts by mistake.
   Clean ignored build artifacts before any public release and consider adding
   a release-check script that fails when local `dist/` artifacts do not match
   the current version.

## Medium-Priority Issues

1. **`clean_room_install_check.py` still writes a v1.0-rc titled report.**

   Evidence: running `python scripts/clean_room_install_check.py --quick --out
   <tmp>/paperwb_hostile_clean_room_v1_7.md` produced a report headed
   `# Current-Environment Release Check v1.0-rc`. The command passed, but the
   label is stale for v1.7 and weakens trust in release-readiness evidence.
   Update the script to derive or accept the current version in the report
   title.

2. **The data-safety audit still reports historical absolute-path warnings.**

   Evidence: the strict data-safety audit reports 0 errors but 8 warnings,
   including historical reports with `/private/...` or `/Users/...` paths and
   two tests containing `/private/...` strings. This is not a release blocker,
   but a public repo should avoid normalizing machine-local paths in committed
   reports.

3. **`paperwb template create` prints absolute paths when `--root` is outside the current directory.**

   Evidence: `paperwb template create finance --project review_finance --root
   <tmp>` prints absolute paths for every written template file. That is
   useful for local confirmation, but users may paste command output into
   committed notes/reports. Prefer workspace-relative display when possible,
   matching the existing `profile_summary` behavior.

4. **Generated report sprawl is making the current release hard to audit.**

   Evidence: `reports/index.md` indexes 136 Markdown reports. Historical
   artifacts are useful for traceability, but the current release signal is
   diluted. The index helps, but it needs stronger current/historical grouping
   and should avoid classifying current required reports as legacy.

5. **The CLI module remains very large.**

   `paper_workbench/cli.py` wires every command group in one file. This is
   working, but it increases regression risk as new feature groups are added.
   Post-release, split parser/handler wiring into focused modules.

## Low-Priority Polish

- Template overview reports are unversioned by filename while most recent
  release artifacts are versioned. This is acceptable because the task required
  exact filenames, but it increases report-index complexity.
- The finance template docs correctly say "not investment advice," but the
  finance template report should keep that boundary prominent in every overview
  section if it becomes more detailed.
- `paperwb project list` output is concise but not discoverable for template
  users; a `template create` success message could suggest `doctor`,
  `dashboard`, and `rules validate-config` next.
- Notebook coverage is structurally valid but still trails late feature growth.
  v1.7 added a script, not a notebook, which is acceptable under the task but
  leaves docs-site onboarding more script-heavy than notebook-heavy.

## Missing Tests

- Template threshold consistency test: every built-in template should have
  matching `theme.min_papers` metadata and `theme_min_papers` rule thresholds.
- Report-index classification test: required current v1.7 template reports
  should appear under the current release section, not legacy unversioned
  reports.
- Release-artifact hygiene test or script: fail or warn when ignored `dist/`
  artifacts do not match `paper_workbench.__version__`.
- Template create display-path test if the CLI is changed to avoid absolute
  path output for external `--root` use.
- A smoke step that runs `rules run` or `dashboard` on every built-in template,
  not only the photocatalysis template.

## Documentation Mismatches

- `reports/index.md` misclassifies current v1.7 template overview reports as
  legacy unversioned reports.
- `scripts/clean_room_install_check.py` generates a v1.0-rc titled report even
  in a v1.7 repository.
- Template docs do not mention that finance/ML/generic currently have
  inconsistent theme-vs-rule paper thresholds. That should be fixed in code,
  not documented as expected behavior.

## CLI Usability Problems

- Finance, ML-methods, and generic template users receive contradictory
  coverage targets across `doctor`, `rules run`, evidence-map findings, and
  dashboard next actions.
- Template creation with an external `--root` prints absolute local paths for
  all generated files.
- The top-level CLI has many command groups. Help output is accurate, but new
  users may need the quickstart/template docs rather than raw `--help`.

## Data-Safety Risks

- No tracked PDFs, SQLite DBs, `.paperwb` logs, Python caches, build outputs,
  or IDE folders were found.
- No cloud, LLM, publisher-scraping, or copyrighted-content dependency risk was
  found in inspected commands.
- Ignored local caches and build artifacts exist in the maintainer workspace:
  `.paperwb/`, `.pytest_cache/`, `paper_workbench/__pycache__/`, `build/`,
  `dist/`, and egg-info. They are ignored, but release maintainers should clean
  them before packaging or screenshots.
- Data-safety audit warnings for historical absolute paths remain unresolved.

## Overengineering Risks

- The repo has many feature layers: registry, BibTeX, notes, claims, evidence
  maps, authoring, draft/manuscript QA, local files, indexed search, sync,
  backup/migration, rules, dashboard, reading sessions, and now templates.
  This is useful, but release confidence increasingly depends on contract tests
  and current docs staying synchronized.
- The dashboard and rule engine can surface the same underlying issue through
  multiple adapters. The template threshold bug shows how duplicated validation
  channels can become inconsistent if the source of truth is not clear.
- Generated reports are numerous enough that stale or misclassified reports can
  mislead maintainers. Future releases should keep one canonical current index
  and automate its correctness.

## Recommended Fix Sequence

1. Fix template threshold consistency in `paper_workbench/templates.py` so
   `themes.json` and generated `rules.json` agree for all built-in templates.
2. Add tests for built-in template threshold consistency and run template
   `doctor`/`rules run` smoke checks for all templates.
3. Regenerate affected template overview reports and `reports/index.md`, and
   add a release-hygiene assertion that current v1.7 template overview reports
   are classified as current, not legacy.
4. Clean ignored local build artifacts before any public packaging step; add a
   release check for stale `dist/` artifact versions if release packaging will
   happen from this workspace.
5. Update the clean-room release-check report title so it reflects the current
   package version.
6. Rerun pytest, smoke CLI workflow, data-safety audit, notebook checks, and
   representative template commands before tagging or handing off.
