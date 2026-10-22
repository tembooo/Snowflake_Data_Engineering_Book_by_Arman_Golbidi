-- Chapter 4 original model. SYNTHETIC DATA ONLY.
-- Prerequisite: current database is a disposable BOOK LAB database.
-- An authorized role must pre-create schema BOOK_CH04 in that database.
-- Destructive statements below replace only the named BOOK_CH04 objects.
-- STOP if current database/role is not your approved laboratory context.

SELECT CURRENT_DATABASE() AS current_database, CURRENT_ROLE() AS current_role,
       CURRENT_SCHEMA() AS current_schema, CURRENT_WAREHOUSE() AS current_warehouse;

CREATE OR REPLACE TRANSIENT TABLE book_ch04.raw_energy (
    raw_id NUMBER(18,0),
    source_code VARCHAR(32),
    metric_code VARCHAR(32),
    interval_text VARCHAR(32),
    mwh_text VARCHAR(32),
    loaded_at_utc TIMESTAMP_NTZ
);
INSERT INTO book_ch04.raw_energy
    (raw_id,source_code,metric_code,interval_text,mwh_text,loaded_at_utc)
VALUES
 (1,'SOLAR_FI','generation_mwh','2026-01-15 00:00:00','10.000','2026-01-15 00:10:00'),
 (2,'WIND_FI','generation_mwh','2026-01-15 00:00:00','20.000','2026-01-15 00:11:00'),
 (3,'SOLAR_FI','generation_mwh','2026-01-15 01:00:00','12.500','2026-01-15 01:10:00'),
 (4,'WIND_FI','generation_mwh','2026-01-15 01:00:00','21.000','2026-01-15 01:11:00'),
 (5,'SOLAR_FI','generation_mwh','2026-01-15 02:00:00','11.500','2026-01-15 02:10:00'),
 (6,'WIND_FI','generation_mwh','2026-01-15 02:00:00','22.000','2026-01-15 02:11:00'),
 (7,'SOLAR_FI','generation_mwh','2026-01-15 01:00:00','13.000','2026-01-15 03:00:00');

-- Temporary and transient staging can be reconstructed from raw inputs.
-- The parsed fact is only accepted when all source-contract checks pass.
CREATE OR REPLACE TRANSIENT TABLE book_ch04.stg_energy_accepted AS
WITH parsed AS (
 SELECT raw_id, source_code, metric_code,
        TRY_TO_TIMESTAMP_NTZ(interval_text) AS interval_start_utc,
        TRY_TO_DECIMAL(mwh_text,18,3) AS energy_mwh,
        loaded_at_utc
 FROM book_ch04.raw_energy
)
SELECT * FROM parsed
WHERE source_code IS NOT NULL AND metric_code='generation_mwh'
  AND interval_start_utc IS NOT NULL
  AND DATE_TRUNC('HOUR',interval_start_utc)=interval_start_utc
  AND energy_mwh IS NOT NULL AND energy_mwh >= 0
QUALIFY ROW_NUMBER() OVER (
 PARTITION BY source_code, metric_code, interval_start_utc
 ORDER BY loaded_at_utc DESC, raw_id DESC
)=1;

CREATE OR REPLACE TRANSIENT TABLE book_ch04.dim_source AS
SELECT column1::NUMBER(18,0) AS source_key,
       column2::VARCHAR(32) AS source_code,
       column3::VARCHAR(32) AS technology
FROM VALUES (1,'SOLAR_FI','solar'),(2,'WIND_FI','wind');

CREATE OR REPLACE TRANSIENT TABLE book_ch04.dim_metric AS
SELECT 1::NUMBER(18,0) AS metric_key,
       'generation_mwh'::VARCHAR(32) AS metric_code,
       'MWh'::VARCHAR(8) AS unit,
       'SUM over non-overlapping intervals and sources'::VARCHAR(128) AS aggregation_rule;

CREATE OR REPLACE TRANSIENT TABLE book_ch04.dim_date_utc AS
SELECT 20260115::NUMBER(8,0) AS utc_date_key,
       '2026-01-15'::DATE AS utc_date,
       2026::NUMBER(4,0) AS year_num,
       1::NUMBER(2,0) AS month_num;

CREATE OR REPLACE TRANSIENT TABLE book_ch04.fact_energy_hourly AS
SELECT s.source_key, m.metric_key,
       d.utc_date_key, v.source_code, v.metric_code,
       v.interval_start_utc, v.energy_mwh,
       v.raw_id, v.loaded_at_utc
FROM book_ch04.stg_energy_accepted AS v
JOIN book_ch04.dim_source AS s ON v.source_code=s.source_code
JOIN book_ch04.dim_metric AS m ON v.metric_code=m.metric_code
JOIN book_ch04.dim_date_utc AS d
  ON TO_DATE(v.interval_start_utc)=d.utc_date;

CREATE OR REPLACE VIEW book_ch04.v_daily_energy AS
SELECT source_code, TO_DATE(interval_start_utc) AS utc_day,
       SUM(energy_mwh) AS generation_mwh
FROM book_ch04.fact_energy_hourly
GROUP BY source_code, TO_DATE(interval_start_utc);

SELECT COUNT(*) AS accepted_rows, SUM(energy_mwh) AS accepted_mwh
FROM book_ch04.fact_energy_hourly;
-- Expected, NOT externally executed here: 6 rows, 97.500 MWh.
