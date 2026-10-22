# Chapter 9 — Architecture Decision Record: energy transformations

**Status**: educational design, not deployed / not production-validated.

- **Business key**: `(provider, technology, interval_utc)`.
- **Version precedence**: highest accepted positive revision; delete tombstones suppress current visible row.
- **Input**: conformed current-state table after event deduplication; 12-row synthetic fixture is only a contract test.
- **Output**: category and UTC interval aggregates in MWh, with dimensional uniqueness confirmed.
- **Decision**: build read-only, lazy Snowpark DataFrame for composable transformation; retain SQL oracle and stdlib offline tests.
- **Alternative**: SQL-only may be simpler if no Python integration is needed. External pandas collection is rejected for large inputs because of transfer, access and memory risks.
- **Execution**: approved Snowflake warehouse after a deliberate action, not in the client interpreter for normal relational operators.
- **Security**: least-privilege role, versioned connection management, no credentials in source/logs.
- **Reliability**: replay-safe ingestion boundary, stable source snapshot, small verification output, query IDs, alert on failed checks.
- **Cost and limits**: no performance, credits or runtime results were measured in Snowflake. Proposed cloud checks require authorisation and a cap.
- **Unresolved**: Snowpark and account version pin, Snowflake live integration, packaging rights for external examples, query-history evidence, deployment and rollback evidence.
