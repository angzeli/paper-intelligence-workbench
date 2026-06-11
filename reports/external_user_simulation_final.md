# Final External-User Simulation

Date: 2026-06-11

## Persona

Simulated user: a technically comfortable undergraduate or early-stage researcher
who knows basic Python and wants to try Paper Intelligence Workbench on synthetic
literature-review data before using it on real local notes.

## Repository State

- Branch: `main`, ahead of `origin/main`; nothing was pushed.
- Worktree at the start: clean.
- Public entry points inspected: `README.md`, `AGENTS.md`, `pyproject.toml`,
  `CHANGELOG.md`, docs index and quickstart docs, CLI help, examples,
  notebooks, generated reports, tests, and `.gitignore`.
- Ignored local files were present, including `.paperwb/`, `.pytest_cache/`,
  `__pycache__/`, `.idea/`, and scratch outputs. They were not tracked.
- No tracked PDFs, SQLite cache files, backup archives, audit logs, build
  artifacts, or Python cache files were found.

## Installation And Import

- Fresh virtual environment created under `<tmp>/paperwb_external_user_sim_v1_8/venv`.
- Documented command `python -m pip install -e ".[test]"` succeeded.
- Fresh install reported `paper-intelligence-workbench==1.8.0`.
- `paperwb --help` worked from the fresh virtual environment.
- Package import worked and reported `paper_workbench.__version__ == "1.8.0"`.

Note: the pre-existing global editable environment reported stale metadata via
`pip show paper-intelligence-workbench` (`1.1.0`), while importing the package
reported `1.8.0`. A fresh install produced correct metadata, so this is a local
environment residue rather than a repository packaging blocker.

## Quickstart Results

Commands tested from public docs:

- `paperwb init --root <tmp>/first_workspace`: passed.
- `paperwb template list`: passed.
- `paperwb template inspect photocatalysis`: passed.
- `paperwb template create photocatalysis --project my_photocatalysis_review`: passed.
- `paperwb project init demo_project`: passed.
- `paperwb project list`: passed.
- `paperwb doctor --project my_photocatalysis_review --out ... --force`: passed.
- `paperwb dashboard --project my_photocatalysis_review --no-audit-log --out ... --force`: passed.
- `paperwb rules validate-config --project my_photocatalysis_review`: passed.

The empty template project produces expected warnings about missing notes and
under-supported themes. These are noisy but useful for a new user because they
explain that the scaffold is empty and needs real local entries.

## Example Data Workflow

Legacy synthetic `data/` workflow:

- `paperwb validate-registry data/registries/example_papers.csv`: passed with
  intentional duplicate/missing-key findings.
- `paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv`:
  passed with intentional synthetic BibTeX findings.
- `paperwb list --registry data/registries/example_papers.csv`: passed.
- `paperwb list --registry data/registries/example_papers.csv --status unread`: passed.
- `paperwb note-template synth_charge_2024 --registry ... --output ... --force`: passed.
- `paperwb claims data/notes --output ...`: passed and wrote 3 claims.
- `paperwb search photocorrosion --notes --claims --notes-dir data/notes`: passed.
- Reports generated successfully: inventory, reading status, BibTeX audit,
  citation audit, evidence map, theme dashboard, weak claims, missing evidence,
  missing notes, and section outline.

Project-profile workflow:

- `paperwb project validate zis_photocatalysis`: passed with actionable
  synthetic findings.
- `paperwb report evidence-map --project zis_photocatalysis`: passed.
- `paperwb report citation-audit --project zis_photocatalysis`: passed.
- `paperwb dashboard --project zis_photocatalysis --view next-actions`: passed.
- `paperwb rules run/report --project zis_photocatalysis`: passed.

## Authoring And Manuscript Workflow

Synthetic draft/manuscript commands passed:

- `paperwb writing-packet --project zis_photocatalysis --theme photocorrosion`.
- `paperwb report evidence-matrix --project zis_photocatalysis --theme photocorrosion`.
- `paperwb draft parse drafts/synthetic_photocorrosion_section.md`.
- `paperwb draft audit drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis`.
- `paperwb manuscript qa drafts/synthetic_overconfident_section.md --project zis_photocatalysis`.
- `paperwb manuscript trace-claims drafts/synthetic_good_section.md --project zis_photocatalysis --theme photocorrosion`.

Generated reports clearly state that matching is heuristic, audit-only, and not
scientific truth evaluation. Unknown citations, review-only evidence,
overconfident wording, and weak evidence were flagged conservatively.

## Reading Workflow

A temporary synthetic project `sim_reading` was generated and used for reading
session checks:

- `paperwb reading queue --project sim_reading`: passed.
- `paperwb reading start sim_reading_synthetic_001 --project sim_reading --goal verify_claims`: passed.
- `paperwb reading finish ... --status read --summary ... --follow-up ... --claims-added 0`: passed.
- `paperwb reading status --project sim_reading`: passed.
- `paperwb followups list/export --project sim_reading`: passed.
- `paperwb reading review --project sim_reading`: passed.

Session logs and audit logs were written only inside the temporary project.
Existing notes were located rather than overwritten.

## Import, Export, Sync, And Safety Workflows

Import dry-runs passed:

- Zotero CSV, generic CSV with mapping, BibTeX, and RIS imports all produced
  dry-run reports without modifying registries.

Exports passed:

- Claims JSON, registry JSON, reading list, Obsidian vault, and backup bundle.
- Backup bundle manifest confirmed `include_pdfs: false` and copied no PDFs.

Sync and safety checks passed:

- `paperwb sync plan` wrote Markdown and JSON plans with actions/conflicts.
- `paperwb sync apply ... --dry-run` wrote a dry-run apply report.
- `paperwb sync plan-obsidian` detected conservative round-trip conflicts.
- `paperwb integrity check --project sim_reading` wrote an integrity report.
- `paperwb backup create/list/inspect/restore --dry-run` worked.
- Backup manifests excluded `.paperwb/audit_log.jsonl`,
  `.paperwb/index.sqlite`, and reading-session logs.
- Migration plan and migration dry-run worked and remained non-destructive.

## Search And Index Workflow

Substring search worked on both checked-in and temporary projects.

Release blocker found and fixed:

- `paperwb index rebuild --project sim_reading --include-text` crashed with
  `sqlite3.IntegrityError: UNIQUE constraint failed: records.record_id` on a
  synthetic project with duplicate BibTeX keys.
- Fix applied: internal indexed record IDs are now deduplicated
  deterministically with `:dupN` suffixes. User-facing paper IDs, BibTeX keys,
  and search output remain unchanged.
- Regression test added in `tests/test_index_v0_5.py`.

After the fix:

- `paperwb index rebuild --project sim_reading --include-text`: passed.
- `paperwb index status --project sim_reading --include-text --check-files`: passed.
- `paperwb search photocorrosion --project sim_reading --indexed`: passed.
- `paperwb search photocorrosion --project zis_photocatalysis --indexed --text --index <tmp>`:
  passed using synthetic sidecar text.

## Notebooks

`python scripts/check_notebooks.py` checked 8 notebooks successfully.

The notebook validation checks JSON structure and titles. Full notebook
execution was skipped to keep the final external-user simulation lightweight;
the checked notebooks use synthetic data and no absolute paths were reported by
the checker.

## Documentation Accuracy

Docs audited:

- README quickstart and feature descriptions.
- `docs/index.md`.
- `docs/EXTERNAL_USER_QUICKSTART.md`.
- Installation, CLI, project profile, report, import/export, search, authoring,
  manuscript QA, reading, backup/migration, rule, dashboard, and template docs.

High-priority docs blockers found: none.

Non-blocking documentation issues:

- The docs are comprehensive but can overwhelm first-time users because many
  mature workflows are listed in the README before a minimal path is complete.
- Several docs overlap: CLI reference, CLI surface, command contracts, workflow
  examples, and report gallery.
- Template-created empty projects intentionally produce many warnings; docs
  explain this but a short "first empty project" troubleshooting note would help.

## Validation Run

- `python -m pytest -q`: passed, 240 tests.
- `python scripts/smoke_cli_workflow.py --quick --out <tmp>/smoke_cli.md`:
  passed, 14 smoke steps.
- `python scripts/data_safety_audit.py --out <tmp>/data_safety_audit.md --strict`:
  passed, 0 errors and 7 warnings.
- `python scripts/check_notebooks.py`: passed, 8 notebooks checked.
- `python -m paper_workbench.cli --help`: passed.
- Fresh editable install: passed.
- Representative CLI workflows across registry, BibTeX, notes, claims,
  reports, projects, authoring, draft/manuscript QA, reading sessions,
  import/export, sync, search/index, files, safety, rules, dashboard, and
  templates passed after the index blocker fix.

## Issues Found

### Blocker Fixed

- Indexed search rebuild crashed on duplicate internal record IDs created from
  duplicate BibTeX keys in synthetic data.

### Non-blocking Issues

- Existing local environment metadata may be stale until users reinstall.
- Empty template projects generate many warnings by design.
- Docs are accurate but broad; a shorter "minimum first hour" path would improve
  onboarding.
- Data-safety audit reports 7 warnings, but no errors.

## Release Verdict

Ready for local dogfooding.

The repository is usable by a new external user who follows the README and docs.
The final blocker discovered during simulation was fixed and covered by tests.
The project remains local-first and did not require cloud APIs, LLM APIs,
publisher scraping, copyrighted PDFs, or real paper full text.
