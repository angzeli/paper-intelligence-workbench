# Documentation Audit v3.4

## Scope

v3.4 audited the public documentation entry points, existing flat docs, v3
stable and experimental surface docs, command reference docs, report docs,
examples, notebooks, generated reports, quality-gate docs, and README.

## Findings

- Existing docs were broad but flat. New users had to choose from many
  overlapping files without a clear reading order.
- The docs already covered most workflows, but cookbook-style recipes were
  missing.
- `docs/STABLE_SURFACE_V3.md` still used v3.2 wording while package metadata
  was moving to v3.4.
- `docs/REPORT_GALLERY_V3.md` still pointed at older v3.1/v3.2 report context.
- Current quality-gate docs were functionally correct after the v3.3 blocker
  fix, but some wording was v3.3-specific.

## Changes Made

- Added a site-source structure under `docs/`:
  - `getting-started/`
  - `concepts/`
  - `workflows/`
  - `command-reference/`
  - `reports/`
  - `safety/`
  - `development/`
  - `cookbook/`
  - `troubleshooting/`
- Rebuilt `docs/index.md` as the main documentation map.
- Added a full synthetic literature-review walkthrough.
- Added a cookbook with recipes for common workflows.
- Replaced the v3 report gallery with current v3.4 guidance.
- Added `scripts/check_docs.py` for Markdown link, path-hygiene, and CLI
  command-example checks.
- Did not add MkDocs or any other site-generator dependency; the docs remain
  plain Markdown source.

## Safety Assessment

- No new cloud, LLM, scraping, PDF, or copied full-text behavior was added.
- New examples use synthetic or existing local demo paths.
- New docs repeat that the tool does not fabricate metadata, claims, citations,
  quotes, summaries, or final prose.
- Documentation checks reject raw absolute-path patterns in README and docs.

## Validation

- `python scripts/check_docs.py`: passed.
- `paperwb --help`: passed during command-reference audit.
- Full test-suite validation is recorded in
  `reports/release_readiness_v3_4.md`.
