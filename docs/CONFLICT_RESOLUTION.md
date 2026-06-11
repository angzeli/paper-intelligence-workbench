# Conflict Resolution

Sync conflicts are conservative warnings that the tool should not guess.

## Conflict Types

- `same_doi_different_title`: one DOI maps to different titles
- `same_title_different_doi`: one normalized title maps to different DOIs
- `same_bibtex_key_different_doi`: one citation key maps to different DOIs
- `registry_field_differs_from_import`: a non-empty registry field differs from
  an import source
- `tag_mismatch`: registry and import tags differ
- `local_note_differs_from_exported_note`: local and exported note content
  differ in parseable fields
- `note_exists_in_export_not_local`: exported note has no local counterpart
- `note_exists_locally_not_in_export`: local note is missing from export

## Resolution Rule

Do not auto-merge conflicts. Review the registry row, BibTeX entry, and note
file manually, then regenerate the sync plan.

For high-risk identifier conflicts, prefer a human decision over automated
metadata changes. The tool may identify a mismatch, but it does not know which
source is authoritative.

