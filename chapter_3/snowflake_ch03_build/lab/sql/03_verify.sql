-- CHAPTER 03: read-only verification. Required: role BOOK_CH03_READER.
-- Use only if you have the role and are in the approved sandbox.
USE ROLE BOOK_CH03_READER;
USE SECONDARY ROLES NONE;
SELECT CURRENT_ACCOUNT() AS account_id,
       CURRENT_REGION() AS region,
       CURRENT_ROLE() AS active_role,
       CURRENT_WAREHOUSE() AS warehouse_name;

SELECT COUNT(*) AS row_count,
       MIN(POWER_MW) AS min_power_mw,
       MAX(POWER_MW) AS max_power_mw
FROM BOOK_CH03_DEV.LAB.ENERGY_READING;

SELECT OBS_ID, SOURCE, EVENT_UTC, POWER_MW
FROM BOOK_CH03_DEV.LAB.ENERGY_READING
ORDER BY OBS_ID;
