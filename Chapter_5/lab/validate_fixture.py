"""Chapter 5 offline source contract and semantic acceptance tests.

Synthetic sample only. Does not connect to Snowflake or external sources.
Run: python validate_fixture.py [--data-dir PATH] [--manifest PATH]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

HEADER = ["source_code", "metric", "interval_start_utc", "value_mwh"]
VERSIONS = {"energy_r1.csv": 1, "energy_r2.csv": 2}
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
EXPECTED_ROWS = 8
EXPECTED_ACCEPTED = 6
EXPECTED_TOTAL = Decimal("97.500")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_manifest(data_dir: Path, manifest_path: Path) -> None:
    rows = []
    for name, revision in sorted(VERSIONS.items(), key=lambda kv: kv[1]):
        file = data_dir / name
        with file.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != HEADER:
                raise ValueError(f"Header mismatch in {name}: {reader.fieldnames!r}")
            lines = list(reader)
            if any(row.get(None) is not None for row in lines):
                raise ValueError(f"Extra CSV fields in {name}")
        rows.append({
            "batch_id": "CH05_SYNTHETIC_20260115",
            "file_name": name,
            "revision_number": revision,
            "sha256": sha256_file(file),
            "size_bytes": file.stat().st_size,
            "expected_rows": len(lines),
            "contract_version": "v1",
            "published_at_utc": f"2026-01-15T0{revision}:00:00Z",
            "license": "AUTHOR_CREATED_SYNTHETIC",
            "source_url": "synthetic://book/ch05",
        })
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def evaluate(data_dir: Path, manifest_path: Path) -> dict:
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        manifest = list(csv.DictReader(handle))
    if {row["file_name"] for row in manifest} != set(VERSIONS):
        raise ValueError("Manifest must list the two declared source files exactly once")
    if len(manifest) != len(VERSIONS):
        raise ValueError("Duplicate file in manifest")
    accepted = {}
    rejected = []
    physical = 0
    valid_rows = 0
    for entry in manifest:
        name = entry["file_name"]
        if int(entry["revision_number"]) != VERSIONS[name]:
            raise ValueError(f"Unexpected revision for {name}")
        file = data_dir / name
        if sha256_file(file) != entry["sha256"]:
            raise ValueError(f"Checksum mismatch: {name}")
        if file.stat().st_size != int(entry["size_bytes"]):
            raise ValueError(f"Byte count mismatch: {name}")
        with file.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != HEADER:
                raise ValueError(f"Header mismatch: {name}")
            count = 0
            for line, row in enumerate(reader, start=2):
                if row.get(None) is not None or None in row.values():
                    raise ValueError(f"Wrong CSV field count in {name}, physical line {line}")
                count += 1
                physical += 1
                identity = (row["source_code"], row["metric"], row["interval_start_utc"])
                reasons = []
                if row["source_code"] not in {"SOLAR_FI", "WIND_FI"}:
                    reasons.append("UNKNOWN_SOURCE")
                if row["metric"] != "generation_mwh":
                    reasons.append("UNKNOWN_METRIC")
                try:
                    when = datetime.strptime(row["interval_start_utc"], TIMESTAMP_FORMAT)
                    if when.year != 2026:
                        reasons.append("OUT_OF_SCOPE_TIME")
                except (ValueError, TypeError):
                    reasons.append("BAD_TIMESTAMP")
                try:
                    value = Decimal(row["value_mwh"])
                    if not value.is_finite() or value < 0:
                        reasons.append("INVALID_MWH_RANGE")
                except (InvalidOperation, TypeError):
                    reasons.append("NONNUMERIC_MWH")
                    value = None
                if reasons:
                    rejected.append({"filename": name, "line": line, "reasons": reasons, "raw": row})
                    continue
                valid_rows += 1
                revision = int(entry["revision_number"])
                current = accepted.get(identity)
                if current is None or revision > current[0]:
                    accepted[identity] = (revision, value, name, line)
                elif revision == current[0]:
                    raise ValueError(f"Ambiguous duplicate revision: {identity!r}")
            if count != int(entry["expected_rows"]):
                raise ValueError(f"Row count mismatch: {name}")
    total = sum((row[1] for row in accepted.values()), Decimal("0.000"))
    result = {
        "fixture_type": "AUTHOR_CREATED_SYNTHETIC",
        "file_count": len(manifest),
        "bronze_rows": physical,
        "numeric_valid_rows": valid_rows,
        "quarantined_rows": len(rejected),
        "superseded_rows": valid_rows - len(accepted),
        "accepted_business_keys": len(accepted),
        "accepted_total_mwh": str(total.quantize(Decimal("0.001"))),
        "quarantine": rejected,
        "accepted_rows": [
            {"key": list(key), "revision": v[0], "mwh": str(v[1]), "file": v[2]}
            for key, v in sorted(accepted.items())
        ],
    }
    return result


def verify_expected(result: dict) -> None:
    assert result["bronze_rows"] == EXPECTED_ROWS, result
    assert result["accepted_business_keys"] == EXPECTED_ACCEPTED, result
    assert Decimal(result["accepted_total_mwh"]) == EXPECTED_TOTAL, result
    assert result["quarantined_rows"] == 1, result
    assert result["superseded_rows"] == 1, result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).parent / "data")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).parent / "source_manifest.csv")
    args = parser.parse_args()
    result = evaluate(args.data_dir, args.manifest)
    verify_expected(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
