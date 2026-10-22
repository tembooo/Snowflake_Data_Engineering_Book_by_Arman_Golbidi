SELECT provider, technology, interval_utc, COUNT(*) AS n
FROM {{ ref('int_energy_current') }}
GROUP BY provider, technology, interval_utc
HAVING COUNT(*) > 1
