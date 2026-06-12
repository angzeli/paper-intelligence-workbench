# Notebook Validation v2.0rc

## Scope

The repository contains lightweight workflow notebooks using synthetic data.

## Validation Status

- `python scripts/check_notebooks.py`: passed.
- Notebooks checked: 8.
- Each checked notebook parsed as valid JSON and reported a workflow title.

## Notebooks Checked

- `notebooks/01_registry_and_bibtex_workflow.ipynb`
- `notebooks/02_notes_claims_and_evidence_map.ipynb`
- `notebooks/04_project_profiles_workflow.ipynb`
- `notebooks/05_citation_audit_workflow.ipynb`
- `notebooks/06_section_outline_workflow.ipynb`
- `notebooks/08_evidence_matrix_workflow.ipynb`
- `notebooks/09_literature_review_writing_packet.ipynb`
- `notebooks/10_subsection_readiness_workflow.ipynb`

## Execution Policy

For release-candidate validation, notebooks are structurally checked for valid
JSON and advertised titles. Full execution is optional and skipped unless a
notebook-specific change requires it.
