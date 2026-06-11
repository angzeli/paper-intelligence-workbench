# Citation Bank

A citation bank groups papers by likely use based on linked claims.

Groups include:

- background
- method
- primary evidence
- mechanism
- limitation
- review context
- comparison
- not yet usable

Each row includes the paper title, year, venue, BibTeX key, reading status, linked claims, evidence strength, and warnings.

```bash
paperwb report citation-bank --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_citation_bank.md --force
```

The grouping is a local completeness aid. It does not invent a citation role for a paper without a tracked claim.
