-- CH13 CLOUD INTEGRATION TEST PLAN — NO TEST WAS RUN IN SNOWFLAKE HERE.
-- Run each group with its intended, separately approved TEST USER.
-- At start of each session set USE SECONDARY ROLES NONE when permitted.
-- Do not treat syntax errors or missing setup as permission denials.

-- GROUP A: APPROVED ANALYST TEST IDENTITY.
USE SECONDARY ROLES NONE;
USE ROLE BOOK13_ANALYST;
SELECT CURRENT_USER() AS WHO, CURRENT_ROLE() AS AS_ROLE;
SELECT COUNT(*) AS ROWS_VISIBLE,
 SUM(MWH) AS TOTAL_MWH
FROM BOOK13_SANDBOX.GOLD.GENERATION_DAILY;
-- Expected ALLOW: 6 rows, 66.000 MWh in clean one-load fixture.

-- GROUP B: SEPARATE STATEMENT, EXPECT AUTHORIZATION ERROR:
SELECT COUNT(*) FROM BOOK13_SANDBOX.RAW.METER_EVENT;
-- If this succeeds, STOP and investigate inherited grants / user grants.

-- GROUP C: SEPARATE STATEMENT, EXPECT AUTHORIZATION ERROR:
INSERT INTO BOOK13_SANDBOX.RAW.METER_EVENT
(EVENT_ID,TECHNOLOGY,REGION,OCCURRED_UTC,MWH,SOURCE_BATCH)
VALUES ('NEGATIVE_TEST','WIND','FI-NORTH','2026-10-02 00:00:00',1,'deny');
-- If this succeeds, STOP, investigate and clean ONLY with approval.

-- GROUP D: WITH SEPARATE APPROVED LOADER TEST IDENTITY:
-- USE SECONDARY ROLES NONE;
-- USE ROLE BOOK13_LOADER;
-- SELECT CURRENT_ROLE(), CURRENT_USER();
-- Test INSERT with a fresh unique ID and rollback via a controlled
-- transaction if allowed, then verify analyst still cannot read RAW.
