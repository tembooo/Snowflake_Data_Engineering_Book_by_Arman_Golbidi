# Chapter 12 Lab — Query Performance and Warehouse Optimization

All contents are original teaching artifacts. The fixture is synthetic, not Finnish
energy telemetry. The numeric values cannot justify a Snowflake speed claim.

## Offline (no database)
1. `python offline_validate.py`
2. `python -m unittest discover -v` (16 standard-library tests).

## Optional, authorised Snowflake route
1. Ask an owner to provision an isolated warehouse, database BOOK_DEV and schema
   CH12_LAB and approve expected compute cost. This repository creates neither
   account roles nor the warehouse. Confirm no existing ENERGY_FACT table before
   running the replacement DDL in `optional_setup.sql`.
2. Review and run `optional_setup.sql` in the approved disposable schema.
3. Confirm 42 rows, total 462.000 MWh and a six-row 4 October answer at 66 MWh.
4. Execute both alternatives in `benchmark_queries.sql`; alternate sequence;
   capture query IDs and relevant Snowsight/Query Profile fields.
5. Compare actual latencies, waits, partition scan and metering in
   `tuning_report.md` and re-check correctness.
6. Reset session overrides, verify object ownership and review commented cleanup.

Important: Accounts, editions, regions, privileges, pricing and metadata delays
vary. Source repositories from the author's 181-project directory are references,
not executed dependencies and do not grant book-republication rights.

## File manifest
- `energy_sample.csv`: six independent source observations, 66.000 MWh.
- `energy_7day_fixture.csv`: exact deterministic expansion, 42 rows, 462.000 MWh.
- `benchmark_results.csv`: **invented illustrative timing inputs**. Credits blank.
- `benchmark_queries.sql`: two comparable query variants.
- `read_only_diagnostics.sql`: account-wide diagnostics, needs monitoring grants.
- `optional_setup.sql`, `optional_cleanup.sql`: review before any execution.
- `offline_validate.py`, `test_lab.py`: real local correctness/statistics checks.
- `tuning_report.md`: template separating observations from assumptions.
