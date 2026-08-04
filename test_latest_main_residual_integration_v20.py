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
        self.assertTrue(valid["EFJX_gauge_superhiggs_response_identified"])
        self.assertTrue(valid["direct_Phi_H_Sigmabar_10x126_tensor_map"])

    def test_false_efjx_claims_are_invalidated(self):
        invalid = self.report["invalidated_selected_point_claims"]
        self.assertTrue(invalid["lambda_lock_raise_does_not_spoil_selected_point"])
        self.assertTrue(invalid["all_post_hessian_residuals_closed"])
        self.assertTrue(invalid["proxy_c_cgc_needed_abs_approx_is_physical"])
        self.assertTrue(invalid["EFJX_gauge_response_is_lambda4_gamma_response"])
        self.assertTrue(invalid["c_norm_needed_is_8p8e29"])
        self.assertIsNone(self.report["dependency_audit"]["EFJX_old_8p8e29_bound"])

    def test_remaining_scope(self):
        remaining = self.report["still_open"]
        self.assertTrue(remaining["full_210_tensor_quartic_basis_in_live_dump"])
        self.assertTrue(remaining["lambda4_CGC_live_encoding"])
        self.assertTrue(remaining["dim6_lambda_lock_live_encoding"])
        self.assertTrue(remaining["published_state_label_dictionary_for_direct_tensor"])
        self.assertTrue(remaining["direct_nonsusy_component_mass_squared_insertion"])
        self.assertTrue(remaining["full_component_hessian_after_direct_tensor"])
        self.assertTrue(remaining["exact_unique_proton_lifetime"])
        self.assertTrue(
            self.report["flag"]["EFJX_cgc_route_invalidated_direct_tensor_open"]
        )
        self.assertFalse(self.report["flag"]["old_8p8e29_bound_valid"])
        self.assertFalse(self.report["flag"]["whole_model_excluded"])
        self.assertFalse(self.report["flag"]["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
