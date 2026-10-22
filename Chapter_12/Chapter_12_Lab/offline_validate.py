"""Author-written CH12 correctness and example-statistics oracle, no Snowflake API."""
from __future__ import annotations
import csv, hashlib, json, statistics
from pathlib import Path
from datetime import datetime, timezone, timedelta
from decimal import Decimal
BASE=Path(__file__).resolve().parent
EXPECTED={'BIOENERGY':Decimal('8.000'),'HYDRO':Decimal('18.000'),
          'NUCLEAR':Decimal('16.000'),'OTHER':Decimal('4.000'),
          'SOLAR':Decimal('6.000'),'WIND':Decimal('14.000')}

def rows(filename: str):
    with (BASE/filename).open(newline='') as f:
        return list(csv.DictReader(f))

def validate_seed():
    seed=rows('energy_sample.csv')
    assert len(seed)==6
    seen={}
    for r in seed:
        d=datetime.fromisoformat(r['interval_utc'].replace('Z','+00:00'))
        assert d.tzinfo==timezone.utc
        tech=r['technology']; val=Decimal(r['energy_mwh'])
        assert tech not in seen and val>=0
        seen[tech]=val
    assert seen==EXPECTED
    assert sum(seen.values())==Decimal('66.000')
    return seed

def validate_expanded():
    dat=rows('energy_7day_fixture.csv')
    assert len(dat)==42
    keys=set(); days={}
    for r in dat:
        k=(r['interval_utc'],r['technology']); assert k not in keys
        keys.add(k); days.setdefault(r['interval_utc'],[]).append(r)
    assert len(days)==7
    expected_dates=[(datetime(2026,10,1,tzinfo=timezone.utc)+timedelta(days=i)).strftime('%Y-%m-%dT00:00:00Z') for i in range(7)]
    assert sorted(days)==expected_dates
    for d,group in days.items():
        assert {r['technology'] for r in group}==set(EXPECTED)
        assert sum(Decimal(r['energy_mwh']) for r in group)==Decimal('66.000')
    assert sum(Decimal(r['energy_mwh']) for r in dat)==Decimal('462.000')
    return dat

def by_date_expression(data, day):
    return {r['technology']: Decimal(r['energy_mwh']) for r in data if r['interval_utc'][:10]==day}

def by_range(data, day):
    start=day+'T00:00:00Z'
    end=(datetime.strptime(day,'%Y-%m-%d').date()+timedelta(days=1)).isoformat()+'T00:00:00Z'
    return {r['technology']: Decimal(r['energy_mwh']) for r in data if start<=r['interval_utc']<end}

def percentile(values, percentage):
    values=sorted(values); assert len(values)>0 and 0<=percentage<=100
    pos=(len(values)-1)*percentage/100; lo=int(pos); hi=min(lo+1,len(values)-1)
    return values[lo]+(values[hi]-values[lo])*(pos-lo)

def summarize_example_timings():
    raw=rows('benchmark_results.csv')
    by_group={}
    for r in raw:
        assert r['status']=='synthetic_illustration' and not r['query_id']
        assert r['warehouse_credits']==''
        by_group.setdefault((r['query_family'],r['variant']),[]).append(float(r['elapsed_seconds']))
    return {f'{a}:{b}':{'n':len(v),'median_s':round(statistics.median(v),3),
                        'p95_s':round(percentile(v,95),3)} for (a,b),v in sorted(by_group.items())}

def verify_manifest():
    manifest=json.loads((BASE/'dataset_sha256.json').read_text())
    for name,sha in manifest.items():
        assert hashlib.sha256((BASE/name).read_bytes()).hexdigest()==sha
    return True

if __name__=='__main__':
    validate_seed(); data=validate_expanded(); verify_manifest()
    for i in range(1,8):
        day=f'2026-10-{i:02d}'
        assert by_date_expression(data,day)==by_range(data,day)
    print('PASS: 6 single-day observations = 66.000 MWh')
    print('PASS: 42 seven-day observations = 462.000 MWh')
    print('PASS: both UTC-day methods agree on seven sample dates')
    print('PASS: checksum manifest verified')
    print('WARNING: all benchmark timings are synthetic illustrations, not Snowflake measurements')
    for key, result in summarize_example_timings().items():print(key, result)
