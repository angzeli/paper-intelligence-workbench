# Response to Review

After importing reviewer comments, generate response and follow-up reports:

```bash
paperwb review-packet response \
  --project zis_photocatalysis \
  --theme photocorrosion \
  --out scratch/response_to_review.md \
  --force

paperwb review-packet followups \
  --project zis_photocatalysis \
  --theme photocorrosion \
  --out scratch/review_followups.md \
  --force
```

The response report groups comments into manual actions:

- unresolved comments
- reread requests
- citation checks
- weak-evidence warnings
- unknown linked items

These reports are checklists. They do not accept reviewer comments as truth and
do not change evidence automatically.
