import copy
import json
import unittest

import sympy as sp
import susy_v99_multipath_g1_frontier_master_audit as audit


class TestV99Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.card = cls.report["consolidated_theory_card"]
        cls.previous = audit.load_bound(audit.V98_PATH, audit.EXPECTED_CORES["v98_master"])
        cls.route = audit.load_bound(audit.V99_PATH, audit.EXPECTED_CORES["v99_route"])

    def test_canonical_fresh_validation(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))
        audit.validate_report(self.report)

    def test_every_historical_route_unchanged(self):
        self.assertEqual(self.report["route_matrix"][:-1], self.previous["route_matrix"])
        self.assertEqual(json.dumps(self.report["route_matrix"][:-1], sort_keys=True, separators=(",", ":")),
                         json.dumps(self.previous["route_matrix"], sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"], audit.canonical_sha(self.previous["route_matrix"]))

    def test_B99_ordinal27_unaccepted(self):
        rows = self.report["route_matrix"]
        self.assertEqual([r["ordinal"] for r in rows], list(range(1, 28)))
        self.assertEqual(rows[-1]["route_id"], "B99")
        self.assertFalse(rows[-1]["accepted"])
        self.assertEqual(self.card["accepted_extension_count"], 0)

    def test_helper_cores_bound_canonically(self):
        for key in audit.HELPER_KEYS:
            self.assertEqual(self.card["bound_helper_core_hashes"][key], self.route[key]["core_sha256"])
            self.assertEqual(self.route[key]["core_sha256"], audit.canonical_sha(self.route[key]))

    def test_frozen_root_rejected_changed_extension_not_adopted(self):
        row = self.card["determinant_root"]
        self.assertEqual(row["D_holonomies_A_U_V"], ["1", "-1", "-1"])
        self.assertFalse(row["frozen_equivariant_root_exists"])
        self.assertFalse(row["changed_central_extension"]["extension_installed_in_frozen_theory"])
        self.assertFalse(row["bare_eta_KT_failure_repaired"])

    def test_root_sign_scope_not_full_finite_bordism(self):
        row = self.card["determinant_root"]
        self.assertEqual(row["root_choice_relative_phases"], ["-1", "-1"])
        self.assertIn("not a flat finite-C8-only", row["root_sign_scope"])
        self.assertFalse(row["specific_response_descends_after_forgetting_root"])
        self.assertFalse(row["full_relative_action_constructed"])
        self.assertFalse(row["quantized_chosen_cover_response"]["quantization_on_its_chosen_root_category_retracted"])

    def test_minimal_replacement_analytic_and_enumerated(self):
        row = self.card["spectator_replacement"]
        self.assertEqual(row["minimal_actual_removal_vectors_checked"], 2956)
        self.assertEqual(row["minimal_rational_survivors"], [])
        self.assertEqual(row["moment_equation"], "108*B-3456*A-A^2=0")
        self.assertEqual(len(row["analytic_proof"]), 5)

    def test_actual_slots_remove_no_constant_modes(self):
        row = self.card["spectator_replacement"]["actual_slots"]
        self.assertEqual(row["selected_six_dimensional_hypers"], 16)
        self.assertEqual(row["source_four_orbit_copies"], 36)
        self.assertEqual(row["removed_constant_N1_chiral_modes"], 0)
        self.assertFalse(row["slot_selection_is_an_accepted_replacement"])

    def test_bounded_regular_extensions_rejected_with_scope(self):
        row = self.card["spectator_replacement"]["bounded_twenty_and_twenty_four_extensions"]
        self.assertEqual(len(row["records"]), 9)
        self.assertEqual((row["twenty_hyper_rational_candidates"], row["twenty_four_hyper_rational_candidates"]), (0, 1))
        self.assertTrue(row["sole_rational_scout_rejected_by_frozen_quotient_quantization"])
        self.assertTrue(row["sole_rational_scout_rejected_by_actual_q0_projector_divisibility"])
        self.assertFalse(row["all_larger_regular_additions_or_other_carriers_excluded"])

    def test_full_independent_flavor_and_modes_not_erased(self):
        row = self.card["spectator_replacement"]["full_independent_flavor_and_spectrum"]
        self.assertEqual(row["new_constant_modes_added"], 8)
        self.assertEqual(row["conditional_total_old_plus_new_N1_chiral_modes"], 19)
        self.assertFalse(row["independent_flavor_anomaly_delta_vanishes"])
        self.assertFalse(row["V97_Dirac_gap_reused"])

    def test_global_flavor_anomaly_scope(self):
        row = self.card["spectator_replacement"]["flavor_GS_and_representation_scope"]
        self.assertIn("not by itself a quantum inconsistency", row["global_flavor_vs_gauge_scope"])
        self.assertFalse(row["full_old_Sp267_compatibility"]["proper_sixteen_hyper_subrepresentation_of_unchanged_fundamental_exists"])

    def test_normal_exact_order_and_pair_response(self):
        row = self.card["normal_pair"]
        self.assertEqual((row["obstruction_order"], row["minimum_positive_quantized_stack"]), (2, 2))
        pair = row["common_reflected_pair"]
        self.assertEqual(pair["integer_eta_levels"], {"N": 1, "1": -15})
        self.assertTrue(pair["quantized_on_all_stated_common_closed5_backgrounds"])
        self.assertFalse(row["normal_pair_is_an_independent_local_repair"])

    def test_shared_normal_vs_independent_endpoint_sign(self):
        pair = self.card["normal_pair"]["common_reflected_pair"]
        self.assertEqual(pair["obstruction_character_product_on_shared_closed6"], "+1")
        self.assertEqual(pair["independent_endpoint_obstruction_phase"], "-1")
        self.assertFalse(pair["actual_orbifold_relative_gluing_constructed"])

    def test_conditional_trace_original_equations_and_squares(self):
        row = self.card["original_section"]
        self.assertEqual(row["coefficient_payload_sha256"], self.previous["consolidated_theory_card"]["original_section"]["coefficient_payload_sha256"])
        self.assertEqual(row["original_equation_list_sha256"], self.previous["consolidated_theory_card"]["original_section"]["original_equation_list_sha256"])
        chart = row["exceptional_chart"]
        self.assertEqual(chart["equation_count"], 6)
        self.assertFalse(chart["candidate_z_H_found"])
        self.assertFalse(chart["K_discriminant_square_required_for_the_trace_point"])
        self.assertEqual(chart["nonzero_ell_charts_from_V98_still_present"], [1, 2, 3])

    def test_trace_identity_and_leading_coefficients(self):
        row = self.card["original_section"]
        self.assertEqual(row["universal_trace_identity"]["trace_identity_residual"], "0")
        actual = row["actual_trace"]
        self.assertEqual(actual["degrees_T_x_y"], [4, 6])
        z = sp.Symbol("z")
        self.assertEqual(sp.sympify(actual["leading_x"]), 36/z)
        self.assertEqual(sp.sympify(actual["leading_y_over_r"]), -216/z**2)
        self.assertFalse(actual["concrete_original_point_has_been_found"])

    def test_height_four_is_conditional_not_rank_lower_bound(self):
        row = self.card["original_section"]["conditional_height_and_rank"]
        self.assertEqual(row["conditional_geometric_height"], 4)
        self.assertFalse(row["original_section_existence_proved"])
        self.assertFalse(row["threefold_height_divisor_of_trace_computed"])
        rank = row["rank_one_compatibility"]
        self.assertEqual(rank["ratios_are_rational_squares"], [False, False])
        self.assertFalse(rank["unconditional_original_rank_lower_bound_raised"])

    def test_new_height_bound_and_repeated_root_exclusion_are_not_omitted(self):
        row = self.card["original_section"]["conditional_height_and_rank"]
        self.assertEqual(row["geometric_D6_minimum_height_certificate"]["minimum_nonzero_geometric_height"], "5/2")
        self.assertTrue(row["repeated_root_subchart_exclusion"]["excluded_over_algebraic_closure_C_X"])
        self.assertTrue(row["conditional_geometric_primitivity"]["primitive_modulo_torsion"])
        self.assertFalse(row["conditional_two_cubic_points_independent"]["unconditional_original_rank_lower_bound_raised"])

    def test_original_rank_torsion_targets_preserved(self):
        for key in ("actual_original_MW_torsion_order", "actual_original_MW_free_rank_bounds", "conditional_unit_charge_section_height_S_F", "conditional_doubled_charge_section_height_S_F"):
            self.assertEqual(self.card[key], self.previous["consolidated_theory_card"][key])
        self.assertIsNone(self.card["actual_original_MW_free_rank"])
        self.assertFalse(self.card["actual_original_nonzero_section_constructed"])

    def test_all_scope_decisions_copied_exactly(self):
        for key, route_key in (("strict_master_decision", "terminal_decision"), ("supersession_ledger", "supersession_boundary"),
                               ("cross_sector_scope_checks", "cross_sector_scope_checks"), ("gate_ledger", "gate_ledger"),
                               ("next_required_action", "next_required_action"), ("primary_sources", "primary_sources")):
            self.assertEqual(self.report[key], self.route[route_key])

    def test_all_branch_gates_open_V21_scope_unchanged(self):
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertEqual(len(self.report["gate_ledger"]), 8)
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])
        self.assertEqual(self.report["next_required_action"]["id"], audit.NEXT_ID)

    def test_no_complete_or_empirical_claim(self):
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])
        self.assertFalse(self.card["experimental_confirmation"])
        self.assertFalse(self.card["full_quantum_anomaly_cancelled"])
        self.assertFalse(self.card["same_action_spectrum_and_geometry_realized"])

    def test_source_test_pins(self):
        self.assertEqual(self.report["artifact_hashes"]["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(self.report["artifact_hashes"]["test_sha256"], audit.file_sha(audit.TEST_PATH))

    def test_resealed_historical_route_change_rejected(self):
        report = copy.deepcopy(self.report)
        report["route_matrix"][0]["accepted"] = True
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_resealed_false_completion_rejected(self):
        report = copy.deepcopy(self.report)
        report["strict_master_decision"]["theory_complete"] = True
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
