# Module Boundaries

This guide records where new code should usually live. It is intentionally
conservative: many v1/v2 modules are large, but broad moves should wait for a
dedicated migration pass.

## Core Modules

| Module | Owns | Should not own |
| --- | --- | --- |
| `schema.py` | Dataclasses, enums, small factories | CLI dispatch, file writes |
| `paths.py` | Workspace path resolution/display/containment | Project profile parsing |
| `markdown.py` | Generic Markdown table escaping/rendering | Domain-specific report content |
| `io.py` | Small text/CSV/JSON reads and writes | Safety policy |
| `registry.py` | Registry CSV parsing and validation | Import mapping, report orchestration |
| `bibtex.py` | Local BibTeX parsing and validation | Remote metadata lookup |
| `notes.py` | Structured note parsing/templates | Claim lifecycle sidecars |
| `claims.py` | Claim collection and claim CSV export | Manuscript QA or truth evaluation |

## Workflow Modules

| Module | Owns | Boundary |
| --- | --- | --- |
| `reporting.py` | Core reports over registry, BibTeX, notes, claims, themes | Keep generic Markdown helpers in `markdown.py`. |
| `authoring.py` | Planning aids: evidence matrices, claim/citation banks, writing packets | Must not write final prose. |
| `drafts.py` / `manuscript.py` | Heuristic citation parsing and QA | Must not fabricate citations or claims. |
| `reading.py` | Reading queue/session/follow-up workflows | Must not mark papers read without explicit command. |
| `sync.py` | Dry-run sync plans and safe apply | Must not silently overwrite user data. |
| `rules.py` | Declarative rule loading and execution | Must not execute arbitrary user code. |
| `workflow.py` | Declarative workflow recipes | Must not execute arbitrary shell commands. |
| `review_packets.py` | Local review-packet export/import sidecars | Must not treat comments as truth or rewrite claims. |
| `rebuild.py` | Content fingerprints and rebuild metadata | Must not run heavy rebuilds unless explicitly commanded. |

## CLI Boundary

`cli.py` may coordinate modules and enforce command-level safety. It should not
gain new domain logic when a feature module can own it. New commands should:

- resolve project paths through the existing project/path helpers;
- preflight writes before generating multiple outputs;
- use explicit `--force` or dry-run behavior for risky actions;
- print clear output paths for generated files;
- add CLI smoke tests for both success and common failure paths.

