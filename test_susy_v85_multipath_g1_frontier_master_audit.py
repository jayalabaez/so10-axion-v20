import copy
import json
import unittest

import susy_v85_multipath_g1_frontier_master_audit as master


class TestV85MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = master.build_report()

    def test_report_validates_and_is_canonical(self):
        master.validate_report(self.report)
        self.assertEqual(master.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V84_master": master.EXPECTED_CORES["v84_master"],
            "V85_route": master.EXPECTED_CORES["v85_route"],
        })

    def test_route_matrix_appends_one_unaccepted_b85(self):
        routes = self.report["route_matrix"]
        self.assertEqual(len(routes), self.report["lineage"]["parent_route_count"] + 1)
        self.assertEqual(routes[-1]["route_id"], "B85")
        self.assertFalse(routes[-1]["accepted"])
        self.assertFalse(routes[-1]["same_action_microscopic_completion"])
        self.assertEqual([row["ordinal"] for row in routes], list(range(1, len(routes) + 1)))

    def test_compact_geometry_gain_and_resolution_boundary(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["explicit_compact_singular_F4_Weierstrass_parent_constructed"])
        self.assertEqual(decision["F4_monodromy_cover_genus_and_vector_hypers"], [3, 3])
        self.assertEqual(decision["F4_forced_4_6_points_on_S"], 0)
        self.assertEqual(decision["F4_equisingular_dimension"], 265)
        self.assertEqual(decision["ordinary_Jacobian_global_form"], "Spin(11)")
        self.assertFalse(decision["projective_crepant_resolution_constructed"])
        self.assertFalse(decision["Hodge_numbers_certified"])

    def test_action_retraction_and_c4f_frontier(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["V84_legacy_spinor_Higgs_rows_retracted"])
        self.assertEqual((decision["C4F_lift_rows_passing"], decision["C4F_quotient_lift_classes"]), (8, 2))
        self.assertTrue(decision["C4F_fixed_stratum_center_characters_classified"])
        self.assertFalse(decision["C4F_full_localized_isotropy_constructed"])
        self.assertEqual(decision["C4F_SU2_squared_residue_mod4"], 2)
        self.assertFalse(decision["C4F_anomaly_trivialization_constructed"])
        self.assertFalse(decision["C4F_order_four_torsor_constructed"])

    def test_ahss_precursor_gain_does_not_resolve_delta(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["AHSS_H9_and_H8"], ["0", "Z^2"])
        self.assertTrue(decision["AHSS_precursor_source_pages_survive"])
        self.assertFalse(decision["delta_d3_value_computed"])
        self.assertFalse(decision["delta_d4_value_computed"])
        self.assertEqual(decision["delta_exact_order"], "OPEN_ZERO_OR_ORDER2")

    def test_acceptance_criteria_encode_exact_open_and_rejected_results(self):
        criteria = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(criteria["A3"], "PASS_EXACT_SINGULAR_WEIERSTRASS")
        self.assertEqual(criteria["A7"], "PASS_CONSISTENCY_PREDICTION_NOT_INDEPENDENT_CERTIFICATE")
        self.assertEqual(criteria["A10"], "OPEN_UNCONSTRUCTED")
        self.assertEqual(criteria["A19"], "REJECTED_RESIDUE_2_MOD4_WITHOUT_CANCELLATION")
        self.assertEqual(criteria["A21"], "OPEN_UNCONSTRUCTED")
        self.assertEqual(criteria["A24"], "PASS_EXACT_ZERO_AND_SURVIVE")
        self.assertEqual(criteria["A25"], "OPEN_UNCOMPUTED")
        self.assertEqual(criteria["A30"], "REJECTED_NOT_FOUND")

    def test_fail_closed_logic_is_explicit(self):
        logic = self.report["fail_closed_logic"]
        self.assertTrue(logic["singular_Weierstrass_is_not_certified_smooth_CY"])
        self.assertTrue(logic["ordinary_Jacobian_is_not_C4F_torsor"])
        self.assertTrue(logic["field_only_shadow_is_not_full_Dai_Freed_character"])
        self.assertTrue(logic["AHSS_source_survival_is_not_differential_value"])
        self.assertTrue(logic["q2_parity_is_not_d4_functional"])
        self.assertFalse(logic["accept_if_scaffolds_only"])

    def test_terminal_master_decision_is_open(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["same_action_microscopic_completion_found"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["accepted_extension_count"], 0)
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])
        self.assertTrue(all(value.startswith("OPEN") for value in self.report["gate_ledger"].values()))

    def test_validator_rejects_promotions(self):
        mutations = [
            (lambda x: x["strict_master_decision"].__setitem__("Hodge_numbers_certified", True), "promoted"),
            (lambda x: x["strict_master_decision"].__setitem__("C4F_SU2_squared_residue_mod4", 0), "residue"),
            (lambda x: x["strict_master_decision"].__setitem__("C4F_order_four_torsor_constructed", True), "promoted"),
            (lambda x: x["strict_master_decision"].__setitem__("delta_d4_value_computed", True), "falsely"),
            (lambda x: x["strict_master_decision"].__setitem__("accepted_full_parent_action_exists", True), "promoted"),
            (lambda x: x["gate_ledger"].__setitem__("G5", "OPEN: reassigned meaning"), "gate identity"),
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
        with self.assertRaisesRegex(RuntimeError, "B85 route"):
            master.validate_report(value)

    def test_validator_rejects_mutated_inherited_route(self):
        value = copy.deepcopy(self.report)
        value["route_matrix"][0]["name"] = "mutated parent route"
        value["lineage"]["parent_route_matrix_sha256"] = master.canonical_sha(value["route_matrix"][:-1])
        value["core_sha256"] = master.canonical_sha(value)
        with self.assertRaisesRegex(RuntimeError, "inherited V84 route matrix"):
            master.validate_report(value)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(master.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(master.OUT_MD.read_text(encoding="utf-8"), master.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
