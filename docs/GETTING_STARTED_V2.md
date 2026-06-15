# Getting Started v2

Use this path first if you are new to Paper Intelligence Workbench.

## Install Or Run Locally

```bash
python -m pip install -e ".[test]"
paperwb --help
```

No-install fallback from the repository root only:

```bash
python -m paper_workbench.cli --help
```

Use `paperwb` for normal work after installation. Initialized workspaces contain
a local `paper_workbench/` data folder, so `python -m paper_workbench.cli ...`
can be shadowed if run from inside a workspace instead of the repository root.

## First Local Project

```bash
paperwb init
paperwb template list
paperwb template create photocatalysis --project my_review
paperwb dashboard --project my_review --no-audit-log
```

The template creates an empty scaffold. Warnings about missing papers, notes, or
evidence are expected.

For a real FYP-style photocatalysis dogfood project, use the onboarding scaffold:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

If you already have a private folder of PDFs and a local BibTeX file, generate a
planning report without copying files or writing registry rows:

```bash
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
```

## Try A Clean Synthetic Project

Use `--strict` when you want validation commands to return non-zero for
error-level findings.

```bash
paperwb validate-registry projects/zis_photocatalysis/registry.csv --strict
paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict
paperwb claims --project zis_photocatalysis --output scratch/zis_claims.csv --force
paperwb report evidence-map --project zis_photocatalysis --out scratch/zis_evidence_map.md --force
paperwb report citation-audit --project zis_photocatalysis --out scratch/zis_citation_audit.md --force
```

## Try Legacy Audit Fixtures

The legacy `data/` fixtures intentionally contain duplicate and incomplete
synthetic records so audit reports have findings to show.

```bash
paperwb claims data/notes --output scratch/example_claims.csv
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/evidence_map.md --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/citation_audit.md --force
```

## First Real Use

Add a small set of verified papers manually or from a dry-run import. Generate
note templates, fill them yourself from sources you are allowed to use, extract
claims, then run citation/evidence reports.

Do not use the tool to fabricate metadata, claims, quotes, or final prose.
