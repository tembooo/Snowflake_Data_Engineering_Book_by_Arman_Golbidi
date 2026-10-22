SELECT provider, technology, interval_utc, energy_mwh
FROM {{ ref('int_energy_current') }}
WHERE energy_mwh < 0 OR energy_mwh IS NULL
