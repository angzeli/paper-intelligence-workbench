# Getting Started

Use this page when you are new to the repository and want a safe first run.

## What The Tool Is

Paper Intelligence Workbench is a local CLI for literature-review evidence
management. It tracks paper metadata, BibTeX keys, structured notes,
user-entered claims, themes, citation coverage, evidence gaps, and generated
Markdown reports.

## What The Tool Is Not

- It does not read papers automatically.
- It does not use cloud APIs, LLM APIs, embeddings, publisher scraping, OCR, or
  PDF downloads.
- It does not fabricate paper metadata, claims, citations, quotes, summaries, or
  final prose.
- It does not silently overwrite notes, registries, BibTeX files, sync state,
  backups, or migrations.

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

For development checks:

```bash
python -m pip install -e ".[dev]"
python scripts/run_quality_gate.py release
```

If your local bootstrap environment is missing development tools, use the
diagnostic target instead of claiming release readiness:

```bash
python scripts/run_quality_gate.py local-diagnostic
```

## First Green Check

The `clean_demo` project is synthetic and intentionally small.

```bash
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb dashboard --project clean_demo --no-audit-log
```

Expected result: no registry or BibTeX findings, and a dashboard with one
synthetic paper, note, claim, BibTeX entry, and theme.

## Start A New Project

For an empty reusable template:

```bash
paperwb template list
paperwb template create generic --project my_review
```

For a first real FYP-style photocatalysis project:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

The dogfood scaffold is empty. Add verified metadata yourself or through a
reviewed local import. Do not copy PDFs or paper full text into Git.

## Next Reading

- [Core Concepts](../concepts/index.md)
- [Full Literature Review Walkthrough](../workflows/full-literature-review-walkthrough.md)
- [Cookbook](../cookbook/index.md)
- [Stable Surface v3](../STABLE_SURFACE_V3.md)
- [Safety](../safety/index.md)
