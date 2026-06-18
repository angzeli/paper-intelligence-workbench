# External Workspace Safety v3.5

## Safety Boundary

- No cloud APIs.
- No LLM APIs.
- No publisher scraping.
- No PDF copying.
- No PDF text extraction.
- No private notes or drafts copied into the repository.
- No real paper metadata committed by the adapter.
- Support bundles stay redacted by default.

## Ignored Local State

`.paperwb-local/` is ignored in `.gitignore`.

If `.paperwb-local/` is ever staged or tracked, the repository data-safety
audit treats it as a forbidden tracked artifact.

## Tested Scenarios

- Local-only config creation.
- External workspace registration.
- External workspace validation.
- Missing path rejection.
- External doctor/dashboard/validation runs.
- Claims, evidence map, and citation-audit outputs written to external paths.
- Support bundle redaction from an external workspace.
- Backup creation in the external project root without copying PDFs.

## Known Limitations

- External workspaces must use the existing project-profile layout:
  `<external_workspace>/projects/<project>/`.
- `external run` intentionally supports only a bounded command list.
- Validation includes project-readiness findings, so early real projects may
  show many evidence/theme gaps.
- The local pointer file is private local state; users must not share it.

