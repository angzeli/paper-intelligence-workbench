# Adding Real Papers Manually

Manual entry is the safest first workflow for a real FYP literature review. The
workbench can validate metadata and citations, but it cannot verify scientific
truth or invent missing fields.

## Add Metadata

Edit the external workspace registry:

```text
<external_workspace>/projects/fyp_zis_lit_review/registry.csv
```

For each paper, fill only fields you have verified:

- `paper_id`
- `title`
- `authors`
- `year`
- `journal`
- `doi`
- `bibtex_key`
- `tags`
- `reading_status`
- `notes_path`
- `included_in_lit_review`
- `user_comment`

Leave uncertain fields blank instead of guessing.

## Add BibTeX

Add the matching entry to:

```text
<external_workspace>/projects/fyp_zis_lit_review/bibtex/library.bib
```

Then run:

```bash
paperwb external run fyp_zis_real validate-registry --strict
paperwb external run fyp_zis_real validate-bib --strict
```

## Generate Notes

After metadata and BibTeX pass validation, generate a note template:

```bash
paperwb note-template PAPER_ID --project fyp_zis_lit_review --output <external_workspace>/projects/fyp_zis_lit_review/notes/PAPER_ID.md
```

Read the paper manually and fill the note yourself. Do not paste copyrighted
full text. Short evidence locations and your own paraphrased notes are enough.

## Extract Claims

```bash
paperwb external run fyp_zis_real claims --out <external_workspace>/projects/fyp_zis_lit_review/reports/claims.csv --force
```

Review extracted claims before using them in a draft. The extractor parses your
structured notes; it does not infer claims from papers.
