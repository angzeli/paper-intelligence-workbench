# Subsection Readiness

The subsection readiness report gives a transparent local completeness score for a theme.

It considers:

- number of supporting or tagged papers
- number of read or deeply read papers
- number of tracked claims
- strong claims
- evidence-type diversity
- missing notes
- missing evidence locations
- missing linked BibTeX entries
- reliance only on review statements

Generate one with:

```bash
paperwb report subsection-readiness --project zis_photocatalysis --theme charge_separation --out scratch/charge_separation_readiness.md --force
```

This is not a truth score. It only reports whether the local evidence tracking looks complete enough to start outlining a subsection.
