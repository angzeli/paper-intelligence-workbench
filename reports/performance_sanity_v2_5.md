# Performance Sanity Report

This is a lightweight sanity check, not a strict benchmark.

## Synthetic Workload

- Requested papers: 500
- Requested claims: 1500
- Requested themes: 50
- Parsed papers: 500
- Parsed notes: 439
- Parsed claims: 1501
- Parsed BibTeX entries: 472
- Search-index records: 3063

## Timings

| Step | Seconds |
| --- | ---: |
| generate synthetic project | 0.0586 |
| load registry | 0.0051 |
| parse notes and claims | 0.0626 |
| parse BibTeX | 0.0229 |
| load themes | 0.0005 |
| validate registry | 0.0368 |
| validate BibTeX | 0.0021 |
| citation audit | 0.0601 |
| workspace doctor | 0.1466 |
| build search-index records | 0.2524 |
| rebuild SQLite search index | 0.0416 |
| check search-index status | 0.0032 |
| build evidence map | 0.0148 |

## Validation Signal

- Registry findings: 156
- BibTeX findings: 247
- Citation-audit findings: 2305
- Workspace-health findings: 1261
- Search-index warnings: 0
- Search-index records stored: 3063
- Evidence-map size: 887139 characters

## Result

The workload completed locally without cloud services, LLM APIs, publisher scraping, or PDF assets.
