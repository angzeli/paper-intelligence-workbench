# BibTeX Audit

The workbench includes a lightweight BibTeX parser for common local libraries.

Run:

```bash
paperwb validate-bib data/bibtex/library.bib --registry data/registries/papers.csv
```

Generate a report:

```bash
paperwb report bibtex-audit --registry data/registries/papers.csv --bibtex data/bibtex/library.bib
```

## Checks

The audit reports:

- missing title
- missing author
- missing year
- missing venue fields such as journal, booktitle, publisher, or school
- duplicate keys
- duplicate DOI values
- empty fields
- suspiciously incomplete entries
- missing DOI warnings for article and conference-style entries
- possible title capitalization issues
- inconsistent field names such as `journaltitle` instead of `journal`
- invalid year format
- BibTeX entries not linked to registry papers
- registry papers without BibTeX entries

The audit never invents citation data and does not aggressively rewrite entries. Suggestions are safe prompts for user review.
