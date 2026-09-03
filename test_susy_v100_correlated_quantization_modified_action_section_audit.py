"""Cross-sector and release-scope regression tests for the F100 route."""
import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp
import susy_v100_correlated_quantization_modified_action_section_audit as audit


class TestV100Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()
        cls.parents = {key: audit.common.load_bound(audit.ROOT/name, core) for key, (name, core) in audit.PARENTS.items()}

    def test_canonical(self):
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_all_helpers_reconstruct(self):
        for key, module in zip(audit.KEYS, audit.MODULES):
            self.assertEqual(self.report[key], module.build_certificate())

    def test_same_immutable_parents(self):
        for key in audit.KEYS:
            for parent, (_, core) in audit.PARENTS.items():
                self.assertEqual(self.report[key]["input_core_hashes"][parent], core)

    def test_source_and_test_pins(self):
        hashes = self.report["artifact_hashes"]
        self.assertEqual(hashes["generator_sha256"], audit.file_sha(audit.ROOT/(audit.__name__+".py")))
        self.assertEqual(hashes["test_sha256"], audit.file_sha(audit.TEST_PATH))
        for name, value in hashes.items():
            if name.endswith(".py"):
                self.assertEqual(value, audit.file_sha(audit.ROOT/name))

    def test_kernel_agreement(self):
        f = self.report["modified_equivariant_cover"]["minimal_combined_operator_cover"]
        q = self.report["correlated_quotient_period"]["genuine_Clifford_module"]
        self.assertEqual(f["old_kernel"], q["kernel"])
        self.assertEqual(f["Sigma_c_character"], q["bare_Sigma_bits"])

    def test_distinct_four_cover_and_eight_stack(self):
        self.assertEqual(self.report["modified_equivariant_cover"]["minimal_combined_operator_cover"]["minimum_simultaneous_operator_cover_degree"], 4)
        self.assertEqual(self.report["correlated_quotient_period"]["exact_quantization"]["minimum_positive_stack"], 8)
        self.assertTrue(self.report["cross_sector_scope_checks"]["cover_degree_four_is_not_response_stack_eight"])

    def test_common_target_polynomial(self):
        d, c = sp.symbols("d c")
        old = sp.sympify(self.report["correlated_quotient_period"]["exact_quantization"]["target_Q"])
        new = sp.sympify(self.report["modified_equivariant_cover"]["quantized_smooth_inverse_response"]["positive_response_curvature"])
        self.assertEqual(sp.expand(old.subs(d, 2*c)-new), 0)

    def test_CP3_witness_and_genuine_operator(self):
        q = self.report["correlated_quotient_period"]
        self.assertEqual(q["CP3_correlated_witness"]["P_over4_period"], "3/8")
        self.assertEqual(q["CP3_correlated_witness"]["indices_E0_E1_E2"], [0, 1, 5])
        self.assertFalse(any(q["genuine_Clifford_module"]["kernel_exponents"]["Sigma_tensor_R"]))

    def test_physical_background_admissibility_stays_open(self):
        q = self.report["correlated_quotient_period"]
        self.assertFalse(q["category"]["physical_Gammahat_or_orbifold_category_identified"])
        self.assertFalse(q["CP3_correlated_witness"]["is_a_frozen_orbifold_background"])

    def test_combined_space_group_not_old_projector(self):
        f = self.report["modified_equivariant_cover"]["pulled_back_square_space_group"]
        self.assertEqual([r["actual_lift_order"] for r in f["fixed_strata"]], [8, 8, 4, 4])
        self.assertTrue(all(r["ordinary_deck_average"] == "0" for r in f["bare_operator_ordinary_deck_projectors"]))
        self.assertFalse(f["orbifold_Dirac_domain_or_twisted_sectors_constructed"])

    def test_changed_response_does_not_forget_cover(self):
        f = self.report["modified_equivariant_cover"]["quantized_smooth_inverse_response"]
        self.assertTrue(f["genuine_quantized_closed5_inverse_defined"])
        self.assertFalse(f["cover_data_can_be_forgotten"])
        self.assertFalse(f["full_boundary_transgression_trivialization_or_corner_gluing_supplied"])

    def test_spectator_normalization_and_budget_gap(self):
        m = self.report["spectator_GS_obstruction"]["independent_W_GS_obstruction"]
        self.assertEqual(m["pure_W_allowed_N"], [0, 108])
        self.assertFalse(m["pure_W_equations_alone_exclude_all_regular_extensions"])
        self.assertEqual(m["required_removed_r4_lower_bound"]-m["entire_old_r4_budget"], 1223)

    def test_gauge_only_scout_not_full_spectrum(self):
        m = self.report["spectator_GS_obstruction"]["gauge_only_regular_replacement_search"]
        self.assertEqual(m["minimum_N"], 40)
        self.assertEqual(m["minimum_scout"]["t"], [0, 2, 4])
        self.assertEqual(m["minimum_scout"]["removed"], [28, 0, 2, 0, 10])
        self.assertEqual(m["minimum_scout"]["ordinary_quotient_half_source"], ["-56", "-18"])
        self.assertFalse(m["minimum_scout"]["is_accepted_new_sector"])

    def test_actual_free_projector_cost_kept(self):
        m = self.report["spectator_GS_obstruction"]["minimum_scout_actual_projector_cost"]
        self.assertEqual(m["conditional_total_free_chiral_count"], 27)
        self.assertTrue(m["both_old_Phi_plus_minus8_unavoidably_removed"])
        self.assertFalse(m["old_Phi_driven_mass_module_preserved"])
        self.assertFalse(m["removal_leaves_original_localized_anomaly_profile_unchanged"])

    def test_global_flavor_caveat_preserved(self):
        m = self.report["spectator_GS_obstruction"]["independent_W_GS_obstruction"]
        self.assertFalse(m["global_W_tHooft_anomaly_alone_is_quantum_inconsistency"])
        self.assertIn("not by itself", m["genuinely_global_W_scope"])

    def test_original_member_unchanged(self):
        g = self.report["original_section_existence"]
        old = self.parents["v99_route"]["original_section_elimination"]
        for key in ("coefficient_payload_sha256", "original_equation_list_sha256", "preserved_frontier"):
            self.assertEqual(g[key], old[key])

    def test_no_original_section_existence_inferred(self):
        self.assertFalse(self.report["terminal_decision"]["original_section_system_solved"])
        self.assertFalse(self.report["cross_sector_scope_checks"]["conditional_lattice_promoted_to_actual_original_sections"])

    def test_exact_conditional_section_lattice_and_saturation(self):
        row = self.report["original_section_existence"]["conditional_rank_two_lattice"]
        self.assertEqual(row["Gram_P1_P2"], [[3, -1], [-1, 3]])
        self.assertEqual(row["Gram_S_A"], [[4, 0], [0, 8]])
        self.assertEqual(row["P1_dot_P2"], 2)
        self.assertTrue(row["conditional_saturation_in_full_geometric_MW"]["rank_two_span_is_saturated"])

    def test_distinct_difference_square_condition(self):
        g = self.report["original_section_existence"]
        row = g["difference_point_and_square_descent"]["actual_original_member_formulas"]
        self.assertEqual(row["height"], 8)
        self.assertEqual(row["degrees_T_x_y"], [8, 12])
        self.assertTrue(row["z_itself_may_be_nonsquare_for_this_difference_point"])
        self.assertFalse(row["actual_z_H_solution_or_original_point_constructed"])
        self.assertFalse(g["existence_search_boundary"]["bounded_exploratory_runs_used_as_proof"])

    def test_old_restricted_results_not_retracted(self):
        s = self.report["supersession_boundary"]
        self.assertTrue(s["V99_old_equivariant_root_and_root_choice_obstructions_retained"])
        self.assertFalse(s["V98_chosen_cover_quantization_retracted"])
        self.assertFalse(s["V99_natural_normal_order_two_retracted"])

    def test_all_branch_gates_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"], [])

    def test_no_complete_or_empirical_claim(self):
        self.assertFalse(self.report["terminal_decision"]["theory_complete"])
        self.assertFalse(self.report["terminal_decision"]["same_action_microscopic_parent_accepted"])
        self.assertFalse(self.report["cross_sector_scope_checks"]["any_full_theory_or_empirical_confirmation_claimed"])

    def test_next_obligation_action_and_existence(self):
        nxt = self.report["next_required_action"]
        self.assertEqual(nxt["id"], audit.NEXT_ID)
        self.assertIn("actual physical background", nxt["primary"])
        self.assertIn("Solve or rigorously exclude", nxt["parallel"])

    def test_resealed_scope_promotion_rejected(self):
        report = copy.deepcopy(self.report)
        report["terminal_decision"]["theory_complete"] = True
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_resealed_history_change_rejected(self):
        report = copy.deepcopy(self.report)
        report["input_core_hashes"]["v99_route"] = "0"*64
        report["core_sha256"] = audit.canonical_sha(report)
        with self.assertRaises(RuntimeError):
            audit.validate_report(report)

    def test_parent_hash_checked_fresh(self):
        with patch.object(audit.common, "load_bound", side_effect=RuntimeError("changed source")):
            with self.assertRaises(RuntimeError):
                audit.build_report()

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
