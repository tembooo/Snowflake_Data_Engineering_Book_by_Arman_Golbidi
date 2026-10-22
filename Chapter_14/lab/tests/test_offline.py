import sys,unittest,tempfile,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ml_baseline import make_fixture,write_fixture,load_fixture,predict,mae,evaluate
class Chapter14BaselineTests(unittest.TestCase):
    def setUp(self): self.rows=make_fixture();self.values=[r['generation_mwh'] for r in self.rows]
    def test_35_rows(self):self.assertEqual(len(self.rows),35)
    def test_utc_dates(self):self.assertEqual((self.rows[0]['date_utc'],self.rows[-1]['date_utc']),('2026-01-01','2026-02-04'))
    def test_provenance(self):self.assertEqual({r['source'] for r in self.rows},{'synthetic'})
    def test_positive(self):self.assertTrue(all(v>=0 for v in self.values))
    def test_fixed_split(self):self.assertEqual((evaluate(self.values)['training_days'],evaluate(self.values)['validation_days'],evaluate(self.values)['test_days']),(21,7,7))
    def test_seasonal_lag(self):self.assertEqual(predict(self.values,28),self.values[21])
    def test_last_value_lag(self):self.assertEqual(predict(self.values,28,'last'),self.values[27])
    def test_no_future_leakage(self):
        changed=self.values.copy();changed[34]+=1000
        self.assertEqual(predict(self.values,34),predict(changed,34))
    def test_injected_anomaly_flag(self):self.assertIn(34,evaluate(self.values)['flagged_test_indices'])
    def test_uncontaminated_no_anomaly(self):
        vals=[x['generation_mwh'] for x in make_fixture(inject_anomaly=False)]
        self.assertNotIn(34,evaluate(vals)['flagged_test_indices'])
    def test_nonzero_mae(self):self.assertGreater(evaluate(self.values)['test_mae_seasonal_mwh'],0)
    def test_mae_rejects_bad_length(self):
        with self.assertRaises(ValueError):mae([1,2],[1])
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.csv';write_fixture(self.rows,p)
            self.assertEqual(load_fixture(p),self.values)
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'duplicate.csv';rows=self.rows.copy();rows[1]=dict(rows[0]);write_fixture(rows,p)
            with self.assertRaises(ValueError):load_fixture(p)
    def test_negative_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'invalid.csv';rows=[dict(r) for r in self.rows];rows[0]['generation_mwh']='-4';write_fixture(rows,p)
            with self.assertRaises(ValueError):load_fixture(p)
    def test_wrong_provenance_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'wrong.csv';rows=[dict(r) for r in self.rows];rows[0]['source']='customer';write_fixture(rows,p)
            with self.assertRaises(ValueError):load_fixture(p)
if __name__=='__main__':unittest.main()
