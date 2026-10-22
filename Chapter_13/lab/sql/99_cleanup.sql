-- CH13 CLEANUP PLAYBOOK - READ ONLY BY DEFAULT.
-- DO NOT EXECUTE DESTRUCTIVE ACTIONS without sandbox-owner approval.
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_ACCOUNT();
SHOW DATABASES LIKE 'BOOK13_SANDBOX';
SHOW ROLES LIKE 'BOOK13_%';
-- Review: masking-policy bindings; role-to-user memberships; share refs;
-- downstream consumers, Time Travel and recovery consequences.
-- Destructive commands intentionally commented; separate approved ticket:
-- DROP DATABASE BOOK13_SANDBOX;
-- DROP ROLE BOOK13_ANALYST;
-- DROP ROLE BOOK13_GOLD_READER;
-- DROP ROLE BOOK13_LOADER;
-- DROP ROLE BOOK13_STEWARD;
