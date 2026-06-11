# Local Files

v0.7 adds local document-file auditing for user-provided files. The workbench can scan project folders, compute hashes, link files to paper IDs, and report missing or duplicate files.

It remains local-first:

- no downloads
- no publisher scraping
- no OCR
- no cloud or LLM APIs
- no committed PDFs

## Supported Files

The scanner recognizes these extensions:

- `pdf`
- `txt`
- `md`
- `bib`
- `ris`
- `csv`

Unsupported files are reported but not modified.

## Default Project Layout

Project profiles use:

```text
projects/<project>/
  papers/
  text/
  notes/
  bibtex/
  files.csv
```

The legacy single-workspace flow uses:

```text
data/papers/
data/text/
data/notes/
data/bibtex/
data/registries/local_files.csv
```

## Commands

```bash
paperwb files scan --project zis_photocatalysis
paperwb files scan --project zis_photocatalysis --write-registry
paperwb files status --project zis_photocatalysis
paperwb files audit --project zis_photocatalysis --force
paperwb files hash projects/zis_photocatalysis/text/zis_charge_2025.txt
```

`scan` is read-only unless `--write-registry` is provided. `audit` writes Markdown reports only.

When `--write-registry` is used, scan results are merged with the existing local file registry instead of replacing it wholesale. Matching rows preserve curated notes and metadata, and older rows that are not present in the current scan are retained for review.

## Linking

```bash
paperwb files link PAPER_ID projects/zis_photocatalysis/papers/PAPER_ID.pdf --project zis_photocatalysis
paperwb files unlink PAPER_ID --project zis_photocatalysis
```

Linking does not copy or delete files. PDF links fill `local_pdf_path` in the paper registry. Existing `local_pdf_path` values are not replaced unless `--force` is used.

Unlinking removes file-registry rows for a paper ID without deleting files. By default it clears `local_pdf_path` only when at least one file-registry row was actually removed; use `--keep-pdf-path` to preserve registry PDF metadata.

## Safety

Store local papers in ignored folders. The repository ignores `*.pdf` so user PDFs are not accidentally committed.
