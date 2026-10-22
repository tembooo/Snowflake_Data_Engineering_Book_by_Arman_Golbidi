"""Chapter 10 independent, zero-cloud contract oracle for synthetic energy events.
Only Python standard-library dependencies. Produces evidence, not a Snowflake test.
"""
from __future__ import annotations
import csv
import json
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KEY = ('PROVIDER','TECHNOLOGY','INTERVAL_UTC')
REQUIRED = ('EVENT_ID','PROVIDER','TECHNOLOGY','INTERVAL_UTC','REVISION','ENERGY_MWH','OPERATION')
UTC = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')


def parse_event(raw):
    if any(not str(raw.get(k, '')).strip() for k in REQUIRED):
        raise ValueError('required_field_missing')
    if not UTC.fullmatch(str(raw['INTERVAL_UTC'])):
        raise ValueError('timestamp_not_utc_z')
    operation = str(raw['OPERATION']).upper()
    if operation not in {'UPSERT', 'DELETE'}:
        raise ValueError('invalid_operation')
    try:
        revision = int(raw['REVISION'])
        value = Decimal(str(raw['ENERGY_MWH']))
    except (ValueError, InvalidOperation):
        raise ValueError('invalid_number') from None
    if revision <= 0 or not value.is_finite() or value < 0:
        raise ValueError('invalid_measure_or_revision')
    return dict(raw, REVISION=revision, ENERGY_MWH=value, OPERATION=operation)


def build_state(rows):
    seen_event_ids = {}
    accepted = []
    quarantine = []
    metrics = Counter()
    for raw in rows:
        metrics['delivered'] += 1
        try:
            event = parse_event(raw)
        except ValueError as exc:
            quarantine.append({'event_id':raw.get('EVENT_ID',''), 'reason':str(exc)})
            metrics['rejected'] += 1
            continue
        event_id = event['EVENT_ID']
        if event_id in seen_event_ids:
            if event != seen_event_ids[event_id]:
                quarantine.append({'event_id':event_id,'reason':'event_id_conflict'})
                metrics['conflicts'] += 1
            else:
                metrics['duplicate_deliveries'] += 1
            continue
        seen_event_ids[event_id] = event
        accepted.append(event)
    grouped = {}
    for event in accepted:
        key = tuple(event[k] for k in KEY)
        grouped.setdefault(key, []).append(event)
    state = []
    for key, revisions in grouped.items():
        highest = max(e['REVISION'] for e in revisions)
        candidates = [e for e in revisions if e['REVISION'] == highest]
        distinct = {(e['OPERATION'],e['ENERGY_MWH']) for e in candidates}
        if len(distinct) > 1:
            quarantine.extend({'event_id':e['EVENT_ID'],'reason':'revision_conflict'} for e in candidates)
            metrics['conflicts'] += 1
            continue
        winner = sorted(candidates, key=lambda e:e['EVENT_ID'])[-1]
        if winner['OPERATION'] == 'DELETE':
            metrics['tombstoned_keys'] += 1
        else:
            state.append(winner)
    state.sort(key=lambda e:tuple(e[k] for k in KEY))
    metrics['accepted_unique_events'] = len(accepted)
    metrics['visible_rows'] = len(state)
    totals = {}
    for e in state:
        gold_key = (e['INTERVAL_UTC'],e['TECHNOLOGY'])
        totals[gold_key] = totals.get(gold_key,Decimal('0')) + e['ENERGY_MWH']
    gold = [dict(interval_utc=k[0], technology=k[1],energy_mwh=f'{v:.3f}')
            for k,v in sorted(totals.items())]
    mwh = sum((e['ENERGY_MWH'] for e in state),Decimal('0'))
    manifest = dict(metrics, total_mwh=f'{mwh:.3f}',unit='MWh',source='SYNTHETIC',
                    snowflake_executed=False, dbt_executed=False, cloud_approved=False)
    return state, quarantine, gold, manifest


def release_gate(state, quarantine, gold, manifest, expected='66.000'):
    keys = [tuple(e[k] for k in KEY) for e in state]
    violations = []
    if len(keys) != len(set(keys)):
        violations.append('duplicate_current_key')
    if any(e['OPERATION'] == 'DELETE' or e['ENERGY_MWH'] < 0 for e in state):
        violations.append('invalid_visible_state')
    if sum((Decimal(x['energy_mwh']) for x in gold),Decimal(0)) != Decimal(manifest['total_mwh']):
        violations.append('gold_silver_mismatch')
    if str(manifest['total_mwh']) != expected:
        violations.append('fixture_oracle_mismatch')
    if manifest['unit'] != 'MWh':
        violations.append('unit_drift')
    if manifest.get('conflicts',0):
        violations.append('conflict_requires_review')
    return dict(status='BLOCK' if violations else 'ACCEPT',violations=violations)


def read_fixture(path=ROOT/'data'/'energy_revisions.csv'):
    with Path(path).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def main():
    state, rejected, gold, manifest = build_state(read_fixture())
    gate=release_gate(state,rejected,gold,manifest)
    out=ROOT/'output';out.mkdir(exist_ok=True)
    (out/'offline_summary.json').write_text(json.dumps({**manifest,'release_gate':gate},indent=2),encoding='utf-8')
    (out/'quarantine.json').write_text(json.dumps(rejected,indent=2),encoding='utf-8')
    with (out/'gold_energy.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['interval_utc','technology','energy_mwh']);w.writeheader();w.writerows(gold)
    print(json.dumps({**manifest,'release_gate':gate},indent=2))
    if gate['status'] != 'ACCEPT':
        raise SystemExit('Release gate blocked the fixture')

if __name__=='__main__':
    main()
