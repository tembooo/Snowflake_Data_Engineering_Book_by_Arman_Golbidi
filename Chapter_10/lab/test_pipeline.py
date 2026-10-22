"""Offline tests: do not import dbt or connect to Snowflake."""
from __future__ import annotations
import copy
import unittest
from decimal import Decimal
from offline_oracle import parse_event, build_state,release_gate,read_fixture

class Chapter10Contracts(unittest.TestCase):
    def setUp(self):
        self.raw = read_fixture()
        self.state,self.rejected,self.gold,self.report=build_state(self.raw)
    def test_delivery_count(self): self.assertEqual(self.report['delivered'],12)
    def test_duplicate_replays(self): self.assertEqual(self.report['duplicate_deliveries'],1)
    def test_rejected_invalid(self): self.assertEqual(self.report['rejected'],2)
    def test_visible_current_state(self): self.assertEqual(len(self.state),6)
    def test_grand_total(self): self.assertEqual(self.report['total_mwh'],'66.000')
    def test_revision_correction(self): self.assertEqual(next(e['ENERGY_MWH'] for e in self.state if e['TECHNOLOGY']=='Wind'),Decimal('14.000'))
    def test_tombstone(self): self.assertFalse(any(e['TECHNOLOGY']=='TEST' for e in self.state))
    def test_broken_measure_quarantined(self): self.assertTrue(any(x['event_id']=='f-012' for x in self.rejected))
    def test_invalid_revision_quarantined(self): self.assertTrue(any(x['event_id']=='f-011' for x in self.rejected))
    def test_release_gate_accepts(self): self.assertEqual(release_gate(self.state,self.rejected,self.gold,self.report)['status'],'ACCEPT')
    def test_release_gate_rejects_unit_change(self):
        bad=dict(self.report,unit='kWh');self.assertIn('unit_drift',release_gate(self.state,self.rejected,self.gold,bad)['violations'])
    def test_conflicting_equal_revision_blocks(self):
        extra=dict(self.raw[6],EVENT_ID='conflict',ENERGY_MWH='999.000')
        s,q,g,m=build_state([*self.raw,extra]);self.assertEqual(release_gate(s,q,g,m)['status'],'BLOCK')
    def test_idempotent_replay(self):
        state,_,_,metrics=build_state([*self.raw,*self.raw]);self.assertEqual(len(state),len(self.state));self.assertEqual(metrics['total_mwh'],'66.000')
    def test_missing_business_key_quarantined(self):
        invalid=dict(self.raw[0],PROVIDER='')
        s,q,g,m=build_state([*self.raw,invalid]);self.assertEqual(m['visible_rows'],6);self.assertGreater(m['rejected'],2)
    def test_timestamp_not_local(self):
        bad=dict(self.raw[0],INTERVAL_UTC='2026-03-01T12:00:00+02:00')
        with self.assertRaisesRegex(ValueError,'timestamp_not_utc_z'):parse_event(bad)
    def test_gold_reconciles_with_state(self):
        self.assertEqual(sum(Decimal(g['energy_mwh']) for g in self.gold),sum(e['ENERGY_MWH'] for e in self.state))

if __name__=='__main__':unittest.main()
