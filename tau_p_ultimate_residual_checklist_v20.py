#!/usr/bin/env python3
"""Correct the ultimate proton-lifetime checklist after EFJX source invalidation.

The previous checklist counted the alleged lambda4 lift of EFJX nulls and the
lambda4/EFJX decoupling result as closed residuals. Both depended on confusing
the Appendix-A gauge coupling g with superpotential gamma. They are now open
and replaced by the direct non-SUSY scalar tensor/Hessian task.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import lam4_potential_efjx_decoupling_v20 as lam4dec
import pq_null_lam4_portal_lift_v20 as pqnull
import scalar_alpha_flavour_nonuniqueness_v20 as alpha
import tau_p_hessian_residual_closure_v20 as hess

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_V20_VERDICT.json"
OUT_MD = ROOT / "TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_V20.md"


def build_report() -> dict[str, Any]:
    hess_rep = hess.build_report()
    pq_rep = pqnull.build_report()
    dec_rep = lam4dec.build_report()
    alpha_rep = alpha.build_report()
    if hess_rep.get("n_failed", 1) != 0:
        return {
            "status": "TAU_P_ULTIMATE_CHECKLIST_NOT_EXECUTED__HESS_FAILED",
            "n_failed": 1,
            "failures": ["tau_p_hessian_residual_closure"],
            "flag": {"exact_unique_proton_lifetime": False},
        }

    life = hess_rep["lifetime"]
    checks = {
        "hessian_stack_executes": True,
        "pq_portal_audit_executes": pq_rep.get("n_failed", 1) == 0,
        "decoupling_correction_executes": dec_rep.get("n_failed", 1) == 0,
        "scalar_alpha_nonuniqueness_retained": alpha_rep.get("n_failed", 1) == 0
        and alpha_rep.get("flag", {}).get("scalar_alpha_proven_nonunique_from_flavour"),
        "efjx_lift_not_counted_closed": not pq_rep.get("flag", {}).get(
            "pq_null_exact_kernel_lifted_by_lam4", True
        ),
        "efjx_decoupling_not_counted_closed": not dec_rep.get("flag", {}).get(
            "lam4_potential_raise_proved_spoiling", True
        ),
        "exact_unique_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    closed = {
        "scalar_alpha_not_unique_from_flavour": bool(
            alpha_rep.get("flag", {}).get("scalar_alpha_proven_nonunique_from_flavour")
        ),
        "efjx_gauge_gamma_source_collision_identified": True,
        "old_efjx_cgc_bound_withdrawn": True,
    }
    still_open = {
        "direct_phi_h_sigmabar_component_label_projection": True,
        "direct_scalar_mass_squared_block": True,
        "full_nonsusy_component_hessian": True,
        "physical_triplet_threshold_spectrum": True,
        "full_two_loop_threshold_running": True,
        "unique_flavour_and_interference_solution": True,
    }
    return {
        "status": (
            "TAU_P_CHECKLIST_CORRECTED__EFJX_CLOSURES_REOPENED"
            if not failures
            else "TAU_P_ULTIMATE_RESIDUAL_CHECKLIST_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "lifetime": life,
        "upstream_status": {
            "hessian_tau": hess_rep.get("status"),
            "pq_portal_correction": pq_rep.get("status"),
            "lam4_efjx_correction": dec_rep.get("status"),
            "scalar_alpha": alpha_rep.get("status"),
        },
        "certificate": {
            "residual_now_closed": closed,
            "residual_still_open": still_open,
            "c_cgc_needed_abs_approx": None,
            "interpretation": (
                "The former EFJX lambda4 lift and c_cgc decoupling closures are reopened. "
                "Any displayed historical lifetime is conditional and cannot become a "
                "unique model prediction until the direct scalar spectrum, thresholds, "
                "running, and flavour amplitudes are rebuilt."
            ),
        },
        "flag": {
            "ultimate_residual_checklist_folded": False,
            "all_post_hessian_residuals_closed": False,
            "EFJX_false_closures_reopened": True,
            "scalar_alpha_proven_nonunique_from_flavour": bool(closed[
                "scalar_alpha_not_unique_from_flavour"
            ]),
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The ultimate proton-lifetime checklist is corrected: EFJX/lambda4 closures "
            "and the c_cgc estimate are withdrawn. Exact unique proton lifetime remains open."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("# Corrected ultimate proton-lifetime checklist — v20\n\n" + report["verdict"] + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
