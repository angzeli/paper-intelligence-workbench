# Incremental Rebuild Plan v2.5

- Project: `zis_photocatalysis`
- Generated at: `2026-06-16T10:36:58.214697+00:00`
- Metadata path: `.paperwb/rebuild_metadata.json`
- Metadata exists: `false`
- Stale targets: 6 / 6

## Target Summary

| Target | Status | Reason | Output |
| --- | --- | --- | --- |
| `claims` | stale | No rebuild metadata recorded. | `reports/claims.csv` |
| `evidence_map` | stale | No rebuild metadata recorded. | `reports/evidence_map.md` |
| `search_index` | stale | Search index file is missing. | `.paperwb/index.sqlite` |
| `report_outputs` | stale | No rebuild metadata recorded. | `reports` |
| `manuscript_qa` | stale | No rebuild metadata recorded. | `reports/manuscript_qa.md` |
| `dashboard` | stale | No rebuild metadata recorded. | `reports/dashboard.md` |

## Recommended Actions

- `claims`: paperwb claims --output projects/zis_photocatalysis/reports/claims.csv --force --project zis_photocatalysis
- `evidence_map`: paperwb report evidence-map --out projects/zis_photocatalysis/reports/evidence_map.md --force --project zis_photocatalysis
- `search_index`: paperwb index rebuild --project zis_photocatalysis
- `report_outputs`: paperwb report all --force --project zis_photocatalysis
- `manuscript_qa`: Run `paperwb manuscript qa DRAFT --project PROJECT --out REPORT` for each active draft.
- `dashboard`: paperwb dashboard --out projects/zis_photocatalysis/reports/dashboard.md --force --project zis_photocatalysis

## Source Coverage

- `claims`: `notes`
- `evidence_map`: `bibtex/library.bib`, `notes`, `registry.csv`, `themes.json`
- `search_index`: `bibtex/library.bib`, `notes`, `registry.csv`, `themes.json`
- `report_outputs`: `bibtex/library.bib`, `notes`, `registry.csv`, `themes.json`
- `manuscript_qa`: `bibtex/library.bib`, `notes`, `registry.csv`, `themes.json`
- `dashboard`: `bibtex/library.bib`, `notes`, `registry.csv`, `themes.json`
