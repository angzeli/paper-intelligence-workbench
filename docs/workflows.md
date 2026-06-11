# Workflows

Paper Intelligence Workbench is organized around local, reproducible workflows.

## Registry And BibTeX

```bash
paperwb validate-registry data/registries/example_papers.csv
paperwb validate-bib data/bibtex/example_library.bib --registry data/registries/example_papers.csv
```

Use this before writing or exporting citations.

## Notes And Claims

```bash
paperwb note-template synth_charge_2024 --registry data/registries/example_papers.csv --output scratch/synth_charge_2024_note.md --force
paperwb claims data/notes --output scratch/claims.csv
```

The parser extracts only user-entered structured note fields. It does not infer claims from papers.

## Evidence And Citation Audits

```bash
paperwb report evidence-map --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/evidence_map.md --force
paperwb report citation-audit --registry data/registries/example_papers.csv --bibtex data/bibtex/example_library.bib --notes-dir data/notes --themes data/examples/themes.json --out scratch/citation_audit.md --force
```

## Project Profiles

```bash
paperwb project list
paperwb project validate zis_photocatalysis
paperwb report evidence-map --project zis_photocatalysis --force
```

## Indexed Search

```bash
paperwb index rebuild --project zis_photocatalysis --include-text
paperwb search photocorrosion --project zis_photocatalysis --indexed --text
```

The index is a local cache and can be rebuilt.

## Authoring Packet

```bash
paperwb writing-packet --project zis_photocatalysis --theme photocorrosion --out scratch/photocorrosion_packet.md --force
```

The packet provides planning aids, not polished prose.
