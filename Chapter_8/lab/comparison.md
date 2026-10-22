# Chapter 8 — procedural vs. declarative incremental materialisation

**Version:** editorial draft, 2026-10-22. **Cloud state:** SQL templates have **not** been executed against Snowflake. External example repos have not been executed or cleared for redistribution.

## Business contract

An observation is identified by `(provider, technology, interval_utc)` with UTC timestamps; `revision` is a non-negative integer monotonically increasing per key. The highest revision wins; deterministic `(ingested_at, event_id)` breaks ties. A `DELETE` is a retained tombstone and must not expose an energy reading. Reject negative measurements before publication; do not silently turn null into zero. All numerical examples are synthetic, not from Fingrid.

## Comparable implementations

- `incremental_stream_task.sql`: append-only Stream on synthetic event log; triggered task applies deterministic `MERGE` into mutable state table. DML transaction commits the stream offset together with the target update. A failed transaction should be retried; monitoring is mandatory.
- `dynamic_table.sql`: declarative SQL defining latest-revision state using `QUALIFY ROW_NUMBER() ... = 1`, explicitly requests incremental refresh with a 20-minute freshness target. A refresh may take longer; check `SHOW DYNAMIC TABLES` and refresh history. Does not support arbitrary external side effects or direct DML into the dynamic table.
- `incremental_model.py`: executable **offline analogy** of the two data results; it intentionally does not claim to reproduce Snowflake storage semantics, scheduler timing, transactions or billing.

## Expected invariant and observed offline experiment

From twelve delivered synthetic rows: eleven valid deliveries, ten unique accepted events after duplicate elimination, one quarantined negative observation, seven latest key states including one deleted key, six visible observations, and exactly 66.000 MWh. The two independent update formulations agree for the supplied fixture; replay is idempotent and an older revision cannot reverse the deletion.

## Release gates before publication

1. Use a disposable database/schema and dedicated role. Record Snowflake cloud/region/edition, warehouse, exact SQL execution, query IDs, run time and actual cost.
2. Verify the feature support matrix for the deployment region. Pin reference repos to commit SHAs and review their licence before copying any source.
3. Test initialisation ordering, two simultaneous producers, a failed MERGE statement, a deletion correction, stream staleness boundary, several independent stream consumers, and a late backfill.
4. Measure event-to-silver lag and credits separately for both approaches on the same workload; do not compare synthetic scheduler timing with live metrics.
5. Suspend and drop resources only after copying evidence, and retain a signed approval for destructive actions.

## Design recommendation

For governed reporting derived solely from SQL, prefer a Dynamic Table when supported operators and achievable target lag satisfy the service objective. Prefer Streams + Tasks when procedural actions, side-effect orchestration, explicit transaction boundaries or complex upsert logic are required. A standard view is a valid low-maintenance option when consumers can bear query-time computation. Neither model eliminates data quality contracts or replay plans.
