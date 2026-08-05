#!/usr/bin/env python3
"""Tests for SO(10) gauge orbit with physical hEW."""

from __future__ import annotations

import unittest

import so10_gauge_orbit_with_hew_v20 as mod


class GaugeOrbitWithHewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "SO10_GAUGE_ORBIT_WITH_HEW_36_GOLDSTONES__FULL_HESSIAN_OPEN",
        )
        flags = self.report["flags"]
        self.assertTrue(flags["hew_extended_orbit_36_goldstones"])
        self.assertTrue(flags["sm_orbit_33_retained"])
        self.assertTrue(flags["em_stabilizer_9"])
        self.assertFalse(flags["full_component_hessian_complete"])
        self.assertFalse(flags["S_and_Phi17_dynamical_in_orbit"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertFalse(flags["whole_model_excluded"])

    def test_breaking_chain(self):
        chain = self.report["breaking_chain"]
        self.assertEqual(chain["SO10_to_SM"]["goldstones"], 33)
        self.assertEqual(chain["SM_to_UEM"]["added_goldstones"], 3)
        self.assertEqual(chain["SO10_to_UEM"]["goldstones"], 36)
        self.assertEqual(chain["SO10_to_UEM"]["stabilizer_dim"], 9)
        self.assertEqual(self.report["embedding"]["total"], 724)
        self.assertAlmostEqual(self.report["projectors"]["trace_P_G"], 36.0, places=6)
        synth = self.report["synthetic_validation"]
        self.assertEqual(synth["n_zero"], 36)
        self.assertEqual(synth["n_positive"], 688)
        self.assertEqual(synth["n_negative"], 0)


if __name__ == "__main__":
    unittest.main()
