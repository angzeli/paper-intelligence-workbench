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

1. Create an external private workspace.
2. Initialize the FYP photocatalysis dogfood project.
3. Add 10-15 verified papers manually.
4. Add BibTeX manually or through a reviewed Zotero export.
5. Validate registry.
6. Validate BibTeX.
7. Generate note templates.
8. Read papers manually.
9. Write structured notes manually.
10. Extract claims from the notes.
11. Generate an evidence map.
12. Generate a citation audit.
13. Generate a writing packet or section outline.
14. Draft one 600-1000 word subsection yourself.
15. Run manuscript or draft QA as a heuristic audit.
16. Review weak claims and missing evidence.
17. Back up the project.
18. Generate a sanitized support bundle only if needed.

Do not use the tool to summarize papers automatically or write final prose.
