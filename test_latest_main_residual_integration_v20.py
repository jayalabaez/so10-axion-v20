#!/usr/bin/env python3
import unittest

import latest_main_residual_integration_v20 as mod


class LatestMainResidualIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_execution(self):
        self.assertEqual(self.report["n_failed"], 0, self.report["failures"])

    def test_valid_new_closures_are_kept(self):
        valid = self.report["valid_new_closures"]
        self.assertTrue(valid["live_pyrate_gauge_artifact"])
        self.assertTrue(valid["live_pyrate_reduced_quartic_soft_artifact"])
        self.assertTrue(valid["scalar_alpha_nonunique_from_current_flavour_fit"])
        self.assertTrue(valid["cal_G_lambda_lock_lift_mechanism_exists_in_principle"])
        self.assertTrue(
            valid["EFJX_gamma_response_matrices_known_in_Aulakh_convention"]
        )

    def test_proxy_selected_point_closures_are_invalidated(self):
        invalid = self.report["invalidated_selected_point_claims"]
        self.assertTrue(invalid["lambda_lock_raise_does_not_spoil_selected_point"])
        self.assertTrue(invalid["all_post_hessian_residuals_closed"])
        self.assertTrue(invalid["proxy_c_cgc_needed_abs_approx_is_physical"])
        self.assertLess(
            self.report["dependency_audit"][
                "physical_historical_min_eigenvalue_GeV2"
            ],
            -1.0e30,
        )
        self.assertFalse(
            self.report["dependency_audit"][
                "EFJX_physical_cgc_normalization_derived"
            ]
        )

    def test_remaining_scope(self):
        remaining = self.report["still_open"]
        self.assertTrue(remaining["full_210_tensor_quartic_basis_in_live_dump"])
        self.assertTrue(remaining["lambda4_CGC_live_encoding"])
        self.assertTrue(remaining["dim6_lambda_lock_live_encoding"])
        self.assertTrue(
            remaining["physical_EFJX_CGC_normalization_on_h174_branch"]
        )
        self.assertTrue(
            remaining["physical_EW_reminimization_after_EFJX_CGC"]
        )
        self.assertTrue(
            remaining["cal_G_lift_revalidation_on_physical_EW_survival_point"]
        )
        self.assertTrue(remaining["exact_unique_proton_lifetime"])
        self.assertTrue(
            self.report["flag"]["EFJX_response_known_but_physical_CGC_open"]
        )
        self.assertFalse(self.report["flag"]["whole_model_excluded"])


if __name__ == "__main__":
    unittest.main()
