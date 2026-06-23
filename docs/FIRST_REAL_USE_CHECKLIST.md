# First Real-use Checklist

Use this checklist when starting the FYP ZnIn2S4 photocatalysis mini literature
review with real papers. Keep real data outside the repository.

## Setup

- [ ] Create an external workspace with `paperwb dogfood create photocatalysis --root <external_workspace> --project fyp_zis_lit_review`.
- [ ] Register it with `paperwb external add fyp_zis_real <external_workspace> --project fyp_zis_lit_review`.
- [ ] Run `paperwb external validate fyp_zis_real --strict`.
- [ ] Confirm `.paperwb-local/workspaces.json` is ignored and not staged.

## First 10-15 Papers

- [ ] Choose papers manually from supervisor-approved or personally verified sources.
- [ ] Add one registry row at a time.
- [ ] Add a matching BibTeX entry for each row.
- [ ] Validate registry and BibTeX after each small batch.
- [ ] Do not mark a paper as read until it has actually been read.

## Reading and Claims

- [ ] Generate a note template for each paper before reading.
- [ ] Fill structured notes manually.
- [ ] Write only claims supported by your own notes.
- [ ] Include page, section, figure, or table evidence locations when available.
- [ ] Run claim extraction and review weak or missing evidence locations.

## First Writing Pass

- [ ] Generate an evidence map.
- [ ] Generate a citation audit.
- [ ] Generate a writing packet or section outline.
- [ ] Draft one 600-1000 word subsection yourself.
- [ ] Run draft or manuscript QA as an audit only.
- [ ] Review weak claims, unknown citations, and missing primary evidence warnings.

## Safety

- [ ] Back up before large imports, sync applies, restores, or migrations.
- [ ] Generate a support bundle only if needed.
- [ ] Inspect support bundles before sharing.
- [ ] Never commit PDFs, full paper text, private notes, private drafts, or private external paths.
