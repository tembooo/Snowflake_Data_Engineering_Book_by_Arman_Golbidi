# Chapter 02 — Architecture Decision Record (ADR-002)

**Status:** proposed teaching decision; not a production benchmark.  
**Date:** 2026-10-21  
**Scenario:** Finland Energy Analytics Platform (synthetic inputs in Chapter 02).

## Context and architectural question

Can a daily, validated, reproducible energy metrics report be delivered on time
without a streaming stack, a multi-cluster warehouse, or externally managed tables?

## Constraints and assumptions

- Data source, rights, and public API limits are still to be verified.
- UTC timestamps and explicit MW/MWh definitions are mandatory.
- Read-only BI access, data-quality checks, a documented incident runbook,
  and measurable freshness are required.
- Budget, account region, edition, warehouse sizing, and credits are **not yet measured**.
- All actual Snowflake lab metrics are **NOT RUN** until an authorized sandbox exists.

## Options considered

| Option | Benefits | Risks / costs | Decision |
|---|---|---|---|
| A. Batch-first ingestion, native Snowflake tables, distinct BI and ELT compute if needed | Simple recovery/replay, managed operations, staged onboarding | Batch freshness; potential two-warehouse costs | **Provisional baseline** |
| B. Continuous ingestion, native tables | Potentially lower ingestion lag | Stateful delivery, monitoring complexity, variable serverless usage | Reconsider only with measured freshness need |
| C. External Iceberg storage | Open-format interoperability | Catalog, permission, and transfer/recovery ownership | Reconsider for multi-engine requirement |
| D. Hybrid tables for interactive reads/writes | Transaction-oriented workload support | Availability and suitability constraints | Not justified for the main BI scan workload |

## Decision

Prototype Option A in a least-privilege sandbox, then measure a realistic,
correctness-validated workload. Do not claim a pricing or speed win before testing.

## Measurement plan

1. Verify query semantics and source rights.
2. Freeze dataset size/version and note timestamp grain.
3. Record query ID, warehouse state, cache setting, scanned/total micro-partitions,
   elapsed time, queueing, and any relevant credits.
4. Compare alternate workload designs under matched conditions and record no-gain results.
5. Reassess after the first actual source integration and service-level objective review.

## Consequences and reversal triggers

If the required freshness falls below what batch safely meets, evaluate a continuous
pattern. If BI queues under ELT contention, benchmark separated warehouses first.
If multi-engine open storage becomes contractual, evaluate Apache Iceberg table options.

## Source-project note

Referenced third-party GitHub demonstrations are research examples only: their
licenses and compatibility must be cleared independently before reusing code or assets.
