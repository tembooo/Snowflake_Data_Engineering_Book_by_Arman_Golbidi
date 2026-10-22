# Chapter 05 — Trustworthy batch ingest lab

**Book:** Snowflake Data Engineering: From Fundamentals to Production-Ready Data Pipelines  
**Author:** Arman Golbidi  
**Status:** Original, synthetic teaching fixture; Python offline tests passed. Snowflake SQL has **NOT** been executed against a live account.

## 1. What the lab proves

The scenario carries forward the six hourly solar/wind observations from Chapter 4. Two immutable batch files include an authorized revision and a malformed future reading. Physical ingestion and business acceptance are deliberately separate.

| Invariant | Expected |
|---|---:|
| Approved files | 2 |
| Physical CSV data rows | 8 |
| Structurally parsed, numeric rows | 7 |
| Quarantined nonnumeric values | 1 |
| Superseded revisions | 1 |
| Accepted unique source/metric/hour keys | 6 |
| Sum of accepted MWh | 97.500 |

**All data are author-created and synthetic.** They do not reproduce or claim a license to a Finnish energy provider's records. Any commercial use of real data needs a separate rights, provenance, and privacy assessment.

## 2. Offline reproduction — no Snowflake, no credit charges

Python 3.10+ standard library only:

```bash
python generate_manifest.py
python validate_fixture.py
python -m unittest discover -s tests -v
```

`generate_manifest.py` calculates SHA-256, checks the exact CSV header, and writes `source_manifest.csv`; `validate_fixture.py` reads and authenticates the manifest and source files, validates domain constraints, resolves the highest approved source revision and prints the accepted rows and quarantine. Five unit tests cover the baseline, tampering detection, drift rejection, authorized correction and bad manifest counts.

The fixture manifest is a build artifact that records source-byte identity. Preserve its SHA-256 and approval metadata when publishing a release. Avoid regenerating the manifest automatically *after* a source changed in an uncontrolled system; that would erase the evidence of a mismatch.

## 3. Optional cloud run (NOT performed for this manuscript)

1. Provision a **disposable** Snowflake database and schema with a least-privilege lab role; choose a small warehouse with auto-suspend and a cost plan. Confirm `CURRENT_ROLE`, `CURRENT_DATABASE`, and `CURRENT_SCHEMA` before execution.
2. Review `sql/file_formats.sql` and run it in your authorized context. Do not use ACCOUNTADMIN as a routine lab role.
3. Upload the two CSV files with a client that supports Snowflake `PUT`. The stage should contain only the approved fixture filenames. For example, replace the OS-specific path in the commented `PUT` examples. **Snowsight worksheets are not a general replacement for a PUT-capable client.**
4. Run `sql/validation_and_audit.sql` **first only through the initial `COPY ... VALIDATION_MODE` block** to check parser-level errors. Its later CREATE VIEW statements require the bronze table.
5. Run `sql/load_batch.sql` and **record the COPY query ID and result**. Expect 8 physical rows and two source files on a fresh database with the two exact fixture files.
6. Run the remainder of `sql/validation_and_audit.sql`. Expect one semantic rejection, six accepted keys, and a sum of 97.500 MWh. The accepted view uses the fixture's two approved versions; real production code should reconcile against a governed manifest table.
7. Inspect `sql/load_history.sql`; repeat `COPY` without `FORCE=TRUE` and record whether new rows were added. Never assume an older file or changed path is automatically idempotent.
8. Review the **commented** cleanup script and remove only approved disposable resources. Retain evidence required for reproducibility.

### Important Snowflake restrictions

* `VALIDATION_MODE` cannot be used with `COPY INTO` statements that apply a `SELECT` transformation. The provenance-enriched load and structural dry-run are intentionally separate.
* The file format `ERROR_ON_COLUMN_COUNT_MISMATCH` has context-dependent behaviour with COPY transformations; therefore the offline validator checks exact headers/field counts before staging.
* Snowflake's COPY file-load history is not a substitute for business-key deduplication. The `FORCE` option can reload already processed files.
* The approved revision is given by the source manifest, **not** by the timestamp at which Snowflake happened to scan a file.

## 4. Sources and related projects

Official docs: https://docs.snowflake.com/en/sql-reference/sql/copy-into-table ; https://docs.snowflake.com/en/user-guide/querying-metadata ; https://docs.snowflake.com/en/sql-reference/sql/create-file-format ; https://docs.snowflake.com/en/sql-reference/functions/copy_history

Companion references from the author's research directory include:
- https://github.com/Snowflake-Labs/sfguide-snowflake-northstar-data-engineering
- https://github.com/Snowflake-Labs/sfguide-data-engineering-with-coco
- https://github.com/Snowflake-Labs/sfguide-getting-started-with-api-enrichment-framework

These GitHub repositories are independent reading references. Their runtime success, exact license for reusing files, and current edition compatibility have not been established here. The code provided in this lab is independently written and does not reproduce their source.

## 5. Editorial release gate

Before commercial publication: test SQL end-to-end against an appropriately configured Snowflake account; save query IDs and actual result logs; verify all SQL options in the edition/region used; confirm optional projects' licenses; inspect typography and code; pin a release tag and the source SHA-256 manifest. No cloud execution or production readiness is claimed in this draft.
