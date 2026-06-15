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

Start with the clean bundled project profile. Use `--strict` when validation
errors should make a script fail.

Validate the registry:

```bash
paperwb validate-registry projects/zis_photocatalysis/registry.csv --strict
```

Validate BibTeX against the registry:

```bash
paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict
```

Extract claims from structured notes:

```bash
paperwb claims --project zis_photocatalysis --output scratch/paperwb_zis_claims.csv --force
```

Generate a temporary evidence map:

```bash
paperwb report evidence-map --project zis_photocatalysis --out scratch/paperwb_zis_evidence_map.md --force
```

Generate a temporary citation audit:

```bash
paperwb report citation-audit --project zis_photocatalysis --out scratch/paperwb_zis_citation_audit.md --force
```

The `--force` flag is required only when replacing an existing report or export file.

The legacy `data/` fixtures are also synthetic, but they intentionally contain
duplicates and incomplete entries so audit commands have findings to show.

## 4. Try a Project Profile

Project profiles keep independent literature-review projects under `projects/`.

```bash
paperwb project list
paperwb project validate zis_photocatalysis
paperwb search photocorrosion --project zis_photocatalysis
paperwb report section-outline --project zis_photocatalysis --theme photocorrosion --out scratch/paperwb_photocorrosion_outline.md --force
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
