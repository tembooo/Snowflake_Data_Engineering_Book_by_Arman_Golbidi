# Snowflake Data Engineering — Chapter 02 companion lab

**Chapter:** Snowflake Architecture: Storage, Compute, and Services  
**Page allocation:** 21–38  
**Status:** Offline Python check executed; Snowflake SQL *not run* in this production workflow.

## Files

- `architecture_v1.svg` — original vector architecture diagram for the Finland energy case.
- `explain_query.sql` — opt-in Snowflake lab script for an approved sandbox.
- `energy_sample.csv` — explicitly **synthetic** power readings, not Finnish statistics.
- `offline_validate.py` — built-in Python check requiring no cloud account.
- `tradeoffs.md` — original architecture decision record.

## Offline workflow

Run `python offline_validate.py`; expected:

```
PASS: synthetic row counts and mean-power outputs
SOLAR: intervals=2, mean_power_mw=0.0
WIND: intervals=2, mean_power_mw=490.0
```

This establishes only the arithmetic of this miniature sample. It does **not**
validate energy statistics, production data quality, Snowflake Query Profile, or performance.

## Optional Snowflake workflow: never run in production

1. Arrange a training Snowflake account with an administrator.
2. Check billing monitoring, current feature support, and X-Small auto-suspend.
3. Have an administrator provision a **dedicated** sandbox database/schema and
   least-privilege test role. Verify all script identifiers point only to that namespace.
4. Inspect `explain_query.sql` for unwanted collisions before execution.
5. Run each block selectively in a worksheet; inspect Query History and the Query Profile.
6. Record measured values and query ID in your own lab journal. No prescribed timing
   or partition counts are claimed in the book.
7. Restore session settings, and remove **only** the objects you created after
   checking ownership and dependencies. Suspend the warehouse only with permission.

**Security and cost:** No passwords, API keys, or private datasets are used. An account
and running warehouse may incur charges; budgets are not universal hard caps.

**Reference and licensing:** External GitHub repositories cited in the chapter are
reading material only. Do not republish their code or images without a permissions check.
