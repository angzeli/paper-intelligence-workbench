# Report Archive Plan v3.0rc2

## Goal

Reduce root `reports/` noise before a later public push or tag while preserving release evidence and test fixtures.

## Keep At Root

- `reports/index.md`
- `reports/hostile_review_latest.md`
- current v3.0rc2 cleanup reports
- current v3.5 private dogfooding reports
- current release-readiness and final verdict reports
- public synthetic demo reports that are linked from docs

## Archive Candidates

Suggested future layout:

```text
reports/archive/v0/
reports/archive/v1/
reports/archive/v2/
reports/archive/v3/
reports/archive/stress/
reports/archive/legacy-unversioned/
```

Archive candidates:

- old v0.x report-regression and stress reports
- old v1.x feature-release reports
- old v2.x readiness and patch-plan reports
- old v3.0rc and v3.1-v3.4 reports after v3.0rc2 is accepted
- legacy unversioned report outputs superseded by project-local reports

## Do Not Archive Yet

- Reports referenced by tests.
- Reports linked from README or docs.
- `reports/hostile_review_latest.md`.
- Current public dogfood demo reports.

## Policy For Future Generated Reports

Use `docs/GENERATED_REPORT_POLICY.md` as the source of truth. In short:

- commit only synthetic, redacted, release-relevant reports
- write ad hoc outputs to `scratch/` or project-local `reports/`
- keep real private project output outside the repository
- regenerate `reports/index.md` only when current release reports change

## Recommended Sequence

1. Run docs link checks and tests.
2. Identify docs/tests references to root reports.
3. Move old reports into archive directories in a dedicated cleanup commit.
4. Regenerate `reports/index.md`.
5. Run data-safety audit and full tests.

No archive moves were performed in this v3.0rc2 cleanup pass.
