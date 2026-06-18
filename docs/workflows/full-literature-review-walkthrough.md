# Full Literature Review Walkthrough

This walkthrough uses synthetic or empty project data only. It demonstrates the
shape of a real workflow without adding real paper metadata, PDFs, copied full
text, or fabricated claims.

## 1. Confirm The CLI Works

```bash
python -c "import paper_workbench; print(paper_workbench.__version__)"
paperwb --help
```

Expected output: a version string and the top-level command list.

## 2. Create An Empty Project

```bash
paperwb template create generic --project tutorial_review
paperwb project validate tutorial_review
paperwb dashboard --project tutorial_review --no-audit-log
```

Expected output: an empty project profile with clear "no papers yet" style
status. If the project already exists, choose a new project name. Template
creation is non-destructive.

## 3. Add A Synthetic Paper Manually

Use `add-paper` for one explicit row:

```bash
paperwb add-paper tutorial_synthetic_001 \
  --project tutorial_review \
  --title "Synthetic Tutorial Paper" \
  --year 2026 \
  --bibtex-key TutorialSynthetic2026 \
  --reading-status unread
```

Expected output: one new registry row. Do not use this command to invent real
metadata; for real projects, copy metadata from a source you trust.

## 4. Validate Metadata

```bash
paperwb validate-registry projects/tutorial_review/registry.csv --strict
paperwb validate-bib projects/tutorial_review/bibtex/library.bib --registry projects/tutorial_review/registry.csv --strict
```

Expected output: registry validation should pass. BibTeX validation may warn if
the new synthetic key is not yet present in `library.bib`.

## 5. Generate A Structured Note Template

```bash
paperwb note-template tutorial_synthetic_001 --project tutorial_review
```

Expected output: a Markdown note template under the project notes folder. Write
notes and claims manually after reading. The tool does not read papers or infer
claims.

## 6. Extract Claims

```bash
paperwb claims --project tutorial_review --output scratch/tutorial_claims.csv --force
```

Expected output: a claims CSV. It may be empty until you add structured claims
to the note.

## 7. Generate Core Reports

```bash
paperwb report inventory --project tutorial_review --out scratch/tutorial_inventory.md --force
paperwb report evidence-map --project tutorial_review --out scratch/tutorial_evidence_map.md --force
paperwb report citation-audit --project tutorial_review --out scratch/tutorial_citation_audit.md --force
paperwb dashboard --project tutorial_review --out scratch/tutorial_dashboard.md --force --no-audit-log
```

Expected output: Markdown reports in `scratch/`. Empty or weak-evidence reports
are normal early in a project.

## 8. Audit A Synthetic Draft

```bash
paperwb manuscript qa drafts/synthetic_good_section.md --project clean_demo --out scratch/tutorial_manuscript_qa.md --force
```

Expected output: a reviewer-style QA report. The matching is heuristic and local
only. It does not rewrite prose or judge scientific truth.

## 9. Back Up Before Risky Work

```bash
paperwb integrity check --project tutorial_review --out scratch/tutorial_integrity.md --force
paperwb backup create --project tutorial_review --notes "Tutorial checkpoint"
```

Expected output: an integrity report and a local backup. Do not include PDFs in
backup bundles unless a future command explicitly documents that behavior.

## 10. Use The Dashboard

```bash
paperwb dashboard --project tutorial_review --no-audit-log
```

Expected output: project counts, missing notes, weak evidence, next actions, and
reading queue hints. The dashboard is read-only unless `--out` writes a report.

## Next Steps

- Use [Adding Real Papers Safely](../ADDING_REAL_PAPERS_SAFELY.md) before
  moving from synthetic metadata to real project metadata.
- Use [Cookbook](../cookbook/index.md) for targeted tasks.
- Use [Safety](../safety/index.md) before import, sync, backup, restore, or
  migration workflows.
