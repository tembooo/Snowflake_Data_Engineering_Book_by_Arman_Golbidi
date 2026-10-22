-- Requires the approved two synthetic files to be present in @stg_energy.
-- Not yet executed against a live Snowflake account.
CREATE TABLE IF NOT EXISTS bronze_energy (
  source_code VARCHAR,
  metric VARCHAR,
  interval_text VARCHAR,
  value_text VARCHAR,
  source_file VARCHAR,
  source_row NUMBER,
  scanned_at TIMESTAMP_LTZ
);

-- Intentional COPY SELECT transformation to carry file+row provenance.
-- VALIDATION_MODE is NOT supported with this transformation form.
COPY INTO bronze_energy (
  source_code, metric, interval_text, value_text,
  source_file, source_row, scanned_at
)
FROM (
  SELECT t.$1, t.$2, t.$3, t.$4,
         METADATA$FILENAME,
         METADATA$FILE_ROW_NUMBER,
         METADATA$START_SCAN_TIME
  FROM @stg_energy (FILE_FORMAT => ff_energy_csv) t
)
ON_ERROR = ABORT_STATEMENT;

-- Save COPY query ID and its returned per-file records in a run log.
SELECT COUNT(*) AS bronze_rows,
       COUNT(DISTINCT source_file) AS staged_files
FROM bronze_energy;
-- Expected on a clean first run: 8 rows across two files.
