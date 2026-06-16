# v3.3 Recommended Patch Plan

## Recommended Scope

Focus v3.3 on real dogfood feedback and friction reduction, not another broad
subsystem.

## Candidate Work

- Run compatibility inspection on a private real dogfood workspace and record
  sanitized findings only.
- Tighten review-packet empty-selection behavior if it remains confusing during
  real use.
- Refresh v3 docs that still have release-candidate phrasing after more
  dogfooding.
- Add a README transcript smoke test if public quickstart drift recurs.
- Consider small CLI extraction only where command-contract tests already pin
  behavior.

## Explicitly Not Recommended

- Do not add cloud sync, LLM summarization, scraping, or automatic PDF text
  extraction.
- Do not expand migration apply behavior beyond copy-based workflows without
  new safety tests.
- Do not mark experimental sidecars stable until they survive real projects.

