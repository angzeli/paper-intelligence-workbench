# Known Limitations v1.0-rc

## Parser Limits

- BibTeX support is intentionally lightweight and does not implement every macro
  or style feature.
- Markdown note parsing is conservative and works best with the generated note
  template.
- RIS import covers common fields only.
- CSV import quality depends on explicit mapping files and source headers.

## Search Limits

- Default search is substring-based.
- Indexed search is a local SQLite cache and must be rebuilt after source files
  change.
- FTS5 availability depends on the local Python SQLite build; fallback behavior
  remains local and lexical.

## Authoring Limits

- Authoring reports are planning aids only.
- The tool does not write polished literature-review prose.
- The tool does not infer unsupported claims or decide whether a scientific
  claim is true.
- Readiness scores measure local evidence-tracking completeness, not truth.

## File And Document Limits

- PDF metadata is advisory only.
- The tool does not download, OCR, scrape, or parse full PDF text by default.
- Text sidecars must be user-provided and copyright-safe.

## Release Hygiene Limits

- Historical reports still contain some absolute-path warnings. The v1.0-rc
  data-safety audit reports zero blocking errors and keeps these warnings
  visible rather than rewriting historical review artifacts.
- The clean-room check uses the current Python environment by default. A stricter
  fresh virtual-environment process is documented in the generated report.
- The package is not published to PyPI and is not tagged as v1.0.0.
