# Evidence Matrix

An evidence matrix is a theme-specific table of tracked claims.

It includes:

- claim ID and claim text
- supporting paper
- BibTeX key
- evidence type
- strength and confidence
- section or page
- quote or paraphrase
- note limitations
- tags and theme

Generate Markdown, CSV, and JSON:

```bash
paperwb report evidence-matrix \
  --project zis_photocatalysis \
  --theme charge_separation \
  --out scratch/charge_separation_evidence_matrix.md \
  --csv-out scratch/charge_separation_evidence_matrix.csv \
  --json-out scratch/charge_separation_evidence_matrix.json \
  --force
```

The CSV and JSON exports are intended for review tables and audit workflows. They preserve user-entered claim text; they do not rewrite claims.
