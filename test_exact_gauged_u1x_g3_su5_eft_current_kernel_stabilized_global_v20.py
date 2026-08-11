import unittest

import exact_gauged_u1x_g3_su5_eft_current_kernel_stabilized_global_v20 as theorem


class EFTCurrentKernelStabilizedGlobalG3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = theorem.build_report()

    def test_core_and_global_sos(self):
        self.assertEqual(
            self.report["core_sha256"],
            theorem.EXPECTED_CORE_SHA256,
        )
        sos = self.report["candidate_and_global_SOS"]
        self.assertTrue(sos["bounded_below_for_arbitrary_486_real_fields"])
        self.assertTrue(sos["selected_target_saturates_every_residual"])
        self.assertFalse(
            sos["EFT_operator"]["inside_renormalizable_51_parameter_contract"]
        )

    def test_exact_current_lattices(self):
        current = theorem.exact_signed_current_hessian_numerator()["report"]
        self.assertTrue(current["source_derivation_exact"])
        self.assertEqual(current["raw_Hessian_denominator"], 200)
        self.assertEqual(
            current["payload_sha256"],
            theorem.EXPECTED_SIGNED_CURRENT_NUMERATOR_SHA256,
        )
        jacobian = theorem.exact_current_kernel_jacobian()["report"]
        self.assertTrue(jacobian["exact_integer_source_derivation"])
        self.assertEqual(jacobian["live_realification_crosscheck_residual"], 0.0)
        self.assertEqual(jacobian["payload_sha256"], theorem.EXPECTED_JACOBIAN_SHA256)

    def test_exact_hessian_and_kernel_intersection(self):
        result = self.report["exact_stabilized_Hessian"]
        base = result["beta_zero_base"]
        final = result["stabilized"]
        kernel = result["kernel_intersection"]
        self.assertTrue(base["exact_PSD"])
        self.assertEqual((base["exact_rank"], base["exact_nullity"]), (442, 44))
        self.assertEqual(base["payload_sha256"], theorem.EXPECTED_BASE_HESSIAN_SHA256)
        self.assertEqual((final["exact_rank"], final["exact_nullity"]), (448, 38))
        self.assertEqual(
            final["payload_sha256"], theorem.EXPECTED_STABILIZED_HESSIAN_SHA256
        )
        self.assertEqual(
            final["raw_integer_formula"],
            "Hgamma_integer=H0_integer+12600 J^T J",
        )
        self.assertEqual(set(kernel["ranks_mod_primes"].values()), {448})
        self.assertTrue(kernel["six_nonsymmetry_base_flats_lifted"])

    def test_global_equality_orbit(self):
        equality = self.report["exact_global_equality_orbit"]
        self.assertTrue(equality["global_equality_orbit_classification_complete"])
        self.assertEqual(equality["selected_stabilizer"], "SU(3)_C x U(1)_em")
        self.assertTrue(
            equality["step_5_EFT_flag"]["coefficientwise_integer_guard"]
        )
        self.assertEqual(equality["selected_full_symmetry_orbit_rank"], 38)

    def test_scope_and_closure_flags(self):
        scope = self.report["scope_boundary"]
        flags = self.report["closure_flags"]
        self.assertTrue(scope["EFT_dimension_six_extension"])
        self.assertFalse(scope["authoritative_renormalizable_51_parameter_model"])
        self.assertTrue(flags["G3_closed_for_EFT_extended_model"])
        self.assertFalse(flags["G3_closed_for_original_renormalizable_model"])
        self.assertFalse(flags["G4_closed"])


if __name__ == "__main__":
    unittest.main()
