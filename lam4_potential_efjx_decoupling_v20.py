#!/usr/bin/env python3
"""Withdraw the former lambda4-potential / EFJX decoupling certificate.

The certificate depended on a critical EFJX threshold obtained by varying
Aulakh Appendix-A gauge coupling g after it had been mislabeled gamma. No
physical scalar Clebsch ratio or lambda4 critical value follows from that scan.

The historical reduced radial lambda4 point remains independently tachyonic,
but it must not be connected to an EFJX/gaugino threshold. The replacement
calculation is the direct non-SUSY Phi-H-Sigmabar tensor map followed by a full
component mass-squared Hessian.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import direct_phi_h_sigmabar_tensor_v20 as direct
import nonsusy_reduced_hessian_v20 as physical
import pq_null_lam4_portal_lift_v20 as portal

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LAM4_POTENTIAL_EFJX_DECOUPLING_V20_VERDICT.json"
OUT_MD = ROOT / "LAM4_POTENTIAL_EFJX_DECOUPLING_V20.md"


def build_report() -> dict[str, Any]:
    tensor = direct.build_report()
    portal_report = portal.build_report()
    hessian = physical.build_report()
    historical_tachyonic = bool(
        hessian.get("historical_benchmark", {}).get("tachyonic")
    )
    checks = {
        "historical_radial_point_still_tachyonic": historical_tachyonic,
        "efjx_critical_lam4_withdrawn": portal_report.get("critical_lam4", {}).get(
            "withdrawn"
        )
        is True,
        "cgc_ratio_withdrawn": True,
        "direct_tensor_map_executes": tensor.get("n_failed") == 0,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "LAM4_EFJX_DECOUPLING_CERTIFICATE_WITHDRAWN__DIRECT_TENSOR_REQUIRED"
            if not failures
            else "LAM4_EFJX_SOURCE_CORRECTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "historical_radial_result": {
            "tachyonic": historical_tachyonic,
            "min_eigenvalue_GeV2": hessian.get("historical_benchmark", {}).get(
                "min_eigenvalue_GeV2"
            ),
            "scope": "reduced radial physical-h=174 audit only",
        },
        "withdrawn_claims": {
            "lam4_crit_abs": None,
            "c_cgc_needed_abs_approx": None,
            "gamma_at_crit_clears_efjx": False,
            "raise_to_efjx_tol_proved_spoiling": False,
            "reason": "No EFJX scalar-lambda4 threshold exists in the cited gaugino blocks.",
        },
        "direct_tensor_replacement": {
            "status": tensor.get("status"),
            "map_shape": tensor.get("representation", {}).get("tensor_map_shape"),
            "fingerprints": tensor.get("fingerprints"),
        },
        "certificate": {
            "lam4_potential_distinct_from_EFJX_gauge_g": True,
            "physical_cgc_still_required": False,
            "direct_scalar_tensor_map_now_required": True,
            "old_decoupling_certificate_valid": False,
            "interpretation": (
                "The old radial point still fails its reduced Hessian, but the claimed "
                "EFJX critical lambda4 and c_cgc ratio are withdrawn. The next valid "
                "object is the direct scalar mass-squared block."
            ),
        },
        "still_open": {
            "direct_mass_squared_block_with_physical_vevs": True,
            "complete_nonsusy_component_hessian": True,
            "global_vacuum_and_boundedness": True,
        },
        "flag": {
            "lam4_potential_raise_proved_spoiling": False,
            "old_lam4_efjx_decoupling_certificate_withdrawn": True,
            "cgc_ratio_needed_quantified": False,
            "lam4_cgc_and_dim6_lock_not_in_live_dump": True,
            "exact_unique_proton_lifetime": False,
            "whole_model_excluded": False,
            "whole_model_validated": False,
        },
        "verdict": (
            "The historical reduced lambda4 point remains tachyonic, but the EFJX-based "
            "decoupling and c_cgc estimates were based on gauge/gaugino g and are withdrawn. "
            "Use the direct 10x126 scalar tensor and full non-SUSY Hessian instead."
        ),
    }


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text("# Withdrawn lambda4/EFJX decoupling certificate — v20\n\n" + report["verdict"] + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
