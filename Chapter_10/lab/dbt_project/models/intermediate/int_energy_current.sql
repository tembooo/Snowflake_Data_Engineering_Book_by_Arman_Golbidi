-- Preserves the winning tombstone until after choosing the latest revision.
-- An equal-revision conflict must be separately quarantined before publication.
WITH latest AS (
 SELECT event_id, provider, technology, interval_utc,
        revision, energy_mwh, operation
 FROM {{ ref('stg_energy_events') }}
 QUALIFY ROW_NUMBER() OVER (
   PARTITION BY provider, technology, interval_utc
   ORDER BY revision DESC, event_id DESC
 ) = 1
)
SELECT provider,technology,interval_utc,revision,energy_mwh,event_id
FROM latest
WHERE operation = 'UPSERT'
