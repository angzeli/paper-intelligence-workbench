# Finance Template Overview

This template is a synthetic scaffold for finance and valuation reading. It
organizes reading and evidence only. It is not investment advice and contains
no real company, security, or paper metadata.

## Included Themes

| Theme | Purpose |
| --- | --- |
| valuation | Track DCF, multiples, and valuation-method evidence |
| financial-statements | Track accounting and statement-analysis evidence |
| profitability | Track margins, ROIC, and earnings-quality evidence |
| leverage | Track debt, coverage, and capital-structure evidence |
| cash-flow | Track free-cash-flow, working-capital, and capex evidence |
| market-cycles | Track cycle, liquidity, and regime context |
| risk | Track scenario, drawdown, and risk evidence |
| behavioral-finance | Track bias, sentiment, and behavior evidence |
| macro | Track rates, inflation, and macro context |

## Included Rule Examples

- Included papers should have BibTeX keys.
- Read papers should have structured notes.
- Included finance readings should be at least partially read.
- Strong claims should have page or section evidence.

## First Workflow

```bash
paperwb template create finance --project my_finance_reading
paperwb dashboard --project my_finance_reading --no-audit-log
paperwb reading queue --project my_finance_reading
```

Generated reports are reading aids only and must not be interpreted as
investment recommendations.
