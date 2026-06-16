# Getting Started v3

Paper Intelligence Workbench is a local-first command-line workbench for
literature-review projects. It helps track paper metadata, BibTeX linkage,
structured notes, user-entered claims, evidence gaps, and writing readiness.

It does not read papers for you, scrape publishers, use cloud or LLM APIs,
fabricate claims, or write final literature-review prose. No cloud APIs or LLM
APIs are required for any v3.0rc workflow.

## Install Or Run Locally

From the repository root:

```bash
python -m pip install -e ".[test]"
paperwb --help
```

Without installing, from the repository root:

```bash
python -m paper_workbench.cli --help
```

Use `paperwb` inside workspaces after installation. A local workspace folder
named `paper_workbench/` can shadow the package when using `python -m`.

## Fast Green First Run

The clean bundled project is intentionally small and synthetic:

```bash
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb dashboard --project clean_demo --no-audit-log
```

Use `projects/zis_photocatalysis` when you want a populated synthetic project
with realistic evidence gaps and warnings.

## Start A Real Project Safely

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

The dogfooding scaffold is empty. Add real metadata manually or through a
reviewed local import. Do not commit PDFs, copied paper text, or private
reference paths.

## First Daily Loop

1. Add or import metadata.
2. Validate registry and BibTeX.
3. Generate a note template.
4. Read the paper yourself.
5. Write structured notes and claims manually.
6. Extract claims.
7. Generate evidence maps, citation audits, checklists, and dashboards.
8. Back up before risky migrations, restores, or sync applies.

## Current Release Docs

- `docs/STABLE_SURFACE_V3.md`
- `docs/EXPERIMENTAL_FEATURES_V3.md`
- `docs/COMMAND_CONTRACTS_V3.md`
- `docs/SCHEMA_REFERENCE_V3.md`
- `docs/DATA_SAFETY_V3.md`
