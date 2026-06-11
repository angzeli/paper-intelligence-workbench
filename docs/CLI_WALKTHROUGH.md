# CLI Walkthrough

This walkthrough uses synthetic data only and avoids writing over repository reports by sending generated files to `scratch/`.

If you have installed the package, use `paperwb`. If not, replace `paperwb` with `python -m paper_workbench.cli`.

## 1. Inspect the CLI

```bash
paperwb --help
paperwb report --help
paperwb export --help
```

The CLI is grouped around registry validation, BibTeX validation, note parsing, search, reports, exports, project profiles, and workspace diagnostics.

## 2. Validate Registry Metadata

```bash
paperwb validate-registry data/registries/example_papers.csv
```

The synthetic example should report duplicate DOI/title findings. That is expected for the fixture and shows that validation is working.

## 3. Validate BibTeX Entries

```bash
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
```

Use this to find missing authors, invalid years, duplicate DOI values, and entries not linked to registry papers.

## 4. List and Search Papers

```bash
paperwb list --registry data/registries/example_papers.csv --tag photocorrosion
paperwb search photocorrosion --project zis_photocatalysis
paperwb search "charge separation" --registry data/registries/example_papers.csv --notes-dir data/notes
```

Search is local substring matching. It does not use embeddings or external services.

## 5. Extract Claims

```bash
paperwb claims data/notes --output scratch/paperwb_walkthrough_claims.csv
```

Claims come only from structured Markdown notes. Empty or malformed fields are not guessed.

## 6. Generate Reports

```bash
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/paperwb_walkthrough_evidence_map.md --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/paperwb_walkthrough_citation_audit.md --force
paperwb report section-outline --theme photocorrosion --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/paperwb_walkthrough_section_outline.md --force
```

Reports refuse to overwrite existing files unless `--force` is present.

## 7. Use Project Profiles

```bash
paperwb project list
paperwb project validate zis_photocatalysis
paperwb report evidence-map --project zis_photocatalysis --out scratch/paperwb_walkthrough_zis_evidence_map.md --force
```

When `--project` is provided, do not also pass `--registry`, `--notes-dir`, `--bibtex`, `--themes`, or `--reports-dir`. The profile defines those paths.

## 8. Export Local Artifacts

```bash
paperwb export claims-json --project zis_photocatalysis --out scratch/paperwb_walkthrough_zis_claims.json --force
paperwb export theme-claims --project zis_photocatalysis --theme photocorrosion --out scratch/paperwb_walkthrough_photocorrosion_claims.json --force
```

Exports are local files for review, backup, or downstream analysis.

## 9. Diagnose Workspace Health

```bash
paperwb doctor --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/paperwb_walkthrough_workspace_health.md --force
```

Use `doctor` when paths, profile files, notes, or reports do not line up.

## Safety Notes

- The workbench does not download papers.
- The workbench does not include copyrighted PDFs.
- The workbench does not fabricate claims or metadata.
- Generated reports and exports require `--force` before replacing existing files.
- User notes are preserved unless an explicit force option is used for note templates.
