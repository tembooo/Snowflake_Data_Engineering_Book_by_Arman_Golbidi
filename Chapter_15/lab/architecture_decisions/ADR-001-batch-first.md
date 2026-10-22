# ADR-001: Batch-first reference pipeline
Status: accepted for LOCAL TEACHING PROJECT, not a cloud authorization.
Date: 2026-10-22
Context: small synthetic fixture; an auditable replay is more valuable than low latency.
Decision: immutable local snapshots, append-only bronze, typed silver validation,
revision-resolved gold; optional streaming is out of base scope.
Alternatives: Snowpipe continuous, Snowpipe Streaming, external queue.
Consequences: simple offline repeatability; no proof of production freshness.
Revisit if a measured consumer SLA cannot be met by approved scheduled batches.
