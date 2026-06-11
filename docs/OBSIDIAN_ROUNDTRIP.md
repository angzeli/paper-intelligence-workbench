# Obsidian Round-trip

The Obsidian round-trip workflow compares an exported Markdown vault against
local structured notes.

```bash
paperwb export obsidian --project zis_photocatalysis --out scratch/obsidian_zis
paperwb sync plan-obsidian \
  --project zis_photocatalysis \
  --vault scratch/obsidian_zis \
  --out scratch/obsidian_roundtrip.md \
  --json-out scratch/obsidian_roundtrip.json \
  --force
```

The command detects:

- exported notes missing locally
- local notes missing from the exported vault
- changed citation keys
- changed reading status
- tag differences
- claim text/count differences
- follow-up action differences
- personal reading note differences

v1.3 does not auto-merge these differences. It produces a manual review plan
only, because user notes are source material and should not be rewritten by a
round-trip tool.

