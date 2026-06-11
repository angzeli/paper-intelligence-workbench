# v1.5 Recommended Patch Plan

## High Priority

- Add more manuscript parser fixtures for footnotes, captions, block quotes, bibliography sections, and uncommon citation macros.
- Add a focused hostile review of manuscript QA reports after real draft trials.
- Improve paragraph classification so background paragraphs without citations are separated from possible claim paragraphs.
- Add regression snapshots for manuscript QA, citation context, and claim traceability report structure.

## Medium Priority

- Add optional draft section filters so users can audit one manuscript subsection at a time.
- Add clearer CLI guidance when a manuscript has citations but no project BibTeX or registry linkage.
- Add theme-specific manuscript QA summaries for literature-review subsections.
- Add report diff tooling for repeated manuscript QA runs.

## Low Priority

- Add optional CSV export for citation context tables.
- Add optional JSON export for manuscript QA findings.
- Add a compact terminal summary mode for manuscript QA.

## Explicitly Not Worth Doing Yet

- Do not add LLM-based draft rewriting.
- Do not add publisher or DOI metadata lookup.
- Do not attempt full LaTeX compilation or CSL formatting.
- Do not automatically edit user manuscripts.

## Overengineering Risks

- Semantic matching, ranking, or auto-revision logic could imply certainty the local evidence cannot support.
- Full document compiler support would add complexity and fragile dependencies.
- Automated citation insertion could become destructive unless it has a separate dry-run and patch-review workflow.
