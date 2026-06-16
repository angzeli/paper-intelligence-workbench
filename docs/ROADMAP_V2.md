# Roadmap v2

## v2.0 Dogfooding Stabilization

- Use `paperwb dogfood create photocatalysis` as the recommended first real-project path.
- Keep dogfood scaffolds empty until users add verified metadata.
- Use metadata-backed planning reports before manually adding a 10-15 paper starter set.
- Keep current release reports up to date after each blocker fix.
- Run full tests, smoke workflow, notebook validation, and data-safety audit.
- Confirm no cache, audit, backup, PDF, or build artifacts are staged.
- Run one dogfooding simulation on a private local project before public release.

## After Local Dogfooding

- Simplify README onboarding.
- Reduce duplicate docs.
- Mark advanced workflows as experimental in CLI docs until they have real-use
  feedback.
- Improve report discoverability without adding more report types.
- Dogfood the evidence graph on a real project before marking graph analytics stable.
- Dogfood claim lifecycle review on real notes before marking lifecycle sidecar
  schema stable.
- Dogfood workflow recipes on a real project before treating recipe schemas as
  stable.
- Consider a guided import-to-registry review command only after dogfooding proves
  the read-only planning report is not enough.

## v2.3 Workflow Runner

- Add declarative local workflow recipes for repeated validation and report
  generation.
- Keep recipes limited to built-in safe step types; do not allow shell or Python
  execution from JSON.
- Prefer dry-run before workflows that create reports, backups, or indexes.

## Recommended v2.4 Scope

- Add local file-based review packets for supervisor/collaborator feedback.
- Import reviewer comments into separate sidecars without mutating evidence.
- Generate response-to-review and follow-up reports from imported comments.

## Recommended v2.5 Scope

- Add performance sanity checks and incremental rebuild planning for larger
  local projects.
- Improve report cleanup and archive guidance for historical generated reports.

## Not Worth Expanding Yet

- Cloud sync.
- LLM summarization.
- PDF full-text extraction by default.
- Web app UI.
- Arbitrary executable plugins.
