"""Standard-library tests for Phase 5B scheduling and output contracts."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from run_decomposition import (
    ROOT, assert_feasible, as_dat, greedy_initial, parse_instance,
    parse_local_output, score, write_log,
)

DATA = ROOT.parent / "01_monolithic" / "benchmark_30.dat"


class TestScheduling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ins = parse_instance(DATA)
        cls.seed = greedy_initial(cls.ins)

    def test_fixture(self):
        self.assertEqual(self.ins["nLots"],30)
        self.assertEqual(self.ins["nOps"],3)
        self.assertEqual(self.ins["nTools"],5)
        self.assertEqual(len(self.ins["maintenance"]),2)

    def test_seed_feasible(self):
        assert_feasible(self.ins,self.seed)
        self.assertEqual(len(self.seed),90)
        self.assertEqual(score(self.ins,self.seed),(789598,2249,199))

    def test_overlapping_machine_rejected(self):
        bad = dict(self.seed)
        # Force one operation to overlap itself with a second operation on same machine.
        (j,o), (m,s,e) = next(iter(bad.items()))
        other = next(key for key, val in bad.items() if key != (j,o) and val[0] == m)
        om,os,oe = bad[other]
        bad[other] = (om,s,s+(oe-os))
        with self.assertRaises(ValueError):
            assert_feasible(self.ins,bad)

    def test_subproblem_data_and_records(self):
        subset = {1,2,3,4,5,6,7,8,9,10}
        dat, idx = as_dat(self.ins,subset,self.seed,5,4)
        self.assertIn("nLots = 10;",dat)
        self.assertIn("blocked = {",dat)
        self.assertIn("timeLimit = 5;",dat)
        original = {v:k for k,v in idx.items()}
        records = ["LOCAL_SUMMARY,0,200"]
        for global_lot in subset:
            for o in (1,2,3):
                m,s,e = self.seed[global_lot,o]
                records.append(f"LOCAL_ASSIGN,{original[global_lot]},{o},{m},{s},{e}")
        parsed = parse_local_output("\n".join(records),idx,3)
        self.assertEqual(parsed,{k:v for k,v in self.seed.items() if k[0] in subset})

    def test_output_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"solution.log"
            write_log(path,self.ins,self.seed,[])
            text=path.read_text(encoding="utf-8")
            self.assertEqual(sum(x.startswith("ASSIGN,") for x in text.splitlines()),90)
            self.assertIn("SUMMARY,2249,199",text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
