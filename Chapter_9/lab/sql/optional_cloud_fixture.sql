-- OPTIONAL CLOUD INTEGRATION, NEVER AUTOMATICALLY EXECUTED.
-- Execute ONLY after selecting an approved account, dedicated small warehouse,
-- disposable schema, and least-privilege role. Requires CREATE TABLE privilege.
-- These are TEMP tables bound to the current Snowflake session.
-- This is a conformed latest-state fixture, NOT a raw revisioned event stream.
CREATE TEMP TABLE ENERGY_SILVER (
 PROVIDER VARCHAR, TECHNOLOGY VARCHAR, INTERVAL_UTC VARCHAR,
 ENERGY_MWH NUMBER(14,3), OPERATION VARCHAR
);
INSERT INTO ENERGY_SILVER VALUES
 ('DEMO_GRID','Wind','2026-03-01T10:00:00Z',14.000,'UPSERT'),
 ('DEMO_GRID','Solar','2026-03-01T10:00:00Z',6.000,'UPSERT'),
 ('DEMO_GRID','Hydro','2026-03-01T10:00:00Z',18.000,'UPSERT'),
 ('DEMO_GRID','Nuclear','2026-03-01T10:00:00Z',16.000,'UPSERT'),
 ('DEMO_GRID','Bioenergy','2026-03-01T10:00:00Z',8.000,'UPSERT'),
 ('DEMO_GRID','Other','2026-03-01T10:00:00Z',4.000,'UPSERT');
CREATE TEMP TABLE TECHNOLOGY_DIM (TECHNOLOGY VARCHAR, CATEGORY VARCHAR);
INSERT INTO TECHNOLOGY_DIM VALUES
 ('Wind','Renewable'),('Solar','Renewable'),('Hydro','Renewable'),
 ('Bioenergy','Renewable'),('Nuclear','OtherLowCarbon'),('Other','Other');
-- Query below provides an SQL oracle; no persisted output table.
SELECT d.CATEGORY, f.INTERVAL_UTC, SUM(f.ENERGY_MWH) AS TOTAL_MWH
FROM ENERGY_SILVER f
LEFT JOIN TECHNOLOGY_DIM d USING (TECHNOLOGY)
GROUP BY d.CATEGORY, f.INTERVAL_UTC
ORDER BY d.CATEGORY;
-- EXPECTED: Other=4.000, OtherLowCarbon=16.000, Renewable=46.000.
-- Temp tables are removed on session termination; never drop shared schemas.
