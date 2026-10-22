# Chapter 13 companion lab — Security, Governance, Reliability, and Cost

Original pedagogical materials accompanying *Snowflake Data Engineering*, Chapter 13 (pp. 227–248). Includes synthetic data only. The project is NOT a claim of production readiness or verified Snowflake cloud compatibility.

## Offline execution (no credentials, no charge)

```sh
python -m unittest discover -s tests -v
python security_lab.py
```

Expected offline proof: **17 tests passed**; **6 accepted observations**; **66.000 MWh**; **3 expected-denial cases in a simulated role graph**; **2.5 hypothetical warehouse credits**, **3.65 hypothetical total compute/service credits** across warehouse, serverless and AI categories, plus **2.0 GB-month** storage (do not add storage to credits). No real vendor price or bill is asserted.

`security_model.json` describes fictional roles. `security_lab.py` models actions and role inheritance solely to test logic offline. It does NOT implement Snowflake privileges, and passing tests does not establish real permissions.

## Optional, administrator-approved Snowflake exercises

1. Agree sandbox account, edition/region, permission scope, spending safeguards and current official documentation. Use your organization's least-privilege grant process.
2. Have an authorized owner inspect `sql/00_bootstrap.sql`. It mutates a disposable namespace, including a one-time INSERT: **do not rerun**.
3. Review `sql/security_policies.sql` in a separate security change request. It creates roles and grants, so never execute as an unreviewed copy/paste student command. Approval and ownership privileges required.
4. Masking is an **OPTIONAL, COMMENTED** advanced feature; check Enterprise Edition and actual policy privileges. Do not claim masked behavior was tested when unavailable.
5. Run `sql/security_tests.sql` with separate real approved analyst and loader identities. Stop on unexpected privilege success; ensure failed queries fail for authorization (not malformed SQL).
6. Use cost views with an approved observation role after relevant metering delay. Do not combine attributed query credits with billed warehouse metering as additive charges.
7. `sql/99_cleanup.sql` is read-only by default; owner approves cleanup after assessing history and grants.

## Reproducibility and limitations
- Python tests run on local Python standard library; no external dependencies.
- Snowflake DDL, masking, BI client flows and external reference repositories **were not executed** against a live account in this deliverable.
- No licenses of the third-party GitHub examples were cleared for source redistribution. The code in this lab is original.
- Feature/edition/pricing behavior must be checked against current Snowflake account-specific documentation before use.
- Privilege-regression evidence requires real separately approved users; switching roles in an admin session is insufficient evidence.
