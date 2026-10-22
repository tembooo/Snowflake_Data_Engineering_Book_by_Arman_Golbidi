"""Chapter 7: deterministic, offline ingestion / replay / freshness simulator.
No Snowflake credentials, network access, dependencies, or billable resources.
Events, receipt and commit times are synthetic, not measured Snowflake latencies.
"""
from __future__ import annotations
import argparse
import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from statistics import median

BASE = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
def iso(seconds: int) -> str:
    return (BASE + timedelta(seconds=seconds)).isoformat().replace('+00:00', 'Z')

# source_offset identifies an immutable Kafka-like source-log position.
# event_id alone is deliberately NOT the silver-layer business key.
EVENTS = [
    dict(offset=0, id='e101', metric='wind', minute=0, value=12.5, rev=1, recv=2, committed=5),
    dict(offset=1, id='e102', metric='solar', minute=0, value=8.0, rev=1, recv=10, committed=14),
    dict(offset=2, id='e103', metric='hydro', minute=0, value=20.0, rev=1, recv=35, committed=40),
    dict(offset=3, id='e102', metric='solar', minute=0, value=8.0, rev=1, recv=41, committed=45), # duplicate
    dict(offset=4, id='e104', metric='wind', minute=0, value=13.0, rev=2, recv=140, committed=145), # correction
    dict(offset=5, id='e105', metric='solar', minute=-5, value=6.0, rev=1, recv=180, committed=185), # late
    dict(offset=6, id='e106', metric='hydro', minute=5, value=-4.0, rev=1, recv=190, committed=194), # invalid
    dict(offset=7, id='e107', metric='wind', minute=5, value=15.0, rev=1, recv=195, committed=199),
    dict(offset=8, id='e108', metric='hydro', minute=5, value=4.0, rev=1, recv=201, committed=211), # replay after failure
]

def process(events=EVENTS, failure_offset=8):
    """Simulate at-least-once delivery with explicit offset and silver deduplication."""
    if failure_offset is not None and not any(e['offset'] == failure_offset for e in events):
        raise ValueError('specified failure offset not in source')
    # Duplicate the failure offset once to simulate retry; commit source offset only on success.
    queue=[]
    for e in events:
        if e['offset'] == failure_offset:
            queue.append((e, True))
        queue.append((e, False))
    bronze=[]; quarantine=[]; attempts=[]; silver={}
    last_offset=-1
    for event, simulated_failure in queue:
        if simulated_failure:
            attempts.append({'offset':event['offset'],'result':'transient_failure','committed':False})
            continue
        if event['offset'] <= last_offset:
            # This simulator uses a single strictly ordered source partition.
            raise AssertionError('out-of-order source offset in simulated log')
        if event['value'] < 0:
            quarantine.append({'source_offset':event['offset'],'event_id':event['id'],'reason':'negative_energy'})
            attempts.append({'offset':event['offset'],'result':'quarantined','committed':True})
            last_offset=event['offset']
            continue
        row={'source_offset':event['offset'],'event_id':event['id'],'provider':'synthetic-fi',
             'technology':event['metric'],'event_utc':iso(60*event['minute']),
             'received_utc':iso(event['recv']),'visible_utc':iso(event['committed']),
             'energy_mwh':event['value'],'revision':event['rev'],
             'freshness_seconds':event['committed']-60*event['minute']}
        bronze.append(row)
        key=(row['provider'],row['technology'],row['event_utc'])
        previous=silver.get(key)
        # Larger revision wins; for equal revision a later source offset is not an update.
        if previous is None or row['revision']>previous['revision']:
            silver[key]=row
        attempts.append({'offset':event['offset'],'result':'accepted','committed':True})
        last_offset=event['offset']
    assert last_offset == events[-1]['offset']
    metrics={'source_events':len(events),'attempts':len(attempts),'bronze_rows':len(bronze),
             'quarantined_rows':len(quarantine),'silver_rows':len(silver),
             'silver_total_mwh':round(sum(r['energy_mwh'] for r in silver.values()),3),
             'median_bronze_freshness_seconds':median(r['freshness_seconds'] for r in bronze),
             'max_bronze_freshness_seconds':max(r['freshness_seconds'] for r in bronze),
             'last_committed_offset':last_offset}
    return bronze,list(sorted(silver.values(),key=lambda r:(r['event_utc'],r['technology']))),quarantine,attempts,metrics

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='output',help='folder for CSV/JSON outputs')
    args=parser.parse_args(); out=Path(args.out);out.mkdir(exist_ok=True,parents=True)
    bronze,silver,quarantine,attempts,metrics=process()
    for filename, rows in [('bronze.csv',bronze),('silver.csv',silver)]:
        with (out/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    for filename,data in [('quarantine.json',quarantine),('attempts.json',attempts),('metrics.json',metrics)]:
        (out/filename).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(metrics,indent=2))
if __name__ == '__main__': main()
