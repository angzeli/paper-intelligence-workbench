# Getting Started

Use this page when you are opening the repository for the first time.

## Install

```bash
python -m pip install -e ".[test]"
paperwb --help
```

No-install fallback:

```bash
python -m paper_workbench.cli --help
```

## First Checks

```bash
paperwb validate-registry data/registries/example_papers.csv
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
paperwb claims data/notes --output scratch/example_claims.csv
```

The example data is synthetic and intentionally includes duplicates, missing fields, weak claims, and incomplete evidence so reports have something to audit.

## First Report

```bash
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/evidence_map.md --force
```

Read the report as an audit of your own tracked evidence, not as a truth judgment about the science.

## Next Steps

- Use [Project Profiles](project-profiles.md) for independent review projects.
- Use [Import / Export](import-export.md) to bring in local CSV, BibTeX, or RIS data.
- Use [Authoring Workbench](authoring-workbench.md) when preparing a literature-review subsection.
- Use [Local Files](local-files.md) to reconcile user-provided files and text sidecars.
