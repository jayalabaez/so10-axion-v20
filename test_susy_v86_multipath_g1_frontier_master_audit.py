import copy
import json
import unittest

import susy_v86_multipath_g1_frontier_master_audit as master


class TestV86MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = master.build_report()

    def test_report_validates_and_is_canonical(self):
        master.validate_report(self.report)
        self.assertEqual(master.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V85_master": master.EXPECTED_CORES["v85_master"],
            "V86_route": master.EXPECTED_CORES["v86_route"],
        })

    def test_route_matrix_appends_one_unaccepted_b86(self):
        routes = self.report["route_matrix"]
        self.assertEqual(len(routes), self.report["lineage"]["parent_route_count"] + 1)
        self.assertEqual(routes[-1]["route_id"], "B86")
        self.assertFalse(routes[-1]["accepted"])
        self.assertFalse(routes[-1]["same_action_microscopic_completion"])
        self.assertEqual([row["ordinal"] for row in routes], list(range(1, len(routes) + 1)))

    def test_geometry_retraction_and_new_target(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["V85_Hodge_prediction_retracted"])
        self.assertEqual(decision["conditional_Hodge_numbers_and_Euler"], [8, 268, -520])
        self.assertTrue(decision["published_crepant_blowup_template_specialized"])
        self.assertFalse(decision["projective_crepant_resolution_constructed"])
        self.assertTrue(decision["V85_four_section_with_j_squared_z_target_retracted"])
        self.assertFalse(decision["corrected_bisection_target_constructed"])

    def test_anomaly_obstruction_and_conditional_inflow(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["C4F_SU2_squared_residue_mod4"], 2)
        self.assertTrue(decision["C4_preserving_gapped_matter_repair_excluded"])
        self.assertTrue(decision["C4_preserving_one_axion_repair_excluded"])
        self.assertTrue(decision["product_background_inflow_target_constructed"])
        self.assertFalse(decision["full_diagonal_anomaly_trivialization_constructed"])

    def test_scoped_ahss_is_closed_without_scope_promotion(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["scoped_AHSS_d3"], "ZERO")
        self.assertEqual(decision["scoped_AHSS_d4"], [0, 0])
        self.assertEqual(decision["scoped_reduced_bordism"], "Z4")
        self.assertEqual(decision["scoped_total_bordism"], "Z4 direct_sum Z4")
        self.assertEqual(decision["scoped_hidden_extension"], "NON_SPLIT_Z4_NOT_Z2_PLUS_Z2")
        self.assertEqual(decision["scoped_qhat_delta"], "ZERO")
        self.assertFalse(decision["full_HGamma_C4F_target_computed"])

    def test_acceptance_criteria_capture_retractions_and_exact_results(self):
        criteria = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(criteria["A2"], "RETRACTED_FALSE")
        self.assertEqual(criteria["A4"], "PASS_EXACT_IF_SMOOTH_PROJECTIVE_CREPANT_8_268_MINUS520")
        self.assertEqual(criteria["A9"], "RETRACTED_CHARGE_NORMALIZATION_MISMATCH")
        self.assertEqual(criteria["A15"], "REJECTED_NONZERO_2_MOD4")
        self.assertEqual(criteria["A23"], "PASS_EXACT_ZERO")
        self.assertEqual(criteria["A24"], "PASS_EXACT_ZERO")
        self.assertEqual(criteria["A25"], "PASS_EXACT_NON_SPLIT_Z4")
        self.assertEqual(criteria["A26"], "PASS_EXACT_DELTA_ZERO")
        self.assertEqual(criteria["A28"], "OPEN_UNFORMULATED")

    def test_fail_closed_logic_is_explicit(self):
        logic = self.report["fail_closed_logic"]
        self.assertTrue(logic["conditional_Hodge_theorem_is_not_resolution_construction"])
        self.assertTrue(logic["crepant_local_template_is_not_global_compact_certificate"])
        self.assertTrue(logic["abstract_j_squared_center_is_not_resolved_bisection"])
        self.assertTrue(logic["product_background_inflow_is_not_full_diagonal_trivialization"])
        self.assertTrue(logic["scoped_Spin_Z8_bordism_is_not_full_HGamma_C4F_bordism"])
        self.assertFalse(logic["accept_if_partial_scaffolds_only"])

    def test_terminal_decision_has_no_closed_gate(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["same_action_microscopic_completion_found"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["accepted_extension_count"], 0)
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_validator_rejects_promotions(self):
        mutations = [
            lambda x: x["strict_master_decision"].__setitem__("projective_crepant_resolution_constructed", True),
            lambda x: x["strict_master_decision"].__setitem__("corrected_bisection_target_constructed", True),
            lambda x: x["strict_master_decision"].__setitem__("C4F_SU2_squared_residue_mod4", 0),
            lambda x: x["strict_master_decision"].__setitem__("C4_preserving_gapped_matter_repair_excluded", False),
            lambda x: x["strict_master_decision"].__setitem__("full_diagonal_anomaly_trivialization_constructed", True),
            lambda x: x["strict_master_decision"].__setitem__("scoped_AHSS_d4", [1, 0]),
            lambda x: x["strict_master_decision"].__setitem__("full_HGamma_C4F_target_computed", True),
            lambda x: x["strict_master_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda x: x["strict_master_decision"].__setitem__("theory_complete", True),
            lambda x: x["gate_ledger"].__setitem__("G8", "CLOSED"),
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
        with self.assertRaisesRegex(RuntimeError, "B86 route"):
            master.validate_report(value)

    def test_validator_rejects_mutated_inherited_route(self):
        value = copy.deepcopy(self.report)
        value["route_matrix"][0]["name"] = "mutated"
        value["lineage"]["parent_route_matrix_sha256"] = master.canonical_sha(value["route_matrix"][:-1])
        value["core_sha256"] = master.canonical_sha(value)
        with self.assertRaisesRegex(RuntimeError, "inherited V85 route matrix"):
            master.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(master.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(master.OUT_MD.read_text(encoding="utf-8"), master.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
