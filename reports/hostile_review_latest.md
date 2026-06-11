# Hostile Maintainer Review: v1.4 Current Repository

Date: 2026-06-11

## Release Verdict

Do not tag or announce a broad external release from the current tree without a short release-hygiene patch first.

I did not find a current data-loss release blocker in the inspected paths. The package imports, the full test suite passes, notebooks validate structurally, the new manuscript QA CLI fails safely on common bad inputs, and tracked-file hygiene does not show PDFs, cache databases, `.paperwb` directories, or secrets.

However, the repository is not presentation-clean for external users. The current report index still advertises v1.3 as current, the docs-site index and matrices omit v1.4 manuscript QA artifacts, and several generated user-facing reports can emit absolute local paths. Those are high-priority issues because this project repeatedly promises reproducible, portable, local-first outputs.

## Review Scope

Inspected:

- package metadata and package layout
- CLI command surface, including `paperwb manuscript`
- project profiles and synthetic projects
- registry, BibTeX, note parsing, claim extraction, evidence maps, citation audits, authoring reports, draft/manuscript audit, local search/indexing, local files, imports/exports, sync, backups, migrations, reading sessions, and safety utilities
- tests, CI workflow, smoke scripts, and notebook checkers
- README, docs-site pages, detailed docs, generated reports, and release-readiness notes
- synthetic data and tracked-file hygiene

Validation commands run:

- `git status --short --branch --ignored=matching`
- `python -m pytest -q`
- `python -m pytest --collect-only -q`
- `python scripts/check_notebooks.py`
- `python scripts/data_safety_audit.py --out scratch/hostile_review_v1_4_data_safety.md --strict`
- `python scripts/smoke_cli_workflow.py --quick --out scratch/hostile_smoke_quick.md`
- `python scripts/clean_room_install_check.py --quick --out scratch/hostile_clean_room_check.md`
- `paperwb --help`
- `paperwb manuscript --help`
- `paperwb project list`
- `paperwb project validate zis_photocatalysis`
- `paperwb validate-registry projects/zis_photocatalysis/registry.csv`
- `paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv`
- `paperwb report evidence-map --project zis_photocatalysis --out scratch/hostile_evidence_map.md --force`
- `paperwb report citation-audit --project zis_photocatalysis --out scratch/hostile_citation_audit.md --force`
- `paperwb manuscript qa drafts/synthetic_overconfident_section.md --project zis_photocatalysis --out scratch/hostile_review_manuscript_qa.md --force`
- manuscript failure probes for missing draft, missing project, and overwrite refusal
- `paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --report scratch/hostile_import_zotero.md --force`
- `paperwb files audit --project zis_photocatalysis --reports-dir scratch/hostile_file_reports --force`
- tracked-file hygiene probes with `git ls-files`

Observed validation results:

- Full pytest passed.
- Pytest collection reported 199 tests.
- Notebook structural validation passed for 8 notebooks.
- Data-safety audit checked 526 repository files with 0 errors and 7 existing absolute-path warnings in historical reports/tests.
- CLI smoke workflow passed 11 quick steps.
- Current-environment install check passed 7 quick steps.
- New manuscript QA command wrote reports and common failure paths returned user-facing errors without tracebacks.

## Release Blockers

No immediate release-blocking data-loss or unsafe-write issue was found in this review.

This is not a clean external release verdict. The high-priority issues below should be fixed before a public-facing v1.4 announcement because they affect trust, portability, and discoverability.

## High-Priority Issues

### 1. `reports/index.md` is stale and still says v1.3 is current

Evidence:

- `reports/index.md:9` says `Current v1.3 Release Reports`.
- `reports/index.md:11-16` lists v1.3 sync reports as the current release report set.
- `reports/index.md:18-20` lists `v1_4_recommended_patch_plan.md` as the next patch plan, even though v1.4 release reports now exist.

Why this matters:

- External users are likely to open `reports/index.md` to understand the current state.
- It currently points them to the previous release stage and the old hostile review context.
- This undermines the v1.4 release-readiness claim even though `reports/release_readiness_v1_4.md` exists.

Required fix:

- Regenerate `reports/index.md` after v1.4.
- Ensure current release reports include `manuscript_qa_v1_4.md`, `citation_context_table_v1_4.md`, `claim_traceability_v1_4.md`, `manuscript_revision_checklist_v1_4.md`, and `release_readiness_v1_4.md`.
- Add a test or smoke check that the report index current version matches the latest release-readiness report.

### 2. Non-indexed search reports leak absolute local paths

Evidence:

- `paperwb search photocorrosion --project zis_photocatalysis --out scratch/hostile_search_report.md --force` wrote absolute paths such as `<workspace>/projects/zis_photocatalysis/notes/zis_stability_2024.md`.
- `paper_workbench/search.py:60` returns `claim.note_file` directly.
- `paper_workbench/search.py:72` returns `str(note_path)` directly.
- `paper_workbench/cli.py:569-575` writes and prints non-indexed search results without applying the relative `display_path` behavior used by indexed search.

Why this matters:

- Search reports are a documented exportable report type.
- The project repeatedly claims reproducible, portable local reports and has data-safety tooling for absolute-path hygiene.
- A user can easily commit or share a search report containing their machine path.

Required fix:

- Normalize non-indexed search result paths relative to the workspace or selected project root before printing or writing Markdown.
- Add tests for `paperwb search ... --project ... --out ...` proving no `/Users/`, `/private/`, or drive-letter path appears in the report.
- Reuse the indexed-search `display_path(..., base_path=...)` behavior where possible.

### 3. Import reports can emit absolute registry paths

Evidence:

- `paperwb import zotero-csv ... --project zis_photocatalysis --dry-run --report scratch/hostile_import_zotero.md --force` wrote `Output registry path: <workspace>/projects/zis_photocatalysis/registry.csv`.
- `paper_workbench/importers.py:620` renders `result.registry_path` directly.

Why this matters:

- Import reports are explicitly meant to be auditable local artifacts.
- They currently expose machine-specific paths when project profiles resolve to absolute paths.
- This is the same portability class as the search-report issue.

Required fix:

- Display import report paths relative to the workspace or project root.
- Add a regression test for project import reports that rejects absolute local path patterns.

### 4. v1.4 docs are not fully wired into the docs-site navigation and matrices

Evidence:

- `docs/index.md:27-30` links authoring and older manuscript evidence-checker docs, but not `MANUSCRIPT_QA.md`, `CITATION_CONTEXT_TABLE.md`, `CLAIM_TRACEABILITY.md`, or `MANUSCRIPT_LIMITATIONS.md`.
- `docs/REPORT_MATRIX.md:19-24` includes draft audit and search report rows but not the new manuscript QA, citation context table, claim traceability, or manuscript revision checklist reports.
- `docs/TEST_MATRIX.md:11-18` omits manuscript QA despite `tests/test_manuscript_v1_4.py` being the new feature coverage.

Why this matters:

- A new external user entering through `docs/index.md` will not discover the main v1.4 docs.
- Release matrices are supposed to map features to tests and docs; the new feature is missing from the canonical matrices.

Required fix:

- Add the v1.4 docs to `docs/index.md` and `docs/SITE_MAP.md`.
- Add manuscript QA rows to `docs/REPORT_MATRIX.md` and `docs/TEST_MATRIX.md`.
- Add a small release-hygiene test that new stable command groups appear in the docs matrices.

## Medium-Priority Issues

### 1. Manuscript QA has tests, but no report-regression or golden coverage

`tests/test_manuscript_v1_4.py` covers parsing, basic findings, report generation, CLI smoke, and overwrite refusal. It does not lock the structure of `reports/manuscript_qa_v1_4.md`, `reports/citation_context_table_v1_4.md`, or `reports/claim_traceability_v1_4.md`.

Recommendation:

- Add normalized snapshot or structured assertions for v1.4 manuscript reports.
- Include at least one unknown-citation and one review-only-support snapshot.

### 2. Manuscript parser coverage is still narrow relative to real drafts

The parser intentionally stays conservative, but current tests do not cover bibliography sections, YAML front matter, block quotes, figure captions, Markdown tables, footnotes, or multi-line LaTeX commands.

Recommendation:

- Add adversarial manuscript fixtures before claiming broad manuscript QA readiness.
- At minimum, ensure bibliography/reference sections do not become ordinary claim paragraphs.

### 3. Smoke and release-check scripts lag the current feature set

Evidence:

- `scripts/smoke_cli_workflow.py:35-95` still exercises the MVP-style workflow plus search/files, but not draft QA, manuscript QA, reading sessions, sync, backups, or authoring packets.
- The smoke report title still defaults to `CLI Smoke Workflow v0.8`.
- `scripts/clean_room_install_check.py` output is still framed as v1.0-rc.

Recommendation:

- Keep quick mode short, but add at least one `paperwb manuscript qa` smoke step.
- Update report titles or make them version-neutral.

### 4. `paper_workbench/cli.py` remains a large regression risk

`paper_workbench/cli.py` is now 2,570 lines and registers many unrelated command groups inline. It still works, but every feature release increases the chance of cross-command regressions.

Recommendation:

- Split command registration and handlers by group after the v1.4 hygiene fixes.
- Keep argparse if desired; the issue is module size and reviewability, not the parser choice.

### 5. Historical report volume is overwhelming

The reports directory contains many stage-specific release-readiness, hostile-review, patch-plan, and demo reports. This is useful audit history, but without a current index it is easy to read stale reports as current state.

Recommendation:

- Archive older reports under a clearly named historical section or directory.
- Keep only the latest release-readiness, hostile review, and report gallery prominent.

## Low-Priority Polish

- `docs/index.md` includes both lowercase docs-site pages and uppercase detailed pages; canonical status is not always obvious.
- `paperwb manuscript citations` without `--out` prints terse tab-separated coverage and omits QA findings; that is acceptable but less helpful than the Markdown report.
- The manuscript QA report has an extra blank line before the embedded paragraph evidence table.
- The readiness verdict `not ready` can be triggered by any uncited paragraph, which is conservative but may be noisy for connective prose.
- The project has ignored local `dist/` and `*.egg-info/` artifacts from older package builds in the working directory. They are not tracked, but they should be cleaned before packaging demonstrations.

## Missing Tests

- Search report path-normalization test for project mode.
- Import report path-normalization test for project mode.
- Report-index freshness test for latest release reports.
- Docs matrix coverage test for stable command groups, especially `manuscript`.
- Manuscript report regression tests for generated Markdown sections and key counts.
- Parser fixtures for manuscript bibliography sections, front matter, footnotes, captions, tables, and multi-line citation commands.

## Documentation Mismatches

- `reports/index.md` is stale and advertises v1.3 as current.
- `docs/index.md` and `docs/SITE_MAP.md` do not expose the new v1.4 manuscript QA docs directly.
- `docs/REPORT_MATRIX.md` and `docs/TEST_MATRIX.md` omit the v1.4 manuscript QA/report/test surface.
- `scripts/smoke_cli_workflow.py` produces a v0.8-titled report despite being used as current release infrastructure.

## CLI Usability Problems

- Non-indexed `paperwb search` prints absolute paths in project mode, while indexed search uses friendlier relative paths.
- Import reports include absolute registry output paths in project mode.
- `paperwb manuscript citations` terminal output is minimal; users need `--out` for useful warnings and context.
- `paperwb index status --project ...` reports a global `.paperwb/index.sqlite` path; this is technically valid but can confuse users expecting project-local cache paths.

## Data-Safety Risks

- No tracked PDFs, SQLite databases, cache folders, `.paperwb` directories, or obvious secrets were found by `git ls-files` probes.
- Data-safety audit reported 0 errors and 7 existing absolute-path warnings in historical reports/tests.
- Generated user reports can still contain absolute paths, especially non-indexed search and import reports.
- Ignored local audit logs and index databases exist in the working tree. They are ignored correctly, but should not be copied into release bundles.

## Overengineering Risks

- The project has many feature surfaces for a zero-dependency local CLI. The breadth is now larger than the CLI architecture.
- Manuscript QA can easily drift from "heuristic audit" toward implied semantic validation. Keep wording conservative.
- Adding full Markdown/LaTeX support would be expensive and fragile; targeted fixtures are a better next step.
- More generated reports without a canonical index will worsen external-user confusion.

## Recommended Fix Sequence

1. Regenerate `reports/index.md` for v1.4 and add a freshness check.
2. Normalize paths in non-indexed search output and import reports; add regression tests.
3. Wire v1.4 manuscript QA docs into `docs/index.md`, `docs/SITE_MAP.md`, `docs/REPORT_MATRIX.md`, and `docs/TEST_MATRIX.md`.
4. Add one current smoke step for `paperwb manuscript qa` and make smoke report titles version-neutral.
5. Add manuscript report regression tests and adversarial manuscript parser fixtures.
6. Defer CLI module splitting until the release-hygiene fixes are complete.
