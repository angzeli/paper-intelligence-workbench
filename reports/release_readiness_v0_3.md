# Release Readiness v0.3

Date: 2026-06-10

## Summary

v0.3 focuses on scale confidence, stress fixtures, parser edge coverage, report stability, and regression hardening. The project remains local-first and does not use cloud services, LLM APIs, publisher scraping, or copyrighted PDFs.

## Implemented Features

- Added deterministic synthetic corpus generation through `paper_workbench.synthetic`.
- Added `paperwb synthetic generate` for local stress-project creation.
- Added checked-in synthetic stress projects for ZIS photocatalysis, finance reading, and ML methods.
- Added parser edge fixtures for structured notes and BibTeX.
- Added golden Markdown report snapshots for the stress ZIS project.
- Added report regression tests for inventory, reading status, BibTeX audit, citation audit, evidence map, theme dashboard, weak claims, missing evidence, workspace health, and section outline.
- Added CLI stress smoke tests for project validation, doctor, registry validation, BibTeX validation, claims extraction, report generation, exports, search, and synthetic generation.
- Hardened citation-audit and workspace-health ordering so report output is stable.
- Added `scripts/performance_sanity.py` for non-flaky local scale sanity checks.
- Added v0.3 stress workflow documentation.

## Stress Corpus Summary

Checked-in stress projects:

- `projects/stress_zis_photocatalysis`
- `projects/stress_finance_reading`
- `projects/stress_ml_methods`

Combined checked-in stress fixture size:

- Papers: 110
- Parsed notes: 101
- Parsed claims: 243
- Themes: 15

The stress projects intentionally include duplicate DOI values, duplicate titles, duplicate BibTeX keys, malformed DOI-like values, missing notes, broken local PDF path warnings, orphan notes, unlinked BibTeX entries, missing BibTeX fields, weak claims, missing evidence locations, and undefined theme references.

## Files Changed

- Package code: `paper_workbench/synthetic.py`, `paper_workbench/cli.py`, `paper_workbench/io.py`, `paper_workbench/audit.py`, `paper_workbench/doctor.py`, version metadata.
- Stress projects: `projects/stress_zis_photocatalysis`, `projects/stress_finance_reading`, `projects/stress_ml_methods`.
- Tests: stress generation, parser edge fixtures, CLI stress coverage, golden report regression.
- Docs: synthetic corpus, stress testing, golden reports, report regression testing, CLI stress workflows, README, AGENTS, roadmap.
- Reports: v0.3 stress reports, performance sanity, release readiness, v0.4 plan.

## Validation Performed

- `python -m pytest -q`: 57 passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: `0.3.0`.
- `python -m paper_workbench.cli --help`: passed and lists `synthetic`.
- `paperwb synthetic generate` equivalent via `python -m paper_workbench.cli synthetic generate`: passed on `/private/tmp`.
- `project validate` passed for all three stress projects, with intentional warnings/errors reported.
- `validate-registry` passed on `projects/stress_zis_photocatalysis/registry.csv`.
- `validate-bib` passed on `projects/stress_zis_photocatalysis/bibtex/library.bib`.
- `claims --project stress_zis_photocatalysis`: wrote 111 claims.
- `report evidence-map`, `report citation-audit`, and `report section-outline`: generated successfully.
- `export registry-json` and `export reading-list`: generated successfully.
- `search --claims --exact`: returned a stress claim match.
- `python scripts/performance_sanity.py --force`: generated `reports/performance_sanity_v0_3.md`.

## Generated Reports

- `reports/stress_inventory_v0_3.md`
- `reports/stress_reading_status_v0_3.md`
- `reports/stress_bibtex_audit_v0_3.md`
- `reports/stress_citation_audit_v0_3.md`
- `reports/stress_evidence_map_v0_3.md`
- `reports/stress_theme_dashboard_v0_3.md`
- `reports/stress_workspace_health_v0_3.md`
- `reports/stress_weak_claims_v0_3.md`
- `reports/stress_missing_evidence_v0_3.md`
- `reports/photocorrosion_section_outline_v0_3.md`
- `reports/stress_claims_v0_3.csv`
- `reports/stress_claims_v0_3.json`
- `reports/performance_sanity_v0_3.md`
- `reports/release_readiness_v0_3.md`
- `reports/v0_4_recommended_patch_plan.md`

## Performance Sanity Result

The performance sanity script generated a temporary 100-paper, 220-claim project and completed local generation, parsing, validation, audit, doctor, and evidence-map construction. It is intentionally a sanity report, not a strict benchmark.

## Backward Compatibility

- Existing `data/` workflow remains supported.
- Existing project-profile workflow remains supported.
- Existing CLI commands remain available.
- New `synthetic` command is additive.
- Report ordering is now more deterministic; this should reduce accidental diffs rather than remove existing output.

## Known Limitations

- Golden snapshots cover one representative stress project, not every project/domain combination.
- Performance sanity uses a single generated workload and does not replace profiling.
- BibTeX parsing remains lightweight and conservative.
- Markdown note parsing still expects recognizable structured headings.
- Stress fixtures intentionally contain validation findings; they are not clean example projects.

## Risks

- Future report changes may require deliberate golden snapshot updates.
- Snapshot tests can become noisy if report output includes new dynamic content.
- Larger real projects may expose parser variants not represented in the synthetic fixtures.
- The checked-in stress data increases repository size, though it remains small and text-only.

## v0.4 Focus

v0.4 should focus on report diff tooling, fixture-size profiles, more note repair diagnostics, optional HTML report export, and safer citation-key suggestion workflows.

## Usability Assessment

The repository is usable for a real small literature-review project around 100 papers, provided users understand that the tool audits local user-provided evidence and does not decide scientific truth.

