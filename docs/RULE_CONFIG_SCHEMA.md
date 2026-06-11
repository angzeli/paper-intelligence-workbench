# Rule Config Schema

Rule config files are local JSON files.

Top-level fields:

| Field | Required | Description |
| --- | --- | --- |
| `version` | no | Schema/version label. Current examples use `1.5`. |
| `name` | no | Human-readable rule set name. |
| `rules` | yes | List of rule objects. |

Rule fields:

| Field | Required | Description |
| --- | --- | --- |
| `rule_id` | yes | Stable unique rule ID. |
| `name` | yes | Human-readable name. |
| `description` | no | Longer explanation. |
| `target` | yes | One of the supported targets. |
| `severity` | yes | `info`, `warning`, or `error`. |
| `enabled` | no | Boolean, defaults to true. |
| `condition` | yes | Declarative condition object. |
| `message` | no | User-facing finding message template. |
| `suggested_action` | no | Suggested local follow-up. |
| `tags` | no | Tags for grouping rules. |
| `project_scope` | no | Documentation-only project label. |

Message templates may use simple placeholders such as:

- `{identifier}`
- `{field}`
- `{value}`
- `{count}`
- `{minimum}`
- `{maximum}`
- `{citation_key}`
- `{paragraph_id}`

Unsupported condition types are reported as config errors. They are not
executed.

Numeric condition fields must be whole numbers:

- `min` or `minimum` for `min_count`
- `max` or `maximum` for `max_count`
- `min_papers` for `theme_min_papers`
- `min_strong_claims` for `theme_min_strong_claims`

`where_equals` comparisons are normalized for JSON booleans, numeric values,
empty values, and case-insensitive strings. This allows JSON `true` to match a
CSV registry value of `true` without requiring users to quote boolean filters.
