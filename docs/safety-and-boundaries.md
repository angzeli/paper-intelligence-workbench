# Safety And Boundaries

Paper Intelligence Workbench is local-first.

## The Tool Does Not

- scrape publishers
- download PDFs
- bypass paywalls
- use cloud APIs
- use LLM APIs
- OCR scans
- parse full PDF text by default
- fabricate paper metadata, claims, citations, quotes, or summaries
- write final literature-review prose

## User-Owned Inputs

The tool organizes local files supplied by the user:

- CSV registries
- BibTeX and RIS files
- Markdown notes
- JSON theme files
- optional plain-text sidecars
- optional local PDFs referenced by path

Do not commit real PDFs or copied paper full text.

## Release Safety Checks

```bash
python scripts/data_safety_audit.py --strict
python scripts/check_notebooks.py
python scripts/smoke_cli_workflow.py --quick
```

See [DATA_SAFETY_MATRIX.md](DATA_SAFETY_MATRIX.md) for the release safety matrix.
