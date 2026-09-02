import copy
import json
import unittest

import sympy as sp

import susy_v98_multipath_g1_frontier_master_audit as audit


class TestV98Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.card = cls.report["consolidated_theory_card"]
        cls.previous = audit.load_bound(audit.V97_PATH, audit.EXPECTED_CORES["v97_master"])
        cls.route = audit.load_bound(audit.V98_PATH, audit.EXPECTED_CORES["v98_route"])

    def test_canonical_lineage_and_fresh_validation(self):
        self.assertEqual(self.report["input_core_hashes"], audit.EXPECTED_CORES)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        self.assertNotEqual(audit.EXPECTED_CORES["v98_route"], "0"*64)
        audit.validate_report(self.report)

    def test_all_twenty_five_old_routes_are_byte_for_data_unchanged(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(json.dumps(self.report["route_matrix"][:-1], sort_keys=True, separators=(",", ":")),
                         json.dumps(self.previous["route_matrix"], sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))
        self.assertEqual(self.report["lineage"]["parent_route_count"], 25)

    def test_B98_ordinal26_unaccepted(self):
        rows = self.report["route_matrix"]
        self.assertEqual([row["ordinal"] for row in rows], list(range(1, 27)))
        self.assertEqual(rows[-1]["route_id"], "B98")
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])
        self.assertEqual(self.card["accepted_extension_count"], 0)

    def test_every_embedded_helper_core_canonical_and_bound(self):
        self.assertEqual(set(self.card["bound_helper_core_hashes"]), set(audit.HELPER_KEYS))
        for key in audit.HELPER_KEYS:
            self.assertEqual(self.card["bound_helper_core_hashes"][key], self.route[key]["core_sha256"])
            self.assertEqual(self.route[key]["core_sha256"], audit.canonical_sha(self.route[key]))

    def test_literal_geometric_failure_is_not_repaired_by_independent_internal_factor(self):
        row = self.card["geometric_descent"]
        self.assertEqual(row["M_twisted_D_geom_exponent"], 1)
        self.assertFalse(row["unchanged_Gammahat_independent_compensator_can_contain_carrier"])
        self.assertFalse(row["even_normal_power_integer_stack_matches_original_P"])

    def test_changed_spectator_algebra_does_not_promote_full_flavor_or_quantum_action(self):
        row = self.card["geometric_descent"]
        self.assertTrue(row["changed_group_is_original_geometric_group_times_U1"])
        self.assertTrue(row["changed_square_space_group_relations_close"])
        for key in ("full_old_267_hyper_flavor_embedding_constructed", "paired_F_is_independent_full_Sp1",
                    "changed_category_accepted", "algebraic_square_lift_is_full_quantum_Gammahat"):
            self.assertFalse(row[key])
        self.assertIn("Sp267", row["full_flavor_scope"])

    def test_spectator_curvature_and_counterprofile_residual_not_erased(self):
        d, u, v = sp.symbols("d u v")
        row = self.card["geometric_descent"]
        self.assertEqual(sp.expand(sp.sympify(row["new_P_W"])-d*d*(d+u+v)), 0)
        self.assertEqual(sp.expand(sp.sympify(row["extra_flavor_curvature_term"])-d*d*v), 0)
        residual = [sp.sympify(z) for z in self.card["positive_hyper_candidate"]["counterprofile_residual_against_original_P"]]
        self.assertEqual(residual, [-d*d*v/4, -d*d*v/4, d*d*v/2])
        self.assertFalse(row["odd_normal_example_allows_curvature_free_compensator"])
        self.assertIn("w=0", row["canonical_geometric_section"])

    def test_positive_minimum_and_exact_counterprofile_allocation(self):
        row = self.card["positive_hyper_candidate"]
        self.assertEqual(row["minimum_full_hyper_units_in_linewise_C4_ansatz"], 16)
        self.assertFalse(row["minimum_is_universal_over_all_repairs"])
        self.assertFalse(row["full_frozen_nonabelian_flavor_representation_constructed"])
        self.assertIn("tensor-product", row["minimum_domain"])
        expected = {0: [1, 0, 2, 1], 1: [2, 4, 0, 2], 2: [1, 0, 2, 1]}
        for n, vector in expected.items():
            actual = [sum(b["multiplicity"] for b in row["counterprofile_blocks"] if b["D_power"] == n and b["phase"] == m) for m in range(4)]
            self.assertEqual(actual, vector)
        self.assertEqual(sum(b["multiplicity"] for b in row["counterprofile_blocks"]), 16)

    def test_eight_free_chirals_are_new_and_not_borrowed_gap(self):
        row = self.card["positive_hyper_candidate"]
        self.assertEqual(row["constant_N1_chiral_multiplets"], 8)
        charges = [(r["covering_U1_charge"], r["W_charge"], r["multiplicity"]) for r in row["zero_mode_charge_rows"]]
        self.assertEqual(charges, [(0, 1, 1), (0, -1, 1), (2, 1, 2), (-2, -1, 2), (4, 1, 1), (-4, -1, 1)])
        self.assertEqual(row["common_D_W_zero_mode_I6"], "0")
        self.assertFalse(row["mass_lifting_constructed"])
        self.assertFalse(row["old_V97_Dirac_gap_reused"])
        self.assertIn("no transverse flux", row["free_spectrum_assumptions"])

    def test_irreducible_bulk_price_and_only_hypothetical_neutral_replacement(self):
        row = self.card["positive_hyper_candidate"]
        self.assertEqual(row["delta_H_V_T"], [16, 0, 0])
        self.assertEqual(row["delta_H_minus_V_plus_29T"], 16)
        self.assertEqual(sp.sympify(row["irreducible_P2_coefficient"]), -sp.Rational(1, 90))
        P1, P2 = sp.symbols("P1 P2")
        polynomial = sp.sympify(row["common_root_bulk_I8"])
        self.assertEqual(sp.expand(polynomial).coeff(P2), -sp.Rational(1, 90))
        replacement = row["hypothetical_neutral_replacement"]
        self.assertEqual(replacement["delta_H_V_T"], [0, 0, 0])
        self.assertEqual(sp.expand(sp.sympify(replacement["remaining_common_root_delta_I8"])).coeff(P2), 0)
        self.assertEqual(sp.expand(sp.sympify(replacement["remaining_common_root_delta_I8"])).coeff(P1, 2), 0)
        self.assertFalse(replacement["new_gauge_normal_flavor_and_mixed_anomalies_cancel"])
        self.assertFalse(replacement["old_neutral_states_and_projectors_identified"])
        self.assertFalse(replacement["same_action_replacement_adopted"])
        self.assertIn("old vector/tensor/gravity spectrum unchanged", row["additive_only_no_go_scope"])

    def test_flavor_anomalies_and_opposite_chirality_SUSY_cost_retained(self):
        row = self.card["positive_hyper_candidate"]
        self.assertTrue(row["independent_flavor_zero_mode_crosscheck_exact"])
        self.assertTrue(row["generic_flavor_backgrounds_leave_local_terms"])
        self.assertEqual(row["opposite_chirality_block_count"], 8)
        self.assertEqual(row["opposite_chirality_counts"], [4, 4])
        self.assertEqual(row["opposite_chirality_matched_background_I8"], "0")
        self.assertNotEqual(sp.sympify(row["opposite_chirality_new_R_flavor_mismatch"]), 0)
        self.assertFalse(row["opposite_chirality_is_same_hyper_only_N1_completion"])

    def test_product_bordism_and_closed5_equality_not_boundary_glue(self):
        row = self.card["restricted_responses"]
        self.assertEqual(row["ordinary_spin_product_Omega5"], {"common": "0", "local": "0", "common_with_R": "Z2", "local_with_R": "Z2"})
        self.assertTrue(row["integer_P_eta_equals_cup_on_stated_closed5"])
        self.assertTrue(row["closed5_uniqueness_given_full_restricted_curvature"])
        self.assertFalse(row["integer_equality_supplies_quarter_roots"])
        self.assertFalse(row["boundary_trivializations_are_unique"])
        self.assertFalse(row["normal_doublet_nu_R_erased"])

    def test_determinant_root_changes_old_backgrounds(self):
        row = self.card["restricted_responses"]
        self.assertEqual(row["old_CP3_P_over4_period"], "1/4")
        self.assertEqual(row["minimum_determinant_cover_degree"], 2)
        self.assertTrue(row["cover_changes_allowed_bundles"])
        self.assertFalse(row["cover_adopted"])
        self.assertFalse(row["full_Gammahat_category_identified"])

    def test_Spin_c_eta_plus_cup_identity_independently(self):
        c, x, p = sp.symbols("c x p")
        index = lambda z: (z+x/2)**3/6-p*(z+x/2)/24
        expected = sp.expand(index(2*c)-2*index(c)+index(0)+c**3)
        row = self.card["restricted_responses"]
        self.assertEqual(sp.expand(expected-sp.sympify(row["natural_Spin_c_quarter_polynomial"])), 0)
        self.assertEqual(expected, 2*c**3+c**2*x/2)
        self.assertEqual(row["natural_Spin_c_integer_eta_levels"], {"C^2": 1, "C": -2, "1": 1})
        self.assertEqual(row["natural_Spin_c_integral_cup"], "c^3")
        self.assertEqual(row["natural_Spin_c_identity_residual"], "0")
        self.assertTrue(row["normal_square_root_not_needed_for_this_response"])

    def test_natural_Spin_c_no_root_example_and_distinct_half_period(self):
        row = self.card["restricted_responses"]
        example = row["CP2_CP1_no_normal_root_example"]
        self.assertFalse(example["normal_square_root_exists"])
        self.assertEqual(example["three_line_indices"], [6, 1, 0])
        self.assertEqual(example["c_cubed_period"], 3)
        self.assertEqual(example["P_over4_period"], 7)
        old = row["distinct_old_normal_half_period"]
        self.assertEqual(old["old_target_period"], "3/2")
        self.assertFalse(old["old_normal_half_period_removed"])
        self.assertFalse(row["SU2_and_finite_refinements_glued"])

    def test_response_levels_not_particle_multiplicities(self):
        row = self.card["restricted_responses"]
        self.assertFalse(row["response_eta_levels_are_new_particle_multiplicities"])
        self.assertTrue(row["particle_and_response_options_are_distinct"])

    def test_generic_half_alpha_exclusion_and_exact_eliminant_degrees(self):
        row = self.card["original_section"]
        self.assertTrue(row["half_alpha_locus_excluded_over_algebraic_closure_C_X"])
        self.assertEqual(row["half_alpha_resultant_mod101"], 84)
        self.assertEqual(row["eliminant_generic_degrees"], [18, 19])
        self.assertTrue(row["no_linear_pivot_zero_case_omitted"])

    def test_all_reduced_charts_and_original_field_square_conditions_preserved(self):
        row = self.card["original_section"]
        self.assertEqual(row["remaining_unknowns_over_C_X"], ["z", "H"])
        self.assertEqual(row["nonzero_linear_pivot_charts"], [1, 2, 3])
        self.assertTrue(row["nonzero_square_z_required"])
        self.assertTrue(row["exhaustive_chart_reduction"])
        self.assertFalse(row["all_linear_pivots_zero_branch_excluded"])
        self.assertFalse(row["original_field_system_solved"])
        self.assertIn("b^2-4*a*c is a square in C(X), including zero", row["all_linear_pivots_zero_conditions"])

    def test_specialized_unit_ideal_is_not_generic_section_no_go(self):
        row = self.card["original_section"]
        self.assertEqual(row["finite_specialization_unit_basis"], ["1"])
        self.assertFalse(row["finite_unit_ideal_implies_generic_exclusion"])
        X, z = sp.symbols("X z")
        example = (X-1)*z-1
        self.assertEqual(sp.cancel(example.subs(z, 1/(X-1))), 0)
        self.assertEqual(example.subs(X, 1), -1)

    def test_original_rank_torsion_and_two_height_normalizations_preserved(self):
        self.assertEqual(self.card["actual_original_MW_torsion_order"], 1)
        self.assertIsNone(self.card["actual_original_MW_free_rank"])
        self.assertEqual(self.card["actual_original_MW_free_rank_bounds"], [0, 11])
        self.assertEqual(self.card["conditional_unit_charge_section_height_S_F"], [148, 768])
        self.assertEqual(self.card["conditional_doubled_charge_section_height_S_F"], [37, 192])
        self.assertFalse(self.card["actual_original_nonzero_section_constructed"])
        self.assertFalse(self.card["all_original_cubic_sections_excluded"])
        self.assertFalse(self.card["all_original_rational_sections_excluded"])

    def test_decisions_supersession_scope_gates_sources_and_next_copied(self):
        for key, route_key in (("strict_master_decision", "terminal_decision"), ("supersession_ledger", "supersession_boundary"),
                               ("cross_sector_scope_checks", "cross_sector_scope_checks"), ("gate_ledger", "gate_ledger"),
                               ("next_required_action", "next_required_action"), ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[key], self.route[route_key])

    def test_all_eight_gates_open_V21_untouched_and_F99(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        for key in ("full_quantum_anomaly_cancelled", "same_action_spectrum_and_geometry_realized", "soft_spectrum_unification_cosmology_complete"):
            self.assertFalse(self.card[key])

    def assert_rehashed_change_rejected(self, path, value):
        changed = copy.deepcopy(self.report)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        changed["core_sha256"] = audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_old_history_edit_rejected(self):
        self.assert_rehashed_change_rejected(["route_matrix", 0, "name"], "forged")

    def test_rehashed_full_flavor_promotion_rejected(self):
        self.assert_rehashed_change_rejected(["consolidated_theory_card", "geometric_descent", "full_old_267_hyper_flavor_embedding_constructed"], True)

    def test_rehashed_spectator_curvature_erasure_rejected(self):
        self.assert_rehashed_change_rejected(["consolidated_theory_card", "geometric_descent", "extra_flavor_curvature_term"], "0")

    def test_rehashed_old_gap_transfer_rejected(self):
        self.assert_rehashed_change_rejected(["consolidated_theory_card", "positive_hyper_candidate", "old_V97_Dirac_gap_reused"], True)

    def test_rehashed_gravity_anomaly_erasure_rejected(self):
        self.assert_rehashed_change_rejected(["consolidated_theory_card", "positive_hyper_candidate", "delta_H_minus_V_plus_29T"], 0)

    def test_rehashed_Spin_c_response_as_original_Gammahat_rejected(self):
        self.assert_rehashed_change_rejected(["consolidated_theory_card", "restricted_responses", "full_Gammahat_category_identified"], True)

    def test_rehashed_generic_section_exclusion_rejected(self):
        self.assert_rehashed_change_rejected(["consolidated_theory_card", "original_section", "finite_unit_ideal_implies_generic_exclusion"], True)

    def test_readable_report_scopes_and_no_table(self):
        markdown = audit.render_markdown(self.report)
        self.assertNotIn("|---", markdown)
        for phrase in ("All eight SUSY/C8 gates remain OPEN", "No complete theory", "linewise C4", "Sp267",
                       "different Dirac gap is not borrowed", "not all extensions", "Eta coefficients are not new particle multiplicities",
                       "needs no genuine normal square root", "distinct V96 normal target still has period3/2",
                       "nonzero square in C(X)", "not a generic no-section theorem", "q_Sh=q_displayed/2"):
            self.assertIn(phrase, markdown)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
