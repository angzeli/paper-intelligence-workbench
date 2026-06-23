# FYP ZnIn2S4 Dogfooding Simulation

Date: 2026-06-23

This report records a synthetic local dogfooding run for the FYP-style ZnIn2S4
photocatalysis workflow. It does not contain real paper metadata, private file
paths, PDFs, copied paper text, real claims, or real citation shortlists.

## Verdict

Ready for private dogfooding with an external workspace.

The scaffold, validation, note, claim extraction, evidence reports, dashboard,
manuscript QA, external workspace adapter, support bundle, and backup smoke path
all ran successfully on a placeholder project. The next real-use step is to add
10-15 verified papers manually in a private external workspace and repeat the
same commands with real user-entered notes.

## Simulated Workspace

- Workspace root: `<synthetic_temp_workspace>`
- Project: `fyp_zis_lit_review`
- Template: `photocatalysis`
- Data: one synthetic placeholder paper, one synthetic BibTeX entry, one
  synthetic structured note, one synthetic extracted claim, one synthetic draft
  paragraph.

## Commands Exercised

- `paperwb dogfood create photocatalysis --project fyp_zis_lit_review --root <synthetic_temp_workspace>`
- `paperwb dogfood status --project fyp_zis_lit_review --root <synthetic_temp_workspace>`
- `paperwb dogfood checklist --project fyp_zis_lit_review --root <synthetic_temp_workspace>`
- `paperwb validate-registry <synthetic_registry> --strict`
- `paperwb validate-bib <synthetic_bibtex> --registry <synthetic_registry> --strict`
- `paperwb add-paper --registry <synthetic_registry> ...`
- `paperwb note-template synthetic_zis_placeholder_1 --registry <synthetic_registry> --notes-dir <synthetic_notes>`
- `paperwb claims <synthetic_notes> --output <synthetic_reports>/claims.csv --force`
- `paperwb report evidence-map ... --out <synthetic_reports>/evidence_map.md --force`
- `paperwb report citation-audit ... --out <synthetic_reports>/citation_audit.md --force`
- `paperwb report section-outline ... --theme znin2s4-photocatalysis --force`
- `paperwb writing-packet ... --theme znin2s4-photocatalysis --force`
- `paperwb manuscript qa <synthetic_draft> ... --force`
- `paperwb dashboard ... --no-audit-log --force`
- `paperwb integrity check --project fyp_zis_lit_review --force`
- `paperwb graph summary ... --force`
- `paperwb external add fyp_sim <synthetic_temp_workspace> --project fyp_zis_lit_review`
- `paperwb external validate fyp_sim`
- `paperwb external run fyp_sim validate-registry`
- `paperwb external run fyp_sim validate-bib`
- `paperwb external run fyp_sim dashboard`
- `paperwb external run fyp_sim support-bundle`
- `paperwb backup create --project fyp_zis_lit_review`

## Results

- Empty dogfood scaffold created without overwriting an existing project.
- Empty registry and empty BibTeX validated cleanly.
- Placeholder paper was added only to the temporary synthetic workspace.
- Placeholder BibTeX validated cleanly against the placeholder registry.
- Structured note template was generated and filled with synthetic-only content.
- Claim extraction produced one synthetic claim.
- Evidence map, citation audit, section outline, writing packet, dashboard,
  manuscript QA, and graph summary reports were generated.
- Project-mode integrity check reported zero errors. Warnings were expected for
  a one-paper placeholder project with many intentionally empty themes.
- External workspace registration redacted paths by default and did not copy
  data into the repository.
- Safe support bundle generation produced diagnostic files without PDFs, cache
  databases, backup archives, or full source notes.

## Expected Warnings

- Most FYP themes remain under-supported because the simulation uses one
  placeholder paper.
- The synthetic evidence type is not a real scientific evidence type.
- Manuscript QA is heuristic and only demonstrates citation and support checks.

## First Real-use Loop

1. Keep the real FYP workspace outside the repository.
2. Register it through `paperwb external add`.
3. Add 10-15 verified papers manually or through reviewed local imports.
4. Validate registry and BibTeX after every batch.
5. Generate note templates only for papers being read.
6. Read papers manually and write structured notes yourself.
7. Extract claims from user-entered notes.
8. Generate evidence maps, citation audits, dashboard, and writing packets.
9. Draft one 600-1000 word subsection yourself.
10. Run manuscript QA as a conservative audit.
11. Back up the external workspace before major edits.
12. Generate a sanitized support bundle only when debugging is needed.

## Boundary

This simulation confirms workflow readiness only. It does not validate any real
photocatalysis claim and does not create a literature review.
