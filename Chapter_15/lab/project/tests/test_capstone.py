import csv, shutil, sys, tempfile, unittest
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'python'))
from capstone import ROOT, FIELDS, evaluate, release_gate, load_and_validate, write_outputs
BASE=ROOT/'data/energy_revisions.csv'

class CapstoneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.gold,cls.bad,cls.stats=evaluate(BASE)
    def test_delivery_count(self): self.assertEqual(self.stats['delivered'],12)
    def test_two_rejected(self): self.assertEqual(len(self.bad),2)
    def test_duplicate(self): self.assertEqual(self.stats['duplicate_deliveries'],1)
    def test_tombstone(self): self.assertEqual(self.stats['tombstoned_keys'],1)
    def test_six_visible(self): self.assertEqual(len(self.gold),6)
    def test_total(self): self.assertEqual(self.stats['total_mwh'],'66.000')
    def test_wind_revision(self): self.assertEqual(next(x for x in self.gold if x['technology']=='Wind')['energy_mwh'],'14.000')
    def test_no_test_metric(self): self.assertNotIn('TEST',[x['technology'] for x in self.gold])
    def test_unique_keys(self): self.assertEqual(len({(x['provider'],x['technology'],x['interval_utc']) for x in self.gold}),6)
    def test_nonnegative(self): self.assertTrue(all(Decimal(x['energy_mwh'])>=0 for x in self.gold))
    def test_utc(self): self.assertTrue(all(x['interval_utc'].endswith('Z') for x in self.gold))
    def test_hydrogen_not_invented(self): self.assertNotIn('Hydrogen',[x['technology'] for x in self.gold])
    def test_gating_pass(self): self.assertEqual(release_gate(self.gold,self.bad,self.stats)['status'],'ACCEPT')
    def test_tampered_gate(self):
        bad=dict(self.stats,total_mwh='67.000')
        self.assertEqual(release_gate(self.gold,self.bad,bad)['status'],'REJECT')
    def test_manifest_digest(self): self.assertEqual(len(self.stats['fixture_sha256']),64)
    def test_deterministic_replay(self): self.assertEqual(evaluate(BASE),evaluate(BASE))
    def test_contract_drift(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'wrong.csv'; p.write_text('WRONG,HEADER\na,b\n')
            with self.assertRaises(ValueError): load_and_validate(p)
    def test_negative_quarantine(self): self.assertTrue(any(x['event_id']=='f-012' for x in self.bad))
    def test_revision_zero_quarantine(self): self.assertTrue(any(x['event_id']=='f-011' for x in self.bad))
    def test_conflict_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'conflict.csv'; rows=list(csv.DictReader(BASE.open()))
            alt=next(x.copy() for x in rows if x['EVENT_ID']=='f-007');alt['EVENT_ID']='f-888';alt['ENERGY_MWH']='44.000'
            rows.append(alt)
            with p.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows)
            with self.assertRaises(ValueError): evaluate(p)
    def test_export(self):
        with tempfile.TemporaryDirectory() as td:
            out=write_outputs(BASE,Path(td)); self.assertEqual(out['release_gate']['status'],'ACCEPT')
            self.assertTrue((Path(td)/'gold_energy.csv').exists())

if __name__=='__main__': unittest.main(verbosity=2)
