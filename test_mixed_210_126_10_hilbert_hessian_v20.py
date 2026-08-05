#!/usr/bin/env python3
import unittest

import mixed_210_126_10_hilbert_hessian_v20 as mod


class MixedHessianSourceCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_withdrawn_fail_closed(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")
        self.assertEqual(
            self.report["status"],
            "MIXED_SUSY_FERMION_MATRICES_WITHDRAWN_FROM_NONSUSY_HESSIAN",
        )

    def test_old_scalar_hessian_claim_is_false(self):
        flags = self.report["flag"]
        self.assertFalse(flags["mixed_210_126_10_complete"])
        self.assertFalse(flags["cal_T_D_E_F_J_X_G_included_as_scalar_hessian"])
        self.assertTrue(flags["imported_susy_hessian_withdrawn"])
        self.assertFalse(flags["combined_extended_hessian_pd"])
        self.assertFalse(flags["full_sm_irrep_mass_matrices"])

    def test_direct_tensor_is_retained(self):
        self.assertTrue(self.report["flag"]["direct_portal_tensor_available"])
        self.assertEqual(
            self.report["direct_tensor_replacement"]["map_shape"], [10, 126]
        )
        self.assertTrue(
            self.report["direct_tensor_replacement"]["analytic_spectrum_derived"]
        )

    def test_no_scalar_rows_emitted(self):
        self.assertTrue(self.report["mixed_spectra"]["withdrawn"])
        self.assertEqual(self.report["mixed_spectra"]["n_blocks"], 0)
        self.assertEqual(self.report["hessian_extension"]["n_physical_rows"], 0)
        self.assertEqual(mod.hessian_rows_from_mixed({}), [])

    def test_helper_is_diagnostic_only(self):
        p = mod.hilbert_matched_params(
            a=1.0,
            omega=1.0,
            p=1.0,
            m_i=1.0,
            m_gut=1.0,
            lam=0.1,
            eta=0.1,
        )
        self.assertEqual(p["gamma"], 0.0)
        self.assertTrue(p["pq_gamma_forbidden"])
        self.assertIn("diagnostic", p["physical_use"])

    def test_no_model_overclaim(self):
        self.assertFalse(self.report["flag"]["whole_model_validated"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(self.report["flag"]["exact_unique_proton_lifetime"])


if __name__ == "__main__":
    unittest.main()
