# Workflows v2

## Stable First Workflow

1. Create a project profile.
2. Add or import verified metadata.
3. Validate registry and BibTeX.
4. Generate structured note templates.
5. Fill notes manually.
6. Extract claims.
7. Run the claim review queue and manually verify or deprecate claims.
8. Generate evidence map and citation audit.
9. Use dashboard, evidence graph summary, and writing packet as planning aids.

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

## Claim Evidence Review

After notes contain extracted claims, review claim readiness before drafting:

```bash
paperwb claim-review queue --project PROJECT
paperwb claim-review mark PAPER_ID:c1 --project PROJECT --status verified
paperwb contradictions report --project PROJECT --out scratch/contradictions.md --force
```

Lifecycle state is sidecar metadata. It does not verify scientific truth, edit
notes, or change claim CSV exports.

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

## Recipe Runner Workflow

After you understand the individual commands, use the v2.3 workflow runner to
repeat common checks:

```bash
paperwb workflow list
paperwb workflow show daily_check
paperwb workflow run daily_check --project PROJECT --dry-run
paperwb workflow run pre_writing_check --project PROJECT --theme THEME --dry-run
```

Recipes are declarative JSON only. They call built-in local step types and do
not execute shell commands or arbitrary Python code.

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
