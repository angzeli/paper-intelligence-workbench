# Evidence Graph

The evidence graph is a local connectivity layer derived from existing
workspace data: registry rows, BibTeX entries, structured notes, user-entered
claims, themes, tags, reading sessions, and follow-up actions.

It does not read PDFs, scrape publishers, use cloud APIs, use LLM APIs, or
infer scientific truth. It shows what is connected in the local workbench.

## Commands

```bash
paperwb graph build --project zis_photocatalysis
paperwb graph summary --project zis_photocatalysis --out scratch/evidence_graph_summary.md --force
paperwb graph export --project zis_photocatalysis --format json --out scratch/evidence_graph.json --force
paperwb graph export --project zis_photocatalysis --format dot --out scratch/evidence_graph.dot --force
```

## Node Types

- `paper`
- `author`
- `bibtex_entry`
- `note`
- `claim`
- `evidence_location`
- `theme`
- `tag`
- `reading_session`
- `followup`

Draft and citation node types are reserved for future integration with
manuscript QA exports.

## Edge Types

- `authored_by`
- `has_bibtex`
- `has_note`
- `contains_claim`
- `supports_theme`
- `tagged_with`
- `has_evidence_location`
- `derived_from_note`
- `has_followup`
- `read_in_session`

## Interpretation Boundary

Graph centrality is a degree count over local nodes and edges. It is not a
paper-quality score, citation-impact score, truth score, or recommendation from
an external model.

