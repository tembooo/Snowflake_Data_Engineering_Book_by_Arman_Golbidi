-- SAFE BY DEFAULT: destructive actions are deliberately COMMENTED OUT.
-- After written approval: inspect current account and full object/dependency list.
SELECT CURRENT_ACCOUNT(), CURRENT_ROLE(), CURRENT_DATABASE();
SHOW TABLES LIKE 'ENERGY_READING' IN SCHEMA BOOK_CH03_DEV.LAB;
SHOW WAREHOUSES LIKE 'BOOK_CH03_XS';

-- Only an authorised operator may suspend a dedicated training warehouse.
-- ALTER WAREHOUSE BOOK_CH03_XS SUSPEND;

-- Only enable if the object was created solely for this lab and no other users
-- or sessions depend on it. Prefer granular removal; never blindly delete
-- a shared database, role or monitoring object to satisfy a book example.
-- DROP TABLE IF EXISTS BOOK_CH03_DEV.LAB.ENERGY_READING;
-- DROP SCHEMA IF EXISTS BOOK_CH03_DEV.LAB;
-- DROP WAREHOUSE IF EXISTS BOOK_CH03_XS;
-- Deliberately no DROP DATABASE / DROP ROLE / DROP RESOURCE MONITOR.
