import copy
import json
import unittest

import susy_v93_multipath_g1_frontier_master_audit as audit


class TestV93Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_report()

    def test_parent_cores(self):
        self.assertEqual(self.report["input_core_hashes"],audit.EXPECTED_CORES)

    def test_all_twenty_old_routes_unchanged(self):
        previous=audit.load_bound(audit.V92_PATH,audit.EXPECTED_CORES["v92_master"])
        self.assertEqual(self.report["route_matrix"][:-1],previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"],audit.canonical_sha(previous["route_matrix"]))

    def test_B93_appended_unaccepted(self):
        rows=self.report["route_matrix"]
        self.assertEqual(len(rows),21)
        self.assertEqual(rows[-1]["route_id"],"B93")
        self.assertEqual([r["ordinal"] for r in rows],list(range(1,22)))
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])

    def test_rank_obstruction_and_mass_matching(self):
        row=self.report["consolidated_theory_card"]
        self.assertEqual((row["ordinary_GS_span_rank"],row["rank_with_bare_local_polynomial"]),(9,10))
        self.assertEqual(row["heavy_singlet_TrQ_TrQ3"],[36,864])
        self.assertTrue(row["independent_normal_axion_half_period_failure"])

    def test_explicit_smooth_R_not_full_action(self):
        row=self.report["consolidated_theory_card"]
        self.assertTrue(row["nine_mass_terms_R_and_wall_character_tests_pass"])
        self.assertFalse(row["same_action_spectrum_and_geometry_realized"])

    def test_Jacobian_matter_is_conditional(self):
        row=self.report["consolidated_theory_card"]
        self.assertEqual(row["conditional_Jacobian_nonlocal_vector11_hypers"],3)
        self.assertEqual(row["torsor_period_and_index"],[2,2])
        self.assertIsNone(row["Jacobian_MW_rank"])

    def test_visible_tensor(self):
        self.assertEqual(self.report["consolidated_theory_card"]["full_conditional_visible_continuous_anomaly_tensor"],[-32,-24,-816,-576,-68,1408,96,384,96])

    def test_zero_accepted_extensions(self):
        self.assertEqual(self.report["consolidated_theory_card"]["accepted_extension_count"],0)
        self.assertFalse(self.report["strict_master_decision"]["theory_complete"])

    def test_all_gates_open_next_F94(self):
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"],[])
        self.assertEqual(self.report["next_required_action"]["id"],"F94_QUANTIZED_RELATIVE_WALL_COMPLETION_AND_MW_HEIGHT")
        self.assertTrue(self.report["lineage"]["canonical_V21_gate_scope_unchanged"])

    def test_rehashed_false_promotions_rejected(self):
        for key in ("theory_complete","same_action_microscopic_parent_accepted",
                    "quantized_relative_WCS_Dai_Freed_trivialization_constructed",
                    "all_F93_obligations_fully_completed"):
            changed=copy.deepcopy(self.report)
            changed["strict_master_decision"][key]=True
            changed["core_sha256"]=audit.canonical_sha(changed)
            with self.assertRaises(RuntimeError):
                audit.validate_report(changed)

    def test_mutated_route_history_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["route_matrix"][0]["name"]="forged"
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__=="__main__":
    unittest.main()
