-- Chapter 6: parsed JSON -> versioned array -> typed silver.
-- Requires a session with CH06_BRONZE_JSON loaded using json_ingestion.sql.
-- The full envelope is accepted only if all three expected readings validate.
CREATE OR REPLACE TEMPORARY TABLE CH06_SILVER AS
WITH parsed AS (
  SELECT SOURCE_LINE, TRY_PARSE_JSON(RAW_LINE) AS PAYLOAD
  FROM CH06_BRONZE_JSON
),
versioned AS (
  SELECT SOURCE_LINE, PAYLOAD,
         PAYLOAD:schema_version::NUMBER AS SCHEMA_VERSION,
         CASE PAYLOAD:schema_version::NUMBER
           WHEN 1 THEN PAYLOAD:observations
           WHEN 2 THEN PAYLOAD:measurements
         END AS READINGS
  FROM parsed
  WHERE IS_OBJECT(PAYLOAD)
    AND PAYLOAD:schema_version::NUMBER IN (1,2)
    AND PAYLOAD:unit::VARCHAR = 'MWh'
    AND TRY_TO_TIMESTAMP_TZ(PAYLOAD:observed_at_utc::VARCHAR) IS NOT NULL
),
flattened AS (
  SELECT v.SOURCE_LINE, v.SCHEMA_VERSION,
         v.PAYLOAD:envelope_id::VARCHAR AS ENVELOPE_ID,
         v.PAYLOAD:provider::VARCHAR AS PROVIDER,
         TRY_TO_TIMESTAMP_TZ(v.PAYLOAD:observed_at_utc::VARCHAR) AS OBSERVED_AT_UTC,
         f.INDEX AS ARRAY_POSITION,
         f.VALUE:tech::VARCHAR AS TECHNOLOGY,
         TRY_TO_DECIMAL(f.VALUE:mwh::VARCHAR,18,3) AS ENERGY_MWH
  FROM versioned v,
       LATERAL FLATTEN(INPUT => v.READINGS) f
  WHERE IS_ARRAY(v.READINGS)
),
valid_envelopes AS (
  SELECT SOURCE_LINE
  FROM flattened
  GROUP BY SOURCE_LINE
  HAVING COUNT(*) = 3
     AND COUNT(DISTINCT TECHNOLOGY) = 3
     AND COUNT_IF(TECHNOLOGY IN ('wind','solar','hydro')
                  AND ENERGY_MWH IS NOT NULL
                  AND ENERGY_MWH BETWEEN 0 AND 100000) = 3
     AND COUNT_IF(PROVIDER IS NOT NULL AND ENVELOPE_ID IS NOT NULL) = 3
)
SELECT f.*
FROM flattened f
JOIN valid_envelopes v USING (SOURCE_LINE);

SELECT COUNT(*) AS accepted_readings,
       SUM(ENERGY_MWH) AS accepted_total_mwh
FROM CH06_SILVER;
-- Expected: 6 and 97.500 (not an actual Snowflake run result).
