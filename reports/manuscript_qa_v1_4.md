# Manuscript Citation QA Report

This reviewer-style QA report audits a user-written manuscript draft against local user-tracked evidence. It does not rewrite prose, judge scientific truth, or fabricate support.

Draft file: drafts/synthetic_overconfident_section.md
Project: zis_photocatalysis
Manuscript title: Synthetic Overconfident Manuscript Section
Sections: 2
Paragraphs: 3
Citation keys found: 1
Unknown BibTeX keys: 0
Unknown registry keys: 0
Cited papers missing notes: 0
Cited papers missing claims: 0
Paragraphs with no citation: 0
Paragraphs with weak or missing evidence: 2
Review-statement-only paragraphs: 1
Final readiness verdict: needs evidence strengthening

## Citation Keys Found

- `zisStability2024` -> zis_stability_2024

## QA Findings

| Severity | Code | Paragraph | Citation | Paper | Message | Suggestion |
| --- | --- | --- | --- | --- | --- | --- |
| warning | cited_paper_only_weak_claims |  | zisStability2024 | zis_stability_2024 | zisStability2024 cites zis_stability_2024, which currently has only weak or low-confidence claims. | Re-read the paper or add stronger evidence before making confident statements. |
| warning | paragraph_only_review_statement_evidence | p002 |  |  | p002 currently matches only review-statement evidence. | Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim. |
| warning | strong_wording_with_weak_evidence | p002 |  |  | p002 uses strong wording (proves, definitively, always) but local evidence is weak, missing, or review-only. | Soften wording or add stronger tracked evidence. |
| warning | paragraph_no_evidence_match | p003 |  |  | p003 has citations but no local claim match. | Check whether the cited paper supports this paragraph in your notes. |

## Paragraph Evidence Table


| Paragraph | Section | Citations | Matched claims | Evidence summary | Warnings |
| --- | --- | --- | --- | --- | --- |
| p001 | Synthetic Overconfident Manuscript Section | [none] | [none] | [none] |  |
| p002 | Photocorrosion Claim | zisStability2024 | zis_stability_2024:c1 (weak, review_statement, score=8) | zis_stability_2024/zisStability2024: moderate via photocorrosion, synthetic, unstable | paragraph_only_review_statement_evidence: Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim.; strong_wording_with_weak_evidence: Soften wording or add stronger tracked evidence. |
| p003 | Photocorrosion Claim | zisStability2024 | [none] | [none] | paragraph_no_evidence_match: Check whether the cited paper supports this paragraph in your notes. |

## Citation Context Table

| Section | Paragraph | Citation key | Paper title | Year | Evidence type | Matched claim | Strength | Confidence | Evidence location | Warning |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Photocorrosion Claim | p002 | zisStability2024 | Synthetic ZIS Stability Screening Memo | 2024 | review_statement | zis_stability_2024:c1: The memo suggests photocorrosion risk may increase under unstable synthetic screening conditions. | weak | low | [missing] | cited_paper_only_weak_claims; paragraph_only_review_statement_evidence; strong_wording_with_weak_evidence |
| Photocorrosion Claim | p003 | zisStability2024 | Synthetic ZIS Stability Screening Memo | 2024 | [no match] | [no local claim match] | [missing] | [missing] | [missing] | cited_paper_only_weak_claims; paragraph_no_evidence_match |

## Revision Checklist

- [ ] cited_paper_only_weak_claims [zisStability2024] [zis_stability_2024]: Re-read the paper or add stronger evidence before making confident statements.
- [ ] paragraph_only_review_statement_evidence (p002): Add primary experimental, method, or mechanism evidence if the paragraph makes a direct claim.
- [ ] strong_wording_with_weak_evidence (p002): Soften wording or add stronger tracked evidence.
- [ ] paragraph_no_evidence_match (p003): Check whether the cited paper supports this paragraph in your notes.

## Suggested Follow-up Reading

- Re-check weak evidence before relying on `zisStability2024` (zis_stability_2024).

## Boundary

Use this report to revise manually. Do not treat lexical matches as semantic certainty.
