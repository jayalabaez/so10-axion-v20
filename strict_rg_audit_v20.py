#!/usr/bin/env python3
"""Strict fail-closed audit for v20 RG, threshold, and FCNC claims."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent

def read_json(name:str)->dict[str,Any]:
    return json.loads(ROOT.joinpath(name).read_text(encoding="utf-8"))

def build_report()->dict[str,Any]:
    push=read_json("PUSH_PHENOMENOLOGY_LIMITS_V20_VERDICT.json")
    common=read_json("COMMON_SCALE_SO10_YUKAWA_V20_VERDICT.json")
    two=read_json("TWO_LOOP_SO10_210_V20_VERDICT.json")
    channel=read_json("CHANNEL_FCNC_RATES_V20_VERDICT.json")
    na62=read_json("NA62_POINTWISE_LIMIT_V20_VERDICT.json")
    p=push.get("one_loop_matrix_yukawa_rge",{}).get("flag",{})
    c=common.get("flag",{}); t=two.get("flag",{}); oldf=two.get("fcnc_limits",{}).get("flag",{}); ch=channel.get("flag",{}); n=na62.get("flag",{})
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
        "counterexample_point_classified":n.get("generation_dependent_portal_point_excluded",False),
        "whole_model_not_rejected":not n.get("whole_v20_model_excluded",False),
        "all_portals_not_rejected":not n.get("all_portal_parameter_space_excluded",False),
        "correlated_likelihood_open":not n.get("full_correlated_experimental_likelihood_implemented",False),
        "component_uv_currents_open":not n.get("component_specific_uv_chiral_currents_derived",False),
        "finite_fcnc_absence_open":not ch.get("finite_model_fcnc_absence_proved",False),
        "unconditional_exclusion_open":not ch.get("unconditional_model_exclusion_claimed",False),
    }
    failures=[name for name,ok in checks.items() if not ok]
    return {
        "status":"PASS" if not failures else "FAIL",
        "n_checks":len(checks),"n_failed":len(failures),"failures":failures,
        "classification":{
            "portal_and_hierarchy_diagnostics":"AVAILABLE",
            "broken_phase_matrix_ode":"DIAGNOSTIC_ONLY",
            "precision_common_scale_fit":"OPEN",
            "pati_salam_interval_matching":"OPEN",
            "full_two_loop_so10_210_yukawa_system":"OPEN",
            "channel_level_fcnc_formulae":"IMPLEMENTED",
            "na62_pointwise_observed_upper_limit":"IMPLEMENTED",
            "generation_dependent_counterexample":"ABOVE_90CL_UPPER_LIMIT_UNDER_COMMON_CURRENT_ASSUMPTION",
            "hierarchical_universal_benchmark":"BELOW_NA62_POINTWISE_LIMIT",
            "component_specific_uv_chiral_matching":"OPEN",
            "full_correlated_fcnc_likelihoods":"OPEN",
            "whole_model_exclusion":"NOT_ESTABLISHED"
        },
        "required_for_closure":[
            "validated type-II matrix beta functions and running VEVs",
            "Pati-Salam RGEs and explicit component threshold matching",
            "reference-derived full two-loop representation contractions",
            "component-specific left/right PQ currents after all thresholds",
            "complete portal-Yukawa posterior scan across the NA62 curve",
            "TWIST angular likelihood and any released NA62 nuisance correlations"
        ],
        "verdict":"The official NA62 zero-mass observed upper limit is applied. The selected generation-dependent portal point is above that limit, while the hierarchical benchmark is below it. This does not establish whole-model exclusion because the UV portal distribution and component-specific currents are not fixed."
    }

def write_markdown(r):
    lines=["# Strict RG / threshold / FCNC audit — v20","",f"**Status:** `{r['status']}`","","## Classification",""]
    lines += [f"- {k}: **{v}**" for k,v in r["classification"].items()]
    lines += ["","## Required for closure",""]+[f"- {x}" for x in r["required_for_closure"]]+["","## Verdict","",r["verdict"],""]
    return "\n".join(lines)

def main():
    r=build_report(); ROOT.joinpath("STRICT_RG_AUDIT_V20_VERDICT.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8"); ROOT.joinpath("STRICT_RG_AUDIT_V20.md").write_text(write_markdown(r),encoding="utf-8"); print(json.dumps(r,indent=2)); return 0 if r["n_failed"]==0 else 1
if __name__=="__main__": raise SystemExit(main())
