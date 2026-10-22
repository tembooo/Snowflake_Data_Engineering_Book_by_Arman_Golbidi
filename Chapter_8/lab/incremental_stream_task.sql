-- Chapter 8 original teaching implementation; NOT EXECUTED against a Snowflake account.
-- Prerequisite: USE ROLE a least-privilege role with CREATE TABLE/STREAM/TASK and
-- ownership or needed grants in a disposable database/schema; USE WAREHOUSE an approved
-- warehouse (replace CH08_WH in CREATE TASK below with an actual approved name).
-- Cost: DDL and insert use a warehouse; enabling TASK or DYNAMIC TABLE incurs ongoing cost.
-- Run this file only in a dedicated disposable schema; object names are prefixed CH08_.
-- Do not use in production as-is. This script deliberately leaves the task SUSPENDED.

CREATE OR REPLACE TABLE CH08_BRONZE_EVENTS (
  event_id VARCHAR, provider VARCHAR, technology VARCHAR,
  interval_utc TIMESTAMP_NTZ, revision NUMBER,
  energy_mwh NUMBER(12,3), operation VARCHAR,
  ingested_at TIMESTAMP_NTZ
);
CREATE OR REPLACE STREAM CH08_BRONZE_STREAM
  ON TABLE CH08_BRONZE_EVENTS APPEND_ONLY = TRUE;
CREATE OR REPLACE TABLE CH08_SILVER_STATE (
  provider VARCHAR, technology VARCHAR, interval_utc TIMESTAMP_NTZ,
  event_id VARCHAR, revision NUMBER, energy_mwh NUMBER(12,3),
  operation VARCHAR, ingested_at TIMESTAMP_NTZ
);

-- Synthetic accepted fixture. Includes a duplicate delivery, an older revision,
-- and a delete tombstone; the quarantined negative measurement is excluded upstream.
INSERT INTO CH08_BRONZE_EVENTS VALUES
 ('A01','fingrid','WIND','2026-10-21 10:00:00',1,12,'UPSERT','2026-10-21 10:00:10'),
 ('A02','fingrid','SOLAR','2026-10-21 10:00:00',1,7,'UPSERT','2026-10-21 10:00:11'),
 ('A03','fingrid','HYDRO','2026-10-21 10:00:00',1,9,'UPSERT','2026-10-21 10:00:12'),
 ('A04','fingrid','NUCLEAR','2026-10-21 10:00:00',1,21,'UPSERT','2026-10-21 10:00:13'),
 ('A05','fingrid','IMPORT','2026-10-21 10:00:00',1,11,'UPSERT','2026-10-21 10:00:14'),
 ('A06','fingrid','BIOMASS','2026-10-21 10:00:00',1,4,'UPSERT','2026-10-21 10:00:15'),
 ('A07','fingrid','WIND','2026-10-21 10:00:00',2,14,'UPSERT','2026-10-21 10:05:00'),
 ('A07','fingrid','WIND','2026-10-21 10:00:00',2,14,'UPSERT','2026-10-21 10:05:01'),
 ('A08','fingrid','TEST','2026-10-21 10:00:00',1,1,'UPSERT','2026-10-21 10:05:02'),
 ('A09','fingrid','TEST','2026-10-21 10:00:00',2,NULL,'DELETE','2026-10-21 10:05:03'),
 ('A10','fingrid','HYDRO','2026-10-21 10:00:00',0,8,'UPSERT','2026-10-21 10:05:04');

-- Inspect without consuming: SELECT does NOT advance the stream offset.
SELECT event_id, technology, revision, METADATA$ACTION
FROM CH08_BRONZE_STREAM ORDER BY technology, revision;

-- MERGE is one transaction: stream offset advances on successful commit.
-- A production quality gate must quarantine invalid business events *before* this merge.
-- Choose and approve your warehouse name before executing CREATE TASK.
CREATE OR REPLACE TASK CH08_ENERGY_MERGE_TASK
  WAREHOUSE = CH08_WH
  WHEN SYSTEM$STREAM_HAS_DATA('CH08_BRONZE_STREAM')
AS
MERGE INTO CH08_SILVER_STATE AS t
USING (
  SELECT event_id, provider, technology, interval_utc,
         revision, energy_mwh, operation, ingested_at
  FROM CH08_BRONZE_STREAM
  WHERE METADATA$ACTION = 'INSERT'
    AND revision >= 0
    AND (operation = 'DELETE'
         OR (operation = 'UPSERT' AND energy_mwh >= 0))
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY provider, technology, interval_utc
    ORDER BY revision DESC, ingested_at DESC, event_id DESC
  ) = 1
) s
ON t.provider = s.provider AND t.technology = s.technology
   AND t.interval_utc = s.interval_utc
WHEN MATCHED AND (s.revision > t.revision OR
     (s.revision = t.revision AND s.ingested_at > t.ingested_at))
  THEN UPDATE SET t.event_id=s.event_id, t.revision=s.revision,
     t.energy_mwh=s.energy_mwh, t.operation=s.operation,
     t.ingested_at=s.ingested_at
WHEN NOT MATCHED THEN INSERT
  (provider, technology, interval_utc, event_id, revision, energy_mwh,
   operation, ingested_at)
  VALUES (s.provider,s.technology,s.interval_utc,s.event_id,s.revision,
   s.energy_mwh,s.operation,s.ingested_at);

-- MANUAL ACTIVATION (not executed by default):
-- ALTER TASK CH08_ENERGY_MERGE_TASK RESUME;
-- EXECUTE TASK CH08_ENERGY_MERGE_TASK;
-- SELECT COUNT(*) AS visible_rows, SUM(energy_mwh) AS total_mwh
-- FROM CH08_SILVER_STATE WHERE operation = 'UPSERT';
-- EXPECTED AFTER SUCCESSFUL COMMIT: visible_rows = 6, total_mwh = 66.000.
-- ALTER TASK CH08_ENERGY_MERGE_TASK SUSPEND;
-- Cleanup only after review and approval:
-- DROP TASK IF EXISTS CH08_ENERGY_MERGE_TASK;
-- DROP STREAM IF EXISTS CH08_BRONZE_STREAM;
-- DROP TABLE IF EXISTS CH08_SILVER_STATE;
-- DROP TABLE IF EXISTS CH08_BRONZE_EVENTS;
