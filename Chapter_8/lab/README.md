# Snowflake Data Engineering — Chapter 08 companion lab

## Purpose and safety
This folder implements an author-original, deterministic offline comparison of procedural incremental updates and a declarative latest-revision snapshot. The fixture is entirely synthetic. No internet access, Snowflake account, tokens, paid services or external packages are needed for the offline part.

### Offline execution (Python 3.10+)
```sh
python incremental_model.py
python -m unittest -v test_incremental_model.py
```
Outputs are created under `output/`. They are safe to delete locally. Sample totals are *not* a Snowflake performance result.

### Optional Snowflake SQL study (not executed)
Read, check and customise `incremental_stream_task.sql` and `dynamic_table.sql`. A least-privilege role must have access to a disposable database/schema and an authorised warehouse. `CH08_WH` is a **placeholder**, not a supplied warehouse. Scripts intentionally leave the task suspended; creating the dynamic table may nonetheless start billed compute. The SQL fixture differs from the offline file because the bad negative event was quarantined before the cloud ingestion boundary. Never enable unattended tasks for a tutorial without approved spending limits and cleanup procedures.

The order is (1) table, (2) stream, (3) synthetic inserts, (4) task, (5) optional manual task resume/execute, (6) dynamic table and completed initial refresh, (7) compare outputs. Stream SELECT does not consume, but a successfully committed MERGE reading the stream advances its offset. See current Snowflake docs for exceptions and feature changes.

### Publications and rights
All original Python/SQL/CSV files in this folder are new instructional examples. The book points to external GitHub repositories for independent reading only. Those repositories are **not bundled**, run-tested, or assumed to have commercial reuse permissions. Pin release tags and test the actual Snowflake account before publication.
