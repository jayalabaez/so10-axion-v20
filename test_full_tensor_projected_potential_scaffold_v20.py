#!/usr/bin/env python3
"""Tests for FULL_TENSOR_PROJECTED_POTENTIAL scaffold."""

from __future__ import annotations

import unittest

import full_tensor_projected_potential_scaffold_v20 as mod


class FullTensorProjectedPotentialScaffoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_fail_closed_scaffold(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertTrue(self.report["flags"]["full_tensor_scaffold_ready"])
        self.assertFalse(self.report["flags"]["full_g2_projection_closed"])
        self.assertTrue(self.report["flags"]["ready_subspace_bfb_only"])
        self.assertFalse(self.report["flags"]["cg_120_320_1050_4125_invented"])
        self.assertFalse(self.report["flags"]["whole_model_validated"])

    def test_ready_bfb_and_open_slots(self):
        self.assertTrue(self.report["ready_subspace_bfb"]["ready_subspace_bfb_green"])
        self.assertEqual(
            set(self.report["open_awaiting_cg"]),
            {
                "MISSING_CG_120",
                "MISSING_CG_320",
                "MISSING_CG_1050",
                "MISSING_CG_4125",
            },
        )
        self.assertIn(
            "PROMOTED_S_PHI17_ISOTROPIC_RESIDUAL",
            self.report["isotropic_residuals"],
        )
        self.assertEqual(
            self.report["off_singlet_censuses"]["210"]["n_nonzero"], 207
        )
        self.assertTrue(
            self.report["checks"]["open_126_54_locking_hermitian_census_ready"]
        )
        self.assertEqual(
            self.report["off_singlet_censuses"]["126_54_locking"][
                "positive_schur_seed"
            ],
            False,
        )


if __name__ == "__main__":
    unittest.main()
