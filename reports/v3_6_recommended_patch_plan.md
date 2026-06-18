# v3.6 Recommended Patch Plan

## Recommended Scope

Keep v3.6 focused on operational polish from real dogfooding feedback.

## Priorities

1. Add transcript tests for the most important cookbook recipes.
2. Add a clearer contract for empty review-packet generation.
3. Improve external-workspace UX if real project paths reveal friction.
4. Continue splitting CLI helper logic only where behavior is already pinned by
   command-contract tests.
5. Keep graph, workflow, review-packet import, indexed search, sync apply, and
   forced restore/migration features experimental until real use confirms their
   contracts.

## Not Recommended

- Do not add cloud sync.
- Do not add LLM summarization.
- Do not add publisher scraping.
- Do not broaden external mode into arbitrary shell command execution.

