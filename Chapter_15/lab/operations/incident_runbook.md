# Incident runbook — preview for authorised operator

Symptoms: source freshness missed, duplicate deliveries, rejected-row spike,
wrong gold total, failed BI refresh or unexpected credits.

1. Record incident ID, environment, detection time, affected metrics and owner.
2. Pause *publication* (with approved access); do not delete the source ledger.
3. Identify fixture/source hash, new revisions and event-time versus ingest-time windows.
4. Run the offline acceptance oracle or authorised cloud reconciliation.
5. Quarantine conflicting versions; do not resolve ties by arrival order.
6. Obtain the owner's explicit approval before replay or cloud rollback.
7. Compare exact gold business keys and sums; verify BI refresh independently.
8. Check cost by service category; use warehouse suspend only for warehouse work.
9. Retain test output, query IDs (redacted publicly), timeline and follow-up actions.

RPO/RTO are *unvalidated targets* until a full timed restore drill succeeds.
No destructive SQL is enabled by default.
