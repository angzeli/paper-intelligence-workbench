# Evidence Review Workflow

Use v2.2 evidence review when a project has extracted claims but the user is not
yet confident which claims are safe to cite or write around.

Recommended loop:

1. Extract claims from structured notes.
2. Run `paperwb claim-review queue`.
3. Add missing page or section evidence locations in the note.
4. Reread papers flagged as skimmed, low-confidence, review-only, or weak.
5. Mark claims `verified` or `ready_for_draft_use` only after manual checking.
6. Mark outdated claims `deprecated` with a reason.
7. Use `paperwb contradictions` for claims that need side-by-side review.
8. Regenerate writing packets, manuscript QA, dashboard, and graph summaries.

The workflow protects the boundary between local completeness checking and
scientific judgment. It never fabricates counterclaims or verifies claims
automatically.
