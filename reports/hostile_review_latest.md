# Hostile Maintainer Review: Latest v0.6 State

## Release Verdict

**Verdict: conditional release candidate, not a polished external release.**

The repository is materially useful and the core test suite is green. The local-first boundary is mostly respected: no cloud APIs, LLM APIs, publisher scraping, tracked PDFs, or tracked SQLite caches were found. The CLI covers the advertised workflows and the v0.6 authoring workbench keeps the right conceptual boundary: planning aids, not final prose.

However, I would not tag this for broad external users until the high-priority issues below are fixed. The biggest problems are not catastrophic data loss; they are non-atomic multi-output writes, weak CI/release automation, authoring-report regression gaps, and confusing/stale generated-report history.

Validation performed during review:

- `python -m pytest -q` passed.
- `python scripts/validate_notebooks.py` passed.
- `python -m paper_workbench.cli report evidence-matrix --project zis_photocatalysis --theme charge-separation --out /private/tmp/hostile_matrix.md --csv-out /private/tmp/hostile_matrix.csv --json-out /private/tmp/hostile_matrix.json --force` passed.
- `python -m paper_workbench.cli report all --project zis_photocatalysis --reports-dir /private/tmp/should_be_rejected` correctly failed with a project-path override error.
- `python -m paper_workbench.cli writing-packet --project zis_photocatalysis --theme photocorrosion --out /private/tmp/hostile_packet.md --force` passed.
- Tracked-file scan found no tracked `.paperwb/`, SQLite DBs, PDFs, Python caches, `.DS_Store`, `.idea`, or notebook checkpoints.

## Release Blockers

None found that would require halting a source-code preview release.

This is not the same as “ready for broad users.” The high-priority issues below are still serious enough that I would fix them before announcing v0.6 externally.

## High-Priority Issues

1. **Evidence-matrix multi-output writes are not atomic.**

   `paperwb report evidence-matrix` writes the Markdown report before attempting `--csv-out` and `--json-out` writes. If a later output path already exists and `--force` is not set, the command exits with code 2 after leaving the earlier Markdown file behind. I reproduced this with `/private/tmp/hostile_partial_matrix_seq.md` and an existing CSV path: stderr reported the CSV overwrite error after stdout had already printed `Wrote /private/tmp/hostile_partial_matrix_seq.md`.

   Relevant code: `paper_workbench/cli.py` lines 496-509.

   Risk: users see a failed command but still get partial generated output. This undermines the project’s non-destructive/reproducible-output story.

   Fix: preflight every requested output path before writing any of them, or write all outputs to temp files and atomically replace only after all renders succeed. Add a CLI regression test where existing `--csv-out` prevents Markdown creation.

2. **No CI configuration is present.**

   There is no `.github/` directory or visible CI workflow. Local tests pass, but external users and maintainers have no automated gate for pytest, notebook validation, packaging import, CLI smoke tests, or tracked-artifact hygiene.

   Risk: parser/report regressions can land silently, especially with this many generated fixtures and CLI workflows.

   Fix: add a minimal CI workflow that runs `python -m pytest -q`, `python scripts/validate_notebooks.py`, package import, `python -m paper_workbench.cli --help`, and a tracked-file hygiene scan.

3. **Authoring reports lack golden/regression coverage.**

   v0.6 adds evidence matrices, claim banks, citation banks, paragraph plans, subsection readiness, and writing packets, but the existing golden report suite only covers older stress reports under `tests/golden/stress_zis_photocatalysis/`. The new authoring outputs have focused unit/CLI tests, not stability snapshots or robust section/count regression checks.

   Risk: writing-facing reports can silently change semantics or omit warnings while tests still pass.

   Fix: add authoring golden snapshots or stable count/section tests for at least one strong theme, one weak theme, and one missing-evidence theme.

4. **Current working tree contains an untracked old hostile review report.**

   `git status --short --branch` shows `?? reports/hostile_review_v0_2.md`. This file is not tracked, but it is also not ignored. It is easy to accidentally stage during release cleanup.

   Risk: stale or irrelevant review artifacts get committed and confuse users.

   Fix: decide whether to track it, delete it, or ignore old hostile-review drafts. Do not leave it floating in a release workspace.

5. **Generated report history is confusing and partly stale.**

   `reports/v0_6_recommended_patch_plan.md` still describes the old search/indexing-oriented v0.6 plan, while current v0.6 is the authoring workbench and `reports/v0_7_recommended_patch_plan.md` is the active next plan. Keeping historical generated reports is reasonable, but the top-level reports directory now mixes current release artifacts with old phase artifacts without a clear index or “current vs historical” marker.

   Risk: external users can read an old report and misunderstand the current product direction.

   Fix: update `reports/index.md` after v0.6, add “historical” labels to older patch plans, or move historical release reports into versioned subdirectories.

## Medium-Priority Issues

1. **`paperwb report all --out ...` silently ignores `--out`.**

   The implementation only uses `--out` when exactly one report is selected. With `report all`, it writes multiple files to the reports directory. That is defensible, but the CLI does not reject or explain `--out` for multi-report generation.

   Relevant code: `paper_workbench/cli.py` lines 485-500.

   Fix: reject `--out` with `report all`, or document and print that it is ignored.

2. **Readiness scoring can look more authoritative than it is.**

   The v0.6 docs correctly say the score is not a truth score, but the report still emits a numeric `Score: N/100` and statuses such as `ready_to_outline`. The rubric is transparent, but users may over-trust it, especially when missing BibTeX only costs five points and missing citations do not block readiness.

   Relevant code: `paper_workbench/authoring.py` lines 560-619.

   Fix: consider renaming to “Completeness score,” make missing BibTeX a blocker for included papers, and add a stronger warning in generated readiness reports.

3. **Citation-bank roles are rule-based but presented as categorical groups.**

   Citation-bank grouping depends entirely on evidence-type labels and missing-note checks. A mislabeled claim can move a paper into “primary evidence” or “mechanism,” and the report does not show the exact rule used per paper.

   Relevant code: `paper_workbench/authoring.py` lines 350-419.

   Fix: include “role reason” text in citation-bank rows, such as `experimental_result claim with location` or `no linked claims`.

4. **Search sidecar indexing is shallow by design, but docs and UX should be clearer.**

   `build_index_records` uses `Path(text_dir).glob("*.txt")`, not recursive discovery. That is acceptable if intentional, but users may expect project text folders to support subdirectories.

   Relevant code: `paper_workbench/index.py` lines 345-360.

   Fix: document “top-level `.txt` only” wherever sidecars are described, or add an explicit `--recursive-text` flag later.

5. **Notebook execution is validated manually, not by the repository test suite.**

   Notebook JSON validation is scripted, but executed notebooks are not part of pytest or CI. The v0.6 notebooks were fixed to run from notebook CWD, but future notebook regressions can still slip in unless CI executes them or a smoke subset.

   Fix: either add a lightweight notebook execution smoke script or CI job for the newest workflow notebooks.

## Low-Priority Polish

- `cmd_report` computes BibTeX audit, citation audit, and workspace health before knowing which report will be rendered. This is inefficient for simple reports and makes unrelated malformed files capable of breaking a report that does not need them.
- Report naming is inconsistent across eras: root reports, v0.2 reports, v0.3 stress reports, v0.4 import reports, v0.5 search reports, and v0.6 authoring reports all live together.
- `paperwb checklist` has older theme-matching logic than the v0.6 authoring reports and may behave differently for aliases or normalized names.
- The project still has no packaged console smoke after editable install in CI because no CI exists.
- `exports.py` directory exports reject non-empty output directories even with `--force`; this is safe but the word “force” can mislead users.

## Missing Tests

- Multi-output preflight/atomicity test for `report evidence-matrix --out --csv-out --json-out`.
- `report all --out` behavior test.
- Authoring golden or stable regression tests for v0.6 reports.
- Citation-bank role-reason tests covering each evidence type.
- Readiness-score tests for missing BibTeX on included papers.
- Notebook execution smoke in automated validation, not just JSON validation.
- CLI smoke test confirming no old substring search behavior changed after authoring additions.
- Test that sidecar indexing is intentionally top-level-only, or test recursive behavior if added.
- CI workflow itself is missing.

## Documentation Mismatches

- `reports/v0_6_recommended_patch_plan.md` is historical but reads like the next plan for v0.6, while the current v0.6 release is already authoring-focused.
- `reports/index.md` appears to predate v0.6 authoring reports and does not clearly distinguish current reports from historical artifacts.
- Sidecar indexing docs should be explicit about top-level-only `.txt` discovery.
- CLI docs should state that `report all` ignores/rejects `--out` once the behavior is decided.
- README describes the workbench as for roughly 10 to 100 papers; stress fixtures demonstrate 100+ papers total but not necessarily one polished real 100-paper user project with CI-backed release automation.

## CLI Usability Problems

- Multi-output evidence matrix can partially succeed after a failing later output.
- `report all --out` does not have clear semantics.
- `--force` means overwrite for file exports but still refuses non-empty directory exports; safe, but not obvious.
- `paperwb report ... --project ... --out reports/foo.md` writes to the caller’s `reports/`, not the project reports directory. This is consistent with explicit `--out`, but users may expect project-relative paths.
- `paperwb search --indexed` error does include a rebuild hint, which is good.

## Data-Safety Risks

- No cloud, LLM, scraping, tracked PDFs, or tracked SQLite DBs found.
- Ignored `.paperwb/index.sqlite`, `.pytest_cache`, and `__pycache__` are present locally but not tracked.
- Backup bundles default to not including PDFs, which is correct.
- Importers preserve non-empty registry fields unless `--fill-missing` is used, and even then only blank fields are filled.
- The main data-safety issue found is partial multi-output writes for evidence matrices.
- The untracked `reports/hostile_review_v0_2.md` is a release hygiene risk.

## Overengineering Risks

- The authoring workbench is close to becoming a writing-assistant surface. Keep it as matrices, banks, checklists, and planning reports. Do not add polished prose generation.
- Readiness scoring can become pseudo-objective. Keep the scoring small, transparent, and explicitly non-scientific.
- SQLite index should remain rebuildable cache, not source-of-truth storage.
- Import conflict resolution could become complex quickly; keep dry-run reports and explicit user review as the default.

## Recommended Fix Sequence

1. Fix evidence-matrix multi-output atomicity and add tests.
2. Add a minimal CI workflow with pytest, notebook JSON validation, package import, CLI help, and tracked-artifact hygiene.
3. Add v0.6 authoring report regression coverage.
4. Resolve the untracked `reports/hostile_review_v0_2.md` workspace hygiene issue.
5. Refresh `reports/index.md` and label/move historical reports.
6. Decide and document/reject `report all --out`.
7. Clarify sidecar discovery semantics.
8. Add role-reason text to citation banks and strengthen readiness-score language.
