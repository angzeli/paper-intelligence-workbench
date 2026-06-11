# Quickstart for External Users

This guide is for a new user opening `paper-intelligence-workbench` for the first time.

The workbench is local-first. It reads your CSV registries, Markdown notes, BibTeX files, and theme definitions from this repository or from project folders under `projects/`. It does not call cloud services, LLM APIs, publisher websites, or external databases. It never invents paper metadata, claims, quotes, or conclusions.

## 1. Install Locally

From the repository root:

```bash
python -m pip install -e ".[test]"
python -m paper_workbench.cli --help
```

You can use `paperwb` after installation, or run the module form shown above.

In offline or restricted-network environments, editable install may fail if `pip` cannot fetch build dependencies. The module form still works from the repository root without installing the package.

## 2. Understand the Example Data

The included corpus is synthetic. It intentionally contains duplicate DOIs, incomplete BibTeX entries, weak claims, missing evidence locations, and under-supported themes. Those problems are useful because they show what the audit reports catch.

No copyrighted PDFs are included.

## 3. Run the Safe First Workflow

Validate the registry:

```bash
paperwb validate-registry data/registries/example_papers.csv
```

Validate BibTeX against the registry:

```bash
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
```

Extract claims from structured notes:

```bash
paperwb claims data/notes --output /private/tmp/paperwb_example_claims.csv
```

Generate a temporary evidence map:

```bash
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_evidence_map.md --force
```

Generate a temporary citation audit:

```bash
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_citation_audit.md --force
```

The `--force` flag is required only when replacing an existing report or export file.

## 4. Try a Project Profile

Project profiles keep independent literature-review projects under `projects/`.

```bash
paperwb project list
paperwb project validate zis_photocatalysis
paperwb search photocorrosion --project zis_photocatalysis
paperwb report section-outline --project zis_photocatalysis --theme photocorrosion --out /private/tmp/paperwb_photocorrosion_outline.md --force
```

When `--project` is used, the profile supplies registry, notes, BibTeX, themes, and report paths. Do not combine `--project` with path override flags such as `--registry` or `--reports-dir`.

## 5. Bring Your Own Project

Create a project profile:

```bash
paperwb project init my_review
```

Then edit the local files under:

```text
projects/my_review/
  registry.csv
  bibtex/library.bib
  notes/
  themes.json
  reports/
```

Add only user-verified metadata and notes. Do not paste fabricated claims or unverifiable quotes.

## 6. What To Read First

- `docs/REGISTRY_SCHEMA.md` for registry fields.
- `docs/NOTE_FORMAT.md` for structured note sections.
- `docs/BIBTEX_AUDIT.md` for citation validation.
- `docs/CITATION_AUDIT.md` for completeness checks.
- `docs/REPORT_GALLERY.md` for choosing the right report.
