"""Chapter 9: deterministic energy transform. No network access by default.

Snowpark is imported only inside build_snowpark_dataframe; Python stdlib can
reproduce the rules without a Snowflake account. All data are synthetic.
"""
from __future__ import annotations
import csv
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

KEY = ('PROVIDER', 'TECHNOLOGY', 'INTERVAL_UTC')
REQUIRED = ('EVENT_ID','PROVIDER','TECHNOLOGY','INTERVAL_UTC','REVISION','ENERGY_MWH','OPERATION')


def validate(raw: dict[str, str]) -> dict[str, Any]:
    missing = [field for field in REQUIRED if not raw.get(field, '').strip()]
    if missing:
        raise ValueError('missing fields: '+','.join(missing))
    op = raw['OPERATION'].upper()
    if op not in {'UPSERT', 'DELETE'}:
        raise ValueError('unrecognised operation')
    try:
        rev = int(raw['REVISION'])
        qty = Decimal(raw['ENERGY_MWH'])
    except (ValueError, InvalidOperation):
        raise ValueError('invalid numeric value') from None
    if rev < 1 or not qty.is_finite() or qty < 0:
        raise ValueError('invalid nonnegative reading or revision')
    if not raw['INTERVAL_UTC'].endswith('Z'):
        raise ValueError('interval must be explicit UTC Z')
    return dict(raw, REVISION=rev, ENERGY_MWH=qty, OPERATION=op)


def transform(records: Iterable[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, str]], dict[str, int]]:
    """Highest revision per business key wins; identical event IDs deduplicated."""
    current: dict[tuple[str, ...], dict[str, Any]] = {}
    seen: set[str] = set()
    rejected: list[dict[str, str]] = []
    counter = Counter()
    for raw in records:
        counter['delivered'] += 1
        try:
            row = validate(raw)
        except ValueError as exc:
            rejected.append({'EVENT_ID': raw.get('EVENT_ID',''), 'REASON': str(exc)})
            counter['rejected'] += 1
            continue
        event_id = row['EVENT_ID']
        if event_id in seen:
            counter['replays'] += 1
            continue
        key = tuple(row[k] for k in KEY)
        prior = current.get(key)
        # A conflicting equal revision must be quarantined in a true production
        # implementation. This fixture deliberately uses unique revision IDs.
        if prior and prior['REVISION'] == row['REVISION'] and prior != row:
            rejected.append({'EVENT_ID': event_id, 'REASON': 'conflicting revision'})
            counter['conflicts'] += 1
            continue
        seen.add(event_id)
        counter['accepted_events'] += 1
        if not prior or row['REVISION'] > prior['REVISION']:
            current[key] = row
    final = [r for r in current.values() if r['OPERATION'] == 'UPSERT']
    final.sort(key=lambda r:(r['INTERVAL_UTC'],r['TECHNOLOGY']))
    counter['visible_rows'] = len(final)
    counter['tombstone_keys'] = sum(r['OPERATION']=='DELETE' for r in current.values())
    return final, rejected, dict(counter)


def build_snowpark_dataframe(session, source_table: str, dimension_table: str):
    """Build lazy Snowpark plan; no action or writes. Requires a live or mock session.

    Accepted, already-conformed bronze rows are assumed: one approved revision
    per key; duplicate/revision resolution belongs in the ingestion contract.
    """
    from snowflake.snowpark.functions import col, lit, sum as sf_sum
    fact = (session.table(source_table)
            .filter((col('OPERATION') == lit('UPSERT')) & (col('ENERGY_MWH') >= lit(0)))
            .select('PROVIDER','TECHNOLOGY','INTERVAL_UTC','ENERGY_MWH'))
    dims = session.table(dimension_table).select('TECHNOLOGY','CATEGORY')
    return (fact.join(dims, ['TECHNOLOGY'], 'left')
            .group_by('CATEGORY','INTERVAL_UTC')
            .agg(sf_sum(col('ENERGY_MWH')).alias('TOTAL_MWH')))


def _read_fixture(path: Path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    root = Path(__file__).resolve().parent
    rows = _read_fixture(root/'data'/'energy_revisions.csv')
    final, rejected, metrics = transform(rows)
    out = root/'output'
    out.mkdir(exist_ok=True)
    with (out/'silver_energy.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=REQUIRED)
        writer.writeheader()
        for row in final:
            writer.writerow({key: str(row[key]) for key in REQUIRED})
    with (out/'quarantine.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=['EVENT_ID','REASON'])
        writer.writeheader(); writer.writerows(rejected)
    total = sum((row['ENERGY_MWH'] for row in final), Decimal(0))
    summary = dict(metrics, total_mwh=f'{total:.3f}', unit='MWh', data='SYNTHETIC',cloud_executed=False)
    (out/'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
