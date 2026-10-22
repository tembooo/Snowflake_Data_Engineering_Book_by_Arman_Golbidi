# Chapter 10 release and incident runbook (educational)

**Not approved for production.** All data are synthetic. Snowflake/dbt cloud integration has not been executed. A reviewed cloud identity, adapter version, edition/region, cost estimate and cleanup plan are needed first.

## Five release gates
1. Reviewed Git commit, dependency and model diff. No secrets in logs or repository.
2. Source/data contract approved: UTC grain, MWh unit, revision and tombstone semantics.
3. Offline oracle returns 6 visible rows and `66.000` MWh; unit and replay assertions pass.
4. Isolated Snowflake dbt `seed -> build -> test` integration success, artifacts and query IDs saved. **UNTESTED at manuscript creation.**
5. Reversible publication strategy, on-call owner and approval recorded.

## Approved development integration only
Install a **verified and locked** supported `dbt-core` / `dbt-snowflake` combination; configure `profiles.yml` outside the repository. Check the account/provider/edition, model SQL, dbt argument syntax and grants with official documentation. Within a disposable dedicated schema:
```
dbt debug --project-dir dbt_project --profiles-dir PRIVATE_PROFILE_DIR
dbt seed --project-dir dbt_project --profiles-dir PRIVATE_PROFILE_DIR
dbt build --project-dir dbt_project --profiles-dir PRIVATE_PROFILE_DIR
```
These commands **have not** been run in this delivery. Use a small auto-suspending warehouse and role with permissions only on owned disposable schemas. Captured profiles and logs must omit secrets.

## Incident triage
Inspect source deliveries, tests, model artifacts, freshness results and consumer publication timestamp in order. Do not auto-retry a domain failure. Keep the last known-good published result until affected keys are reconciled and promotion is approved.

## Rollback
Reverting a SQL commit does not reverse changed data. Stage a last-good relation or rebuild from approved immutable bronze input, run uniqueness/unit/current-revision checks, approve consumer repointing and document downstream invalidation. Snowflake Time Travel is object- and retention-dependent. Avoid unreviewed database drops.

## Cleanup
Offline cleanup: remove only `output/` from this lab. Cloud: list disposable schemas and objects created by the test, back up run evidence and delete only those named objects with account-owner approval. No destructive SQL scripts are distributed.
