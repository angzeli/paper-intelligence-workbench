# Compatibility Matrix v3.2

This matrix documents which historical local workspace shapes are inspectable, migratable, or require manual review.

| Source workspace | Supported | Inspectable | Migratable | Requires backup | Manual review | Tests | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| legacy data/ workflow | yes | yes | yes, to project profile | yes | if malformed or partially migrated | tests/test_compatibility_v3_2.py | Reports and caches are not copied by default. |
| early project profile without project.json | yes | yes | not needed | no | if required files are missing | tests/test_compatibility_v3_2.py | Loaded through project-root defaults. |
| pre-v2 registry schema | yes | yes | copy-preserved | yes for migration | if extra or missing columns exist | tests/test_compatibility_v3_2.py | Current loaders ignore unknown columns; migration copies raw CSV. |
| v2.0rc dogfood workspace | yes | yes | not needed | no | no, unless user data is incomplete | tests/test_compatibility_v3_2.py | Empty scaffolds are valid and should explain missing data clearly. |
| v3.0rc project workspace | yes | yes | not needed | no | no for clean projects | tests/test_compatibility_v3_2.py | Advanced sidecars remain experimental. |
| malformed missing registry | partial | yes | no | n/a | yes | tests/test_compatibility_v3_2.py | User must create or recover a registry first. |
| malformed broken notes | partial | yes | not until repaired | yes if migrating | yes | tests/test_compatibility_v3_2.py | Notes are reported with parser warnings; claims are not invented. |
| partial migration conflict | partial | yes | blocked until target chosen | yes | yes | tests/test_compatibility_v3_2.py | Existing project targets are never overwritten silently. |
| workspace with extra registry columns | yes | yes | copy-preserved | yes for migration | yes | tests/test_compatibility_v3_2.py | Extra columns are not interpreted but should be preserved by copy-based migration. |

## Policy

- Inspect before migrating.
- Dry-run before forced migration.
- Preserve extra user columns by copying raw registries where possible.
- Never overwrite existing project targets without an explicit future safety-reviewed force workflow.
