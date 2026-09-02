import copy
import json
import unittest

import susy_v94_boundary_defects_and_mw_descent_audit as audit


class TestV94Route(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report()

    def test_parent_cores_and_canonical(self):
        self.assertEqual(self.report["input_core_hashes"], {k:v[1] for k,v in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"], audit.canonical_sha(self.report))

    def test_helpers_canonical_and_valid(self):
        for key,module in (("normal_wall_quantization",audit.normal),
                           ("Phi_zero_locus_and_defect_matching",audit.defects),
                           ("actual_Jacobian_and_quadratic_section",audit.geometry),
                           ("visible_Higgs_patch_and_periods",audit.visible)):
            module.validate_certificate(self.report[key])

    def test_all_helper_sources_and_tests_bound(self):
        for stem in audit.HELPERS:
            for filename in (stem+".py","test_"+stem+".py"):
                self.assertEqual(self.report["artifact_hashes"][filename],audit.file_sha(audit.ROOT/filename))

    def test_no_V93_retraction_or_unfounded_promotion(self):
        self.assertTrue(all(v is False for v in self.report["supersession_boundary"].values()))

    def test_both_C4_normal_restrictions(self):
        rows=self.report["cross_certificate_checks"]["both_C4_normal_restrictions"]
        self.assertEqual([r["stratum"] for r in rows],["z00","z11"])
        self.assertTrue(all(r["bare_plus_conditional_wall_f_zero"]=="0" for r in rows))
        checks=self.report["cross_certificate_checks"]
        self.assertEqual(checks["conditional_wall_components_per_C4"],28)
        self.assertEqual(checks["conditional_components_if_independently_replicated_at_both_C4"],56)
        self.assertFalse(checks["replication_constructs_global_wall_orbibundle"])

    def test_defect_and_threshold_same_charges(self):
        row=self.report["cross_certificate_checks"]
        self.assertTrue(row["defect_operator_and_visible_threshold_heavy_moments_match"])
        self.assertEqual(row["defect_B4_plus_I4"],"0")

    def test_same_geometry_member_not_same_action(self):
        row=self.report["cross_certificate_checks"]
        self.assertTrue(row["actual_Jacobian_uses_unchanged_V93_coefficients"])
        self.assertFalse(row["checks_prove_global_same_action_completion"])

    def test_conditional_constructive_results(self):
        row = self.report["terminal_decision"]
        self.assertTrue(row["conditional_normal_spin_period_repair_constructed"])
        self.assertTrue(row["conditional_wall_fermion_normal_slice_cancellation_constructed"])
        self.assertTrue(row["mass_sector_defect_index_and_curvature_matching_computed"])

    def test_MW_torsion_not_rank(self):
        row = self.report["terminal_decision"]
        self.assertTrue(row["actual_Jacobian_torsion_subgroup_trivial"])
        self.assertFalse(row["actual_Jacobian_free_rank_and_height_computed"])

    def test_extension_section_does_not_descend(self):
        row = self.report["terminal_decision"]
        self.assertTrue(row["explicit_non_torsion_section_over_quadratic_extension_constructed"])
        self.assertFalse(row["that_section_or_nonzero_multiple_descends_to_original_field"])

    def test_all_gates_open(self):
        self.assertEqual(set(self.report["gate_ledger"]),{"G"+str(i) for i in range(1,9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"],[])

    def test_F94_not_fully_completed(self):
        row = self.report["terminal_decision"]
        for key in ("full_Gammahat_wall_representations_frozen","quantized_relative_WCS_Dai_Freed_trivialization_constructed",
                    "same_action_microscopic_parent_accepted","all_F94_obligations_fully_completed","theory_complete"):
            self.assertFalse(row[key])

    def test_F95_not_a_twist_shortcut(self):
        self.assertEqual(self.report["next_required_action"]["id"],audit.NEXT_ID)
        self.assertIn("ORIGINAL",self.report["next_required_action"]["parallel"])
        self.assertFalse(self.report["next_required_action"]["accepted"])

    def test_rehashed_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["terminal_decision"]["theory_complete"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_arithmetic_change_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["visible_Higgs_patch_and_periods"]["census"]["moments"]["full"]["TrQ3"]=0
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__ == "__main__":
    unittest.main()
