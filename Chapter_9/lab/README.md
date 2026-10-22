# Chapter 9 companion lab — Snowpark Python

Original educational materials accompanying **Snowflake Data Engineering: From Fundamentals to Production-Ready Data Pipelines**, Chapter 9 (Arman Golbidi). Synthetic data only. No Snowflake account is needed for the default route.

## Offline quick start

Python 3.10+ with no required third-party dependencies:

```bash
python snowpark_pipeline.py
python -m unittest -v test_snowpark.py
```

Expected: 12 synthetic deliveries, 2 rejected invalid rows, 1 duplicate delivery, 9 distinct accepted events, 1 tombstoned key, 6 current visible energy facts, **66.000 MWh**, and **12 passing offline tests**. Output is written only to `output/`. These are deterministic Python business-contract tests; they do **not** exercise Snowflake DataFrame execution, billing, permissions, session semantics, query plans, or cloud packages.

## Optional Snowpark integration (NOT RUN)

`build_snowpark_dataframe(session, source_table, dimension_table)` builds a **read-only, lazy DataFrame** from a conformed latest-state table and a unique technology dimension. **Do not pass the raw revisioned event fixture directly into this method**: it expects revision resolution already completed. The separate `sql/optional_cloud_fixture.sql` provides a session-scoped synthetic integration fixture and SQL oracle. To use it, run its statements in the same Snowpark session that later reads the temporary tables. Alternatively, use approved persistent conformed tables and `run_optional_cloud.py`, which is disabled unless `CH09_LIVE_APPROVED=YES` is set. Note that a fresh connection cannot access temporary tables from another session.

Do not execute cloud tests until account owner approval, role and schema selection, expected spend, package and edition compatibility, and teardown are documented. Record actual query IDs and errors. The present archive has **NO verified Snowflake cloud run**.

## Files

- `snowpark_pipeline.py`: stdlib reference business rules plus lazy Snowpark DataFrame builder.
- `test_snowpark.py`: twelve stdlib contract tests independent of Snowflake.
- `data/energy_revisions.csv`: small synthetic revision fixture.
- `sql/optional_cloud_fixture.sql`: commented optional setup guidance and temporary fixture.
- `run_optional_cloud.py`: opt-in read-only Snowpark integration on pre-approved tables.
- `pyproject.toml`: dependency categories; **not** a locked environment; pin versions for published releases.
- `output/`: generated local CSV and JSON proof.

## Ethics and external resources

All manuscript diagrams and code here are newly authored, not copied from example GitHub repositories. Project references from the source outline remain pointers only; check license, commit SHA and test status before reproducing any externally owned code in a commercial book. Recheck the current Snowflake docs for APIs, Python runtimes, cost/edition distinctions before publication.

## Safety and cleanup

Only local `output/` files are written by default. No customer data or tokens are included. Neither this package nor the offline script creates/drops Snowflake objects. Optional cloud templates can incur costs. Do not use production credentials, shared schemas or admin roles in demonstrations.
