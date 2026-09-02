import copy
import json
import unittest

import susy_v90_multipath_g1_frontier_master_audit as audit


class TestV90MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_report_validates_and_core_is_canonical(self):
        audit.validate_report(self.report)
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_lineage_cores_are_exact(self):
        self.assertEqual(self.report["input_core_hashes"], {
            "V89_master": audit.EXPECTED_CORES["v89_master"],
            "V90_route": audit.EXPECTED_CORES["v90_route"],
        })

    def test_v89_route_matrix_is_preserved_and_B90_appended(self):
        parent = audit.load_bound(audit.V89_MASTER_PATH, audit.EXPECTED_CORES["v89_master"])
        self.assertEqual(
            audit.canonical_sha(self.report["route_matrix"][:-1]),
            audit.canonical_sha(parent["route_matrix"]),
        )
        self.assertEqual(len(self.report["route_matrix"]), len(parent["route_matrix"]) + 1)
        last = self.report["route_matrix"][-1]
        self.assertEqual(last["route_id"], "B90")
        self.assertFalse(last["accepted"])
        self.assertFalse(last["same_action_microscopic_completion"])

    def test_acceptance_ledger_records_exact_gains_and_no_gos(self):
        rows = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(rows["A2"], "PASS_EXACT")
        self.assertEqual(rows["A6"], "PASS_EXACT_ZERO")
        self.assertEqual(rows["A7"], "OPEN_UNDERDETERMINED")
        self.assertEqual(rows["A10"], "REJECTED_UNIVERSAL_SIGN_CONTRADICTION")
        self.assertEqual(rows["A11"], "PASS_EXACT_CLASSICAL_POLYNOMIAL")
        self.assertEqual(rows["A13"], "RETRACTED_U1X_NONINVARIANT")
        self.assertEqual(rows["A16"], "REJECTED_BREAKS_TO_C2")
        self.assertEqual(rows["A18"], "PASS_EXACT")
        self.assertEqual(rows["A19"], "PASS_EXACT_UNIT")
        self.assertEqual(rows["A20"], "PASS_EXACT_MU4_X_MU2")
        self.assertEqual(rows["A22"], "REJECTED_NO_ROOT")
        self.assertEqual(rows["A25"], "REJECTED_NOT_FOUND")

    def test_quantum_decision_is_fail_closed(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["G8_component_extension_computed"])
        self.assertTrue(row["all_current_4D_C8_shadows_pass"])
        self.assertFalse(row["full_G8_quotient_Dai_Freed_character_computed"])
        self.assertFalse(row["neutral_tensor_gravity_projectors_frozen"])
        self.assertFalse(row["common_BV_regulator_constructed"])
        self.assertFalse(row["differential_WCS_trivialization_constructed"])
        self.assertFalse(row["Phi_zero_mode_Gammahat_projectors_constructed"])
        self.assertFalse(row["localized_continuous_inflow_constructed"])
        self.assertFalse(row["repaired_action_full_finite_anomaly_cancelled"])

    def test_action_repair_is_exact_but_unaccepted(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["unmodified_continuous_U1_8_parent_rejected"])
        self.assertTrue(row["conditional_smooth_bulk_GS_polynomial_scout_found"])
        self.assertTrue(row["corrected_compensator_conditional_operator_scout_found"])
        self.assertTrue(row["old_V88_compensator_decay_portals_retracted"])
        self.assertFalse(row["repair_physical_tensor_cone_certified"])
        self.assertFalse(row["primitive_C8_preserved_by_repair_vacuum"])

    def test_compact_geometry_is_complete_but_deck_root_is_not(self):
        row = self.report["strict_master_decision"]
        self.assertTrue(row["specific_rational_compact_member_frozen"])
        self.assertTrue(row["resolved_compact_member_smooth"])
        self.assertTrue(row["projection_descending_stabilizer_classified"])
        self.assertTrue(row["literal_global_C4_action_constructed"])
        self.assertFalse(row["classified_order4_deck_root_exists"])
        self.assertFalse(row["diagonal_resolved_Gammahat_orbibundle_constructed"])

    def test_no_extension_or_gate_is_accepted(self):
        self.assertEqual(self.report["consolidated_theory_card"]["accepted_extension_count"], 0)
        self.assertFalse(self.report["strict_master_decision"]["accepted_full_parent_action_exists"])
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"], [])
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])

    def test_every_SUSY_C8_branch_gate_remains_open(self):
        self.assertEqual(set(self.report["gate_ledger"]), {f"G{index}" for index in range(1, 9)})
        self.assertTrue(all(value.startswith("OPEN:") for value in self.report["gate_ledger"].values()))

    def test_fail_closed_guards_are_enabled(self):
        row = self.report["fail_closed_logic"]
        self.assertFalse(row["accept_if_partial_scaffolds_only"])
        self.assertTrue(all(
            value for key, value in row.items()
            if key != "accept_if_partial_scaffolds_only"
        ))

    def test_supersession_ledger_is_scoped(self):
        row = self.report["supersession_ledger"]
        self.assertTrue(row["V89_specific_compact_member_open_promoted_to_exact_rational_member"])
        self.assertTrue(row["V89_Rees_saturation_obligation_answered_by_finite_standard_open_smoothness_certificate"])
        self.assertTrue(row["V89_literal_order4_open_promoted_to_projection_descending_mu4_x_mu2_classification"])
        self.assertFalse(row["literal_C4_promoted_to_required_deck_root"])
        self.assertTrue(row["old_compensator_decay_portals_retracted"])
        self.assertFalse(row["four_dimensional_C8_shadows_promoted_to_full_G8_character"])

    def test_next_action_is_bound_from_V90(self):
        self.assertEqual(
            self.report["next_required_action"],
            self.report["consolidated_theory_card"]["next_required_action"],
        )
        self.assertEqual(
            self.report["next_required_action"]["id"],
            "F91_FINITE_G8_BORDISM_WCS_OR_PHYSICAL_TENSOR_CONE_DECISION",
        )

    def test_source_manifest_is_canonical(self):
        row = self.report["source_manifest"]
        self.assertEqual(row["kind"], "primary_sources_only")
        self.assertEqual(row["count"], 6)
        self.assertEqual(row["catalog_sha256"], audit.canonical_sha(self.report["primary_sources"]))

    def test_validator_rejects_false_promotions(self):
        mutations = [
            lambda value: value["route_matrix"][-1].__setitem__("accepted", True),
            lambda value: value["strict_master_decision"].__setitem__("full_G8_quotient_Dai_Freed_character_computed", True),
            lambda value: value["strict_master_decision"].__setitem__("common_BV_regulator_constructed", True),
            lambda value: value["strict_master_decision"].__setitem__("repair_physical_tensor_cone_certified", True),
            lambda value: value["strict_master_decision"].__setitem__("primitive_C8_preserved_by_repair_vacuum", True),
            lambda value: value["strict_master_decision"].__setitem__("classified_order4_deck_root_exists", True),
            lambda value: value["strict_master_decision"].__setitem__("diagonal_resolved_Gammahat_orbibundle_constructed", True),
            lambda value: value["strict_master_decision"].__setitem__("accepted_full_parent_action_exists", True),
            lambda value: value["strict_master_decision"].__setitem__("theory_complete", True),
            lambda value: value["gate_ledger"].__setitem__("G1", "CLOSED"),
            lambda value: value["fail_closed_logic"].__setitem__("literal_C4_is_not_order4_deck_root", False),
        ]
        for mutate in mutations:
            candidate = copy.deepcopy(self.report)
            mutate(candidate)
            candidate["core_sha256"] = audit.canonical_sha(candidate)
            with self.assertRaises(RuntimeError):
                audit.validate_report(candidate)

    def test_generated_artifacts_are_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")), self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"), audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
