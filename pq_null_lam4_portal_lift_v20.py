#!/usr/bin/env python3
"""Withdraw the former EFJX PQ-null/lambda4 lift certificate.

The old certificate varied the Python parameter ``gamma`` inside Appendix-A
E/F/J/X matrices. In the Aulakh source those particular entries are gauge
coupling ``g`` and mix chiral fermions with gauginos. They do not describe a
non-supersymmetric scalar PQ-null mode lifted by lambda4.

The allowed operator Phi(210) H(10) Sigmabar(126bar) S still exists, but its
physical effect must be obtained from the direct scalar tensor map and the full
non-SUSY mass-squared Hessian.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct
import nonsusy_z17_pq_potential_filter_v20 as z17

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PQ_NULL_LAM4_PORTAL_LIFT_V20.json"
OUT_MD = ROOT / "PQ_NULL_LAM4_PORTAL_LIFT_V20.md"


def lam4_portal_charge_certificate() -> dict[str, Any]:
    counts = {"210_H": 1, "10_H": 1, "126bar_H": 1, "S": 1}
    totals = z17._total_charge(counts)
    allowed = z17._allowed(totals, require_x=True)
    bare_counts = {"210_H": 1, "10_H": 1, "126bar_H": 1}
    bare_totals = z17._total_charge(bare_counts)
    return {
        "operator": "210_H 10_H 126bar_H S",
        "charge_totals": totals,
        "allowed": allowed,
        "bare_cubic": {
            "operator": "210_H 10_H 126bar_H",
            "charge_totals": bare_totals,
            "allowed": z17._allowed(bare_totals, require_x=True),
        },
        "physical_matching": (
            "Direct non-SUSY scalar mixing lambda4 <S> T_<Phi>; no EFJX/gaugino "
            "gamma_eff identification is permitted."
        ),
    }


def build_report() -> dict[str, Any]:
    portal = lam4_portal_charge_certificate()
    tensor = direct.build_report()
    checks = {
        "quartic_portal_charge_allowed": bool(portal["allowed"]["all"]),
        "bare_cubic_pq_forbidden": not bool(portal["bare_cubic"]["allowed"]["PQ"]),
        "direct_tensor_map_executes": tensor.get("n_failed") == 0,
        "efjx_gaugino_route_withdrawn": True,
        "old_critical_lam4_withdrawn": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "PQ_LAM4_PORTAL_ALLOWED__EFJX_LIFT_CERTIFICATE_WITHDRAWN"
            if not failures
            else "PQ_LAM4_PORTAL_SOURCE_CORRECTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "portal": portal,
        "direct_tensor": {
            "status": tensor.get("status"),
            "map_shape": tensor.get("representation", {}).get("tensor_map_shape"),
            "fingerprints": tensor.get("fingerprints"),
        },
        "critical_lam4": {
            "found": False,
            "lam4_crit_abs": None,
            "withdrawn": True,
            "reason": "Former threshold was an EFJX gauge/gaugino threshold, not a scalar lambda4 threshold.",
        },
        "flag": {
            "portal_charge_allowed": bool(portal["allowed"]["all"]),
            "pq_null_exact_kernel_lifted_by_lam4": False,
            "selected_lam4_clears_gut_null_tol": False,
            "EFJX_lift_route_invalidated": True,
            "direct_scalar_tensor_map_available": tensor.get("n_failed") == 0,
            "physical_component_hessian_required": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "still_open": {
            "direct_component_mass_squared_spectrum": True,
            "full_nonsusy_hessian": True,
            "global_vacuum_and_boundedness": True,
        },
        "verdict": (
            "The lambda4 portal is charge-allowed, but the previous E/F/J/X PQ-null lift "
            "certificate is withdrawn because those g entries are gauge/gaugino mixings. "
            "The direct 10x126 scalar tensor is available; its full mass-squared insertion "
            "and vacuum analysis remain open."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("# Corrected lambda4 portal audit — v20\n\n" + report["verdict"] + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
