# Release Readiness v1.4

Paper Intelligence Workbench v1.4 adds manuscript citation QA for local Markdown and LaTeX-ish literature-review drafts. The release remains local-first and does not use cloud APIs, LLM APIs, publisher scraping, or copyrighted examples.

## Features Added

- Manuscript parsing through `paperwb manuscript parse`.
- Citation-key extraction for Pandoc-style citations, plain `@key` citations, and common LaTeX-style commands including `\cite`, `\citep`, `\citet`, `\citealp`, `\autocite`, and `\parencite`.
- Reviewer-style manuscript QA through `paperwb manuscript qa`.
- Citation context tables through `paperwb manuscript context-table`.
- Claim-to-draft traceability through `paperwb manuscript trace-claims`.
- Manuscript revision checklists through `paperwb manuscript checklist`.
- Paragraph-level manuscript evidence tables through `paperwb manuscript evidence-matrix`.
- Synthetic manuscript drafts covering good support, overconfident wording, unknown citations, review-only support, and claim mismatch cases.

## Commands Checked

- `paperwb manuscript qa drafts/synthetic_overconfident_section.md --project zis_photocatalysis --out reports/manuscript_qa_v1_4.md --force`
- `paperwb manuscript context-table drafts/synthetic_overconfident_section.md --project zis_photocatalysis --out reports/citation_context_table_v1_4.md --force`
- `paperwb manuscript trace-claims drafts/synthetic_overconfident_section.md --project zis_photocatalysis --theme photocorrosion --out reports/claim_traceability_v1_4.md --force`
- `paperwb manuscript checklist drafts/synthetic_overconfident_section.md --project zis_photocatalysis --out reports/manuscript_revision_checklist_v1_4.md --force`

## Reports Generated

- `reports/manuscript_qa_v1_4.md`
- `reports/citation_context_table_v1_4.md`
- `reports/claim_traceability_v1_4.md`
- `reports/manuscript_revision_checklist_v1_4.md`

## Tests And Validation

- `python -m pytest -q` passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"` returned `1.4.0`.
- `paperwb --help` passed.
- `paperwb manuscript --help` passed.
- `paperwb manuscript parse`, `citations`, `qa`, `checklist`, `context-table`, `trace-claims`, and `evidence-matrix` were exercised on synthetic drafts.
- `python scripts/check_notebooks.py` passed structural notebook validation.
- `python scripts/data_safety_audit.py --out scratch/data_safety_v1_4_smoke.md --strict` completed with zero errors and existing historical absolute-path warnings only.

## Writing Boundary Assessment

The manuscript workflow audits and annotates drafts only. It does not rewrite final prose, invent citations, fabricate claims, fabricate quotes, or judge scientific truth. Paragraph-to-claim matching is lexical and heuristic, so all findings require manual review.

## False-positive Risks

- Paragraphs may be flagged when they use strong wording in a cautious or quoted context.
- Keyword overlap may match a paragraph to a claim that is topically similar but not the intended support.
- Review-only support warnings may be noisy for paragraphs that are explicitly background context.

## False-negative Risks

- Unsupported claims may be missed when they do not use strong wording or project theme terms.
- Citations embedded in uncommon LaTeX macros, tables, captions, or footnotes may not be detected.
- Valid evidence may be missed if local notes lack tags, claims, or evidence locations.

## Known Limitations

- The parser is not a full Markdown or LaTeX compiler.
- Matching uses local citation keys, tags, themes, and normalized keyword overlap only.
- The workflow depends on structured notes and extracted claims; sparse notes produce sparse QA.
- Manuscript reports are planning aids, not submission-readiness certification.

## Readiness Verdict

Usable as a conservative manuscript QA aid for synthetic and small real local projects. It is ready for external testing with the documented limitations.
