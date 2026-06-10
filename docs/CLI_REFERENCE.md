# CLI Reference

Core commands:

```bash
paperwb init
paperwb project init NAME
paperwb project list
paperwb project validate NAME
paperwb validate-registry data/registries/papers.csv
paperwb validate-bib data/bibtex/library.bib --registry data/registries/papers.csv
paperwb add-paper --title "..." --year 2026
paperwb list --tag photocorrosion
paperwb note-template PAPER_ID
paperwb claims data/notes --output reports/claims.csv
paperwb search "charge separation" --claims
paperwb doctor --out reports/workspace_health.md
```

Report types:

```bash
paperwb report inventory
paperwb report reading-status
paperwb report papers-by-tag
paperwb report bibtex-audit
paperwb report claims-by-theme
paperwb report evidence-map
paperwb report citation-audit
paperwb report missing-notes
paperwb report weak-claims
paperwb report theme-dashboard
paperwb report missing-evidence
paperwb report workspace-health
paperwb report section-outline --theme photocorrosion
paperwb report all
```

Report commands refuse to overwrite an existing output file unless `--force` is provided. The same no-overwrite behavior applies to `doctor --out` and `validate-bib --report`.

Exports:

```bash
paperwb export registry-csv --out data/processed/registry.csv
paperwb export registry-json --out data/processed/registry.json
paperwb export claims --out data/processed/claims.csv
paperwb export claims-json --out data/processed/claims.json
paperwb export reading-list --tag photocorrosion --out reports/reading_list.md
paperwb export unread --out reports/unread.md
paperwb export theme-claims --theme photocorrosion --out data/processed/photocorrosion_claims.json
```

Export commands refuse to overwrite an existing output file unless `--force` is provided.

Most workflow commands accept `--project NAME` to use profile paths. When `--project` is used, registry, notes, BibTeX, themes, and reports path flags are rejected to avoid silently ignoring user input. Use `--out` for an explicit single report or export destination.
