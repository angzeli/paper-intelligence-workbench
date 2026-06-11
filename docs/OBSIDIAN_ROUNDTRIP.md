# Obsidian Export Comparison

The Obsidian comparison workflow compares an exported Markdown vault against
local structured notes. The v1.3 Obsidian export is a one-way Markdown view for
reading and linking; it is not an authoritative structured-note round-trip
format.

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

Because the vault files are optimized for Obsidian-style reading rather than
the original structured note template, a freshly exported vault can report note
differences. Treat those findings as manual review prompts, not as proof that
local notes changed.

v1.3 does not auto-merge these differences. It produces a manual review plan
only, because user notes are source material and should not be rewritten by a
sync tool.
