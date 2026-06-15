# v2.2 Recommended Patch Plan

## Recommended Scope

- Dogfood evidence graph analytics on the real photocatalysis project.
- Add optional manuscript/draft citation occurrence nodes once the audit workflow has stable output IDs.
- Add a graph diff report for before/after reading sessions or sync plans.
- Add a small DOT rendering guide without adding Graphviz as a required dependency.
- Review dashboard next-action noise from graph-derived warnings.

## Do Not Expand Yet

- Do not add a graph database.
- Do not add embeddings or semantic similarity.
- Do not infer paper importance from graph centrality.
- Do not auto-create claims, themes, or citation links.
- Do not parse PDF full text for graph construction.

## Validation Needed Before v2.2

- Run graph summary and export on a real project.
- Compare graph orphan-paper warnings with manual project expectations.
- Check whether tag-based theme links are too noisy.
- Confirm JSON export does not leak private paths when used on real local projects.

