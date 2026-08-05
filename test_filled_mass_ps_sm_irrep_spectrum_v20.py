#!/usr/bin/env python3
"""Tests for filled mass PS/SM irrep spectrum."""

from __future__ import annotations

import unittest

import filled_mass_ps_sm_irrep_spectrum_v20 as mod


class FilledMassPsSmIrrepSpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(self.report["H10"]["dim_sum"], 10)
        self.assertEqual(self.report["Sigmabar126"]["dim_sum"], 126)
        self.assertEqual(
            self.report["inventory"]["open_mixed_10_status"],
            "ABSORBED_INTO_PORTAL_B",
        )
        self.assertFalse(self.report["flags"]["mode_by_mode_cg_splitting"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
