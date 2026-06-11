# Custom Rules

Custom rules are JSON objects under a top-level `rules` list.

Example:

```json
{
  "version": "1.5",
  "name": "Example project rules",
  "rules": [
    {
      "rule_id": "example.claims.need_locations",
      "name": "Strong claims need locations",
      "target": "claim",
      "severity": "error",
      "enabled": true,
      "condition": {
        "type": "required_field",
        "field": "section",
        "where_field": "strength",
        "where_equals": "strong"
      },
      "message": "Strong claim {identifier} is missing a section/page evidence location.",
      "suggested_action": "Add a section, page, figure, table, or appendix location."
    }
  ]
}
```

Rules are read-only. Use reports to decide what to fix manually.

## Supported Targets

- `registry`
- `bibtex`
- `note`
- `claim`
- `theme`
- `manuscript`
- `project`
- `file`
- `workspace`

## Supported Rule Types

- `required_field`
- `allowed_values`
- `regex_match`
- `min_count`
- `max_count`
- `contains_tag`
- `missing_note_for_status`
- `claim_strength_threshold`
- `evidence_type_required`
- `citation_key_required`
- `theme_min_papers`
- `theme_min_strong_claims`
- `manuscript_no_unknown_citations`

Validate every rules file before relying on it:

```bash
paperwb rules validate-config --project zis_photocatalysis --strict
```

