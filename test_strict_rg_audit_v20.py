#!/usr/bin/env python3
import json, tempfile, unittest
from pathlib import Path
from unittest import mock
import channel_fcnc_rates_v20 as channel
import na62_pointwise_limit_v20 as na62
import twist_massless_limit_v20 as twist
import portal_constraint_ray_v20 as ray
import portal_boundary_heavy_spectrum_v20 as spectrum
import portal_family_orientation_map_v20 as orientation
import strict_rg_audit_v20 as strict

class StrictRGAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module,name in ((channel,"CHANNEL_FCNC_RATES_V20_VERDICT.json"),(na62,"NA62_POINTWISE_LIMIT_V20_VERDICT.json"),(twist,"TWIST_MASSLESS_LIMIT_V20_VERDICT.json"),(ray,"PORTAL_CONSTRAINT_RAY_V20_VERDICT.json"),(spectrum,"PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json"),(orientation,"PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json")):
            report=module.build_report(); module.ROOT.joinpath(name).write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    def test_current_artifacts_pass_honesty_audit(self):
        r=strict.build_report(); self.assertEqual(r["status"],"PASS"); self.assertEqual(r["n_failed"],0)
        self.assertEqual(r["classification"]["complex_F1_F2_orientation_map"],"SCANNED_AT_FIXED_NORM_AND_ORDERED_HEAVY_YQ")
        self.assertEqual(r["classification"]["na62_orientation_dependence"],"EXCLUDED_AND_SURVIVING_ORIENTATIONS_FOUND")
        self.assertEqual(r["classification"]["twist_orientation_dependence"],"ALL_5856_SAMPLED_ORIENTATIONS_BELOW_PUBLISHED_BENCHMARKS")
        self.assertEqual(r["classification"]["orientation_grid_fraction"],"NOT_A_PROBABILITY_OR_UV_POSTERIOR")
        self.assertEqual(r["classification"]["full_complex_three_family_orientation"],"OPEN")
        self.assertEqual(r["classification"]["whole_model_exclusion"],"NOT_ESTABLISHED")
    def _write_minimal_artifacts(self, root:Path, *, matrix_closed=False, whole_model_excluded=False, correlated_likelihood=False, twist_continuous=False, twist_A_predicted=False, boundary_solved=True, full_portal_scan=False, bare_D_physical=False, spectrum_solved=True, piecewise_complete=False, grid_probability=False, full_three_family=False, orientation_posterior=False, orientation_mixed=True):
        (root/"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(json.dumps({"one_loop_matrix_yukawa_rge":{"flag":{"actual_one_loop_matrix_beta_system_solved":matrix_closed}}}))
        (root/"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(json.dumps({"flag":{}}))
        (root/"TWO_LOOP_SO10_210_V20_VERDICT.json").write_text(json.dumps({"flag":{},"fcnc_limits":{"flag":{}}}))
        (root/"CHANNEL_FCNC_RATES_V20_VERDICT.json").write_text(json.dumps({"flag":{"channel_level_amplitudes_implemented":True,"channel_level_branching_ratios_implemented":True,"left_right_mass_basis_rotations_implemented":True,"finite_model_fcnc_absence_proved":False,"unconditional_model_exclusion_claimed":False}}))
        (root/"NA62_POINTWISE_LIMIT_V20_VERDICT.json").write_text(json.dumps({"flag":{"official_pointwise_observed_limit_ingested":True,"offline_provenance_hash_verified":True,"generation_dependent_portal_point_excluded":True,"whole_v20_model_excluded":whole_model_excluded,"all_portal_parameter_space_excluded":False,"full_correlated_experimental_likelihood_implemented":correlated_likelihood,"component_specific_uv_chiral_currents_derived":False}}))
        (root/"TWIST_MASSLESS_LIMIT_V20_VERDICT.json").write_text(json.dumps({"flag":{"three_published_asymmetry_limits_ingested":True,"offline_provenance_hash_verified":True,"hierarchical_survives_all_three_TWIST_benchmarks":True,"generation_dependent_survives_all_three_TWIST_benchmarks":True,"continuous_arbitrary_A_likelihood_implemented":twist_continuous,"TWIST_asymmetry_predicted_from_uv_currents":twist_A_predicted,"full_muon_channel_likelihood_implemented":False,"whole_v20_model_excluded":whole_model_excluded}}))
        (root/"PORTAL_CONSTRAINT_RAY_V20_VERDICT.json").write_text(json.dumps({"flag":{"one_dimensional_conditional_ray_scanned":True,"all_crossings_searched":True,"central_NA62_survival_boundary_solved":boundary_solved,"form_factor_uncertainty_propagated":True,"reference_generation_dependent_point_excluded":True,"reference_generation_dependent_point_survives_TWIST":True,"full_portal_parameter_space_scanned":full_portal_scan,"portal_yukawa_posterior_derived":False,"component_specific_uv_chiral_currents_derived":False,"full_correlated_likelihood_implemented":False,"whole_v20_model_excluded":whole_model_excluded}}))
        (root/"PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json").write_text(json.dumps({"flag":{"bare_D_is_not_a_physical_mass_eigenvalue":not bare_D_physical,"full_three_heavy_singular_values_computed":spectrum_solved,"lightest_heavy_equals_vS_boundary_solved":spectrum_solved,"ordered_point_survives_NA62":spectrum_solved,"ordered_point_survives_TWIST":spectrum_solved,"individual_Q_like_mass_eigenstate_uniquely_identified":False,"piecewise_threshold_matching_complete":piecewise_complete,"whole_v20_model_excluded":whole_model_excluded}}))
        excluded=5664 if orientation_mixed else 5856; surviving=192 if orientation_mixed else 0
        (root/"PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json").write_text(json.dumps({"flag":{"complex_F1_F2_orientation_plane_scanned":True,"ordered_heavy_boundary_used":True,"heavy_spectrum_orientation_invariant_at_fixed_norm":True,"NA62_has_excluded_grid_points":excluded>0,"NA62_has_surviving_grid_points":surviving>0,"TWIST_has_excluded_grid_points":False,"TWIST_has_surviving_grid_points":True,"grid_fraction_is_probability":grid_probability,"full_complex_three_family_orientation_scanned":full_three_family,"all_portal_magnitudes_and_phases_scanned":full_portal_scan,"portal_yukawa_posterior_derived":orientation_posterior,"component_specific_uv_chiral_currents_derived":False,"whole_v20_model_excluded":whole_model_excluded},"scan":{"counts":{"n_grid_points":5856,"n_NA62_excluded":excluded,"n_NA62_surviving":surviving,"n_TWIST_excluded":0,"grid_fraction_is_probability":grid_probability},"extrema":{}}}))
    def _audit(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self._write_minimal_artifacts(root,**kwargs)
            with mock.patch.object(strict,"ROOT",root): return strict.build_report()
    def test_rg_overclaim_fails(self): self.assertIn("matrix_rge_open",self._audit(matrix_closed=True)["failures"])
    def test_whole_model_exclusion_overclaim_fails(self): self.assertIn("whole_model_not_rejected",self._audit(whole_model_excluded=True)["failures"])
    def test_correlated_likelihood_overclaim_fails(self): self.assertIn("correlated_likelihood_open",self._audit(correlated_likelihood=True)["failures"])
    def test_twist_continuous_likelihood_overclaim_fails(self): self.assertIn("twist_continuous_A_likelihood_open",self._audit(twist_continuous=True)["failures"])
    def test_missing_boundary_fails(self): self.assertIn("central_na62_boundary_solved",self._audit(boundary_solved=False)["failures"])
    def test_bare_D_mass_overclaim_fails(self): self.assertIn("bare_D_not_called_physical_mass",self._audit(bare_D_physical=True)["failures"])
    def test_piecewise_matching_overclaim_fails(self): self.assertIn("spectrum_piecewise_matching_open",self._audit(piecewise_complete=True)["failures"])
    def test_grid_probability_overclaim_fails(self): self.assertIn("grid_fraction_not_probability",self._audit(grid_probability=True)["failures"])
    def test_full_three_family_overclaim_fails(self): self.assertIn("full_three_family_orientation_open",self._audit(full_three_family=True)["failures"])
    def test_orientation_posterior_overclaim_fails(self): self.assertIn("orientation_posterior_open",self._audit(orientation_posterior=True)["failures"])
    def test_missing_na62_survivors_fails(self): self.assertIn("orientation_has_na62_surviving_points",self._audit(orientation_mixed=False)["failures"])

if __name__=="__main__": unittest.main()
