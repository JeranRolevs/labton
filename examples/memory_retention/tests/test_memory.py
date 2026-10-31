"""Deterministic contract, generator and calibration checks; no submitted code execution."""
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from memory_policy_contract import compile_policy,validate_update,FIFO_SOURCE,RESERVOIR_SOURCE
from memory_benchmark import scenario,rank_threshold,interval


class MemoryTests(unittest.TestCase):
    protocol={"steps":192,"warmup":48,"dimension":16}
    def test_reference_sources_match_the_declared_api(self):
        for source in (FIFO_SOURCE,RESERVOIR_SOURCE):
            self.assertIsNotNone(compile_policy(source))

    def test_imports_and_introspection_are_rejected(self):
        for source in ("import os\n"+FIFO_SOURCE,
                       "def select(bank, ages, new, t, capacity, aux):\n    return new.__class__"):
            with self.assertRaises(ValueError): compile_policy(source)

    def test_state_overflow_duplicates_and_nonfinite_values_are_rejected(self):
        for result in ({"keep":[0,1,2],"aux":[]},{"keep":[0,0],"aux":[]},
                       {"keep":[0],"aux":[float("nan")]},{"keep":[0],"aux":[0]*33}):
            with self.assertRaises(ValueError): validate_update(result,3,2)

    def test_fault_injection_changes_only_the_labelled_interval(self):
        clean=scenario(543,self.protocol,False)
        fault=scenario(543,self.protocol,True)
        self.assertTrue(np.array_equal(clean["x"][~fault["fault"]],fault["x"][~fault["fault"]]))
        self.assertTrue(np.all(np.flatnonzero(fault["fault"])>=self.protocol["warmup"]))
        self.assertFalse(np.any(fault["fault"]&fault["benign_recurrence"]))

    def test_generator_is_repeatable_and_seed_is_not_an_observation_field(self):
        a=scenario(14,self.protocol);b=scenario(14,self.protocol)
        self.assertTrue(np.array_equal(a["x"],b["x"]))
        self.assertNotIn("seed",a)
        self.assertEqual(a["x"].shape,(192,16))

    def test_finite_calibration_resolution_and_cp_endpoints(self):
        self.assertIsNone(rank_threshold(np.arange(24),.01)["value"])
        self.assertLessEqual(rank_threshold(np.arange(200),.1)["marginal_exchangeable_exceedance_bound"],.1)
        self.assertEqual(interval(0,12)[0],0)
        self.assertEqual(interval(12,12)[1],1)

    def test_seed_panels_cannot_overlap_calibration_scoring_or_confirmation(self):
        from memory_evaluator import validate_panels
        panels={"development":{"calibration":[1],"null":[2],"fault":[3]},
                "confirmation":{"calibration":[4],"null":[5],"fault":[6]}}
        protocol={"calibration_runs":1,"null_runs":1,"fault_runs":1}
        validate_panels(panels,protocol)
        panels["confirmation"]["fault"]=[1]
        with self.assertRaises(ValueError): validate_panels(panels,protocol)
