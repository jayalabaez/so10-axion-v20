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
    ps=read_json("PATI_SALAM_YUKAWA_MATCHING_V20_VERDICT.json")
    cert=read_json("THEORY_CERTIFICATION_MATH_V20_VERDICT.json")
    posterior=read_json("PORTAL_YUKAWA_POSTERIOR_V20_VERDICT.json")
    halo=read_json("HALOSCOPE_37GHZ_LIMIT_COMPARE_V20_VERDICT.json")
    vac=read_json("UV_VACUUM_ALIGNMENT_V20_VERDICT.json")
    rge2=read_json("YUKAWA_RGE_2LOOP_V20_VERDICT.json")
    lik=read_json("FCNC_EXACT_LIKELIHOOD_V20_VERDICT.json")
    p=push.get("one_loop_matrix_yukawa_rge",{}).get("flag",{})
    c=common.get("flag",{}); t=two.get("flag",{}); oldf=two.get("fcnc_limits",{}).get("flag",{})
    ch=channel.get("flag",{}); n=na62.get("flag",{}); w=twist.get("flag",{}); r=ray.get("flag",{}); s=spectrum.get("flag",{}); o=orientation.get("flag",{})
    psf=ps.get("flag",{}); cf=cert.get("flag",{}); pf=posterior.get("flag",{}); hf=halo.get("flag",{})
    vf=vac.get("flag",{}); rf=rge2.get("flag",{}); lf=lik.get("flag",{})
    counts=(orientation.get("scan") or {}).get("counts",{})
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
        "orientation_counts_reproduced":counts.get("n_grid_points")==5856 and counts.get("n_NA62_excluded")==5664 and counts.get("n_NA62_surviving")==192 and counts.get("n_TWIST_excluded")==0,
        "grid_fraction_not_probability":not o.get("grid_fraction_is_probability",True) and not counts.get("grid_fraction_is_probability",True),
        "full_three_family_orientation_open":not o.get("full_complex_three_family_orientation_scanned",False),
        "all_portal_magnitudes_phases_open":not o.get("all_portal_magnitudes_and_phases_scanned",False),
        "orientation_posterior_open":not o.get("portal_yukawa_posterior_derived",False),
        "orientation_component_currents_open":not o.get("component_specific_uv_chiral_currents_derived",False),
        "full_portal_space_remains_open":not r.get("full_portal_parameter_space_scanned",False),
        "ray_full_posterior_open":not r.get("portal_yukawa_posterior_derived",False),
        "ps_one_loop_yukawa_layer_solved":psf.get("pati_salam_one_loop_yukawa_layer_solved",False),
        "ps_not_using_so10_beta_on_interval":not psf.get("uses_so10_beta_across_PS_interval",True),
        "ps_component_matching_open":not psf.get("piecewise_component_threshold_matching_complete",False),
        "ps_two_loop_not_overclaimed":not psf.get("two_loop_so10_complete",False),
        "uniqueness_obstruction_proved":cf.get("mathematical_obstruction_proved",False),
        "conditional_axioms_unique_cf":cf.get("conditional_unique_Cf_under_named_axioms",False),
        "unconditional_unique_cf_open":not cf.get("unconditional_unique_Cf",False),
        "portal_sector_posterior_derived":pf.get("portal_sector_posterior_derived",False),
        "full_portal_posterior_open":not pf.get("full_portal_yukawa_posterior_derived",False),
        "sector_survival_fraction_not_probability":not pf.get("survival_fraction_is_probability",True),
        "lab_37ghz_compare_executed":hf.get("lab_limit_comparison_executed",False),
        "real_37ghz_detection_open":not hf.get("real_37GHz_detection",False),
        "vacuum_alignment_principle_stated":vf.get("vacuum_alignment_principle_stated",False),
        "vacuum_unique_cf_under_principle":vf.get("unique_Cf_under_vacuum_alignment_principle",False),
        "vacuum_unconditional_open":not vf.get("unconditional_unique_Cf",False),
        "vacuum_quartics_not_overclaimed":not vf.get("scalar_quartic_landscape_fully_minimized",False),
        "clebsch_threshold_matching_implemented":rf.get("clebsch_threshold_matching_implemented",False),
        "piecewise_yukawa_chain_integrated":rf.get("piecewise_yukawa_chain_integrated",False),
        "rge2_published_210_open":not rf.get("published_210_tensor_contractions",False),
        "rge2_two_loop_so10_open":not rf.get("two_loop_so10_complete",False),
        "exact_fcnc_br_implemented":lf.get("exact_kaon_branching_ratio_implemented",False) and lf.get("exact_muon_branching_ratio_implemented",False),
        "pointwise_ul_likelihood_implemented":lf.get("pointwise_ul_likelihood_implemented",False),
        "full_151_na62_open":not lf.get("full_151_point_NA62_curve_ingested",False),
        "full_correlated_likelihood_open_exact":not lf.get("full_correlated_experimental_likelihood_implemented",False),
        "whole_model_not_rejected":all(not x.get("whole_v20_model_excluded",False) for x in (n,w,r,s,o,pf,lf)),
        "all_portals_not_rejected":not n.get("all_portal_parameter_space_excluded",False) and not r.get("full_portal_parameter_space_scanned",False) and not o.get("all_portal_magnitudes_and_phases_scanned",False),
        "correlated_likelihood_open":not n.get("full_correlated_experimental_likelihood_implemented",False) and not r.get("full_correlated_likelihood_implemented",False),
        "component_uv_currents_open":not n.get("component_specific_uv_chiral_currents_derived",False) and not r.get("component_specific_uv_chiral_currents_derived",False) and not o.get("component_specific_uv_chiral_currents_derived",False),
        "finite_fcnc_absence_open":not ch.get("finite_model_fcnc_absence_proved",False),
        "unconditional_exclusion_open":not ch.get("unconditional_model_exclusion_claimed",False),
    }
    failures=[name for name,ok in checks.items() if not ok]
    extrema=((orientation.get("scan") or {}).get("extrema") or {})
    return {
        "status":"PASS" if not failures else "FAIL",
        "n_checks":len(checks),"n_failed":len(failures),"failures":failures,
        "classification":{
            "full_two_loop_so10_210_yukawa_system":"OPEN",
            "conditional_na62_yQ_survival_boundary":"SOLVED_ON_ONE_FIXED_PORTAL_RAY",
            "full_heavy_singular_spectrum":"COMPUTED_ON_THE_FIXED_RAY",
            "bare_D_mass_interpretation":"NOT_A_PHYSICAL_EIGENMASS",
            "piecewise_component_threshold_matching":"OPEN",
            "pati_salam_one_loop_yukawa_layer":"SOLVED_ON_MI_TO_MGUT",
            "clebsch_threshold_matching_chain":"IMPLEMENTED_WITH_FACTOR_MINUS_THREE",
            "published_two_loop_SO10_210_contractions":"OPEN",
            "unique_Cf_from_charges_alone":"IMPOSSIBLE_BY_THEOREM",
            "conditional_unique_Cf_under_named_axioms":"DERIVED",
            "unique_Cf_under_vacuum_alignment_principle":"DERIVED",
            "exact_fcnc_pointwise_ul_likelihood":"IMPLEMENTED_ON_VENDORED_ANCHORS",
            "full_151_point_correlated_NA62_likelihood":"OPEN",
            "portal_sector_posterior":"DISCRETE_GRID_ON_CONDITIONAL_SECTOR",
            "full_portal_yukawa_posterior":"OPEN",
            "complex_F1_F2_orientation_map":"SCANNED_AT_FIXED_NORM_AND_ORDERED_HEAVY_YQ",
            "na62_orientation_dependence":"EXCLUDED_AND_SURVIVING_ORIENTATIONS_FOUND",
            "twist_orientation_dependence":"ALL_5856_SAMPLED_ORIENTATIONS_BELOW_PUBLISHED_BENCHMARKS",
            "orientation_grid_fraction":"NOT_A_PROBABILITY_OR_UV_POSTERIOR",
            "full_complex_three_family_orientation":"OPEN",
            "full_portal_parameter_space":"OPEN",
            "lab_37ghz_limit_comparison":"EXECUTED__NO_DETECTION",
            "whole_model_exclusion":"NOT_ESTABLISHED"
        },
        "orientation_summary":{
            "n_grid_points":counts.get("n_grid_points"),
            "n_NA62_excluded":counts.get("n_NA62_excluded"),
            "n_NA62_surviving":counts.get("n_NA62_surviving"),
            "n_TWIST_excluded":counts.get("n_TWIST_excluded"),
            "min_NA62_ratio":((extrema.get("min_NA62_ratio") or {}).get("NA62_ratio")),
            "max_NA62_ratio":((extrema.get("max_NA62_ratio") or {}).get("NA62_ratio")),
            "max_TWIST_ratio":((extrema.get("max_TWIST_ratio") or {}).get("TWIST_ratio")),
            "grid_fraction_is_probability":False,
        },
        "required_for_closure":[
            "validated type-II matrix beta functions and running VEVs",
            "explicit component-level Pati-Salam and EW threshold matching of PQ currents",
            "reference-derived full two-loop SO(10)+210 representation contractions (SARAH/PyR@TE)",
            "component-specific left/right PQ currents after all thresholds",
            "full complex F1-F2-F3 orientation and all portal magnitudes/phases",
            "full UV portal-Yukawa prior/posterior beyond the conditional sector grid",
            "full 151-point correlated NA62 likelihood and continuous TWIST A likelihood",
            "real 36.6-37.6 GHz conversion data under the all-DM assumption",
            "a UV principle that uniquely fixes the full scalar-quartic landscape without extra axioms"
        ],
        "verdict":"Blueprint certification modules are fail-closed: vacuum alignment yields unique C_f only under a named principle; the piecewise Yukawa chain applies the −3 lepton Clebsch; exact FCNC BRs enter a pointwise UL likelihood on vendored anchors. Published SO(10)+210 two-loop contractions, full correlated NA62, and unconditional unique C_f remain open."
    }

def write_markdown(r):
    lines=["# Strict RG / threshold / FCNC audit — v20","",f"**Status:** `{r['status']}`","","## Classification",""]
    lines += [f"- {k}: **{v}**" for k,v in r["classification"].items()]
    lines += ["","## Orientation summary","",f"```json\n{json.dumps(r['orientation_summary'],indent=2)}\n```","","## Required for closure",""]+[f"- {x}" for x in r["required_for_closure"]]+["","## Verdict","",r["verdict"],""]
    return "\n".join(lines)

def main():
    r=build_report(); ROOT.joinpath("STRICT_RG_AUDIT_V20_VERDICT.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8"); ROOT.joinpath("STRICT_RG_AUDIT_V20.md").write_text(write_markdown(r),encoding="utf-8"); print(json.dumps(r,indent=2)); return 0 if r["n_failed"]==0 else 1
if __name__=="__main__": raise SystemExit(main())
