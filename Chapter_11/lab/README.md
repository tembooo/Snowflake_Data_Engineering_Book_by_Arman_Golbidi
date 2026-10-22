# Snowflake Data Engineering — Chapter 11 companion

Original accompanying teaching artifacts. **Synthetic data only. No Snowflake or Power BI account was accessed or tested.**

## Run without Snowflake / Power BI
```bash
cd lab
python metrics.py
python -m unittest discover -s tests -v
```
Requirements: Python 3.10+; standard library only. Outputs: `outputs/metrics_validation.json` and terminal test logs. Fixture sourced exactly from Chapter 10's approved synthetic `gold_energy.csv`, supplemented by one separately labelled **synthetic consumption** record. No cloud credentials or spend required.

## Cloud implementation
Review `sql/serving_views.sql`, `powerbi_report/snowflake_connection.pq`, and `powerbi_report/measures.dax`. These are explanatory or setup templates only, not integration-tested code. Confirm connector versions, role grants, data residency, source refresh timing, licensing, BI workspace permissions, query folding and query costs. Use a restricted BI-only warehouse and turn on auto-suspend. Avoid sharing credentials.

Source reference status: GitHub external repositories P121–P134 referenced in the book are learning references, not executed or licensed for republishing here. Architecture and diagrams here are original.

## Official documentation to re-check before publication
- Snowflake Power Query connector: https://learn.microsoft.com/en-us/power-query/connectors/snowflake
- Power BI DirectQuery: https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-directquery-about
- Query folding: https://learn.microsoft.com/en-us/power-bi/guidance/power-query-folding
- Snowflake/Power BI service and SSO: https://learn.microsoft.com/en-us/power-bi/connect-data/service-connect-snowflake
- Snowflake Query Profile: https://docs.snowflake.com/en/user-guide/ui-query-profile
