#!/usr/bin/env python3
"""Tests for the withdrawn λ₄-potential / E/F/J/X decoupling certificate."""

from __future__ import annotations

import unittest

import lam4_potential_efjx_decoupling_v20 as mod


class Lam4PotentialEfjxDecouplingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_status_ok(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(
            self.report["status"],
            "LAM4_EFJX_DECOUPLING_CERTIFICATE_WITHDRAWN__DIRECT_TENSOR_REQUIRED",
        )
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_old_spoiling_claims_are_withdrawn(self):
        flags = self.report["flag"]
        self.assertFalse(flags["lam4_potential_raise_proved_spoiling"])
        self.assertTrue(flags["old_lam4_efjx_decoupling_certificate_withdrawn"])
        self.assertFalse(flags["cgc_ratio_needed_quantified"])
        withdrawn = self.report["withdrawn_claims"]
        self.assertIsNone(withdrawn["lam4_crit_abs"])
        self.assertIsNone(withdrawn["c_cgc_needed_abs_approx"])
        self.assertFalse(withdrawn["gamma_at_crit_clears_efjx"])
        self.assertFalse(withdrawn["raise_to_efjx_tol_proved_spoiling"])

    def test_historical_radial_still_tachyonic(self):
        self.assertTrue(
            self.report["checks"]["historical_radial_point_still_tachyonic"]
        )
        self.assertTrue(self.report["historical_radial_result"]["tachyonic"])

    def test_direct_tensor_replacement_required(self):
        cert = self.report["certificate"]
        self.assertTrue(cert["direct_scalar_tensor_map_now_required"])
        self.assertFalse(cert["old_decoupling_certificate_valid"])
        self.assertFalse(cert["physical_cgc_still_required"])
        shape = self.report["direct_tensor_replacement"]["map_shape"]
        self.assertEqual(shape, [10, 126])

    def test_honesty(self):
        flags = self.report["flag"]
        self.assertTrue(flags["lam4_cgc_and_dim6_lock_not_in_live_dump"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["whole_model_validated"])
        self.assertTrue(
            self.report["still_open"]["complete_nonsusy_component_hessian"]
        )


if __name__ == "__main__":
    unittest.main()
