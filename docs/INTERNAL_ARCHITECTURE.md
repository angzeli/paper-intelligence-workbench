# Internal Architecture

Paper Intelligence Workbench is a local-first CLI application with a Python
package behind it. The stable user surface is the `paperwb` CLI and the
documented local file formats. Most package modules are internal implementation
building blocks for that CLI.

## Layers

| Layer | Modules | Responsibility |
| --- | --- | --- |
| Data models | `schema.py` | Core dataclasses and controlled vocabularies. |
| Low-level utilities | `io.py`, `paths.py`, `markdown.py`, `errors.py` | File writes, path display, Markdown rendering, and diagnostic text. |
| Parsers and validators | `registry.py`, `bibtex.py`, `notes.py`, `tags.py` | Conservative parsing and local validation. |
| Core evidence workflows | `claims.py`, `audit.py`, `reporting.py`, `authoring.py` | Claim extraction, citation audit, evidence maps, and writing packets. |
| Project and safety workflows | `projects.py`, `doctor.py`, `integrity.py`, `backups.py`, `migration.py`, `auditlog.py` | Project profiles, checks, backups, migration plans, and local audit events. |
| Experimental workflow modules | `drafts.py`, `manuscript.py`, `reading.py`, `sync.py`, `rules.py`, `graph.py`, `workflow.py`, `review_packets.py`, `rebuild.py` | v1/v2 feature workflows that remain local and conservative. |
| CLI dispatch | `cli.py` | Argument parsing, command dispatch, and command-level safety checks. |

## Design Constraints

- Keep workflows local-first and deterministic.
- Do not execute user-provided Python or shell from config files.
- Keep report generation reproducible from checked-in synthetic data or explicit
  user inputs.
- Prefer shared helpers for path display, Markdown escaping, and finding
  construction.
- Avoid broad rewrites of `cli.py`; move helpers out gradually with tests.

## Current Stabilization Decisions

- `paper_workbench.markdown` owns Markdown table escaping and simple table
  rendering.
- `paper_workbench.paths` owns workspace path display and path containment
  helpers.
- `paper_workbench.schema.make_validation_finding` is the preferred factory for
  new `ValidationFinding` construction.
- Feature modules may keep local report functions, but new table-heavy reports
  should use `markdown_table` or `findings_table`.

