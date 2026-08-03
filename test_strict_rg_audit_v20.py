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
import portal_full_complex_orientation_sphere_v20 as sphere
import strict_rg_audit_v20 as strict

class StrictRGAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for module,name in (
            (channel,"CHANNEL_FCNC_RATES_V20_VERDICT.json"),
            (na62,"NA62_POINTWISE_LIMIT_V20_VERDICT.json"),
            (twist,"TWIST_MASSLESS_LIMIT_V20_VERDICT.json"),
            (ray,"PORTAL_CONSTRAINT_RAY_V20_VERDICT.json"),
            (spectrum,"PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json"),
            (orientation,"PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json"),
            (sphere,"PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json"),
        ):
            report=module.build_report()
            module.ROOT.joinpath(name).write_text(
                json.dumps(report,indent=2)+"\n",encoding="utf-8"
            )

    def test_current_artifacts_pass_honesty_audit(self):
        r=strict.build_report()
        self.assertEqual(r["status"],"PASS")
        self.assertEqual(r["n_failed"],0)
        self.assertEqual(
            r["classification"]["full_complex_three_family_orientation"],
            "HAAR_S5_LOW_DISCREPANCY_SAMPLE_AT_FIXED_NORM",
        )
        self.assertEqual(
            r["classification"]["chosen_geometric_NA62_excluded_fraction"],
            "0.9940185546875",
        )
        self.assertEqual(
            r["classification"]["geometric_fraction_interpretation"],
            "NOT_A_UV_PROBABILITY_OR_POSTERIOR",
        )
        self.assertEqual(
            r["classification"]["twist_orientation_dependence"],
            "ALL_16384_SAMPLED_ORIENTATIONS_BELOW_PUBLISHED_BENCHMARKS",
        )
        self.assertEqual(
            r["classification"]["joint_orientation_and_portal_magnitudes"],
            "OPEN",
        )
        self.assertEqual(r["classification"]["whole_model_exclusion"],"NOT_ESTABLISHED")

    def _write_minimal_artifacts(
        self,
        root:Path,
        *,
        matrix_closed=False,
        whole_model_excluded=False,
        correlated_likelihood=False,
        twist_continuous=False,
        boundary_solved=True,
        bare_D_physical=False,
        spectrum_solved=True,
        piecewise_complete=False,
        plane_grid_probability=False,
        sphere_sampled=True,
        sphere_count_delta=0,
        sphere_probability=False,
        all_portal_magnitudes=False,
        sphere_posterior=False,
        sphere_component_currents=False,
        sphere_continuous_likelihood=False,
    ):
        (root/"PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json").write_text(json.dumps({"one_loop_matrix_yukawa_rge":{"flag":{"actual_one_loop_matrix_beta_system_solved":matrix_closed}}}))
        (root/"COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json").write_text(json.dumps({"flag":{}}))
        (root/"TWO_LOOP_SO10_210_V20_VERDICT.json").write_text(json.dumps({"flag":{},"fcnc_limits":{"flag":{}}}))
        (root/"CHANNEL_FCNC_RATES_V20_VERDICT.json").write_text(json.dumps({"flag":{"channel_level_amplitudes_implemented":True,"channel_level_branching_ratios_implemented":True,"left_right_mass_basis_rotations_implemented":True,"finite_model_fcnc_absence_proved":False,"unconditional_model_exclusion_claimed":False}}))
        (root/"NA62_POINTWISE_LIMIT_V20_VERDICT.json").write_text(json.dumps({"flag":{"official_pointwise_observed_limit_ingested":True,"offline_provenance_hash_verified":True,"generation_dependent_portal_point_excluded":True,"whole_v20_model_excluded":whole_model_excluded,"all_portal_parameter_space_excluded":False,"full_correlated_experimental_likelihood_implemented":correlated_likelihood,"component_specific_uv_chiral_currents_derived":False}}))
        (root/"TWIST_MASSLESS_LIMIT_V20_VERDICT.json").write_text(json.dumps({"flag":{"three_published_asymmetry_limits_ingested":True,"offline_provenance_hash_verified":True,"hierarchical_survives_all_three_TWIST_benchmarks":True,"generation_dependent_survives_all_three_TWIST_benchmarks":True,"continuous_arbitrary_A_likelihood_implemented":twist_continuous,"TWIST_asymmetry_predicted_from_uv_currents":False,"full_muon_channel_likelihood_implemented":False,"whole_v20_model_excluded":whole_model_excluded}}))
        (root/"PORTAL_CONSTRAINT_RAY_V20_VERDICT.json").write_text(json.dumps({"flag":{"one_dimensional_conditional_ray_scanned":True,"all_crossings_searched":True,"central_NA62_survival_boundary_solved":boundary_solved,"form_factor_uncertainty_propagated":True,"reference_generation_dependent_point_excluded":True,"reference_generation_dependent_point_survives_TWIST":True,"full_portal_parameter_space_scanned":False,"portal_yukawa_posterior_derived":False,"component_specific_uv_chiral_currents_derived":False,"full_correlated_likelihood_implemented":False,"whole_v20_model_excluded":whole_model_excluded}}))
        (root/"PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json").write_text(json.dumps({"flag":{"bare_D_is_not_a_physical_mass_eigenvalue":not bare_D_physical,"full_three_heavy_singular_values_computed":spectrum_solved,"lightest_heavy_equals_vS_boundary_solved":spectrum_solved,"ordered_point_survives_NA62":spectrum_solved,"ordered_point_survives_TWIST":spectrum_solved,"individual_Q_like_mass_eigenstate_uniquely_identified":False,"piecewise_threshold_matching_complete":piecewise_complete,"whole_v20_model_excluded":whole_model_excluded}}))
        (root/"PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json").write_text(json.dumps({"flag":{"complex_F1_F2_orientation_plane_scanned":True,"ordered_heavy_boundary_used":True,"heavy_spectrum_orientation_invariant_at_fixed_norm":True,"NA62_has_excluded_grid_points":True,"NA62_has_surviving_grid_points":True,"TWIST_has_excluded_grid_points":False,"TWIST_has_surviving_grid_points":True,"grid_fraction_is_probability":plane_grid_probability,"all_portal_magnitudes_and_phases_scanned":False,"portal_yukawa_posterior_derived":False,"component_specific_uv_chiral_currents_derived":False,"whole_v20_model_excluded":whole_model_excluded},"scan":{"counts":{"n_grid_points":5856,"n_NA62_excluded":5664,"n_NA62_surviving":192,"n_TWIST_excluded":0,"grid_fraction_is_probability":plane_grid_probability},"extrema":{}}}))
        excluded=16286+sphere_count_delta
        surviving=16384-excluded
        (root/"PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json").write_text(json.dumps({
            "flag":{
                "full_complex_three_family_orientation_sphere_sampled":sphere_sampled,
                "rotationally_invariant_orientation_measure_explicit":True,
                "scrambled_sobol_replicates_executed":True,
                "NA62_has_excluded_samples":excluded>0,
                "NA62_has_surviving_samples":surviving>0,
                "TWIST_has_excluded_samples":False,
                "TWIST_has_surviving_samples":True,
                "geometric_fraction_is_uv_probability":sphere_probability,
                "all_portal_magnitudes_and_phases_scanned":all_portal_magnitudes,
                "portal_yukawa_posterior_derived":sphere_posterior,
                "component_specific_uv_chiral_currents_derived":sphere_component_currents,
                "continuous_experimental_likelihoods_implemented":sphere_continuous_likelihood,
                "whole_v20_model_excluded":whole_model_excluded,
            },
            "scan":{
                "aggregate_counts":{
                    "n_total_points":16384,
                    "n_NA62_excluded":excluded,
                    "n_NA62_surviving":surviving,
                    "n_TWIST_excluded":0,
                    "n_TWIST_surviving":16384,
                    "NA62_excluded_fraction_under_chosen_geometric_measure":excluded/16384,
                    "geometric_fraction_is_uv_probability":sphere_probability,
                },
                "replicate_fraction_diagnostics":{
                    "NA62_mean":0.9940185546875,
                    "NA62_min":0.99169921875,
                    "NA62_max":0.99658203125,
                    "replicate_spread_is_not_a_uv_posterior_uncertainty":True,
                },
                "sampled_extrema":{},
            },
        }))

    def _audit(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self._write_minimal_artifacts(root,**kwargs)
            with mock.patch.object(strict,"ROOT",root):
                return strict.build_report()

    def test_rg_overclaim_fails(self):
        self.assertIn("matrix_rge_open",self._audit(matrix_closed=True)["failures"])

    def test_whole_model_exclusion_overclaim_fails(self):
        self.assertIn("whole_model_not_rejected",self._audit(whole_model_excluded=True)["failures"])

    def test_correlated_likelihood_overclaim_fails(self):
        self.assertIn("correlated_likelihood_open",self._audit(correlated_likelihood=True)["failures"])

    def test_twist_continuous_likelihood_overclaim_fails(self):
        self.assertIn("twist_continuous_A_likelihood_open",self._audit(twist_continuous=True)["failures"])

    def test_missing_boundary_fails(self):
        self.assertIn("central_na62_boundary_solved",self._audit(boundary_solved=False)["failures"])

    def test_bare_D_mass_overclaim_fails(self):
        self.assertIn("bare_D_not_called_physical_mass",self._audit(bare_D_physical=True)["failures"])

    def test_piecewise_matching_overclaim_fails(self):
        self.assertIn("spectrum_piecewise_matching_open",self._audit(piecewise_complete=True)["failures"])

    def test_plane_grid_probability_overclaim_fails(self):
        self.assertIn("grid_fraction_not_probability",self._audit(plane_grid_probability=True)["failures"])

    def test_missing_full_sphere_sample_fails(self):
        self.assertIn("full_complex_sphere_sampled",self._audit(sphere_sampled=False)["failures"])

    def test_changed_sphere_count_fails(self):
        self.assertIn("sphere_counts_reproduced",self._audit(sphere_count_delta=-1)["failures"])
        self.assertIn("sphere_fraction_reproduced",self._audit(sphere_count_delta=-1)["failures"])

    def test_geometric_fraction_as_uv_probability_fails(self):
        failures=self._audit(sphere_probability=True)["failures"]
        self.assertIn("geometric_fraction_not_uv_probability",failures)

    def test_all_portal_magnitudes_complete_overclaim_fails(self):
        failures=self._audit(all_portal_magnitudes=True)["failures"]
        self.assertIn("all_portal_magnitudes_phases_open",failures)
        self.assertIn("full_portal_space_remains_open",failures)

    def test_sphere_posterior_overclaim_fails(self):
        failures=self._audit(sphere_posterior=True)["failures"]
        self.assertIn("sphere_posterior_open",failures)
        self.assertIn("portal_posterior_remains_open",failures)

    def test_component_current_overclaim_fails(self):
        self.assertIn("sphere_component_currents_open",self._audit(sphere_component_currents=True)["failures"])

    def test_continuous_likelihood_overclaim_fails(self):
        failures=self._audit(sphere_continuous_likelihood=True)["failures"]
        self.assertIn("sphere_continuous_likelihoods_open",failures)
        self.assertIn("correlated_likelihood_open",failures)

if __name__=="__main__": unittest.main()
