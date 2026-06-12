# Workflows v2

## Stable First Workflow

1. Create a project profile.
2. Add or import verified metadata.
3. Validate registry and BibTeX.
4. Generate structured note templates.
5. Fill notes manually.
6. Extract claims.
7. Generate evidence map and citation audit.
8. Use dashboard and writing packet as planning aids.

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

