# Photocatalysis Template Overview

This template is a synthetic scaffold for an FYP-style photocatalysis
literature-review project. It contains no real paper metadata, PDFs, claims,
quotes, or conclusions.

## Included Themes

| Theme | Purpose |
| --- | --- |
| material-synthesis | Track synthesis routes, precursors, and crystal-growth context |
| thin-films | Track deposition, coating, and film-fabrication evidence |
| charge-separation | Track interface and photocarrier evidence |
| photocorrosion | Track degradation and self-oxidation evidence |
| cocatalysts | Track surface sites and cocatalyst loading evidence |
| CO2 reduction | Track CO2 reduction evidence without asserting truth |
| selectivity | Track product-distribution and selectivity evidence |
| stability | Track durability and cycling evidence |
| reactor-design | Track reactor and mass-transfer context |
| characterization | Track XPS, XRD, microscopy, spectroscopy, and related evidence |

## Included Rule Examples

- Each major theme should have at least 3 papers before writing.
- Read papers should have structured notes.
- Included papers should have BibTeX keys.
- Strong claims should have page or section evidence.
- Manuscript citations should resolve to local registry and BibTeX entries.

## First Workflow

```bash
paperwb template create photocatalysis --project my_photocatalysis_review
paperwb doctor --project my_photocatalysis_review
paperwb dashboard --project my_photocatalysis_review --no-audit-log
paperwb rules validate-config --project my_photocatalysis_review
```

The template is ready for real user-entered sources, but it starts empty by
design.
