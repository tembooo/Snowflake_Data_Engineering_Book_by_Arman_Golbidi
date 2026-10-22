"""Chapter 6 offline JSON contract validator; no external dependencies or services.

Run: python validate_payloads.py
This is an original synthetic teaching fixture, not Finnish public energy data.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import json
from typing import Any

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "data" / "sample_api_payload.jsonl"
EXPECTED_TECH = {"wind", "solar", "hydro"}


def _utc(text: Any) -> str:
    if not isinstance(text, str) or not text.endswith("Z"):
        raise ValueError("observed_at_utc: UTC Z timestamp required")
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("observed_at_utc: invalid timestamp") from e
    if dt.tzinfo is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError("observed_at_utc: non-UTC offset")
    if not (0 <= dt.minute < 60 and dt.second == 0 and dt.minute == 0):
        raise ValueError("observed_at_utc: not hour-aligned")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_envelope(doc: Any, line_number: int) -> list[dict[str, Any]]:
    if not isinstance(doc, dict):
        raise ValueError("envelope must be an object")
    version = doc.get("schema_version")
    if type(version) is not int or version not in {1, 2}:
        raise ValueError("unsupported schema_version")
    provider = doc.get("provider")
    envelope_id = doc.get("envelope_id")
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError("missing provider")
    if not isinstance(envelope_id, str) or not envelope_id.strip():
        raise ValueError("missing envelope_id")
    if doc.get("unit") != "MWh":
        raise ValueError("required unit must be MWh")
    ts = _utc(doc.get("observed_at_utc"))
    array_key = "observations" if version == 1 else "measurements"
    readings = doc.get(array_key)
    if not isinstance(readings, list) or len(readings) != 3:
        raise ValueError(f"{array_key} must contain exactly three readings")
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, r in enumerate(readings):
        if not isinstance(r, dict):
            raise ValueError(f"reading {index} must be an object")
        tech = r.get("tech")
        if tech not in EXPECTED_TECH or tech in seen:
            raise ValueError(f"duplicate or unrecognized tech at index {index}")
        seen.add(tech)
        value = r.get("mwh")
        if type(value) not in {Decimal, int} or isinstance(value, bool):
            raise ValueError(f"mwh must be numeric at index {index}")
        d = Decimal(value)
        if not d.is_finite() or d < 0 or d > 100000:
            raise ValueError(f"mwh out of range at index {index}")
        results.append({
            "source_line": line_number,
            "envelope_id": envelope_id,
            "provider": provider,
            "observed_at_utc": ts,
            "technology": tech,
            "energy_mwh": d,
            "array_position": index,
            "schema_version": version,
        })
    if seen != EXPECTED_TECH:
        raise ValueError("technology coverage is incomplete")
    return results


def inspect_lines(lines: list[str]) -> dict[str, Any]:
    outcome: Counter[str] = Counter()
    accepted: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    keys: set[tuple[str, str, str]] = set()
    for number, raw in enumerate(lines, start=1):
        try:
            doc = json.loads(raw, parse_float=Decimal, parse_int=int)
        except (json.JSONDecodeError, ValueError) as exc:
            outcome["syntax_rejected"] += 1
            quarantine.append({"line": number, "reason": "syntax", "detail": str(exc)})
            continue
        try:
            candidate = validate_envelope(doc, number)
            for reading in candidate:
                key = (reading["provider"], reading["observed_at_utc"], reading["technology"])
                if key in keys:
                    raise ValueError(f"duplicate business key: {key}")
            accepted.extend(candidate)
            keys.update((r["provider"], r["observed_at_utc"], r["technology"]) for r in candidate)
            outcome["accepted_envelopes"] += 1
        except ValueError as exc:
            outcome["contract_rejected"] += 1
            quarantine.append({"line": number, "reason": "contract", "detail": str(exc)})
    result = {
        "physical_lines": len(lines),
        "accepted_envelopes": outcome["accepted_envelopes"],
        "syntax_rejected": outcome["syntax_rejected"],
        "contract_rejected": outcome["contract_rejected"],
        "accepted_readings": len(accepted),
        "accepted_total_mwh": str(sum((r["energy_mwh"] for r in accepted), Decimal("0")).quantize(Decimal("0.001"))),
        "quarantine": quarantine,
        "readings": [{**r, "energy_mwh": str(r["energy_mwh"])} for r in accepted],
    }
    assert (result["accepted_envelopes"] + result["syntax_rejected"] + result["contract_rejected"] == result["physical_lines"])
    return result


def main() -> None:
    lines = FIXTURE.read_text(encoding="utf-8").splitlines()
    report = inspect_lines(lines)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    (ROOT / "expected_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
