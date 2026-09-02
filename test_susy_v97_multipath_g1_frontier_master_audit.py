import copy
import json
import unittest

import sympy as sp

import susy_v97_multipath_g1_frontier_master_audit as audit


class TestV97Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.previous = audit.load_bound(audit.V96_PATH, audit.EXPECTED_CORES["v96_master"])
        cls.route = audit.load_bound(audit.V97_PATH, audit.EXPECTED_CORES["v97_route"])

    def test_canonical_lineage_and_validation(self):
        self.assertEqual(self.report["input_core_hashes"], audit.EXPECTED_CORES)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_report(self.report)

    def test_all_twenty_four_previous_routes_unchanged(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(json.dumps(self.report["route_matrix"][:-1], sort_keys=True, separators=(",", ":")),
                         json.dumps(self.previous["route_matrix"], sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))
        self.assertEqual(self.report["lineage"]["parent_route_count"], 24)

    def test_B97_appended_ordinal25_unaccepted(self):
        rows = self.report["route_matrix"]
        self.assertEqual([row["ordinal"] for row in rows], list(range(1, 26)))
        self.assertEqual(rows[-1]["route_id"], "B97")
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])

    def test_new_SU2_representation_changes_old_R_assignments(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["new_SU2_R_highest_weight"], 1)
        self.assertEqual(card["new_R_weights"], [-1, 1])
        self.assertEqual(card["new_normal_root_weight"], -3)
        self.assertEqual(card["new_complex_Weyl_components"], 2)
        self.assertFalse(card["new_SU2_representation_is_unchanged_V96_R_representation"])

    def test_normal_R_curvature_and_required_Witten_class_both_retained(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["new_sector_normal_R_curvature_residual"], "0")
        self.assertEqual(card["new_normal_R_CS_integer_coefficients"], [-1, 10, -3])
        self.assertEqual(card["new_SU2_repair_forced_Witten_parity"], 1)
        self.assertEqual(card["new_SU2_repair_product_bordism"], "Z2")
        self.assertTrue(card["nu_R_restores_reference_on_stated_product_backgrounds"])
        self.assertFalse(card["restoring_reference_trivializes_reference_anomaly"])
        self.assertFalse(card["nu_R_same_action_inflow_constructed"])
        self.assertFalse(card["new_sector_cancels_original_bulk_R_flavor_anomalies"])

    def test_conditional_projected_index_and_core_modes_are_zero(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["conditional_mass_invariant_chiral_index"], 0)
        self.assertEqual(card["isolated_protected_linear_core_modes_surviving_projection"], 0)
        self.assertFalse(card["zero_index_alone_proves_zero_kernel"])
        self.assertEqual(card["conditional_mass_operator_assumptions"],
                         self.route["equivariant_mass_defect_index"]["conditional_Dirac_operator"]["new_assumptions"])

    def test_small_mass_gap_is_bounded_and_conditional(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["conditional_projected_gap_lower_bound"], "2*pi/L-|lambda|/2")
        self.assertEqual(card["conditional_projected_invertibility_range"], "|lambda|*L<4*pi")
        self.assertEqual(card["conditional_projected_kernel_dimensions_in_range"], [0, 0])
        self.assertFalse(card["gap_for_all_masses_or_extra_backgrounds_proved"])
        self.assertFalse(card["conditional_gap_cancels_local_anomalies"])
        self.assertFalse(card["full_mass_SMW_Gammahat_action_constructed"])
        self.assertFalse(card["mass_supersymmetric_completion_constructed"])

    def test_common_primitive_order_four_profile_and_quantized_integer_parts(self):
        card = self.report["consolidated_theory_card"]
        d, u = sp.symbols("d u")
        self.assertEqual(sp.expand(sp.sympify(card["primitive_common_mixed_polynomial_P"])-d*d*(d+u)), 0)
        self.assertEqual(card["common_mixed_fractional_profile"], ["1/4", "1/4", "-1/2"])
        self.assertEqual(card["common_mixed_fractional_profile_sum"], "0")
        self.assertEqual(card["P_over_four_order_mod_quantized_curvatures"], 4)
        self.assertTrue(card["integer_mixed_response_pieces_quantized"])
        self.assertTrue(card["common_product_negative_total_curvature_response_constructed"])
        self.assertFalse(card["P_curvature_order_is_full_Gammahat_anomaly_order"])
        self.assertFalse(card["integer_response_cancels_unknown_original_anomaly_character"])

    def test_actual_normal_isotropy_zero_trace_is_inadmissible_not_cancellation(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["actual_normal_uncompensated_H_fourth_powers"], ["1", "1"])
        self.assertEqual(card["actual_normal_uncompensated_raw_profile"], ["0", "0", "0"])
        self.assertFalse(card["actual_normal_uncompensated_frozen_closure_passes"])
        self.assertFalse(card["actual_normal_uncompensated_physical_sector_constructed"])

    def test_projective_compensator_is_not_full_Gammahat_gluing(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["conditional_compensator_fourth_power"], "-I")
        self.assertEqual(card["conditional_compensator_order"], 8)
        self.assertTrue(card["conditional_compensator_restores_profile_algebraically"])
        self.assertFalse(card["conditional_compensator_full_Gammahat_representation_constructed"])
        self.assertFalse(card["formal_carrier_is_quantized_relative_determinant"])
        self.assertFalse(card["five_and_three_dimensional_responses_glued"])

    def test_cubic_zero_b4_obstruction_and_exact_resultant(self):
        card = self.report["consolidated_theory_card"]
        self.assertTrue(card["original_leading_minus24_cubic_b4_zero_branch_excluded"])
        self.assertEqual(card["original_cubic_h_zero_obstruction_at_X_one"], "-1407/32")
        self.assertEqual(card["original_cubic_resultant_mod101"], 37)

    def test_remaining_cubic_square_branch_not_claimed_solved(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["remaining_cubic_equation_count"], 4)
        self.assertEqual(card["remaining_cubic_unknowns_over_C_X"], ["z", "H", "K"])
        self.assertTrue(card["remaining_cubic_requires_nonzero_original_field_square"])
        self.assertFalse(card["remaining_cubic_original_field_system_solved"])
        self.assertFalse(card["actual_original_nonzero_section_constructed"])
        self.assertFalse(card["all_original_cubic_sections_excluded"])
        self.assertFalse(card["all_original_rational_sections_excluded"])

    def test_original_rank_torsion_and_height_normalization_preserved(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["actual_original_MW_torsion_order"], 1)
        self.assertEqual(card["actual_original_MW_free_rank_bounds"], [0, 11])
        self.assertIsNone(card["actual_original_MW_free_rank"])
        self.assertEqual(card["conditional_unit_charge_section_height_S_F"], [148, 768])
        self.assertEqual(card["conditional_doubled_charge_section_height_S_F"], [37, 192])

    def test_decisions_supersession_gates_next_sources_copied_exactly(self):
        for key, route_key in (("strict_master_decision", "terminal_decision"),
                               ("supersession_ledger", "supersession_boundary"), ("gate_ledger", "gate_ledger"),
                               ("next_required_action", "next_required_action"), ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[key], self.route[route_key])

    def test_eight_gates_open_no_parent_and_F98(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["accepted_extension_count"], 0)
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        for key in ("full_quantum_anomaly_cancelled", "same_action_spectrum_and_geometry_realized", "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(card[key])

    def assert_rehashed_card_change_rejected(self, key, value):
        changed = copy.deepcopy(self.report)
        changed["consolidated_theory_card"][key] = value
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_old_history_change_rejected(self):
        changed = copy.deepcopy(self.report)
        changed["route_matrix"][0]["name"] = "forged"
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_Witten_erasure_rejected(self):
        self.assert_rehashed_card_change_rejected("new_SU2_repair_forced_Witten_parity", 0)

    def test_rehashed_arbitrary_mass_gap_promotion_rejected(self):
        self.assert_rehashed_card_change_rejected("gap_for_all_masses_or_extra_backgrounds_proved", True)

    def test_rehashed_raw_profile_physical_promotion_rejected(self):
        self.assert_rehashed_card_change_rejected("actual_normal_uncompensated_physical_sector_constructed", True)

    def test_rehashed_compensator_full_descent_promotion_rejected(self):
        self.assert_rehashed_card_change_rejected("conditional_compensator_full_Gammahat_representation_constructed", True)

    def test_rehashed_square_condition_erasure_rejected(self):
        self.assert_rehashed_card_change_rejected("remaining_cubic_requires_nonzero_original_field_square", False)

    def test_rehashed_general_section_exclusion_rejected(self):
        self.assert_rehashed_card_change_rejected("all_original_rational_sections_excluded", True)

    def test_readable_report_retains_scope_boundaries(self):
        markdown = audit.render_markdown(self.report)
        self.assertNotIn("|---", markdown)
        for phrase in ("All eight SUSY/C8 gates remain OPEN", "No complete theory", "Witten parity",
                       "does not trivialize that reference anomaly", "Index zero alone", "|lambda|*L<4*pi",
                       "not a physical cancellation", "not a specialization rank argument", "nonzero square in C(X)",
                       "q_Sh=q_displayed/2"):
            self.assertIn(phrase, markdown)
        self.assertIn("extension-field statement does not apply to V96's separate leading-12 branch", markdown)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
