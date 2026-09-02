import copy
import json
import unittest

import sympy as sp
import susy_v97_equivariant_index_relative_glue_section_audit as audit


class TestV97Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_lineage_and_core(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})

    def test_helpers_reconstruct(self):
        for key, module in zip(audit.KEYS, audit.MODULES):
            self.assertEqual(self.report[key], module.build_certificate())

    def test_source_test_pins(self):
        hashes = self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"], audit.file_sha(audit.TEST_PATH))
        for name, digest in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(digest, audit.file_sha(audit.ROOT/name))

    def test_normal_target_rebound(self):
        u, e2, p = sp.symbols("u e2 p")
        self.assertEqual(sp.sympify(self.report["cross_sector_scope_checks"]["unchanged_normal_target_I6"]), -u*e2+u**3+u*p/4)

    def test_normal_SU2_flat_class_not_erased(self):
        n = self.report["normal_SU2_refinement"]
        self.assertEqual(n["nonabelian_curvature_repair"]["residual"], "0")
        self.assertEqual(n["forced_Witten_class_in_this_ansatz"]["forced_Witten_parity"], 1)
        self.assertEqual(n["restricted_product_bordism"]["Omega5"], "Z2")
        self.assertTrue(n["flat_refinement"]["multiplying_by_nu_R_restores_reference_on_all_stated_product_backgrounds"])
        self.assertFalse(n["flat_refinement"]["restores_reference_means_trivializes_reference_anomaly"])

    def test_compact_equivariant_index_and_not_double_counted(self):
        m = self.report["equivariant_mass_defect_index"]
        rows = m["compact_equivariant_index"]["charge_block_results"]
        self.assertEqual(rows[0]["characters_identity_A_A2_A3"], ["0", "2", "-4", "2"])
        self.assertEqual([row["invariant_signed_index"] for row in rows], [0, 0])
        self.assertTrue(m["charge_reality_and_counting"]["conjugate_charge_block_must_not_be_counted_twice"])

    def test_conditional_gap_not_all_mass_vanishing(self):
        row = self.report["equivariant_mass_defect_index"]["small_mass_compact_gap"]
        self.assertEqual(row["strict_invertibility_condition"], "|lambda|*L<4*pi")
        self.assertEqual(row["left_and_right_projected_kernel_dimensions_in_that_range"], [0, 0])
        self.assertFalse(row["gap_at_every_mass_or_with_extra_backgrounds_established"])
        self.assertFalse(row["absence_of_massless_modes_cancels_local_anomalies"])

    def test_primitive_common_quarter_class(self):
        r = self.report["mixed_gauge_relative_glue"]
        self.assertEqual(r["exact_index_decomposition"]["fractional_profile"], ["1/4", "1/4", "-1/2"])
        self.assertEqual(r["primitive_period_and_order"]["P_over4_exact_order_mod_quantized_curvatures"], 4)
        self.assertEqual(r["primitive_period_and_order"]["rows"][0]["R_periods"], ["61/4", "61/4", "-1/2"])

    def test_integer_responses_not_full_relative_action(self):
        r = self.report["mixed_gauge_relative_glue"]
        self.assertTrue(r["quantized_integer_piece_responses"]["quantized_integer_piece_responses_constructed"])
        self.assertFalse(r["quantized_integer_piece_responses"]["combined_original_anomaly_character_proved_cancelled"])
        self.assertFalse(r["correlated_filling_screen"]["formal_transgression_is_a_quantized_relative_action"])

    def test_actual_normal_root_not_omitted(self):
        r = self.report["mixed_gauge_relative_glue"]["equivariant_virtual_carrier_and_normal_lift"]
        case = r["cases"]["actual_normal_root_uncompensated"]
        self.assertEqual(case["H_fourth_powers"], ["1", "1"])
        self.assertEqual(case["raw_stratum_profile"], ["0", "0", "0"])
        self.assertFalse(case["frozen_H_fourth_minus_identity_condition_passes"])
        self.assertTrue(r["conditional_compensator"]["restores_the_frozen_effective_H_and_formal_P_profile_algebraically"])
        self.assertFalse(r["conditional_compensator"]["compatible_full_Gammahat_kernel_representation_constructed"])

    def test_section_b4_zero_exclusion(self):
        row = self.report["original_cubic_section"]["b4_zero_subbranch_exclusion"]
        self.assertTrue(row["entire_b4_zero_branch_excluded_over_algebraic_closure_C_X"])
        self.assertEqual(row["h_nonzero"]["first_two_resultant_mod_prime"], 37)
        self.assertEqual(row["h_zero"]["value_at_X_one"], "-1407/32")

    def test_surviving_original_square_condition(self):
        row = self.report["original_cubic_section"]["remaining_nonzero_b4_system"]
        self.assertEqual(row["equation_count"], 4)
        self.assertEqual(row["unknowns_over_C_X"], ["z", "H", "K"])
        self.assertTrue(row["z_must_be_nonzero_square_in_C_X"])
        self.assertFalse(row["system_solved_over_C_X"])

    def test_original_rank_not_promoted(self):
        row = self.report["original_cubic_section"]["preserved_frontier"]
        self.assertEqual(row["original_free_rank_upper_bound"], 11)
        self.assertFalse(row["all_rational_sections_excluded"])
        self.assertFalse(row["target_height_or_primitive_generator_constructed"])

    def test_separate_candidates_not_conflated(self):
        row = self.report["cross_sector_scope_checks"]
        for key in ("old_charge_two_mass_model_and_new_virtual_P_carrier_are_same_sector", "all_new_candidate_sectors_simultaneously_installed_in_one_action", "common_order4_class_is_the_same_as_isolated_defect_bordism_anomaly", "independent_wall_normal_and_Phi_vortex_normal_bundles_identified", "all_new_quantized_responses_glued_to_parent"):
            self.assertFalse(row[key])

    def test_eight_open_gates(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"], [])
        self.assertFalse(self.report["terminal_decision"]["all_F97_obligations_fully_completed"])

    def test_F98_next(self):
        self.assertEqual(self.report["next_required_action"]["id"], "F98_GAMMAHAT_TRANSPORT_LIFT_AND_ORIGINAL_SQUARE_SECTION")

    def test_rehashed_scope_promotion_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["terminal_decision"]["theory_complete"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_candidate_identification_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["cross_sector_scope_checks"]["old_charge_two_mass_model_and_new_virtual_P_carrier_are_same_sector"] = True
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_readable_scope_boundaries(self):
        markdown = audit.render_markdown(self.report)
        for phrase in ("All eight SUSY/C8 gates remain OPEN", "not the old charge-two Dirac model", "a square in C(X)", "not a rank-specialization argument", "Witten sign", "even though the mass vanishes"):
            self.assertIn(phrase, markdown)

    def test_generated_artifacts_match(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
