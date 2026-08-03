#!/usr/bin/env python3
"""Strict fail-closed audit for v20 RG, threshold, FCNC, and portal claims."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent

def read_json(name:str)->dict[str,Any]: return json.loads(ROOT.joinpath(name).read_text(encoding="utf-8"))

def build_report()->dict[str,Any]:
    push=read_json("PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json")
    common=read_json("COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json")
    two=read_json("TWO_LOOP_SO10_210_V20_VERDICT.json")
    channel=read_json("CHANNEL_FCNC_RATES_V20_VERDICT.json")
    na62=read_json("NA62_POINTWISE_LIMIT_V20_VERDICT.json")
    twist=read_json("TWIST_MASSLESS_LIMIT_V20_VERDICT.json")
    ray=read_json("PORTAL_CONSTRAINT_RAY_V20_VERDICT.json")
    spectrum=read_json("PORTAL_BOUNDARY_HEAVY_SPECTRUM_V20_VERDICT.json")
    orientation=read_json("PORTAL_FAMILY_ORIENTATION_MAP_V20_VERDICT.json")
    sphere=read_json("PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json")
    p=push.get("one_loop_matrix_yukawa_rge",{}).get("flag",{})
    c=common.get("flag",{}); t=two.get("flag",{}); oldf=two.get("fcnc_limits",{}).get("flag",{})
    ch=channel.get("flag",{}); n=na62.get("flag",{}); w=twist.get("flag",{}); r=ray.get("flag",{}); s=spectrum.get("flag",{}); o=orientation.get("flag",{}); q=sphere.get("flag",{})
    plane_counts=(orientation.get("scan") or {}).get("counts",{})
    sphere_scan=sphere.get("scan") or {}
    sphere_counts=sphere_scan.get("aggregate_counts",{})
    sphere_diag=sphere_scan.get("replicate_fraction_diagnostics",{})
    checks={
        "matrix_rge_open":not p.get("actual_one_loop_matrix_beta_system_solved",False),
        "matrix_coefficients_unvalidated":not p.get("reference_validated_type_II_coefficients",False),
        "running_vevs_open":not p.get("running_vevs_included",False),
        "precision_common_scale_fit_open":not c.get("full_RG_global_fit_minimal",False),
        "piecewise_matching_open":not c.get("piecewise_threshold_yukawa_matching_complete",False),
        "two_loop_open":not t.get("two_loop_so10_complete",False),
        "reference_two_loop_open":not t.get("explicit_two_loop_yukawa_betas",False),
        "legacy_fcnc_likelihood_not_claimed":not oldf.get("experimental_FCNC_bound_applied",False),
        "channel_amplitudes_implemented":ch.get("channel_level_amplitudes_implemented",False),
        "channel_branching_ratios_implemented":ch.get("channel_level_branching_ratios_implemented",False),
        "chiral_rotations_implemented":ch.get("left_right_mass_basis_rotations_implemented",False),
        "na62_limit_ingested":n.get("official_pointwise_observed_limit_ingested",False),
        "na62_provenance_verified":n.get("offline_provenance_hash_verified",False),
        "na62_counterexample_point_classified":n.get("generation_dependent_portal_point_excluded",False),
        "twist_three_limits_ingested":w.get("three_published_asymmetry_limits_ingested",False),
        "twist_provenance_verified":w.get("offline_provenance_hash_verified",False),
        "twist_hierarchical_survives":w.get("hierarchical_survives_all_three_TWIST_benchmarks",False),
        "twist_counterexample_survives":w.get("generation_dependent_survives_all_three_TWIST_benchmarks",False),
        "twist_continuous_A_likelihood_open":not w.get("continuous_arbitrary_A_likelihood_implemented",False),
        "twist_A_not_uv_predicted":not w.get("TWIST_asymmetry_predicted_from_uv_currents",False),
        "twist_full_likelihood_open":not w.get("full_muon_channel_likelihood_implemented",False),
        "conditional_portal_ray_scanned":r.get("one_dimensional_conditional_ray_scanned",False),
        "all_ray_crossings_searched":r.get("all_crossings_searched",False),
        "central_na62_boundary_solved":r.get("central_NA62_survival_boundary_solved",False),
        "form_factor_uncertainty_propagated":r.get("form_factor_uncertainty_propagated",False),
        "ray_reference_excluded_by_na62":r.get("reference_generation_dependent_point_excluded",False),
        "ray_reference_survives_twist":r.get("reference_generation_dependent_point_survives_TWIST",False),
        "full_heavy_singular_spectrum_computed":s.get("full_three_heavy_singular_values_computed",False),
        "bare_D_not_called_physical_mass":s.get("bare_D_is_not_a_physical_mass_eigenvalue",False),
        "lightest_heavy_ordering_boundary_solved":s.get("lightest_heavy_equals_vS_boundary_solved",False),
        "ordered_point_passes_na62":s.get("ordered_point_survives_NA62",False),
        "ordered_point_passes_twist":s.get("ordered_point_survives_TWIST",False),
        "Q_like_eigenstate_not_overidentified":not s.get("individual_Q_like_mass_eigenstate_uniquely_identified",False),
        "spectrum_piecewise_matching_open":not s.get("piecewise_threshold_matching_complete",False),
        "orientation_plane_scanned":o.get("complex_F1_F2_orientation_plane_scanned",False),
        "orientation_uses_ordered_heavy_boundary":o.get("ordered_heavy_boundary_used",False),
        "orientation_preserves_heavy_spectrum":o.get("heavy_spectrum_orientation_invariant_at_fixed_norm",False),
        "orientation_has_na62_excluded_points":o.get("NA62_has_excluded_grid_points",False),
        "orientation_has_na62_surviving_points":o.get("NA62_has_surviving_grid_points",False),
        "orientation_has_no_twist_excluded_points":not o.get("TWIST_has_excluded_grid_points",True) and o.get("TWIST_has_surviving_grid_points",False),
        "orientation_counts_reproduced":plane_counts.get("n_grid_points")==5856 and plane_counts.get("n_NA62_excluded")==5664 and plane_counts.get("n_NA62_surviving")==192 and plane_counts.get("n_TWIST_excluded")==0,
        "grid_fraction_not_probability":not o.get("grid_fraction_is_probability",True) and not plane_counts.get("grid_fraction_is_probability",True),
        "full_complex_sphere_sampled":q.get("full_complex_three_family_orientation_sphere_sampled",False),
        "sphere_measure_explicit":q.get("rotationally_invariant_orientation_measure_explicit",False),
        "sphere_scrambled_replicates_executed":q.get("scrambled_sobol_replicates_executed",False),
        "sphere_has_na62_excluded_samples":q.get("NA62_has_excluded_samples",False),
        "sphere_has_na62_surviving_samples":q.get("NA62_has_surviving_samples",False),
        "sphere_has_no_twist_excluded_samples":not q.get("TWIST_has_excluded_samples",True) and q.get("TWIST_has_surviving_samples",False),
        "sphere_counts_reproduced":sphere_counts.get("n_total_points")==16384 and sphere_counts.get("n_NA62_excluded")==16286 and sphere_counts.get("n_NA62_surviving")==98 and sphere_counts.get("n_TWIST_excluded")==0 and sphere_counts.get("n_TWIST_surviving")==16384,
        "sphere_fraction_reproduced":sphere_counts.get("NA62_excluded_fraction_under_chosen_geometric_measure")==0.9940185546875,
        "sphere_replicate_range_reproduced":sphere_diag.get("NA62_min")==0.99169921875 and sphere_diag.get("NA62_max")==0.99658203125 and sphere_diag.get("NA62_mean")==0.9940185546875,
        "geometric_fraction_not_uv_probability":not q.get("geometric_fraction_is_uv_probability",True) and not sphere_counts.get("geometric_fraction_is_uv_probability",True),
        "replicate_spread_not_uv_uncertainty":sphere_diag.get("replicate_spread_is_not_a_uv_posterior_uncertainty",False),
        "all_portal_magnitudes_phases_open":not q.get("all_portal_magnitudes_and_phases_scanned",False),
        "sphere_posterior_open":not q.get("portal_yukawa_posterior_derived",False),
        "sphere_component_currents_open":not q.get("component_specific_uv_chiral_currents_derived",False),
        "sphere_continuous_likelihoods_open":not q.get("continuous_experimental_likelihoods_implemented",False),
        "full_portal_space_remains_open":not r.get("full_portal_parameter_space_scanned",False) and not q.get("all_portal_magnitudes_and_phases_scanned",False),
        "portal_posterior_remains_open":not r.get("portal_yukawa_posterior_derived",False) and not q.get("portal_yukawa_posterior_derived",False),
        "whole_model_not_rejected":all(not x.get("whole_v20_model_excluded",False) for x in (n,w,r,s,o,q)),
        "all_portals_not_rejected":not n.get("all_portal_parameter_space_excluded",False) and not r.get("full_portal_parameter_space_scanned",False) and not q.get("all_portal_magnitudes_and_phases_scanned",False),
        "correlated_likelihood_open":not n.get("full_correlated_experimental_likelihood_implemented",False) and not r.get("full_correlated_likelihood_implemented",False) and not q.get("continuous_experimental_likelihoods_implemented",False),
        "component_uv_currents_open":not n.get("component_specific_uv_chiral_currents_derived",False) and not r.get("component_specific_uv_chiral_currents_derived",False) and not q.get("component_specific_uv_chiral_currents_derived",False),
        "finite_fcnc_absence_open":not ch.get("finite_model_fcnc_absence_proved",False),
        "unconditional_exclusion_open":not ch.get("unconditional_model_exclusion_claimed",False),
    }
    failures=[name for name,ok in checks.items() if not ok]
    plane_extrema=((orientation.get("scan") or {}).get("extrema") or {})
    sphere_extrema=sphere_scan.get("sampled_extrema") or {}
    return {
        "status":"PASS" if not failures else "FAIL",
        "n_checks":len(checks),"n_failed":len(failures),"failures":failures,
        "classification":{
            "full_two_loop_so10_210_yukawa_system":"OPEN",
            "conditional_na62_yQ_survival_boundary":"SOLVED_ON_ONE_FIXED_PORTAL_RAY",
            "full_heavy_singular_spectrum":"COMPUTED_ON_THE_FIXED_RAY",
            "bare_D_mass_interpretation":"NOT_A_PHYSICAL_EIGENMASS",
            "piecewise_component_threshold_matching":"OPEN",
            "complex_F1_F2_orientation_map":"SCANNED_AT_FIXED_NORM_AND_ORDERED_HEAVY_YQ",
            "full_complex_three_family_orientation":"HAAR_S5_LOW_DISCREPANCY_SAMPLE_AT_FIXED_NORM",
            "chosen_geometric_NA62_excluded_fraction":"0.9940185546875",
            "geometric_fraction_interpretation":"NOT_A_UV_PROBABILITY_OR_POSTERIOR",
            "na62_orientation_dependence":"EXCLUDED_AND_SURVIVING_ORIENTATIONS_FOUND",
            "twist_orientation_dependence":"ALL_16384_SAMPLED_ORIENTATIONS_BELOW_PUBLISHED_BENCHMARKS",
            "joint_orientation_and_portal_magnitudes":"OPEN",
            "full_portal_parameter_space":"OPEN",
            "whole_model_exclusion":"NOT_ESTABLISHED"
        },
        "orientation_summary":{
            "F1_F2_plane":{"n_grid_points":plane_counts.get("n_grid_points"),"n_NA62_excluded":plane_counts.get("n_NA62_excluded"),"n_NA62_surviving":plane_counts.get("n_NA62_surviving"),"min_NA62_ratio":((plane_extrema.get("min_NA62_ratio") or {}).get("NA62_ratio")),"max_NA62_ratio":((plane_extrema.get("max_NA62_ratio") or {}).get("NA62_ratio")),"grid_fraction_is_probability":False},
            "full_complex_S5":{"n_total_points":sphere_counts.get("n_total_points"),"n_NA62_excluded":sphere_counts.get("n_NA62_excluded"),"n_NA62_surviving":sphere_counts.get("n_NA62_surviving"),"n_TWIST_excluded":sphere_counts.get("n_TWIST_excluded"),"chosen_measure_excluded_fraction":sphere_counts.get("NA62_excluded_fraction_under_chosen_geometric_measure"),"replicate_min":sphere_diag.get("NA62_min"),"replicate_max":sphere_diag.get("NA62_max"),"sampled_min_NA62_ratio":((sphere_extrema.get("min_NA62_ratio") or {}).get("NA62_ratio")),"sampled_max_NA62_ratio":((sphere_extrema.get("max_NA62_ratio") or {}).get("NA62_ratio")),"sampled_max_TWIST_ratio":((sphere_extrema.get("max_TWIST_ratio") or {}).get("TWIST_ratio")),"geometric_fraction_is_uv_probability":False}
        },
        "required_for_closure":[
            "validated type-II matrix beta functions and running VEVs",
            "Pati-Salam RGEs and explicit component threshold matching",
            "reference-derived full two-loop representation contractions",
            "component-specific left/right PQ currents after all thresholds",
            "joint scan of y_Q, portal norm, lam_Q_R, lam_S_Q_Rbar, and remaining portal magnitudes/phases",
            "a derived UV portal-Yukawa prior or posterior",
            "continuous NA62/TWIST likelihood information"
        ],
        "verdict":"The full complex three-family orientation sphere is sampled at fixed norm and ordered-heavy y_Q using an explicit rotationally invariant measure. Under that chosen geometric measure 16286/16384 samples exceed NA62, but 98 survive and exact survivor anchors exist; all sampled orientations remain below TWIST. The 0.9940186 fraction is not a UV probability, and joint portal-magnitude inference plus threshold matching remain open."
    }

def write_markdown(r):
    lines=["# Strict RG / threshold / FCNC audit — v20","",f"**Status:** `{r['status']}`","","## Classification",""]
    lines += [f"- {k}: **{v}**" for k,v in r["classification"].items()]
    lines += ["","## Orientation summary","",f"```json\n{json.dumps(r['orientation_summary'],indent=2)}\n```","","## Required for closure",""]+[f"- {x}" for x in r["required_for_closure"]]+["","## Verdict","",r["verdict"],""]
    return "\n".join(lines)

def main():
    r=build_report(); ROOT.joinpath("STRICT_RG_AUDIT_V20_VERDICT.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8"); ROOT.joinpath("STRICT_RG_AUDIT_V20.md").write_text(write_markdown(r),encoding="utf-8"); print(json.dumps(r,indent=2)); return 0 if r["n_failed"]==0 else 1
if __name__=="__main__": raise SystemExit(main())
