# Migration Plan v0.9

This is a non-destructive plan. Migration copies files into a new project and preserves the legacy `data/` workflow.

Source: legacy
Target project: migrated_lit_review
Project root: projects/migrated_lit_review
Dry run: true
Operations: 7
Warnings: 1
Conflicts: 0
Pre-migration backup: not created

## Copy Operations

- copy `data/registries/papers.csv` -> `projects/migrated_lit_review/registry.csv`
- copy `data/bibtex/example_library.bib` -> `projects/migrated_lit_review/bibtex/example_library.bib`
- copy `data/examples/themes.json` -> `projects/migrated_lit_review/themes.json`
- copy `data/notes/example_note_1.md` -> `projects/migrated_lit_review/notes/example_note_1.md`
- copy `data/notes/example_note_2.md` -> `projects/migrated_lit_review/notes/example_note_2.md`
- copy `data/notes/example_note_3.md` -> `projects/migrated_lit_review/notes/example_note_3.md`
- create project config `projects/migrated_lit_review/project.json`

## Warnings

- Legacy reports detected but not copied by default: reports

## Safety

- The legacy source files are copied, not moved.
- Existing target projects are treated as conflicts.
- Run with `--dry-run` first; use `--force` only after reviewing this plan.
