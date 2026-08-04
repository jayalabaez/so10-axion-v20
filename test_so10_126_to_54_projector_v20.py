#!/usr/bin/env python3
"""Tests for explicit SO(10) 126→54 projector."""

from __future__ import annotations

import math
import unittest

import so10_126_to_54_projector_v20 as mod


class So10126To54Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()
        cls.proj = cls.report["projector"]

    def test_status_and_flags(self):
        self.assertEqual(
            self.report["status"],
            "126_TO_54_PROJECTOR_EXPANDED__LOCKING_CG_COMBINATORIAL",
        )
        self.assertEqual(self.report["n_failed"], 0)
        flags = self.report["flag"]
        self.assertTrue(flags["126_to_54_fully_expanded"])
        self.assertTrue(flags["combinatorial_cg_not_published_table"])
        self.assertFalse(flags["invented_unpublished_cg_values"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])

    def test_hodge_and_self_dual(self):
        self.assertLess(
            self.proj["hodge"]["star_squared_plus_identity_max_abs"], 1e-12
        )
        self.assertEqual(self.proj["self_dual"]["rank_plus_i"], 126)
        self.assertEqual(self.proj["self_dual"]["rank_minus_i"], 126)

    def test_c126_positive_finite(self):
        c = self.proj["C_126_to_54"]
        self.assertTrue(math.isfinite(c))
        self.assertGreater(c, 0.0)
        self.assertNotAlmostEqual(c, 1.0, places=3)  # no longer schematic 1

    def test_image_in_54(self):
        sample = self.proj["contraction"]["stats_126"]["sample_self_contraction"]
        self.assertLess(sample["trace_abs"], 1e-10)
        self.assertLess(sample["asymmetry_max_abs"], 1e-10)

    def test_locking_phase_pattern(self):
        lock = self.report["locking_reeval"]
        self.assertTrue(lock["all_phase_one_massive"])
        self.assertTrue(lock["all_phase_two_flat"])
        self.assertAlmostEqual(lock["C_126_to_54"], self.proj["C_126_to_54"])


if __name__ == "__main__":
    unittest.main()
