-- Chapter 07 monitoring examples. Adapt names and privileges to your account.
-- Event time / visibility time in this simulator are pre-recorded. In a real
-- deployment record publisher, broker, ingest, and query visibility timestamps
-- separately, with clock synchronization and UTC normalization.
-- These queries have NOT BEEN RUN IN SNOWFLAKE.

-- 1. Detect duplicates in the raw event log.
SELECT EVENT_ID, COUNT(*) AS COPIES
FROM ENERGY_TELEMETRY_RAW
GROUP BY EVENT_ID
HAVING COUNT(*) > 1;

-- 2. Create a latest-revision logical projection. Tie-breakers are explicit.
WITH ranked AS (
 SELECT *, ROW_NUMBER() OVER (
  PARTITION BY TECHNOLOGY, EVENT_UTC
  ORDER BY REVISION DESC, RECEIVED_UTC DESC, EVENT_ID DESC
 ) AS rn
 FROM ENERGY_TELEMETRY_RAW
 WHERE ENERGY_MWH >= 0
)
SELECT TECHNOLOGY, EVENT_UTC, ENERGY_MWH, REVISION
FROM ranked WHERE rn = 1 ORDER BY EVENT_UTC, TECHNOLOGY;

-- 3. Ingest-to-observation age (NOT a true measured event-to-query latency).
SELECT TECHNOLOGY,
       DATEDIFF('second', EVENT_UTC, RECEIVED_UTC) AS event_to_receive_seconds
FROM ENERGY_TELEMETRY_RAW
WHERE EVENT_UTC IS NOT NULL AND RECEIVED_UTC IS NOT NULL;

-- 4. Separate privileges required for ACCOUNT_USAGE (up to hours of latency).
-- SELECT TO_DATE(START_TIME) AS day, PIPE_NAME,
--        SUM(CREDITS_USED) AS credits, SUM(BYTES_BILLED) AS bytes_billed
-- FROM SNOWFLAKE.ACCOUNT_USAGE.PIPE_USAGE_HISTORY
-- WHERE START_TIME >= DATEADD('day',-7,CURRENT_TIMESTAMP())
-- GROUP BY 1,2 ORDER BY 1,2;
