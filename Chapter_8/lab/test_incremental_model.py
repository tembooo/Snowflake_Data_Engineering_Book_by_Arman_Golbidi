from pathlib import Path
from decimal import Decimal
import unittest
from incremental_model import (load_fixture,accepted_unique,validate,latest_snapshot,apply_incrementally,visible,energy_total,simulate,Event)

FIXTURE=Path(__file__).resolve().parent/'energy_events.csv'

class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.rows=load_fixture(FIXTURE)
        self.accepted,self.bad=accepted_unique(self.rows)
    def test_counts(self): self.assertEqual((len(self.rows),len(self.accepted),len(self.bad)),(12,10,1))
    def test_duplicate_delivery_removed(self): self.assertEqual(sum(e.event_id=='A07' for e in self.accepted),1)
    def test_negative_value_quarantined(self): self.assertEqual([e.event_id for e in self.bad],['A11'])
    def test_latest_revision_selected(self):
        s=latest_snapshot(self.accepted)
        self.assertEqual(s[('fingrid','WIND','2026-10-21T10:00:00Z')].revision,2)
    def test_older_replay_no_regression(self):
        s=latest_snapshot(self.accepted)
        old=next(e for e in self.accepted if e.event_id=='A01')
        self.assertEqual(s,apply_incrementally(s,[old]))
    def test_delete_tombstone_blocks_resurrection(self):
        s=latest_snapshot(self.accepted)
        key=('fingrid','TEST','2026-10-21T10:00:00Z')
        self.assertEqual(s[key].operation,'DELETE')
        self.assertNotIn(key,visible(s))
        s2=apply_incrementally(s,[next(e for e in self.accepted if e.event_id=='A08')])
        self.assertEqual(s2,s)
    def test_energy_total(self): self.assertEqual(energy_total(latest_snapshot(self.accepted)),Decimal('66.000'))
    def test_incremental_and_full_match(self):
        s,*rest=simulate(self.rows)
        self.assertEqual(s,latest_snapshot(self.accepted))
    def test_failed_batch_retry(self):
        a,_,offset,failures,_=simulate(self.rows,fail_at_batch=1)
        b,*_=simulate(self.rows)
        self.assertEqual(a,b);self.assertEqual(offset,len(self.accepted));self.assertEqual(failures,1)
    def test_replay_is_idempotent(self):
        initial=latest_snapshot(self.accepted)
        self.assertEqual(apply_incrementally(initial,self.accepted),initial)
    def test_event_validation_contract(self):
        neg=Event('x','p','t','2026-10-21T00:00:00Z',1,Decimal('-2'),'UPSERT','2026-10-21T01:00:00Z')
        self.assertFalse(validate(neg))
        self.assertTrue(validate(next(e for e in self.rows if e.event_id=='A09')))

if __name__=='__main__': unittest.main()
