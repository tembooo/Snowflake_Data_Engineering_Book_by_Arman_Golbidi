# Chapter 4 Data Dictionary — Fictional Energy Observations

**Data status:** Fully synthetic; not a source of Finnish national energy statistics.

**Accepted fact grain:** one accepted generation_MWh reading per `(source_code, metric_code, interval_start_utc)`.
**Time:** `TIMESTAMP_NTZ` represents UTC wall-clock by explicit source contract. The example does not parse local ambiguous times.
**Interval:** start inclusive, next hour exclusive; all readings cover non-overlapping 1-hour periods.
**Units:** `energy_mwh` stores fixed decimal MWh. Power MW is not a synonym.
**Duplicate policy:** newest `loaded_at_utc`, tie-broken with `raw_id`, supersedes earlier correction for the same business key.
**Raw row count:** 7; **accepted row count:** 6; **accepted MWh:** 97.500.

| Column | Source / table | Type | Definition |
|---|---|---|---|
| raw_id | raw_energy, fact | NUMBER(18,0) | Source-ingest record identity; provenance. |
| source_code | raw_energy, dimension, fact | VARCHAR(32) | Natural source code (two synthetic sources). |
| metric_code | raw_energy, dimension, fact | VARCHAR(32) | `generation_mwh` only in this lab. |
| interval_text | raw_energy | VARCHAR(32) | Input timestamp; guaranteed UTC in fixture. |
| interval_start_utc | stage, fact | TIMESTAMP_NTZ | Parsed UTC hour start (contract-defined). |
| mwh_text | raw_energy | VARCHAR(32) | Source-provided decimal text. |
| energy_mwh | stage, fact | NUMBER(18,3) | Accepted interval generation in MWh. |
| loaded_at_utc | raw_energy, fact | TIMESTAMP_NTZ | Ingestion time, not energy observation time. |
| source_key | dim_source, fact | NUMBER(18,0) | Example surrogate for source dimension. |
| metric_key | dim_metric, fact | NUMBER(18,0) | Example surrogate for metric dimension. |
| utc_date_key | dim_date_utc, fact | NUMBER(8,0) | YYYYMMDD UTC calendar key. |

**Production adaptation requirements:** genuine source provenance and licenses, metering semantics, DST-aware source parsing, authorization and privacy, late-arrival windows, unit conversion precision, source overlap rules, SCD strategy, test results and real billing observations.
