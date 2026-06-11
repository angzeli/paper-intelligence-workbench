# Manuscript QA Limitations

Manuscript QA is intentionally conservative.

Known limitations:

- It does not parse full LaTeX projects or compile LaTeX.
- Citation extraction supports common Markdown, Pandoc, and simple LaTeX-ish citation commands only.
- Paragraph-to-claim matching is lexical and heuristic.
- It can miss valid support when the draft paraphrases far from the structured claim text.
- It can flag false positives when a paragraph shares keywords with a claim but uses them differently.
- It cannot judge scientific truth or whether an argument is correct.
- It cannot replace manual citation checking before submission.

Supported citation patterns include:

- `@key`
- `[@key]`
- `[@key; @key2]`
- `\cite{key}`
- `\citep{key}`
- `\citet{key}`
- `\citealp{key}`
- `\autocite{key}`
- `\parencite{key}`

The tool only audits and structures local evidence. It must not be used to fabricate citations, claims, quotes, or final prose.
