# Workflows v2

## Stable First Workflow

1. Create a project profile.
2. Add or import verified metadata.
3. Validate registry and BibTeX.
4. Generate structured note templates.
5. Fill notes manually.
6. Extract claims.
7. Generate evidence map and citation audit.
8. Use dashboard, evidence graph summary, and writing packet as planning aids.

For a first real photocatalysis FYP project, start with the dogfood workflow:

```bash
paperwb dogfood create photocatalysis --project fyp_zis_lit_review
paperwb dogfood status --project fyp_zis_lit_review
paperwb dogfood checklist --project fyp_zis_lit_review
```

The dogfood scaffold is intentionally empty. It adds onboarding files, a
first-week plan, evidence-tracking checklists, and an expanded photocatalysis
theme pack. It does not add papers, PDFs, claims, or BibTeX entries.

## Metadata-backed Intake Plan

If you have a private references folder and BibTeX file, generate a local
planning report before adding anything to the project:

```bash
paperwb dogfood plan-from-files photocatalysis --project fyp_zis_lit_review --references-dir <references_dir> --bibtex <ref.bib> --out scratch/fyp_15_paper_plan.md --force
```

The report compares PDF filename slugs with BibTeX keys, excludes obvious
supplement files, and proposes a 15-paper starter shortlist from direct matches.
It does not read PDF text, copy files, or write registry rows.

## Draft Audit Workflow

Draft and manuscript QA are audit-only. Use them after you have local notes and
claims. They flag unknown citations, weak support, and overconfident wording;
they do not rewrite prose.

## Safety Workflow

Before imports, sync applies, migration, or restore:

```bash
paperwb doctor --project PROJECT
paperwb backup create --project PROJECT
paperwb sync plan ...
paperwb migrate plan ...
paperwb backup restore BACKUP_ID --project PROJECT --dry-run
```

## Experimental Workflow Rule

For experimental commands, prefer dry-run, write outputs under `scratch/`, and
review generated Markdown before applying changes.

## Evidence Graph Workflow

Use the graph workflow after registry rows, themes, and notes exist:

```bash
paperwb graph build --project PROJECT
paperwb graph summary --project PROJECT --out scratch/evidence_graph_summary.md --force
paperwb graph export --project PROJECT --format json --out scratch/evidence_graph.json --force
```

The graph is derived from local metadata and user-entered notes. It helps find
orphan papers, isolated themes, claims without evidence locations, and highly
connected papers. It is not a truth or citation-impact score.
