import copy
import json
import unittest

import susy_v82_multipath_g1_frontier_master_audit as v82m


class TestV82MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v82m.build_report()

    def test_master_validates_and_is_canonical(self):
        v82m.validate_report(self.report)
        self.assertEqual(v82m.canonical_sha(self.report), self.report["core_sha256"])

    def test_frozen_inputs_are_bound(self):
        self.assertEqual(self.report["input_core_hashes"]["V81_master"], v82m.EXPECTED_CORES["v81_master"])
        self.assertEqual(self.report["input_core_hashes"]["V82_route"], v82m.EXPECTED_CORES["v82_route"])

    def test_B82_appends_without_changing_parent_routes(self):
        parent = json.loads(v82m.V81_MASTER_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.report["route_matrix"][:-1], parent["route_matrix"])
        self.assertEqual(self.report["route_matrix"][-1]["route_id"], "B82")
        self.assertFalse(self.report["route_matrix"][-1]["accepted"])

    def test_acceptance_matrix_scopes_progress(self):
        rows = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(rows["A3"], "PASS_EXACT_ORDER4")
        self.assertEqual(rows["A4"], "OPEN_ZERO_OR_ORDER2_SECONDARY")
        self.assertEqual(rows["A8"], "RETRACTED_CATEGORY_ERROR")
        self.assertEqual(rows["A12"], "REJECTED_MOD4_NONUNIQUENESS")
        self.assertEqual(rows["A17"], "REJECTED_FIBER_LAMBDA_2R2")
        self.assertEqual(rows["A19"], "OPEN_UNCLASSIFIED")
        self.assertEqual(rows["A24"], "OPEN_ILL_TYPED")
        self.assertEqual(rows["A29"], "OPEN_FAILED")

    def test_qhat_exact_order_and_kernel_scope(self):
        value = self.report["strict_master_decision"]
        self.assertTrue(value["qhat_Q4_reduced_order_computed"])
        self.assertEqual(value["qhat_Q4_reduced_order"], 4)
        self.assertEqual(value["qhat_Q4_split_coordinate"], 1)
        self.assertTrue(value["qhat_minus_basepoint_in_collapse_kernel"])
        self.assertEqual(value["qhat_minus_basepoint_order_divides"], 2)
        self.assertFalse(value["qhat_minus_basepoint_kernel_class_computed"])

    def test_source_domain_correction_and_D15_scope(self):
        value = self.report["strict_master_decision"]
        self.assertTrue(value["closed7_nonzero_Y_admissible"])
        self.assertTrue(value["V81_closed7_source_requirement_retracted"])
        self.assertFalse(value["D15_mandatory_for_closed_Q4"])
        self.assertTrue(value["D15_mandatory_for_compact6_nonzero_Y"])
        self.assertFalse(value["compact6_source_residues_computed"])
        self.assertTrue(value["optional_closed7_defect_residues_computed"])
        self.assertEqual(value["source_generator_order"], 4)

    def test_worldsheet_progress_is_not_promoted(self):
        value = self.report["strict_master_decision"]
        self.assertTrue(value["candidate_positive_lifts_pass_conditional_screens"])
        self.assertEqual(value["qhat_candidate_central_data"]["cL"], 44)
        self.assertEqual(value["basepoint_candidate_central_data"]["cL"], 92)
        self.assertFalse(value["physical_integral_charge_lift_selected"])
        self.assertFalse(value["physical_D15_worldsheet_SCFT_constructed"])

    def test_compensator_no_go_is_scoped(self):
        value = self.report["strict_master_decision"]
        self.assertTrue(value["fixed_fiber_base_twist_compensator_rejected"])
        self.assertFalse(value["general_nonflat_same_rank_compensator_rejected"])
        self.assertEqual(value["fiber_lambda_obstruction"], "2r^2")
        self.assertFalse(value["every_changed_action_compensator_rejected"])

    def test_theory_card_has_no_accepted_extension(self):
        card = self.report["consolidated_theory_card"]
        self.assertEqual(card["current_action_status"], "REJECTED")
        self.assertEqual(card["accepted_extension_count"], 0)
        self.assertEqual(card["accepted_extension_count"], sum(row["accepted"] for row in self.report["route_matrix"]))
        self.assertFalse(self.report["route_matrix"][-1]["accepted"])
        self.assertEqual(len(card["exact_gains"]), 9)
        self.assertTrue(any("source exclusion retracted" in item for item in card["exact_gains"]))
        self.assertTrue(any("topology does not select" in item for item in card["exact_gains"]))

    def test_validator_rejects_route_acceptance_count_drift(self):
        mutated = copy.deepcopy(self.report)
        mutated["route_matrix"][-1]["accepted"] = True
        mutated["core_sha256"] = v82m.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "accepted extension count"):
            v82m.validate_report(mutated)

    def test_terminal_master_is_fail_closed(self):
        value = self.report["strict_master_decision"]
        self.assertFalse(value["full_HGamma_qhat_lift_constructed"])
        self.assertFalse(value["physical_bare_phase_evaluated"])
        self.assertFalse(value["physical_WCS_phase_evaluated"])
        self.assertFalse(value["accepted_full_parent_action_exists"])
        self.assertEqual(value["closed_gates"], [])
        self.assertFalse(value["complete_theory"])

    def test_next_action_advances_parent_phase_and_D15(self):
        action = self.report["next_required_action"]
        self.assertEqual(action["id"], "F83_PARENT_QHAT_LIFT_REGULATED_PHASE_AND_D15_CHARGE_SELECTION")
        self.assertIn("bare-times-WCS", action["primary_objective"])
        self.assertFalse(action["accepted"])

    def test_generated_artifacts_are_current(self):
        disk = json.loads(v82m.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(v82m.OUT_MD.read_text(encoding="utf-8"), v82m.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
