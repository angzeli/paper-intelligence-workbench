# Public vs Internal API

Paper Intelligence Workbench v3.0rc treats the CLI and documented local schemas as
the primary public API. Python imports are useful for tests and local scripts,
but most modules remain internal unless listed as stable in `docs/API_SURFACE.md`
or `docs/STABLE_SURFACE_V3.md`.

## Public And Stable

- `paperwb` command groups documented in `docs/CLI_REFERENCE_V3.md`.
- Registry CSV fields documented in `docs/SCHEMA_REFERENCE_V3.md`.
- Structured note Markdown documented in `docs/NOTE_FORMAT.md`.
- Project profile layout under `projects/<name>/`.
- Themes JSON and rule JSON as documented in their schema guides.

## Semi-Stable Python Helpers

These are acceptable for local scripts when the CLI is not enough:

- `paper_workbench.registry.load_registry`, `save_registry`, `validate_registry`
- `paper_workbench.bibtex.parse_bibtex_file`, `validate_bibtex`
- `paper_workbench.notes.parse_note_file`, `write_note_template`
- `paper_workbench.claims.collect_notes`, `collect_claims`, `save_claims_csv`
- `paper_workbench.projects.create_project_profile`, `list_project_profiles`, `resolve_project_profile`
- `paper_workbench.safety.audit_data_safety`

Fields may be added to dataclasses, but existing documented field names should
not be removed without a migration note.

## Internal Helpers

These modules are intended for maintainers and tests, not external extension
points:

- `paper_workbench.cli`
- `paper_workbench.io`
- `paper_workbench.paths`
- `paper_workbench.markdown`
- `paper_workbench.errors`

They may change when preserving CLI behavior requires cleanup. Keep changes
small and covered by behavior tests.

## Experimental Modules

The following modules are useful but not API-frozen:

- `drafts.py`, `manuscript.py`
- `reading.py`, `sync.py`
- `rules.py`, `graph.py`
- `claim_lifecycle.py`
- `workflow.py`, `review_packets.py`
- `index.py`, `rebuild.py`

Use their CLI workflows first. If a Python script imports them, pin tests to the
specific behavior the script relies on.
