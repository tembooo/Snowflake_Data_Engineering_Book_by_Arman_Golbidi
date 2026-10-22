-- CHAPTER 03: GRANT ADMINISTRATOR ONLY; NOT for the learner role.
-- A role with CREATE ROLE privileges creates BOOK_CH03_READER.
-- An appropriately authorised grant manager/owner applies subsequent grants.
-- Check managed-access schema settings and effective ownership first.
CREATE ROLE IF NOT EXISTS BOOK_CH03_READER;

GRANT USAGE ON WAREHOUSE BOOK_CH03_XS TO ROLE BOOK_CH03_READER;
GRANT USAGE ON DATABASE BOOK_CH03_DEV TO ROLE BOOK_CH03_READER;
GRANT USAGE ON SCHEMA BOOK_CH03_DEV.LAB TO ROLE BOOK_CH03_READER;
GRANT SELECT ON TABLE BOOK_CH03_DEV.LAB.ENERGY_READING
  TO ROLE BOOK_CH03_READER;

-- Explicit authorisation and named learner account required before enabling:
-- GRANT ROLE BOOK_CH03_READER TO USER YOUR_APPROVED_LAB_USERNAME;
-- NOTE: This SQL file spans operations that may need different admin roles.
-- Apply in approved separate sessions if your organisation requires it.
