# Synthetic Corpus

v0.3 adds deterministic synthetic corpus generation for local scale testing. The generated data is intentionally fake and must not be cited as real literature.

## Generate a Project

```bash
paperwb synthetic generate --project stress_demo --papers 100 --claims 220 --themes 6 --domain zis
```

Supported domains are `zis`, `finance`, and `ml`. The domain changes only the synthetic theme labels and paper-title vocabulary.

The command creates:

- `projects/<project>/registry.csv`
- `projects/<project>/bibtex/library.bib`
- `projects/<project>/notes/*.md`
- `projects/<project>/themes.json`
- `projects/<project>/project.json`

Existing projects are not overwritten unless `--force` is provided.

## Intentional Findings

The generator deliberately includes some incomplete or suspicious records so diagnostics can be tested:

- duplicate DOI values
- duplicate normalized titles
- duplicate BibTeX keys
- malformed DOI-like strings
- missing note cases
- broken local PDF path warnings
- orphan notes without registry rows
- unlinked BibTeX entries
- weak claims
- claims missing evidence locations
- undefined theme references
- review-statement-heavy themes

These findings are regression fixtures, not bugs in the generated project.

## Checked-in Stress Projects

v0.3 includes three synthetic stress projects:

- `projects/stress_zis_photocatalysis`
- `projects/stress_finance_reading`
- `projects/stress_ml_methods`

Together they cover more than 100 papers, more than 200 parsed claims, and 15 themes.

## Boundary

The generator does not:

- use real paper metadata
- use copyrighted PDFs
- scrape publishers
- call cloud services
- call LLM APIs
- fabricate real claims

