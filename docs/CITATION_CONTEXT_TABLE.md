# Citation Context Table

`paperwb manuscript context-table` lists each citation occurrence in a manuscript draft.

For each occurrence, it reports:

- section
- paragraph ID
- citation key
- linked paper title and year
- best local claim match
- evidence type
- claim strength and confidence
- section/page evidence location when tracked
- warnings from the manuscript QA audit

Example:

```bash
paperwb manuscript context-table drafts/synthetic_good_section.md \
  --project zis_photocatalysis \
  --out reports/citation_context_table_v1_4.md \
  --force
```

Use the table to verify whether each citation is being used in a way that matches your own notes.
