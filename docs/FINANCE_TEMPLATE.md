# Finance Template

The finance template is for organizing valuation and finance reading. It is
not investment advice and does not recommend securities, trades, or strategies.

## Themes

- valuation
- financial statements
- profitability
- leverage
- cash flow
- market cycles
- risk
- behavioral finance
- macro

## Rule Examples

- Included papers should have BibTeX keys.
- Read papers should have notes.
- Finance papers included in a review should be at least partially read.
- Strong claims should have local evidence locations.

## Recommended Workflow

```bash
paperwb template create finance --project my_finance_reading
paperwb dashboard --project my_finance_reading --no-audit-log
paperwb reading queue --project my_finance_reading
```

Use the project to track reading and evidence. Do not treat generated reports
as investment recommendations.
