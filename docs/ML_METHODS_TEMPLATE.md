# ML Methods Template

The ML methods template supports reading projects about machine-learning
methodology. It emphasizes assumptions, benchmarks, uncertainty, evaluation,
reproducibility, and limitations.

## Themes

- model assumptions
- benchmarks
- uncertainty
- optimization
- evaluation metrics
- reproducibility
- limitations

## Rule Examples

- Included papers should have BibTeX keys.
- Read papers should have notes.
- Theme coverage should be checked before writing.
- Strong claims should have page or section evidence.
- Manuscript citations should resolve to local registry and BibTeX entries.

## Recommended Workflow

```bash
paperwb template create ml-methods --project my_ml_methods
paperwb rules validate-config --project my_ml_methods
paperwb dashboard --project my_ml_methods --no-audit-log
```

The template does not judge model quality or benchmark validity. It only helps
track what the user has read and recorded.
