"""Cross-sector arithmetic, lineage and non-closure tests for V101."""
import copy
import json
import unittest
from unittest.mock import patch

import sympy as sp
import susy_v101_cover_lift_higgs_section_solvability_audit as audit


class TestV101Route(unittest.TestCase):
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

    def test_five_cover_kernels_match(self):
        f = self.report["frozen_space_group_cover_obstruction"]["five_cover_all_lift_choices"]
        q = self.report["intermediate_cover_quantization"]["classification"]
        self.assertEqual([r["kernel_Kprime"] for r in f], [r["kernel"] for r in q])

    def test_exact_levels_and_cover_degrees_are_distinct(self):
        q = self.report["intermediate_cover_quantization"]["classification"]
        self.assertEqual([r["minimum_positive_integer_stack"] for r in q], [8, 2, 4, 8, 1])
        self.assertEqual([r["cover_degree_over_old"] for r in q], [1, 2, 2, 2, 4])

    def test_no_cover_passes_both_single_response_and_unchanged_S(self):
        f = self.report["frozen_space_group_cover_obstruction"]["five_cover_all_lift_choices"]
        q = self.report["intermediate_cover_quantization"]["classification"]
        self.assertFalse(any(a["frozen_representation_lifts"] and b["minimum_positive_integer_stack"] == 1 for a, b in zip(f, q)))

    def test_all_central_lifts_not_just_saved_generators(self):
        f = self.report["frozen_space_group_cover_obstruction"]["exact_obstruction_theorem"]
        self.assertEqual(f["number_of_central_generator_choices_checked"], 89)
        self.assertEqual(f["number_of_proper_covers_admitting_frozen_representation"], 0)

    def test_changed_domains_not_installed(self):
        f = self.report["frozen_space_group_cover_obstruction"]["explicit_changed_spatial_domains"]
        self.assertEqual(f["checkerboard_gauge_root_lift"]["index_in_frozen_S"], 2)
        self.assertEqual(f["translation_combined_lift"]["minimum_index_of_any_finite_index_subgroup_that_lifts_to_combined_cover"], 4)
        self.assertFalse(f["changed_compactification_or_subgroup_adopted"])
        self.assertFalse(f["new_projectors_twisted_sectors_or_spectrum_computed"])

    def test_deck_not_old_fermion_parity(self):
        f = self.report["frozen_space_group_cover_obstruction"]["deck_versus_old_fermion_parity"]
        self.assertTrue(f["both_deck_generators_trivial_on_every_old_genuine_representation"])
        self.assertFalse(f["epsT_is_unchanged_universal_fermion_parity"])

    def test_diagonal_product_test_not_full_extension(self):
        q = self.report["intermediate_cover_quantization"]["diagonal_cover_analysis"]
        self.assertEqual(q["CP3_Q_period"], "1/8")
        self.assertFalse(q["passing_V100_diagonal_deck_product_test_proves_global_extension"])

    def test_actual_original_Phi_lines(self):
        m = self.report["Higgs_background_restriction"]["CP3_original_cocharacter"]
        self.assertEqual(m["selected_N1_scalar_line_degrees"]["Phi_plus"], 5)
        self.assertEqual(m["selected_N1_scalar_line_degrees"]["Phi_minus"], -4)
        self.assertEqual(m["Phi_pair_c2_coefficient_H2"], -20)

    def test_Phi_only_compensation_is_insufficient_for_mass_tensor(self):
        m = self.report["Higgs_background_restriction"]["CP3_Phi_only_compensated_cocharacter"]
        self.assertTrue(m["both_selected_Phi_lines_topologically_trivial"])
        self.assertFalse(m["constant_V93_lambda_kappa_covariant_under_this_Cartan"])
        self.assertEqual(m["required_lambda_kappa_coupling_line_degrees"], [-4, -4])

    def test_selected_mass_compensation_keeps_period_not_full_action(self):
        m = self.report["Higgs_background_restriction"]["CP3_selected_mass_compensated_cocharacter"]
        self.assertTrue(m["constant_V93_lambda_kappa_covariant_under_this_Cartan"])
        self.assertEqual(m["required_lambda_kappa_coupling_line_degrees"], [0, 0])
        self.assertEqual(sp.Rational(m["V100_P_over4_period_unchanged"]), sp.Rational(3, 8))
        self.assertFalse(m["actual_physical_background_admissibility_proved"])

    def test_UV_and_finite_phases_not_erased(self):
        m = self.report["Higgs_background_restriction"]["UV_IR_and_finite_boundary"]
        self.assertFalse(m["UV_anomaly_erased_by_Higgsing"])
        self.assertFalse(m["finite_C8_or_residual_C2_torsion_anomaly_computed_here"])
        self.assertEqual(m["V90_full_VEV_external_stabilizer_order"], 2)

    def test_original_member_and_frontier_preserved(self):
        g = self.report["original_section_solvability"]
        old = self.parents["v100_route"]["original_section_existence"]
        for key in ("coefficient_payload_sha256", "original_equation_list_sha256", "preserved_frontier"):
            self.assertEqual(g[key], old[key])

    def test_both_valuations_control_poles(self):
        g = self.report["original_section_solvability"]["transformed_newton_boundary_certificate"]
        self.assertEqual(g["common_possible_pole_rays"], [[-3, 1], [1, 1]])
        self.assertTrue(g["all_solution_coordinates_integral_at_X_one"])
        self.assertTrue(g["all_X_one_solution_coordinates_integral_at_101"])
        self.assertTrue(g["zero_coordinate_cases"]["w_identically_zero_cannot_allow_z_pole"])

    def test_universal_saturation_before_specialization(self):
        g = self.report["original_section_solvability"]["universal_saturation_identity"]
        self.assertEqual(g["exact_universal_identity"], "c*ell-b*mu=a*E")
        self.assertEqual(g["exact_universal_identity_residual"], "0")
        self.assertTrue(g["specialized_pivot_is_not_divided_out"])

    def test_modular_contradiction_not_alone_generic_proof(self):
        g = self.report["original_section_solvability"]["specialized_finite_field_certificate"]
        self.assertEqual(g["augmented_seven_equation_Groebner_basis"], ["1"])
        self.assertEqual(g["univariate_Bezout"]["exact_residue"], "1")
        self.assertFalse(g["unit_ideal_alone_claimed_to_imply_generic_exclusion"])

    def test_one_chart_excluded_three_remain_open(self):
        g = self.report["original_section_solvability"]
        self.assertTrue(g["exceptional_chart_valuative_exclusion"]["all_zero_linear_pivot_chart_excluded_over_algebraic_closure_C_X"])
        frontier = g["remaining_section_frontier"]
        self.assertEqual(frontier["nonzero_linear_pivot_charts_still_open"], [1, 2, 3])
        self.assertFalse(frontier["all_rational_sections_excluded"])
        self.assertEqual([frontier["original_free_rank_lower_bound"], frontier["original_free_rank_upper_bound"]], [0, 11])

    def test_conditional_formulas_remain_identities_not_instances(self):
        g = self.report["original_section_solvability"]["exceptional_chart_valuative_exclusion"]
        self.assertTrue(g["old_conditional_exceptional_pair_trace_difference_has_no_instance_on_this_member"])
        self.assertFalse(g["V100_conditional_group_law_and_lattice_identities_retracted"])

    def test_all_eight_gates_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {"G"+str(i) for i in range(1, 9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"], [])
        self.assertFalse(self.report["terminal_decision"]["theory_complete"])

    def test_next_step_targets_remaining_not_empty_chart(self):
        next_step = self.report["next_required_action"]
        self.assertEqual(next_step["id"], audit.NEXT_ID)
        self.assertIn("three remaining nonzero-linear-pivot", next_step["primary"])
        self.assertIn("common action", next_step["parallel"])

    def test_resealed_promotion_rejected(self):
        bad = copy.deepcopy(self.report)
        bad["terminal_decision"]["theory_complete"] = True
        bad["core_sha256"] = audit.canonical_sha(bad)
        with self.assertRaises(RuntimeError):
            audit.validate_report(bad)

    def test_changed_parent_rejected(self):
        with patch.object(audit.common, "load_bound", side_effect=RuntimeError("changed parent")):
            with self.assertRaises(RuntimeError):
                audit.build_report()

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
