-- Educational synthetic fixture; source raw seed is immutable input.
WITH typed AS (
  SELECT
    CAST(event_id AS VARCHAR) AS event_id,
    CAST(provider AS VARCHAR) AS provider,
    CAST(technology AS VARCHAR) AS technology,
    CAST(interval_utc AS VARCHAR) AS interval_utc,
    TRY_TO_NUMBER(revision) AS revision,
    TRY_TO_DECIMAL(energy_mwh, 18, 3) AS energy_mwh,
    UPPER(CAST(operation AS VARCHAR)) AS operation
  FROM {{ ref('energy_revisions') }}
), valid AS (
  SELECT * FROM typed
  WHERE event_id IS NOT NULL AND TRIM(event_id) <> ''
    AND provider IS NOT NULL AND TRIM(provider) <> ''
    AND technology IS NOT NULL AND TRIM(technology) <> ''
    AND interval_utc IS NOT NULL
    AND REGEXP_LIKE(interval_utc, '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z')
    AND revision >= 1
    AND energy_mwh >= 0
    AND operation IN ('UPSERT', 'DELETE')
)
SELECT * FROM valid
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY event_id
  ORDER BY revision DESC, energy_mwh DESC
) = 1
