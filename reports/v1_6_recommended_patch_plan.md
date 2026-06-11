# v1.6 Recommended Patch Plan

## High Priority

- Add `--severity` and `--category` filters for `paperwb rules run/report`.
- Add CSV and JSON exports for rule findings.
- Add more adversarial rule-config fixtures for malformed JSON and unsupported
  condition shapes.
- Add rule report regression checks that normalize path and ordering details.

## Medium Priority

- Add optional rule packs for common workflows such as literature-review
  readiness, manuscript citation QA, and import hygiene.
- Add docs showing how to maintain project-specific rules across multiple
  project profiles.
- Add richer rule messages for built-in adapters without changing underlying
  validators.

## Low Priority

- Add HTML export for rule reports through the existing Markdown-report path.
- Add convenience commands to scaffold a starter `rules.json`.

## Not Worth Doing Yet

- Do not add arbitrary expression execution.
- Do not add plugin marketplaces or remote rule downloads.
- Do not auto-fix metadata from rule findings.
- Do not expand into a full policy language before real user workflows justify
  the complexity.

