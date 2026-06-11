# Project Profiles

Project profiles keep independent review projects under `projects/`.

```text
projects/<project>/
  registry.csv
  themes.json
  notes/
  bibtex/
  reports/
  text/
  papers/
```

## Commands

```bash
paperwb project list
paperwb project init demo_review
paperwb project validate zis_photocatalysis
```

## Use A Project

```bash
paperwb report evidence-map --project zis_photocatalysis --force
paperwb search photocorrosion --project zis_photocatalysis
paperwb files scan --project zis_photocatalysis
```

The legacy `data/` workflow remains available for single-project use.

Detailed docs: [PROJECT_PROFILES.md](PROJECT_PROFILES.md).
