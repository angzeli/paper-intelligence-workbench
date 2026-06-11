# Photocatalysis Template

The photocatalysis template is intended for an FYP-style literature-review
project. It provides domain vocabulary and checklists only. It does not include
real paper metadata or scientific claims.

## Themes

- material synthesis
- thin films
- charge separation
- photocorrosion
- cocatalysts
- CO2 reduction
- selectivity
- stability
- reactor design
- characterization

## Rule Examples

- Each major theme should have at least three supporting papers before writing.
- Read or deeply read papers should have structured notes.
- Included papers should have BibTeX keys.
- Strong claims should have page or section evidence.
- Manuscript citations should resolve to local registry and BibTeX entries.

## Recommended Workflow

```bash
paperwb template create photocatalysis --project my_photocatalysis_review
paperwb doctor --project my_photocatalysis_review
paperwb dashboard --project my_photocatalysis_review --no-audit-log
paperwb rules report --project my_photocatalysis_review --out scratch/photo_rules.md --force
```

Use this template to organize verified local sources. Do not let the tool infer
material performance or scientific conclusions.
