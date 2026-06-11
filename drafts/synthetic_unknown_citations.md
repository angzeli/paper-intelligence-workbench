# Synthetic Unknown Citations Manuscript

This synthetic manuscript tests missing citation-key diagnostics.

## Missing Citation Coverage

The draft cites a placeholder work that is not present in the local BibTeX or registry [@unknownSynthetic2027]. The tool should report citation cleanup rather than inventing a paper.

The manuscript also uses an author-year command \autocite{anotherMissing2028} so LaTeX-ish missing keys are detected.
