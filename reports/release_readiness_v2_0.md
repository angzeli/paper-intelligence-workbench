# Release Readiness v2.0

Version: `2.0`

## Verdict

Ready for local dogfooding after validation.

## Added In v2.0

- `paperwb dogfood create` for empty real-project scaffolds.
- `paperwb dogfood status` for empty-project-friendly status messages.
- `paperwb dogfood checklist` for real-paper intake guidance.
- `paperwb dogfood plan-from-files` for read-only metadata-backed starter planning from local PDF filenames and BibTeX keys.
- Expanded FYP photocatalysis theme pack.
- Real-project onboarding docs and reports.

## Data Safety

- No real paper metadata was added to repository fixtures.
- No PDFs or copied paper full text were added.
- The metadata-backed plan command does not parse PDF text, copy files, or write registry rows.
- Private reference paths should be used only at runtime and should not be committed.

## Compatibility

- Existing `template`, `project`, validation, report, dashboard, and import/export commands are preserved.
- Existing template creation remains non-destructive.
- Dogfood project creation refuses existing project paths.
- Public quickstarts now use clean project-profile validation examples with
  `--strict`; legacy `data/` fixtures remain intentionally imperfect audit
  examples.
- Source distributions include public docs, synthetic examples, reports,
  scripts, notebooks, fixtures, and project profiles needed to reproduce the
  documented clone-based workflows.

## Validation Run

- `pytest -p no:cacheprovider`
- package import
- `paperwb --help`
- `paperwb dogfood --help`
- clean project registry validation with `--strict`
- clean project BibTeX validation with `--strict`
- dogfood project creation in a temporary workspace
- empty dogfood status and checklist
- synthetic metadata-backed planning report
- source distribution content contract

## Known Limitations

- `plan-from-files` matches only simple filename slugs to BibTeX keys.
- It does not infer metadata from PDFs.
- It does not select papers semantically.
- The user must manually verify every registry row and claim.
- Validation commands remain in review mode by default. Use `--strict` when
  error-level findings should fail a script or CI job.

## Release Boundary

v2.0 is an onboarding and dogfooding patch, not an automated paper-ingestion or
literature-writing system.
