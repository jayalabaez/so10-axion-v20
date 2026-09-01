import copy
import json
import unittest

import susy_v82_qhat_bordism_d15_compensator_audit as v82


class TestV82QhatBordismD15CompensatorAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v82.build_report()

    def test_report_validates_and_is_canonical(self):
        v82.validate_report(self.report)
        self.assertEqual(v82.canonical_sha(self.report), self.report["core_sha256"])

    def test_lineage_is_hash_pinned(self):
        self.assertEqual(self.report["lineage"]["V77_route_core"], v82.EXPECTED_CORES["v77_route"])
        self.assertEqual(self.report["lineage"]["V81_route_core"], v82.EXPECTED_CORES["v81_route"])
        self.assertEqual(self.report["lineage"]["V81_master_core"], v82.EXPECTED_CORES["v81_master"])

    def test_qhat_graph_class_has_exact_order_four(self):
        audit = self.report["reduced_qhat_Q4_bordism_audit"]
        self.assertEqual(audit["classes"]["order_d"], 4)
        self.assertEqual(audit["classes"]["collapse_d"], "q")
        self.assertEqual(audit["classes"]["split_Z4_coordinate_d"], 1)
        self.assertEqual(audit["classes"]["order_delta_divides"], 2)
        self.assertEqual(audit["relative_kernel_problem"]["delta_zero"], "OPEN")
        self.assertEqual(audit["relative_kernel_problem"]["delta_exact_order"], "OPEN_ZERO_OR_ORDER2")

    def test_exact_AHSS_filtration_data(self):
        data = self.report["reduced_qhat_Q4_bordism_audit"]["AHSS_filtration_data"]
        self.assertEqual(data["Q4_H7_BC4_coefficient"], 2)
        self.assertEqual(data["filtration7_symbol"], "2xy^3")
        self.assertTrue(data["basepoint_and_qhat_same_filtration7_symbol"])
        self.assertEqual(data["delta_filtration_at_most"], 6)

    def test_complex_eta_probes_do_not_detect_delta(self):
        eta = self.report["reduced_qhat_Q4_bordism_audit"]["relative_eta_non_detection"]
        self.assertEqual(eta["vector_reduced_rho_integer"], "1")
        self.assertEqual(eta["vector_reduced_rho_mod1"], "0")
        self.assertEqual(eta["spinor_reduced_rho_integer"], "3")
        self.assertEqual(eta["spinor_reduced_rho_mod1"], "0")

    def test_closed7_source_retraction_is_precise(self):
        split = self.report["closed7_source_scope_correction"]["correct_domain_split"]
        self.assertTrue(split["closed_7d_anomaly_morphism_with_nonzero_checkY_admissible"])
        self.assertFalse(split["closed_Q4_requires_D15_strings"])
        self.assertTrue(split["compact_physical_6d_object_with_nonzero_Y_requires_sources_or_trivialization"])

    def test_source_residues_and_lift_ambiguity(self):
        audit = self.report["optional_closed7_defect_source_residue_audit"]
        self.assertEqual(audit["cohomology"]["g_order"], 4)
        self.assertEqual(audit["formal_source_data"]["qhat_charge_residue_in_Lambda_mod4Lambda"], [1, 1])
        self.assertEqual(audit["formal_source_data"]["basepoint_charge_residue_in_Lambda_mod4Lambda"], [1, 3])
        self.assertEqual(audit["formal_source_data"]["W3_boundary_on_closed_Q4"], "empty")
        self.assertFalse(audit["formal_source_data"]["compact6_restriction_or_boundary_map_constructed"])
        self.assertFalse(audit["lift_ambiguity"]["topology_selects_integral_charge_lift"])

    def test_qhat_worldsheet_local_probe(self):
        qhat = self.report["D15_local_worldsheet_inflow_audit"]["canonical_qhat_lift"]
        self.assertEqual((qhat["Q_squared"], qhat["Q_dot_a_KSV"], qhat["Q_dot_b_Spin11"]), (2, -4, 1))
        self.assertEqual(qhat["interacting_I4_prime"]["p1_T2"], "13/12")
        self.assertEqual((qhat["central_and_current_data"]["cL"], qhat["central_and_current_data"]["cR"]), (44, 18))
        self.assertEqual(qhat["Spin11_Sugawara"]["affine_c"], "11/2")
        self.assertTrue(qhat["necessary_local_screen_pass"])

    def test_basepoint_worldsheet_local_probe_and_bad_lift(self):
        audit = self.report["D15_local_worldsheet_inflow_audit"]
        base = audit["canonical_basepoint_lift"]
        bad = audit["same_residue_bad_basepoint_lift"]
        self.assertEqual((base["Q_squared"], base["Q_dot_a_KSV"], base["Q_dot_b_Spin11"]), (6, -8, 5))
        self.assertEqual((base["central_and_current_data"]["cL"], base["central_and_current_data"]["cR"]), (92, 42))
        self.assertEqual(base["Spin11_Sugawara"]["affine_c"], "275/14")
        self.assertTrue(base["necessary_local_screen_pass"])
        self.assertFalse(bad["necessary_local_screen_pass"])

    def test_compensator_fiber_no_go_is_scoped(self):
        comp = self.report["fixed_fiber_base_twist_compensator_audit"]
        self.assertEqual(comp["fiber"]["lambda_restriction"], "2r^2")
        self.assertFalse(comp["theorem"]["fixed_fiber_base_twist_compensator_exists"])
        self.assertFalse(comp["scoped_consequences"]["general_nonflat_same_rank_compensator_rejected"])
        self.assertTrue(comp["scoped_consequences"]["stable_extra_bundle_with_lambda_2r2_can_cancel_bookkeeping"])
        self.assertFalse(comp["scoped_consequences"]["stable_extra_bundle_preserves_same_action"])

    def test_fail_closed_terminal_decision(self):
        decision = self.report["terminal_decision"]
        self.assertTrue(decision["qhat_Q4_reduced_order_computed"])
        self.assertFalse(decision["compact6_source_residues_computed"])
        self.assertTrue(decision["optional_closed7_defect_residues_computed"])
        self.assertFalse(decision["general_nonflat_same_rank_compensator_rejected"])
        self.assertFalse(decision["physical_D15_worldsheet_SCFT_constructed"])
        self.assertFalse(decision["accepted_full_parent_action_exists"])
        self.assertEqual(decision["closed_gates"], [])
        self.assertFalse(decision["theory_complete"])

    def test_acceptance_ledgers_are_consistent_and_empty(self):
        accepted = [row["id"] for row in self.report["candidate_matrix"] if row["accepted"]]
        self.assertEqual(self.report["candidate_adjudication"]["accepted_ids"], accepted)
        self.assertEqual(accepted, [])
        self.assertFalse(self.report["terminal_decision"]["selected_candidate_accepted"])

    def test_validator_rejects_promoted_candidate(self):
        mutated = copy.deepcopy(self.report)
        mutated["candidate_matrix"][0]["accepted"] = True
        mutated["candidate_adjudication"]["accepted_ids"] = [mutated["candidate_matrix"][0]["id"]]
        mutated["terminal_decision"]["selected_candidate_accepted"] = True
        mutated["core_sha256"] = v82.canonical_sha(mutated)
        with self.assertRaisesRegex(RuntimeError, "acceptance|unaccepted"):
            v82.validate_report(mutated)

    def test_generated_artifacts_are_current(self):
        disk = json.loads(v82.OUT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(disk, self.report)
        self.assertEqual(v82.OUT_MD.read_text(encoding="utf-8"), v82.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
