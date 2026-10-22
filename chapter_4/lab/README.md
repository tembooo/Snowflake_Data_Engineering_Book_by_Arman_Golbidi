# Chapter 4 — Snowflake SQL and Data Modeling Lab

Original companion material to *Snowflake Data Engineering* (Chapter 4), Arman Golbidi.
All input data are synthetic. This lab is not affiliated with or approved by Snowflake.

## 1. Offline verification (no account or cloud charges)

```bash
python validate_fixture.py
python -m unittest discover -s tests -v
```

Expected output from validator: raw_rows=7; accepted_rows=6; accepted_mwh=97.500; corrected_raw_id=7. The unit tests include negative and invalid-input probes.

## 2. Snowflake live run — NOT YET EXECUTED BY THE AUTHORING SYSTEM

Prerequisites: an authorized *nonproduction* Snowflake account with a dedicated training database, a precreated disposable `BOOK_CH04` schema in that database and a small warehouse with auto-suspend. The operator must have explicit authorization to create/replace objects in the schema. **Never use ACCOUNTADMIN for ordinary operation.**

1. Review `sql/model.sql`, especially every `CREATE OR REPLACE` statement. Run its first `SELECT` and verify the current context. Do not continue if it points to production or a non-disposable database.
2. Run the model statements using the approved lab role. No external files or tokens are required.
3. Run every file in `sql-tests/`; **each must return zero rows**.
4. Confirm `COUNT(*)=6` and `SUM(energy_mwh)=97.500`.
5. Capture actual query IDs, edition/region, warehouse size, consumption observations, SQL version and test outputs in a run log. Do not report expected outputs as actual before execution.
6. Review `cleanup.sql`. It deliberately contains no active DROP statements. After authorization, explicitly suspend your lab warehouse and remove only lab-owned artifacts.

## 3. Scope and limits

These are self-contained teaching scripts, not a claim of successful live Snowflake integration, universal edition compatibility, or production readiness. `CREATE OR REPLACE` drops/recreates the named lab objects; never execute outside the approved temporary training schema. The tie-breaker `raw_id` reflects a synthetic fixture, not a general correction policy. Storage and compute charges may apply to a live run.

## 4. Cross references

Snowflake documentation links are embedded in the chapter PDF. External GitHub references P035–P045 are bibliographic teaching aids, not dependencies. All implementations in this package were written for this book; licenses of unrelated repositories have not been cleared for republication.
