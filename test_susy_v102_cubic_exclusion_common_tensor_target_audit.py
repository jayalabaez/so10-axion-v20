"""F102 exact cross-sector, evidence-boundary and immutable-input checks."""
import copy
import json
import unittest
from unittest.mock import patch

import susy_v102_cubic_exclusion_common_tensor_target_audit as audit


class TestV102Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.parents = {key: audit.common.load_bound(audit.ROOT/name, core) for key, (name, core) in audit.PARENTS.items()}

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_helpers_reconstruct(self):
        for key, module in zip(audit.KEYS, audit.MODULES):
            self.assertEqual(self.report[key], module.build_certificate())

    def test_all_helpers_share_immutable_parents(self):
        for key in audit.KEYS:
            for parent, (_, core) in audit.PARENTS.items():
                self.assertEqual(self.report[key]["input_core_hashes"][parent], core)

    def test_fresh_source_and_test_hashes(self):
        hashes = self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"], audit.file_sha(audit.TEST_PATH))
        for name, value in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(value, audit.file_sha(audit.ROOT/name))

    def test_all_18_written_tensors_match(self):
        f = self.report["finite_VEV_stabilizer"]["written_action_and_full_VEV_stabilizer"]
        m = self.report["driver_mass_background"]["source_bound_operator_network"]
        allowed = [row for row in m if row["include_in_constant_tensor_system"]]
        self.assertEqual(len(allowed), 18)
        self.assertEqual(sorted(map(audit.tensor_signature, allowed)), sorted(map(audit.tensor_signature, f["written_action_checks"])))

    def test_all_V90_rows_including_forbidden_preserved(self):
        rows = self.report["driver_mass_background"]["source_bound_operator_network"]
        self.assertEqual(len(rows), 22)
        self.assertEqual(sum(not r["include_in_constant_tensor_system"] for r in rows), 4)
        self.assertEqual(sum(r["operator_kind"] == "Kahler" and r["include_in_constant_tensor_system"] for r in rows), 1)

    def test_fixed_constants_and_five_VEVs_not_omitted(self):
        f = self.report["finite_VEV_stabilizer"]["written_action_and_full_VEV_stabilizer"]
        self.assertTrue(f["driver_constants_are_fixed_neutral_numbers"])
        self.assertEqual(f["VEV_order"], list(audit.matter.VEVS))
        rows = self.report["driver_mass_background"]["source_bound_operator_network"]
        self.assertEqual(len([r for r in rows if r["id"].startswith("V90_constant_")]), 3)

    def test_exact_line_system_and_GM_rank(self):
        s = self.report["driver_mass_background"]["common_component_line_system"]
        self.assertEqual((s["number_of_equations"], s["number_of_fields"], s["matrix_rank"], s["augmented_rank"]), (26, 22, 20, 20))
        self.assertEqual((s["rational_solution_dimension"], s["rank_without_GM"]), (2, 19))
        self.assertEqual(set(s["all_equation_residuals"]), {"0"})

    def test_old_H3_obstruction_not_hidden(self):
        h = self.report["driver_mass_background"]["V101_unretuned_H3_obstruction"]
        self.assertEqual(h["B0_degree"], 3)
        self.assertEqual(h["SB_Phi_minus_B0_squared_product_degree_with_SB2"], 8)
        self.assertEqual(h["that_superpotential_term_required_degree"], 2)
        self.assertFalse(h["spurions_or_charged_constants_installed"])

    def test_common_restricted_background_keeps_period(self):
        m = self.report["driver_mass_background"]
        for key in ("CP3_common_tensor_witness_k0", "CP3_common_tensor_witness_k2"):
            row = m[key]
            self.assertEqual(row["P_over4_period"], "3/8")
            self.assertEqual(row["N_D"], ["O(1)", "O(1)"])
            self.assertEqual(row["full_known_cocharacter_endpoint"], [0, 1, 0, 1, 1, 1, 1])
            self.assertTrue(row["all_five_selected_VEV_lines_trivial"])
            self.assertFalse(row["full_same_action_physical_background_proved"])
            self.assertFalse(row["localized_component_line_weights_are_full_representations"])

    def test_optional_legacy_not_silently_installed(self):
        optional = self.report["driver_mass_background"]["legacy_and_forbidden_boundary"]["optional_V70_Majorana"]
        self.assertTrue(optional["k0_witness_passes"])
        self.assertFalse(optional["explicitly_reinstalled_in_V90_operator_ledger"])
        self.assertFalse(optional["adopted_as_new_action_term"])

    def test_actual_finite_group_not_charge_gcd(self):
        f = self.report["finite_VEV_stabilizer"]
        self.assertEqual(f["known_finite_subgroup"]["order"], 64)
        row = f["written_action_and_full_VEV_stabilizer"]
        self.assertEqual((row["stabilizer_order"], row["bosonic_quotient_by_f_order"]), (16, 8))
        self.assertFalse(f["full_stabilizer_boundary"]["full_unbroken_continuous_and_finite_group_classified"])

    def test_locked_parity_is_known_quotient_identity(self):
        row = self.report["finite_VEV_stabilizer"]["known_finite_subgroup"]
        self.assertEqual(row["exact_quotient_identity"], "P265=Rtilde^2 * k^4 * f")
        self.assertFalse(row["P265_is_old_universal_fermion_parity"])
        self.assertFalse(row["epsilonT_relabelled_as_fermion_parity"])

    def test_odd_actual_projected_modes_and_visible_kernel(self):
        f = self.report["finite_VEV_stabilizer"]
        census = f["locked_flavor_parity_and_frozen_projectors"]
        self.assertEqual((census["odd_full_hypers"], census["odd_selected_N1_zero_modes"], census["even_selected_Phi_zero_modes"]), (265, 9, 2))
        chars = f["component_characters_and_selection_rule"]
        self.assertEqual((chars["visible_only_faithful_image_order"], chars["with_nine_extras_faithful_image_order"]), (8, 16))

    def test_quantum_and_cosmology_are_conditional(self):
        row = self.report["finite_VEV_stabilizer"]["component_characters_and_selection_rule"]
        self.assertIn("FULL quantum action", row["conditional_lightest_odd_state_stability"])
        self.assertIn("not the earlier V65", row["extra_sector_identity"])
        for key in ("cosmological_viability_mass_or_abundance_computed", "full_P265_quantum_anomaly_freedom_proved", "stable_particle_prediction_of_an_accepted_theory"):
            self.assertFalse(row[key])

    def test_only_one_proved_frontier_flag_changes(self):
        g = self.report["nonzero_pivot_section_elimination"]
        old = self.parents["v101_route"]["original_section_solvability"]["preserved_frontier"]
        self.assertEqual(g["prior_frontier"], old)
        self.assertEqual(self.report["target_height_pole_atlas"]["preserved_frontier"], old)
        updated = copy.deepcopy(old)
        updated["all_cubic_polynomial_x_sections_excluded"] = True
        self.assertEqual(g["preserved_frontier"], updated)

    def test_original_member_equations_unchanged(self):
        g = self.report["nonzero_pivot_section_elimination"]
        old = self.parents["v101_route"]["original_section_solvability"]
        for key in ("coefficient_payload_sha256", "original_equation_list_sha256"):
            self.assertEqual(g[key], old[key])
        self.assertEqual(self.report["target_height_pole_atlas"]["coefficient_payload_sha256"], g["coefficient_payload_sha256"])

    def test_resultants_necessary_not_sufficient(self):
        row = self.report["nonzero_pivot_section_elimination"]["shared_resultant_necessity"]
        self.assertTrue(row["no_a_ell_mu_or_K_discriminant_division"])
        self.assertTrue(row["all_three_nonzero_ell_charts_and_zero_ell_boundary_retained"])
        self.assertFalse(row["pairwise_resultants_claimed_sufficient_for_common_K_root"])

    def test_exact_newton_and_two_valuation_certificate(self):
        g = self.report["nonzero_pivot_section_elimination"]
        n = g["shared_resultant_newton_certificate"]
        self.assertEqual(n["common_possible_pole_rays"], [[-2, 1], [1, 1]])
        self.assertEqual([r["universal_normalized_term_count"] for r in n["rows"]], [5560, 9500, 21128])
        self.assertTrue(g["two_valuation_generic_exclusion"]["both_valuations_and_coordinate_axes_controlled"])
        self.assertEqual(g["finite_field_unit_ideal"]["Groebner_basis"], ["1"])
        self.assertFalse(g["two_valuation_generic_exclusion"]["generic_exclusion_from_modular_unit_ideal_alone_claimed"])

    def test_combined_exclusion_is_original_field_only(self):
        row = self.report["nonzero_pivot_section_elimination"]["combined_original_polynomial_ansatz_conclusion"]
        self.assertTrue(row["all_cubic_polynomial_x_sections_excluded_over_original_field"])
        self.assertFalse(row["nonzero_original_section_with_polynomial_x_degree_at_most_three_exists"])
        self.assertFalse(row["entire_low_degree_exclusion_over_algebraic_closure_C_X_claimed"])
        self.assertEqual(row["all_three_former_nonzero_linear_pivot_charts_excluded"], [1, 2, 3])

    def test_higher_degree_and_denominators_not_excluded(self):
        g = self.report["nonzero_pivot_section_elimination"]
        row = g["remaining_section_frontier"]
        self.assertEqual(row["nonzero_linear_pivot_charts_still_open"], [])
        self.assertTrue(row["higher_polynomial_degree_or_T_denominator_search_open"])
        self.assertEqual((row["original_free_rank_lower_bound"], row["original_free_rank_upper_bound"], row["original_MW_torsion_order"]), (0, 11, 1))
        self.assertFalse(g["combined_original_polynomial_ansatz_conclusion"]["all_rational_sections_excluded"])

    def test_exact_global_pole_budgets(self):
        rows = self.report["target_height_pole_atlas"]["target_sections"]
        self.assertEqual([(r["height"], r["P_dot_O"]) for r in rows], [(37, 17), (148, 72)])
        self.assertEqual([r["global_degrees_Z_U_V"] for r in rows], [[17, 38, 57], [72, 148, 222]])
        self.assertEqual([r["all_O_intersections_forced_finite_in_T"] for r in rows], [True, False])

    def test_primitivity_is_not_existence_or_two_divisibility(self):
        rows = self.report["target_height_pole_atlas"]["target_sections"]
        self.assertTrue(rows[0]["primitive_modulo_torsion_if_exists"])
        self.assertEqual([r["possible_nontrivial_integer_divisions"] for r in rows], [[], [2]])
        self.assertFalse(rows[1]["divisible_by_two_proved"])
        self.assertFalse(any(r["actual_section_or_threefold_height_constructed"] for r in rows))

    def test_rank_one_target_boundary_not_rank_determination(self):
        row = self.report["target_height_pole_atlas"]["rank_one_target_boundary"]
        self.assertTrue(row["any_nonzero_section_of_height_less_than37_excludes_rank_one_with_either_target"])
        self.assertFalse(row["original_rank_lower_bound_raised"])
        self.assertFalse(row["low_degree_section_is_the_required_target"])

    def test_all_eight_gates_remain_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["bounded_F102_research_step_completed"])
        self.assertFalse(decision["all_F102_obligations_fully_completed"])
        self.assertFalse(decision["theory_complete"])
        self.assertEqual(decision["closed_gates"], [])

    def test_next_task_targets_higher_not_exhausted_cubic_charts(self):
        row = self.report["next_required_action"]
        self.assertEqual(row["id"], audit.NEXT_ID)
        self.assertIn("beyond the exhausted cubic ansatz", row["primary"])
        self.assertIn("normal-frame covariance", row["parallel"])
        self.assertIn("full quantum action", row["parallel"])

    def test_resealed_unsupported_promotion_rejected(self):
        bad = copy.deepcopy(self.report)
        bad["terminal_decision"]["theory_complete"] = True
        bad["core_sha256"] = audit.canonical_sha(bad)
        with self.assertRaises(RuntimeError):
            audit.validate_report(bad)

    def test_crosscheck_rejects_tampered_tensor_or_frontier(self):
        certs = [copy.deepcopy(self.report[key]) for key in audit.KEYS]
        certs[1]["source_bound_operator_network"][0]["factors"] = ["X"]
        with self.assertRaises(RuntimeError):
            audit.crosscheck(self.parents, *certs)
        certs = [copy.deepcopy(self.report[key]) for key in audit.KEYS]
        certs[2]["preserved_frontier"]["all_cubic_polynomial_x_sections_excluded"] = False
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
