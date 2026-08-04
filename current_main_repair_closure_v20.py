#!/usr/bin/env python3
"""Aggregate repaired scalar breakpoints with a signed invariant audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import mixed_rep_enlarged_floor_basis_v20 as signed_basis
import mixed_rep_hilbert_bfb_completion_v20 as bfb_basis
import mixed_rep_invariant_floor_audit_v20 as omission_audit
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
    bfb = bfb_basis.build_report()
    omissions = omission_audit.build_report()
    signed = signed_basis.build_report()
    hessian = nonsusy.build_report()
    orbit = gauge_orbit.build_report()

    execution_failures: list[str] = []
    for label, report in (
        ("base_audit", base),
        ("ps_rge", rge),
        ("bfb_basis", bfb),
        ("omission_audit", omissions),
        ("signed_basis", signed),
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
        "locking_modulus_companion": bool(
            bfb.get("flag", {}).get("modulus_locking_companion_added")
        ),
        "historical_invariant_claim_falsified": bool(
            omissions.get("flag", {}).get(
                "historical_complete_filtered_basis_claim_falsified"
            )
        ),
        "mechanical_floor37_rejected": bool(
            signed.get("flag", {}).get("mechanical_floor37_rejected")
        ),
        "signed_guaranteed_floor34_emitted": bool(
            signed.get("flag", {}).get("canonical_signed_floor_34_emitted")
            and signed.get("counts", {}).get("signed_guaranteed_floor_total") == 34
        ),
        "forbidden_210_10dag10_removed": bool(
            signed.get("flag", {}).get("forbidden_210_10dag10_removed")
        ),
        "physical_electroweak_vev_restored": bool(
            hessian.get("flag", {}).get("physical_electroweak_10_vev_used")
            and hessian.get("target_vevs_GeV", {}).get("H10_EW") == 174.0
        ),
        "radial_cross_quartics_restored": bool(
            hessian.get("flag", {}).get(
                "cross_quartics_from_radial_witness_included"
            )
        ),
        "arbitrary_precision_hessian": bool(
            hessian.get("flag", {}).get("arbitrary_precision_diagonalization_used")
        ),
        "zero_lam4_survival_point_positive": bool(
            hessian.get("survival_benchmark", {}).get("positive_definite")
        ),
        "historical_lam4_point_falsified": bool(
            hessian.get("historical_benchmark", {}).get("tachyonic")
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
        "complete_mixed_rep_invariant_enumeration": not bool(
            signed.get("flag", {}).get("full_unfiltered_molien_haar_series")
        ),
        "full_signed_floor34_tensor_projection_and_reminimization": not bool(
            hessian.get("radial_coverage", {}).get(
                "independent_tensor_channels_resolved_in_five_amplitudes"
            )
        ),
        "lambda4_ew_hierarchy_cancellation_or_tiny_coupling": bool(
            hessian.get("ew_portal_consistency", {}).get(
                "requires_cancellation_or_tiny_lam4"
            )
        ),
        "full_component_nonsusy_hessian": not bool(
            hessian.get("flag", {}).get("full_component_nonsusy_hessian")
        ),
        "full_component_global_vacuum_proof": not bool(
            hessian.get("flag", {}).get("full_component_global_vacuum_proof")
        ),
        "full_tensor_two_loop_betas": not bool(
            rge.get("flag", {}).get("full_component_tensor_betas")
        ),
        "live_sarah_or_pyrate_run": not bool(
            base_cert.get("live_sarah_or_pyrate_run")
        ),
        "exact_unique_proton_lifetime": not bool(
            base_cert.get("exact_unique_proton_lifetime")
        ),
        "selected_lam4_below_null_tolerance": not bool(
            base_cert.get("selected_lam4_clears_null_tolerance")
        ),
        "cal_G_soft_mode": bool(base_cert.get("cal_G_soft_mode_remaining")),
    }

    hard_failures = list(base.get("hard_theory_failures", []))
    audit_findings = [
        "historical invariant ledger is incomplete and contains a forbidden 210·10†·10 cubic",
        "mechanical augmented count 37 is rejected; conservative signed floor is 34",
    ]
    if resolved["historical_lam4_point_falsified"]:
        audit_findings.append(
            "historical lambda4=-kappa*M_I/M_GUT point is tachyonic at h=174 GeV"
        )
    if hessian.get("numerics", {}).get("float64_relative_error", 0.0) > 100.0:
        audit_findings.append(
            "float64 cannot resolve the electroweak Hessian mode across the GUT hierarchy"
        )

    if execution_failures:
        state = "EXECUTION_FAIL"
    elif hard_failures:
        state = "THEORY_FAIL"
    elif any(remaining.values()):
        state = "BLOCKED"
    elif all(resolved.values()):
        state = "PASS"
    else:
        state = "BLOCKED"

    return {
        "status": "CURRENT_MAIN_REPAIR_CLOSURE_EXECUTED",
        "overall_state": state,
        "execution_failures": execution_failures,
        "hard_theory_failures": hard_failures,
        "audit_findings": audit_findings,
        "resolved_breakpoints": resolved,
        "remaining_blockers": remaining,
        "numerical": {
            "historical_invariant_claimed_total": signed.get("counts", {}).get(
                "historical_ledger_claimed_total"
            ),
            "mechanical_augmented_total_rejected": signed.get("counts", {}).get(
                "mechanical_augmented_total_before_signed_corrections"
            ),
            "signed_guaranteed_invariant_floor": signed.get("counts", {}).get(
                "signed_guaranteed_floor_total"
            ),
            "missing_norm_quartics": omissions.get("counts", {}).get(
                "historical_missing_norm_products"
            ),
            "multiplicity_deficits": omissions.get("counts", {}).get(
                "historical_multiplicity_deficits"
            ),
            "physical_H10_vev_GeV": hessian.get("target_vevs_GeV", {}).get(
                "H10_EW"
            ),
            "survival_lam4": hessian.get("survival_benchmark", {}).get("lam4"),
            "survival_min_eigenvalue_GeV2": hessian.get(
                "survival_benchmark", {}
            ).get("min_eigenvalue_GeV2"),
            "survival_lightest_mass_GeV": hessian.get(
                "survival_benchmark", {}
            ).get("lightest_mass_GeV"),
            "historical_lam4": hessian.get("historical_benchmark", {}).get(
                "lam4"
            ),
            "historical_min_eigenvalue_GeV2": hessian.get(
                "historical_benchmark", {}
            ).get("min_eigenvalue_GeV2"),
            "historical_lam4_over_ew_bound": hessian.get(
                "ew_portal_consistency", {}
            ).get("historical_abs_lam4_over_bound"),
            "float64_hessian_relative_error": hessian.get("numerics", {}).get(
                "float64_relative_error"
            ),
            "goldstone_count": orbit.get("orbit", {}).get(
                "combined_orbit_rank_goldstones"
            ),
            "unbroken_stabilizer_dimension": orbit.get("orbit", {}).get(
                "combined_stabilizer_dimension"
            ),
            "so6_stabilizer_dimension": orbit.get("orbit", {}).get(
                "so6_stabilizer_dimension"
            ),
            "so4_stabilizer_dimension": orbit.get("orbit", {}).get(
                "so4_stabilizer_dimension"
            ),
        },
        "flags": {
            "whole_model_excluded": bool(base_cert.get("whole_model_excluded")),
            "whole_model_validated": state == "PASS",
            "executable_breakpoints_repaired": all(resolved.values()),
            "goldstone_problem_resolved": resolved["exact_goldstone_count_33"],
            "historical_basis_claim_falsified": resolved[
                "historical_invariant_claim_falsified"
            ],
            "mechanical_floor37_rejected": resolved[
                "mechanical_floor37_rejected"
            ],
            "historical_selected_point_excluded": resolved[
                "historical_lam4_point_falsified"
            ],
            "survival_parameter_region_exists": resolved[
                "zero_lam4_survival_point_positive"
            ],
            "full_component_problem_resolved": not remaining[
                "full_component_nonsusy_hessian"
            ],
        },
        "upstream_status": {
            "base_audit": base.get("overall_state"),
            "ps_rge": rge.get("status"),
            "bfb_basis": bfb.get("status"),
            "omission_audit": omissions.get("status"),
            "signed_basis": signed.get("status"),
            "nonsusy_hessian": hessian.get("status"),
            "gauge_orbit": orbit.get("status"),
        },
        "verdict": (
            "The executable scalar repairs now use a signed invariant audit: "
            "mechanical floor37 is rejected and the conservative guaranteed "
            "floor is 34. Pati-Salam running, locking boundedness, the exact "
            "33-Goldstone orbit, physical h=174 GeV high-precision Hessian, "
            "and a lambda4=0 survival point are executable. The historical "
            "lambda4 point is tachyonic. Full tensor minimization, RGEs, "
            "thresholds, and unique proton lifetime remain open."
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
        "## Audit findings",
        "",
    ]
    lines.extend(f"- {item}" for item in report["audit_findings"])
    lines.extend(["", "## Resolved", ""])
    lines.extend(
        f"- `{key}`: {value}"
        for key, value in report["resolved_breakpoints"].items()
    )
    lines.extend(["", "## Remaining blockers", ""])
    lines.extend(
        f"- `{key}`: {value}"
        for key, value in report["remaining_blockers"].items()
    )
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
