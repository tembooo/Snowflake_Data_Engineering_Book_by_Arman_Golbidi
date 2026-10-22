# Chapter 1 — Finland Energy Analytics (synthetic offline check)

The data are **synthetic** and are not sourced from Fingrid or Statistics Finland. Each value is an average power in MW over the specified duration in minutes.

Run in this directory: `python chapter01_lab.py` (Python 3.9+; standard library only; no Snowflake credentials and no cloud costs).

Expected output: `{'SOLAR': 0.0, 'WIND': 245.0}`.

For a negative test, add a second row with the same `timestamp_utc` and `source`; the program should raise an `AssertionError` for the duplicate. Restore the sample afterward. For another negative test, set a `minutes` field to zero; the program should raise `AssertionError: Invalid interval`.

This minimal teaching script does not validate actual timestamp parsing, missing readings, real data permissions, negative power constraints, or live Snowflake integration. In real systems use explicit validation rather than Python assertions where assertions could be disabled.
