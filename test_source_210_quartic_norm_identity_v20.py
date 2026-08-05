#!/usr/bin/env python3
"""Tests for selected-vacuum source quartic densities."""

from __future__ import annotations

import unittest

import source_210_quartic_norm_identity_v20 as mod


class SelectedVacuumSourceQuarticDensityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertFalse(self.report["flags"]["whole_model_validated"])
        self.assertFalse(self.report["flags"]["g1_closed"])
        self.assertTrue(self.report["flags"]["pure_210_identity_owned_upstream"])

    def test_selected_vacuum_activates_45_with_nonnegative_1050(self):
        self.assertTrue(self.report["flags"]["selected_vacuum_symmetric_45_active"])
        dens = self.report["selected_vacuum"]["effective_quartic_densities"]
        self.assertGreater(dens["||(ΦΦ)_45||^2 / ||Φ||^4"], 0.0)
        self.assertGreaterEqual(dens["||(ΦΦ)_1050||^2 / ||Φ||^4"], -1e-12)
        self.assertGreaterEqual(self.report["ps_span_probe"]["rhs_1050_min"], -1e-9)
        self.assertTrue(self.report["flags"]["reduced_potential_insertion_pending"])


if __name__ == "__main__":
    unittest.main()
