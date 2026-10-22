-- Chapter 05 / run within a disposable DB + schema with a restricted role.
-- Confirm active role and context before creating or loading objects.
SELECT CURRENT_ROLE(), CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_WAREHOUSE();

CREATE FILE FORMAT IF NOT EXISTS ff_energy_csv
    TYPE = CSV
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    ENCODING = 'UTF8'
    NULL_IF = ('__MISSING__')
    EMPTY_FIELD_AS_NULL = FALSE
    ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE;

CREATE STAGE IF NOT EXISTS stg_energy
    FILE_FORMAT = ff_energy_csv;

-- From a client supporting PUT (local paths are illustrative):
-- PUT file:///absolute/path/data/energy_r1.csv @stg_energy AUTO_COMPRESS=FALSE OVERWRITE=FALSE;
-- PUT file:///absolute/path/data/energy_r2.csv @stg_energy AUTO_COMPRESS=FALSE OVERWRITE=FALSE;
LIST @stg_energy;
