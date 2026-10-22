# BI operational handoff — working example

**Pre-production design only.** Assign actual responsible names/roles before publication or deployment.

| Check | Evidence required | Owner (to assign) |
|---|---|---|
| Source delivered | Last source event, completeness, input contract | Source steward |
| Gold approved | Data tests, unique grain, accepted revisions, query ID | Data engineer |
| Semantic model version | DAX review, relationships, measures, unit definitions | Analytics engineer |
| Refresh reliability | Power BI service refresh history, source timestamps | BI operator |
| Identity security | Role grants, workspace permissions, tested RLS/SSO | Security owner |
| Dashboard performance | Performance Analyzer and Snowflake Query Profile | Platform owner |
| Deployment approval | Reviewed commit, rollback object, release summary | Product owner |

Escalation: mark report stale/under review if net position cannot be verified; do not default missing consumption to zero. Fix the earliest failing stage. For source restatements, capture old/new calculations, effective timestamp and approved notification.

**Cost:** no BI or warehouse service was run to create this artifact. Actual cost and region/edition/licence eligibility require review in the deployment tenant.
