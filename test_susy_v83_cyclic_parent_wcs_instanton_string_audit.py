import copy
import json
import unittest

import susy_v83_cyclic_parent_wcs_instanton_string_audit as v83


class TestV83CyclicParentWCSInstantonStringAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v83.build_report()

    def test_report_validates_and_is_canonical(self):
        v83.validate_report(self.report)
        self.assertEqual(v83.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        mapping = {
            "v70_route": "V70_route_core",
            "v71_route": "V71_route_core",
            "v77_route": "V77_route_core",
            "v78_route": "V78_route_core",
            "v79_route": "V79_route_core",
            "v81_route": "V81_route_core",
            "v82_route": "V82_route_core",
            "v82_master": "V82_master_core",
        }
        for key, report_key in mapping.items():
            self.assertEqual(self.report["lineage"][report_key], v83.EXPECTED_CORES[key])

    def test_charged_hyper_root_completes_cyclic_fourth_power(self):
        audit = self.report["smooth_bulk_cyclic_parent_audit"]
        roots = audit["rotation_roots"]
        self.assertEqual(roots["charged_hyper_m_values"], [3, 0, 1])
        self.assertEqual(roots["A3_scalar_exponents_mod8"], [7, 1, 3, 1, 7, 5])
        self.assertEqual(roots["A3_hyperino_exponents_mod8"], [1, 7, 5, 7, 1, 3])
        self.assertEqual(roots["A_3_fourth_power"], "-I_6")
        self.assertEqual(roots["combined_rotation_fourth_power_mod2"], [1, 1, 1, 1, 1])
        self.assertTrue(roots["combined_rotation_square_is_noncentral"])
        self.assertEqual(roots["combined_rotation_has_order_in_quotient"], 4)
        reconstruction = roots["V70_superfield_projector_reconstruction"]
        self.assertTrue(reconstruction["all_rows_match_z00_and_z11"])
        self.assertEqual(
            [(row["m"], row["R_times_flavor_Phi_plus_exponent_mod4"], row["full_hyper_constraint_Phi_minus_exponent_mod4"]) for row in reconstruction["rows"]],
            [(3, 3, 0), (0, 0, 3), (1, 1, 2)],
        )

    def test_smooth_bulk_parities_descend_but_kernel_is_not_unique(self):
        audit = self.report["smooth_bulk_cyclic_parent_audit"]
        self.assertTrue(audit["smooth_bulk_representation_descent"]["every_displayed_row_annihilates_Kdiag"])
        self.assertEqual(
            audit["bulk_kernel_nonuniqueness"]["annihilator_subspace_mod2"],
            [[0, 0, 0, 0, 0], [0, 1, 0, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1]],
        )
        self.assertEqual(audit["bulk_kernel_nonuniqueness"]["subgroups_containing_rotation_fourth_power"], 2)
        self.assertFalse(audit["constructed_object"]["full_HGamma_orbibundle"])
        projection = audit["constructed_object"]["cycle_data_projection_to_reduced_H78"]
        self.assertEqual(projection["projected_Spin11_bundle"], "F_E,qhat=R^3+4(L_r)_R")
        self.assertEqual(projection["V82_graph"], "jq: F_E=R^3+4(L_r)_R")
        self.assertEqual(projection["V82_order"], 4)
        self.assertTrue(projection["recorded_data_match_jq_q"])
        self.assertFalse(audit["constructed_object"]["functorial_HGamma_to_H78_forgetful_map_constructed"])

    def test_square_space_group_translation_cocycle_remains_unrepaired(self):
        gamma = self.report["smooth_bulk_cyclic_parent_audit"]["square_space_group_relation_cocycle"]
        self.assertEqual(
            gamma["choice_U_equals_V_equals_what_relation_defects"],
            {"A4": "k_all", "UVUinvVinv": "1", "AUAinvVinv": "1", "AVAinvU": "z_11"},
        )
        self.assertFalse(gamma["flipping_one_translation_sign_removes_all_defects"])
        self.assertFalse(gamma["z11_is_in_minimal_diagonal_kernel"])
        self.assertFalse(gamma["current_b_is_in_2U"])
        self.assertFalse(gamma["SO11_global_form_route_passes_quantization"])
        self.assertFalse(gamma["repair_constructed"])

    def test_regulated_bare_character_is_exactly_typed_but_not_evaluated(self):
        bare = self.report["regulated_bare_anomaly_contract"]
        self.assertEqual(bare["current_smooth_spectrum_substitution"]["complex_half_hyper_dimension"], 598)
        self.assertEqual(bare["current_smooth_spectrum_substitution"]["twice_H_check"], 598)
        self.assertEqual(bare["lattice_signature_term"]["signature"], 0)
        self.assertEqual(bare["exact_target"], "Z_bare(Q4)=exp(pi i xi_Rprime(Q4))")
        self.assertFalse(bare["numeric_xi_Rprime_on_Q4_evaluated"])
        self.assertEqual(bare["bare_phase_value"], "OPEN")
        self.assertEqual(bare["V81_ordinary_complex_spin_half_shadow"]["value"], "-3/4")
        self.assertFalse(bare["V81_ordinary_complex_spin_half_shadow"]["is_physical_bare_phase"])
        self.assertFalse(bare["naive_tensoring_first_terms_by_complex_2R_is_allowed"])

    def test_Q4_torsion_linking_form_is_nonsingular(self):
        audit = self.report["Q4_linking_and_reference_WCS_audit"]
        linking = audit["linking_form"]
        self.assertEqual(linking["matrix_mod1"], [["1/2", "1/4"], ["1/4", "0"]])
        self.assertEqual(linking["determinant_mod4"], 3)
        self.assertTrue(linking["nonsingular"])
        self.assertEqual(linking["g_coordinates_mod4"], [1, 2])
        self.assertEqual(linking["L_g_g"], "1/2")

    def test_even_U_reference_Gauss_sum_and_shadow(self):
        ref = self.report["Q4_linking_and_reference_WCS_audit"]["even_U_reference_quadratic_refinement"]
        self.assertEqual(ref["Gauss_phase_counts_exponent_0_1_2_3"], [88, 48, 72, 48])
        self.assertEqual(ref["Gauss_sum_numerator"], {"real": 16, "imaginary": 0})
        self.assertEqual(ref["normalized_Gauss_sum"], "1")
        self.assertEqual((ref["q0_qhat_exponent_mod4"], ref["q0_basepoint_exponent_mod4"]), (2, 2))
        self.assertEqual((ref["reference_qhat_phase"], ref["reference_basepoint_phase"]), ("-1", "-1"))

    def test_reference_shadow_is_not_a_physical_phase(self):
        audit = self.report["Q4_linking_and_reference_WCS_audit"]
        ambiguity = audit["refinement_nonselection_theorem"]
        self.assertEqual(ambiguity["characters_enumerated"], 256)
        self.assertEqual(ambiguity["raw_distinct_pairs"], 8)
        self.assertEqual(ambiguity["raw_multiplicity_each"], 32)
        self.assertEqual(ambiguity["Arf_normalized_distinct_pairs"], 8)
        normalized = {
            (row["qhat_exponent_mod4"], row["base_exponent_mod4"]): row["multiplicity"]
            for row in ambiguity["Arf_normalized_algebraic_pairs"]
        }
        self.assertEqual(
            normalized,
            {(0, 0): 56, (0, 2): 32, (1, 1): 16, (1, 3): 32, (2, 0): 32, (2, 2): 40, (3, 1): 32, (3, 3): 16},
        )
        self.assertEqual(ambiguity["ratio_exponents_mod4"], [0, 2])
        self.assertFalse(ambiguity["primary_Y_and_linking_select_physical_phase"])
        self.assertFalse(ambiguity["all_algebraic_refinements_are_admissible_for_one_fixed_physical_WCS_theory"])
        self.assertFalse(audit["scope"]["physical_WCS_phase_evaluated"])
        total = audit["total_anomaly_character_constraint"]
        self.assertEqual(total["allowed_total_character_values"], ["1", "i", "-1", "-i"])
        self.assertEqual(total["current_total_character_exponent"], "UNKNOWN")
        self.assertFalse(total["bare_times_WCS_identity_proved"])

    def test_delta_is_localized_to_h0_hidden_extension_but_open(self):
        audit = self.report["relative_delta_hidden_extension_audit"]
        self.assertTrue(audit["classes"]["delta_equals_two_epsilon"])
        self.assertTrue(audit["classes"]["two_delta_zero"])
        self.assertEqual(audit["classes"]["delta_exact_order"], "OPEN_ZERO_OR_ORDER2")
        self.assertEqual(audit["ordinary_complex_eta"]["half_vector_phase_counts"], [7, 2, 0, 2])
        self.assertEqual(audit["ordinary_complex_eta"]["epsilon_vector_rho"], "1/2")
        self.assertEqual(audit["ordinary_complex_eta"]["delta_vector_rho_integer"], "1")
        self.assertEqual(audit["ordinary_complex_eta"]["delta_complex_rho_mod1"], "0")
        self.assertEqual(audit["Adams_diagnosis"]["candidate"], "h0*p")
        self.assertFalse(audit["degree_eight_obstruction"]["candidate_half_eta_is_bordism_character"])

    def test_action_matches_rank_one_4SO11_sector(self):
        sector = self.report["instanton_string_and_compact_source_audit"]["action_derived_sector"]
        self.assertEqual(sector["rank_one_tensor_branch_label"], "4 SO(11)")
        self.assertEqual(sector["b_Spin11"], [2, -1])
        self.assertEqual(sector["b_squared"], -4)
        self.assertEqual(sector["a_KSV_dot_b"], -2)
        self.assertEqual(sector["vector_hypers"], 3)
        self.assertEqual(sector["spinor_hypers"], 0)
        self.assertEqual(sector["flavor_group"], "Sp(3)")
        self.assertFalse(sector["whole_supergravity_action_identified_with_decoupled_rank_one_SCFT"])

    def test_instanton_string_central_charges_and_current(self):
        ws = self.report["instanton_string_and_compact_source_audit"]["known_local_0_4_worldsheet"]
        self.assertEqual((ws["one_string_full_cL"], ws["one_string_full_cR"]), (42, 54))
        self.assertEqual((ws["one_string_interacting_cL"], ws["one_string_interacting_cR"]), (38, 48))
        self.assertEqual(ws["reduced_instanton_moduli_quaternionic_dimension"], 8)
        self.assertEqual(ws["Sp3_Sugawara_c"], "21/5")
        self.assertEqual(ws["six_dimensional_SO11_elliptic_genus_level"], -4)
        self.assertFalse(ws["orbifold_HGamma_descent_constructed"])

    def test_instanton_exception_prevents_KSV_misuse(self):
        scope = self.report["instanton_string_and_compact_source_audit"]["physical_orientation_and_KSV_scope"]
        self.assertEqual(scope["V70_j_dot_Q"], "3/2")
        self.assertEqual(scope["V82_J_dot_Q"], 1)
        self.assertEqual(scope["Q_dot_b"], -4)
        self.assertFalse(scope["KSV_nondegenerate_formula_applicable_to_Q_equals_b"])
        self.assertFalse(scope["formal_values_are_physical_worldsheet_data"])

    def test_compact_T2xS4_source_incidence_is_exact_and_scoped(self):
        inc = self.report["instanton_string_and_compact_source_audit"]["compact_six_dimensional_source_incidence"]
        self.assertEqual(inc["Y_vector"], [-2, 1])
        self.assertTrue(inc["Y_equals_minus_b_u"])
        self.assertEqual(inc["Q_Sigma"], [2, -1])
        self.assertEqual(inc["source_equation_residual"], [0, 0])
        self.assertTrue(inc["compact_cohomological_incidence_constructed"])
        self.assertFalse(inc["on_shell_half_BPS_compactification_constructed"])
        self.assertFalse(inc["differential_WCS_worldsheet_gluing_constructed"])

    def test_instanton_tower_cannot_realize_Q4_residues(self):
        no_go = self.report["instanton_string_and_compact_source_audit"]["instanton_tower_Q4_residue_no_go"]
        self.assertEqual(no_go["residues_m_0_to_3"], [[0, 0], [2, 3], [0, 2], [2, 1]])
        self.assertTrue(no_go["first_coordinate_always_even"])
        self.assertFalse(no_go["pure_instanton_stack_reaches_either_target"])
        self.assertFalse(no_go["other_lattice_string_or_bound_state_excluded"])

    def test_infinite_integral_lifts_defeat_unique_selection(self):
        audit = self.report["infinite_charge_lift_nonselection_audit"]
        self.assertEqual(len(audit["exact_samples_t_0_to_4"]), 10)
        self.assertTrue(all(row["conditional_screen_pass"] for row in audit["exact_samples_t_0_to_4"]))
        self.assertTrue(audit["theorem"]["infinitely_many_distinct_integral_lifts"])
        self.assertFalse(audit["theorem"]["topology_positivity_and_KSV_select_unique_lift"])
        self.assertFalse(audit["theorem"]["existence_of_an_actual_string_for_each_formal_lift_proved"])
        self.assertTrue(audit["theorem"]["all_t_symbolic_proof"]["covers_every_integer_t_at_least_zero"])
        self.assertEqual(
            audit["theorem"]["all_t_symbolic_proof"]["qhat_Sugawara_bound"],
            "55q/(q+9)<=11q/2<6q^2+36q+2=cL",
        )

    def test_terminal_decision_is_fail_closed(self):
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["smooth_bulk_cyclic_C4_lift_constructed"])
        self.assertTrue(decision["local_4SO11_instanton_worldsheet_constructed"])
        self.assertTrue(decision["compact6_cohomological_source_incidence_constructed"])
        self.assertFalse(decision["full_HGamma_parent_lift_constructed"])
        self.assertFalse(decision["physical_WCS_phase_evaluated"])
        self.assertFalse(decision["physical_bare_phase_evaluated"])
        self.assertFalse(decision["compact6_on_shell_half_BPS_solution_constructed"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])

    def test_acceptance_ledgers_are_consistent_and_empty(self):
        accepted = [row["id"] for row in self.report["candidate_matrix"] if row["accepted"]]
        self.assertEqual(self.report["candidate_adjudication"]["accepted_ids"], accepted)
        self.assertEqual(accepted, [])
        self.assertFalse(self.report["terminal_decision"]["selected_candidate_accepted"])

    def test_validator_rejects_promoted_reference_phase(self):
        mutated = copy.deepcopy(self.report)
        mutated["Q4_linking_and_reference_WCS_audit"]["scope"]["physical_WCS_phase_evaluated"] = True
        mutated["terminal_decision"]["physical_WCS_phase_evaluated"] = True
        mutated["core_sha256"] = v83.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "reference WCS shadow|promoted"):
            v83.validate_report(mutated)

    def test_validator_rejects_promoted_candidate(self):
        mutated = copy.deepcopy(self.report)
        mutated["candidate_matrix"][0]["accepted"] = True
        mutated["candidate_adjudication"]["accepted_ids"] = [mutated["candidate_matrix"][0]["id"]]
        mutated["terminal_decision"]["selected_candidate_accepted"] = True
        mutated["core_sha256"] = v83.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "acceptance|unaccepted"):
            v83.validate_report(mutated)

    def test_validator_rejects_corrupted_exact_cycle_and_source_values(self):
        mutations = [
            (
                lambda value: value["smooth_bulk_cyclic_parent_audit"]["rotation_roots"].__setitem__("A_3_fourth_power", "+I_6"),
                "fourth power",
            ),
            (
                lambda value: value["smooth_bulk_cyclic_parent_audit"]["rotation_roots"].__setitem__("combined_rotation_has_order_in_quotient", 2),
                "quotient order",
            ),
            (
                lambda value: value["Q4_linking_and_reference_WCS_audit"]["even_U_reference_quadratic_refinement"].__setitem__("reference_basepoint_phase", "+1"),
                "reference WCS shadow",
            ),
            (
                lambda value: value["instanton_string_and_compact_source_audit"]["compact_six_dimensional_source_incidence"].__setitem__("p1_E", "999u"),
                "characteristic data",
            ),
            (
                lambda value: value["infinite_charge_lift_nonselection_audit"]["theorem"].__setitem__("all_have_positive_V70_tension", False),
                "theorem flags",
            ),
        ]
        for mutate, message in mutations:
            with self.subTest(message=message):
                value = copy.deepcopy(self.report)
                mutate(value)
                value["core_sha256"] = v83.canonical_sha(value)
                with self.assertRaisesRegex(RuntimeError, message):
                    v83.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(v83.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(v83.OUT_MD.read_text(encoding="utf-8"), v83.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
