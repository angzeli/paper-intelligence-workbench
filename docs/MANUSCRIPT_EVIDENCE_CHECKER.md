# Manuscript Evidence Checker

The manuscript evidence checker compares draft paragraphs with user-entered
claims and evidence locations from structured notes.

It can flag:

- unknown citation keys;
- cited papers missing notes;
- cited papers with no extracted claims;
- cited papers marked unread or skimmed;
- paragraphs with citations but no local claim match;
- paragraphs supported only by `review_statement` evidence;
- strong wording backed only by weak, low-confidence, or review-only evidence.

It cannot:

- verify scientific truth;
- infer claims from papers;
- read PDFs;
- generate missing citations;
- rewrite a manuscript section as final prose.

Use it before polishing a literature-review subsection, especially after
creating evidence maps and writing packets.
