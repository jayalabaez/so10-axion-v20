import copy
import json
import unittest

import susy_v83_multipath_g1_frontier_master_audit as master


class TestV83MultipathG1FrontierMasterAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = master.build_report()

    def test_report_validates_and_is_canonical(self):
        master.validate_report(self.report)
        self.assertEqual(master.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        self.assertEqual(self.report["input_core_hashes"]["V82_master"], master.EXPECTED_CORES["v82_master"])
        self.assertEqual(self.report["input_core_hashes"]["V83_route"], master.EXPECTED_CORES["v83_route"])

    def test_route_matrix_appends_one_unaccepted_B83(self):
        routes = self.report["route_matrix"]
        self.assertEqual(len(routes), self.report["lineage"]["parent_route_count"] + 1)
        self.assertEqual(routes[-1]["route_id"], "B83")
        self.assertFalse(routes[-1]["accepted"])
        self.assertEqual([row["ordinal"] for row in routes], list(range(1, len(routes) + 1)))

    def test_cyclic_gain_and_square_group_gap_are_both_preserved(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["smooth_bulk_cyclic_C4_lift_constructed"])
        self.assertEqual(decision["cycle_level_H78_shadow"], "jq(q) at the recorded cycle-data level")
        self.assertTrue(decision["cycle_data_projection"]["recorded_data_match_jq_q"])
        self.assertEqual(decision["cycle_data_projection"]["V82_order"], 4)
        self.assertFalse(decision["functorial_HGamma_to_H78_forgetful_map_constructed"])
        self.assertEqual(decision["bulk_kernel_choices_containing_rotation"], 2)
        self.assertFalse(decision["unique_global_center_kernel_selected"])
        self.assertEqual(decision["translation_relation_defect"], "z_11")
        self.assertFalse(decision["SO11_global_form_route_passes_quantization"])
        self.assertFalse(decision["full_Gammahat_space_group_constructed"])
        self.assertFalse(decision["full_HGamma_parent_lift_constructed"])

    def test_bare_and_WCS_contract_is_fail_closed(self):
        decision = self.report["strict_master_decision"]
        self.assertEqual(decision["U_signature"], 0)
        self.assertFalse(decision["physical_bare_phase_evaluated"])
        self.assertEqual(decision["Q4_linking_matrix"], [["1/2", "1/4"], ["1/4", "0"]])
        self.assertEqual(decision["Q4_g_self_linking"], "1/2")
        self.assertEqual(decision["reference_Gauss_sum"], "1")
        self.assertEqual(decision["reference_qhat_WCS_shadow"], "-1")
        self.assertFalse(decision["physical_WCS_phase_evaluated"])
        self.assertEqual(decision["total_anomaly_character_exponent"], "UNKNOWN")
        self.assertFalse(decision["bare_times_WCS_identity_proved"])

    def test_delta_remains_the_h0_hidden_extension(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["delta_equals_two_epsilon"])
        self.assertEqual(decision["epsilon_complex_rho"], "1/2")
        self.assertEqual(decision["delta_complex_rho_mod1"], "0")
        self.assertEqual(decision["delta_Adams_candidate"], "h0*p")
        self.assertEqual(decision["delta_exact_order"], "OPEN_ZERO_OR_ORDER2")

    def test_local_string_and_compact_source_are_retained_without_promotion(self):
        decision = self.report["strict_master_decision"]
        self.assertTrue(decision["local_4SO11_instanton_worldsheet_constructed"])
        self.assertEqual(decision["instanton_string_full_central_charges"], [42, 54])
        self.assertEqual(decision["compact6_source_Y"], [-2, 1])
        self.assertEqual(decision["compact6_source_residual"], [0, 0])
        self.assertTrue(decision["compact6_cohomological_source_incidence_constructed"])
        self.assertFalse(decision["compact6_on_shell_half_BPS_solution_constructed"])
        self.assertFalse(decision["full_HGamma_D15_sector_constructed"])

    def test_instanton_residue_no_go_and_charge_nonselection(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["instanton_tower_reaches_Q4_residues"])
        self.assertTrue(decision["infinite_formal_Q4_charge_lifts"])
        self.assertFalse(decision["unique_integral_Q4_charge_lift_selected"])

    def test_acceptance_criteria_preserve_pass_open_and_rejected_scopes(self):
        criteria = {row["id"]: row["status"] for row in self.report["acceptance_criteria"]}
        self.assertEqual(criteria["A4"], "PASS_EXACT")
        self.assertEqual(criteria["A7"], "OPEN_Z11_COCYCLE")
        self.assertEqual(criteria["A8"], "REJECTED_STRONG_QUANTIZATION_B_NOT_IN_2U")
        self.assertEqual(criteria["A18"], "PASS_EXACT_MINUS_ONE")
        self.assertEqual(criteria["A19"], "OPEN_NOT_SELECTED")
        self.assertEqual(criteria["A25"], "OPEN_ZERO_OR_ORDER2")
        self.assertEqual(criteria["A31"], "PASS_EXACT_COHOMOLOGICAL")
        self.assertEqual(criteria["A32"], "OPEN_UNCONSTRUCTED")
        self.assertEqual(criteria["A34"], "REJECTED_MOD4_PARITY")

    def test_fail_closed_logic_is_explicit(self):
        logic = self.report["fail_closed_logic"]
        self.assertTrue(logic["G1_requires_full_HGamma_and_common_regulator"])
        self.assertTrue(logic["G6_requires_on_shell_source_and_global_worldsheet_glue"])
        self.assertTrue(logic["G8_requires_numeric_bare_and_physical_WCS_total_character_one"])
        self.assertTrue(logic["reference_WCS_shadow_is_not_physical_value"])
        self.assertTrue(logic["local_worldsheet_is_not_full_orbifold_D15"])
        self.assertFalse(logic["accept_if_exact_local_gains_only"])

    def test_terminal_master_decision_is_rejected_and_open(self):
        decision = self.report["strict_master_decision"]
        self.assertFalse(decision["same_action_microscopic_completion_found"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["accepted_extension_count"], 0)
        self.assertEqual(decision["current_action_status"], "REJECTED")
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])
        self.assertTrue(all(value.startswith("OPEN") for value in self.report["gate_ledger"].values()))

    def test_validator_rejects_reference_shadow_promotion(self):
        mutated = copy.deepcopy(self.report)
        mutated["strict_master_decision"]["physical_WCS_phase_evaluated"] = True
        mutated["strict_master_decision"]["total_anomaly_character_exponent"] = 0
        mutated["strict_master_decision"]["bare_times_WCS_identity_proved"] = True
        mutated["core_sha256"] = master.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "reference WCS shadow|total character"):
            master.validate_report(mutated)

    def test_validator_rejects_local_string_promotion(self):
        mutated = copy.deepcopy(self.report)
        mutated["strict_master_decision"]["compact6_on_shell_half_BPS_solution_constructed"] = True
        mutated["strict_master_decision"]["full_HGamma_D15_sector_constructed"] = True
        mutated["core_sha256"] = master.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "cohomological incidence|full D15"):
            master.validate_report(mutated)

    def test_validator_rejects_route_acceptance(self):
        mutated = copy.deepcopy(self.report)
        mutated["route_matrix"][-1]["accepted"] = True
        mutated["strict_master_decision"]["accepted_extension_count"] = 1
        mutated["core_sha256"] = master.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "B83 route|acceptance"):
            master.validate_report(mutated)

    def test_validator_rejects_mutated_inherited_route(self):
        mutated = copy.deepcopy(self.report)
        mutated["route_matrix"][0]["name"] = "mutated parent route"
        mutated["lineage"]["parent_route_matrix_sha256"] = master.canonical_sha(mutated["route_matrix"][:-1])
        mutated["core_sha256"] = master.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "inherited V82 route matrix"):
            master.validate_report(mutated)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(master.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(master.OUT_MD.read_text(encoding="utf-8"), master.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
