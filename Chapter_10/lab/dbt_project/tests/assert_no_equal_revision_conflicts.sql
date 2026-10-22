-- Flag conflicting values or operations at the winning revision of each business key.
WITH events AS (
 SELECT * FROM {{ ref('stg_energy_events') }}
), top_revision AS (
 SELECT provider,technology,interval_utc,MAX(revision) AS max_revision
 FROM events GROUP BY 1,2,3
)
SELECT e.provider,e.technology,e.interval_utc,e.revision
FROM events e JOIN top_revision r
 ON e.provider=r.provider AND e.technology=r.technology
 AND e.interval_utc=r.interval_utc AND e.revision=r.max_revision
GROUP BY 1,2,3,4
HAVING COUNT(DISTINCT e.operation || ':' || TO_VARCHAR(e.energy_mwh)) > 1
