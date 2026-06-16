# v3.2 Recommended Patch Plan

## Goal

Dogfood v3.1 support bundles on a real local literature-review project and
tighten any privacy or usability issues found.

## Recommended Work

1. Run `paperwb support redact-preview` and `paperwb support bundle` on one real
   project.
2. Inspect generated CSV samples for accidental sensitive metadata.
3. Add redaction tests for any newly observed private-field patterns.
4. Improve support-bundle reproduction guidance if users need clearer issue
   reports.
5. Keep the bundle local-first and generated-summary-only.

## Not In Scope

- Cloud diagnostics.
- LLM-based log analysis.
- PDF copying.
- Full-note or full-draft sharing.
- Automatic repair of project data.
