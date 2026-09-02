import copy
import unittest

import v92_singlet_mass_module as module
import v92_singlet_projector_certificate as projectors


class TestV92SingletMassModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projectors = projectors.build_certificate()
        cls.result = module.build_certificate(cls.projectors)

    def test_channels_are_gauge_and_conditionally_R_invariant(self):
        for row in self.result["charge_checked_channels"]:
            self.assertEqual(row["continuous_charge_sum"],0)
            self.assertEqual(row["finite_C8_sum_mod8"],0)
            self.assertEqual(row["R4_sum_mod4"],2)

    def test_nine_by_nine_mass_matrix_full_rank_only_at_nonzero_vev(self):
        row = self.result["calculation"]
        self.assertEqual(row["mass_matrix_determinant"],"-v**9")
        self.assertEqual(row["rank_for_v_nonzero"],9)
        self.assertEqual(row["rank_for_v_zero"],0)
        self.assertEqual(row["M_dagger_M_over_abs_v_squared"],[[int(i==j) for j in range(9)] for i in range(9)])

    def test_vacuum_not_shifted_by_this_module_at_origin(self):
        self.assertEqual(self.result["calculation"]["F_residuals_at_S_zero"],["0"]*10)
        self.assertTrue(self.result["preexisting_F_and_D_equations_unchanged_at_S_zero"])

    def test_changed_charge_signs_rejected(self):
        changed = copy.deepcopy(self.projectors)
        changed["eleven_mode_normal_aligned_witness"]["constant_N1_signed_continuous_charges"][7] = -6
        changed["core_sha256"] = projectors.canonical_sha(changed)
        with self.assertRaisesRegex(RuntimeError,"all-positive"):
            module.build_certificate(changed)

    def test_noncanonical_supplied_projector_report_rejected(self):
        changed = copy.deepcopy(self.projectors)
        changed["core_sha256"] = "0"*64
        with self.assertRaisesRegex(RuntimeError,"noncanonical"):
            module.build_certificate(changed)

    def test_local_mass_ansatz_not_promoted_to_action_or_anomaly_solution(self):
        for key in ("R_assignment_was_previously_frozen","orbifold_m_is_identified_with_independent_R4",
                    "new_R4_action_descends_through_full_Gammahat_kernel",
                    "all_localized_operator_representations_constructed",
                    "full_gauged_Kahler_or_sugra_action_constructed",
                    "new_sector_full_anomaly_cancelled",
                    "integrating_out_chiral_fields_erases_anomaly_matching_obligations",
                    "mass_terms_are_derived_from_the_existing_six_dimensional_action","gate_closed"):
            self.assertFalse(self.result[key])


if __name__ == "__main__":
    unittest.main()
