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
- Consider a guided import-to-registry review command only after dogfooding proves
  the read-only planning report is not enough.

## Not Worth Expanding Yet

- Cloud sync.
- LLM summarization.
- PDF full-text extraction by default.
- Web app UI.
- Arbitrary executable plugins.
