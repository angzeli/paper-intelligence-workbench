# Support Bundle Data Safety v3.1

The support-bundle workflow was checked against the v3.1 privacy boundary.

## Safe Defaults

- `paperwb support bundle` defaults to safe redaction.
- Paper titles, authors, DOI/URL values, BibTeX keys, local PDF paths, claim
  text, quotes, note bodies, and user comments are redacted from CSV samples.
- Bundle summaries preserve counts, schema shape, validation codes, and report
  inventory without copying source notes or drafts.

## Excluded Artifacts

The demo bundle was inspected for forbidden output types:

- `*.pdf`: none
- `*.sqlite`: none
- `*.db`: none
- backup archives: none
- raw `audit.log`: none

## Remaining Risk

Verbose local-only mode can include more metadata for private debugging. Users
must inspect verbose bundles manually before sharing them.
