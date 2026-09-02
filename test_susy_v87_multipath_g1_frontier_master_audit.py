import copy
import json
import unittest

import susy_v87_multipath_g1_frontier_master_audit as master


class TestV87MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = master.build_report()

    def test_report_validates_and_is_canonical(self):
        master.validate_report(self.report)
        self.assertEqual(master.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V86_master": master.EXPECTED_CORES["v86_master"],
            "V87_route": master.EXPECTED_CORES["v87_route"],
        })

    def test_route_matrix_appends_one_unaccepted_b87(self):
        routes = self.report["route_matrix"]
        self.assertEqual(len(routes), self.report["lineage"]["parent_route_count"] + 1)
        self.assertEqual(routes[-1]["route_id"], "B87")
        self.assertFalse(routes[-1]["accepted"])
        self.assertFalse(routes[-1]["same_action_microscopic_completion"])
        self.assertEqual([row["ordinal"] for row in routes], list(range(1, len(routes) + 1)))

    def test_compact_geometry_is_exact_but_smoothness_open(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["global_projective_crepant_ambient_constructed"])
        self.assertTrue(decision["compact_flatness_proved"])
        self.assertEqual(decision["formal_Euler_characteristic"], -520)
        self.assertEqual(decision["conditional_Hodge_numbers"], [8, 268])
        self.assertFalse(decision["compact_strict_transform_smooth_certified"])
        self.assertFalse(decision["unconditional_Hodge_numbers"])

    def test_period_two_geometry_is_not_resolved_relation(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["period_two_bisection_and_Spin11_Jacobian_constructed"])
        self.assertEqual(decision["bisection_period_index"], [2, 2])
        self.assertFalse(decision["resolved_bisection_j_squared_center_proved"])

    def test_selected_B_neutral_action_and_anomaly(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["selected_charge_pattern"], [2, 0, 2])
        self.assertTrue(decision["B_neutral_fixed_stratum_phase_candidate_passes"])
        self.assertFalse(decision["B_neutral_full_space_group_projectors_restored"])
        self.assertTrue(decision["B_neutral_rank1_action_exact"])
        self.assertTrue(decision["B_neutral_ordinary_C4_anomaly_residues_zero"])
        self.assertEqual(decision["selected_anomaly_tensor"], {
            "A3": 12, "A2": 16, "FY6_squared": 432, "FX_squared": 672,
            "TrF": 64, "TrF_cubed": 112, "F_squared_Y6": 0,
            "F_squared_X": 0, "FY6X": 48,
        })

    def test_zero_mode_inflow_does_not_determine_uv_counterterm(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["zero_mode_shadow_requires_V86_k2"])
        self.assertFalse(decision["UV_k2_counterterm_coefficient_determined"])
        self.assertEqual(decision["selected_aw4_coefficient"], 0)
        supersession = self.report["supersession_ledger"]
        self.assertTrue(supersession["V86_positive_lift_qF_B_equals_2_tensor_remains_correct"])
        self.assertFalse(supersession["V86_positive_lift_branch_selected"])
        self.assertFalse(supersession["V86_k2_product_inflow_required_by_zero_mode_shadow"])
        self.assertFalse(supersession["UV_k2_coefficient_determined"])

    def test_GS_screen_not_promoted(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["charge4_GS_integer_factorization_screen_passes"])
        self.assertFalse(decision["differential_GS_common_regulator_constructed"])

    def test_vacuum_has_only_nonfaithful_C2(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["residual_nongauge_component"], "C2")
        self.assertFalse(decision["faithful_C4_low_energy_selector_survives"])

    def test_full_quantum_and_same_action_boundaries_stay_open(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["global_diagonal_bisection_Sp3_bundle_constructed"])
        self.assertFalse(decision["full_stratified_HGamma_target_selected"])
        self.assertFalse(decision["full_fixed_wall_Dai_Freed_trivialization_constructed"])
        self.assertFalse(decision["same_action_microscopic_completion_found"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])

    def test_acceptance_ledger_marks_exact_superseded_and_open_results(self):
        criteria = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(criteria["A5"], "PASS_EXACT_EULER_MINUS520")
        self.assertEqual(criteria["A8"], "PASS_EXACT_2_2")
        self.assertEqual(criteria["A16"], "PASS_EXACT_ZERO")
        self.assertEqual(criteria["A17"], "SUPERSEDED_BRANCH_CORRECT_NOT_SELECTED")
        self.assertEqual(criteria["A13"], "PASS_EXACT_PHASE_TABLE_ONLY")
        self.assertEqual(criteria["A13B"], "OPEN_UNCONSTRUCTED")
        self.assertEqual(criteria["A18"], "NOT_REQUIRED_BY_ZERO_MODE_SHADOW")
        self.assertEqual(criteria["A18B"], "OPEN_UNDETERMINED")
        self.assertEqual(criteria["A26"], "OPEN_UNFORMULATED")

    def test_fail_closed_logic_is_explicit(self):
        logic = self.report["fail_closed_logic"]
        self.assertTrue(logic["smooth_projective_ambient_is_not_smooth_hypersurface"])
        self.assertTrue(logic["ordinary_anomaly_residues_are_not_full_fixed_wall_Dai_Freed"])
        self.assertTrue(logic["phase_level_projector_match_is_not_full_Gammahat_lift"])
        self.assertTrue(logic["residual_C2_is_not_faithful_C4_selector"])
        self.assertTrue(logic["partial_scaffolds_are_not_same_action_completion"])
        self.assertFalse(logic["accept_if_partial_scaffolds_only"])

    def test_terminal_decision_has_no_closed_gate(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["accepted_extension_count"], 0)
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_validator_rejects_false_promotions(self):
        mutations = [
            lambda x: x["strict_master_decision"].__setitem__("compact_strict_transform_smooth_certified", True),
            lambda x: x["strict_master_decision"].__setitem__("resolved_bisection_j_squared_center_proved", True),
            lambda x: x["strict_master_decision"].__setitem__("selected_charge_pattern", [2, 2, 2]),
            lambda x: x["strict_master_decision"].__setitem__("B_neutral_full_space_group_projectors_restored", True),
            lambda x: x["strict_master_decision"].__setitem__("selected_aw4_coefficient", 1),
            lambda x: x["strict_master_decision"].__setitem__("UV_k2_counterterm_coefficient_determined", True),
            lambda x: x["strict_master_decision"].__setitem__("faithful_C4_low_energy_selector_survives", True),
            lambda x: x["strict_master_decision"].__setitem__("full_fixed_wall_Dai_Freed_trivialization_constructed", True),
            lambda x: x["strict_master_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda x: x["strict_master_decision"].__setitem__("theory_complete", True),
            lambda x: x["gate_ledger"].__setitem__("G1", "CLOSED"),
        ]
        for mutate in mutations:
            value = copy.deepcopy(self.report)
            mutate(value)
            value["core_sha256"] = master.canonical_sha(value)
            with self.assertRaises(RuntimeError):
                master.validate_report(value)

    def test_validator_rejects_route_acceptance(self):
        value = copy.deepcopy(self.report)
        value["route_matrix"][-1]["accepted"] = True
        value["strict_master_decision"]["accepted_extension_count"] = 1
        value["core_sha256"] = master.canonical_sha(value)
        with self.assertRaisesRegex(RuntimeError, "B87 route"):
            master.validate_report(value)

    def test_validator_rejects_mutated_inherited_route(self):
        value = copy.deepcopy(self.report)
        value["route_matrix"][0]["name"] = "mutated"
        value["core_sha256"] = master.canonical_sha(value)
        with self.assertRaisesRegex(RuntimeError, "inherited V86 route matrix"):
            master.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(master.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(master.OUT_MD.read_text(encoding="utf-8"), master.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
