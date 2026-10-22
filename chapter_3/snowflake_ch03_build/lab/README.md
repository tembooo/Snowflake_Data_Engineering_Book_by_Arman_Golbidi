# Chapter 03 — A Governed First Snowflake Workspace

Companion resources for *Snowflake Data Engineering*, Chapter 3 (pages 39–56), by Arman Golbidi.

## Evidence and safety status

The Python offline preflight test can be run without credentials. The Snowflake SQL scripts and live Python connection are **not executed** here and require review by an authorised administrator, a dedicated sandbox account and appropriate spend controls. No observed Snowflake query results are claimed. All sample readings are synthetic and illustrative.

## Prerequisites

- Python 3.10 or later for `lab_preflight.py`.
- Optional: current supported Snowflake CLI; Snowflake account with least-privilege roles assigned by an administrator.
- Optional: Snowflake Connector for Python installed in a virtual environment. Determine and pin a compatible version before publication.
- Approved account identifier, EU or other suitable region, cost budget, virtual warehouse policy and an environment owner.

## Sequence

1. Run `python lab_preflight.py` locally. It checks the companion files and dangerous SQL markers, without cloud access.
2. Have a designated **object provisioner** inspect `sql/01_bootstrap.sql` and execute it in a dedicated sandbox using its authorised privileges.
3. Have the **security or grant administrator** review and execute `sql/02_grants.sql`. They must explicitly assign `BOOK_CH03_READER` to the intended teaching identity. It is not automatic.
4. Verify identity and read access with `sql/03_verify.sql` using only `BOOK_CH03_READER` and (if permitted) no secondary roles.
5. If the lab instructor authorises it, execute `sql/04_negative_test.sql`, which is expected to fail at the attempted write. Stop if it succeeds; inspect any inherited grants.
6. Independently suspend the dedicated lab warehouse as soon as queries complete, following organisation policy.
7. Have a provisioner inspect the resource manifest and selectively enable the commented cleanup statements. Never execute a broad DROP against shared resources.

Expected data (if the bootstrap insert executed once): one synthetic row (`OBS_ID=1`, `SOURCE='synthetic_wind'`, `POWER_MW=82.0`). This is an expected assertion, not a measured result.

## Role design and caution

`CREATE ROLE` and `GRANT` require different permissions from normal querying. The learner should never gain `ACCOUNTADMIN` for this lab. For real organisations, `USE SECONDARY ROLES NONE` and role-hierarchy grants affect negative-test outcomes. Stop immediately if the selected account or objects differ from the reviewed manifest.

## File map

- `sql/01_bootstrap.sql` — provisioning definition and a single synthetic seed row.
- `sql/02_grants.sql` — admin-only least-privilege reader role and grants.
- `sql/03_verify.sql` — read-only query checks.
- `sql/04_negative_test.sql` — deliberately denied attempt to write, run only with approval.
- `sql/99_cleanup.sql` — safe-by-default commented destructive operations for manual review.
- `connection_probe.py` — interactive external-browser sample; does not run unless explicitly invoked.
- `lab_preflight.py` — offline static safety checks and sample-row checks.
- `.env.example` — names of environment variables, no credentials.

## Selected primary references

- https://docs.snowflake.com/en/user-guide/admin-trial-account
- https://docs.snowflake.com/en/user-guide/security-access-control-overview
- https://docs.snowflake.com/en/sql-reference/sql/create-warehouse
- https://docs.snowflake.com/en/developer-guide/snowflake-cli/connecting/configure-connections
- https://docs.snowflake.com/en/user-guide/cost-controlling

The official and third-party GitHub projects in the chapter are **reading references**, not copied source-code listings. Their test compatibility and redistribution rights must be checked individually before final publication.
