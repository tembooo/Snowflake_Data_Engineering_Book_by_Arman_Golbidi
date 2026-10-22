"""Ch11 offline semantic acceptance oracle, stdlib only, synthetic fixtures.

This is not a Power BI, Snowflake, or DAX execution engine.
"""
from __future__ import annotations
import csv
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from collections import Counter
import json

ROOT = Path(__file__).parent
EXPECTED = {'Wind', 'Solar', 'Hydro', 'Nuclear', 'Bioenergy', 'Other'}

def read_csv(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def utc_check(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.utcoffset() != timezone.utc.utcoffset(dt):
        raise ValueError('timestamps must be UTC')
    return dt

def calculate(generation, consumption, require_full=True):
    keys = set(); sums = Counter(); slots = set()
    for row in generation:
        k = (row['interval_utc'], row['technology'])
        if k in keys:
            raise ValueError(f'duplicate generation key: {k}')
        keys.add(k)
        utc_check(row['interval_utc'])
        value = Decimal(row['energy_mwh'])
        if not value.is_finite() or value < 0:
            raise ValueError('nonfinite or negative generation MWh')
        if row['technology'] not in EXPECTED:
            raise ValueError('unknown technology')
        sums[row['technology']] += value
        slots.add(row['interval_utc'])
    if len(slots) != 1:
        raise ValueError('fixture expects exactly one generation interval')
    if require_full and set(sums) != EXPECTED:
        raise ValueError('missing technology in generation snapshot')
    cons_keys = set(); cons = {};
    for row in consumption:
        k = (row['interval_utc'], row['geography'])
        if k in cons_keys: raise ValueError('duplicate consumption key')
        cons_keys.add(k)
        utc_check(row['interval_utc'])
        amount = Decimal(row['consumption_mwh'])
        if not amount.is_finite() or amount < 0:
            raise ValueError('invalid consumption MWh')
        if row['geography'] != 'FI':
            raise ValueError('unexpected geography')
        cons[row['interval_utc']] = amount
    interval = next(iter(slots))
    total = sum(sums.values(), Decimal('0'))
    consumption_mwh = cons.get(interval)
    wind_share = (sums['Wind']/total*100) if total else None
    return {
      'interval_utc': interval,
      'generation_mwh': total,
      'consumption_mwh': consumption_mwh,
      'net_mwh': total-consumption_mwh if consumption_mwh is not None else None,
      'wind_share_pct': wind_share,
      'generation_coverage': f'{len(set(sums))}/{len(EXPECTED)}',
      'row_count': len(generation),
      'limitations': ['synthetic single interval', 'not a real Finnish grid measurement',
                      'consumption separate illustrative source', 'Power BI/Snowflake untested']
    }

def main():
    g=read_csv(ROOT/'data/gold_generation.csv')
    c=read_csv(ROOT/'data/consumption.csv')
    m=calculate(g,c)
    assert m['generation_mwh'] == Decimal('66.000')
    assert m['consumption_mwh'] == Decimal('60.000')
    assert m['net_mwh'] == Decimal('6.000')
    assert m['row_count']==6
    out = {k:(str(v) if isinstance(v,Decimal) else v) for k,v in m.items()}
    (ROOT/'outputs').mkdir(exist_ok=True)
    (ROOT/'outputs'/'metrics_validation.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
if __name__ == '__main__':main()
