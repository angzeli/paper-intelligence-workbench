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

## Try Synthetic Examples

```bash
paperwb validate-registry data/registries/example_papers.csv
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
paperwb claims data/notes --output scratch/example_claims.csv
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/evidence_map.md --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/citation_audit.md --force
```

## First Real Use

Add a small set of verified papers manually or from a dry-run import. Generate
note templates, fill them yourself from sources you are allowed to use, extract
claims, then run citation/evidence reports.

Do not use the tool to fabricate metadata, claims, quotes, or final prose.
