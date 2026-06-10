# Local Search

v0.5 adds an optional local SQLite search index. The original live substring search remains the default:

```bash
paperwb search photocorrosion --project zis_photocatalysis
```

Use indexed search only after rebuilding the cache:

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search "charge separation" --project zis_photocatalysis --indexed
```

The index is local and rebuildable. It stores derived text from registry rows, BibTeX entries, structured notes, claims, themes, tags, and optional user-provided text sidecars.

## Indexed Result Fields

Indexed search prints:

- source type
- paper ID
- score
- title
- source path

Markdown export includes matched field and snippet:

```bash
paperwb search "charge separation" --project zis_photocatalysis --indexed --out reports/search_charge_separation.md --force
```

## Source Filters

```bash
paperwb search "charge transfer" --project zis_photocatalysis --indexed --claims
paperwb search "photocorrosion" --project zis_photocatalysis --indexed --notes
paperwb search "photocorrosion" --project zis_photocatalysis --indexed --text
```

The `--text` filter searches only sidecar records in the SQLite index. It does not parse PDFs.

