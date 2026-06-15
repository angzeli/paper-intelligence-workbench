# Claim Review Queue

The claim review queue ranks extracted claims that need manual evidence review
before draft use.

Ranking is transparent and local. Higher-priority items include:

- strong or moderate claims without page/section evidence locations
- claims marked as used in drafts but not verified
- low-confidence, weak, or speculative claims
- claims supported only by review statements
- claims from unread or skimmed papers
- claims marked deprecated, contradicted, or needing rereading

Example:

```bash
paperwb claim-review queue --project zis_photocatalysis --theme photocorrosion --out reports/claim_review_queue.md
```

The queue is a planning aid. It does not prove that a claim is correct.
