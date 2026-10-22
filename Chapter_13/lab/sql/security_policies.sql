-- CH13 SECURITY CHANGE PROPOSAL — privilege-affecting, NEVER AUTO-DEPLOY.
-- Review exact account, roles, existing object ownership and admin approvals.
-- Intended for an approved disposable BOOK13_SANDBOX from 00_bootstrap.sql.
-- Do not run as a student or with ACCOUNTADMIN as routine default.

-- 1: Privileges; run through separately approved security administration.
CREATE ROLE IF NOT EXISTS BOOK13_GOLD_READER;
CREATE ROLE IF NOT EXISTS BOOK13_ANALYST;
CREATE ROLE IF NOT EXISTS BOOK13_LOADER;
CREATE ROLE IF NOT EXISTS BOOK13_STEWARD;
GRANT USAGE ON DATABASE BOOK13_SANDBOX TO ROLE BOOK13_GOLD_READER;
GRANT USAGE ON SCHEMA BOOK13_SANDBOX.GOLD TO ROLE BOOK13_GOLD_READER;
GRANT SELECT ON TABLE BOOK13_SANDBOX.GOLD.GENERATION_DAILY
 TO ROLE BOOK13_GOLD_READER;
GRANT ROLE BOOK13_GOLD_READER TO ROLE BOOK13_ANALYST;
GRANT ROLE BOOK13_GOLD_READER TO ROLE BOOK13_STEWARD;
GRANT USAGE ON DATABASE BOOK13_SANDBOX TO ROLE BOOK13_LOADER;
GRANT USAGE ON SCHEMA BOOK13_SANDBOX.RAW TO ROLE BOOK13_LOADER;
GRANT INSERT ON TABLE BOOK13_SANDBOX.RAW.METER_EVENT
 TO ROLE BOOK13_LOADER;
-- Session execution and BI access also require separate USAGE on a suitable
-- warehouse and user assignments by an approved administrator; NOT supplied.
-- Explicitly NO SELECT on RAW to ANALYST, NO CREATE USER to LOADER.

-- 2: OPTIONAL Enterprise Edition or higher; governance/admin approval needed.
-- Create this policy through authorized policy deployment only.
-- CREATE MASKING POLICY BOOK13_SANDBOX.GOV.EMAIL_MASK
--  AS (val STRING) RETURNS STRING ->
--  CASE WHEN IS_ROLE_IN_SESSION('BOOK13_STEWARD')
--       THEN val ELSE '[MASKED]' END;
-- ALTER TABLE BOOK13_SANDBOX.GOLD.CONTACT_CONTEXT
--  MODIFY COLUMN CONTACT_EMAIL
--  SET MASKING POLICY BOOK13_SANDBOX.GOV.EMAIL_MASK;
-- Separate role grants to CONTACT_CONTEXT are intentionally not made here.
-- Classification tagging, row policies and sharing need a fresh edition/
-- region/permission check and dedicated authorized test users.
