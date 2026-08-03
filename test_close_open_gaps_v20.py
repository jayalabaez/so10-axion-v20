#!/usr/bin/env python3
import json, unittest
import push_phenomenology_limits_v20 as push
import common_scale_so10_yukawa_v20 as common
import two_loop_so10_210_yukawa_v20 as two
import channel_fcnc_rates_v20 as channel
import na62_pointwise_limit_v20 as na62
import twist_massless_limit_v20 as twist
import portal_constraint_ray_v20 as ray
import portal_boundary_heavy_spectrum_v20 as spectrum
import portal_family_orientation_map_v20 as orientation
import portal_full_complex_orientation_sphere_v20 as sphere
import pati_salam_yukawa_matching_v20 as ps
import theory_certification_math_v20 as cert
import portal_yukawa_posterior_v20 as posterior
import haloscope_37ghz_limit_compare_v20 as halo
import uv_vacuum_alignment_v20 as vac
import yukawa_rge_2loop_v20 as rge2
import fcnc_exact_likelihood_v20 as lik
import ensure_portal_artifacts_v20 as ensure
import strict_rg_audit_v20 as strict
import close_open_gaps_v20 as gaps

class OpenGapAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Sphere and portal chain must exist before strict_rg_audit reads them.
        ensure.ensure_portal_artifacts(force=True)
        for module,name in ((push,"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json"),(common,"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json"),(two,"TWO_LOOP_SO10_210_V20_VERDICT.json"),(channel,"CHANNEL_FCNC_RATES_V20_VERDICT.json"),(na62,"NA62_POINTWISE_LIMIT_V20_VERDICT.json"),(twist,"TWIST_MASSLESS_LIMIT_V20_VERDICT.json"),(ray,"PORTAL_CONSTRAINT_RAY_V20_VERDICT.json"),(spectrum,"PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json"),(orientation,"PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json"),(sphere,"PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json"),(ps,"PATI_SALAM_YUKAWA_MATCHING_V20_VERDICT.json"),(cert,"THEORY_CERTIFICATION_MATH_V20_VERDICT.json"),(posterior,"PORTAL_YUKAWA_POSTERIOR_V20_VERDICT.json"),(halo,"HALOSCOPE_37GHZ_LIMIT_COMPARE_V20_VERDICT.json"),(vac,"UV_VACUUM_ALIGNMENT_V20_VERDICT.json"),(rge2,"YUKAWA_RGE_2LOOP_V20_VERDICT.json"),(lik,"FCNC_EXACT_LIKELIHOOD_V20_VERDICT.json")):
            r=module.build_report(); module.ROOT.joinpath(name).write_text(json.dumps(r,indent=2,default=str)+"\n",encoding="utf-8")
        r=strict.build_report(); strict.ROOT.joinpath("STRICT_RG_AUDIT_V20_VERDICT.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    def test_conditional_region_is_not_unique(self):
        r=gaps.conditional_unique_cf(); self.assertTrue(r["flag"]["conditional_region_Cf"]); self.assertFalse(r["flag"]["conditional_unique_Cf"]); self.assertFalse(r["flag"]["unconditional_unique_Cf"])
    def test_fcnc_experiments_ray_and_spectrum_advance_without_closure(self):
        r=gaps.fcnc_absence_theorem(); self.assertTrue(r["flag"]["exact_qI_theorem_proved"]); self.assertTrue(r["flag"]["official_NA62_pointwise_limit_ingested"]); self.assertTrue(r["flag"]["generation_dependent_portal_point_excluded_by_NA62"]); self.assertTrue(r["flag"]["conditional_portal_ray_scanned"]); self.assertTrue(r["flag"]["conditional_NA62_survival_boundary_solved"]); self.assertTrue(r["flag"]["full_heavy_singular_spectrum_computed"]); self.assertTrue(r["flag"]["bare_D_not_physical_eigenmass"]); self.assertTrue(r["flag"]["lightest_heavy_equals_vS_boundary_solved"]); self.assertTrue(r["flag"]["ordered_threshold_point_passes_NA62"]); self.assertTrue(r["flag"]["ordered_threshold_point_passes_TWIST"]); self.assertFalse(r["flag"]["piecewise_threshold_matching_complete"]); self.assertTrue(r["flag"]["TWIST_three_published_asymmetry_limits_ingested"]); self.assertTrue(r["flag"]["generation_dependent_portal_point_passes_all_three_TWIST_cases"]); self.assertFalse(r["flag"]["continuous_TWIST_asymmetry_likelihood_implemented"]); self.assertFalse(r["flag"]["all_portal_parameter_space_excluded"]); self.assertFalse(r["flag"]["whole_v20_model_excluded"]); self.assertFalse(r["flag"]["component_specific_uv_chiral_currents_derived"]); self.assertLess(r["conditional_portal_ray"]["central_survival_boundary"]["lightest_heavy_over_vS"],1.0); self.assertAlmostEqual(r["physical_heavy_spectrum"]["ordered_threshold_boundary"]["lightest_heavy_singular_GeV"],6.313855e11,delta=1e5)
    def test_rg_completion_remains_open(self):
        r=gaps.yukawa_rg_global_fit(); self.assertTrue(r["flag"]["diagnostic_matrix_ODE_integrated"]); self.assertTrue(r["flag"]["pati_salam_one_loop_yukawa_layer_solved"]); self.assertTrue(r["flag"]["clebsch_threshold_matching_implemented"]); self.assertTrue(r["flag"]["piecewise_yukawa_chain_integrated"]); self.assertFalse(r["flag"]["actual_one_loop_matrix_beta_system_solved"]); self.assertFalse(r["flag"]["piecewise_threshold_yukawa_matching_complete"]); self.assertFalse(r["flag"]["piecewise_component_threshold_matching_complete"]); self.assertFalse(r["flag"]["two_loop_so10_complete"]); self.assertFalse(r["flag"]["published_210_tensor_contractions"])
    def test_detection_not_claimed(self):
        r=gaps.ghz_detection_package(); self.assertTrue(r["flag"]["lab_limit_comparison_executed"]); self.assertFalse(r["flag"]["real_37GHz_detection"])
    def test_certification_math_and_sector_posterior(self):
        r=gaps.certification_math_package(); self.assertTrue(r["flag"]["mathematical_obstruction_proved"]); self.assertTrue(r["flag"]["conditional_unique_Cf_under_named_axioms"]); self.assertTrue(r["flag"]["unique_Cf_under_vacuum_alignment_principle"]); self.assertFalse(r["flag"]["unconditional_unique_Cf"]); self.assertTrue(r["flag"]["portal_sector_posterior_derived"]); self.assertFalse(r["flag"]["full_portal_yukawa_posterior_derived"]); self.assertTrue(r["flag"]["exact_fcnc_br_likelihood_implemented"]); self.assertFalse(r["flag"]["full_correlated_experimental_likelihood_implemented"])
    def test_aggregate_report(self):
        r=gaps.build_report(); self.assertEqual(r["n_failed"],0); self.assertEqual(r["status"],"OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE"); self.assertTrue(r["gap_status"]["official_NA62_pointwise_limit"]); self.assertTrue(r["gap_status"]["conditional_NA62_yQ_survival_boundary"]); self.assertTrue(r["gap_status"]["full_heavy_singular_spectrum_on_ray"]); self.assertFalse(r["gap_status"]["bare_D_is_physical_eigenmass"]); self.assertTrue(r["gap_status"]["lightest_heavy_equals_vS_boundary"]); self.assertFalse(r["gap_status"]["piecewise_component_threshold_matching"]); self.assertTrue(r["gap_status"]["pati_salam_one_loop_yukawa_layer"]); self.assertTrue(r["gap_status"]["clebsch_threshold_matching_chain"]); self.assertTrue(r["gap_status"]["portal_sector_posterior_map"]); self.assertFalse(r["gap_status"]["full_multidimensional_portal_scan"]); self.assertFalse(r["gap_status"]["full_portal_yukawa_posterior"]); self.assertTrue(r["gap_status"]["TWIST_three_massless_asymmetry_benchmarks"]); self.assertFalse(r["gap_status"]["continuous_TWIST_asymmetry_likelihood"]); self.assertFalse(r["gap_status"]["all_portal_parameter_space_excluded"]); self.assertFalse(r["gap_status"]["full_common_scale_Yukawa_RG_fit"]); self.assertFalse(r["gap_status"]["two_loop_SO10_threshold_closure"]); self.assertFalse(r["gap_status"]["published_two_loop_SO10_210_contractions"]); self.assertTrue(r["gap_status"]["lab_37GHz_limit_comparison"]); self.assertFalse(r["gap_status"]["real_37GHz_detection"]); self.assertTrue(r["gap_status"]["uniqueness_obstruction_proved"]); self.assertTrue(r["gap_status"]["conditional_unique_Cf_under_named_axioms"]); self.assertTrue(r["gap_status"]["unique_Cf_under_vacuum_alignment_principle"]); self.assertTrue(r["gap_status"]["exact_fcnc_pointwise_ul_likelihood"]); self.assertFalse(r["gap_status"]["exact_unique_full_Ce_Cp_Cn"])

if __name__=="__main__": unittest.main()
