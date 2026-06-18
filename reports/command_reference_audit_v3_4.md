# Command Reference Audit v3.4

## Source Of Truth

`paperwb --help` and `paperwb COMMAND --help` remain the source of truth for
exact flags. v3.4 adds a grouped user-facing command map at
`docs/command-reference/index.md`.

## Top-Level Commands Observed

```text
init
project
template
dogfood
support
compatibility
workflow
review-packet
validate-registry
validate-bib
import
sync
add-paper
list
note-template
claims
claim-review
contradictions
search
index
rebuild
files
report
dashboard
graph
rules
writing-packet
checklist
draft
manuscript
reading
followups
doctor
integrity
audit-log
backup
migrate
export
synthetic
```

## Stable Groups Documented

- `init`
- `project`
- `template`
- `dogfood`
- `validate-registry`
- `validate-bib`
- `add-paper`
- `list`
- `note-template`
- `claims`
- `report`
- `checklist`
- `doctor`
- `dashboard`
- `support`
- `compatibility`

## Experimental Or Safety-Sensitive Groups Documented

- `workflow`
- `review-packet`
- `import`
- `sync`
- `search --indexed`
- `index`
- `rebuild`
- `files`
- `draft`
- `manuscript`
- `reading`
- `followups`
- `graph`
- `rules`
- `backup`
- `migrate`
- `audit-log`
- `claim-review`
- `contradictions`

## Automated Check

`scripts/check_docs.py` now parses README and `docs/**/*.md` for `paperwb`
command examples and verifies that referenced top-level commands exist in the
actual CLI help output.

## Result

- `python scripts/check_docs.py`: passed.
- No missing linked docs were found.
- No unknown top-level `paperwb` command examples were found.
- No raw absolute-path patterns were found in README or docs.
