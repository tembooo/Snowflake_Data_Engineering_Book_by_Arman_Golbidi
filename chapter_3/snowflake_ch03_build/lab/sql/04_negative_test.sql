-- DANGEROUS BY DESIGN: only execute in isolated training account with approval.
-- EXPECTED: INSERT fails because BOOK_CH03_READER should have only SELECT.
-- STOP if it succeeds; roles/grants are too broad and data has been modified.
USE ROLE BOOK_CH03_READER;
USE SECONDARY ROLES NONE;
INSERT INTO BOOK_CH03_DEV.LAB.ENERGY_READING
  (OBS_ID, SOURCE, EVENT_UTC, POWER_MW)
VALUES (999, 'should_not_insert', CURRENT_TIMESTAMP()::TIMESTAMP_NTZ, 1.0);
