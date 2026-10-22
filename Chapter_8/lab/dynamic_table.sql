-- Chapter 8 declarative comparison; SQL UNTESTED on Snowflake.
-- Run after CH08_BRONZE_EVENTS has been created/seeded by incremental_stream_task.sql.
-- This CREATE DYNAMIC TABLE starts managed refresh and can incur credits immediately.
-- Replace CH08_WH with the actual approved virtual warehouse. Obtain cost approval.
-- A full source snapshot recomputation is compared with the procedural MERGE result.
CREATE OR REPLACE DYNAMIC TABLE CH08_DT_LATEST
  TARGET_LAG = '20 minutes'
  WAREHOUSE = CH08_WH
  REFRESH_MODE = INCREMENTAL
AS
SELECT event_id, provider, technology, interval_utc,
       revision, energy_mwh, operation, ingested_at
FROM CH08_BRONZE_EVENTS
WHERE revision >= 0
  AND (operation = 'DELETE'
       OR (operation = 'UPSERT' AND energy_mwh >= 0))
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY provider, technology, interval_utc
  ORDER BY revision DESC, ingested_at DESC, event_id DESC
) = 1;

CREATE OR REPLACE VIEW CH08_DT_VISIBLE AS
SELECT provider,technology,interval_utc,revision,energy_mwh
FROM CH08_DT_LATEST WHERE operation='UPSERT';

SHOW DYNAMIC TABLES LIKE 'CH08_DT_LATEST';
-- Refresh completion is asynchronous. Verify status before querying results.
-- SELECT COUNT(*) AS visible_rows,SUM(energy_mwh) AS total_mwh FROM CH08_DT_VISIBLE;
-- Expected after completed init: 6 rows and 66.000 MWh.
-- Compare both materializations only after the task MERGE is committed and DT initialized:
-- (SELECT provider,technology,interval_utc,revision,energy_mwh FROM CH08_SILVER_STATE WHERE operation='UPSERT')
-- MINUS
-- (SELECT provider,technology,interval_utc,revision,energy_mwh FROM CH08_DT_VISIBLE);
-- Reverse MINUS direction as well; both must return zero rows.
-- REQUIRES APPROVAL -- DROP VIEW IF EXISTS CH08_DT_VISIBLE;
-- REQUIRES APPROVAL -- DROP DYNAMIC TABLE IF EXISTS CH08_DT_LATEST;
