-- 1. Structural/parser validation on a separate table; no transformed COPY.
-- VALIDATION_MODE reports parse/load type errors, NOT semantic quality failures.
CREATE TEMPORARY TABLE csv_shape_check (
   source_code VARCHAR,
   metric VARCHAR,
   interval_text VARCHAR,
   value_text VARCHAR
);
COPY INTO csv_shape_check
FROM @stg_energy
FILE_FORMAT = (FORMAT_NAME = ff_energy_csv)
VALIDATION_MODE = RETURN_ALL_ERRORS;

-- 2. Semantic rejections retained as a VIEW (bronze remains untouched).
CREATE OR REPLACE VIEW ch05_rejected_energy AS
SELECT source_code, metric, interval_text, value_text,
       source_file, source_row,
       CASE
         WHEN source_code NOT IN ('SOLAR_FI','WIND_FI') THEN 'UNKNOWN_SOURCE'
         WHEN metric <> 'generation_mwh' THEN 'UNKNOWN_METRIC'
         WHEN TRY_TO_TIMESTAMP_NTZ(interval_text,'YYYY-MM-DD HH24:MI:SS') IS NULL
           THEN 'BAD_TIMESTAMP'
         WHEN TRY_TO_DECIMAL(value_text,18,3) IS NULL
           THEN 'NONNUMERIC_MWH'
         WHEN TRY_TO_DECIMAL(value_text,18,3) < 0
           THEN 'INVALID_MWH_RANGE'
         ELSE 'REVIEW'
       END AS reject_reason
FROM bronze_energy
WHERE source_code NOT IN ('SOLAR_FI','WIND_FI')
   OR metric <> 'generation_mwh'
   OR TRY_TO_TIMESTAMP_NTZ(interval_text,'YYYY-MM-DD HH24:MI:SS') IS NULL
   OR TRY_TO_DECIMAL(value_text,18,3) IS NULL
   OR TRY_TO_DECIMAL(value_text,18,3) < 0;

-- 3. This fixture has an explicit two-file approval manifest. A production
--    pipeline should load and validate approved manifest records independently.
CREATE OR REPLACE VIEW ch05_accepted_energy AS
WITH approved_file_versions AS (
  SELECT column1 AS file_name, column2 AS revision_number
  FROM VALUES ('energy_r1.csv',1), ('energy_r2.csv',2)
), parsed AS (
  SELECT b.source_code, b.metric, b.interval_text,
         TRY_TO_TIMESTAMP_NTZ(b.interval_text,'YYYY-MM-DD HH24:MI:SS') AS interval_start_utc,
         TRY_TO_DECIMAL(b.value_text,18,3) AS energy_mwh,
         b.source_file, b.source_row, a.revision_number
  FROM bronze_energy b
  JOIN approved_file_versions a ON ENDSWITH(b.source_file,a.file_name)
), eligible AS (
  SELECT * FROM parsed
  WHERE source_code IN ('SOLAR_FI','WIND_FI')
    AND metric = 'generation_mwh'
    AND interval_start_utc IS NOT NULL
    AND energy_mwh >= 0
)
SELECT source_code, metric, interval_start_utc, energy_mwh,
       revision_number, source_file, source_row
FROM eligible
QUALIFY ROW_NUMBER() OVER (
   PARTITION BY source_code, metric, interval_start_utc
   ORDER BY revision_number DESC, source_file DESC, source_row DESC
) = 1;

-- 4. Independent release checks (run and inspect results).
SELECT COUNT(*) AS raw_rows,
       COUNT(DISTINCT source_file) AS files_seen
FROM bronze_energy;
SELECT COUNT(*) AS rejected_rows FROM ch05_rejected_energy;
SELECT COUNT(*) AS accepted_rows,
       SUM(energy_mwh) AS accepted_total_mwh
FROM ch05_accepted_energy;
SELECT source_code, metric, interval_start_utc, COUNT(*) AS count_per_key
FROM ch05_accepted_energy
GROUP BY source_code, metric, interval_start_utc
HAVING COUNT(*) > 1;
-- Acceptance: 8 raw, 2 files, 1 rejected, 6 accepted, 97.500 MWh,
--             and ZERO key duplicates. Capture observed results (not assumptions).
