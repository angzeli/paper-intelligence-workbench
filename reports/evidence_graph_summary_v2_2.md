# Evidence Graph Summary v2.2

This report summarizes a local evidence graph derived from registry, BibTeX, structured notes, claims, themes, and reading-session state. It is a completeness and connectivity aid, not a truth score.

Project: `zis_photocatalysis`

## Node Counts

| Node type | Count |
| --- | ---: |
| `author` | 3 |
| `bibtex_entry` | 2 |
| `claim` | 2 |
| `evidence_location` | 1 |
| `followup` | 2 |
| `note` | 2 |
| `paper` | 2 |
| `tag` | 3 |
| `theme` | 2 |

## Edge Counts

| Edge type | Count |
| --- | ---: |
| `authored_by` | 3 |
| `contains_claim` | 4 |
| `derived_from_note` | 2 |
| `has_bibtex` | 2 |
| `has_evidence_location` | 1 |
| `has_followup` | 2 |
| `has_note` | 2 |
| `supports_theme` | 11 |
| `tagged_with` | 14 |

## Connectivity Warnings

- Orphan papers: 0
- Papers without notes: 0
- Notes without claims: 0
- Claims without themes: 0
- Claims missing evidence locations: 1
- Deprecated claims: 0
- Unverified lifecycle claims: 0
- Isolated themes: 0
- Review-paper-heavy themes: 0

## Central Papers

| Rank | Paper | Degree |
| ---: | --- | ---: |
| 1 | `zis_charge_2025`: Synthetic ZIS Charge Transfer Benchmark | 11 |
| 2 | `zis_stability_2024`: Synthetic ZIS Stability Screening Memo | 9 |

## Theme Connectivity

| Theme | Papers | Claims | Minimum papers | Minimum claims | Review-like papers | Warning |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `photocorrosion` photocorrosion | 2 | 1 | 2 | 2 | 0 | below configured minimum |
| `charge-separation` charge separation | 1 | 1 | 1 | 1 | 0 | ok |
