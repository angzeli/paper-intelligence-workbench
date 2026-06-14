# FYP Dogfooding Workflow

This workflow is for an FYP-style photocatalysis literature review. It starts
with an empty local project and builds toward a real evidence-tracking workspace.

## Start

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
```

The generated project includes onboarding files, a first-week plan, an evidence
tracking checklist, and an expanded photocatalysis theme pack.

## Theme Pack

The photocatalysis dogfood pack includes empty themes for ZnIn2S4 structure,
xanthate-derived thin films, precursor chemistry, charge separation,
heterojunctions, cocatalysts, Co-Pi and CoOx, photocorrosion and stability, CO2
adsorption, CO2 reduction products, selectivity, sacrificial agents, reactor
configuration, characterization methods, quantum efficiency, and controls.

These themes are labels for organizing user-entered evidence. They are not
claims.

## Metadata-backed Starter Plan

Use this only against local files you are allowed to inspect:

```bash
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
```

Review the plan manually. Add only verified metadata to the registry.

## First Week

1. Choose a small starter set.
2. Validate registry and BibTeX after every batch.
3. Generate note templates for papers you actually read.
4. Fill claims manually with evidence locations.
5. Generate evidence-map and citation-audit reports.
6. Use dashboard and rules reports for cleanup before drafting.

Do not use the tool to summarize papers automatically or write final prose.
