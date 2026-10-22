-- OPTIONAL, BILLABLE LAB. All AI invocations are commented on purpose.
-- NOT EXECUTED against Snowflake. Obtain admin/security and budget approval.
-- Model IDs, AI SQL signatures, regions, account roles and charges change.
-- Verify: https://docs.snowflake.com/en/sql-reference/functions/ai_complete
-- Verify: https://docs.snowflake.com/en/sql-reference/functions/ai_classify
-- Verify: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cross-region-inference

-- Read-only account check (requires suitable privilege):
-- SHOW PARAMETERS LIKE 'CORTEX_ENABLED_CROSS_REGION' IN ACCOUNT;

-- Examples below must be enabled one-by-one only after prerequisites reviewed.
-- SELECT AI_CLASSIFY('Turbine B stopped after inverter alarm',
--                    ['maintenance','operations','commercial']) AS labels;

-- SELECT AI_COMPLETE('<approved_model_id>',
--   'Summarize only the cited synthetic note; abstain without evidence.') AS summary;

-- Cortex Search and Cortex Analyst require separate configuration, access and
-- cost testing; neither is created by this script. No account changes occur.
