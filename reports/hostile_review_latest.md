# Hostile Maintainer Review: v1.1 Current Repository

Date: 2026-06-11

## Release Verdict

**Verdict: do not ship v1.1 to external users until the `paperwb report all` write-path bugs are fixed.**

The repository is now a broad local-first research workbench with registry validation, BibTeX validation, structured notes, claim extraction, evidence maps, citation audits, project profiles, import/export, indexed search, local file audits, authoring reports, draft citation audits, backup/migration workflows, adversarial tests, CI, docs, synthetic projects, and release reports.

The v1.1 draft-audit feature is directionally sound and stays inside the project boundary: it audits Markdown drafts with local citations and tracked evidence, does not use cloud or LLM APIs, and does not rewrite prose.

The current release candidate still has release-grade CLI safety problems in `paperwb report all`. The command can leave a partially generated report set after a later output collision, and it silently accepts `--out` while ignoring it. These violate the documented command contract for safe, predictable generated outputs.

Validation performed during this review:

- `python -m pytest -q`: passed.
- `python -m pytest --collect-only -q`: 160 tests collected.
- `python scripts/data_safety_audit.py --out <tmp-report> --title "Hostile Review Data Safety" --strict`: passed with 0 errors and 11 warnings.
- `python scripts/check_notebooks.py`: passed, 8 notebooks checked.
- `python scripts/validate_notebooks.py`: passed, 8 notebooks validated.
- `python scripts/clean_room_install_check.py --quick --out <tmp-report>`: passed, 7 current-environment steps, 0 failures.
- `python -m paper_workbench.cli --help`: passed.
- `python -m paper_workbench.cli draft --help`: passed.
- `python -m paper_workbench.cli draft audit drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis --out <tmp-report> --force`: passed.
- `python -m paper_workbench.cli audit-log clear`: returned exit code 2 with a clean user-facing error and no traceback.
- `python -m build --sdist --wheel`: could not be verified in the active local environment because the current Python environment does not expose an executable `build.__main__`.

## Release Blockers

### 1. `paperwb report all` leaves partial output after a later collision

Probe:

```bash
paperwb report all \
  --registry data/registries/example_papers.csv \
  --bibtex data/bibtex/example_library.bib \
  --notes-dir data/notes \
  --themes data/examples/themes.json \
  --reports-dir <tmp-reports-dir>
```

Setup: `<tmp-reports-dir>/citation_audit.md` existed before the command.

Observed behavior:

- exit code: `2`
- the protected `citation_audit.md` was not overwritten;
- earlier reports were already written before failure:
  - `inventory.md`
  - `reading_status.md`
  - `papers_by_tag.md`
  - `bibtex_audit.md`
  - `claims_by_theme.md`
  - `evidence_map.md`

Why this blocks release:

- The command contract says generated outputs should be safe and predictable.
- A failed `report all` run should not leave a half-current report directory.
- Users can reasonably mistake partial generated reports for a complete audit run.

Required fix:

- Preflight every output path for `report all` before writing the first report.
- Fail before writing anything if any selected output exists and `--force` is not passed.
- Add a regression test that seeds a later output path and asserts no earlier report file is created.

### 2. `paperwb report all --out ...` silently ignores `--out`

Probe:

```bash
paperwb report all \
  --registry data/registries/example_papers.csv \
  --bibtex data/bibtex/example_library.bib \
  --notes-dir data/notes \
  --themes data/examples/themes.json \
  --reports-dir <tmp-reports-dir> \
  --out <tmp-single-report> \
  --force
```

Observed behavior:

- exit code: `0`
- `<tmp-single-report>` was not created;
- 12 report files were written under `--reports-dir`;
- stderr was empty.

Why this blocks release:

- Silently accepting and ignoring an explicit output path is a serious CLI contract violation.
- `--out` has a clear meaning for other report types.
- This creates misplaced outputs without warning.

Required fix:

- Reject `--out` when `report_type == "all"` with a clear message explaining that `--reports-dir` controls multi-report output, or implement a documented single index output.
- Add a CLI regression test for the chosen behavior.

## High-Priority Issues

### 1. Active version/surface docs are stale after the v1.1 bump

`pyproject.toml` and `paper_workbench.__version__` now report `1.1.0`, but active surface documents still present themselves as v1.0-rc:

- `docs/API_SURFACE.md`
- `docs/CLI_SURFACE.md`
- `docs/COMMAND_CONTRACTS.md`
- related tests under `tests/test_v1_0_rc_command_contracts.py`

Why this matters:

- These are not just historical release notes; they describe the active command/API contract.
- Tests currently codify the stale `v1.0-rc` text.
- External users will not know whether the v1.1 `draft` command is part of the stable surface or a bolted-on addendum.

Required fix:

- Either rename these documents as historical v1.0-rc artifacts and create v1.1 surfaces, or update their titles/content/tests to v1.1.
- Keep historical v1.0-rc reports under `reports/`, but do not let active docs advertise the wrong release surface.

### 2. Active docs still encourage writing into tracked `reports/` paths

Multiple user-facing docs and README sections still show commands writing directly to checked-in `reports/` files, often with `--force`.

Examples include authoring reports, workspace integrity, restore dry-runs, migration plans, export examples, stress workflows, and CLI reference examples.

Why this matters:

- A new user following docs can dirty a fresh checkout.
- The examples normalize `--force` before users understand what is being overwritten.
- This contradicts the safe-write narrative and the external quickstart's safer `scratch/` convention.

Required fix:

- Move tutorial output examples to `scratch/`, project-local temporary paths, or clearly ignored output directories.
- Reserve checked-in `reports/` paths for maintainer-generated release artifacts.
- Add a docs smoke check that fails on unsafe tutorial examples unless explicitly marked as maintainer report regeneration.

### 3. Current release reports disagree with the latest risk state

`reports/release_readiness_v1_1.md` reports the v1.1 draft feature as usable but does not mention the known `report all` blockers. `reports/final_project_handoff.md` is now stale in the opposite direction: it still says the latest hostile review found the `audit-log clear` traceback blocker, which has been fixed.

Why this matters:

- A maintainer reading the report directory gets contradictory release verdicts.
- `reports/hostile_review_latest.md` should be the current risk register, but the report index and release readiness files do not make that relationship obvious enough.

Required fix:

- Regenerate release readiness after fixing the blockers.
- Update report index language so `hostile_review_latest.md` is the canonical current risk register.
- Treat older readiness and handoff reports as historical snapshots.

### 4. Package build is still not locally verified in this review environment

`python -m build --sdist --wheel` failed because the active Python environment does not expose `build.__main__`.

CI installs `.[dev]` and has a build step, so this may pass in CI. The local release review still cannot prove the distribution artifacts.

Required fix:

- Run the build in CI or a true clean environment with development extras installed.
- Record the successful build check in the next release-readiness report.

### 5. Local file link/unlink still appear non-transactional across metadata writes

`files link` and `files unlink` update file-registry and paper-registry state. The implementation still appears to perform multi-file metadata updates without an explicit rollback strategy if a later write fails.

Why this matters:

- Local file reconciliation is data-integrity sensitive.
- A partial write can leave file registry and paper registry metadata disagreeing.

Required fix:

- Add simulated write-failure tests for `files link` and `files unlink`.
- Preflight all writable paths before mutation.
- Prefer write-to-temp-and-rename or a compensating consistency check if a later write fails.

### 6. Draft citation extraction does not preserve source-order across mixed citation syntaxes

`extract_citations()` collects LaTeX-style `\cite...{}` matches first and `@key` matches second. In a paragraph where bracketed `[@key]` appears before a later `\cite{other}`, the reported citation order will not match source order.

Why this matters:

- The draft auditor's first promise is "which citation keys appear in the draft."
- Order matters for paragraph-level diagnostics and user trust.

Required fix:

- Collect citation regex matches with spans, sort by source position, and then split grouped keys.
- Add a test for mixed syntax in source order.

## Medium-Priority Issues

- `paper_workbench/cli.py` remains very large and continues to accumulate command orchestration.
- The v1.1 draft parser is intentionally conservative but does not yet handle footnotes, tables, definition lists, reference-style links, or citations in HTML comments.
- Draft-audit false positives are visible in synthetic reports: introductory fixture paragraphs are flagged as uncited claims.
- `files hash` on a missing path returns no traceback, but the message is a raw filesystem error rather than the project's structured "what/where/why/next step" diagnostic format.
- The canonical `zis_photocatalysis` project still fails `project validate --strict` because it intentionally contains weak evidence and missing locations; docs need to keep warning users that these are synthetic audit fixtures.
- Historical data-safety warnings remain in reports/tests. They are warning-class, but the warning budget should not grow.
- Notebook validation is structural only; notebooks are not executed in CI.
- The `draft` command is covered by tests, but the general CLI smoke script does not yet exercise draft workflows.
- Build and clean-room naming remain slightly overstated: the checked script is a current-environment release check, not a full fresh virtual environment by default.

## Low-Priority Polish

- `reports/` is crowded with versioned artifacts; users can easily open stale reports.
- `docs/CLI_REFERENCE.md` and `docs/CLI_SURFACE.md` overlap and can drift.
- Uppercase reference docs and lowercase docs-site pages duplicate several topics.
- The v1.1 draft docs are present, but there is no notebook for the draft workflow; an example script exists instead.
- Some active CLI help still uses old release labels such as v0.7 and v0.9 in command descriptions.
- The draft reports use many warning rows; a compact summary by severity/code would improve scanability.

## Missing Tests

Add focused tests for:

- `paperwb report all` preflights all outputs before writing any file.
- `paperwb report all --out <path>` fails clearly or produces a documented single output.
- docs examples do not write to tracked `reports/` paths unless marked as maintainer report regeneration.
- v1.1 API/CLI surface docs match package version or are explicitly marked historical.
- `files link` and `files unlink` under simulated partial write failure.
- backup creation under simulated copy/write failure.
- draft citation extraction preserves source order across mixed `[@key]` and `\cite{key}` syntax.
- draft parser handling of footnotes, tables, and comments.
- draft CLI commands in `scripts/smoke_cli_workflow.py` or a dedicated draft smoke script.
- local package build success in a clean release environment.

## Documentation Mismatches

- Active surface docs say v1.0-rc while package metadata says v1.1.0.
- `reports/release_readiness_v1_1.md` omits the known `report all` blockers.
- `reports/final_project_handoff.md` says `audit-log clear` is still the latest blocker, which is now stale.
- README and docs still contain many commands writing to `reports/` with `--force`.
- `docs/COMMAND_CONTRACTS.md` says generated files should be safe and predictable; `report all` violates this through partial writes and ignored `--out`.

## CLI Usability Problems

- `paperwb report all --out` is accepted and ignored.
- `paperwb report all` can fail after writing partial output.
- `files hash` missing-path errors are terse.
- `project validate --strict zis_photocatalysis` fails on intentional fixture issues without always making clear that this is expected synthetic data.
- `draft citations` prints useful coverage, but it always exits 0 even when citations are unknown. This may be fine for report generation, but a `--strict` mode would be useful later.

## Data-Safety Risks

No tracked PDFs, SQLite cache databases, `.paperwb` directories, backup archives, `scratch/` outputs, IDE folders, Python cache files, or obvious secret files were found in tracked files.

No cloud API, LLM API, publisher scraping, PDF download, OCR, or copyrighted example PDF behavior was found.

Remaining data-safety risks:

- Docs still encourage writing generated artifacts into tracked `reports/` paths.
- `report all` can leave partial generated outputs after a failure.
- Multi-file local-file metadata writes need stronger failure simulation.
- Historical absolute-path warnings remain visible in generated reports/tests.
- Text sidecar and draft content copyright safety cannot be proven automatically; examples are synthetic and clearly labelled.

## Overengineering Risks

The project now includes many local subsystems: registry, BibTeX, notes, claims, themes, reports, authoring, draft auditing, indexed search, imports, exports, local files, integrity, backups, migration, audit logs, synthetic corpora, adversarial fixtures, docs-site pages, and release reports.

The main risk is no longer feature absence. It is consistency:

- write safety must be uniform across every command;
- active docs must match the package version and command behavior;
- release reports must not contradict the latest hostile review;
- heuristic draft-audit reports must not drift into pseudo-semantic claims;
- monolithic CLI orchestration makes safety review harder.

Do not expand the feature surface until the `report all` blockers and stale surface docs are fixed.

## Recommended Fix Sequence

1. Fix `paperwb report all` preflight behavior and add no-partial-output tests.
2. Reject or implement `paperwb report all --out`; add CLI regression tests.
3. Update v1.1 API/CLI surface docs and tests so they no longer claim v1.0-rc as the active surface.
4. Move unsafe tutorial examples from tracked `reports/` paths to `scratch/` or another ignored location.
5. Regenerate release-readiness and report-index artifacts so they point to the current hostile review as the risk register.
6. Add partial-write failure tests for local file linking/unlinking and backup creation.
7. Fix draft citation source-order extraction and add mixed-syntax tests.
8. Verify package build in CI or a true clean release environment.
