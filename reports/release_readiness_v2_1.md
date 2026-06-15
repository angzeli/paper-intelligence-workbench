# Release Readiness v2.1

Release label: `v2.1`

## Features Added

- Local evidence graph data model with nodes and edges derived from existing workbench data.
- Graph builder for project profiles and explicit registry/BibTeX/notes/themes paths.
- Graph analytics for orphan papers, papers without notes, notes without claims, claims without themes, isolated themes, review-heavy themes, central papers, and missing evidence locations.
- CLI group:
  - `paperwb graph build`
  - `paperwb graph summary`
  - `paperwb graph export --format json`
  - `paperwb graph export --format dot`
- Dashboard graph metrics for orphan papers, isolated themes, and review-heavy themes.
- JSON and Graphviz DOT graph exports.
- Synthetic graph workflow example.

## Commands Checked

```bash
python -m paper_workbench.cli graph --help
python -m paper_workbench.cli graph build --project zis_photocatalysis
python -m paper_workbench.cli dashboard --project zis_photocatalysis --limit 3
pytest tests/test_evidence_graph_v2_1.py
```

## Reports Generated

- `reports/evidence_graph_summary_v2_1.md`
- `reports/orphan_nodes_v2_1.md`
- `reports/theme_connectivity_v2_1.md`
- `reports/central_papers_v2_1.md`
- `reports/graph_export_inventory_v2_1.md`

## Data Safety Assessment

- No PDFs are read or copied.
- No PDF text, copyrighted paper text, fabricated metadata, or fabricated claims are included.
- Graph exports may contain local titles, paper IDs, citation keys, tags, and user-entered claim metadata already present in the workspace.
- Graph analytics are local connectivity checks, not scientific-truth checks.
- The tracked public dogfood demo has been replaced with synthetic-only placeholders.
- Data-safety checks now flag non-synthetic public demo registry rows, copied BibTeX-style demo metadata, and non-synthetic PDF filename mentions in public demo Markdown.

## Blocker Fix Validation

- Removed tracked private dogfood outputs from `public/demos/v2_0_dogfood_real/`.
- Preserved the removed private dogfood output locally outside the repository before cleanup.
- Changed `scripts/performance_sanity.py` default output to ignored `scratch/performance_sanity.md` so the script no longer overwrites a committed historical report by default.
- Aligned package metadata with v2.1 and updated v2 API/CLI surface docs to mark graph and advanced workflows honestly.
- `python scripts/data_safety_audit.py --strict`: 0 errors, 7 warnings.
- Full `python -m pytest -q`: passed.

## Known Limitations

- Draft/manuscript citation occurrences are not yet first-class graph nodes.
- Graph centrality is only a degree count.
- Theme support is based on explicit `supports_theme` values and local tag matching.
- Review-heavy theme detection is heuristic and based on local `source_type`, tags, and labels.
- No external graph database or visualization dependency is included.

## Verdict

Ready for local dogfooding as an experimental v2.1 feature. Keep graph analytics marked experimental until they have been used on a real project and false-positive behavior has been reviewed.
