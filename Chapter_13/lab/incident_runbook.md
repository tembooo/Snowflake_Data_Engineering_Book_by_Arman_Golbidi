# Chapter 13 — Synthetic energy platform incident runbook

**Status:** Educational simulation; not a deployed incident-response plan. **Owner:** assign a named service owner before any cloud use. **Environment:** isolated BOOK13_SANDBOX, never production without separate review.

## Incident A: unintended role inheritance exposes raw energy/contact data
1. Open a ticket, record reporter, account, role, event time and affected table.
2. Triage using a separately authorized review identity. Capture SHOW GRANTS and relevant query IDs without copying sensitive values into shared tickets.
3. Determine whether secondary roles or direct grants broaden effective permission. Confirm with a real authorized analyst test identity, not admin.
4. Obtain incident commander and security owner approval to revoke the specific unintended role edge; rotate any exposed keys.
5. Repeat allowed SELECT of GOLD and denied SELECT/INSERT of RAW. Check whether downstream data was exported; escalate to privacy/legal reviewer where necessary.
6. Log communication, data impact, final grants, owner and remediation deadlines. Remove temporary privileges.

## Incident B: unexpected cloud spending
1. Confirm alert scope and category. Budget alert != hard cap. Resource Monitor applies to warehouse credits, **not** every serverless/AI charge.
2. Identify the workload owner; preserve identifiers, query tags, meter period, and billing publication lag.
3. If approved, stop or suspend the *isolated experimental warehouse* after checking that essential data workflows do not share it. Do not blindly halt production.
4. Inspect the schedule, query drift, retention and serverless features. Document actual usage only from authoritative metering; separate estimates from billed costs.
5. Restore at a controlled cadence with a named owner, alert threshold, data freshness check and updated cost estimate.

## Recovery evidence record
Incident ID, detection timestamp, first containment timestamp, RPO, RTO, data restored, query IDs, affected objects, cost category, responsible approver, communication timestamps, observed outcome, unresolved issues, follow-up owner.

## Safety and rollback
Destructive commands are commented in `sql/99_cleanup.sql`; only an authorized owner can execute them. Never remove audit logs to hide errors. Recovery from Time Travel, source replay, or separately approved backup must be tested rather than assumed. Fail-safe is not an instant user-controlled backup.
