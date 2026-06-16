# Hostile Maintainer Review: Current Repository

Date: 2026-06-16

Scope: standalone release-gate review of the current Paper Intelligence
Workbench repository as if deciding whether this version is safe for local
dogfooding. I inspected package architecture, CLI behavior, stable versus
experimental surface docs, registry and BibTeX workflows, notes and claims,
evidence maps, manuscript and draft QA, reading sessions, imports and exports,
sync and conflict planning, search and indexing, backup/migration/integrity,
rule engine, dashboard, evidence graph, claim lifecycle, workflow runner,
review packets, tests, docs, notebooks, reports, synthetic data, data-safety
boundaries, `.gitignore`, and git status.

## Release Verdict

**Ready for cautious local dogfooding. Not ready to present as polished public
stable software without fixing the v2.4 review-packet first-use mismatch and
continuing release-hygiene cleanup.**

The core local-first workflows still work: package import succeeds, the CLI
entry point loads, the full test suite passes, notebook structure checks pass,
the data-safety audit reports no errors, and representative registry, BibTeX,
dashboard, graph, rules, workflow, manuscript QA, sync, import, backup, and
review-packet commands run without Python tracebacks.

The main release risk is now usability rather than data destruction. The
new `review-packet` workflow exports a `comments.csv` template that looks
ready to import, and the public docs show importing that path, but importing
the untouched template fails because blank comment/recommendation cells are
treated as row errors. A real reviewer who fills the file works fine; a new
user following the README too literally hits an avoidable failure.

## Validation Performed

- `git status --short --branch`: clean before this report was written; branch
  was `main...origin/main [ahead 27]`.
- `python -c "import paper_workbench; print(paper_workbench.__version__)"`:
  `2.4`.
- `paperwb --help`: passed and listed the stable and experimental command
  surface.
- `paperwb review-packet --help`, `paperwb workflow --help`,
  `paperwb graph --help`, `paperwb claim-review --help`, `paperwb rules --help`,
  and `paperwb sync --help`: passed.
- `paperwb validate-registry projects/zis_photocatalysis/registry.csv --strict`:
  passed with no findings.
- `paperwb validate-bib projects/zis_photocatalysis/bibtex/library.bib
  --registry projects/zis_photocatalysis/registry.csv --strict`: passed with one
  sparse synthetic-entry warning.
- `paperwb dashboard --project zis_photocatalysis --no-audit-log --out
  scratch/hostile_dashboard.md --force`: passed.
- `paperwb graph summary --project zis_photocatalysis --out
  scratch/hostile_graph_summary.md --force`: passed.
- `paperwb rules report --project zis_photocatalysis --out
  scratch/hostile_rules_report.md --force`: passed and reported expected
  synthetic evidence-gap findings.
- `paperwb workflow run daily_check --project zis_photocatalysis --dry-run
  --out scratch/hostile_workflow_daily.md --force`: passed, with expected
  synthetic fixture errors and warnings in the report.
- `paperwb manuscript qa drafts/synthetic_overconfident_section.md --project
  zis_photocatalysis --out scratch/hostile_manuscript_qa.md --force`: passed.
- `paperwb review-packet create --project zis_photocatalysis --theme
  photocorrosion --out scratch/hostile_review_packet --force`: passed; packet
  included 5 review items and no PDFs.
- `paperwb review-packet import-comments
  scratch/hostile_review_packet/comments.csv --project zis_photocatalysis
  --theme photocorrosion --dry-run --manifest
  scratch/hostile_review_packet/manifest.json --out
  scratch/hostile_comment_import.md --force-report`: failed as a user-facing
  validation failure because the generated template rows were blank.
- `python examples/review_packet_workflow.py`: passed with a populated synthetic
  reviewer comment.
- `paperwb integrity check --project zis_photocatalysis --out
  scratch/hostile_integrity.md --force`: passed and reported expected synthetic
  fixture gaps.
- `paperwb search photocorrosion --project zis_photocatalysis`: passed.
- `paperwb index status --project zis_photocatalysis`: passed and clearly
  reported a missing index.
- `paperwb backup create --project zis_photocatalysis --notes
  hostile-review-smoke`: passed; backup files were created under an ignored
  project-local backups folder and excluded PDFs/caches.
- `paperwb backup list --project zis_photocatalysis`: passed after backup
  creation and listed the new backup.
- `paperwb sync plan --project zis_photocatalysis --source
  data/examples/zotero_export.csv --source-type zotero-csv --out
  scratch/hostile_sync_plan.md --json-out scratch/hostile_sync_plan.json
  --force`: passed.
- `paperwb import zotero-csv data/examples/zotero_export.csv --project
  zis_photocatalysis --dry-run --report scratch/hostile_import_zotero.md
  --force`: passed.
- `python scripts/check_notebooks.py`: checked 8 notebooks successfully.
- `python scripts/data_safety_audit.py --out scratch/hostile_data_safety.md
  --strict`: checked repository files with 0 errors and historical local-path
  warnings.
- `python scripts/smoke_cli_workflow.py --quick`: 14 smoke steps, 0 failures.
- `python scripts/clean_room_install_check.py --out
  scratch/hostile_clean_room_check.md`: 16 release-check steps, 0 failures.
- `python -m pytest -q`: passed.
- `git ls-files` checks found no tracked PDFs, SQLite/cache databases,
  `.paperwb` sidecars, Python caches, build artifacts, backup archives, or egg
  metadata.
- `git tag --points-at HEAD`: no release tag at `HEAD`.

## Release Blockers

None found for cautious local dogfooding.

This is not a polished public-stable verdict. The repository is safe enough to
use locally on user-owned metadata and notes, but the high-priority issues
below should be fixed before advertising v2.4 review packets as a smooth
external-user workflow.

## High-Priority Issues

1. **The new review-packet import path fails on the generated comment
   template.**

   Evidence: `review-packet create` writes `comments.csv` rows for each review
   item with empty `comment` and `recommendation` fields. Importing that file
   immediately with `review-packet import-comments ... --dry-run` returns
   row-level errors for every generated item. The README, v2 CLI reference, and
   comment-import doc all show importing the packet `comments.csv` path without
   first making the "fill in at least one comment or recommendation" requirement
   explicit.

   Why it matters: this is the newest workflow and the first thing a supervisor
   review user will try. It does not corrupt data, but it makes the feature feel
   broken.

   Recommended fix: either skip untouched template rows as a no-op warning or
   update the docs and examples to say the reviewer must fill `comment` or
   `recommendation` before import. Add a regression test for the untouched
   template behavior whichever policy is chosen.

2. **The canonical dogfooding project still produces error-level findings in
   normal review and dashboard workflows.**

   Evidence: `workflow run daily_check`, `rules report`, `integrity check`, and
   the dashboard all surface intentional gaps such as missing claim evidence
   locations. The project is labelled as intentionally imperfect, but it is also
   the main project used in quickstarts, docs, examples, and smoke commands.

   Why it matters: intentional red flags are valuable for demos, but a new user
   needs one obvious green-path project where stable commands return clean
   results. Otherwise users cannot easily tell whether they installed the tool
   correctly or are seeing fixture-driven warnings.

   Recommended fix: keep `zis_photocatalysis` as the imperfect evidence-gap
   fixture, but add or designate a clean tiny project for installation and
   first-use validation. Avoid hiding the warnings; route first-time smoke docs
   to the green path.

3. **Data-safety warnings remain in historical reports and tests.**

   Evidence: the strict audit reports no errors, but still warns about
   historical local absolute-path strings in old release reports and tests.

   Why it matters: warnings are not blockers, but repeated historical local-path
   hits make it harder to spot new private path leaks during future release
   checks.

   Recommended fix: either sanitize old historical reports or explicitly add a
   documented allowlist for known historical warning files so new warnings stand
   out.

## Medium-Priority Issues

1. **`paper_workbench/cli.py` remains the architectural hotspot.**

   It is roughly 3,700 lines and still owns parser construction, dispatch,
   path handling, report writes, and adapters for nearly every subsystem.
   Existing tests are strong enough for dogfooding, but command changes are
   expensive to review.

2. **Several feature modules combine models, analysis, persistence, and
   Markdown rendering.**

   Larger modules include workflow, rules, authoring, index, reading, sync,
   graph, drafts, review packets, registry, and importers. This keeps runtime
   dependencies low, but increases regression risk as the project grows.

3. **Docs and reports are useful but noisy.**

   The repository now has more than 130 top-level docs pages and about 200
   reports. `reports/index.md` helps, but search results still mix current
   v2.4 guidance with historical v0.x/v1.x/v2.0rc artifacts.

4. **Notebook coverage lags behind the current feature surface.**

   Eight notebooks validate structurally. Newer graph, claim lifecycle,
   workflow-runner, dogfood, sync, and review-packet workflows are covered by
   tests, examples, docs, and reports rather than notebooks.

5. **Strict validation semantics remain a scripting footgun.**

   `validate-bib --strict` exits successfully for warnings. That is reasonable
   if "strict" means "errors fail"; it is surprising if users expect warnings
   to fail CI. The docs should keep spelling this out.

6. **Review comments are not yet connected to the broader review lifecycle.**

   Imported comments are safely isolated, but response/follow-up reports do not
   yet integrate with claim lifecycle queues or follow-up action state. This is
   acceptable for v2.4 experimental status.

## Low-Priority Polish

- `paperwb --help` is accurate but dense because the command surface is now
  very broad.
- `integrity` requires an explicit `check` subcommand; users may try the shorter
  mental model first.
- Public demo folder names include `real`, even though committed contents are
  synthetic placeholders. The embedded warnings are good; the name can still
  confuse quick scans.
- Some command examples write to `scratch/`, while project-profile commands
  default to project report folders; this is safe but inconsistent for first
  users.
- Historical version labels remain part of archived report filenames and docs;
  this is acceptable but requires users to prefer `*_V2` docs and
  `reports/index.md`.

## Data-Safety Risks

- Strict data-safety audit result during review: 0 errors, historical path
  warnings only.
- No tracked PDFs, SQLite databases, `.paperwb` sidecars, backup archives,
  Python caches, build artifacts, or egg metadata were found.
- The committed dogfood demo uses synthetic placeholder filenames and BibTeX
  keys. The report explicitly warns that private real plans must not be
  committed.
- Local smoke checks created ignored scratch outputs, audit sidecars, and a
  project-local backup. They are ignored by Git and were not staged.
- The data-safety boundary remains sound: no cloud APIs, no LLM APIs, no
  scraping, no PDF copying by default, and no fabricated real metadata in
  committed examples.

## Docs Mismatches

- README and v2 CLI/comment-import docs show importing the generated review
  packet `comments.csv`, but do not make clear that untouched template rows are
  invalid until a reviewer fills `comment` or `recommendation`.
- The v2 docs honestly classify review packets, workflow recipes, graph,
  claim lifecycle, sync apply, backup/restore/migration, indexed search, and
  manuscript QA as experimental or safety-sensitive.
- `reports/index.md` correctly marks current v2.4 release reports, but the
  report directory still contains many historical files that can look current
  when opened directly.

## CLI Usability Issues

- The new review-packet import dry-run failure on untouched templates is the
  clearest usability problem.
- Top-level help is comprehensive but intimidating.
- Advanced write-capable commands are visible from top-level help before a user
  has read safety docs.
- `workflow run daily_check` returning a report with error-level findings can
  look like a failed installation unless users understand the intentionally
  imperfect fixture.
- Some commands use `--out`; import commands use `--report`; backup create uses
  `--backups-dir`. The inconsistency is manageable, but it raises support cost.

## Overengineering Risks

- The product now includes registry/BibTeX validation, structured notes, claim
  extraction, evidence maps, manuscript QA, authoring packets, reading sessions,
  import/export, sync planning, local files, indexing, backups, migration,
  integrity, audit logs, rules, dashboard, templates, dogfood scaffolds, graph,
  claim lifecycle, workflow recipes, and review packets.
- The next patch should not add another subsystem unless it directly improves
  performance, maintainability, or first-use clarity.
- Avoid graph databases, embeddings, cloud sync, web apps, plugin marketplaces,
  automatic contradiction inference, automatic review-comment application, and
  default PDF full-text extraction.

## Stale Generated Reports

- `reports/index.md` indexes about 200 Markdown reports and correctly puts the
  current v2.4 reports first.
- Historical reports remain useful audit trail artifacts but should not be used
  as current docs.
- `hostile_review_latest.md` is the canonical current review; versioned hostile
  reviews are intentionally omitted from the report index.
- Current v2.4 generated reports exist for review-packet import, reviewer
  comments, response to review, follow-ups, release readiness, and the v2.5
  patch plan.

## Missing Tests

- Untouched review-packet `comments.csv` template import behavior.
- Docs/example regression that prevents README from showing a command sequence
  that fails immediately on generated artifacts.
- Draft-specific review-packet creation smoke test.
- Green-path synthetic project where stable validation, dashboard, and workflow
  checks produce no error-level findings.
- Data-safety warning allowlist or regression that distinguishes historical
  accepted warnings from new private-path leaks.
- Optional notebook coverage for v2.4 review packets; the example script is
  useful but notebooks are older.

## Recommended Blocker-Fix Sequence

No local-dogfooding release blockers were found. Recommended high-priority fix
sequence:

1. Fix or document untouched review-packet template import behavior; add a test.
2. Patch README, `docs/CLI_REFERENCE_V2.md`, and `docs/COMMENT_IMPORT.md` so
   the review-packet workflow says reviewers must add comment/recommendation
   content before import, unless the importer is changed to skip blank rows.
3. Add a clean green-path synthetic project or redirect first-use smoke docs to
   a clean template-created project.
4. Decide whether historical local-path warnings should be sanitized or
   allowlisted.
5. Keep v2.5 focused on performance/cache hygiene and maintainability, not new
   product surface.
