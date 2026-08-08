import os
import unittest
from fractions import Fraction

import exact_gauged_u1x_g3_replacement_stationary_orbit_v20 as gate


class ReplacementStationaryOrbitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stationarity = gate.exact_full_stationarity_certificate()
        cls.orbit = gate.exact_orbit_rank_certificate()
        cls.no_go = gate.exact_fixed_p_gap_curvature_no_go()
        cls.report = gate.build_report()

    def test_sigma_gradient_is_exactly_radial(self):
        sigma = self.stationarity["Sigma_252_real_coordinates"]
        self.assertEqual(sigma["gradient_eigenvalue"], Fraction(33))
        self.assertEqual(sigma["maximum_gradient_identity_residual"], 0)
        self.assertTrue(sigma["full_252_real_gradient_cancellation"])
        self.assertEqual(sigma["Sigma_norm_squared_over_r2"], Fraction(100, 99))

    def test_complete_486_stationarity_is_source_bound(self):
        self.assertEqual(self.stationarity["complete_nonzero_parameter_count"], 27)
        self.assertTrue(self.stationarity["complete_27_parameter_map_source_bound"])
        self.assertTrue(self.stationarity["full_486_gradient_exactly_zero"])
        self.assertTrue(self.stationarity["source_binding_exact"])

    def test_mixed_square_zero_locus_is_exact(self):
        mixed = self.stationarity["mixed_square_zero_locus"]
        self.assertEqual(mixed["A_P_minus_2_z_norm_squared"], 0)
        self.assertEqual(mixed["C_P_z_norm_squared"], 0)
        self.assertTrue(mixed["all_Phi_and_Sigma_mixed_square_gradients_zero"])

    def test_exact_orbit_ranks_and_quotient(self):
        self.assertEqual(self.orbit["P_plus_Sigma_SO10"]["rank"], 36)
        self.assertEqual(self.orbit["SO10"]["rank"], 39)
        self.assertEqual(self.orbit["SO10_plus_U1X"]["rank"], 40)
        self.assertEqual(self.orbit["SO10_plus_U1X_plus_PQ"]["rank"], 41)
        self.assertEqual(self.orbit["physical_quotient_dimension"], 445)
        self.assertNotEqual(
            self.orbit["SO10_plus_U1X_plus_PQ"]["nonzero_minor_determinant"],
            "0",
        )
        self.assertTrue(self.orbit["source_binding_exact"])

    def test_numerical_hessian_is_positive_but_not_promoted(self):
        hessian = self.report["live_hessian_classification"]
        self.assertEqual(hessian["transverse_dimension"], 445)
        self.assertGreater(hessian["minimum_transverse_eigenvalue"], 0.005)
        self.assertEqual(
            hessian["negative_transverse_eigenvalues_below_minus_1e_minus_10"], 0
        )
        self.assertEqual(hessian["zero_transverse_eigenvalues_at_1e_minus_10"], 0)
        self.assertTrue(hessian["strict_local_minimum_high_confidence_numeric"])
        self.assertFalse(hessian["strict_local_minimum_proof_grade"])

    def test_explicit_two_tangent_gap_curvature_no_go(self):
        tangent = self.no_go["explicit_two_tangent_source_binding"]
        expected = {
            "54": Fraction(0),
            "1050bar": Fraction(0),
            "2772bar": Fraction(4, 3),
            "4125": Fraction(-4, 3),
        }
        self.assertEqual(tangent["tangent_inner_product"], 0)
        self.assertEqual(tangent["P_plus_Delta_SO10_gauge_rank"], 33)
        self.assertEqual(tangent["rank_after_adding_both_tangents"], 35)
        self.assertTrue(tangent["both_tangents_non_gauge"])
        for name in ("A", "B"):
            record = tangent["tangents"][name]
            self.assertEqual(record["q_norm_squared"], 8)
            self.assertEqual(record["channel_Hessian_signatures"], expected)
            self.assertEqual(record["A_P_minus_2_tangent_norm_squared"], 0)
            self.assertEqual(record["C_P_tangent_norm_squared"], 0)
        self.assertTrue(tangent["source_binding_exact"])

    def test_all_six_O44_values_and_full_51_gap_are_exact(self):
        o44 = self.no_go["all_six_O44_endpoint_values"]
        self.assertTrue(o44["all_six_individual_O44_values_equal_exactly"])
        self.assertEqual(
            o44["expected_common_values"],
            {
                "1": Fraction(1, 21),
                "45": Fraction(0),
                "210": Fraction(0),
                "770": Fraction(-2, 15),
                "5940": Fraction(0),
                "8910": Fraction(3, 35),
            },
        )
        self.assertEqual(self.no_go["exact_X_parameter_count"], 51)
        self.assertEqual(
            self.no_go["number_of_exact_zero_parameter_differences"], 49
        )
        self.assertEqual(
            self.no_go["number_of_exact_nonzero_parameter_differences"], 2
        )
        self.assertTrue(self.no_go["gap_equals_minus_one_eighth_curvature"])
        self.assertTrue(self.no_go["source_binding_exact"])

    def test_replacement_has_wrong_target_gauge_symmetry(self):
        self.assertEqual(self.orbit["SO10_plus_U1X"]["rank"], 40)
        self.assertNotEqual(
            self.orbit["SO10_plus_U1X"]["rank"],
            gate.TARGET_SELECTED_GAUGE_ORBIT_RANK,
        )
        self.assertFalse(
            self.report["flags"]["replacement_target_gauge_symmetry_correct"]
        )

    def test_global_and_G3_claims_remain_open(self):
        flags = self.report["flags"]
        self.assertTrue(flags["replacement_full_stationarity_exact"])
        self.assertFalse(flags["replacement_strict_local_minimum_proof_grade"])
        self.assertFalse(flags["replacement_global_minimum_established"])
        self.assertFalse(flags["replacement_global_uniqueness_established"])
        self.assertFalse(flags["G3_closed"])

    @unittest.skipUnless(
        os.environ.get("RUN_G3_REPLACEMENT_HEAVY") == "1",
        "set RUN_G3_REPLACEMENT_HEAVY=1 for the live 486-Hessian rebuild",
    )
    def test_live_heavy_recomputation(self):
        observed = gate.recompute_live_unit_scale_hessian()
        self.assertEqual(observed["nonzero_parameter_count"], 27)
        self.assertEqual(observed["numerical_symmetry_orbit_rank"], 41)
        self.assertEqual(observed["transverse_dimension"], 445)
        self.assertGreater(observed["minimum_transverse_eigenvalue"], 0.005)
        self.assertTrue(observed["strict_local_minimum_high_confidence_numeric"])


if __name__ == "__main__":
    unittest.main()
