# Terminal Workflow

The terminal workflow is intended for a daily local research loop:

1. Open the dashboard.
2. Review project health and next actions.
3. Pick a reading item, missing note, weak claim, or manuscript warning.
4. Run the relevant local command.
5. Regenerate reports when useful.

Example:

```bash
paperwb dashboard --project zis_photocatalysis
paperwb dashboard --project zis_photocatalysis --view next-actions
paperwb reading queue --project zis_photocatalysis
paperwb followups list --project zis_photocatalysis
paperwb report evidence-map --project zis_photocatalysis --out reports/evidence_map.md --force
```

For writing checks:

```bash
paperwb dashboard --project zis_photocatalysis --manuscript drafts/synthetic_unknown_citations.md --view health
paperwb manuscript qa drafts/synthetic_unknown_citations.md --project zis_photocatalysis --out reports/manuscript_qa.md --force
```

The dashboard intentionally remains plain text and dependency-free. A richer
interactive TUI is deferred until there is a concrete workflow need.

