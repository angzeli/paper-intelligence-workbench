# CLI Reference

This page is a site-friendly entry point. The fuller reference is [CLI_REFERENCE.md](CLI_REFERENCE.md).

## Core Commands

```text
paperwb init
paperwb project list
paperwb validate-registry PATH
paperwb validate-bib PATH --registry PATH
paperwb add-paper --title "..." --year 2026
paperwb list
paperwb note-template PAPER_ID
paperwb claims NOTES_DIR
paperwb search QUERY
paperwb report REPORT_TYPE
paperwb doctor
```

## Project-Aware Commands

Most workflows accept `--project NAME`:

```bash
paperwb search photocorrosion --project zis_photocatalysis
paperwb report evidence-map --project zis_photocatalysis --force
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/writing_packet.md --force
```

When `--project` is used, path overrides for registry, notes, BibTeX, themes, and reports are rejected in most commands to avoid ambiguity.

## Import / Export

```bash
paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run
paperwb export claims-json --project zis_photocatalysis --out scratch/claims.json --force
```

## Local Search And Files

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
paperwb files scan --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --force
```

Use `paperwb COMMAND --help` for exact options.
