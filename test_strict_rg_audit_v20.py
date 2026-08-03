#!/usr/bin/env python3
import json, tempfile, unittest
from pathlib import Path
from unittest import mock
import channel_fcnc_rates_v20 as channel
import na62_pointwise_limit_v20 as na62
import twist_massless_limit_v20 as twist
import portal_constraint_ray_v20 as ray
import portal_boundary_heavy_spectrum_v20 as spectrum
import strict_rg_audit_v20 as strict

class StrictRGAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module,name in ((channel,"CHANNEL_FCNC_RATES_V20_VERDICT.json"),(na62,"NA62_POINTWISE_LIMIT_V20_VERDICT.json"),(twist,"TWIST_MASSLESS_LIMIT_V20_VERDICT.json"),(ray,"PORTAL_CONSTRAINT_RAY_V20_VERDICT.json"),(spectrum,"PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json")):
            report=module.build_report(); module.ROOT.joinpath(name).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    def test_current_artifacts_pass_honesty_audit(self):
        r=strict.build_report(); self.assertEqual(r["status"],"PASS"); self.assertEqual(r["n_failed"],0); self.assertEqual(r["classification"]["full_two_loop_so10_210_yukawa_system"],"OPEN"); self.assertEqual(r["classification"]["conditional_na62_yQ_survival_boundary"],"SOLVED_ON_ONE_FIXED_PORTAL_RAY"); self.assertEqual(r["classification"]["full_heavy_singular_spectrum"],"COMPUTED_ON_THE_FIXED_RAY"); self.assertEqual(r["classification"]["bare_D_mass_interpretation"],"NOT_A_PHYSICAL_EIGENMASS"); self.assertEqual(r["classification"]["piecewise_component_threshold_matching"],"OPEN"); self.assertEqual(r["classification"]["full_portal_parameter_space"],"OPEN"); self.assertEqual(r["classification"]["whole_model_exclusion"],"NOT_ESTABLISHED")
    def _write_minimal_artifacts(self, root:Path, *, matrix_closed:bool=False, whole_model_excluded:bool=False, correlated_likelihood:bool=False, twist_continuous:bool=False, twist_A_predicted:bool=False, boundary_solved:bool=True, full_portal_scan:bool=False, bare_D_physical:bool=False, spectrum_solved:bool=True, piecewise_complete:bool=False):
        (root/"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(json.dumps({"one_loop_matrix_yukawa_rge":{"flag":{"actual_one_loop_matrix_beta_system_solved":matrix_closed}}}))
        (root/"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(json.dumps({"flag":{}}))
        (root/"TWO_LOOP_SO10_210_V20_VERDICT.json").write_text(json.dumps({"flag":{},"fcnc_limits":{"flag":{}}}))
        (root/"CHANNEL_FCNC_RATES_V20_VERDICT.json").write_text(json.dumps({"flag":{"channel_level_amplitudes_implemented":True,"channel_level_branching_ratios_implemented":True,"left_right_mass_basis_rotations_implemented":True,"finite_model_fcnc_absence_proved":False,"unconditional_model_exclusion_claimed":False}}))
        (root/"NA62_POINTWISE_LIMIT_V20_VERDICT.json").write_text(json.dumps({"flag":{"official_pointwise_observed_limit_ingested":True,"offline_provenance_hash_verified":True,"generation_dependent_portal_point_excluded":True,"whole_v20_model_excluded":whole_model_excluded,"all_portal_parameter_space_excluded":False,"full_correlated_experimental_likelihood_implemented":correlated_likelihood,"component_specific_uv_chiral_currents_derived":False}}))
        (root/"TWIST_MASSLESS_LIMIT_V20_VERDICT.json").write_text(json.dumps({"flag":{"three_published_asymmetry_limits_ingested":True,"offline_provenance_hash_verified":True,"hierarchical_survives_all_three_TWIST_benchmarks":True,"generation_dependent_survives_all_three_TWIST_benchmarks":True,"continuous_arbitrary_A_likelihood_implemented":twist_continuous,"TWIST_asymmetry_predicted_from_uv_currents":twist_A_predicted,"full_muon_channel_likelihood_implemented":False,"whole_v20_model_excluded":whole_model_excluded}}))
        (root/"PORTAL_CONSTRAINT_RAY_V20_VERDICT.json").write_text(json.dumps({"flag":{"one_dimensional_conditional_ray_scanned":True,"all_crossings_searched":True,"central_NA62_survival_boundary_solved":boundary_solved,"form_factor_uncertainty_propagated":True,"reference_generation_dependent_point_excluded":True,"reference_generation_dependent_point_survives_TWIST":True,"full_portal_parameter_space_scanned":full_portal_scan,"portal_yukawa_posterior_derived":False,"component_specific_uv_chiral_currents_derived":False,"full_correlated_likelihood_implemented":False,"whole_v20_model_excluded":whole_model_excluded},"form_factor_boundary_band":{"f0_central":{"y_Q":2.42e-6}}}))
        (root/"PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json").write_text(json.dumps({"flag":{"bare_D_is_not_a_physical_mass_eigenvalue":not bare_D_physical,"full_three_heavy_singular_values_computed":spectrum_solved,"lightest_heavy_equals_vS_boundary_solved":spectrum_solved,"all_heavy_singular_values_above_vS_at_ordered_point":spectrum_solved,"ordered_point_survives_NA62":spectrum_solved,"ordered_point_survives_TWIST":spectrum_solved,"individual_Q_like_mass_eigenstate_uniquely_identified":False,"piecewise_threshold_matching_complete":piecewise_complete,"whole_v20_model_excluded":whole_model_excluded},"na62_survival_boundary":{"heavy_spectrum":{"bare_D_GeV":1.71e11,"lightest_heavy_singular_GeV":4.78e11,"lightest_heavy_over_vS":0.757}},"lightest_heavy_equals_vS_scan":{"unique_ordering_boundary":{"y_Q":6.31e-6,"bare_D_GeV":4.46e11,"lightest_heavy_singular_GeV":6.31e11,"lightest_heavy_over_vS":1.0}}}))
    def _audit(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self._write_minimal_artifacts(root,**kwargs)
            with mock.patch.object(strict,"ROOT",root): return strict.build_report()
    def test_rg_overclaim_fails(self):
        r=self._audit(matrix_closed=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("matrix_rge_open",r["failures"])
    def test_whole_model_exclusion_overclaim_fails(self):
        r=self._audit(whole_model_excluded=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("whole_model_not_rejected",r["failures"])
    def test_correlated_likelihood_overclaim_fails(self):
        r=self._audit(correlated_likelihood=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("correlated_likelihood_open",r["failures"])
    def test_twist_continuous_likelihood_overclaim_fails(self):
        r=self._audit(twist_continuous=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("twist_continuous_A_likelihood_open",r["failures"])
    def test_twist_A_prediction_overclaim_fails(self):
        r=self._audit(twist_A_predicted=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("twist_A_not_uv_predicted",r["failures"])
    def test_missing_boundary_fails(self):
        r=self._audit(boundary_solved=False); self.assertEqual(r["status"],"FAIL"); self.assertIn("central_na62_boundary_solved",r["failures"])
    def test_full_portal_scan_overclaim_fails(self):
        r=self._audit(full_portal_scan=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("full_portal_space_remains_open",r["failures"])
    def test_bare_D_mass_overclaim_fails(self):
        r=self._audit(bare_D_physical=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("bare_D_not_called_physical_mass",r["failures"])
    def test_missing_spectrum_boundary_fails(self):
        r=self._audit(spectrum_solved=False); self.assertEqual(r["status"],"FAIL"); self.assertIn("full_heavy_singular_spectrum_computed",r["failures"]); self.assertIn("lightest_heavy_ordering_boundary_solved",r["failures"])
    def test_piecewise_matching_overclaim_fails(self):
        r=self._audit(piecewise_complete=True); self.assertEqual(r["status"],"FAIL"); self.assertIn("spectrum_piecewise_matching_open",r["failures"])

if __name__=="__main__": unittest.main()
