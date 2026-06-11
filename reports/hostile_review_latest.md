# Hostile Maintainer Review: v1.5 Current Repository

Date: 2026-06-11

## Release Verdict

Do not cut a broad external v1.5 release until the high-priority rule-engine defects below are fixed.

I did not find a release-blocking data-loss issue, unsafe overwrite path, tracked copyrighted content, tracked cache database, tracked backup archive, or cloud/LLM dependency. The package imports, the CLI is discoverable, the full test suite passes, notebook JSON validation passes, and the data-safety audit reports no errors.

The current risk is narrower but still important: the new v1.5 custom rule system can certify invalid rule configs, silently miss natural JSON boolean filters, and double-count manuscript unknown-citation findings. Because v1.5 is specifically about custom validation, those are high-priority release issues even though they fail non-destructively.

## Review Scope

Inspected:

- package metadata and package layout
- CLI command surface, including `paperwb rules`
- project profiles and synthetic projects
- registry, BibTeX, note parsing, claim extraction, evidence maps, citation audits, authoring reports, draft/manuscript audit, local search/indexing, local files, imports/exports, sync, backups, migrations, reading sessions, safety utilities, and rule-engine integration
- tests, CI workflow, smoke scripts, and notebook checkers
- README, docs-site pages, detailed docs, generated reports, and release-readiness notes
- synthetic data and tracked-file hygiene

Validation and probes run:

- `git status --short --branch --ignored=matching`
- `python -m pytest -q`
- `python -m pytest --collect-only -q`
- `python scripts/validate_notebooks.py`
- `python scripts/check_notebooks.py`
- `python scripts/data_safety_audit.py --out <scratch>/paperwb_hostile_data_safety.md --strict`
- `python -m paper_workbench.cli --help`
- `python -m paper_workbench.cli rules --help`
- `python -m paper_workbench.cli rules validate-config --help`
- `python -m paper_workbench.cli rules run --help`
- `python -m paper_workbench.cli rules list --project zis_photocatalysis --builtins`
- `python -m paper_workbench.cli rules validate-config --project zis_photocatalysis --strict`
- `python -m paper_workbench.cli rules run --project zis_photocatalysis --no-builtins`
- `python -m paper_workbench.cli rules report --project zis_photocatalysis --out <scratch>/rules_report.md --force`
- rule-engine probes with invalid numeric thresholds, JSON boolean `where_equals`, and manuscript unknown-citation rules
- overwrite refusal probes for rule reports
- missing-project failure probes
- tracked-file hygiene probes with `git ls-files`

Observed validation results:

- Full pytest passed.
- Pytest collection found 216 tests.
- Notebook structural validation passed for 8 notebooks.
- Data-safety audit checked 540 repository files with 0 errors and 7 existing absolute-path warnings in historical reports/tests.
- No tracked PDFs, SQLite/cache databases, `.paperwb` directories, Python caches, backup archives, audit logs, or obvious secrets were found by tracked-file probes.

## Release Blockers

No immediate release-blocking data-loss, destructive migration, unsafe restore, or tracked copyrighted-content issue was found.

This is not a clean v1.5 release verdict. The high-priority issues below should be fixed before advertising custom rules as reliable external-user functionality.

## High-Priority Issues

### 1. `rules validate-config` accepts numeric thresholds that later crash at runtime

Evidence:

- A JSON rule with `theme_min_papers` and `"min_papers": "abc"` was accepted by `paperwb rules validate-config ... --strict` as valid.
- Running the same rule with `paperwb rules run ... --no-builtins` failed with the raw Python message `invalid literal for int() with base 10: 'abc'`.
- `paper_workbench/rules.py:466-514` validates required fields, regex shape, and strength thresholds, but not integer fields.
- `paper_workbench/rules.py:593-600`, `paper_workbench/rules.py:649-655`, and `paper_workbench/rules.py:659-665` cast rule values with `int(...)` during execution.

Why this matters:

- v1.5 promises safe declarative rules and explicit config validation.
- A config validator that certifies invalid configs undermines the main v1.5 feature.
- The runtime failure is non-destructive, but the error quality is poor and not actionable.

Required fix:

- Validate integer fields for `min_count`, `max_count`, `theme_min_papers`, and `theme_min_strong_claims`.
- Return structured rule config findings with suggested actions instead of allowing `ValueError` from `int(...)`.
- Add tests for invalid numeric values in both `validate-config` and `rules run`.

### 2. JSON boolean filters silently fail to match registry fields

Evidence:

- A rule using `"where_field": "included_in_lit_review"` and `"where_equals": true` returned `No rule findings.`
- The same rule using `"where_equals": "true"` returned the expected findings.
- `paper_workbench/rules.py:690-699` compares `str(field_value) == str(expected)`, so registry string values like `true` do not match JSON boolean values like `True`.

Why this matters:

- Rule files are JSON. Users will naturally write booleans as `true` and `false`.
- Silent false negatives are more dangerous than visible validation errors because users can trust a clean report that missed real problems.
- This affects project-specific registry, note, claim, and workspace filters anywhere `where_equals` is used.

Required fix:

- Normalize comparison values consistently for booleans, numbers, strings, and empty values.
- Document the comparison behavior.
- Add regression tests proving JSON `true` and string `"true"` match the same registry data.

### 3. Manuscript unknown-citation rule double-counts the same missing citation key

Evidence:

- Running the ZIS project rule set against `drafts/synthetic_unknown_citations.md` reported each missing citation key twice.
- The duplicate rows come from separate manuscript findings for `citation_key_not_in_bibtex` and `citation_key_not_in_registry`.
- `paper_workbench/rules.py:669-687` maps both finding codes directly into configured rule findings without deduplicating by citation key and paragraph.

Why this matters:

- Unknown citations are exactly the kind of manuscript issue users will want project rules to catch.
- Duplicated findings inflate error counts and make rule reports look worse than the underlying manuscript audit.
- This also makes `--strict` output noisier and less trustworthy.

Required fix:

- Deduplicate configured manuscript unknown-citation findings by `(citation_key, paragraph_id)`.
- Keep a message that explains the key may be missing from BibTeX, registry, or both.
- Add tests for a draft with unknown citations proving one configured-rule finding per key/paragraph.

## Medium-Priority Issues

### 1. `import_export` is accepted as a rule target but has no real context records

Evidence:

- `RuleCategory.IMPORT_EXPORT = "import_export"` is present in `paper_workbench/rules.py:40-50`.
- `RULE_TARGETS` therefore accepts `import_export` configs.
- `_items_for_target` in `paper_workbench/rules.py:546-558` never returns import/export records.
- `docs/CUSTOM_RULES.md:33-43` omits `import_export` from the supported-target list.

Why this matters:

- The v1.5 product scope said imports/exports should be configurable rule targets.
- Current behavior is ambiguous: the target is accepted internally but not documented, and most item-level rules operate on an empty target set.

Recommendation:

- Either implement import/export context records or remove the target from `RULE_TARGETS`.
- If it remains experimental, document that clearly and make `validate-config` warn when item-level rule types target `import_export`.

### 2. `rules validate-config` uses a different explicit-file interface than other rule commands

Evidence:

- `rules list`, `rules run`, `rules report`, and `rules explain` accept `--rules-file`.
- `rules validate-config` only accepts a positional `[rules_file]`.
- `paperwb rules validate-config --project zis_photocatalysis --rules-file ...` fails with `unrecognized arguments: --rules-file`.
- Docs say to pass `--rules-file` for explicit rule configs, which is not true for validation.

Why this matters:

- Users will validate a rule file before running it. The command that should be safest is the one with the least consistent interface.
- This is not a data-safety issue, but it is a CLI contract mismatch.

Recommendation:

- Add `--rules-file` to `rules validate-config` as an alias while preserving the positional argument.
- Add a CLI contract test for both forms.

### 3. Rule reports can still be noisy because built-in adapters overlap

Evidence:

- Built-in rule findings adapt registry validation, citation audit, evidence-map coverage, workspace health, and optional manuscript QA.
- These layers can report related conditions with different IDs, even after basic finding deduplication.

Why this matters:

- Rule reports should help users prioritize work.
- Overlapping built-ins can make one underlying problem appear as several independent issues.

Recommendation:

- Add optional category/severity filters or a summary grouped by paper/theme/claim.
- Keep raw rows available, but make the first report section less noisy.

### 4. Historical data-safety warnings remain in release artifacts

Evidence:

- The strict data-safety audit reported 0 errors and 7 warnings for absolute local paths in historical reports/tests.
- Those are not tracked-file blockers, but they are release-hygiene debt.

Recommendation:

- Redact or archive historical reports that contain machine-specific paths.
- Keep tests that intentionally mention local path patterns, but ensure report-facing artifacts do not leak real machine paths.

### 5. Notebook coverage no longer reflects the full feature set

The notebook checker validates 8 notebooks, but the repo now includes draft/manuscript QA, reading sessions, sync, local files, backups, and rules. Some of those workflows are covered by scripts and tests, but a new external user may expect notebook walkthroughs to cover current headline features.

Recommendation:

- Either label notebooks as historical examples or add current notebooks selectively for manuscript QA and custom rules.
- Avoid adding notebooks for every feature if scripts are a better maintenance surface.

## Low-Priority Polish

- `default_rule_file(root, project="")` currently returns `rules.json` in both branches; the unused `project` argument is confusing.
- `paper_workbench/cli.py` remains very large, and `paper_workbench/rules.py` is now another large module. Both are manageable today, but future feature work should split command handlers and rule evaluators.
- The reports directory contains many historical stage reports. This is useful audit history but overwhelming for external users.
- Docs have both lowercase docs-site pages and uppercase detailed pages, which is workable but not always obviously canonical.
- `rules explain` is useful for configured rules and built-ins, but it does not explain rule type schemas such as required condition fields.

## Missing Tests

- Invalid numeric rule config tests for `min_count`, `max_count`, `theme_min_papers`, and `theme_min_strong_claims`.
- CLI failure-path tests proving invalid numeric rule configs return structured config findings rather than raw Python conversion errors.
- JSON boolean `where_equals` tests for registry fields such as `included_in_lit_review`.
- Manuscript unknown-citation rule deduplication tests.
- `rules validate-config --rules-file ...` alias tests if that interface is added.
- Tests clarifying whether `import_export` is supported, rejected, or experimental.
- Rule report regression assertions for configured manuscript rules and project-specific rule sets.

## Documentation Mismatches

- `docs/CUSTOM_RULES.md` omits the accepted `import_export` target, while code accepts it.
- `docs/CLI_REFERENCE.md` and related rule docs imply explicit rule files use `--rules-file`, but `rules validate-config` does not support that flag.
- Rule docs do not describe type coercion for `where_equals`, which is currently important because JSON booleans and CSV strings behave differently.
- Rule docs list rule types but do not provide a concise field schema per type.
- Release-readiness reports say v1.5 rule configs validate, but they do not mention the numeric-validation blind spot found here.

## CLI Usability Problems

- Invalid numeric rule configs fail at runtime with a Python conversion message instead of a rule-specific diagnostic.
- `rules validate-config` has an inconsistent explicit-file interface compared with the rest of the `rules` group.
- `rules run --strict` can return duplicated configured manuscript findings for one unknown citation.
- `rules report` overwrite protection works correctly, but the default report name can be easy to overwrite intentionally with `--force`; keep that behavior but ensure reports say exactly which rule file was used.

## Data-Safety Risks

- No tracked PDFs, SQLite/cache databases, `.paperwb` directories, Python caches, backup archives, audit logs, or obvious secrets were found in tracked files.
- The strict data-safety audit reported 0 errors and 7 warnings for absolute local paths in historical reports/tests.
- Rule config execution is data-only and does not execute arbitrary Python code. That boundary appears intact.
- The main current data-safety risk is indirect: users may trust a clean rule report that missed issues because of JSON boolean filter false negatives.

## Overengineering Risks

- The project has many feature surfaces for a zero-dependency local CLI. v1.5 adds another cross-cutting abstraction on top of already broad validators.
- The rule engine should stay declarative. Do not add expression evaluation or arbitrary plugin code.
- Built-in rule adapters should not become a second, divergent validation system. Keep them thin or route existing validators through structured findings.
- Adding every possible target before context records exist will make the rule surface look broader than it is.

## Recommended Fix Sequence

1. Add rule-config numeric validation and convert runtime numeric parsing failures into structured config findings.
2. Normalize `where_equals` comparisons so JSON booleans match equivalent CSV/string values.
3. Deduplicate `manuscript_no_unknown_citations` findings by citation key and paragraph.
4. Decide whether `import_export` is supported in v1.5; either implement context records or reject/warn in config validation.
5. Add `--rules-file` as a non-breaking alias for `rules validate-config`, then update CLI contract tests.
6. Update rule docs with target support, condition schemas, and comparison semantics.
7. Regenerate affected v1.5 reports after the fixes and keep historical path warnings out of current release-facing reports.
