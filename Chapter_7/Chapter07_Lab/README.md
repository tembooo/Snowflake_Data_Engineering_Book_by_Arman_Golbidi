# Chapter 7 — Offline Streaming & Replay Lab

**Book**: Snowflake Data Engineering — From Fundamentals to Production-Ready Data Pipelines  
**Author**: Arman Golbidi  
**Status**: Educational original code; deterministic **offline** Python lab tested on 22 October 2026. Snowflake integration SQL is a template **not executed in Snowflake**.

## Run (Python 3.10+; standard library only)

```shell
python streaming_simulator.py --out output
python -m unittest -v test_streaming_simulator.py
```

Expected `metrics.json`: 9 source events, 10 attempts because one retry, 8 accepted bronze rows, 1 quarantined event, 6 deduplicated silver rows, **66.000 MWh**, median bronze freshness **27 seconds**, maximum **485 seconds**, last committed synthetic offset 8. Timestamps and delays are illustrative: **these are not Snowflake performance benchmarks**.

## Model and tests

* Source offsets are ordered within one synthetic partition; producer retries one event after a transient failure.
* Bronze preserves the accepted delivery log including a duplicate and superseded revision.
* Silver materializes the highest revision per `(provider, technology, event_utc)`, excluding negative readings and not counting duplicates as distinct observations.
* Event timestamps are UTC. Freshness is synthetic `visible_utc - event_utc`; this includes a late event, so it is not merely ingest service latency.
* `quarantine.json` logs rejected records; `attempts.json` differentiates failures from committed processing.
* Eight unit tests cover counting, correction precedence, total, quarantine, replay, late arrivals, determinism, and a no-failure baseline.

## Cloud integration boundaries

`snowpipe_setup.sql` deliberately leaves account-specific external stages and live streaming pipe creation **commented out**. The SQL includes a small raw-table example and templates for file-based Snowpipe and the current high-performance Snowpipe Streaming architecture. It does **not** provision AWS/Azure/GCP event notifications, OAuth/JWT, secrets, or any billable deployment. A cloud reviewer must check permissions, regional/edition capability, role minimization, and [the current Snowflake documentation](https://docs.snowflake.com/en/user-guide/snowpipe-streaming/snowpipe-streaming-high-performance-overview) before uncommenting. The two architectures have different client/pipe conventions.

## Cleanup

The offline lab creates only files in `output/`; `rm -r output` (Linux/macOS) or `rmdir /s output` (Windows CMD) deletes them. No default command destroys a Snowflake object. Review and explicitly approve each cloud DROP statement if adapting this exercise to a test account.

## Publishing and attribution

Original instructional implementation and synthetic data. Referenced third-party repositories are *further reading only*, not source-code copies or verified working deployments. Before a commercial edition, rerun Snowflake SQL, capture query IDs and billed usage, pin a documentation snapshot, review repository licenses and seek an independent technical review.
