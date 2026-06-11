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
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index status --project zis_photocatalysis --check-files
paperwb search "charge separation" --project zis_photocatalysis --indexed
paperwb files scan --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --force
paperwb doctor --out reports/workspace_health.md
```

Imports:

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --dry-run
paperwb import csv data/examples/generic_papers.csv --mapping data/examples/generic_mapping.json --dry-run
paperwb import bibtex data/examples/library_import.bib --dry-run
paperwb import ris data/examples/library.ris --dry-run
```

Import commands preserve existing registry rows. `--fill-missing` fills only blank fields on matched rows. Import reports are written to the selected reports directory unless `--report` is provided. If the report path already exists and `--force` is not provided, the command fails before writing the registry.

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
paperwb report evidence-matrix --theme photocorrosion
paperwb report claim-bank --theme photocorrosion
paperwb report citation-bank --theme photocorrosion
paperwb report paragraph-plan --theme photocorrosion
paperwb report subsection-readiness --theme photocorrosion
paperwb report all
```

Report commands refuse to overwrite an existing output file unless `--force` is provided. The same no-overwrite behavior applies to `doctor --out` and `validate-bib --report`.

Authoring reports:

```bash
paperwb report evidence-matrix --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_evidence_matrix.md --force
paperwb report evidence-matrix --project zis_photocatalysis --theme charge_separation --csv-out reports/charge_matrix.csv --json-out reports/charge_matrix.json --force
paperwb report claim-bank --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_claim_bank.md --force
paperwb report citation-bank --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_citation_bank.md --force
paperwb report paragraph-plan --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_paragraph_plan.md --force
paperwb report subsection-readiness --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_readiness.md --force
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_writing_packet.md --force
```

These commands generate evidence-based planning aids, not final prose.

Exports:

```bash
paperwb export registry-csv --out data/processed/registry.csv
paperwb export registry-json --out data/processed/registry.json
paperwb export claims --out data/processed/claims.csv
paperwb export claims-json --out data/processed/claims.json
paperwb export reading-list --tag photocorrosion --out reports/reading_list.md
paperwb export unread --out reports/unread.md
paperwb export theme-claims --theme photocorrosion --out data/processed/photocorrosion_claims.json
paperwb export reading-list --theme photocorrosion --out reports/photocorrosion.md
paperwb export reading-list --high-priority --format csv --out reports/high_priority.csv
paperwb export obsidian --project zis_photocatalysis --out exports/obsidian_zis
paperwb export bundle --project zis_photocatalysis --out exports/zis_bundle
paperwb export project-summary --project zis_photocatalysis --out reports/project_summary.md
paperwb export report-index --project zis_photocatalysis --out reports/index.md
```

Export commands refuse to overwrite an existing output file unless `--force` is provided. Directory exports such as `obsidian` and `bundle` require a new or empty output directory; they do not merge into or clean non-empty directories.

Indexed search:

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb index status --project zis_photocatalysis --include-text --check-files --out reports/index_status.md --force
paperwb index clear --project zis_photocatalysis
paperwb search photocorrosion --project zis_photocatalysis --indexed
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
paperwb search "charge separation" --project zis_photocatalysis --indexed --out reports/search_charge_separation.md --force
```

The original substring search remains the default unless `--indexed` is provided. Cache databases live under `.paperwb/` and should not be committed.

Local files:

```bash
paperwb files scan --project zis_photocatalysis
paperwb files scan --project zis_photocatalysis --write-registry
paperwb files status --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --force
paperwb files link PAPER_ID projects/zis_photocatalysis/papers/PAPER_ID.pdf --project zis_photocatalysis
paperwb files unlink PAPER_ID --project zis_photocatalysis
paperwb files hash projects/zis_photocatalysis/text/PAPER_ID.txt
paperwb files sidecars --project zis_photocatalysis
```

Local-file commands do not download, scrape, OCR, copy, move, or delete documents. PDF links update `local_pdf_path`; existing values require `--force` to replace. `files scan --write-registry` merges with existing `files.csv` rows so curated notes are preserved. `files unlink` clears `local_pdf_path` only when it removed at least one matching file-registry row, unless `--keep-pdf-path` is used.

Most workflow commands accept `--project NAME` to use profile paths. When `--project` is used, registry, notes, BibTeX, themes, and reports path flags are rejected to avoid silently ignoring user input. Use `--out` for an explicit single report or export destination.
