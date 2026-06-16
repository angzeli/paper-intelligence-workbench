# 📚 paper-intelligence-workbench

`paper-intelligence-workbench` is a local-first CLI tool for small academic literature-review projects. It manages paper metadata, structured Markdown notes, user-recorded claims, evidence links, BibTeX validation, project profiles, theme coverage, citation-audit reports, and an optional SQLite search cache without cloud services, publisher scraping, or LLM APIs.

Start with [docs/GETTING_STARTED_V2.md](docs/GETTING_STARTED_V2.md), [docs/STABLE_SURFACE_V2.md](docs/STABLE_SURFACE_V2.md), and [docs/COMMAND_CONTRACTS_V2.md](docs/COMMAND_CONTRACTS_V2.md).

## 🧭 What It Does

- Maintains local paper registries, BibTeX files, notes, themes, rules, and reports.
- Generates structured Markdown note templates and extracts user-entered claims.
- Validates registry rows, BibTeX entries, citations, notes, themes, and evidence links.
- Builds evidence maps, local evidence graphs, citation audits, claim banks, claim review queues, writing packets, and manuscript QA reports.
- Supports project profiles, reusable project templates, reading queues, follow-up actions, and dashboards.
- Imports and exports local CSV, BibTeX, RIS, JSON, Markdown, Obsidian-style vaults, and backup bundles.
- Provides local search, optional SQLite indexing, file audits, backup planning, migration checks, sync plans, and rule reports.
- Tracks manual claim lifecycle state and contradiction/tension groups without auto-verifying claims.
- Runs declarative local workflow recipes for repeatable validation, report, dashboard, manuscript QA, and backup-precheck routines.
- Exports local review packets and imports reviewer comments as separate advisory sidecars.
- Plans incremental rebuilds with local content fingerprints for repeated large-project work.

## 🚫 What It Does Not Do

- No cloud APIs, LLM APIs, embeddings, publisher scraping, PDF downloading, OCR, or web app.
- No copyrighted PDFs or copied full-text papers in examples.
- No fabricated paper metadata, citations, claims, quotes, summaries, or conclusions.
- No scientific-truth judgment and no polished final prose generation.
- No silent overwrites, migrations, restores, or sync writes without explicit command flags.
- No arbitrary code execution from custom rule files.

## 🗃️ Repository File Tree

```text
paper-intelligence-workbench/
├── paper_workbench/        # Python package and CLI implementation
├── data/                   # legacy synthetic examples and registries
│   ├── bibtex/
│   ├── examples/
│   ├── notes/
│   └── registries/
├── projects/               # project-profile workspaces and synthetic fixtures
├── drafts/                 # synthetic draft/manuscript examples
├── docs/                   # user docs, workflow guides, schema docs, API/CLI surfaces
├── reports/                # generated Markdown audits, readiness reports, and examples
├── notebooks/              # lightweight workflow notebooks using synthetic data
├── examples/               # runnable local workflow scripts
├── scripts/                # smoke checks, notebook checks, safety audits, performance checks
├── tests/                  # unit, CLI, regression, adversarial, and workflow tests
├── pyproject.toml          # package metadata and CLI entry point
├── README.md               # public project overview
├── CHANGELOG.md            # version history
└── AGENTS.md               # repository rules for future agents
```

## ⚙️ Installation

From the repository root:

```bash
python -m pip install -e ".[test]"
```

The CLI entry point is:

```bash
paperwb --help
```

You can also run it without installing from the repository root:

```bash
python -m paper_workbench.cli --help
```

In offline or restricted-network environments, `pip` may be unable to fetch build dependencies for editable install. In that case, use the no-install `python -m paper_workbench.cli ...` form from the repository root, or install after local build dependencies such as `setuptools` and `pytest` are available. For normal work inside initialized workspaces, use `paperwb`; workspace data folders can shadow the Python package when using `python -m`.

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for release-check commands and troubleshooting.

## 🚀 Quickstart

Initialize a workspace:

```bash
paperwb init
```

Create a project from a template:

```bash
paperwb template list
paperwb template inspect photocatalysis
paperwb template create photocatalysis --project my_photocatalysis_review
paperwb dashboard --project my_photocatalysis_review --no-audit-log
```

Start a real-project dogfooding scaffold:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

Validate a clean bundled project registry:

```bash
paperwb validate-registry projects/zis_photocatalysis/registry.csv --strict
```

Validate its synthetic BibTeX library:

```bash
paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict
```

Extract claims from notes:

```bash
paperwb claims data/notes --output scratch/example_claims.csv
```

Generate reports:

```bash
paperwb report inventory --registry data/registries/example_papers.csv --out scratch/inventory.md --force
paperwb report bibtex-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --out scratch/bibtex_audit.md --force
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/evidence_map.md --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/citation_audit.md --force
paperwb graph summary --project zis_photocatalysis --out scratch/evidence_graph_summary.md --force
```

Run a repeatable workflow recipe:

```bash
paperwb workflow list
paperwb workflow show daily_check
paperwb workflow run daily_check --project zis_photocatalysis --dry-run --out scratch/daily_check.md --force
```

Run diagnostics and a section outline:

```bash
paperwb doctor --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/workspace_health.md --force
paperwb report section-outline --theme photocorrosion --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/photocorrosion_section_outline.md --force
```

## 🧪 Project Profile Workflow

Project profiles are the recommended v2 workflow. They keep each literature
review in its own local folder under `projects/`, with separate registry,
BibTeX, notes, themes, rules, reports, and safety artifacts.

```bash
paperwb template list
paperwb template inspect photocatalysis
paperwb template create photocatalysis --project my_review
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb project validate my_review
paperwb dashboard --project my_review --no-audit-log
```

After adding verified paper metadata and user-written notes, use the same
project flag across the main daily workflow:

```bash
paperwb note-template PAPER_ID --project my_review
paperwb claims --project my_review --output scratch/my_review_claims.csv --force
paperwb report evidence-map --project my_review --out scratch/my_review_evidence_map.md --force
paperwb report citation-audit --project my_review --out scratch/my_review_citation_audit.md --force
paperwb manuscript qa drafts/synthetic_good_section.md --project my_review --out scratch/my_review_manuscript_qa.md --force
paperwb reading queue --project my_review --out scratch/my_review_reading_queue.md --force
paperwb integrity check --project my_review --out scratch/my_review_integrity.md --force
paperwb backup create --project my_review --notes "Before major note cleanup"
```

Templates create empty scaffolds only. They do not include real paper metadata,
claims, quotes, or copyrighted documents. Existing project files are not
overwritten unless a command exposes and receives an explicit force flag.

For a first real FYP-style photocatalysis review, prefer the dogfood scaffold.
It adds onboarding checklists, a first-week plan, evidence-tracking reminders,
and an expanded photocatalysis theme pack while still keeping the project empty
until you add verified metadata yourself.

## 🔧 Common Workflows

```bash
# Import/export
paperwb import zotero-csv data/examples/zotero_export.csv --project zis_photocatalysis --dry-run --force
paperwb export reading-list --theme photocorrosion --project zis_photocatalysis --out scratch/reading_list.md --force

# Search and index
paperwb search photocorrosion --project zis_photocatalysis
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search photocorrosion --project zis_photocatalysis --indexed
paperwb rebuild plan --project zis_photocatalysis --out scratch/rebuild_plan.md --force-report
paperwb rebuild run --project zis_photocatalysis
paperwb graph build --project zis_photocatalysis
paperwb graph export --project zis_photocatalysis --format json --out scratch/evidence_graph.json --force

# Writing and manuscript QA
paperwb workflow run pre_writing_check --project zis_photocatalysis --theme photocorrosion --dry-run --out scratch/pre_writing_check.md --force
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/writing_packet.md --force
paperwb manuscript qa drafts/synthetic_overconfident_section.md --project zis_photocatalysis --out scratch/manuscript_qa.md --force
paperwb review-packet create --project zis_photocatalysis --theme photocorrosion --out scratch/review_packet_photocorrosion --force
# Fill scratch/review_packet_photocorrosion/comments.csv before importing comments.
paperwb review-packet import-comments scratch/review_packet_photocorrosion/comments.csv --project zis_photocatalysis --theme photocorrosion --dry-run

# Reading and safety
paperwb reading queue --project zis_photocatalysis
paperwb followups list --project zis_photocatalysis
paperwb integrity check --project zis_photocatalysis --out scratch/integrity.md --force
paperwb backup create --project zis_photocatalysis --notes "Before major note cleanup"
```

Use `--dry-run` for imports, sync, restore, and migration planning before writing
changes. Use `--force` only when you intend to overwrite an output file.

## 🗂️ Data Model

- Registry: CSV rows with stable `paper_id` values, metadata, BibTeX keys, tags, reading status, note paths, priorities, and user comments.
- Notes: structured Markdown files with metadata, summaries, methods, claims, evidence, open questions, follow-ups, and personal notes.
- Claims: user-entered statements extracted from notes, with evidence type, location, confidence, strength, tags, themes, and comments.
- Themes: local JSON definitions used for evidence maps, dashboards, rules, and writing packets.
- Evidence graph: derived nodes and edges connecting papers, notes, claims, themes, tags, BibTeX entries, sessions, and follow-ups.
- Reports: generated Markdown or CSV/JSON outputs; they are audit artifacts, not authoritative source data.

Schema docs:
[registry](docs/REGISTRY_SCHEMA.md),
[notes](docs/NOTE_FORMAT.md),
[BibTeX audit](docs/BIBTEX_AUDIT.md),
and [v2 schema freeze](docs/SCHEMA_FREEZE_V2.md).

## 📊 Report Examples

Reports are written to `reports/` for legacy `data/` workflows or to a
project's `reports/` folder when `--project` is used. Existing outputs are not
overwritten unless `--force` is provided.

Common reports include inventory, reading status, BibTeX audit, citation audit,
evidence map, theme dashboard, missing notes, weak claims, evidence matrix,
claim bank, citation bank, paragraph plan, subsection readiness, manuscript QA,
workspace integrity, evidence graph, and dashboard summaries.

## ⌨️ CLI Reference

```text
paperwb init
paperwb template list
paperwb template create photocatalysis --project my_review
paperwb project validate my_review
paperwb validate-registry projects/zis_photocatalysis/registry.csv --strict
paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib --registry projects/zis_photocatalysis/registry.csv --strict
paperwb list
paperwb note-template PAPER_ID
paperwb claims data/notes/
paperwb search QUERY
paperwb report evidence-map
paperwb report citation-audit
paperwb graph summary --project zis_photocatalysis
paperwb writing-packet --theme photocorrosion
paperwb review-packet create --project zis_photocatalysis --theme photocorrosion --out scratch/review_packet --force
paperwb doctor
paperwb dogfood create photocatalysis --project fyp_review
paperwb dogfood plan-from-files photocatalysis --project fyp_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
paperwb import zotero-csv data/examples/zotero_export.csv --dry-run
paperwb export claims --out scratch/claims.csv
paperwb dashboard --project zis_photocatalysis
```

Run `paperwb --help` or see [docs/CLI_REFERENCE_V2.md](docs/CLI_REFERENCE_V2.md)
for the full command map.

## ⚠️ Limitations

- BibTeX parsing targets common local entries, not every BibTeX edge case.
- Markdown note parsing expects the provided template headings.
- Default search is substring-based; indexed search is opt-in and uses local SQLite with FTS5 plus substring fallback behavior.
- Theme mapping is tag-based only.
- Evidence graph analytics are local connectivity checks, not truth or quality scores.
- SQLite indexing is a rebuildable cache, not an authoritative database.
- Citation audit checks completeness of user notes, not scientific correctness.

## 📘 More Documentation

- [docs/GETTING_STARTED_V2.md](docs/GETTING_STARTED_V2.md)
- [docs/STABLE_SURFACE_V2.md](docs/STABLE_SURFACE_V2.md)
- [docs/REAL_PROJECT_ONBOARDING.md](docs/REAL_PROJECT_ONBOARDING.md)
- [docs/FYP_DOGFOODING_WORKFLOW.md](docs/FYP_DOGFOODING_WORKFLOW.md)
- [docs/EXPERIMENTAL_FEATURES_V2.md](docs/EXPERIMENTAL_FEATURES_V2.md)
- [docs/COMMAND_CONTRACTS_V2.md](docs/COMMAND_CONTRACTS_V2.md)
- [docs/CLI_REFERENCE_V2.md](docs/CLI_REFERENCE_V2.md)
- [docs/EVIDENCE_GRAPH.md](docs/EVIDENCE_GRAPH.md)
- [docs/GRAPH_EXPORTS.md](docs/GRAPH_EXPORTS.md)
- [docs/GRAPH_ANALYTICS.md](docs/GRAPH_ANALYTICS.md)
- [docs/REVIEW_PACKETS.md](docs/REVIEW_PACKETS.md)
- [docs/COMMENT_IMPORT.md](docs/COMMENT_IMPORT.md)
- [docs/RESPONSE_TO_REVIEW.md](docs/RESPONSE_TO_REVIEW.md)
- [docs/REPORTS_V2.md](docs/REPORTS_V2.md)
- [docs/DATA_SAFETY_V2.md](docs/DATA_SAFETY_V2.md)
- [docs/KNOWN_LIMITATIONS_V2.md](docs/KNOWN_LIMITATIONS_V2.md)

## 🧭 Roadmap

See [docs/ROADMAP_V2.md](docs/ROADMAP_V2.md) for the current maintenance roadmap.

## 👤 Author

Angze Li
