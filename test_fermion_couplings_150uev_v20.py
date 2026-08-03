#!/usr/bin/env python3
"""Fail-closed tests for the v20 fermion benchmark and open matching."""

import unittest

import fermion_couplings_150uev_v20 as m


class FermionCouplingAudit(unittest.TestCase):
    def test_exact_reduced_axion_projection(self):
        expected = (
            m.VS_GEV
            * m.VPHI_GEV
            / ((17.0 * m.VPHI_GEV) ** 2 + (4.0 * m.VS_GEV) ** 2) ** 0.5
        )
        self.assertAlmostEqual(m.FA_GEV, expected)

    def test_aligned_central_numbers(self):
        row = m.aligned_coefficients(1.5)
        self.assertIn("ALIGNED_CURRENT", row["classification"])
        self.assertAlmostEqual(row["C_e"], 0.04072398190036261, places=14)
        self.assertAlmostEqual(row["C_p"], -0.4721493212669636, places=14)
        self.assertAlmostEqual(row["C_n"], 0.0065837104071811425, places=14)

    def test_legacy_rounded_comparison_is_gated(self):
        with self.assertRaises(RuntimeError):
            m.ert_leading_extrapolation(1.5)
        row = m.ert_leading_extrapolation(
            1.5, acknowledge_not_full_matching=True
        )
        self.assertIn("LEGACY_ROUNDED", row["classification"])

    def test_one_family_physical_shift_is_not_erased_by_berry_sum(self):
        row = m.q_portal_one_family_diagnostic(lambda_q=1.0, y_q=1.0)
        self.assertGreater(row["projected_shift_norm"], 0.0)
        self.assertGreater(row["berry_norm"], 0.0)
        self.assertLess(row["moving_identity_error"], 1e-12)
        self.assertFalse(row["physical_shift_is_zero"])

    def test_report_fails_closed(self):
        report = m.build_report()
        self.assertIn("MATCHING_OPEN", report["status"])
        self.assertIsNone(
            report["aligned_bound_checks_only"]["full_model_pass"]
        )
        self.assertIn("Q_proj=I-4W", report["correction_history"]["current_resolution"])
        self.assertIn("remain open", report["verdict"])


if __name__ == "__main__":
    unittest.main()
