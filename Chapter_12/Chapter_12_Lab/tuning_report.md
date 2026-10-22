# Chapter 12 — Energy query tuning report (template)

**Status:** Offline correctness oracle validated. No live Snowflake benchmark has been run.

## Input and correctness
- Synthetic six-technology seed for one UTC interval: 6 rows; 66.000 MWh.
- Synthetic seven-day fixture: 42 rows; 462.000 MWh.
- Candidate date filters must agree on six keyed rows and 66.000 MWh for 2026-10-04.
- Synthetic example latencies in `benchmark_results.csv` are **illustrative inventions**,
  not an observed Snowflake latency or credit measurement.

## Real benchmark form (fill only after an authorised run)
| Field | Evidence |
|---|---|
| Date / time / account region | NOT MEASURED |
| Edition / warehouse / role / size | NOT MEASURED |
| Table snapshot and row count | NOT MEASURED |
| Query IDs per treatment | NOT MEASURED |
| Result equality proof | Offline only |
| Baseline median / p95 | NOT MEASURED |
| Candidate median / p95 | NOT MEASURED |
| Partitions scanned and spilled bytes | NOT MEASURED |
| Queue and compilation time | NOT MEASURED |
| Warehouse metering and paid service credits | NOT MEASURED |
| Deployment decision | DEFER until live evidence |

## Proposed decision
Try a correctness-preserving half-open timestamp predicate before changing warehouse
size or enabling clustering/search optimisation. Test and record query profiles under
matched conditions. Include maintenance and idle compute in any business case.

## Risk and cleanup
Use a disposable table in an owner-approved schema, an isolated small warehouse,
a limited role, explicit budget and manual cleanup. Do not run load tests in production.
