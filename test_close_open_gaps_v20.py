#!/usr/bin/env python3
import json, unittest
import push_phenomenology_limits_v20 as push
import common_scale_so10_yukawa_v20 as common
import two_loop_so10_210_yukawa_v20 as two
import channel_fcnc_rates_v20 as channel
import strict_rg_audit_v20 as strict
import close_open_gaps_v20 as gaps

class OpenGapAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module,name in (
            (push,"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json"),
            (common,"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json"),
            (two,"TWO_LOOP_SO10_210_V20_VERDICT.json"),
            (channel,"CHANNEL_FCNC_RATES_V20_VERDICT.json"),
        ):
            r=module.build_report(); module.ROOT.joinpath(name).write_text(json.dumps(r,indent=2,default=str)+"\n",encoding="utf-8")
        r=strict.build_report(); strict.ROOT.joinpath("STRICT_RG_AUDIT_V20_VERDICT.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    def test_conditional_region_is_not_unique(self):
        r=gaps.conditional_unique_cf(); self.assertTrue(r["flag"]["conditional_region_Cf"]); self.assertFalse(r["flag"]["conditional_unique_Cf"]); self.assertFalse(r["flag"]["unconditional_unique_Cf"])
    def test_fcnc_channel_rates_advance_without_closure(self):
        r=gaps.fcnc_absence_theorem(); self.assertTrue(r["flag"]["exact_qI_theorem_proved"]); self.assertTrue(r["flag"]["channel_level_amplitudes_implemented"]); self.assertTrue(r["flag"]["channel_level_branching_ratios_implemented"]); self.assertFalse(r["flag"]["actual_finite_model_fcnc_absence_proved"]); self.assertFalse(r["flag"]["experimental_FCNC_bound_applied"]); self.assertFalse(r["flag"]["pointwise_experimental_likelihoods_implemented"]); self.assertFalse(r["flag"]["component_specific_uv_chiral_currents_derived"])
    def test_rg_completion_remains_open(self):
        r=gaps.yukawa_rg_global_fit(); self.assertTrue(r["flag"]["diagnostic_matrix_ODE_integrated"]); self.assertFalse(r["flag"]["actual_one_loop_matrix_beta_system_solved"]); self.assertFalse(r["flag"]["piecewise_threshold_yukawa_matching_complete"]); self.assertFalse(r["flag"]["two_loop_so10_complete"])
    def test_detection_not_claimed(self):
        self.assertFalse(gaps.ghz_detection_package()["flag"]["real_37GHz_detection"])
    def test_aggregate_report(self):
        r=gaps.build_report(); self.assertEqual(r["n_failed"],0); self.assertEqual(r["status"],"OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE"); self.assertTrue(r["gap_status"]["channel_level_FCNC_rates"]); self.assertFalse(r["gap_status"]["finite_model_tree_FCNC_absence_proved"]); self.assertFalse(r["gap_status"]["pointwise_experimental_FCNC_likelihoods"]); self.assertFalse(r["gap_status"]["full_common_scale_Yukawa_RG_fit"]); self.assertFalse(r["gap_status"]["two_loop_SO10_threshold_closure"])

if __name__=="__main__": unittest.main()
