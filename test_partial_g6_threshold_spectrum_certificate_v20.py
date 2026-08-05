#!/usr/bin/env python3
"""Tests for partial G6 threshold spectrum certificate."""

from __future__ import annotations

import unittest

import partial_g6_threshold_spectrum_certificate_v20 as mod


class PartialG6ThresholdSpectrumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_executes_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["partial_g6_threshold_spectrum_bundled"])
        self.assertFalse(self.report["flags"]["mode_by_mode_cg_splitting"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_sections_present(self):
        secs = self.report["sections"]
        self.assertIn("isotropic_ps_multiplicities", secs)
        self.assertIn("aulakh_off_singlet_210", secs)
        self.assertIn("susyno_gauge_uv", secs)
        self.assertTrue(
            secs["susyno_gauge_uv"]["literature_check_126_only"]["V_massless"]
        )


if __name__ == "__main__":
    unittest.main()
