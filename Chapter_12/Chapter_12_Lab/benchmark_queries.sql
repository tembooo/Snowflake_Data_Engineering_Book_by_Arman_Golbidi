-- CH12 read-only tagged Snowflake benchmark queries. NOT CLOUD-EXECUTED.
-- Precondition: optional_setup.sql ran in an approved isolated sandbox.
-- Do not use a shared warehouse or assume a warm/cold cache state.
ALTER SESSION SET QUERY_TAG='book_ch12_energy_benchmark_v1';
ALTER SESSION SET USE_CACHED_RESULT=FALSE;

-- Baseline date expression (correctness should match candidate below).
SELECT technology, SUM(energy_mwh) AS mwh
FROM BOOK_DEV.CH12_LAB.ENERGY_FACT
WHERE TO_DATE(interval_utc)='2026-10-04'
GROUP BY technology ORDER BY technology;

-- Candidate half-open UTC range; identical expected result: 6 rows, 66 MWh.
SELECT technology, SUM(energy_mwh) AS mwh
FROM BOOK_DEV.CH12_LAB.ENERGY_FACT
WHERE interval_utc >= '2026-10-04'::TIMESTAMP_NTZ
  AND interval_utc < '2026-10-05'::TIMESTAMP_NTZ
GROUP BY technology ORDER BY technology;

-- Repeat each representative query 5-10 times, alternating variants.
-- Record Query ID, dataset snapshot, warehouse size, role, time, queue,
-- partitions scanned, execution time and separately metered credits.
-- Small fixture is NOT suitable for generalizing real performance.
ALTER SESSION UNSET USE_CACHED_RESULT;
ALTER SESSION UNSET QUERY_TAG;
