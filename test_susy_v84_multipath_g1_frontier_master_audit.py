import copy
import json
import unittest

import susy_v84_multipath_g1_frontier_master_audit as master


class TestV84MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = master.build_report()

    def test_report_validates_and_is_canonical(self):
        master.validate_report(self.report)
        self.assertEqual(master.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        self.assertEqual(self.report["input_core_hashes"]["V83_master"], master.EXPECTED_CORES["v83_master"])
        self.assertEqual(self.report["input_core_hashes"]["V84_route"], master.EXPECTED_CORES["v84_route"])

    def test_route_matrix_appends_one_unaccepted_b84(self):
        routes = self.report["route_matrix"]
        self.assertEqual(len(routes), self.report["lineage"]["parent_route_count"] + 1)
        self.assertEqual(routes[-1]["route_id"], "B84")
        self.assertFalse(routes[-1]["accepted"])
        self.assertEqual([row["ordinal"] for row in routes], list(range(1, len(routes) + 1)))

    def test_unchanged_parent_is_rejected_but_redesign_not_promoted(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["unchanged_Gammahat_assignments_enumerated"], 1024)
        self.assertTrue(decision["pure_Spin11_center_forced"])
        self.assertTrue(decision["unchanged_five_factor_parent_rejected_exactly"])
        self.assertFalse(decision["C4F_kernel_contains_pure_z11"])
        self.assertTrue(decision["C4F_Spin11_faithful"])
        self.assertTrue(decision["C4F_direct_matched_representative_rows_pass"])
        self.assertEqual(decision["C4F_independent_sign_rows_passing"], 8)
        self.assertFalse(decision["C4F_fatal_spinor_adjoint_target_vacuum_admissible"])
        self.assertTrue(decision["C4F_localized_pure_center_repaired"])
        self.assertFalse(decision["C4F_full_localized_isotropy_constructed"])
        self.assertFalse(decision["C4F_full_quantum_parent_constructed"])

    def test_bare_phase_and_algebraic_wcs_screen_are_scoped(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["smooth_Q4_bare_phase_values"], ["i", "-i"])
        self.assertTrue(decision["smooth_Q4_bare_phase_primitive_fourth_root"])
        self.assertFalse(decision["bare_phase_fully_BV_orientation_pinned"])
        self.assertEqual(decision["algebraic_r2_shift_WCS_counts"], {"0": 4, "2": 12})
        self.assertFalse(decision["algebraic_r2_screen_classifies_physical_refinements"])
        self.assertFalse(decision["all_full_HGamma_WCS_refinements_fail"])

    def test_f4_uv_and_residue_junction_gains_are_preserved(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["F4_section_fiber_canonical"], [[2, -1], [-1, 0], [2, 2]])
        self.assertEqual(decision["F4_so11_Lie_algebra_vector_and_neutral_hypers"], [3, 266])
        self.assertFalse(decision["F4_global_gauge_group_matched"])
        self.assertEqual(decision["critical_heterotic_full_central_charges"], [24, 12])
        self.assertEqual(decision["minimal_effective_residue_lifts"], [[1, -1], [5, -3]])
        self.assertFalse(decision["residue_lifts_irreducible"])
        self.assertFalse(decision["explicit_compact_F4_Weierstrass_parent_constructed"])

    def test_source_cap_and_delta_frontier_are_fail_closed(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["restricted_T2xS4_half_BPS_solution_exists"])
        self.assertTrue(decision["ordinary_relative_product_cap_constructed"])
        self.assertFalse(decision["product_cap_double_represents_Q4"])
        maps = decision["delta_potential_associated_graded_candidate_differentials"]
        self.assertEqual(len(maps), 2)
        self.assertIn("potential incoming d3:", maps[0])
        self.assertIn("potential incoming d4:", maps[1])
        self.assertFalse(decision["delta_d3_source_page_survival_computed"])
        self.assertFalse(decision["delta_d4_source_page_survival_computed"])
        self.assertFalse(decision["delta_d3_value_computed"])
        self.assertFalse(decision["delta_d4_value_computed"])
        self.assertFalse(decision["delta_chain_level_candidate_identification_proved"])
        self.assertFalse(decision["delta_post_Einfinity_extension_resolved"])
        self.assertEqual(decision["delta_exact_order"], "OPEN_ZERO_OR_ORDER2")

    def test_acceptance_criteria_encode_pass_rejection_and_open_boundaries(self):
        criteria = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(criteria["A3"], "REJECTED_PURE_Z11_FORCED")
        self.assertEqual(criteria["A6"], "PASS_EXACT")
        self.assertEqual(criteria["A10"], "OPEN_UNCONSTRUCTED")
        self.assertEqual(criteria["A15"], "PASS_EXACT_PRIMITIVE_FOURTH_ROOT")
        self.assertEqual(criteria["A19"], "OPEN_FALSE_BOUNDARY_NOT_A_CLASSIFICATION")
        self.assertEqual(criteria["A24"], "PASS_EXACT")
        self.assertEqual(criteria["A25"], "REJECTED_FIXED_SECTION_COMPONENTS")
        self.assertEqual(criteria["A31"], "REJECTED_FORGETFUL_CLASS_ZERO_VS_ORDER4")
        self.assertEqual(criteria["A35"], "OPEN_ZERO_OR_ORDER2")

    def test_fail_closed_logic_is_explicit(self):
        logic = self.report["fail_closed_logic"]
        self.assertTrue(logic["unchanged_parent_no_go_does_not_reject_action_changes"])
        self.assertTrue(logic["C4F_algebra_is_not_full_stratified_parent"])
        self.assertTrue(logic["F4_topological_spectrum_match_is_not_explicit_compact_UV_model"])
        self.assertTrue(logic["algebraic_coefficient_scan_is_not_physical_refinement_classification"])
        self.assertTrue(logic["ordinary_cap_is_not_WCS_or_Dai_Freed_glue"])
        self.assertFalse(logic["accept_if_scaffolds_only"])

    def test_terminal_master_decision_is_open(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["same_action_microscopic_completion_found"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["accepted_extension_count"], 0)
        self.assertEqual(decision["current_action_status"], "REJECTED")
        self.assertIn("VIABLE", decision["research_program_status"])
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])
        self.assertTrue(all(value.startswith("OPEN") for value in self.report["gate_ledger"].values()))

    def test_validator_rejects_promotions(self):
        mutations = [
            (lambda x: x["strict_master_decision"].__setitem__("C4F_full_quantum_parent_constructed", True), "promoted"),
            (lambda x: x["strict_master_decision"].__setitem__("bare_phase_fully_BV_orientation_pinned", True), "falsely"),
            (lambda x: x["strict_master_decision"].__setitem__("algebraic_r2_screen_classifies_physical_refinements", True), "promoted"),
            (lambda x: x["strict_master_decision"].__setitem__("residue_lifts_irreducible", True), "classification"),
            (lambda x: x["strict_master_decision"].__setitem__("product_cap_double_represents_Q4", True), "product cap"),
        ]
        for mutate, message in mutations:
            with self.subTest(message=message):
                value = copy.deepcopy(self.report)
                mutate(value)
                value["core_sha256"] = master.canonical_sha(value)
                with self.assertRaisesRegex(RuntimeError, message):
                    master.validate_report(value)

    def test_validator_rejects_route_acceptance(self):
        value = copy.deepcopy(self.report)
        value["route_matrix"][-1]["accepted"] = True
        value["strict_master_decision"]["accepted_extension_count"] = 1
        value["core_sha256"] = master.canonical_sha(value)
        with self.assertRaisesRegex(RuntimeError, "B84 route|acceptance"):
            master.validate_report(value)

    def test_validator_rejects_mutated_inherited_route(self):
        value = copy.deepcopy(self.report)
        value["route_matrix"][0]["name"] = "mutated parent route"
        value["lineage"]["parent_route_matrix_sha256"] = master.canonical_sha(value["route_matrix"][:-1])
        value["core_sha256"] = master.canonical_sha(value)
        with self.assertRaisesRegex(RuntimeError, "inherited V83 route matrix"):
            master.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(master.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(master.OUT_MD.read_text(encoding="utf-8"), master.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
