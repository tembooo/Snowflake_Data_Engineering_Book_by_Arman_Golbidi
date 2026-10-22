-- CHAPTER 02 OPTIONAL LAB / SNOWFLAKE SQL
-- Status: AUTHOR-WRITTEN; NOT EXECUTED AGAINST SNOWFLAKE.
-- SAFETY: Obtain a sandbox database, a least-privilege training role,
--         and a suspended X-Small test warehouse from an administrator.
--         Never run this against production or with broad privileges.
--         Change BOOK_DEV/CH02_LAB to approved names BEFORE running.
-- The table is not DROPped by this script. Review objects and cleanup separately.

USE DATABASE BOOK_DEV;
USE SCHEMA CH02_LAB;
USE WAREHOUSE BOOK_CH02_XS;

ALTER SESSION SET QUERY_TAG = 'BOOK_CH02_LAB';
ALTER SESSION SET USE_CACHED_RESULT = FALSE;

-- The sandbox schema must belong to this lab only.
-- Do not run this when an unrelated table with the name already exists.
CREATE TRANSIENT TABLE IF NOT EXISTS ENERGY_READING (
    scenario_id VARCHAR NOT NULL,
    event_utc TIMESTAMP_NTZ NOT NULL,
    source VARCHAR NOT NULL,
    power_mw FLOAT NOT NULL,
    minutes INTEGER NOT NULL
) DATA_RETENTION_TIME_IN_DAYS = 0;

-- MERGE preserves our four synthetic keys when the script is rerun.
MERGE INTO ENERGY_READING AS t
USING (
  SELECT column1::VARCHAR AS scenario_id,
         column2::TIMESTAMP_NTZ AS event_utc,
         column3::VARCHAR AS source,
         column4::FLOAT AS power_mw,
         column5::INTEGER AS minutes
  FROM VALUES
    ('CH02_SYNTH','2026-01-15 00:00:00','WIND',480.0,15),
    ('CH02_SYNTH','2026-01-15 00:15:00','WIND',500.0,15),
    ('CH02_SYNTH','2026-01-15 00:00:00','SOLAR',0.0,15),
    ('CH02_SYNTH','2026-01-15 00:15:00','SOLAR',0.0,15)
) AS s
ON t.scenario_id = s.scenario_id
AND t.event_utc = s.event_utc AND t.source = s.source
WHEN NOT MATCHED THEN INSERT
  (scenario_id, event_utc, source, power_mw, minutes)
  VALUES (s.scenario_id, s.event_utc, s.source,
          s.power_mw, s.minutes);

-- Run a small, semantically explicit query and open Query Profile.
SELECT source,
       COUNT(*) AS intervals,
       ROUND(AVG(power_mw), 1) AS mean_power_mw
FROM BOOK_DEV.CH02_LAB.ENERGY_READING
WHERE scenario_id = 'CH02_SYNTH'
  AND event_utc >= '2026-01-15'::TIMESTAMP_NTZ
  AND event_utc <  '2026-01-16'::TIMESTAMP_NTZ
GROUP BY source
ORDER BY source;

-- Expected synthetic logical result (not a recorded Snowflake run):
-- SOLAR | 2 | 0.0
-- WIND  | 2 | 490.0
-- Profile measures (execution time, partitions scanned, credits) vary.

-- Reset session-specific diagnostic state.
ALTER SESSION SET USE_CACHED_RESULT = TRUE;
ALTER SESSION UNSET QUERY_TAG;
-- If this is a dedicated lab warehouse and no one else uses it,
-- request approval before: ALTER WAREHOUSE BOOK_CH02_XS SUSPEND;
-- Cleanup only after confirming ownership and no external dependencies:
-- DROP TABLE BOOK_DEV.CH02_LAB.ENERGY_READING;
