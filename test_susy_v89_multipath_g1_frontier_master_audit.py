import copy
import json
import unittest

import susy_v89_multipath_g1_frontier_master_audit as audit


class TestV89MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_report_validates_and_core_is_canonical(self):
        audit.validate_report(self.report)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_lineage_cores_are_exact(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V88_master": audit.EXPECTED_CORES["v88_master"],
            "V89_route": audit.EXPECTED_CORES["v89_route"],
        })

    def test_v88_route_matrix_is_preserved_and_b89_appended(self):
        parent = audit.load_bound(audit.V88_MASTER_PATH, audit.EXPECTED_CORES["v88_master"])
        self.assertEqual(
            audit.canonical_sha(self.report["route_matrix"][:-1]),
            audit.canonical_sha(parent["route_matrix"]),
        )
        last = self.report["route_matrix"][-1]
        self.assertEqual(last["route_id"], "B89")
        self.assertFalse(last["accepted"])
        self.assertFalse(last["same_action_microscopic_completion"])

    def test_acceptance_ledger_records_exact_gains_and_no_gos(self):
        rows = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(rows["A2"], "PASS_EXACT_8_TRANSLATION_PAIRS_8_NECESSARY_PROJECTOR_TRIPLES")
        self.assertEqual(rows["A3"], "REJECTED_C8_FACTOR_PROJECTION_CONTAINED_IN_K2_C4")
        self.assertEqual(rows["A4"], "PASS_EXACT_KERNEL_PARITY_AND_BULK_ONLY__LOCAL_WALL_QUOTIENT_OPEN")
        self.assertEqual(rows["A9"], "REJECTED_GRAVITY_COUNT_AND_THREE_GS_EQUATIONS")
        self.assertEqual(rows["A10"], "PASS_EXACT_ZERO")
        self.assertEqual(rows["A13"], "PASS_EXACT")
        self.assertEqual(rows["A14"], "PASS_EXACT_EXISTENCE")
        self.assertEqual(rows["A19"], "REJECTED_NOT_FOUND")

    def test_c8_and_localized_decision_is_scoped(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["C8_exponent_projections_enumerated_for_frozen_V88_lifts"])
        self.assertTrue(row["independent_external_C8_kernel_parity_assignment_constructed"])
        self.assertTrue(row["audited_bulk_G8_representation_descent_constructed"])
        self.assertFalse(row["localized_wall_quotient_representation_descent_constructed"])
        self.assertTrue(row["new_z00_split_U5_local_phase_candidate_constructed"])
        self.assertTrue(row["split_U5_component_characters_are_new_action_data"])
        self.assertFalse(row["primitive_k_in_C8_factor_projection_for_frozen_V88_lifts"])
        self.assertFalse(row["external_C8_quantum_gauging_accepted"])
        self.assertFalse(row["z00_placement_inherited_from_V70"])
        self.assertFalse(row["rank_VEVs_preserve_primitive_C8"])
        self.assertFalse(row["common_BV_regulator_constructed"])

    def test_anomaly_decision_records_exact_no_go_and_boundary(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["smooth_connected_Spin11_I8_computed"])
        self.assertTrue(row["charged_fermion_gauge_log_twist_component_zero"])
        self.assertTrue(row["new_U1_vector_irreducible_gravity_obstruction"])
        self.assertFalse(row["gauged_continuous_U1_T_parent_current_spectrum"])
        self.assertFalse(row["signed_fixed_wall_character_computed"])
        self.assertFalse(row["fixed_wall_character_required_inputs_fully_frozen"])

    def test_compact_geometry_gain_is_not_overpromoted(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["global_projective_crepant_torsor_blowups_constructed"])
        self.assertTrue(row["generic_compact_smooth_resolved_member_exists"])
        self.assertTrue(row["natural_order4_root_rejected"])
        self.assertFalse(row["specific_compact_member_frozen_and_saturated"])
        self.assertFalse(row["literal_global_order4_action_constructed"])
        self.assertFalse(row["diagonal_resolved_Gammahat_orbibundle_constructed"])

    def test_no_extension_or_gate_is_accepted(self):
        self.assertEqual(self.report["consolidated_theory_card"]["accepted_extension_count"], 0)
        self.assertFalse(self.report["strict_master_decision"]["accepted_full_parent_action_exists"])
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])

    def test_every_gate_remains_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {f"G{index}" for index in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_fail_closed_guards_are_enabled(self):
        row = self.report["fail_closed_logic"]
        self.assertFalse(row["accept_if_partial_scaffolds_only"])
        self.assertTrue(all(value for key, value in row.items() if key != "accept_if_partial_scaffolds_only"))

    def test_next_action_is_bound_from_v89(self):
        self.assertEqual(
            self.report["next_required_action"],
            self.report["consolidated_theory_card"]["next_required_action"],
        )
        self.assertEqual(
            self.report["next_required_action"]["id"],
            "F90_EXTERNAL_U1_8_BV_FIXED_WALL_OR_EQUIVARIANT_GEOMETRY_DECISION",
        )

    def test_source_manifest_is_canonical(self):
        row = self.report["source_manifest"]
        self.assertEqual(row["kind"], "primary_sources_only")
        self.assertEqual(row["count"], 7)
        self.assertEqual(row["catalog_sha256"], audit.canonical_sha(self.report["primary_sources"]))

    def test_validator_rejects_false_promotions(self):
        mutations = [
            lambda value: value["route_matrix"][-1].__setitem__("accepted", True),
            lambda value: value["strict_master_decision"].__setitem__("primitive_k_in_C8_factor_projection_for_frozen_V88_lifts", True),
            lambda value: value["strict_master_decision"].__setitem__("external_C8_quantum_gauging_accepted", True),
            lambda value: value["strict_master_decision"].__setitem__("gauged_continuous_U1_T_parent_current_spectrum", True),
            lambda value: value["strict_master_decision"].__setitem__("signed_fixed_wall_character_computed", True),
            lambda value: value["strict_master_decision"].__setitem__("specific_compact_member_frozen_and_saturated", True),
            lambda value: value["strict_master_decision"].__setitem__("literal_global_order4_action_constructed", True),
            lambda value: value["strict_master_decision"].__setitem__("diagonal_resolved_Gammahat_orbibundle_constructed", True),
            lambda value: value["strict_master_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda value: value["strict_master_decision"].__setitem__("theory_complete", True),
            lambda value: value["gate_ledger"].__setitem__("G1", "CLOSED"),
            lambda value: value["fail_closed_logic"].__setitem__("continuous_U1T_no_go_does_not_reject_finite_C4", False),
        ]
        for mutate in mutations:
            value = copy.deepcopy(self.report)
            mutate(value)
            value["core_sha256"] = audit.canonical_sha(value)
            with self.assertRaises(RuntimeError):
                audit.validate_report(value)

    def test_generated_artifacts_are_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
