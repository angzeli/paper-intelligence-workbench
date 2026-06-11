# Claim Bank

A claim bank groups claims for a theme by readiness.

Sections include:

- strong claims
- moderate claims
- weak or speculative claims
- claims missing evidence locations
- claims supported by review statements
- claims with conflicting theme tags
- claims not ready for confident use

Generate one with:

```bash
paperwb report claim-bank --project zis_photocatalysis --theme photocorrosion --out reports/photocorrosion_claim_bank.md --force
```

Use the report to decide which claims can support a subsection and which claims need more reading before citation.
