# Chapter 10 companion — dbt delivery and release controls

Original educational materials by Arman Golbidi for *Snowflake Data Engineering*, Chapter 10. **Synthetic data only.** External GitHub projects are linked only as research pointers in the manuscript; their source code is not reproduced here.

## Safe, free offline run
```
python offline_oracle.py
python -m unittest -v test_pipeline.py
```
Expected from the 12-event fixture: 2 rejected invalid events, 1 duplicate delivery, 9 unique accepted events, 1 tombstoned key, 6 visible current energy facts and **66.000 MWh**. The release gate must report `ACCEPT`. Sixteen offline contract tests are included.

**No live Snowflake or dbt run is represented by these results.** The offline Python oracle independently expresses business rules and produces `output/` JSON and CSV. The SQL/dbt project is a manuscript teaching artifact requiring separate Snowflake integration, cost, security, edition and version checks.

## dbt project (UNTESTED IN SNOWFLAKE)
`dbt_project/` has a small synthetic seed and three models: accepted event staging, current business-key state, and a gold hourly mart. Model properties and singular tests include the 66.000 MWh fixture assertion, unique current key, nonnegative measure and equal-revision conflict check. `profiles.example.yml` has no credentials and assumes an interactive development context. Copy to a private profile location, use approved minimal roles and validate actual adapter versions before any cloud action.

## CI/CD
`.github/workflows/offline-checks.yml` runs the offline route without credentials. It assumes this lab's files are copied into a repository as the `lab/` directory with `.github/workflows` at repository root. `manual-cloud-deploy.yml` is deliberately *only* an approval-gated template: it **does not execute cloud SQL**. Review and pin Action SHAs in production.

## Limitations
The dbt fixture is not a complete enterprise ingestion connector. It rejects invalid events at staging but does not persist an independent cloud quarantine; an actual deployment must retain and monitor rejected input. A unique event ID carrying different values is a source-contract violation: offline checker rejects it; SQL model tests cover business-key conflicts, but a cloud pre-load audit should also reject conflicting event-ID payloads. Time values are explicit ISO UTC strings; real projects should use a typed timestamp and DST-aware requirements. Cost and timings are deliberately not invented.

## Clean up
Only `output/` is written by default. Never point demonstration commands at production. No cloud teardown commands are enabled. Follow `docs/deployment_runbook.md` if you elect to run the separately approved integration steps.
