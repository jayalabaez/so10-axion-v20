#!/usr/bin/env python3
"""Tests for the archival 37 GHz software-ceiling campaign."""

from __future__ import annotations

import unittest

import nrao_37ghz_software_ceiling_v20 as ceiling


class SoftwareCeilingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = ceiling.run_campaign()

    def test_units_and_honesty(self):
        self.assertIn("GHz", self.report["units_lock"]["observing_band"])
        self.assertIn("kHz", self.report["units_lock"]["line_and_channel_resolution"])
        self.assertFalse(self.report["flag"]["real_37GHz_detection"])
        self.assertFalse(self.report["flag"]["new_experimental_exclusion"])
        self.assertTrue(self.report["flag"]["v20_still_open"])
        self.assertEqual(self.report["n_failed"], 0)

    def test_2mhz_not_suitable_and_does_not_exclude(self):
        row = next(r for r in self.report["simulation_campaign"] if "2MHz" in r["name"])
        self.assertEqual(row["resolution_vs_37kHz_halo"], "not_suitable")
        self.assertGreater(row["dilution_channel_over_line"], 50.0)
        self.assertFalse(row["excludes_v20_standard"])
        self.assertFalse(row["excludes_v20_maximal_cusp"])

    def test_published_ratios(self):
        lit = self.report["literature_J1745"]
        self.assertGreater(lit["ratio_standard_over_v20"], 100.0)
        self.assertGreater(lit["ratio_cusp_over_v20"], 1.0)
        self.assertTrue(lit["published_does_not_exclude_v20"])

    def test_hard_ceiling_flags(self):
        hc = self.report["hard_ceiling"]
        self.assertFalse(hc["can_download_MS_without_AAT_login"])
        self.assertFalse(hc["can_claim_new_experimental_exclusion"])
        self.assertFalse(hc["archived_Ka_2MHz_resolves_37kHz_halo_line"])


if __name__ == "__main__":
    unittest.main()
