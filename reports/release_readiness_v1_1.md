# Release Readiness v1.1

Date: 2026-06-11

## Release Verdict

Paper Intelligence Workbench v1.1 implements the draft citation auditor and
manuscript evidence checker as a local-only, heuristic audit workflow. The
feature is usable on synthetic Markdown drafts and project-profile evidence.

This is not a final prose writer. It does not fabricate citations, claims,
quotes, or evidence.

## Implemented Features

- Added `paper_workbench.drafts` with Markdown draft parsing, citation
  extraction, citation coverage checks, paragraph-level evidence matching, and
  revision checklist generation.
- Added support for citation forms including `@key`, `[@key]`,
  `[@key; @other]`, `\cite{key}`, `\citep{key,other}`, and `\citet{key}`.
- Added local heuristic paragraph-to-claim matching using citation-key,
  keyword, tag, and theme overlap.
- Added strong-wording warnings for terms such as `proves`, `confirms`,
  `demonstrates`, `clearly shows`, `definitively`, `always`, `never`,
  `exclusively`, and `significantly improves`.
- Added detection for unknown citation keys, cited papers missing notes, cited
  papers without claims, unread or skimmed cited papers, weak-only cited
  evidence, paragraphs without citations, citations without evidence matches,
  and review-statement-only support.
- Added `paperwb draft parse`, `paperwb draft citations`, `paperwb draft
  audit`, `paperwb draft checklist`, and `paperwb draft evidence-matrix`.
- Added three synthetic Markdown draft fixtures under `drafts/`.
- Added `examples/draft_citation_audit_workflow.py`.
- Fixed the inherited `paperwb audit-log clear` no-force path so it returns a
  clean user-facing error instead of a traceback.

## CLI Commands Checked

- `python -m paper_workbench.cli --help`
- `python -m paper_workbench.cli draft --help`
- `python -m paper_workbench.cli draft parse drafts/synthetic_photocorrosion_section.md`
- `python -m paper_workbench.cli draft audit drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis`
- `python -m paper_workbench.cli draft checklist drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis`
- `python -m paper_workbench.cli draft evidence-matrix drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis`
- `python -m paper_workbench.cli draft citations drafts/synthetic_weakly_cited_section.md` with explicit legacy example paths
- `python -m paper_workbench.cli audit-log clear`

## Tests Run

- `python -m pytest -q`: passed.
- Targeted draft and command-contract tests passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: passed, `1.1.0`.
- `python scripts/validate_notebooks.py`: passed, 8 notebooks validated.
- `python examples/draft_citation_audit_workflow.py`: passed and wrote ignored scratch outputs.

## Generated Reports

- `reports/draft_audit_v1_1.md`
- `reports/citation_coverage_v1_1.md`
- `reports/paragraph_evidence_matrix_v1_1.md`
- `reports/revision_checklist_v1_1.md`
- `reports/release_readiness_v1_1.md`
- `reports/v1_2_recommended_patch_plan.md`

## Writing Boundary Assessment

The v1.1 workflow audits and annotates only. It does not rewrite draft
paragraphs, suggest polished final prose, invent missing citations, infer
claims from papers, or judge scientific truth.

Report language uses terms such as "possible unsupported claim" and
"heuristic evidence audit" to avoid overclaiming semantic certainty.

## False Positive Risks

- Introductory or transitional paragraphs without citations may be flagged.
- Strong-wording heuristics may catch words used in a non-claim context.
- Keyword overlap can match a paragraph to a claim when the citation is only
  loosely related.
- Review-only warnings may be too strict for background paragraphs.

## False Negative Risks

- Unsupported claims written without strong wording or known theme keywords may
  pass without a warning.
- Citation keys in unsupported citation syntaxes may be missed.
- Real semantic mismatch can be missed if a paragraph and claim share many
  keywords.
- Claims split across multiple paragraphs are audited paragraph by paragraph.

## Known Limitations

- The parser is not a full Markdown or citation-processor implementation.
- Matching is lexical and local; it does not use embeddings or LLMs.
- The draft auditor depends on existing registry, BibTeX, notes, claims, and
  themes. Weak upstream evidence tracking produces weak audit quality.
- Paragraphs in tables, footnotes, or complex Markdown constructs are not
  deeply parsed.

## Recommended v1.2 Scope

- Reduce false positives for short connective paragraphs.
- Add more citation-pattern fixtures based on real user Markdown styles.
- Add optional CSV/JSON export for paragraph evidence matrices.
- Add draft-audit report diffing between manuscript revisions.
- Keep the tool local-first and audit-only.
