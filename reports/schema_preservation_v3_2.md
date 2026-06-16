# Compatibility Inspection Report v3.2

This report inspects historical or malformed local workspaces. It does not modify files.

Root: `tests/fixtures/workspaces/extra_columns_registry`
Workspace type: `legacy_data_workflow`
Approximate version: `v0.1-v0.9 legacy data workflow`
Supported: `yes`
Inspectable: `yes`
Migration needed: `yes`
Migratable: `yes`
Requires backup: `yes`
Requires manual review: `yes`

## Registry Schema Observations

| Path | Headers | Missing required | Extra columns |
| --- | --- | --- | --- |
| data/registries/papers.csv | paper_id, title, authors, year, bibtex_key, tags, reading_status, notes_path, local_pdf_path, reviewer_private_code, legacy_score | none | reviewer_private_code, legacy_score |

## Project Observations

No project profiles detected.

## Findings

| Severity | Code | Identifier | Message | Suggestion |
| --- | --- | --- | --- | --- |
| info | extra_registry_columns | tests/fixtures/workspaces/extra_columns_registry/data/registries/papers.csv | Registry has extra user columns: reviewer_private_code, legacy_score | Copy-based migration preserves the raw CSV; avoid rewriting this registry through schema-normalizing commands until reviewed. |
| warning | unsafe_local_pdf_path | tests/fixtures/workspaces/extra_columns_registry/data/registries/papers.csv | Registry row 2 has an unsafe or absolute local_pdf_path. | Keep local file paths relative where possible and do not commit PDFs. |

## Recommended Actions

- Run `paperwb migrate run --dry-run` and inspect the migration plan.
- Create or confirm a backup before any forced migration.

## Safety Boundary

- Compatibility inspection is read-only.
- Migration should be dry-run first and should copy, not move, legacy files.
- Extra registry columns are reported so migrations can preserve the raw CSV rather than rewriting user fields.
- Real workspaces should be backed up before any forced migration.
