# v2.4 Recommended Patch Plan

## Goal

Harden the workflow runner after real local use without expanding it into a general automation engine.

## Recommended Scope

- Add workflow run history summaries from generated Markdown reports.
- Add stable-only recipe presets for conservative external users.
- Add clearer recipe examples for dogfooding, manuscript QA, and weekly review.
- Add stricter schema documentation for workflow JSON.
- Add regression tests for common project-local recipe mistakes.

## Out Of Scope

- Arbitrary shell execution.
- Python plugin execution from recipe files.
- Cloud, LLM, or scraping integrations.
- Automatic data rewrites without explicit user action.

## Release Criteria

- Full test suite passes.
- Workflow dry-run behavior remains non-destructive.
- Recipe validation rejects unsafe fields.
- Documentation stays aligned with actual CLI behavior.
