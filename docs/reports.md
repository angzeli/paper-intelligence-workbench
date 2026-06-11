# Reports

Reports are Markdown files generated from local inputs. Existing files are not overwritten unless `--force` is supplied.

## Common Reports

- `inventory`: registry inventory and validation context.
- `reading-status`: counts and lists by reading status.
- `bibtex-audit`: BibTeX completeness and registry-link findings.
- `evidence-map`: theme-based claims and evidence coverage.
- `citation-audit`: citation-readiness gaps.
- `theme-dashboard`: theme coverage table.
- `weak-claims`: claims with low confidence or weak strength.
- `missing-evidence`: claims without section/page/location details.
- `workspace-health`: structural workspace diagnostics from `paperwb doctor`.

## Authoring Reports

- `evidence-matrix`
- `claim-bank`
- `citation-bank`
- `paragraph-plan`
- `subsection-readiness`
- `writing-packet`

These are planning reports only. They do not write final prose or invent evidence.

## Local-File Reports

```bash
paperwb files audit --project zis_photocatalysis --force
```

The audit generates local file, duplicate file, missing file, and text-sidecar reports.

See [Report Gallery](REPORT_GALLERY.md) for command examples and interpretation boundaries.
