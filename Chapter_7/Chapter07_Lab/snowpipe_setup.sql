-- Snowflake Data Engineering, Chapter 07 | illustrative integration scripts
-- NOT EXECUTED IN A LIVE SNOWFLAKE ACCOUNT. Review feature availability,
-- role permissions, region, cloud integration, and costs before running.
-- Use an approved least-privilege role, temporary learning database, and short-lived warehouse.

-- Example A: create a small raw landing table and a controlled manual file load.
CREATE TABLE IF NOT EXISTS ENERGY_TELEMETRY_RAW (
    event_id VARCHAR, technology VARCHAR,
    event_utc TIMESTAMP_NTZ, energy_mwh NUMBER(18,3),
    revision NUMBER, received_utc TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
);
-- Upload files to a designated external stage before using Snowpipe.
-- A Cloud admin must FIRST configure an allowed external stage and event integration.
-- These identifiers are intentionally placeholders, not runnable credentials.
-- CREATE OR REPLACE STAGE ENERGY_EVENTS_EXT
--   URL = 's3://REPLACE_WITH_AUTHORIZED_BUCKET/telemetry/'
--   STORAGE_INTEGRATION = REPLACE_WITH_APPROVED_STORAGE_INTEGRATION
--   FILE_FORMAT = (TYPE=JSON);
-- CREATE OR REPLACE PIPE ENERGY_FILE_PIPE AUTO_INGEST=FALSE AS
--   COPY INTO ENERGY_TELEMETRY_RAW
--   FROM (SELECT $1:event_id::VARCHAR,
--                $1:technology::VARCHAR,
--                TRY_TO_TIMESTAMP_NTZ($1:event_utc::VARCHAR),
--                TRY_TO_DECIMAL($1:energy_mwh::VARCHAR,18,3),
--                TRY_TO_NUMBER($1:revision::VARCHAR),
--                CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
--         FROM @ENERGY_EVENTS_EXT)
--   FILE_FORMAT=(TYPE=JSON);
-- NOTE: Auto-ingest requires a supported cloud event integration/notification
-- setup. Merely setting AUTO_INGEST=TRUE does not provision a cloud queue.
-- SELECT SYSTEM$PIPE_STATUS('ENERGY_FILE_PIPE');

-- Example B: HIGH-PERFORMANCE streaming pipe; NOT the classic SDK syntax.
-- Define its target in your own separate, disposable schema, then use an
-- approved high-performance SDK/REST client to send rows to this pipe.
-- CREATE OR REPLACE PIPE ENERGY_EVENTS_STREAM_PIPE AS
--   COPY INTO ENERGY_TELEMETRY_RAW
--     (EVENT_ID, TECHNOLOGY, EVENT_UTC, ENERGY_MWH, REVISION)
--   FROM (SELECT $1:event_id::VARCHAR,
--                $1:technology::VARCHAR,
--                TRY_TO_TIMESTAMP_NTZ($1:event_utc::VARCHAR),
--                TRY_TO_DECIMAL($1:energy_mwh::VARCHAR,18,3),
--                TRY_TO_NUMBER($1:revision::VARCHAR)
--         FROM TABLE(DATA_SOURCE(TYPE => 'STREAMING')));
-- Authorization and client offsets are deliberately not hard-coded.
-- The original source event log, not Snowflake, determines source replay order.

-- Non-destructive verification only:
SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE();
