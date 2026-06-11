# Revision Checklists

`paperwb draft checklist` turns a draft audit into manual revision tasks.

Example:

```bash
paperwb draft checklist drafts/synthetic_photocorrosion_section.md \
  --project zis_photocatalysis \
  --out scratch/revision_checklist.md \
  --force
```

Checklist items may include:

- verify unknown citation keys;
- add notes for cited papers;
- add claim/evidence blocks to notes;
- add page, section, figure, or table locations;
- soften strong wording;
- replace review-only support with primary evidence where appropriate.

The checklist never rewrites prose. It names gaps for the user to resolve.
