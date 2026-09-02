import copy
import json
import unittest

import sympy as sp
import susy_v98_geometric_descent_response_and_section_audit as audit


class TestV98Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_canonical_lineage(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertEqual(self.report["input_core_hashes"], {k: v[1] for k, v in audit.PARENTS.items()})

    def test_all_helpers_reconstruct(self):
        for key, module in zip(audit.KEYS, audit.MODULES):
            self.assertEqual(self.report[key], module.build_certificate())

    def test_source_and_test_pins(self):
        hashes = self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"], audit.file_sha(audit.TEST_PATH))
        for key, value in hashes.items():
            if key.endswith(".py"):
                self.assertEqual(value, audit.file_sha(audit.ROOT/key))

    def test_literal_geometric_identity_obstructs_independent_compensation(self):
        row = self.report["gammahat_compensator"]["unchanged_geometric_kernel_obstruction"]
        self.assertTrue(row["D_geom_is_literal_identity_before_internal_quotient"])
        self.assertEqual(row["M_twisted_D_geom_exponent_for_both"], 1)
        self.assertFalse(row["unchanged_geometric_Gammahat_with_independent_F_can_contain_the_M_twisted_carrier"])

    def test_even_normal_powers_do_not_reconstruct_odd_target(self):
        row = self.report["gammahat_compensator"]["minimal_even_normal_power_alternatives"]
        self.assertEqual(row["target_d_squared_u_coefficient"], 1)
        self.assertFalse(row["integer_even_power_carrier_stack_matches_frozen_P"])

    def test_new_spectator_category_is_explicit_not_adopted(self):
        row = self.report["gammahat_compensator"]["explicit_changed_spectator_category"]
        self.assertTrue(row["abstract_new_group_is_original_geometric_group_times_one_U1"])
        self.assertFalse(row["natural_map_c_to_c_comma_one_descends_through_original_K"])
        self.assertFalse(row["new_category_is_accepted_same_action_parent"])

    def test_full_flavor_curvature_matches_between_independent_helpers(self):
        check = self.report["cross_sector_scope_checks"]
        d, v = sp.symbols("d v")
        self.assertEqual(sp.expand(sp.sympify(check["spectator_P_W"])-sp.sympify(check["original_P"])), d*d*v)
        self.assertEqual([sp.sympify(value) for value in check["counterprofile_residual_after_retaining_flavor_curvature"]],
                         [-d*d*v/4, -d*d*v/4, d*d*v/2])

    def test_global_normal_half_root_counterexample(self):
        row = self.report["gammahat_compensator"]["retained_curvature_and_global_normal_boundary"]["odd_normal_example"]
        self.assertFalse(row["normal_M_square_root_exists"])
        self.assertFalse(row["curvature_free_compensator_exists"])
        self.assertFalse(row["this_is_a_full_compact_orbifold_or_quantum_anomaly_calculation"])

    def test_positive_character_minimum_is_ansatz_bounded(self):
        row = self.report["transport_physical_realization"]["positive_hyper_character_realization"]
        self.assertEqual(row["minimum_within_this_linewise_C4_character_ansatz"], 16)
        self.assertFalse(row["minimum_is_claimed_over_all_possible_physical_repairs"])
        self.assertEqual({v["orientation"] for v in row["realizations"]}, {1, -1})

    def test_positive_hyper_spectrum_not_old_gap(self):
        row = self.report["transport_physical_realization"]["positive_hyper_constant_spectrum"]
        self.assertEqual(row["N1_chiral_multiplet_count"], 8)
        self.assertEqual(row["vectorlike_pairs_by_D_magnitude"], {"0": 1, "1": 2, "2": 1})
        self.assertFalse(row["V97_Dirac_gap_applied_to_this_carrier"])

    def test_bulk_gravity_and_hypothetical_replacement_not_hidden(self):
        row = self.report["transport_physical_realization"]["positive_hyper_bulk_and_flavor_anomalies"]
        self.assertEqual(row["delta_H_minus_V_plus_29T"], 16)
        self.assertEqual(row["irreducible_P2_coefficient"], "-1/90")
        self.assertFalse(row["ordinary_GS_quadratic_four_form_factorization_can_cancel_this_P2_term"])
        replacement = row["hypothetical_neutral_replacement"]
        self.assertTrue(replacement["irreducible_gravity_rank_cancels_under_this_assumption"])
        self.assertFalse(replacement["new_gauge_normal_flavor_and_mixed_anomalies_cancel"])
        self.assertFalse(replacement["same_action_replacement_adopted"])

    def test_opposite_chirality_option_is_not_hyper_only_SUSY(self):
        row = self.report["transport_physical_realization"]["opposite_chirality_realization"]
        self.assertEqual(row["common_background_bulk_I8"], "0")
        self.assertFalse(row["same_6D_N1_hyper_only_completion_exists"])
        self.assertFalse(row["all_other_SUSY_completions_excluded"])

    def test_continuous_bordism_scope(self):
        tables = self.report["common_response_bordism"]["ordinary_spin_product_bordism"]
        self.assertEqual([tables[k]["Omega5"] for k in ("local", "common", "local_with_R", "common_with_R")], ["0", "0", "Z2", "Z2"])
        self.assertFalse(tables["common"]["full_Gammahat_or_finite_symmetry_category_computed"])

    def test_integer_eta_cup_equality_is_not_a_quarter_root(self):
        row = self.report["common_response_bordism"]["P_eta_cup_comparison"]
        self.assertTrue(row["equal_on_all_closed_spin5_of_local_and_common_product_categories"])
        self.assertFalse(row["equality_provides_canonical_quarter_roots"])

    def test_quantized_Spin_c_quarter_after_gauge_cover(self):
        row = self.report["common_response_bordism"]["natural_Spin_c_determinant_root_response"]
        self.assertEqual(row["exact_identity_difference"], "0")
        self.assertTrue(row["normal_square_root_not_needed_for_this_response"])
        self.assertEqual(row["CP2_times_CP1_example"]["three_line_indices"], [6, 1, 0])
        self.assertEqual(row["CP2_times_CP1_example"]["P_over4_period"], 7)
        self.assertFalse(row["changed_determinant_cover_adopted"])

    def test_different_normal_half_period_and_R_sign_retained(self):
        r = self.report["common_response_bordism"]
        self.assertEqual(r["natural_Spin_c_determinant_root_response"]["distinct_V96_normal_repair_half_period"]["old_target_period"], "3/2")
        self.assertEqual(r["SU2_flat_refinement"]["V97_added_normal_doublet_phase_on_generator"], "-1")
        self.assertFalse(self.report["cross_sector_scope_checks"]["new_response_removes_distinct_V96_normal_half_period"])

    def test_generic_half_alpha_exclusion(self):
        row = self.report["original_square_section"]["half_alpha_generic_exclusion"]
        self.assertEqual(row["specialized_degrees"], [18, 19])
        self.assertEqual(row["resultant_mod_prime"], 84)
        self.assertTrue(row["excluded_over_algebraic_closure_C_X"])
        self.assertTrue(row["no_division_by_A_and_no_A_zero_branch_omitted"])

    def test_all_two_variable_charts_and_square_conditions_retained(self):
        row = self.report["original_square_section"]["square_aware_two_variable_reduction"]
        self.assertEqual(row["unknowns_after_elimination"], ["z", "H"])
        self.assertEqual(row["nonzero_ell_branches"]["pivot_cases"], [1, 2, 3])
        self.assertTrue(row["nonzero_ell_branches"]["z_nonzero_square_in_C_X_required"])
        self.assertFalse(row["all_ell_zero_branch"]["branch_excluded"])
        self.assertFalse(row["system_solved_over_C_X"])

    def test_finite_unit_ideal_not_promoted_and_rank_unchanged(self):
        g = self.report["original_square_section"]
        self.assertEqual(g["full_system_finite_specialization"]["basis"], ["1"])
        self.assertFalse(g["full_system_finite_specialization"]["generic_C_X_exclusion_follows_from_this_unit_ideal"])
        self.assertEqual([g["preserved_frontier"]["original_free_rank_lower_bound"], g["preserved_frontier"]["original_free_rank_upper_bound"]], [0, 11])

    def test_gate_ledger_and_next_obligation(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"], [])
        self.assertFalse(self.report["terminal_decision"]["theory_complete"])
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)

    def test_resealed_scope_tamper_rejected(self):
        report = copy.deepcopy(self.report)
        report["terminal_decision"]["theory_complete"] = True
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_generated_json_and_markdown_are_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
