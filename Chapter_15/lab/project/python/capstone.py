"""Deterministic offline acceptance oracle for the synthetic Chapter 15 capstone.

This module does not connect to Snowflake or Fingrid.
"""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ['EVENT_ID','PROVIDER','TECHNOLOGY','INTERVAL_UTC','REVISION','ENERGY_MWH','OPERATION']
ALLOWED_OPERATIONS = {'UPSERT','DELETE'}

def load_and_validate(path: Path):
    path = Path(path)
    with path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError(f'Contract mismatch: columns {reader.fieldnames!r}')
        events, rejected = [], []
        for index, r in enumerate(reader, start=2):
            try:
                if not r['EVENT_ID'] or not r['PROVIDER'] or not r['TECHNOLOGY']:
                    raise ValueError('missing business identifier')
                if r['OPERATION'] not in ALLOWED_OPERATIONS:
                    raise ValueError('unknown operation')
                timestamp = r['INTERVAL_UTC']
                parsed = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                if parsed.strftime('%Y-%m-%dT%H:%M:%SZ') != timestamp:
                    raise ValueError('noncanonical UTC timestamp')
                revision = int(r['REVISION'])
                if revision < 1:
                    raise ValueError('revision must be positive')
                value = Decimal(r['ENERGY_MWH'])
                if not value.is_finite() or value < 0:
                    raise ValueError('non-finite or negative energy')
                if r['OPERATION'] == 'DELETE' and value != 0:
                    raise ValueError('tombstone must carry zero energy')
                events.append((r, revision, value))
            except (ValueError, InvalidOperation, TypeError, OverflowError) as exc:
                rejected.append({'file_row': index, 'event_id': r.get('EVENT_ID'), 'reason': str(exc)})
    return events, rejected

def evaluate(path: Path):
    path = Path(path)
    events, rejected = load_and_validate(path)
    seen, deduped = set(), []
    for record, rev, val in events:
        fingerprint = tuple(record[k] for k in FIELDS)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduped.append((record, rev, val))
    # Conflict at equal business key/revision is a release blocker, not a last-writer choice.
    versions = {}
    for r, rev, val in deduped:
        key = (r['PROVIDER'],r['TECHNOLOGY'],r['INTERVAL_UTC'],rev)
        existing = versions.get(key)
        if existing is not None and existing != (r['OPERATION'],val):
            raise ValueError(f'conflicting same-revision payload for {key}')
        versions[key] = (r['OPERATION'],val)
    by_key = {}
    for r, rev, val in deduped:
        key = (r['PROVIDER'],r['TECHNOLOGY'],r['INTERVAL_UTC'])
        prior = by_key.get(key)
        if prior is None or rev > prior[1]:
            by_key[key] = (r, rev, val)
    gold = []
    tombstone_count = 0
    for (provider,technology,timestamp),(r,rev,val) in sorted(by_key.items()):
        if r['OPERATION'] == 'DELETE':
            tombstone_count += 1
            continue
        gold.append({'provider':provider,'technology':technology,'interval_utc':timestamp,
                     'revision':rev,'energy_mwh':f'{val:.3f}'})
    total=sum((Decimal(r['energy_mwh']) for r in gold),Decimal(0))
    summary={'delivered':len(events)+len(rejected), 'duplicate_deliveries':len(events)-len(deduped),
        'rejected':len(rejected), 'tombstoned_keys':tombstone_count,
        'visible_rows':len(gold),'total_mwh':f'{total:.3f}','unit':'MWh',
        'fixture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'data_classification':'SYNTHETIC', 'live_snowflake_executed':False}
    return gold,rejected,summary

def release_gate(gold,rejected,summary):
    errors=[]
    keys=[(r['provider'],r['technology'],r['interval_utc']) for r in gold]
    if len(keys)!=len(set(keys)): errors.append('duplicate gold keys')
    if any(Decimal(r['energy_mwh'])<0 for r in gold): errors.append('negative energy')
    if summary['visible_rows']!=6 or summary['total_mwh']!='66.000': errors.append('fixture invariant changed')
    if summary['rejected']!=2 or summary['duplicate_deliveries']!=1: errors.append('fixture audit changed')
    return {'status':'ACCEPT' if not errors else 'REJECT', 'violations':errors}

def write_outputs(input_path=ROOT/'data/energy_revisions.csv', out_dir=ROOT/'output'):
    gold,rejected,summary=evaluate(Path(input_path))
    summary['release_gate']=release_gate(gold,rejected,summary)
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    with (out_dir/'gold_energy.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['provider','technology','interval_utc','revision','energy_mwh'])
        writer.writeheader();writer.writerows(gold)
    for name,data in [('quarantine.json',rejected),('acceptance.json',summary)]:
        (out_dir/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return summary

if __name__=='__main__':
    print(json.dumps(write_outputs(),indent=2))
