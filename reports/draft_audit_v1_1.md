# Draft Citation And Evidence Audit

This report audits a user-written Markdown draft against local user-tracked evidence. It does not rewrite the draft, judge scientific truth, or fabricate support.

Draft file: drafts/synthetic_photocorrosion_section.md
Project: zis_photocatalysis
Sections: 2
Paragraphs: 5
Citation keys found: 2
Unknown BibTeX keys: 1
Unknown registry keys: 1
Cited papers missing notes: 0
Paragraphs with weak or missing evidence: 4
Paragraphs with no citations: 2

## Citation Keys Found

- `zisStability2024` -> zis_stability_2024
- `unknownPhotocorrosion2026` -> [not linked]

## Findings

| Severity | Code | Paragraph | Citation | Paper | Message | Suggestion |
| --- | --- | --- | --- | --- | --- | --- |
| warning | cited_paper_only_weak_claims |  | zisStability2024 | zis_stability_2024 | zisStability2024 cites zis_stability_2024, which currently has only weak or low-confidence claims. | Re-read the paper or add stronger evidence before making confident statements. |
| error | citation_key_not_in_bibtex |  | unknownPhotocorrosion2026 |  | Citation key unknownPhotocorrosion2026 is not present in the BibTeX library. | Add or correct the BibTeX entry before using this citation. |
| error | citation_key_not_in_registry |  | unknownPhotocorrosion2026 |  | Citation key unknownPhotocorrosion2026 is not linked to a registry paper. | Link the citation key to a paper registry row. |
| warning | paragraph_without_citations | p001 |  |  | p001 has no citation keys. | Add citations or mark the paragraph as connective prose. |
| warning | paragraph_only_review_statement_evidence | p002 |  |  | p002 currently matches only review-statement evidence. | Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim. |
| warning | paragraph_only_review_statement_evidence | p003 |  |  | p003 currently matches only review-statement evidence. | Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim. |
| warning | strong_wording_with_weak_evidence | p003 |  |  | p003 uses strong wording (proves, definitively, always) but local evidence is weak, missing, or review-only. | Soften wording or add stronger tracked evidence. |
| warning | paragraph_without_citations | p004 |  |  | p004 has no citation keys. | Add citations or mark the paragraph as connective prose. |
| warning | paragraph_only_review_statement_evidence | p004 |  |  | p004 currently matches only review-statement evidence. | Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim. |
| warning | possible_unsupported_claim | p004 |  |  | p004 mentions project theme(s) photocorrosion without citations. | Add supporting citations or verify this is only transitional prose. |
| warning | paragraph_no_evidence_match | p005 |  |  | p005 has citations but no local claim match. | Check whether the cited paper supports this paragraph in your notes. |

## Citation Coverage


| Citation key | BibTeX | Registry | Paper ID | Reading status | Note | Claims | Strongest claim | Warnings |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| zisStability2024 | yes | yes | zis_stability_2024 | read | yes | 1 | weak | cited paper has only weak or low-confidence claims |
| unknownPhotocorrosion2026 | no | no | [missing] | [missing] | no | 0 | [none] | citation key not found in BibTeX; citation key not found in registry |

## Paragraph Evidence Mapping


| Paragraph | Section | Citations | Matched claims | Evidence summary | Warnings |
| --- | --- | --- | --- | --- | --- |
| p001 | Synthetic Photocorrosion Draft Section | [none] | [none] | [none] | paragraph_without_citations: Add citations or mark the paragraph as connective prose. |
| p002 | Photocorrosion Risk | zisStability2024 | zis_stability_2024:c1 (weak, review_statement, score=13) | zis_stability_2024/zisStability2024: high via increase, memo, photocorrosion, review-style, risk | paragraph_only_review_statement_evidence: Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim. |
| p003 | Photocorrosion Risk | zisStability2024 | zis_stability_2024:c1 (weak, review_statement, score=7) | zis_stability_2024/zisStability2024: moderate via photocorrosion, unstable | paragraph_only_review_statement_evidence: Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim.; strong_wording_with_weak_evidence: Soften wording or add stronger tracked evidence. |
| p004 | Photocorrosion Risk | [none] | zis_stability_2024:c1 (weak, review_statement, score=5) | zis_stability_2024/zisStability2024: low via photocorrosion, catalyst-stability | paragraph_without_citations: Add citations or mark the paragraph as connective prose.; paragraph_only_review_statement_evidence: Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim.; possible_unsupported_claim: Add supporting citations or verify this is only transitional prose. |
| p005 | Photocorrosion Risk | unknownPhotocorrosion2026 | [none] | [none] | paragraph_no_evidence_match: Check whether the cited paper supports this paragraph in your notes. |

## Recommended Revision Checklist

- [ ] cited_paper_only_weak_claims [zisStability2024] [zis_stability_2024]: Re-read the paper or add stronger evidence before making confident statements.
- [ ] citation_key_not_in_bibtex [unknownPhotocorrosion2026]: Add or correct the BibTeX entry before using this citation.
- [ ] citation_key_not_in_registry [unknownPhotocorrosion2026]: Link the citation key to a paper registry row.
- [ ] paragraph_without_citations (p001): Add citations or mark the paragraph as connective prose.
- [ ] paragraph_only_review_statement_evidence (p002): Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim.
- [ ] paragraph_only_review_statement_evidence (p003): Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim.
- [ ] strong_wording_with_weak_evidence (p003): Soften wording or add stronger tracked evidence.
- [ ] paragraph_without_citations (p004): Add citations or mark the paragraph as connective prose.
- [ ] paragraph_only_review_statement_evidence (p004): Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim.
- [ ] possible_unsupported_claim (p004): Add supporting citations or verify this is only transitional prose.
- [ ] paragraph_no_evidence_match (p005): Check whether the cited paper supports this paragraph in your notes.
