# Scale Limits

v2.5 targets local literature-review projects with hundreds of papers and
hundreds or thousands of user-entered claims.

## Practical Expectations

- Registry and BibTeX validation should remain fast for hundreds of records.
- Note parsing and claim extraction are plain file scans and scale with note
  count and note length.
- Evidence maps and dashboards are generated Markdown reports and can become
  large on broad projects.
- The optional SQLite index is useful when repeated substring searches become
  slow.
- Incremental rebuild metadata helps decide what to refresh, but does not avoid
  all work automatically.

## Deliberate Non-goals

- No background daemon.
- No cloud cache.
- No heavy graph database.
- No LLM embeddings.
- No automatic paper reading, summarization, or claim generation.

## Recommended Large-project Workflow

```bash
paperwb rebuild plan --project PROJECT
paperwb index status --project PROJECT --check-files
paperwb workflow run weekly_review --project PROJECT --dry-run
python scripts/performance_sanity.py --papers 500 --claims 1500 --themes 50 --out scratch/performance_sanity.md --force
```

Keep large generated stress projects in ignored scratch folders or another
temporary directory outside committed repo content.
