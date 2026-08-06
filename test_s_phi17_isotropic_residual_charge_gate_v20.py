#!/usr/bin/env python3
"""Tests for S/Φ17 isotropic residual charge gate."""

from __future__ import annotations

import unittest

import s_phi17_isotropic_residual_charge_gate_v20 as mod


class SPhi17IsotropicResidualChargeGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_keep_isotropic_awaiting_paper(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["decision"],
            "KEEP_ISOTROPIC_AWAITING_PAPER_LINEAR_CG",
        )
        self.assertTrue(self.report["flags"]["keep_isotropic_residual"])
        self.assertFalse(self.report["flags"]["drop_as_charge_forbidden"])
        self.assertFalse(self.report["flags"]["linear_cg_invented"])
        self.assertTrue(self.report["operators"]["210_norm_S"]["charge_allowed"])
        self.assertTrue(
            self.report["operators"]["210_norm_Phi17"]["charge_allowed"]
        )


if __name__ == "__main__":
    unittest.main()
