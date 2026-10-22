-- Audit and classify the four synthetic raw input lines.
WITH classified AS (
 SELECT SOURCE_LINE, TRY_PARSE_JSON(RAW_LINE) AS P,
        CASE WHEN TRY_PARSE_JSON(RAW_LINE) IS NULL
                  THEN 'syntax_or_empty'
             WHEN NOT IS_OBJECT(TRY_PARSE_JSON(RAW_LINE))
                  THEN 'unexpected_top_level_type'
             WHEN TRY_PARSE_JSON(RAW_LINE):schema_version::NUMBER NOT IN (1,2)
                  THEN 'unsupported_version'
             ELSE 'parsed_object' END AS PARSE_CLASS
 FROM CH06_BRONZE_JSON
)
SELECT PARSE_CLASS, COUNT(*) AS envelope_count
FROM classified GROUP BY PARSE_CLASS ORDER BY PARSE_CLASS;
-- Parsed is not equivalent to accepted: one parsed_object fails numeric contract.

SELECT SOURCE_LINE, TYPEOF(TRY_PARSE_JSON(RAW_LINE)) AS TOP_LEVEL_TYPE
FROM CH06_BRONZE_JSON ORDER BY SOURCE_LINE;

SELECT COUNT(*) AS accepted_silver_rows, SUM(ENERGY_MWH) AS accepted_mwh
FROM CH06_SILVER;

SELECT PROVIDER, OBSERVED_AT_UTC, TECHNOLOGY, COUNT(*) AS copies
FROM CH06_SILVER
GROUP BY 1,2,3 HAVING COUNT(*) > 1;
-- Expected: zero duplicate business keys.
