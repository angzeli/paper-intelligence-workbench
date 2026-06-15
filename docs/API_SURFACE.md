# API Surface v2

Paper Intelligence Workbench is a local-first command-line project. The Python
package is usable by tests and scripts, but v2 does not promise a broad
stable library API. The stable user interface is the `paperwb` CLI plus the
documented local file formats.

The package does not use cloud APIs, LLM APIs, publisher scraping, or remote
metadata lookup. API helpers operate on user-provided local CSV, JSON,
Markdown, BibTeX, RIS, text sidecar, and project-profile files.

## Stable For v2

The stable external API for v2 is the CLI plus documented file formats.
For Python callers, only these small entry points are treated as stable enough
for local automation:

| Module | Stable entry points | Purpose |
| --- | --- | --- |
| `paper_workbench.registry` | `load_registry`, `save_registry`, `save_registry_json`, `validate_registry`, `filter_papers`, `add_paper` | Registry loading, validation, filtering, and appending |
| `paper_workbench.bibtex` | `parse_bibtex_file`, `validate_bibtex` | Lightweight BibTeX parsing and audit findings |
| `paper_workbench.notes` | `write_note_template`, `parse_note_file` | Structured note template writing and conservative note parsing |
| `paper_workbench.claims` | `collect_notes`, `collect_claims`, `save_claims_csv` | Claim extraction from local structured notes |
| `paper_workbench.tags` | `normalize_tag`, `load_themes`, `map_claims_to_themes` | Tag normalization and theme mapping |
| `paper_workbench.audit` | `citation_audit` | Citation-readiness findings from registry, notes, claims, themes, and BibTeX |
| `paper_workbench.projects` | `create_project_profile`, `list_project_profiles`, `resolve_project_profile` | Project-profile path resolution |
| `paper_workbench.safety` | `audit_data_safety`, `safety_audit_markdown` | Tracked-file data-safety audit |
| `paper_workbench.reading` | `build_reading_queue`, `start_reading_session`, `finish_reading_session`, `collect_followups`, `build_weekly_review` | Local reading-session workflow helpers |
| `paper_workbench.sync` | `build_registry_sync_plan`, `apply_registry_sync_plan`, `build_obsidian_roundtrip_plan` | Local sync planning, safe registry apply, and conflict detection |
| `paper_workbench.manuscript` | `audit_manuscript`, `manuscript_qa_report`, `manuscript_context_table_report`, `build_claim_traceability` | Manuscript citation QA and traceability reports |
| `paper_workbench.rules` | `load_rule_set`, `validate_rule_set`, `run_rule_set`, `rule_report` | Declarative local rule loading, validation, execution, and reporting |
| `paper_workbench.templates` | `list_templates`, `get_template`, `inspect_template`, `create_project_from_template` | Built-in empty project scaffolds and template inspection |
| `paper_workbench.claim_lifecycle` | `build_claim_review_queue`, `mark_claim_status`, `create_contradiction_group` | Experimental v2.2 claim review sidecar helpers |

## Stable Data Models

The dataclasses in `paper_workbench.schema` are stable enough for local scripts:

- `Paper`
- `Author`
- `BibTeXEntry`
- `PaperNote`
- `Claim`
- `EvidenceLink`
- `Tag`
- `ProjectTheme`
- `CitationAuditFinding`
- `ValidationFinding`
- enum-like constants for reading status, claim strength, and evidence type

Fields may grow in future releases, but v1.8 aims to preserve existing field
names and meanings.

## Semi-Stable And Experimental Modules

These modules are public in the package but remain more likely to change. Use
the CLI when possible unless a script specifically needs Python objects:

- `paper_workbench.reporting`: report Markdown helpers.
- `paper_workbench.importers`: Zotero CSV, generic CSV, BibTeX, and RIS import
  workflows.
- `paper_workbench.exports`: CSV, JSON, Markdown, Obsidian, bundle,
  reading-list, and report-index exports.
- `paper_workbench.index`: rebuildable local SQLite search cache helpers.
- `paper_workbench.files`: local file registry, sidecar, hash, duplicate, and
  missing-file helpers.
- `paper_workbench.authoring`: evidence matrix, claim bank, citation bank,
  paragraph plan, readiness, and writing packet helpers.
- `paper_workbench.integrity`: structural consistency checks.
- `paper_workbench.backups`: local backup snapshots and non-destructive restore
  planning.
- `paper_workbench.migration`: legacy `data/` to project-profile migration
  planning/copying.
- `paper_workbench.auditlog`: local JSONL audit log events.
- `paper_workbench.synthetic`: deterministic stress fixtures and generated
  synthetic projects.
- `paper_workbench.drafts`: Markdown draft parsing, citation extraction,
  paragraph evidence matching, and draft-audit report helpers.
- `paper_workbench.manuscript`: reviewer-style manuscript QA and traceability
  helpers built on the draft-audit core.
- `paper_workbench.rules`: local declarative rule engine and built-in adapters.
- `paper_workbench.graph`: local evidence graph models, builders, transparent
  analytics, and JSON/DOT/Markdown exports.
- `paper_workbench.errors`: user-facing diagnostic taxonomy helpers.
- `paper_workbench.doctor`: workspace-health aggregation.

They are useful for tests and release checks, but downstream automation should
prefer CLI commands unless it needs direct Python objects.

## Internal Or Low-Level Modules

These modules are implementation details:

- `paper_workbench.cli`
- `paper_workbench.io`

The `paper_workbench.paths.display_path` helper is shared internally to keep
report path rendering consistent, but `paper_workbench.paths` as a module
remains low-level and should not be treated as a plugin surface.

They can be imported by tests, but they are not a stable extension API.

## Compatibility Notes

- v2 keeps the legacy `data/` workflow and the `projects/` workflow.
- CSV, JSON, Markdown notes, BibTeX, RIS, and theme JSON remain authoritative
  inputs.
- SQLite indexes, audit logs, caches, backups, and generated reports are
  rebuildable or local release artifacts, not remote services.
- The tool audits evidence completeness and local data consistency. It does not
  evaluate scientific truth or fabricate claims, citations, quotes, summaries,
  or polished prose.
