# Architecture Audit v2.6

Date: 2026-06-16  
Scope: internal architecture stabilization and maintainability review after the
v2.5 performance and incremental rebuild work.

## Inspection Summary

- `paper_workbench/cli.py` remains the largest module at roughly 3,785 lines and
  owns argument parsing, dispatch, project-path resolution, write preflights,
  audit-log calls, and command output.
- Large feature modules combine models, analysis, persistence, and Markdown
  rendering: `workflow.py`, `rules.py`, `authoring.py`, `index.py`,
  `review_packets.py`, `reading.py`, `sync.py`, `graph.py`, `drafts.py`,
  `registry.py`, and `importers.py`.
- Path display and path containment helpers were duplicated across integrity,
  migration, backups, safety, imports, sync, rules, claims, reading, and index
  code.
- Markdown table escaping was duplicated in many report modules through local
  `_escape` helpers.
- `ValidationFinding` construction had small duplicate local factories in
  health/integrity/importer-style modules.

## Safe Refactors To Perform Now

- Add a shared internal Markdown helper for table escaping and simple table
  rendering.
- Add shared path containment/relative helpers to `paper_workbench.paths`.
- Add a small `make_validation_finding` factory to `paper_workbench.schema`.
- Migrate only low-risk call sites:
  - core reporting finding tables;
  - workspace integrity report finding tables and path containment;
  - workspace health diagnostic finding wrapper.
- Add behavior-preservation tests for the shared helpers and migrated reports.

## Risky Refactors To Defer

- Splitting `cli.py` into command modules. This is desirable but high-risk
  because command contracts and safety checks are broad.
- Moving every report renderer to a generic table builder. Many golden reports
  depend on exact formatting and should migrate incrementally.
- Unifying every finding-like dataclass. Domain-specific findings in sync,
  rules, workflow, graph, dashboard, drafts, manuscript, and review packets
  carry different fields.
- Replacing project path resolution or profile loading wholesale.
- Deleting historical reports or collapsing duplicate docs without a dedicated
  docs cleanup release.

## Modules To Leave Alone In This Pass

- `registry.py`, `bibtex.py`, and `notes.py`: parser behavior is sensitive and
  covered by adversarial fixtures.
- `sync.py`, `backups.py`, and `migration.py`: write-path safety matters more
  than cleanup during this stabilization pass.
- `workflow.py` and `review_packets.py`: newer features need more usage before
  internal APIs are worth freezing.
- `rules.py`: declarative rule behavior should remain stable while v3 surfaces
  are classified.

## Behavioral Contracts To Preserve

- Stable CLI command names, flags, exit behavior, and output paths.
- `--project` path resolution and refusal of conflicting path overrides.
- No silent overwrites without explicit force behavior.
- Local-first safety boundary: no cloud, LLM, scraping, copied PDFs, or
  fabricated evidence.
- Existing Markdown report content unless a test explicitly documents a change.
- Data-safety ignore behavior for `.paperwb`, cache DBs, backups, audit logs,
  PDFs, and build artifacts.

## Tests Needed Before Refactor

- Shared Markdown escaping and table rendering.
- Finding-table rendering through an existing report.
- Integrity report rendering after shared helper migration.
- Path display and path containment behavior.
- Representative CLI smoke tests after refactors.

## v2.6 Decision

Proceed only with the safe helper consolidation above. Defer the large CLI split
and broad report migration to a future v3.x architecture plan.

