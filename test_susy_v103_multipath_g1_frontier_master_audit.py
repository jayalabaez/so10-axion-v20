"""Immutable history, scientific scope and fresh source tests for V103 master."""
import copy
import json
import unittest
from unittest.mock import patch

import susy_v103_multipath_g1_frontier_master_audit as audit


class TestV103Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.card = cls.report["consolidated_theory_card"]
        cls.previous = audit.load_bound(audit.V102_PATH, audit.EXPECTED_CORES["v102_master"])
        cls.route = audit.load_bound(audit.V103_PATH, audit.EXPECTED_CORES["v103_route"])

    def test_canonical_report(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_fresh_reconstruction(self):
        audit.validate_report(self.report)

    def test_all_30_historical_records_preserved_exactly(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))
        self.assertEqual(self.card["historical_V102_card_sha256"], audit.canonical_sha(self.previous["consolidated_theory_card"]))

    def test_B103_is_unaccepted_ordinal31(self):
        self.assertEqual(len(self.report["route_matrix"]), 31)
        row = self.report["route_matrix"][-1]
        self.assertEqual((row["route_id"], row["ordinal"]), ("B103", 31))
        self.assertFalse(row["accepted"])
        self.assertFalse(row["same_action_microscopic_completion"])

    def test_zero_accepted_extensions(self):
        self.assertEqual(self.card["accepted_extension_count"], 0)
        self.assertFalse(any(r["accepted"] for r in self.report["route_matrix"]))

    def test_four_frozen_helpers_embedded_exactly(self):
        self.assertEqual(len(audit.HELPER_KEYS), 4)
        for key in audit.HELPER_KEYS:
            self.assertEqual(self.card[key], self.route[key])
            self.assertEqual(self.card["bound_helper_core_hashes"][key], self.route[key]["core_sha256"])
            self.assertEqual(self.route[key]["core_sha256"], audit.canonical_sha(self.route[key]))

    def test_original_rank_torsion_and_two_targets_not_changed(self):
        old = self.previous["consolidated_theory_card"]
        for key in ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds", "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F", "target_O_intersections_by_height"):
            self.assertEqual(self.card[key], old[key])
        self.assertIsNone(self.card["actual_original_MW_free_rank"])
        self.assertFalse(self.card["actual_original_nonzero_section_constructed"])

    def test_cubic_field_scope_and_global_integral_theorem_preserved(self):
        self.assertTrue(self.card["all_original_cubic_sections_excluded"])
        self.assertEqual(self.card["cubic_exclusion_original_field"], "C(X)(T)")
        self.assertFalse(self.card["combined_cubic_exclusion_after_algebraic_constant_extension_claimed"])
        self.assertEqual(self.card["nonzero_linear_pivot_charts_still_open"], [])
        self.assertEqual(self.card["surviving_global_integral_chart"], self.previous["consolidated_theory_card"]["surviving_global_integral_chart"])

    def test_natural_normal_pair_preserved(self):
        self.assertEqual(self.card["preserved_natural_Spin_c_normal_pair"], self.previous["consolidated_theory_card"]["preserved_natural_Spin_c_normal_pair"])

    def test_only_double_pivot_quartic_boundary_closed(self):
        self.assertTrue(self.card["quartic_L_M_zero_boundary_excluded"])
        self.assertFalse(self.card["all_original_quartic_sections_excluded"])
        self.assertEqual(self.card["remaining_original_quartic_charts"], [{"id": "Q1", "conditions": ["t!=0", "L!=0"]}, {"id": "Q2", "conditions": ["t!=0", "L=0", "M!=0"]}])
        self.assertFalse(self.card["all_original_rational_sections_excluded"])

    def test_quartic_original_field_and_repeated_root_conditions_retained(self):
        g = self.card["original_quartic_sections"]
        self.assertTrue(g["rational_leading_normalization"]["t_may_not_be_set_to_one"])
        self.assertTrue(g["remaining_quartic_charts"]["live_charts"][1]["repeated_q_root_retained"])
        self.assertFalse(g["remaining_quartic_charts"]["live_charts"][1]["square_test_alone_solves_all_remaining_equations"])
        self.assertTrue(g["remaining_quartic_charts"]["no_degree_bound_on_rational_functions_of_X_imposed"])

    def test_target_counts_and_constant_pivots_bound_exactly(self):
        self.assertEqual(self.card["target_reduced_equations_and_free_variables_by_height"], {"37": [74, 73], "148": [222, 221]})
        j = self.card["target_section_jet_reduction"]
        self.assertEqual(j["near_height37_reduced_system"]["constant_pivot_for_every_solved_coefficient"], 1296)
        self.assertEqual(j["identity_height148_reduced_system"]["constant_pivot_for_every_solved_coefficient"], 2)
        self.assertFalse(self.card["target_global_tail_systems_solved"])
        self.assertFalse(self.card["actual_target_sections_constructed"])

    def test_target_global_infinity_poles_and_primitivity_not_discarded(self):
        j = self.card["target_section_jet_reduction"]
        self.assertEqual(j["identity_height148_reduced_system"]["all_infinity_pole_multiplicities_retained"], list(range(73)))
        self.assertFalse(j["identity_height148_reduced_system"]["Z0_divided_out"])
        self.assertTrue(j["equivalence_and_local_global_boundary"]["sufficiency_requires_all_tail_equations_and_homogeneous_primitivity"])
        self.assertFalse(j["equivalence_and_local_global_boundary"]["coefficient_count_is_a_no_solution_proof"])

    def test_normal_tensor_obstruction_has_exact_ranks(self):
        self.assertTrue(self.card["independent_normal_neutral_constant_extension_inconsistent"])
        self.assertEqual(self.card["pure_normal_equation_matrix_shape"], [18, 11])
        self.assertEqual(self.card["pure_normal_matrix_and_augmented_ranks"], [10, 11])
        n = self.card["normal_frame_tensor_representations"]
        self.assertEqual([row["required_coefficient_normal_charge"] for row in n["independent_normal_tensor_system"]["two_direct_V93_obstructions"]], ["1", "1"])

    def test_U5_family_rank_not_a_general_SM_or_KK_no_go(self):
        self.assertEqual(self.card["three_family_constant_U5_up_rank_upper_bound"], 2)
        self.assertFalse(self.card["rank_bound_includes_arbitrary_SM_KK_or_nonlocal_reconstruction"])
        f = self.card["normal_frame_tensor_representations"]["three_family_up_Yukawa_obstruction"]
        self.assertTrue(f["normal_generator_commutes_with_the_written_U5_wall_representation"])
        self.assertTrue(f["given_three_family_U5_sector_assumed_not_mixed_with_new_10s"])
        self.assertEqual(f["nonuniversal_witness"]["rank"], 2)

    def test_normal_obstruction_preserves_named_limited_witnesses(self):
        self.assertFalse(self.card["normal_obstruction_retracts_frozen_finite_or_frame_fixed_algebra"])
        self.assertEqual(self.card["preserved_flat_normal_nine_mode_mass_rank"], 9)
        self.assertFalse(self.card["full_normal_covariant_localized_representations_constructed"])
        self.assertFalse(self.card["nonlinear_QK_supersymmetric_vacuum_constructed"])

    def test_four_dimensional_parity_result_not_six_dimensional_cancellation(self):
        self.assertEqual(self.card["ordinary_4D_Spin_times_P_global_anomaly"], "trivial")
        self.assertEqual(self.card["bare_6D_ordinary_Spin_times_P_character_mod16"], 9)
        p = self.card["locked_parity_quantum_boundary"]
        self.assertEqual(p["full_SMW_parity_trace_census"]["SMW_P_odd_moments_0_2_4"][0], 265)
        self.assertFalse(p["full_SMW_parity_trace_census"]["projected_out_modes_can_be_discarded_from_6D_anomaly"])

    def test_ordinary_even_U_rejection_not_full_Gammahat_no_go(self):
        self.assertEqual(self.card["ordinary_even_U_counterterm_character_classes_mod16"], [0, 8])
        self.assertFalse(self.card["ordinary_even_U_refinement_cancels_bare_restricted_parity"])
        self.assertFalse(self.card["full_Gammahat_parity_background_admissibility_proved"])
        p = self.card["locked_parity_quantum_boundary"]
        self.assertFalse(p["ordinary_even_U_WCS_boundary"]["all_generalized_Gammahat_GS_extensions_excluded"])
        self.assertFalse(p["reduced_6D_RP7_eta_character"]["inverse_eta_is_a_constructed_same_action_inflow"])

    def test_global_anomaly_not_declared_explicit_parity_breaking(self):
        self.assertFalse(self.card["global_tHooft_anomaly_proves_explicit_parity_breaking"])
        self.assertFalse(self.card["locked_parity_quantum_boundary"]["physical_scope_and_quantum_interpretation"]["full_anomaly_cancellation_or_nonconservation_claimed"])

    def test_R2_condensate_is_conditional_and_weakens_selectors(self):
        self.assertTrue(self.card["P265_survives_specified_conditional_R2_condensate"])
        self.assertEqual(self.card["specified_conditional_R2_stabilizer_order"], 8)
        self.assertFalse(self.card["conditional_parity_survival_preserves_all_old_R_selectors"])
        self.assertFalse(self.card["R2_condensate_or_new_operators_installed"])
        s = self.card["locked_parity_quantum_boundary"]["R2_condensate_and_surviving_selection"]
        self.assertFalse(s["allowed_operators_are_proved_generated_or_numerically_safe"])

    def test_route_decisions_scopes_and_sources_copied_exactly(self):
        for target, source in (("strict_master_decision", "terminal_decision"), ("supersession_ledger", "supersession_boundary"),
                               ("cross_sector_scope_checks", "cross_sector_scope_checks"), ("gate_ledger", "gate_ledger"),
                               ("next_required_action", "next_required_action"), ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[target], self.route[source])

    def test_all_gates_open_canonical_V21_unchanged(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])

    def test_no_full_theory_or_empirical_promotion(self):
        self.assertFalse(self.report["strict_master_decision"]["same_action_microscopic_parent_accepted"])
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])
        for k in ("experimental_confirmation", "physical_background_category_identified", "full_quantum_anomaly_cancelled", "same_action_spectrum_and_geometry_realized", "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(self.card[k])

    def test_next_obligation_is_F104(self):
        self.assertEqual(self.report["next_required_action"]["id"], "F104_COVARIANT_ACTION_PARITY_INFLOW_AND_REMAINING_SECTION_SYSTEMS")
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)

    def test_current_generator_and_test_pins(self):
        self.assertEqual(self.report["artifact_hashes"]["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(self.report["artifact_hashes"]["test_sha256"], audit.file_sha(audit.TEST_PATH))

    def test_parent_route_helper_source_and_test_mutations_rejected(self):
        original = audit.file_sha
        for name in ("susy_v102_multipath_g1_frontier_master_audit.py", "test_susy_v103_normal_parity_quartic_target_audit.py",
                     "v103_normal_frame_tensor_representation_audit.py", "test_v103_locked_parity_quantum_boundary_audit.py",
                     "v103_original_quartic_section_audit.py", "test_v103_target_section_jet_reduction_audit.py"):
            with patch.object(audit, "file_sha", side_effect=lambda p: "0"*64 if p.name == name else original(p)):
                with self.assertRaises(RuntimeError):
                    audit.build_report()

    def test_resealed_history_and_scientific_scope_mutations_rejected(self):
        for which in ("history", "quartic", "rank", "parity", "normal", "R2", "completion"):
            bad = copy.deepcopy(self.report)
            if which == "history":
                bad["route_matrix"][0]["accepted"] = True
            else:
                key, value = {"quartic": ("all_original_quartic_sections_excluded", True), "rank": ("actual_original_MW_free_rank", 0),
                              "parity": ("global_tHooft_anomaly_proves_explicit_parity_breaking", True), "normal": ("normal_obstruction_retracts_frozen_finite_or_frame_fixed_algebra", True),
                              "R2": ("R2_condensate_or_new_operators_installed", True), "completion": ("full_quantum_anomaly_cancelled", True)}[which]
                bad["consolidated_theory_card"][key] = value
            bad["core_sha256"] = audit.canonical_sha(bad)
            with self.assertRaises(RuntimeError):
                audit.validate_report(bad)

    def test_generated_JSON_and_readable_MD_are_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        text = audit.render_markdown(self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), text)
        for phrase in ("All 30 historical route records are preserved exactly", "18-by-11", "ordinary Spin x P", "does not itself prove explicit parity breaking", "The entire quartic system remains OPEN", "not experimental confirmation"):
            self.assertIn(phrase, text)
        self.assertNotIn("| ---", text)


if __name__ == "__main__":
    unittest.main()
