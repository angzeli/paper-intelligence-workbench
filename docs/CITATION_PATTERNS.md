# Citation Patterns

The draft parser supports a small set of common Markdown and LaTeX-like
citation patterns:

```text
@smith2024
[@smith2024]
[@smith2024; @lee2023]
\cite{smith2024}
\citep{smith2024,lee2023}
\citet{smith2024}
```

Parsing is conservative. It does not try to support every citation processor or
BibTeX key style. Ambiguous markers are reported as warnings rather than
guessed fixes.

Add tests whenever a new citation pattern is supported.
