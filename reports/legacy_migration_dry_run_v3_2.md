# Migration Plan v3.2

This is a non-destructive plan. Migration copies files into a new project and preserves the legacy `data/` workflow.

Source: legacy
Target project: migrated_review
Project root: projects/migrated_review
Dry run: true
Operations: 5
Warnings: 1
Conflicts: 0
Pre-migration backup: not created

## Copy Operations

- copy `data/registries/papers.csv` -> `projects/migrated_review/registry.csv`
- copy `data/bibtex/library.bib` -> `projects/migrated_review/bibtex/library.bib`
- copy `data/examples/themes.json` -> `projects/migrated_review/themes.json`
- copy `data/notes/legacy_alpha_2026.md` -> `projects/migrated_review/notes/legacy_alpha_2026.md`
- create project config `projects/migrated_review/project.json`

## Warnings

- Legacy reports detected but not copied by default: reports

## Safety

- The legacy source files are copied, not moved.
- Existing target projects are treated as conflicts.
- Run with `--dry-run` first; use `--force` only after reviewing this plan.
