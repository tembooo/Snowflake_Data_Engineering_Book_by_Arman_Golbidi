"""Independent offline reference for the Chapter 4 SYNTHETIC fixture.

No Snowflake access, credentials, external dependencies or network required.
Use: python validate_fixture.py
"""
from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_RAW = 7
EXPECTED_ACCEPTED = 6
EXPECTED_MWH = Decimal("97.500")


def read_rows(path: Path = ROOT / "energy_sample.csv") -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def choose_accepted(rows: list[dict]) -> dict[tuple[str, str, str], dict]:
    accepted = {}
    for row in rows:
        assert row["source_code"] and row["metric_code"], "Missing business key"
        start = datetime.fromisoformat(row["interval_text"])
        loaded = datetime.fromisoformat(row["loaded_at_utc"])
        try:
            energy = Decimal(row["mwh_text"])
        except InvalidOperation as exc:
            raise AssertionError(f"Cannot parse {row['raw_id']}") from exc
        assert energy >= 0, f"Negative energy for raw_id {row['raw_id']}"
        assert start.minute == start.second == 0, "Expected full hourly start"
        assert row["metric_code"] == "generation_mwh", "Unapproved metric"
        key = (row["source_code"], row["metric_code"], row["interval_text"])
        record = {**row, "energy_mwh": energy, "loaded": loaded, "raw_id_num": int(row["raw_id"])}
        previous = accepted.get(key)
        if previous is None or (loaded, record["raw_id_num"]) > (previous["loaded"], previous["raw_id_num"]):
            accepted[key] = record
    return accepted


def validate(rows: list[dict]) -> dict:
    accepted = choose_accepted(rows)
    total = sum((r["energy_mwh"] for r in accepted.values()), Decimal("0"))
    by_source = Counter(r["source_code"] for r in accepted.values())
    assert len(rows) == EXPECTED_RAW, f"Expected {EXPECTED_RAW} source events"
    assert len(accepted) == EXPECTED_ACCEPTED, f"Expected {EXPECTED_ACCEPTED} accepted observations"
    assert total == EXPECTED_MWH, f"Expected {EXPECTED_MWH} MWh, got {total}"
    assert by_source == Counter({"SOLAR_FI": 3, "WIND_FI": 3}), by_source
    assert accepted[("SOLAR_FI", "generation_mwh", "2026-01-15 01:00:00")]["raw_id"] == "7"
    return {"raw_rows": len(rows), "accepted_rows": len(accepted), "accepted_mwh": str(total), "corrected_raw_id": 7}


if __name__ == "__main__":
    results = validate(read_rows())
    for key, value in results.items():
        print(f"{key}: {value}")
    print("PASS: synthetic fixture and correction semantics verified OFFLINE")
