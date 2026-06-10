# Workflow Examples

## Legacy Data Workflow

```bash
paperwb validate-registry data/registries/example_papers.csv
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
paperwb claims data/notes --output reports/example_claims.csv
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --force
```

## Project Profile Workflow

```bash
paperwb project list
paperwb project validate zis_photocatalysis
paperwb search photocorrosion --project zis_photocatalysis
paperwb report evidence-map --project zis_photocatalysis --force
paperwb report section-outline --project zis_photocatalysis --theme photocorrosion --out projects/zis_photocatalysis/reports/photocorrosion_section_outline.md --force
paperwb export claims-json --project zis_photocatalysis --out data/processed/zis_claims.json --force
```

## End-to-End Script

Run the synthetic workflow script:

```bash
python examples/end_to_end_workflow.py
```

It creates a temporary workspace, initializes a profile, copies synthetic fixtures, validates registry and BibTeX data, parses notes, extracts claims, generates reports, exports claims, and runs workspace health diagnostics.
