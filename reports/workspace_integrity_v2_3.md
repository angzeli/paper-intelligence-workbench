# Workspace Integrity Report v2.3

This report checks local workspace consistency. It does not modify files.

Root: projects/zis_photocatalysis
Project: zis_photocatalysis
Errors: 1
Warnings: 5
Checked paths: 6

## Checked Paths

- `projects/zis_photocatalysis/registry.csv`
- `projects/zis_photocatalysis/bibtex/library.bib`
- `projects/zis_photocatalysis/notes`
- `projects/zis_photocatalysis/themes.json`
- `projects/zis_photocatalysis/reports`
- `projects/zis_photocatalysis/files.csv`

## Findings

| Severity | Code | Identifier | Message | Suggestion |
| --- | --- | --- | --- | --- |
| warning | note_parse_warning | zis_stability_2024 | zis_stability_2024.md: Claim A is missing evidence location. | Review the note against the structured note format. |
| warning | suspiciously_incomplete | zisStability2024 | zisStability2024 looks sparse. | Review the entry for missing author, venue, DOI, or URL fields. |
| warning | theme_under_supported | photocorrosion | photocorrosion has 1 supporting claim(s); target is 2. | Add more verified claims or adjust the theme threshold. |
| warning | theme_too_few_papers | photocorrosion | photocorrosion has evidence from 1 paper(s); target is 2. | Add evidence from more papers or adjust the theme threshold. |
| error | claim_missing_evidence_location | zis_stability_2024:c1 | zis_stability_2024:c1 has no section/page evidence location. | Add a section, page, figure, table, or appendix location. |
| warning | local_file_warning |  | Scan folder missing: papers | Run `paperwb files audit` for details. |

## Boundary

- This is a completeness and path-safety audit, not a scientific truth audit.
- It does not download, scrape, parse PDFs, or inspect ignored private files.
- Warnings should be reviewed before migration, restore, or external release.
