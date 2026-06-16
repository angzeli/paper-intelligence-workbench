# Review Packets

`paperwb review-packet` creates local, file-based packets for manual review by
a supervisor or collaborator. It does not send email, use cloud services, copy
PDFs, or modify project evidence.

```bash
paperwb review-packet create \
  --project zis_photocatalysis \
  --theme photocorrosion \
  --out scratch/review_packet_photocorrosion \
  --force
```

A packet directory contains:

- `overview.md`
- `review_instructions.md`
- `comments.csv`
- `manifest.json`
- `evidence_matrix.md`
- `claim_bank.md`
- `citation_bank.md`
- `missing_evidence.md`

When `--draft` is supplied, the packet also includes draft parse and audit
outputs. Draft review remains heuristic and local; it does not rewrite prose.

## Boundary

Review packets expose only the local metadata and evidence reports the user
chooses to export. They do not include PDFs by default. Reviewer comments are
advisory and are imported into a separate sidecar, not into claims or notes.
