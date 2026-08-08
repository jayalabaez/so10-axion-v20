import unittest
from fractions import Fraction

import exact_gauged_u1x_g3_su5_max_negative_full_residual_bound_v20 as audit


class MaxNegativeFullResidualBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = audit.build_report()

    def test_live_source_normalizations_are_exact(self) -> None:
        source = audit.exact_restricted_source_matrices()
        self.assertTrue(source["source_binding_exact"])
        self.assertEqual(source["matrix_shapes"]["A_mixed"], (272, 210))
        self.assertEqual(source["matrix_shapes"]["A_chiral"], (504, 210))
        self.assertEqual(source["mixed_target_norm_squared"], 512)
        self.assertEqual(source["mixed_particular_residual_max_abs"], 0)
        self.assertEqual(source["chiral_particular_residual_max_abs"], 0)
        self.assertTrue(
            source["sliced_chiral_rows_equal_independent_reconstruction"]
        )

    def test_4125_scalar_covariant_is_an_exact_psd_bound(self) -> None:
        certificate = audit.exact_4125_scalar_covariant_certificate()
        self.assertTrue(certificate["proof_grade"])
        self.assertEqual(certificate["computed_nonzero_entry_gcd"], 49_152)
        self.assertEqual(certificate["Y_equals_projector_response_times"], 63)
        self.assertEqual(certificate["Y_Frobenius_norm_squared"], 70_560)
        self.assertEqual(certificate["z0_transpose_Y_z0"], 1120)
        self.assertEqual(certificate["particular_bound_value"], Fraction(8, 45))
        self.assertEqual(
            certificate["projector_response_norm_squared"], Fraction(160, 9)
        )
        self.assertEqual(certificate["physical_Cauchy_denominator"], 7_056_000)
        self.assertTrue(certificate["PD_Phi_projector_source_binding_exact"])
        self.assertEqual(certificate["maximum_connected_block_size"], 2)
        self.assertTrue(certificate["Y_plus_52I_PSD_exact"])
        self.assertEqual(certificate["shifted_nullity"], 6)

    def test_anchor_schur_bound_is_strict(self) -> None:
        certificate = audit.exact_anchor_schur_certificate()
        self.assertTrue(certificate["proof_grade"])
        self.assertEqual(
            certificate["exact_K_spectral_floor"], Fraction(7, 50_000)
        )
        self.assertEqual(
            certificate["forcing_Schur_value"],
            Fraction(13_448_450, 94_419_073),
        )
        self.assertEqual(certificate["basis_Gram_determinant"], 524_288)
        self.assertTrue(certificate["basis_linearly_independent_exact"])
        self.assertEqual(
            certificate["exact_anchor_lower_bound"],
            Fraction(20_777_185_031_397, 944_190_730_000_000),
        )
        self.assertGreater(
            certificate["exact_anchor_lower_bound"], Fraction(1, 50)
        )

    def test_piecewise_completion_and_saturation_are_exact(self) -> None:
        radial = audit.exact_piecewise_radial_certificate()
        saturation = audit.exact_saturation_certificate()
        self.assertTrue(radial["proof_grade"])
        self.assertEqual(
            radial["region_u_below_9_over_10"]["v_minimizer_u_shift"],
            Fraction(1, 5),
        )
        self.assertEqual(
            radial["region_u_below_9_over_10"][
                "derivative_at_u_equals_9_over_10"
            ],
            Fraction(-211, 1_000),
        )
        self.assertEqual(
            radial["region_u_below_9_over_10"]["minimum_on_0<=u<=9/10"],
            Fraction(83, 20_000),
        )
        self.assertEqual(
            radial[
                "region_u_at_least_9_over_10__v_at_least_1_over_4"
            ]["excess_above_1_over_5000"],
            Fraction(127, 9_950),
        )
        self.assertTrue(
            radial[
                "region_u_at_least_9_over_10__v_at_most_1_over_4"
            ]["coefficient_domination"]["proof_grade"]
        )
        self.assertTrue(
            radial[
                "region_u_at_least_9_over_10__v_at_least_1_over_4"
            ]["coefficient_domination"]["proof_grade"]
        )
        self.assertTrue(
            radial["quadrant_partition"]["covers_every_u_v_nonnegative"]
        )
        self.assertTrue(saturation["proof_grade"])
        self.assertEqual(saturation["restricted_gap"], Fraction(1, 5_000))

    def test_report_is_fail_closed_and_does_not_promote_g3(self) -> None:
        self.assertEqual(
            self.report["status"],
            "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED",
        )
        self.assertEqual(
            self.report["overall_state"],
            "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM",
        )
        self.assertEqual(self.report["n_failed"], 0)
        self.assertTrue(self.report["scope"]["Phi_arbitrary_real_210"])
        self.assertTrue(
            self.report["scope"]["nonzero_Phi_Sigma_residuals_covered"]
        )
        self.assertFalse(
            self.report["scope"]["arbitrary_Sigma_orientation_proved"]
        )
        self.assertFalse(self.report["scope"]["G3_closed"])


if __name__ == "__main__":
    unittest.main()
