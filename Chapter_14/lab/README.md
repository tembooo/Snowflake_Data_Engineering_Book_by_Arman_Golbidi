# Chapter 14 Companion Lab — Offline, Safe by Default

**Book:** *Snowflake Data Engineering: From Fundamentals to Production-Ready Data Pipelines*, Chapter 14.
**Author:** Arman Golbidi. **Release label:** chapter14-draft-2026-10-22.

This is an original, Python-standard-library-only baseline lab demonstrating chronological splitting, naive forecasting, outlier testing, and reproducible evaluation. It is **not** a live Cortex experiment and does not need Snowflake credentials.

## Reproduce

From this directory, with Python 3.10+:

```bash
python ml_baseline.py
python -m unittest discover -s tests -v
```

The first command regenerates `data/synthetic_daily_energy.csv` and prints the evaluation summary. The generated JSON result is included as a verified reference snapshot in `data/baseline_results.json`. The second command runs 16 unit tests. No third-party packages, accounts or internet are needed.

## Expected observations

- 35 synthetic, contiguous UTC dates, 2026-01-01 through 2026-02-04.
- Training/validation/test counts: 21/7/7.
- Seasonal lag-7 test MAE 1.0643 MWh; lag-1 MAE 3.2500 MWh.
- Threshold 0.8500 MWh from validation residuals; test index 34 flagged.
- 16 unit tests pass; failed data validation is tested for duplicate dates, non-finite or negative amounts and unexpected provenance.

## Why the numbers cannot be generalized

The series is hand-generated with a weekly pattern and single injected spike. It is not sampled from real Finnish grid data, cannot establish a model's production accuracy, and should never be used for physical safety/operations. The 66.000 MWh fixture from preceding chapters is a separate synthetic reconciliation case.

## Optional AI extension

`sql/optional_ai.sql` holds **only commented** billable examples. Before enabling any AI call, verify account region, cross-region routing, model allow-list, `CORTEX_USER` / model RBAC, feature availability, privacy approval, owner budget, token count and actual cost attribution. Never put real customer or operator data in prompts without a lawful, approved basis.

A human reviewer can use `data/ai_eval_cases.csv` to design a labelled evaluation set. These are expected-behaviour descriptions, not actual model scores.

## Cleanup

Local-only outputs can be regenerated or deleted. No SQL objects are created by default and no live account cleanup should be necessary.

## External teaching leads

The manuscript cites Snowflake-Labs guides from the author-provided 181-project index. Their code was neither copied into this lab nor executed; licensing, exact commits and cloud requirements must be reviewed before republication.
