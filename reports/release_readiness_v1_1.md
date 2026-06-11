# Release Readiness v1.1

Date: 2026-06-11

## Release Verdict

Paper Intelligence Workbench v1.1 implements the draft citation auditor and
manuscript evidence checker as a local-only, heuristic audit workflow. The
feature is usable on synthetic Markdown drafts and project-profile evidence.

This is not a final prose writer. It does not fabricate citations, claims,
quotes, or evidence.

The targeted post-review hardening pass on 2026-06-11 addressed the
release-blocking and high-priority issues from `reports/hostile_review_latest.md`:

- `paperwb report all` now preflights every output path before writing any
  report, so a later collision no longer leaves a partial report set.
- `paperwb report all --out ...` now fails with a clear user-facing error
  because `--out` is a single-report destination and `--reports-dir` controls
  multi-report output.
- Active API, CLI, and command-contract docs now describe v1.1 rather than
  v1.0-rc.
- User-facing documentation examples now write tutorial outputs to ignored
  `scratch/` paths rather than checked-in `reports/` paths.
- Local file link/unlink metadata updates now restore prior metadata files if
  a later write fails.
- Draft citation extraction now preserves citation source order across mixed
  Markdown and LaTeX-style citation syntaxes.
- The report index generator now recognizes v1.x report names when grouping
  current release reports.
- Local package build verification succeeded after installing the declared
  development extra; setuptools emitted non-blocking license metadata
  deprecation warnings for future cleanup.

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
- `python -m pytest --collect-only -q`: 167 tests collected.
- Targeted report-all, draft-citation-order, local-file rollback,
  report-index, docs-safety, and command-contract tests passed.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`: passed, `1.1.0`.
- `python scripts/validate_notebooks.py`: passed, 8 notebooks validated.
- `python examples/draft_citation_audit_workflow.py`: passed and wrote ignored scratch outputs.
- `python -m build --sdist --wheel`: passed after installing `.[dev]`.

## Additional CLI Smoke Checks

- `python -m paper_workbench.cli --help`: passed.
- `python -m paper_workbench.cli files --help`: passed.
- `python -m paper_workbench.cli draft citations drafts/synthetic_photocorrosion_section.md --project zis_photocatalysis`: passed.
- `python -m paper_workbench.cli report all ... --reports-dir <tmp>/paperwb_report_all_smoke --force`: passed and wrote a complete temporary report set.
- `python -m paper_workbench.cli report all ... --out <tmp>/paperwb_report_all_single.md --force`: returned exit code 2 with a clear `--out is not supported with report all` message.
- `python -m paper_workbench.cli report all ... --reports-dir <tmp>/paperwb_report_all_collision`: returned exit code 2 before writing partial outputs when a later report path already existed.

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
- Package builds currently pass, but setuptools warns that the TOML license
  table and license classifier should be modernized before the 2027 deprecation
  deadline.

## Recommended v1.2 Scope

- Reduce false positives for short connective paragraphs.
- Add more citation-pattern fixtures based on real user Markdown styles.
- Add optional CSV/JSON export for paragraph evidence matrices.
- Add draft-audit report diffing between manuscript revisions.
- Keep the tool local-first and audit-only.
