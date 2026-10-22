-- Gold grain: UTC interval and technology. All quantities are synthetic MWh.
SELECT interval_utc, technology,
       CAST(SUM(energy_mwh) AS NUMBER(18,3)) AS energy_mwh
FROM {{ ref('int_energy_current') }}
GROUP BY interval_utc, technology
