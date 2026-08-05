#!/usr/bin/env python3
import unittest

import latest_main_residual_integration_v20 as mod


class LatestMainSourceCorrectionIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = mod.build_report()

    def test_execution(self):
        self.assertEqual(self.report["n_failed"], 0, self.report)
        self.assertEqual(self.report["overall_state"], "BLOCKED")

    def test_valid_work_is_retained(self):
        valid = self.report["valid_new_closures"]
        self.assertTrue(valid["live_pyrate_gauge_artifact"])
        self.assertTrue(valid["live_pyrate_reduced_quartic_soft_artifact"])
        self.assertTrue(valid["scalar_alpha_nonunique_from_current_flavour_fit"])
        self.assertTrue(valid["direct_Phi_H_Sigmabar_10x126_tensor_map"])
        self.assertTrue(valid["direct_tensor_closed_analytic_3p3p2p2_spectrum"])
        self.assertTrue(valid["published_gamma_TD_clebsch_crosscheck"])
        self.assertTrue(
            valid["map_repository_selected_vevs_to_canonical_tensor_convention"]
        )
        self.assertTrue(valid["direct_portal_component_mass_squared_insertion"])
        self.assertTrue(valid["EFJX_gauge_superhiggs_source_identified"])

    def test_contaminated_claims_are_withdrawn(self):
        withdrawn = self.report["withdrawn_or_reopened_claims"]
        for name, value in withdrawn.items():
            self.assertTrue(value, name)
        self.assertIsNone(
            self.report["dependency_audit"]["EFJX_old_8p8e29_bound"]
        )
        self.assertTrue(
            self.report["dependency_audit"][
                "mixed_susy_hessian_withdrawn"
            ]
        )
        self.assertTrue(
            self.report["dependency_audit"]["cal_G_route_withdrawn"]
        )

    def test_remaining_scope(self):
        for name, value in self.report["still_open"].items():
            self.assertTrue(value, name)

    def test_final_flags(self):
        flags = self.report["flag"]
        self.assertTrue(flags["direct_tensor_problem_closed"])
        self.assertTrue(flags["direct_portal_m2_block_inserted"])
        self.assertTrue(flags["EFJX_cgc_route_invalidated"])
        self.assertFalse(flags["old_8p8e29_bound_valid"])
        self.assertTrue(flags["all_susy_matrix_scalar_closures_withdrawn"])
        self.assertFalse(flags["exact_unique_proton_lifetime"])
        self.assertFalse(flags["whole_model_excluded"])
        self.assertFalse(flags["whole_model_validated"])


if __name__ == "__main__":
    unittest.main()
