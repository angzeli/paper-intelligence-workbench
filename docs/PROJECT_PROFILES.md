# Project Profiles

Project profiles let one workspace hold multiple literature-review projects without replacing the legacy `data/` workflow.

```text
projects/
  zis_photocatalysis/
    project.json
    registry.csv
    themes.json
    notes/
    bibtex/library.bib
    reports/
```

Create and inspect profiles:

```bash
paperwb project init demo_review
paperwb project list
paperwb project validate demo_review
```

Use a profile with commands:

```bash
paperwb search photocorrosion --project zis_photocatalysis
paperwb claims --project zis_photocatalysis --output data/processed/zis_claims.csv
paperwb report evidence-map --project zis_photocatalysis --force
paperwb doctor --project zis_photocatalysis
```

When `--project` is provided, profile paths are used for registry, notes, BibTeX, themes, and reports. Explicit legacy path flags such as `--registry`, `--notes-dir`, or `--reports-dir` are rejected with a user-facing error instead of being silently ignored. Without `--project`, the existing `data/` workflow remains unchanged.

Profiles are local JSON plus folders only. There is no database and no cloud synchronization.
