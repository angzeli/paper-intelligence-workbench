# Core Workflow v3

The stable v3 workflow is intentionally simple.

## 1. Create Or Select A Project

```bash
paperwb project list
paperwb template create generic --project my_review
```

For a real first run, prefer:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
```

## 2. Validate Metadata

```bash
paperwb validate-registry projects/my_review/registry.csv --strict
paperwb validate-bib projects/my_review/bibtex/library.bib --registry projects/my_review/registry.csv --strict
```

## 3. Create Notes And Claims

```bash
paperwb note-template PAPER_ID --project my_review
paperwb claims projects/my_review/notes --output scratch/claims.csv
```

Claims are extracted from structured notes only. The tool does not invent
claims from PDFs, abstracts, or draft prose.

## 4. Generate Evidence Reports

```bash
paperwb report inventory --project my_review --out scratch/inventory.md --force
paperwb report evidence-map --project my_review --out scratch/evidence_map.md --force
paperwb report citation-audit --project my_review --out scratch/citation_audit.md --force
paperwb dashboard --project my_review --out scratch/dashboard.md --force --no-audit-log
```

## 5. Use Advanced Workflows Carefully

Manuscript QA, sync, review packets, graph exports, workflow recipes, indexed
search, and incremental rebuilds are useful but experimental in v3.0rc. Use
dry-run/report-first workflows and keep source data untouched unless a command
explicitly documents its write.
