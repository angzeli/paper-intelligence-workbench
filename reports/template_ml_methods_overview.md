# ML Methods Template Overview

This template is a synthetic scaffold for machine-learning methodology reading.
It contains no real paper metadata or claims.

## Included Themes

| Theme | Purpose |
| --- | --- |
| model-assumptions | Track assumptions, inductive bias, and model design |
| benchmarks | Track datasets, baselines, and benchmark limitations |
| uncertainty | Track uncertainty, calibration, and confidence evidence |
| optimization | Track training, convergence, and optimization context |
| evaluation-metrics | Track metrics, measurement, and evaluation choices |
| reproducibility | Track replication, open-code, and reproducibility evidence |
| limitations | Track scope, failure modes, and caveats |

## Included Rule Examples

- Included papers should have BibTeX keys.
- Read papers should have structured notes.
- Strong claims should have page or section evidence.
- Manuscript citations should resolve to local registry and BibTeX entries.

## First Workflow

```bash
paperwb template create ml-methods --project my_ml_methods
paperwb rules validate-config --project my_ml_methods
paperwb dashboard --project my_ml_methods --no-audit-log
```

The template helps track method evidence. It does not judge model quality,
benchmark fairness, or scientific truth.
