import unittest
from streaming_simulator import process, EVENTS

class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.bronze,self.silver,self.quarantine,self.attempts,self.metrics=process()
    def test_counts(self):
        self.assertEqual((self.metrics['source_events'],self.metrics['bronze_rows'],self.metrics['quarantined_rows'],self.metrics['silver_rows']), (9,8,1,6))
    def test_corrected_wind(self):
        rows=[r for r in self.silver if r['technology']=='wind' and r['event_utc'].endswith('10:00:00Z')]
        self.assertEqual(len(rows),1);self.assertEqual((rows[0]['energy_mwh'],rows[0]['revision']),(13.0,2))
    def test_total_not_double_counted(self): self.assertEqual(self.metrics['silver_total_mwh'],66.0)
    def test_negative_quarantine(self): self.assertEqual(self.quarantine[0]['reason'],'negative_energy')
    def test_retry_then_commit(self):
        self.assertEqual([a['result'] for a in self.attempts if a['offset']==8],['transient_failure','accepted'])
        self.assertEqual(self.metrics['last_committed_offset'],8)
    def test_late_event(self):
        e=next(r for r in self.silver if r['event_utc'].endswith('09:55:00Z'))
        self.assertGreater(e['freshness_seconds'],300)
    def test_deterministic_replay(self):
        _,silver2,_,attempts2,m2=process()
        self.assertEqual(silver2,self.silver);self.assertEqual(m2,self.metrics)
    def test_no_failure_mode(self):
        b,s,q,a,m=process(failure_offset=None)
        self.assertEqual((len(b),len(s),len(q)),(8,6,1));self.assertEqual(len(a),9)

if __name__=='__main__':unittest.main()
