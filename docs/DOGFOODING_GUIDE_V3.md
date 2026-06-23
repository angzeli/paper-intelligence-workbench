# Dogfooding Guide v3

The dogfooding workflow is the recommended bridge from synthetic examples to a
real local literature-review project.

## Create An Empty Project

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

The scaffold contains empty registry, BibTeX, notes, reports, drafts, and
reading-session folders plus onboarding checklists. It contains no real papers.

## Plan From Local Files Without Importing

```bash
paperwb dogfood plan-from-files photocatalysis \
  --project fyp_zis_lit_review \
  --references-dir <references_dir> \
  --bibtex <ref.bib> \
  --limit 15 \
  --out scratch/fyp_15_paper_plan.md \
  --force
```

The plan reports counts, supplement-like files, BibTeX keys, filename/key
matches, unmatched files, unmatched keys, and a starter shortlist if enough
exact matches exist. It does not copy PDFs, read PDF text, or write registry
rows.

## First Week Target

- Add 10-15 verified papers manually.
- Generate note templates.
- Read and write structured notes.
- Extract claims.
- Generate an evidence map and citation audit.
- Use dashboard and checklist reports to decide what to read next.

## Private External Workspace Mode

For real dogfooding, keep the workspace outside this repository and register a
local pointer:

```bash
paperwb external add fyp_zis_real <external_workspace> --project fyp_zis_lit_review
paperwb external validate fyp_zis_real --strict
paperwb external run fyp_zis_real dashboard
paperwb external run fyp_zis_real support-bundle
```

The pointer file lives in ignored `.paperwb-local/workspaces.json`. Do not
commit it, and do not copy private PDFs, notes, drafts, or BibTeX files into
the repo. See [PRIVATE_DOGFOODING.md](PRIVATE_DOGFOODING.md).
