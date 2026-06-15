# Graph Exports

`paperwb graph export` writes a local evidence graph in simple portable formats.

## JSON

```bash
paperwb graph export --project zis_photocatalysis --format json --out scratch/evidence_graph.json --force
```

The JSON export contains:

- `project`
- `nodes`
- `edges`

Each node has `node_id`, `node_type`, `label`, and local metadata. Each edge has
`source`, `target`, `edge_type`, optional `label`, and metadata.

## Graphviz DOT

```bash
paperwb graph export --project zis_photocatalysis --format dot --out scratch/evidence_graph.dot --force
```

DOT output is intended for local visualization with Graphviz-compatible tools.
The workbench does not require Graphviz to build or export the graph.

## Safety

Exports do not include PDF text or copied paper full text. They may include
local paper IDs, citation keys, titles, user tags, claim IDs, and user-entered
claim metadata already present in the workspace.

