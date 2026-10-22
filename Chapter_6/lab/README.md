# Chapter 6 Companion Lab — JSON and Semi-Structured Data

A **synthetic** Finnish-energy-themed teaching project for the book *Snowflake Data Engineering* by Arman Golbidi. No real Finnish publisher data are embedded, and no actual Snowflake warehouse execution is claimed.

## Offline path (executed and tested)

```bash
python validate_payloads.py
python -m unittest discover -s tests -v
```

Python 3.10+ standard library only; no additional dependencies, cloud services, tokens, or API requests. The verifier preserves each original physical line as the unit of traceability. It refuses a numeric null, unsupported version, wrong shape, unexpected unit, duplicate technology, repeated business key, or invalid UTC-hour timestamp. Expected output: **4 lines; 2 accepted envelopes; 1 syntax reject; 1 contract reject; 6 accepted readings; 97.500 MWh**.

The schema revision mapping is explicit: v1 `observations`; v2 `measurements`. The `source_line` is ingestion provenance only, never a business key. A rejected envelope contributes **zero** accepted measurements and does **not** turn null measurements into zero.

## Snowflake SQL path (NOT EXECUTED)

1. Use a disposable authorized database and schema with a small auto-suspending warehouse and a limited role.
2. Run `sql/json_ingestion.sql` to load the four *raw text* fixtures as session-scoped temporary rows.
3. Run `sql/flatten_transform.sql` to create a temporary typed silver table with whole-envelope validity.
4. Run `sql/validation_queries.sql`, inspect outputs, query IDs and unique-key conditions.
5. Review the commented `sql/cleanup.sql` if you need manual cleanup. Temporary tables drop at session end.

SQL must be validated in a real account/edition/region, particularly before commercial print. `CREATE OR REPLACE TEMPORARY TABLE` is scoped to the current schema and can replace an identically named temporary object; use an isolated lab schema.

## Files

- `data/sample_api_payload.jsonl`: two valid versioned envelopes, one semantically invalid, one syntactically invalid.
- `validate_payloads.py`: original deterministic, provenance-aware verifier.
- `tests/test_payloads.py`: six executed unittest checks.
- `expected_report.json` / `run_report.txt`: offline fixture-derived results, not measured Snowflake output.
- `sql/`: original Snowflake learning scripts. Comments indicate illustrative expected results.

## Permissions and references

The chapter references external GitHub projects for additional study. Their original repositories must be checked independently for version, licensing, region, execution cost and current compatibility before excerpts or screenshots are republished. This lab does not copy their code.
