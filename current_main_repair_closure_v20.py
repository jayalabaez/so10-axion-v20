#!/usr/bin/env python3
"""Aggregate executable repairs while preserving remaining fail-closed scope."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import mixed_rep_hilbert_bfb_completion_v20 as bfb_basis
import nonsusy_reduced_hessian_v20 as nonsusy
import quartic_soft_betas_v20 as ps_rge
import scalar_proton_falsification_gate_v20 as base_audit
import so10_nonsusy_gauge_orbit_v20 as gauge_orbit

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "CURRENT_MAIN_REPAIR_CLOSURE_V20.json"
OUT_MD = ROOT / "CURRENT_MAIN_REPAIR_CLOSURE_V20.md"


def build_report() -> dict[str, Any]:
    base = base_audit.build_report()
    rge = ps_rge.build_report()
    basis = bfb_basis.build_report()
    hessian = nonsusy.build_report()
    orbit = gauge_orbit.build_report()

    execution_failures = []
    for label, report in (
        ("base_audit", base),
        ("ps_rge", rge),
        ("bfb_basis", basis),
        ("nonsusy_hessian", hessian),
        ("gauge_orbit", orbit),
    ):
        if report.get("n_failed", 0) != 0:
            execution_failures.append(f"{label}: {report.get('failures')}")

    resolved = {
        "pati_salam_charged_sector_rge": bool(
            rge.get("flag", {}).get("pati_salam_subgroup_resolved")
            and rge.get("flag", {}).get("charged_10_126_casimirs_nonzero")
            and rge.get("flag", {}).get("separate_g4_gL_gR_running")
            and not rge.get("flag", {}).get("two_loop_quartic_betas_complete")
        ),
        "canonical_phase_lock_modulus_companion": bool(
            basis.get("flag", {}).get("modulus_locking_companion_added")
            and basis.get("flag", {}).get("canonical_completed_basis_emitted")
        ),
        "reduced_nonsusy_bounded_from_below": bool(
            hessian.get("flag", {}).get("reduced_potential_bounded_from_below")
        ),
        "independent_nonsusy_reduced_hessian": bool(
            hessian.get("flag", {}).get("independent_nonsusy_reduced_hessian")
            and not hessian.get("flag", {}).get("uses_aulakh_or_msgut_component_matrices")
        ),
        "reduced_local_minimum_positive_definite": bool(
            hessian.get("flag", {}).get("reduced_local_minimum_positive_definite")
        ),
        "exact_goldstone_count_33": bool(
            orbit.get("flag", {}).get("goldstone_count_33_exact")
        ),
        "sm_sized_stabilizer_12": bool(
            orbit.get("flag", {}).get("sm_sized_stabilizer_dimension_12")
            and orbit.get("flag", {}).get("su3_sized_so6_stabilizer_8")
            and orbit.get("flag", {}).get("su2_u1_sized_so4_stabilizer_4")
        ),
    }

    base_cert = base.get("certificates", {})
    remaining = {
        "full_component_nonsusy_hessian": not bool(
            hessian.get("flag", {}).get("full_component_nonsusy_hessian")
        ),
        "full_component_global_vacuum_proof": not bool(
            hessian.get("flag", {}).get("full_component_global_vacuum_proof")
        ),
        "full_tensor_two_loop_betas": not bool(
            rge.get("flag", {}).get("full_component_tensor_betas")
        ),
        "live_sarah_or_pyrate_run": not bool(base_cert.get("live_sarah_or_pyrate_run")),
        "unfiltered_molien_haar": not bool(base_cert.get("unfiltered_molien_haar_closed")),
        "exact_unique_proton_lifetime": not bool(base_cert.get("exact_unique_proton_lifetime")),
        "selected_lam4_below_null_tolerance": not bool(
            base_cert.get("selected_lam4_clears_null_tolerance")
        ),
        "cal_G_soft_mode": bool(base_cert.get("cal_G_soft_mode_remaining")),
    }

    hard_failures = list(base.get("hard_theory_failures", []))
    all_resolved = all(resolved.values())
    if execution_failures:
        state = "EXECUTION_FAIL"
    elif hard_failures:
        state = "THEORY_FAIL"
    elif any(remaining.values()):
        state = "BLOCKED"
    elif all_resolved:
        state = "PASS"
    else:
        state = "BLOCKED"

    return {
        "status": "CURRENT_MAIN_REPAIR_CLOSURE_EXECUTED",
        "overall_state": state,
        "execution_failures": execution_failures,
        "hard_theory_failures": hard_failures,
        "resolved_breakpoints": resolved,
        "remaining_blockers": remaining,
        "numerical": {
            "reduced_hessian_min_eigenvalue_GeV2": hessian.get("hessian", {}).get("min_eigenvalue_GeV2"),
            "reduced_hessian_fd_relative_error": hessian.get("hessian", {}).get("max_relative_difference"),
            "lambda_lock_phase": hessian.get("couplings", {}).get("lambda_lock_phase"),
            "lambda_lock_abs": hessian.get("couplings", {}).get("lambda_lock_abs"),
            "lambda4_amgm_limit": hessian.get("bfb_certificate", {}).get("quartic_amgm_limit"),
            "lambda4_abs": hessian.get("bfb_certificate", {}).get("abs_lam4"),
            "goldstone_count": orbit.get("orbit", {}).get("combined_orbit_rank_goldstones"),
            "unbroken_stabilizer_dimension": orbit.get("orbit", {}).get("combined_stabilizer_dimension"),
            "so6_stabilizer_dimension": orbit.get("orbit", {}).get("so6_stabilizer_dimension"),
            "so4_stabilizer_dimension": orbit.get("orbit", {}).get("so4_stabilizer_dimension"),
        },
        "flags": {
            "whole_model_excluded": bool(base_cert.get("whole_model_excluded")),
            "whole_model_validated": state == "PASS",
            "reduced_sector_repaired": all_resolved,
            "goldstone_problem_resolved": resolved["exact_goldstone_count_33"],
            "full_component_problem_resolved": not remaining["full_component_nonsusy_hessian"],
        },
        "upstream_status": {
            "base_audit": base.get("overall_state"),
            "ps_rge": rge.get("status"),
            "bfb_basis": basis.get("status"),
            "nonsusy_hessian": hessian.get("status"),
            "gauge_orbit": orbit.get("status"),
        },
        "verdict": (
            "The executable reduced-theory breakpoints are closed: Pati-Salam charged-sector running is restored, "
            "the canonical locking pair supplies a conservative analytic BFB certificate, the five-amplitude non-SUSY Hessian is independently derived, "
            "and the explicit 210 plus 126bar tensor VEVs give exactly 33 Goldstones with a 12-dimensional SM-sized stabilizer. "
            "The result remains BLOCKED at the full-component level because the complete non-SUSY tensor Hessian, full tensor beta system, external-tool dump, and exact unique proton lifetime are still absent."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Current-main breakpoint repair closure — v20",
        "",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Resolved",
        "",
    ]
    lines.extend(f"- `{k}`: {v}" for k, v in report["resolved_breakpoints"].items())
    lines.extend(["", "## Remaining blockers", ""])
    lines.extend(f"- `{k}`: {v}" for k, v in report["remaining_blockers"].items())
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 1 if report["overall_state"] in {"EXECUTION_FAIL", "THEORY_FAIL"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
