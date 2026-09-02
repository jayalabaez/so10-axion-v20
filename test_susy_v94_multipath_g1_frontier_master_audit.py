import copy
import json
import unittest

import susy_v94_multipath_g1_frontier_master_audit as audit


class TestV94Master(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_report()

    def test_lineage_and_core(self):
        self.assertEqual(self.report["input_core_hashes"],audit.EXPECTED_CORES)
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))

    def test_old_twenty_one_routes_unchanged(self):
        previous=audit.load_bound(audit.V93_PATH,audit.EXPECTED_CORES["v93_master"])
        self.assertEqual(self.report["route_matrix"][:-1],previous["route_matrix"])
        self.assertEqual(self.report["lineage"]["parent_route_matrix_sha256"],audit.canonical_sha(previous["route_matrix"]))

    def test_B94_appended_unaccepted(self):
        rows=self.report["route_matrix"]
        self.assertEqual(len(rows),22)
        self.assertEqual([r["ordinal"] for r in rows],list(range(1,23)))
        self.assertEqual(rows[-1]["route_id"],"B94")
        self.assertFalse(rows[-1]["accepted"])
        self.assertFalse(rows[-1]["same_action_microscopic_completion"])

    def test_conditional_wall_and_kernel_counts(self):
        row=self.report["consolidated_theory_card"]
        self.assertEqual(row["conditional_wall_Weyl_components"],28)
        self.assertEqual(row["wall_components_failing_natural_diagonal_kernel"],8)

    def test_defect_index_and_residual(self):
        row=self.report["consolidated_theory_card"]
        self.assertEqual(row["unit_defect_real_chiral_index"],9)
        self.assertEqual(row["unit_defect_net_chiral_central_charge"],"9/2")
        self.assertEqual(row["defect_curvature_exact_residual"],"0")

    def test_visible_moments_retained(self):
        self.assertEqual(self.report["consolidated_theory_card"]["full_visible_TrQ_TrQ3"],[-68,1408])

    def test_torsion_not_free_rank(self):
        row=self.report["consolidated_theory_card"]
        self.assertEqual(row["actual_Jacobian_torsion_order"],1)
        self.assertIsNone(row["actual_Jacobian_free_MW_rank"])
        self.assertFalse(row["cover_point_nonzero_multiples_descend"])

    def test_twist_not_same_gauge_group(self):
        row=self.report["consolidated_theory_card"]
        self.assertTrue(row["twist_has_non_torsion_section"])
        self.assertEqual(row["twist_minimal_S_orders"],[0,0,2])
        self.assertFalse(row["twist_preserves_required_B5"])

    def test_all_gates_open_F95(self):
        self.assertEqual(self.report["consolidated_theory_card"]["accepted_extension_count"],0)
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["strict_master_decision"]["closed_gates"],[])
        self.assertEqual(self.report["next_required_action"]["id"],"F95_RELATIVE_SPIN_NORMAL_DEFECT_GLUE_AND_INVARIANT_MW_SECTION")

    def test_rehashed_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["strict_master_decision"]["theory_complete"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_history_change_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["route_matrix"][0]["name"]="forged"
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
