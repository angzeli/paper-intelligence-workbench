# Compatibility Inspection Report v3.2

This report inspects historical or malformed local workspaces. It does not modify files.

Root: `tests/fixtures/workspaces/partial_migration_conflict`
Workspace type: `partial_migration_workspace`
Approximate version: `v1-v3 project-profile workflow`
Supported: `yes`
Inspectable: `yes`
Migration needed: `yes`
Migratable: `no`
Requires backup: `yes`
Requires manual review: `yes`

## Registry Schema Observations

| Path | Headers | Missing required | Extra columns |
| --- | --- | --- | --- |
| data/registries/papers.csv | paper_id, title, authors, year, bibtex_key, tags, reading_status, notes_path | none | none |
| projects/migrated_review/registry.csv | paper_id, title, authors, year | none | none |

## Project Observations

| Project path | project.json | Registry | BibTeX | Notes | Themes | Reports |
| --- | --- | --- | --- | --- | --- | --- |
| projects/migrated_review | yes | registry.csv | bibtex/library.bib | notes | themes.json | reports |

## Findings

| Severity | Code | Identifier | Message | Suggestion |
| --- | --- | --- | --- | --- |
| warning | project_bibtex_missing | tests/fixtures/workspaces/partial_migration_conflict/projects/migrated_review/bibtex/library.bib | Project path is missing: projects/migrated_review/bibtex/library.bib | Recover the file or adjust project.json. |
| warning | project_notes_missing | tests/fixtures/workspaces/partial_migration_conflict/projects/migrated_review/notes | Project path is missing: projects/migrated_review/notes | Recover the file or adjust project.json. |
| warning | project_themes_missing | tests/fixtures/workspaces/partial_migration_conflict/projects/migrated_review/themes.json | Project path is missing: projects/migrated_review/themes.json | Recover the file or adjust project.json. |
| warning | partial_migration_workspace | tests/fixtures/workspaces/partial_migration_conflict | Legacy data/ files and project profiles both exist; migration needs manual target review. | Inspect existing projects before choosing a migration target. |
| error | migration_target_conflict | tests/fixtures/workspaces/partial_migration_conflict/projects/migrated_review | Default migration target already exists and is not empty: projects/migrated_review | Choose a new --to-project name or inspect the existing project before migration. |

## Recommended Actions

- Fix error-level findings before running forced migration.
- Use `paperwb compatibility report` after repairs to confirm the workspace shape.

## Safety Boundary

- Compatibility inspection is read-only.
- Migration should be dry-run first and should copy, not move, legacy files.
- Extra registry columns are reported so migrations can preserve the raw CSV rather than rewriting user fields.
- Real workspaces should be backed up before any forced migration.
