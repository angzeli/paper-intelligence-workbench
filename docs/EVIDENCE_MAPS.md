# Evidence Maps

Evidence maps group user-entered claims by theme. They are designed to help prepare literature-review subsections without writing or fabricating prose.

Generate one:

```bash
paperwb report evidence-map --project zis_photocatalysis
```

v0.2 evidence maps include:

- theme name
- number of papers
- number of claims
- strong, moderate, and weak claim counts
- claims missing evidence locations
- review-statement versus primary/contextual evidence counts
- papers supporting the theme
- strongest claims
- weak claims
- missing notes
- suggested follow-up actions

Evidence-type weighting is transparent:

- `experimental_result` is treated as stronger direct evidence.
- `method_description` is contextual evidence.
- `review_statement` is secondary support.
- `opinion_or_interpretation` and `unclear` are weaker and should be reviewed carefully.

The report does not decide whether claims are scientifically true. It only organizes the user's tracked evidence.
