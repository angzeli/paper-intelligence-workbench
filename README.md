# 📚 paper-intelligence-workbench

`paper-intelligence-workbench` is a local-first command-line workbench for literature-review projects. It helps a student or researcher track paper metadata, BibTeX keys, structured notes, user-written claims, evidence coverage, citation gaps, reading status, and project health without sending data to cloud services.

Start with [docs/index.md](docs/index.md), [docs/getting-started/index.md](docs/getting-started/index.md), and [docs/STABLE_SURFACE_V3.md](docs/STABLE_SURFACE_V3.md).

## What It Is Not

- It does not use cloud APIs, LLM APIs, embeddings, publisher scraping, PDF downloading, OCR, or a browser app.
- It does not include copyrighted PDFs or copied paper full text.
- It does not fabricate real paper metadata, citations, claims, quotes, summaries, or conclusions.
- It does not judge scientific truth or write final literature-review prose.
- It does not silently overwrite notes, registries, BibTeX files, migrations, restores, or sync outputs.

## Install

From the repository root:

```bash
python -m pip install -e ".[test]"
paperwb --help
```

If editable install is not available, run the CLI from the repository root:

```bash
python -m paper_workbench.cli --help
```

## Quickstart

Use the clean synthetic project first:

```bash
paperwb validate-registry projects/clean_demo/registry.csv --strict
paperwb validate-bib projects/clean_demo/bibtex/library.bib --registry projects/clean_demo/registry.csv --strict
paperwb dashboard --project clean_demo --no-audit-log
paperwb claims data/notes --output scratch/example_claims.csv
```

Use `projects/zis_photocatalysis` when you want a populated synthetic project with intentionally imperfect evidence gaps for dashboard, rule, citation-audit, and manuscript-QA demos.

Create an empty real-project scaffold:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

For real private data, keep the workspace outside this repository and register a local pointer:

```bash
paperwb external add fyp_zis_real <external_workspace> --project fyp_zis_lit_review
paperwb external validate fyp_zis_real --strict
paperwb external run fyp_zis_real dashboard
```

External registrations live in ignored `.paperwb-local/workspaces.json`. Do not commit that file or copy private project data into this repository.

## Core Workflow

1. Create a project profile or dogfooding scaffold.
2. Add verified metadata and BibTeX manually or through dry-run imports.
3. Generate note templates and write notes yourself.
4. Extract claims from structured notes.
5. Generate evidence maps, citation audits, dashboards, and writing packets.
6. Audit drafts heuristically without rewriting final prose.
7. Back up before risky imports, migrations, restores, or sync applies.

## Stable Starting Points

Stable v3 workflows include:

- `init`, `project`, `template`, `dogfood`, `external`
- `validate-registry`, `validate-bib`, `add-paper`, `list`
- `note-template`, `claims`
- core `report` commands, `dashboard`, `doctor`
- `support` diagnostics and `compatibility` inspection

See [docs/STABLE_SURFACE_V3.md](docs/STABLE_SURFACE_V3.md) and [docs/CLI_REFERENCE_V3.md](docs/CLI_REFERENCE_V3.md).

## Experimental Workflows

Experimental workflows remain local and tested, but their schemas and report formats are not frozen:

- sync apply, backup restore, migration run
- indexed search, local-file sidecars, incremental rebuild metadata
- manuscript QA, reading sessions, rule engine, workflow recipes
- evidence graph exports, claim lifecycle, review packets

See [docs/EXPERIMENTAL_FEATURES_V3.md](docs/EXPERIMENTAL_FEATURES_V3.md).

## Safety Boundary

The repository examples are synthetic or empty scaffolds. Real projects should live in external workspaces. Support bundles redact private content by default and must not include PDFs, full notes, full drafts, cache databases, backups, or raw audit logs.

Safety docs:

- [docs/DATA_SAFETY_V3.md](docs/DATA_SAFETY_V3.md)
- [docs/PRIVATE_DOGFOODING.md](docs/PRIVATE_DOGFOODING.md)
- [docs/EXTERNAL_WORKSPACES.md](docs/EXTERNAL_WORKSPACES.md)
- [docs/SUPPORT_BUNDLES.md](docs/SUPPORT_BUNDLES.md)
- [docs/GENERATED_REPORT_POLICY.md](docs/GENERATED_REPORT_POLICY.md)

## Repository Layout

```text
paper-intelligence-workbench/
├── paper_workbench/        # Python package and CLI implementation
├── data/                   # legacy synthetic examples and registries
├── projects/               # synthetic project-profile workspaces
├── drafts/                 # synthetic draft/manuscript examples
├── docs/                   # user, workflow, safety, and maintainer docs
├── reports/                # generated audits, readiness reports, and examples
├── notebooks/              # lightweight synthetic workflow notebooks
├── examples/               # runnable local workflow scripts
├── scripts/                # smoke checks, notebook checks, and safety audits
└── tests/                  # unit, CLI, regression, and workflow tests
```

## Test

```bash
python -m pytest -q
python scripts/data_safety_audit.py --out scratch/data_safety.md --strict
python scripts/run_quality_gate.py local-diagnostic --out scratch/quality_gate.md
```

The strict release quality gate expects development tooling from `.[dev]`.

## Status

Current release line and package metadata are `3.5`. The `v3.0rc2` reports are historical release-hardening artifacts from the stabilization cycle, not a separate package version or rollback target. No release has been published from this repository.

## Author

Angze Li
