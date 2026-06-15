# Graph Analytics

Graph analytics are transparent completeness checks over the local evidence
graph. They are designed to reveal gaps before writing a literature review.

## Current Analytics

- Orphan papers: registry papers with no note, no claim edge, and no theme edge.
- Papers without notes.
- Notes without claims.
- Claims without themes.
- Claims missing evidence locations.
- Isolated themes.
- Themes below configured minimum paper or claim counts.
- Review-paper-heavy themes based on local `source_type`, tags, or labels.
- Central papers ranked by graph degree.

## Dashboard Integration

The terminal dashboard includes graph-derived counts for:

- orphan papers
- isolated themes
- review-heavy themes

It may also suggest a next action to run `paperwb graph summary` when graph
connectivity gaps are found.

## Limitations

Graph analytics do not judge whether a scientific claim is true. Theme support
is based on explicit `supports_theme` values and local tag matching. Review-heavy
theme detection is a heuristic over local metadata.

