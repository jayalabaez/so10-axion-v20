"""F103 cross-sector checks, immutable lineage and explicit nonpromotion tests."""
import copy
import json
import unittest
from unittest.mock import patch

import susy_v103_normal_parity_quartic_target_audit as audit


class TestV103Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.parents = {key: audit.common.load_bound(audit.ROOT/name, core) for key, (name, core) in audit.PARENTS.items()}

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_helpers_reconstruct(self):
        for key, module in zip(audit.KEYS, audit.MODULES):
            self.assertEqual(self.report[key], module.build_certificate())

    def test_shared_immutable_parents(self):
        for key in audit.KEYS:
            for parent, (_, core) in audit.PARENTS.items():
                self.assertEqual(self.report[key]["input_core_hashes"][parent], core)

    def test_fresh_source_and_test_hashes(self):
        hashes = self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"], audit.file_sha(audit.TEST_PATH))
        self.assertEqual(len(hashes), 10)
        for name, value in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(value, audit.file_sha(audit.ROOT/name))

    def test_normal_ranks_and_mass_obstruction(self):
        row = self.report["normal_frame_tensor_representations"]["independent_normal_tensor_system"]
        self.assertEqual((row["number_of_equations"], row["number_of_unknowns"], row["matrix_rank"], row["augmented_rank"]), (18, 11, 10, 11))
        self.assertTrue(row["V93_arbitrary_family_lambda_and_kappa_must_vanish_with_neutral_coefficients"])
        self.assertFalse(row["all_written_constant_tensors_covariant_under_independent_normal"])

    def test_three_family_rank_is_scoped_not_universal(self):
        row = self.report["normal_frame_tensor_representations"]["three_family_up_Yukawa_obstruction"]
        self.assertEqual(row["three_family_maximum_rank"], 2)
        self.assertEqual(row["nonuniversal_witness"]["rank"], 2)
        self.assertFalse(row["full_KK_or_nonlocal_mass_matrix_rank_bounded_by_this_theorem"])

    def test_restricted_witness_preserved_not_promoted(self):
        row = self.report["normal_frame_tensor_representations"]["restricted_witness_and_redesign_boundary"]["positive_restricted_character_witness"]
        self.assertEqual(row["all_18_tensor_residuals"], [0]*18)
        self.assertFalse(row["full_independent_normal_representation_constructed"])
        self.assertFalse(row["full_physical_CP3_background_accepted"])
        self.assertEqual(self.parents["v102_route"]["driver_mass_background"]["CP3_common_tensor_witness_k0"]["P_over4_period"], "3/8")

    def test_normal_obstruction_does_not_retract_local_mass(self):
        row = self.report["normal_frame_tensor_representations"]["source_and_assumption_boundary"]
        self.assertFalse(row["finite_or_frame_fixed_local_mass_rank_calculations_retracted"])
        self.assertFalse(row["no_go_applies_to_every_possible_compactification"])
        self.assertFalse(row["normal_frame_covariance_equivalent_to_anomaly_cancellation"])
        mass = self.report["locked_parity_quantum_boundary"]["reduced_4D_parity_mass_patch"]
        self.assertEqual(mass["rank_for_nonzero_phi"], 9)
        self.assertFalse(mass["quantum_parity_of_full_compactification_proved"])

    def test_full_R_flavor_and_normal_coefficient_lines(self):
        row = self.report["normal_frame_tensor_representations"]["mass_tensor_full_curvature_and_finite_checks"]
        self.assertTrue(row["R_and_all_flavor_curvatures_retained"])
        self.assertEqual(set(row["pure_normal_restriction"].values()), {"x"})
        self.assertEqual(set(row["CP3_both_coefficient_degrees"].values()), {0})
        self.assertFalse(row["coefficient_line_is_a_new_installed_field"])

    def test_all_265_hypers_retained(self):
        row = self.report["locked_parity_quantum_boundary"]["full_SMW_parity_trace_census"]
        self.assertEqual(row["SMW_total_moments_0_2_4"], [267, 6472, 387808])
        self.assertEqual(row["SMW_P_odd_moments_0_2_4"], [265, 6344, 379616])
        self.assertEqual(row["SMW_P_inserted_moments_0_2_4"], [-263, -6216, -371424])
        self.assertEqual((row["selected_odd_zero_modes"], row["odd_hypers_without_selected_constant_zero_modes"]), (9, 256))
        self.assertFalse(row["projected_out_modes_can_be_discarded_from_6D_anomaly"])

    def test_4D_parity_mass_is_not_parent_anomaly_cancellation(self):
        row = self.report["locked_parity_quantum_boundary"]["reduced_4D_parity_mass_patch"]
        self.assertEqual(row["determinant"], "-phi**9")
        self.assertEqual(row["continuous_parent_TrQ_TrQ3"], [36, 864])
        self.assertEqual(row["reduced_quantum_test"]["ordinary_OmegaSpin5_BC2"], "0")
        self.assertFalse(row["continuous_parent_anomaly_erased_by_the_mass"])
        self.assertFalse(row["Phi_zeros_or_defect_matching_completed"])

    def test_6D_eta_generator_and_inverse_not_installed(self):
        row = self.report["locked_parity_quantum_boundary"]["reduced_6D_RP7_eta_character"]
        self.assertEqual(row["ordinary_OmegaSpin7_BC2"], "Z/16")
        self.assertEqual((row["bare_character_class_in_canonical_MM_convention_mod16"], row["necessary_inverse_character_class_mod16"]), (9, 7))
        self.assertEqual(row["bare_character_order"], 16)
        self.assertTrue(row["RP7_with_nontrivial_P_is_a_generator"])
        self.assertFalse(row["inverse_eta_is_a_constructed_same_action_inflow"])
        self.assertFalse(row["full_normal_split_Gammahat_background_admissibility_proved"])

    def test_ordinary_even_U_counterterms_exhausted_only_in_scope(self):
        row = self.report["locked_parity_quantum_boundary"]["ordinary_even_U_WCS_boundary"]
        self.assertEqual(row["ordinary_U_counterterm_character_subgroup_mod16"], [0, 8])
        self.assertEqual(row["bare_character_order_modulo_this_counterterm_subgroup"], 8)
        self.assertEqual(len(row["all_spin_orientation_and_refinement_tests"]), 16)
        self.assertFalse(row["any_ordinary_even_U_degree4_refinement_cancels"])
        self.assertFalse(row["all_generalized_Gammahat_GS_extensions_excluded"])

    def test_anomaly_is_not_explicit_breaking_or_cosmology(self):
        row = self.report["locked_parity_quantum_boundary"]["physical_scope_and_quantum_interpretation"]
        for key in ("global_tHooft_anomaly_is_explicit_parity_breaking", "full_anomaly_cancellation_or_nonconservation_claimed", "nonlinear_vacuum_supersymmetry_soft_spectrum_or_cosmology_constructed", "nine_V93_extra_singlets_are_V65_orphan_quarks", "new_particles_condensates_counterterms_or_domain_adopted"):
            self.assertFalse(row[key])

    def test_conditional_R2_not_a_new_vacuum(self):
        row = self.report["locked_parity_quantum_boundary"]["R2_condensate_and_surviving_selection"]
        self.assertEqual(row["specified_stabilizer_after_order"], 8)
        self.assertTrue(row["P265_survives_this_R2_breaking"])
        self.assertFalse(row["parity_survival_preserves_all_Z4R_proton_and_mu_selectors"])
        self.assertFalse(row["new_order_parameter_or_operator_adopted"])

    def test_original_frontier_not_promoted(self):
        old = self.parents["v102_route"]["nonzero_pivot_section_elimination"]
        g = self.report["original_quartic_sections"]
        a = self.report["target_section_jet_reduction"]
        self.assertEqual(g["preserved_frontier"], old["preserved_frontier"])
        self.assertEqual(a["inherited_frontier"], old["preserved_frontier"])
        self.assertTrue(g["preserved_frontier"]["all_cubic_polynomial_x_sections_excluded"])

    def test_original_member_and_equations_unchanged(self):
        old = self.parents["v102_route"]["nonzero_pivot_section_elimination"]
        g = self.report["original_quartic_sections"]
        for key in ("coefficient_payload_sha256", "original_equation_list_sha256"):
            self.assertEqual(g[key], old[key])
        self.assertEqual(self.report["target_section_jet_reduction"]["coefficient_payload_sha256"], g["coefficient_payload_sha256"])

    def test_quartic_t_is_not_affine_curve_gauge(self):
        row = self.report["original_quartic_sections"]["rational_leading_normalization"]
        self.assertTrue(row["t_may_not_be_set_to_one"])
        self.assertFalse(row["square_root_extension_or_rescaling_of_original_curve"])
        self.assertEqual((row["exact_coordinate_degrees"], row["height_if_exists"]), ([4, 6], 4))

    def test_boundary_determinant_is_nonzero_with_fixed_degrees(self):
        deepest = self.report["original_quartic_sections"]["pivot_boundary_data"]["deepest_zero_pivot_exclusion"]
        self.assertEqual((deepest["X_one_degrees"], deepest["resultant_mod101"]), ([3, 5], 54))
        row = self.report["original_quartic_sections"]["double_pivot_generic_exclusion"]
        self.assertEqual([r["degree_mod101"] for r in row["resultant_rows"]], [28, 33])
        self.assertEqual((row["specialized_fixed_Sylvester_size"], row["specialized_fixed_Sylvester_determinant_mod101"]), (61, 23))
        self.assertTrue(row["generic_L_M_zero_boundary_excluded_over_algebraic_closure_C_X"])
        self.assertTrue(row["no_linear_h_pivot_or_quadratic_discriminant_divided"])

    def test_two_live_quartic_charts_unsolved(self):
        row = self.report["original_quartic_sections"]["remaining_quartic_charts"]
        self.assertEqual([(r["id"], r["conditions"]) for r in row["live_charts"]], [("Q1", ["t!=0", "L!=0"]), ("Q2", ["t!=0", "L=0", "M!=0"])])
        self.assertTrue(row["no_degree_bound_on_rational_functions_of_X_imposed"])
        self.assertFalse(row["entire_quartic_chart_excluded"])
        self.assertFalse(row["actual_rational_candidate_found"])
        self.assertTrue(row["live_charts"][1]["repeated_q_root_retained"])

    def test_target_counts_pivots_and_pole_budgets(self):
        a = self.report["target_section_jet_reduction"]
        rows = [a[k] for k in ("near_height37_reduced_system", "identity_height148_reduced_system")]
        self.assertEqual([(r["height"], r["global_P_dot_O"], r["free_variable_count"], r["remaining_equation_count"], r["constant_pivot_for_every_solved_coefficient"]) for r in rows], [(37, 17, 73, 74, 1296), (148, 72, 221, 222, 2)])
        self.assertFalse(any(r["global_tail_solved"] for r in rows))

    def test_all_infinity_multiplicities_retained(self):
        a = self.report["target_section_jet_reduction"]
        row = a["identity_height148_reduced_system"]
        self.assertEqual(row["all_infinity_pole_multiplicities_retained"], list(range(73)))
        self.assertFalse(row["Z0_divided_out"])
        self.assertEqual(a["identity_target_infinity_partition"]["m72_polynomial_degrees_x_y"], [148, 222])
        self.assertFalse(a["identity_target_infinity_partition"]["a_polynomial_x_coordinate_implies_global_integrality"])

    def test_tail_and_primitivity_not_counts_or_samples(self):
        row = self.report["target_section_jet_reduction"]["equivalence_and_local_global_boundary"]
        self.assertTrue(row["sufficiency_requires_all_tail_equations_and_homogeneous_primitivity"])
        self.assertEqual(len(row["remaining_primitivity_conditions"]), 3)
        for key in ("leading_jet_solution_is_a_global_section", "coefficient_count_is_a_no_solution_proof", "finite_modular_samples_prove_original_field_solvability"):
            self.assertFalse(row[key])

    def test_all_gates_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        row = self.report["terminal_decision"]
        self.assertTrue(row["bounded_F103_research_step_completed"])
        for key in ("all_F103_obligations_fully_completed", "theory_complete", "same_action_microscopic_parent_accepted"):
            self.assertFalse(row[key])
        self.assertEqual(row["closed_gates"], [])

    def test_next_step_is_explicit_not_declarative_cancellation(self):
        row = self.report["next_required_action"]
        self.assertEqual(row["id"], audit.NEXT_ID)
        self.assertIn("covariant action repair", row["primary"])
        self.assertIn("Do not install a formal inverse eta character", row["primary"])
        self.assertIn("Q1 and Q2", row["parallel"])
        self.assertIn("homogeneous primitivity", row["parallel"])

    def test_sources_unique_and_primary(self):
        rows = self.report["primary_sources"]
        self.assertEqual(len(rows), len({r["url"] for r in rows}))
        self.assertTrue(all(r["url"].startswith("https://") and r["use"] for r in rows))

    def test_resealed_theory_promotion_rejected(self):
        bad = copy.deepcopy(self.report)
        bad["terminal_decision"]["theory_complete"] = True
        bad["core_sha256"] = audit.canonical_sha(bad)
        with self.assertRaises(RuntimeError):
            audit.validate_report(bad)

    def test_crosscheck_rejects_mass_scope_and_parity_promotions(self):
        for index, outer, key, value in ((0, "reduced_4D_parity_mass_patch", "quantum_parity_of_full_compactification_proved", True), (0, "ordinary_even_U_WCS_boundary", "any_ordinary_even_U_degree4_refinement_cancels", True), (1, "three_family_up_Yukawa_obstruction", "three_family_maximum_rank", 3)):
            certs = [copy.deepcopy(self.report[k]) for k in audit.KEYS]
            certs[index][outer][key] = value
            with self.assertRaises(RuntimeError):
                audit.crosscheck(self.parents, *certs)

    def test_crosscheck_rejects_point_and_tail_promotions(self):
        for index, outer, key, value in ((2, "remaining_quartic_charts", "entire_quartic_chart_excluded", True), (3, "identity_height148_reduced_system", "global_tail_solved", True), (2, "preserved_frontier", "all_cubic_polynomial_x_sections_excluded", False)):
            certs = [copy.deepcopy(self.report[k]) for k in audit.KEYS]
            certs[index][outer][key] = value
            with self.assertRaises(RuntimeError):
                audit.crosscheck(self.parents, *certs)

    def test_changed_parent_or_source_rejected(self):
        with patch.object(audit.common, "load_bound", side_effect=RuntimeError("changed parent")):
            with self.assertRaises(RuntimeError):
                audit.build_report()
        with patch.object(audit, "file_sha", return_value="0"*64):
            with self.assertRaises(RuntimeError):
                audit.build_report()

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
