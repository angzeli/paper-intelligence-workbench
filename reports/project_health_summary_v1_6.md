# Project Health Summary v1.6

Project: zis_photocatalysis

## Counts

| Area | Errors | Warnings | Info |
| --- | ---: | ---: | ---: |
| BibTeX | 0 | 1 | 0 |
| Citation audit | 1 | 6 | 0 |
| Workspace health | 1 | 4 | 0 |
| Rules | 8 | 16 | 0 |
| Manuscript QA | 4 | 2 | 0 |

## Gaps

- Missing parsed notes: 0
- Weak/low-confidence claims: 1
- Claims missing evidence locations: 1

## Highest Priority Actions

| Priority | Action ID | Reason | Command | Related |
| --- | --- | --- | --- | --- |
| critical | `health:claim_missing_evidence_location:zis_stability_2024:c1` | Workspace health error: zis_stability_2024:c1 has no section/page evidence location. | `paperwb doctor --project zis_photocatalysis` | zis_stability_2024:c1 |
| high | `rule:builtin.manuscript.citation_key_not_in_bibtex:unknownSynthetic2027` | Rule violation: Citation key unknownSynthetic2027 is not present in the BibTeX library. | `paperwb rules report --project zis_photocatalysis` | unknownSynthetic2027 |
| medium | `citation:theme_only_review_statements:photocorrosion` | Citation audit warning: photocorrosion is supported only by review statements. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `citation:theme_too_few_papers:photocorrosion` | Citation audit warning: photocorrosion has evidence from 1 paper(s); target is 2. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `citation:theme_under_supported:photocorrosion` | Citation audit warning: photocorrosion has 1 supporting claim(s); target is 2. | `paperwb report evidence-map --project zis_photocatalysis` | photocorrosion |
| medium | `followup:note:zis_charge_2025:1` | Add verified notes from user-owned sources. | `paperwb followups list --project zis_photocatalysis` | zis_charge_2025 |
| medium | `followup:note:zis_stability_2024:1` | Add section/page before citing. | `paperwb followups list --project zis_photocatalysis` | zis_stability_2024 |
| medium | `manuscript:citation_key_not_in_bibtex:anotherMissing2028` | Manuscript QA warning: Citation key anotherMissing2028 is not present in the BibTeX library. | `paperwb manuscript qa DRAFT.md --project zis_photocatalysis` | anotherMissing2028 |
| medium | `manuscript:citation_key_not_in_bibtex:unknownSynthetic2027` | Manuscript QA warning: Citation key unknownSynthetic2027 is not present in the BibTeX library. | `paperwb manuscript qa DRAFT.md --project zis_photocatalysis` | unknownSynthetic2027 |
| medium | `manuscript:citation_key_not_in_registry:anotherMissing2028` | Manuscript QA warning: Citation key anotherMissing2028 is not linked to a registry paper. | `paperwb manuscript qa DRAFT.md --project zis_photocatalysis` | anotherMissing2028 |
