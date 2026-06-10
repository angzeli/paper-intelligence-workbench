# Obsidian Export

The Obsidian export writes normal Markdown files. It does not require Obsidian and does not create a web app.

```bash
paperwb export obsidian --project zis_photocatalysis --out exports/obsidian_zis --force
```

The export creates:

- `index.md`
- `papers/<paper_id>.md`
- `tags.md`
- `themes.md`
- `reading_status.md`
- `claims.md`
- `missing_evidence.md`
- `export_summary.md`

Paper pages include metadata, BibTeX key, tags, reading status, theme links, claims, evidence type, evidence location, confidence, and strength.

The export uses only local registry, note, claim, and theme data. It does not invent summaries, claims, or citations.
