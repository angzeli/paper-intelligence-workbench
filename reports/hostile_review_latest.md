# Hostile Maintainer Review: v1.3 Current Repository

Date: 2026-06-11

## Release Verdict

Do not release the current v1.3 state to external users until the sync data-integrity blockers are fixed.

The non-sync surface looks substantially hardened: package import works, the full test suite passes, notebook JSON checks pass, the data-safety audit reports no errors, and the repository does not appear to track PDFs, SQLite cache databases, backup archives, or `.paperwb` cache folders. However, the new v1.3 sync workflow violates the project's core safety promise: a forced sync can mutate registry data in ways that were not explicitly planned, and the planner can attach applyable updates to a source row that it simultaneously classifies as a high-risk identity conflict.

That is release-blocking for a local-first research data tool.

## Review Scope

Inspected:

- package metadata and package layout
- CLI command surface, especially `paperwb sync`
- project profiles and generated synthetic projects
- registry, BibTeX, note, claim, evidence-map, citation-audit, authoring, search, file-ingestion, import/export, backup, audit-log, reading-session, draft-audit, and sync modules
- tests and fixture coverage
- notebooks and notebook validation
- generated reports
- docs and release-readiness notes
- tracked-file hygiene and data-safety boundaries

Validation commands run during review:

- `git status --short --branch --ignored=matching`
- `python -m pytest -q`
- `python -m pytest --collect-only -q`
- `python scripts/check_notebooks.py`
- `python scripts/data_safety_audit.py --out scratch/hostile_review_data_safety_current.md --strict`
- `paperwb --help`
- `paperwb sync --help`
- `paperwb project list`
- `paperwb report all --out scratch/hostile_should_fail.md`
- focused `paperwb sync plan`, `paperwb sync apply --dry-run`, and `paperwb sync apply --force --no-backup` probes against synthetic scratch registries

Observed validation results:

- Full tests passed: 187 pytest tests.
- Notebook structural validation passed for 8 notebooks.
- Data-safety audit checked 508 files with 0 errors and 8 warnings.
- `paperwb report all --out ...` correctly fails with a clear error instead of overwriting a single report path.
- `paperwb sync` help and basic planning commands work.

## Release Blockers

### 1. Sync plans can include applyable actions for a high-risk conflicted source record

The sync planner detects high-risk identity conflicts, but it still schedules low-risk `fill_blank_field` actions for the same matched registry paper and source record.

Synthetic reproduction:

- Registry row: `known`, title `Known Synthetic Study`, DOI `10.1300/sync.known`, blank journal/tags/source_type.
- Import row: title `Conflicting Title`, same DOI `10.1300/sync.known`, journal/tags/source_type populated.
- Command: `paperwb sync plan --source scratch/.../conflict.csv --source-type zotero-csv --registry scratch/.../registry.csv ...`
- Result: plan contains conflict `C0001 same_doi_different_title` with risk `high`, but also action IDs `A0001`, `A0002`, and `A0003` to fill `journal`, `tags`, and `source_type` on `known`.

Why this blocks release:

- The planner is saying "this may be the wrong paper" and "these fields are safe to copy" at the same time.
- A user who sees low-risk actions in the same report can reasonably believe the forced apply is constrained to safe changes.
- The project repeatedly promises conservative, non-destructive sync behavior.

Required fix:

- If an incoming source row produces a high-risk identity conflict for a matched paper, suppress all applyable actions derived from that source row.
- Emit only conflict records and manual-review guidance for that row.
- Add a regression test that a same-DOI/different-title record produces zero `fill_blank_field` actions for the conflicted paper.

### 2. Forced sync apply rewrites registry fields that are not present in the sync plan

`sync apply --force` can change existing registry formatting for fields not listed in the plan. In a scratch probe, the registry author value changed from `Synthetic Author` to `Author, Synthetic` even though no author action appeared in the plan.

Likely cause:

- `apply_registry_sync_plan()` deep-copies every existing `Paper` through `paper_to_row()` and `paper_from_row()`.
- CLI writeback uses `save_registry()` on the reconstructed `Paper` objects.
- This normalizes existing rows even when a field was not part of the sync plan.

Why this blocks release:

- The apply report does not list the author change.
- The user did not approve that field change.
- This directly contradicts "report every changed field" and "never silently overwrite user data".
- Even if the normalized form is acceptable internally, sync apply must preserve untouched registry text unless the plan explicitly says the field will change.

Required fix:

- Make sync apply row-preserving for existing registry CSV rows.
- Apply only planned field changes to the original row dictionaries.
- Preserve original values and formatting for untouched fields.
- Add a regression test that forced sync apply leaves non-action fields byte-for-byte or value-for-value unchanged.

### 3. `--force` is overloaded as both write confirmation and high-risk conflict override

Current behavior lets a forced apply proceed when a plan contains high-risk conflicts. Combined with blocker 1, this allows safe-looking field fills from a conflicted record to be written after a single `--force`.

Why this blocks release:

- `--force` is already used throughout the project to mean "perform the write" or "overwrite output".
- Using the same flag to allow high-risk identity-conflict plans makes the most dangerous path too easy.
- This is especially risky for imported Zotero CSV/BibTeX/RIS data, where title, DOI, and citation-key conflicts are common.

Required fix:

- Refuse real apply when any high-risk conflict exists, regardless of ordinary `--force`, unless a separate explicit conflict-override flag is introduced.
- Prefer no conflict override for v1.3 unless there is a strong use case.
- Add CLI and unit tests that high-risk plans cannot write registry changes by default.

## High-Priority Issues

### 1. Dry-run apply reports use misleading "Applied actions" language

`paperwb sync apply PLAN --dry-run` produces a report with `Applied actions: N` and an `## Applied Actions` section even though no registry write occurred.

Why it matters:

- Dry-run reports are the user's safety mechanism.
- The report should say "Would apply actions" or "Planned actions in dry run".

Required fix:

- Change dry-run report labels while preserving the existing command behavior.
- Add a test that dry-run Markdown does not claim actions were actually applied.

### 2. Fresh Obsidian export round-trip reports conflicts immediately

`reports/obsidian_roundtrip_v1_3.md` shows 8 `local_note_differs_from_exported_note` conflicts for the `zis_photocatalysis` project after comparing a generated Obsidian-style vault back to local notes.

Why it matters:

- A fresh export that immediately produces conflicts will make users distrust the round-trip workflow.
- The report is technically conservative, but the feature name and docs imply a round-trip comparison. The current behavior looks more like a one-way export format being parsed as if it were the original structured note format.

Required fix:

- Define whether Obsidian export is one-way or round-trip-capable.
- If one-way, rename or document the command/report clearly and avoid implying parseable round-trip fidelity.
- If round-trip-capable, adjust export or parsing so a fresh export does not generate false conflicts for unchanged notes.
- Add a regression test for the chosen behavior.

### 3. Sync apply has weak stale-plan protection

The apply path skips some actions when the current registry no longer matches expected blank fields, but the plan does not appear to include a registry content hash, source hash, or generated-against fingerprint.

Why it matters:

- A user can generate a sync plan, edit the registry, and then apply an old plan.
- The tool may skip some actions, but the report does not clearly identify "this plan may be stale".

Required fix:

- Add lightweight plan freshness metadata, such as registry file hash and source file hash.
- Warn loudly or refuse apply if hashes differ.
- Add tests for applying a stale plan after registry mutation.

### 4. Sync plan JSON is treated as trusted internal input

`sync_plan_from_dict()` constructs dataclasses directly from JSON fields. Malformed or hand-edited plan JSON can produce low-level type errors rather than a user-quality CLI error.

Why it matters:

- Sync plans are files the user may inspect, move, or edit.
- A bad plan should fail with an actionable error: which file, what field, and how to regenerate.

Required fix:

- Add validation around plan JSON loading.
- Convert malformed plan errors into a clear CLI failure.
- Add adversarial tests for missing source/target/actions/conflicts fields.

## Medium-Priority Issues

### 1. `paper_workbench/cli.py` is too large for the current feature set

The CLI now contains many command groups and inline helpers across import/export/search/files/backup/migration/reading/drafts/sync. It still works, but future changes are likely to regress unrelated commands.

Recommendation:

- Split command registration into focused modules by command group after v1.3 blockers are fixed.
- Keep argparse, but move each group into a small `add_*_commands(parser)` function.

### 2. Historical reports are numerous and sometimes stale by design

The `reports/` directory contains release-readiness, hostile-review, patch-plan, stress, and workflow reports from many stages. This is useful for audit history, but an external user can easily confuse stale historical verdicts with the current release state.

Recommendation:

- Add a short "current report index" at the top of `reports/index.md`.
- Clearly separate current release artifacts from historical phase artifacts.

### 3. Documentation volume is high and overlapping

There are many pairs of uppercase workflow docs and docs-site lowercase equivalents. The coverage is strong, but it is hard to know which file is canonical.

Recommendation:

- Mark canonical docs in `docs/index.md`.
- Move older stage-specific docs into an archive section or link them as reference material.

### 4. Notebook coverage is structural, not executable

The notebook checker validates JSON and path hygiene. That is appropriate for a lightweight release check, but it does not prove notebooks run top-to-bottom in a clean environment.

Recommendation:

- Keep structural checks in CI.
- Add one optional manual or nightly notebook execution target for the smallest notebook set.

## Low-Priority Polish

- Several reports include stage-specific naming that makes the current state harder to scan.
- Some CLI help text is accurate but long; command groups would benefit from one-line workflow examples in docs rather than expanding help output further.
- Sync reports should show the source record identifier next to every action and conflict, not only target paper ID.
- The conflict report should group conflicts by source record and target paper for review ergonomics.
- `reports/audit_log_demo_v0_9.md` is tracked, but actual audit logs are ignored; the demo should stay clearly labelled synthetic.

## Missing Tests

Add tests for these release-relevant cases:

- Same DOI with different title produces a high-risk conflict and no field-fill actions for that source row.
- Same title with different DOI produces a high-risk conflict and no field-fill actions for that source row.
- Same BibTeX key with different DOI produces a high-risk conflict and no field-fill actions for that source row.
- Forced sync apply preserves all untouched registry fields and formatting.
- Forced sync apply refuses high-risk plans unless a separately named conflict override exists.
- Dry-run sync apply report uses "would apply" language.
- Stale sync plan detection after registry file changes.
- Malformed sync plan JSON fails with an actionable CLI error.
- Fresh Obsidian export round-trip behavior, either no false conflicts or explicitly documented one-way behavior.

## Documentation Mismatches

### Sync safety docs overpromise current behavior

`docs/SYNC.md` says forced applies "only create missing registry rows and fill blank fields" and "do not overwrite non-empty registry fields." That is incomplete because forced apply can still rewrite untouched row formatting through normalization.

`docs/SAFE_SYNC_WORKFLOW.md` says "Never use sync to overwrite notes or registry fields that contain user-entered data." The implementation currently can alter user-entered author formatting without a planned action.

`reports/release_readiness_v1_3.md` says v1.3 does not overwrite non-empty registry metadata. The scratch probe contradicts that at the file-output level.

### Obsidian round-trip docs need sharper boundaries

The generated Obsidian round-trip report shows immediate conflicts for a generated vault. The docs should state whether Obsidian export is a one-way readable vault export or a supported note round-trip source.

## CLI Usability Problems

- `sync apply --dry-run` reports "Applied actions" for a dry-run.
- `sync apply --force` is too broad: it means "write changes" and effectively "accept high-risk plan conflicts".
- Sync plan reports do not visually tie actions to conflict-bearing source records, making it hard to see when one import row generated both a conflict and applyable actions.
- Malformed sync plan JSON needs a better user-facing error path.

## Data-Safety Risks

No evidence of cloud, LLM, publisher scraping, copyrighted PDFs, tracked cache databases, tracked backup archives, or tracked `.paperwb` directories was found in the current tracked file list.

The primary data-safety risk is local data mutation:

- Sync apply can modify registry values not present in the plan.
- Sync apply can mutate a paper from a source record with a high-risk identity conflict.
- The current report language can make dry-run behavior look like actual application.

These are not theoretical release-polish issues. They affect user registry integrity.

## Overengineering Risks

- The project has accumulated many workflow modules and reports. The core value remains evidence tracking and auditability, but the expanding CLI surface is now hard to reason about.
- Sync conflict application should not grow into an automatic merge engine. The right v1.3 fix is stricter suppression/refusal, not smarter guessing.
- Obsidian round-trip should stay conservative. If exact round-trip is not feasible, document one-way export rather than adding fragile Markdown merge logic.

## Recommended Fix Sequence

1. Change sync planning so any source row with a high-risk identity conflict emits conflicts only and no applyable actions.
2. Change sync apply to operate on original registry CSV rows and update only explicitly planned fields.
3. Make real sync apply refuse high-risk-conflict plans unless a separate, deliberately named override is introduced.
4. Fix dry-run report wording.
5. Add the missing sync regression tests listed above.
6. Decide and document Obsidian round-trip semantics; add one regression test for that behavior.
7. Regenerate affected sync reports and release-readiness notes.
8. Re-run full pytest, notebook JSON validation, data-safety audit, and representative CLI smoke tests.

## Final Maintainer Position

The repository is close to an external-quality local research workbench, but the current v1.3 sync workflow is not safe enough to release. Fix the sync blockers before any public release candidate or external-user handoff.
