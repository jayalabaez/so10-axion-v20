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
    pflag=push.get("one_loop_matrix_yukawa_rge",{}).get("flag",{})
    cflag=common.get("flag",{}); tflag=two.get("flag",{}); fflag=two.get("fcnc_limits",{}).get("flag",{})
    checks={
        "matrix_rge_not_overclaimed":not pflag.get("actual_one_loop_matrix_beta_system_solved",False),
        "matrix_coefficients_not_called_validated":not pflag.get("reference_validated_type_II_coefficients",False),
        "running_vevs_not_claimed":not pflag.get("running_vevs_included",False),
        "precision_common_scale_fit_not_overclaimed":not cflag.get("full_RG_global_fit_minimal",False),
        "piecewise_matching_not_overclaimed":not cflag.get("piecewise_threshold_yukawa_matching_complete",False),
        "two_loop_not_overclaimed":not tflag.get("two_loop_so10_complete",False),
        "reference_two_loop_not_overclaimed":not tflag.get("explicit_two_loop_yukawa_betas",False),
        "fcnc_likelihood_not_overclaimed":not fflag.get("experimental_FCNC_bound_applied",False),
        "finite_fcnc_absence_not_overclaimed":not fflag.get("actual_finite_model_fcnc_absence_proved",False),
    }
    failures=[n for n,ok in checks.items() if not ok]
    return {"status":"PASS" if not failures else "FAIL","n_checks":len(checks),"n_failed":len(failures),"failures":failures,
            "classification":{"portal_and_hierarchy_diagnostics":"AVAILABLE","broken_phase_matrix_ode":"DIAGNOSTIC_ONLY","precision_common_scale_fit":"OPEN","pati_salam_interval_matching":"OPEN","full_two_loop_so10_210_yukawa_system":"OPEN","channel_level_fcnc_likelihood":"OPEN"},
            "required_for_closure":["published-convention validated type-II matrix beta functions","running VEV/scalar-sector treatment","Pati-Salam Yukawa beta functions between M_I and M_GUT","explicit component threshold matching at M_I and M_GUT","reference-derived two-loop representation contractions and scalar-quartic terms","channel-level FCNC amplitudes, form factors, branching ratios, and experimental likelihoods"],
            "verdict":"The new calculations are useful diagnostic envelopes, but none of the precision matrix-RG, Pati-Salam matching, full two-loop SO(10)+210, or finite-model FCNC-likelihood blockers is closed."}

def write_markdown(r):
    lines=["# Strict RG / threshold / FCNC audit — v20","",f"**Status:** `{r['status']}`","","## Classification",""]
    lines += [f"- {k}: **{v}**" for k,v in r["classification"].items()]
    lines += ["","## Required for closure",""]+[f"- {x}" for x in r["required_for_closure"]]+["","## Verdict","",r["verdict"],""]
    return "\n".join(lines)

def main():
    r=build_report(); ROOT.joinpath("STRICT_RG_AUDIT_V20_VERDICT.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8"); ROOT.joinpath("STRICT_RG_AUDIT_V20.md").write_text(write_markdown(r),encoding="utf-8"); print(json.dumps(r,indent=2)); return 0 if r["n_failed"]==0 else 1
if __name__=="__main__": raise SystemExit(main())
