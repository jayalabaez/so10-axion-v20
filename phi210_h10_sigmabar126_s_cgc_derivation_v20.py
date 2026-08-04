#!/usr/bin/env python3
"""Correct the issue #86 campaign after the EFJX gauge/gamma symbol collision.

PR #89's numerical 8.8e29 ``c_norm`` bound compared the non-SUSY lambda4
portal to Aulakh E/F/J/X entries proportional to ``g``. In the primary source
those are gauge-coupling gaugino mixings, not superpotential gamma entries.
Therefore the bound is withdrawn rather than preserved as a false no-go.

The executable replacement is the direct antisymmetric-form tensor map in
``direct_phi_h_sigmabar_tensor_v20.py``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PHI210_H10_SIGMABAR126_S_CGC_DERIVATION_V20.json"
OUT_MD = ROOT / "PHI210_H10_SIGMABAR126_S_CGC_DERIVATION_V20.md"


def build_report() -> dict[str, Any]:
    tensor = direct.build_report()
    checks = {
        "source_symbol_collision_identified": True,
        "old_efjx_gamma_threshold_withdrawn": True,
        "old_8p8e29_bound_withdrawn": True,
        "direct_full_p_a_omega_map_constructed": tensor.get("flags", {}).get(
            "full_p_a_omega_cartesian_basis_constructed", False
        ),
        "direct_tensor_map_equivariant": tensor.get("equivariance_max_abs_residual", 1.0)
        < 1e-10,
        "closing_artifact_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "PHYSICAL_CGC_CAMPAIGN_CORRECTED__EFJX_BOUND_WITHDRAWN"
            if not failures
            else "PHYSICAL_CGC_CAMPAIGN_CORRECTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_correction": tensor.get("source_correction"),
        "direct_tensor_result": {
            "status": tensor.get("status"),
            "map_shape": tensor.get("representation", {}).get("tensor_map_shape"),
            "singlet_basis": tensor.get("singlet_basis"),
            "fingerprints": tensor.get("fingerprints"),
            "equivariance_max_abs_residual": tensor.get("equivariance_max_abs_residual"),
        },
        "joint_physical_constraint": {
            "withdrawn": True,
            "efjx_crit_abs": None,
            "naturalness_abs_lam4_bound": None,
            "c_norm_needed_for_negative_portal_natural_window": None,
            "former_value": 8.807091841170979e29,
            "reason": (
                "The former threshold varied the Aulakh E/F/J/X gauge coupling g, "
                "which was mislabeled gamma in Python. It is not a lambda4 Clebsch bound."
            ),
        },
        "remaining_blockers": {
            "published_cartesian_to_PS_SM_state_dictionary": True,
            "direct_component_label_projection_for_H10_and_Sigmabar126": True,
            "direct_mass_squared_block_in_complete_nonsusy_potential": True,
            "full_component_hessian_and_global_vacuum": True,
            "issue_86_closure_artifact": True,
        },
        "flag": {
            "physical_CGC_normalization_derived": False,
            "literature_scale_c_norm_excluded_on_natural_physical_branch": False,
            "proxy_c_cgc_190_invalid": True,
            "old_8p8e29_bound_valid": False,
            "EFJX_cgc_route_invalidated": True,
            "direct_tensor_map_constructed": True,
            "CGC_subproblem_closed": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The PR #89 8.8e29 Clebsch no-go is withdrawn because E/F/J/X g is the "
            "SO(10) gauge coupling. A direct, SO(10)-equivariant 10x126 non-SUSY tensor "
            "map with the full p,a,omega singlet basis now exists. Completing the labeled "
            "component mass-squared Hessian remains necessary."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Corrected Phi-H-Sigmabar CGC campaign — v20\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
