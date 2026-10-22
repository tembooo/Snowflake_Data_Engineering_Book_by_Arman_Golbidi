"""Chapter 8 offline reference: two independently implemented paths to latest-revision energy state.
No Snowflake calls; this is a correctness model, not a benchmark of vendor features.
"""
from __future__ import annotations
import csv
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

@dataclass(frozen=True)
class Event:
    event_id: str
    provider: str
    technology: str
    interval_utc: str
    revision: int
    energy_mwh: Decimal | None
    operation: str
    ingested_at_utc: str
    @property
    def key(self): return (self.provider, self.technology, self.interval_utc)
    @property
    def precedence(self): return (self.revision, self.ingested_at_utc, self.event_id)


def load_fixture(path: Path):
    events=[]
    with path.open(newline='', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            events.append(Event(row['event_id'],row['provider'],row['technology'],
                row['interval_utc'],int(row['revision']),
                Decimal(row['energy_mwh']) if row['energy_mwh'] else None,
                row['operation'],row['ingested_at_utc']))
    return events


def validate(event: Event):
    if not event.provider or not event.technology or not event.interval_utc or event.revision < 0:
        return False
    if event.operation == 'DELETE':
        return event.energy_mwh is None
    return event.operation == 'UPSERT' and event.energy_mwh is not None and event.energy_mwh >= 0


def accepted_unique(events):
    """The upstream normalization gate: invalid rows quarantined; identical event IDs deduplicated."""
    accepted,quarantined,seen=[],[],set()
    for event in events:
        if not validate(event):
            quarantined.append(event)
        elif event.event_id not in seen:
            accepted.append(event)
            seen.add(event.event_id)
    return accepted,quarantined


def latest_snapshot(events):
    """Recompute every business key from accepted history (declarative-query analogy)."""
    state={}
    for event in events:
        old=state.get(event.key)
        if old is None or event.precedence > old.precedence:
            state[event.key]=event
    return state


def apply_incrementally(state, events):
    """Only apply a simulated committed micro-batch (MERGE/stream-task analogy)."""
    new=dict(state)
    batch=latest_snapshot(events)
    for key,event in batch.items():
        old=new.get(key)
        if old is None or event.precedence > old.precedence:
            new[key]=event  # Retain delete tombstones to block older replay.
    return new


def visible(state):
    return {key:e for key,e in state.items() if e.operation == 'UPSERT'}


def energy_total(state):
    return sum((e.energy_mwh for e in visible(state).values()),Decimal('0.000'))


def simulate(events, fail_at_batch=None):
    """An unsuccessful commit neither publishes a state nor advances the logical offset."""
    accepted,quarantine=accepted_unique(events)
    sizes=(3,3,4,2)
    chunks=[]; i=0
    for size in sizes:
        chunks.append(accepted[i:i+size]); i+=size
    if i<len(accepted): chunks.append(accepted[i:])
    state={}; offset=0; failures=0
    for idx,chunk in enumerate(chunks):
        if not chunk: continue
        tentative=apply_incrementally(state,chunk)
        if idx == fail_at_batch:
            failures+=1  # aborted transaction; replay same batch
        state=tentative
        offset+=len(chunk)
    return state,quarantine,offset,failures,accepted


def main():
    root=Path(__file__).resolve().parent
    events=load_fixture(root/'energy_events.csv')
    state,quarantine,offset,failures,accepted=simulate(events,fail_at_batch=1)
    oracle=latest_snapshot(accepted)
    assert state == oracle
    out=root/'output';out.mkdir(exist_ok=True)
    summary={'input_rows':len(events),'accepted_unique_events':len(accepted),
             'duplicate_deliveries':len(events)-len(accepted)-len(quarantine),
             'quarantined_rows':len(quarantine),'committed_source_offset':offset,
             'simulated_failures_retried':failures,'latest_keys_including_tombstone':len(state),
             'visible_keys':len(visible(state)),'total_mwh':str(energy_total(state)),
             'procedural_equals_snapshot':state==oracle,'cloud_execution':'NOT TESTED'}
    (out/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    for filename, items in [('current_rows.csv',visible(state).values()),('quarantined_rows.csv',quarantine)]:
        with (out/filename).open('w',newline='',encoding='utf-8') as fh:
            writer=csv.writer(fh); writer.writerow(['event_id','provider','technology','interval_utc','revision','energy_mwh','operation'])
            for e in sorted(items,key=lambda x:(x.technology,x.revision)):
                writer.writerow([e.event_id,e.provider,e.technology,e.interval_utc,e.revision,str(e.energy_mwh) if e.energy_mwh is not None else '',e.operation])
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
