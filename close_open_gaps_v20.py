#!/usr/bin/env python3
"""Aggregate v20 open gaps after RG, channel-FCNC, NA62, TWIST, and portal-ray audits."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
import numpy as np
import full_fermion_matching_v20 as matching
import physical_cf_matching_v20 as physical
import portal_tensors_abcd_v20 as portals
ROOT=Path(__file__).resolve().parent

def _read(name:str)->dict[str,Any]: return json.loads(ROOT.joinpath(name).read_text(encoding="utf-8"))
def hierarchical_universal_block(lam:float=0.2):
    return portals.build_abcd(portals.PortalCouplings(y_P=1.0,y_R=1.0,y_Q=1.0,lam_Q_F=(lam,lam,lam),lam_Q_R=0.0,lam_S_Q_Rbar=0.0,y_F_Pbar=(0,0,0),y_F_Rbar=(0,0,0)))

def conditional_unique_cf():
    block=hierarchical_universal_block(); current=matching.portal_current_match(block["A"],block["B"],block["C"],block["D"])
    gf=_read("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json"); best=gf.get("display_best") or gf["best_point"]
    viable=[float(x) for x in gf.get("viable_tan_beta_samples",[])] or [float(best["tan_beta"])]
    rows=[matching.coefficients_at_tan_beta(x) for x in viable]; rep=matching.coefficients_at_tan_beta(float(best["tan_beta"]))
    suppressed=float(current["projected_shift_norm"])<1e-3 and float(current["projected_off_diagonal_norm"])<1e-8
    return {"status":"CONDITIONAL_CF_REGION__NOT_UNIQUE_FULL_V20","representative_best_fit_point":{"tan_beta":float(best["tan_beta"]),"v_r_GeV":float(best["v_r_GeV"]),"chi2":float(best["chi2"]),"C_e":rep["C_e"],"C_p_central":rep["C_p_central"],"C_n_central":rep["C_n_central"]},"portal_diagnostics":{"projected_shift_norm":float(current["projected_shift_norm"]),"projected_off_diagonal_norm":float(current["projected_off_diagonal_norm"]),"hierarchically_suppressed":suppressed},"viable_tan_beta_samples":viable,"viable_region_envelope":{k:[min(float(r[k]) for r in rows),max(float(r[k]) for r in rows)] for k in ("C_e","C_p_central","C_n_central")},"flag":{"conditional_region_Cf":suppressed,"conditional_unique_Cf":False,"unconditional_unique_Cf":False,"unique_tan_beta_under_principle":False},"reason_not_unique":"Portal assumptions and a finite scan do not derive one UV point or one tan(beta)."}

def fcnc_absence_theorem():
    block=hierarchical_universal_block(); current=matching.portal_current_match(block["A"],block["B"],block["C"],block["D"]); q=np.asarray(current["Q_projected"],dtype=complex); dep=float(np.linalg.norm(q-np.trace(q)/3*np.eye(3)))
    bases=physical.flavour_mass_bases(); le=physical.rotate_to_basis(q,bases["U_e"]); up=physical.rotate_to_basis(q,bases["U_uL"]); dn=physical.rotate_to_basis(q,bases["U_dL"]); qo=max(float(up["off_diagonal_norm"]),float(dn["off_diagonal_norm"])); suppressed=max(float(le["off_diagonal_norm"]),qo)<1e-8
    bad=portals.build_abcd(portals.PortalCouplings(y_Q=1e-6,lam_Q_F=(1.0,0.01,0.0),lam_Q_R=0.3,lam_S_Q_Rbar=0.2)); bc=matching.portal_current_match(bad["A"],bad["B"],bad["C"],bad["D"]); bl=physical.rotate_to_basis(np.asarray(bc["Q_projected"],dtype=complex),bases["U_e"])
    channel=_read("CHANNEL_FCNC_RATES_V20_VERDICT.json"); na62=_read("NA62_POINTWISE_LIMIT_V20_VERDICT.json"); twist=_read("TWIST_MASSLESS_LIMIT_V20_VERDICT.json"); ray=_read("PORTAL_CONSTRAINT_RAY_V20_VERDICT.json")
    h=channel["hierarchical_benchmark"]; c=channel["generation_dependent_counterexample"]
    nh=na62["hierarchical_universal_benchmark"]; nc=na62["generation_dependent_counterexample"]
    th=twist["hierarchical_universal_benchmark"]; tc=twist["generation_dependent_counterexample"]
    boundary=ray["form_factor_boundary_band"]["f0_central"]
    return {
        "status":"EXACT_QI_THEOREM__CHANNEL_RATES_NA62_TWIST_AND_CONDITIONAL_RAY_APPLIED__MODEL_CLOSURE_OPEN",
        "exact_theorem":"If Q_proj=qI exactly, every unitary mass-basis rotation preserves qI and tree-level axion FCNCs vanish.",
        "finite_hierarchical_benchmark":{"departure_from_q_identity":dep,"lepton_off_diagonal_norm":float(le["off_diagonal_norm"]),"quark_off_diagonal_norm":qo,"exactly_scalar_to_1e_14":dep<=1e-14,"numerically_suppressed_to_1e_8":suppressed,"BR_mu_to_e_a":float(h["mu_to_e_a"]["branching_ratio"]),"BR_K_to_pi_a":float(h["K_to_pi_a"]["branching_ratio"]),"NA62_observed_limit_90cl":float(nh["observed_br_upper_limit_90cl"]),"NA62_pointwise_excluded":bool(nh["pointwise_excluded_90cl"]),"TWIST_survives_A_minus1_0_plus1":bool(th["survives_all_three_published_hypotheses"]),"channel_level_amplitudes_implemented":True,"channel_level_branching_ratios_implemented":True},
        "generation_dependent_counterexample":{"lepton_off_diagonal_norm":float(bl["off_diagonal_norm"]),"fcnc_possible":bool(bl["fcnc_possible"]),"BR_mu_to_e_a":float(c["mu_to_e_a"]["branching_ratio"]),"BR_K_to_pi_a":float(c["K_to_pi_a"]["branching_ratio"]),"NA62_observed_limit_90cl":float(nc["observed_br_upper_limit_90cl"]),"prediction_over_NA62_limit":float(nc["prediction_over_limit"]),"NA62_pointwise_excluded":bool(nc["pointwise_excluded_90cl"]),"TWIST_survives_A_minus1_0_plus1":bool(tc["survives_all_three_published_hypotheses"]),"TWIST_strongest_safety_factor":float(tc["strongest_published_benchmark"]["safety_factor_limit_over_prediction"])},
        "conditional_portal_ray":{"status":ray["status"],"fixed_texture":ray["central_scan"]["configuration"]["texture"],"central_survival_boundary":{"y_Q":float(boundary["y_Q"]),"M_Q_GeV":float(boundary["M_Q_GeV"]),"M_Q_over_vS":float(boundary["M_Q_over_vS"]),"BR_mu_to_e_a":float(boundary["BR_mu_to_e_a"]),"TWIST_ratio":float(boundary["TWIST_ratio"])},"form_factor_boundary_band":ray["form_factor_boundary_band"],"full_portal_parameter_space_scanned":False},
        "na62_artifact":{"status":na62["status"],"source":na62["source"],"interpretation":na62["interpretation"]},
        "twist_artifact":{"status":twist["status"],"source":twist["source"],"interpretation":twist["interpretation"]},
        "channel_rate_artifact":{"status":channel["status"],"references":channel["conventions"],"remaining_for_closure":channel["remaining_for_closure"]},
        "flag":{"exact_qI_theorem_proved":True,"actual_finite_model_fcnc_absence_proved":False,"actual_finite_model_fcnc_suppressed":suppressed,"channel_level_amplitudes_implemented":True,"channel_level_branching_ratios_implemented":True,"official_NA62_pointwise_limit_ingested":True,"hierarchical_benchmark_passes_NA62":not nh["pointwise_excluded_90cl"],"generation_dependent_portal_point_excluded_by_NA62":nc["pointwise_excluded_90cl"],"conditional_portal_ray_scanned":ray["flag"]["one_dimensional_conditional_ray_scanned"],"conditional_NA62_survival_boundary_solved":ray["flag"]["central_NA62_survival_boundary_solved"],"form_factor_uncertainty_propagated":ray["flag"]["form_factor_uncertainty_propagated"],"TWIST_three_published_asymmetry_limits_ingested":True,"hierarchical_benchmark_passes_all_three_TWIST_cases":th["survives_all_three_published_hypotheses"],"generation_dependent_portal_point_passes_all_three_TWIST_cases":tc["survives_all_three_published_hypotheses"],"continuous_TWIST_asymmetry_likelihood_implemented":False,"all_portal_parameter_space_excluded":False,"whole_v20_model_excluded":False,"full_correlated_experimental_likelihood_implemented":False,"component_specific_uv_chiral_currents_derived":False,"proved_for_arbitrary_portals":False},
        "reason_not_closed":"A conditional NA62 boundary is solved on one fixed portal ray. NA62 excludes the original point while the heavier-Q side survives, and TWIST does not exclude the corresponding muon rates. The whole model remains open because the multidimensional UV portal distribution, component currents, and continuous likelihoods are not fixed."
    }

def yukawa_rg_global_fit():
    push=_read("PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json"); common=_read("COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json"); two=_read("TWO_LOOP_SO10_210_V20_VERDICT.json"); strict=_read("STRICT_RG_AUDIT_V20_VERDICT.json"); gf=_read("GLOBAL_FLAVOUR_FIT_V20_VERDICT.json"); best=gf["best_point"]
    return {"status":"RG_DIAGNOSTICS_AVAILABLE__PRECISION_MATRIX_AND_TWO_LOOP_OPEN","proxy_best_point":{"v_r_GeV":float(best["v_r_GeV"]),"chi2":float(best["chi2"]),"tan_beta":float(best["tan_beta"]),"viable_chi2_lt_30":bool(best["viable_chi2_lt_30"])},"diagnostic_artifacts":{"push":push["status"],"common":common["status"],"two_loop":two["status"],"strict_audit":strict["status"]},"flag":{"effective_power_law_proxy_applied":True,"diagnostic_matrix_ODE_integrated":True,"actual_one_loop_matrix_beta_system_solved":False,"reference_validated_type_II_coefficients":False,"running_vevs_included":False,"piecewise_threshold_yukawa_matching_complete":False,"full_RG_global_fit_minimal":False,"two_loop_so10_complete":False},"missing_for_closure":strict["required_for_closure"],"reason_not_closed":strict["verdict"]}

def ghz_detection_package():
    return {"status":"SOFTWARE_INJECTION_RECOVERY_PASS__NO_EXPERIMENTAL_DETECTION","flag":{"software_injection_recovery_certified":True,"real_37GHz_detection":False,"experimental_discovery":False},"hard_falsifier":"A real null at g_agamma<=2.3e-14 GeV^-1 over 36.6-37.6 GHz kills the all-DM benchmark."}

def build_report():
    cf=conditional_unique_cf(); f=fcnc_absence_theorem(); rg=yukawa_rg_global_fit(); det=ghz_detection_package()
    checks={"conditional_region_available":cf["flag"]["conditional_region_Cf"],"unique_cf_not_overclaimed":not cf["flag"]["unconditional_unique_Cf"],"channel_fcnc_rates_implemented":f["flag"]["channel_level_amplitudes_implemented"] and f["flag"]["channel_level_branching_ratios_implemented"],"na62_limit_ingested":f["flag"]["official_NA62_pointwise_limit_ingested"],"excluded_portal_point_recorded":f["flag"]["generation_dependent_portal_point_excluded_by_NA62"],"conditional_ray_scanned":f["flag"]["conditional_portal_ray_scanned"],"conditional_boundary_solved":f["flag"]["conditional_NA62_survival_boundary_solved"],"form_factor_uncertainty_propagated":f["flag"]["form_factor_uncertainty_propagated"],"twist_limits_ingested":f["flag"]["TWIST_three_published_asymmetry_limits_ingested"],"twist_counterexample_survives":f["flag"]["generation_dependent_portal_point_passes_all_three_TWIST_cases"],"continuous_twist_likelihood_not_overclaimed":not f["flag"]["continuous_TWIST_asymmetry_likelihood_implemented"],"whole_model_not_overclaimed":not f["flag"]["whole_v20_model_excluded"],"finite_fcnc_not_overclaimed":not f["flag"]["actual_finite_model_fcnc_absence_proved"],"matrix_rg_not_overclaimed":not rg["flag"]["actual_one_loop_matrix_beta_system_solved"],"two_loop_not_overclaimed":not rg["flag"]["two_loop_so10_complete"],"detection_not_claimed":not det["flag"]["real_37GHz_detection"]}
    fail=[n for n,o in checks.items() if not o]
    return {"status":"OPEN_GAPS_AUDITED__NO_UNCONDITIONAL_FULL_CLOSURE" if not fail else "OPEN_GAP_AUDIT_FAILED","n_checks":len(checks),"n_failed":len(fail),"failures":fail,"conditional_cf_region":cf,"fcnc_analysis":f,"yukawa_rg_analysis":rg,"ghz37_package":det,"gap_status":{"exact_unique_full_Ce_Cp_Cn":False,"conditional_aligned_Cf_region":True,"channel_level_FCNC_rates":True,"official_NA62_pointwise_limit":True,"generation_dependent_kaon_portal_point_excluded":True,"conditional_portal_ray_scan":True,"conditional_NA62_yQ_survival_boundary":True,"full_multidimensional_portal_scan":False,"TWIST_three_massless_asymmetry_benchmarks":True,"generation_dependent_muon_portal_point_survives_TWIST_benchmarks":True,"continuous_TWIST_asymmetry_likelihood":False,"all_portal_parameter_space_excluded":False,"finite_model_tree_FCNC_absence_proved":False,"full_correlated_experimental_FCNC_likelihood":False,"full_common_scale_Yukawa_RG_fit":False,"two_loop_SO10_threshold_closure":False,"real_37GHz_detection":False},"verdict":"A conditional NA62 survival boundary is solved on the displayed generation-dependent portal ray. The original point is excluded, while y_Q above the crossing survives on that ray; the muon channel remains below the published TWIST benchmark limits. This is not a full portal-space, whole-model, or discovery result."}

def write_markdown(r): return f"# Open-gap audit — v20\n\n**Status:** `{r['status']}`\n\n{r['verdict']}\n"
def main():
    r=build_report(); ROOT.joinpath("OPEN_GAPS_CLOSURE_V20_VERDICT.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8"); ROOT.joinpath("OPEN_GAPS_CLOSURE_V20.md").write_text(write_markdown(r),encoding="utf-8"); print(json.dumps(r,indent=2)); return 0 if r["n_failed"]==0 else 1
if __name__=="__main__": raise SystemExit(main())
