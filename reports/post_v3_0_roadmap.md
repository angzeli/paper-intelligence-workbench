# Post v3.0 Roadmap

## Immediate Maintenance

- Dogfood v3.0rc on one real 10-15 paper project.
- Track any command, docs, or schema friction from that project.
- Fix only blockers and high-priority usability issues before v3.0.0.
- Keep v3 stable/experimental docs in sync with CLI help.

## Potential v3.x Work

- Reduce duplicated historical docs and generated reports.
- Split `paper_workbench/cli.py` behind command-contract tests.
- Harden project-local import review workflows after real use.
- Improve report discoverability without adding many new report types.
- Dogfood evidence graph, review packets, workflow recipes, and claim lifecycle
  sidecars before considering any stability promotion.

## Not Recommended

- Cloud sync.
- LLM summarization or embeddings.
- Publisher scraping.
- Web app UI.
- Automatic claim verification.
- Arbitrary shell/Python workflow plugins.
