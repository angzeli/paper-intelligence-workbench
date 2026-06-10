# Performance Sanity Report v0.3

This is a lightweight sanity check, not a strict benchmark.

## Synthetic Workload

- Requested papers: 100
- Requested claims: 220
- Requested themes: 6
- Parsed papers: 100
- Parsed notes: 89
- Parsed claims: 221
- Parsed BibTeX entries: 96

## Timings

| Step | Seconds |
| --- | ---: |
| generate synthetic project | 0.0133 |
| load registry | 0.0012 |
| parse notes and claims | 0.0109 |
| parse BibTeX | 0.0040 |
| load themes | 0.0002 |
| validate registry | 0.0026 |
| validate BibTeX | 0.0005 |
| citation audit | 0.0054 |
| workspace doctor | 0.0190 |
| build evidence map | 0.0015 |

## Validation Signal

- Registry findings: 34
- BibTeX findings: 62
- Citation-audit findings: 332
- Workspace-health findings: 232
- Evidence-map size: 124112 characters

## Result

The v0.3 workload completed locally without cloud services, LLM APIs, publisher scraping, or PDF assets.
