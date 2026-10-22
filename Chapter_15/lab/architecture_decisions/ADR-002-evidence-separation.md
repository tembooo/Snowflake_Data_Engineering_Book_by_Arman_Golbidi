# ADR-002: Separate offline oracle from cloud integration tests
Status: accepted for educational project, 2026-10-22.
Decision: Python standard-library reference implementation is the deterministic
acceptance source; Snowflake SQL is a separately reviewed compatibility target.
Positive: no credentials or credits required to inspect data correctness.
Negative: cannot validate roles, billing, SQL syntax, warehouse performance or BI refresh.
Rule: no live execution claims without captured query IDs and evidence.
