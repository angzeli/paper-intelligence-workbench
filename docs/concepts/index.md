# Core Concepts

This page defines the terms used across the docs and CLI.

## Workspace

A workspace is a local folder containing the repository, project profiles,
synthetic examples, docs, reports, tests, and ignored local state such as
`.paperwb/` caches.

## Project Profile

A project profile lives under `projects/<project>/`. It keeps one
literature-review project together:

```text
projects/<project>/
├── registry.csv
├── bibtex/library.bib
├── notes/
├── themes.json
├── rules.json
├── reports/
├── drafts/
└── reading_sessions/
```

Use `--project <project>` for the recommended v3 workflow.

## Registry

The registry is a CSV file of user-provided paper metadata. Stable fields are
documented in [Schema Reference v3](../SCHEMA_REFERENCE_V3.md). Extra user
columns should be preserved by compatibility and migration workflows.

## BibTeX Library

The BibTeX library links citation keys to registry rows. Validation checks
missing keys, duplicate keys, DOI/title mismatches, and unknown registry links.

## Structured Notes

Notes are Markdown files written by the user. They are the source of extracted
claims. The tool does not infer claims from PDFs, abstracts, titles, or draft
paragraphs.

## Claims

Claims are user-entered statements extracted from structured notes. A useful
claim should include evidence type, evidence location, confidence or strength,
tags, themes, and user comments when relevant.

## Themes

Themes group evidence for literature-review structure. Evidence maps,
dashboards, rules, and writing packets use themes to show coverage and gaps.

## Reports

Reports are generated Markdown artifacts. They are meant for human review and
planning, not as stable machine APIs.

## Stable And Experimental Surfaces

Use [Stable Surface v3](../STABLE_SURFACE_V3.md) for commands and schemas that
should remain predictable. Use [Experimental Features v3](../EXPERIMENTAL_FEATURES_V3.md)
for useful workflows whose output formats may still change.

## Safety Boundary

All workflows are local-first. The tool must not use cloud APIs, LLM APIs,
publisher scraping, copied paper full text, or fabricated scientific content.
