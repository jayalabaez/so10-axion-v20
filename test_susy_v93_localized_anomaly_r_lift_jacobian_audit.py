import copy
import json
import unittest

import susy_v93_localized_anomaly_r_lift_jacobian_audit as audit


class TestV93IntegratedRoute(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=audit.build_report()

    def test_lineage_and_canonical_core(self):
        self.assertEqual(self.report["input_core_hashes"],{k:v[1] for k,v in audit.PARENTS.items()})
        self.assertEqual(self.report["core_sha256"],audit.canonical_sha(self.report))

    def test_independent_singlet_crosschecks(self):
        rows=self.report["cross_certificate_checks"]["independent_singlet_trace_vs_bulk_assembly"]
        self.assertEqual(len(rows),4)
        self.assertTrue(all(row["exact_difference"]=="0" for row in rows))

    def test_GS_obstruction_not_ignored(self):
        row=self.report["bare_bulk_local_anomaly"]["calculation"]["ordinary_bulk_GS_obstruction"]
        self.assertEqual(row["bare_bulk_value"],"1/2")
        self.assertFalse(self.report["terminal_decision"]["ordinary_bulk_GS_alone_cancels_selected_bare_bulk"])

    def test_smooth_R_does_not_complete_wall_action(self):
        row=self.report["smooth_R_and_wall_mass_extension"]
        self.assertTrue(row["singlet_R_extension"]["descends_through_all_current_smooth_kernel_generators"])
        self.assertFalse(row["limitations"]["all_inherited_localized_R_and_Gammahat_representations_constructed"])

    def test_mass_anomaly_not_erased(self):
        row=self.report["smooth_R_and_wall_mass_extension"]["mass_anomaly_matching"]
        self.assertEqual((row["TrQ"],row["TrQ3"]),(36,864))
        self.assertFalse(row["mass_erases_anomaly_matching_obligation"])

    def test_torsor_and_Jacobian_distinguished(self):
        row=self.report["actual_member_Jacobian_and_torsor"]
        self.assertEqual(row["torsor_section_obstruction"]["period"],2)
        self.assertFalse(row["torsor_section_obstruction"]["rational_section_exists"])
        self.assertIsNone(row["spectrum_compatibility"]["Jacobian_Mordell_Weil_rank"])

    def test_all_helper_files_bound(self):
        for stem in audit.HELPERS:
            for filename in (stem+".py","test_"+stem+".py"):
                self.assertEqual(self.report["artifact_hashes"][filename],audit.file_sha(audit.ROOT/filename))

    def test_no_mixed_action_promotion(self):
        boundary=self.report["supersession_boundary"]
        for key in ("mass_module_is_derived_from_existing_global_action",
                    "V92_four_lens_passes_imply_full_local_anomaly_cancellation",
                    "formal_two_axion_polynomial_identity_is_quantized_WCS",
                    "torsor_no_section_implies_Jacobian_MW_rank_zero"):
            self.assertFalse(boundary[key])

    def test_all_gates_open_F94_selected(self):
        self.assertEqual(set(self.report["gate_ledger"]),{"G"+str(i) for i in range(1,9)})
        self.assertTrue(all(v.startswith("OPEN:") for v in self.report["gate_ledger"].values()))
        self.assertEqual(self.report["terminal_decision"]["closed_gates"],[])
        self.assertEqual(self.report["next_required_action"]["id"],audit.NEXT_ID)
        self.assertFalse(self.report["terminal_decision"]["all_F93_obligations_fully_completed"])

    def test_rehashed_false_promotion_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["terminal_decision"]["quantized_relative_WCS_Dai_Freed_trivialization_constructed"]=True
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_rehashed_arithmetic_change_rejected(self):
        changed=copy.deepcopy(self.report)
        changed["bare_bulk_local_anomaly"]["calculation"]["ordinary_bulk_GS_obstruction"]["bare_bulk_value"]="0"
        changed["core_sha256"]=audit.canonical_sha(changed)
        with self.assertRaises(RuntimeError):
            audit.validate_report(changed)

    def test_generated_artifacts_current(self):
        self.assertEqual(json.loads(audit.OUT_JSON.read_text(encoding="utf-8")),self.report)
        self.assertEqual(audit.OUT_MD.read_text(encoding="utf-8"),audit.render_markdown(self.report))


if __name__=="__main__":
    unittest.main()
