# Report Gallery

Reports are Markdown files generated from local registry, BibTeX, notes, claims, and theme files. They are reproducible from local inputs and do not call external services.

Use `--force` when intentionally replacing an existing report.

## Inventory

Question answered: Which papers are in my registry, and are required registry fields missing?

```bash
paperwb report inventory --registry data/registries/example_papers.csv --out /private/tmp/paperwb_inventory.md --force
```

Look for duplicate DOI/title findings, missing BibTeX keys, and incorrect reading status values.

## Reading Status

Question answered: Which papers are unread, skimmed, partially read, read, or deeply read?

```bash
paperwb report reading-status --registry data/registries/example_papers.csv --out /private/tmp/paperwb_reading_status.md --force
```

Use this before planning the next reading session.

## Papers by Tag

Question answered: Which papers are associated with each research tag?

```bash
paperwb report papers-by-tag --registry data/registries/example_papers.csv --out /private/tmp/paperwb_papers_by_tag.md --force
```

Use this to check whether tags are too broad, too sparse, or inconsistent.

## BibTeX Audit

Question answered: Which citation entries are incomplete, duplicated, or not linked to registry papers?

```bash
paperwb report bibtex-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --out /private/tmp/paperwb_bibtex_audit.md --force
```

Use this before submitting a bibliography or exporting references to another tool.

## Claims by Theme

Question answered: Which claims are currently mapped to each theme?

```bash
paperwb report claims-by-theme --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_claims_by_theme.md --force
```

Use this to find typoed or undefined theme names.

## Evidence Map

Question answered: Which themes have enough strong, located evidence to support a literature-review subsection?

```bash
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_evidence_map.md --force
```

Look for missing evidence locations, weak claims, missing notes, and themes relying only on review statements.

## Theme Dashboard

Question answered: Which themes need follow-up before drafting?

```bash
paperwb report theme-dashboard --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_theme_dashboard.md --force
```

Use this as a quick planning table.

## Citation Audit

Question answered: Am I citing papers for claims that are not properly tracked?

```bash
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_citation_audit.md --force
```

This is the main pre-writing audit. It reports missing notes, claims without evidence locations, registry/BibTeX link gaps, and under-supported themes.

## Missing Notes

Question answered: Which registry papers do not have parsed notes?

```bash
paperwb report missing-notes --registry data/registries/example_papers.csv --notes-dir data/notes --out /private/tmp/paperwb_missing_notes.md --force
```

Use this to decide what to read or annotate next.

## Weak Claims

Question answered: Which claims should not be used as core support yet?

```bash
paperwb report weak-claims --registry data/registries/example_papers.csv --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_weak_claims.md --force
```

Use this before turning notes into prose.

## Missing Evidence

Question answered: Which claims lack a section, page, figure, table, or appendix location?

```bash
paperwb report missing-evidence --registry data/registries/example_papers.csv --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_missing_evidence.md --force
```

Use this to re-open notes before citation-heavy writing.

## Section Outline

Question answered: What evidence do I have for a specific subsection?

```bash
paperwb report section-outline --theme photocorrosion --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_photocorrosion_outline.md --force
```

The output is an evidence-based outline, not polished prose.

## Workspace Health

Question answered: Is the current workspace structurally healthy?

```bash
paperwb doctor --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out /private/tmp/paperwb_workspace_health.md --force
```

Use this when onboarding a project or checking whether paths and project files still line up.
