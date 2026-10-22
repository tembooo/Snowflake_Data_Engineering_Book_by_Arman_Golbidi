-- Illustrative Snowflake-only SQL. NOT EXECUTED in a Snowflake account.
-- Prerequisite: authorised read on FINLAND_ENERGY_DEMO.GOLD.FCT_ENERGY_HOURLY.
-- Run selectively in YOUR disposable, approved environment. All names are samples.
-- Grain must be (interval_utc, technology); do not sum power (MW) as energy (MWh).
SELECT interval_utc, technology, SUM(energy_mwh) AS energy_mwh
FROM FINLAND_ENERGY_DEMO.GOLD.FCT_ENERGY_HOURLY
GROUP BY interval_utc, technology;

-- Data-quality acceptance checks; expected when fixture is loaded: six rows, 66 MWh.
SELECT COUNT(*) AS row_count, SUM(energy_mwh) AS total_mwh
FROM FINLAND_ENERGY_DEMO.GOLD.FCT_ENERGY_HOURLY
WHERE interval_utc = '2026-03-01T10:00:00Z'::TIMESTAMP_TZ;

SELECT interval_utc, technology, COUNT(*) AS count_at_grain
FROM FINLAND_ENERGY_DEMO.GOLD.FCT_ENERGY_HOURLY
GROUP BY 1,2 HAVING COUNT(*) > 1;

-- A separate source is required to claim a consumption or net-position metric.
-- Consumption 60 MWh is only an offline synthetic companion fixture.
