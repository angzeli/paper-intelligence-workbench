# CLI Behavior Matrix

| Command area | Example command | Non-destructive default | Overwrite behavior | Project support | Test coverage |
| --- | --- | --- | --- | --- | --- |
| Init | `paperwb init --root scratch/workspace` | Creates missing folders only | Existing files are preserved | Legacy workspace root | CLI smoke |
| Registry | `paperwb validate-registry data/registries/example_papers.csv` | Read-only unless `--json` is requested | `--force` required for existing JSON export path | Path-based | Registry/CLI tests |
| Templates | `paperwb template create photocatalysis --project my_project` | Refuses existing project path | No force workflow in v1.7 | Creates profile | Template tests |
| BibTeX | `paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv` | Read-only | Optional report requires force | Path-based | BibTeX tests |
| Notes | `paperwb note-template PAPER_ID --output scratch/note.md` | Refuses existing output | `--force` overwrites output | Yes | CLI tests |
| Claims | `paperwb claims data/notes --output scratch/claims.csv` | Refuses missing notes paths and existing output files | `--force` overwrites output CSV | Yes | Notes/CLI tests |
| Search | `paperwb search photocorrosion --project zis_photocatalysis` | Read-only | Optional report requires force | Yes | Search/index tests |
| Index | `paperwb index rebuild --project zis_photocatalysis --include-text` | Writes ignored cache | Rebuildable cache | Yes | Index tests |
| Files | `paperwb files scan --project zis_photocatalysis` | Read-only | `--write-registry` writes merged CSV | Yes | Local-file tests |
| Reports | `paperwb report evidence-map --project zis_photocatalysis --force` | Refuses existing reports | `--force` overwrites reports | Yes | Report tests |
| Rules | `paperwb rules report --project zis_photocatalysis` | Read-only except optional report output | `--force` overwrites rule report | Yes | Rule tests |
| Dashboard | `paperwb dashboard --project zis_photocatalysis --view next-actions` | Read-only terminal output | Optional `--out` requires `--force`; `--no-audit-log` omits ignored local audit state | Yes | Dashboard tests |
| Import | `paperwb import zotero-csv ... --dry-run` | Dry-run available | Writes only when not dry-run | Yes | Import/export tests |
| Export | `paperwb export claims-json --out scratch/claims.json` | Explicit output path | `--force` for files | Yes | Import/export tests |
| Synthetic | `paperwb synthetic generate --project stress_demo` | Refuses existing project | `--force` for regeneration | Creates profile | Stress tests |
