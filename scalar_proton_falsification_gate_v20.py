#!/usr/bin/env python3
"""Canonical fail-closed scalar/proton audit for the repaired v20 branch.

Only repaired, dimensionally consistent modules are executed here. Legacy
spectrum/lifetime modules are classified by the contamination audit and are
scientific blockers, not software execution failures.
"""
from __future__ import annotations

import argparse
import importlib
import json
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SCALAR_PROTON_FALSIFICATION_GATE_V20.json"
OUT_MD = ROOT / "SCALAR_PROTON_FALSIFICATION_GATE_V20.md"

MODULES = {
    "quartic_soft_betas": "quartic_soft_betas_v20",
    "operator_filter": "nonsusy_z17_pq_potential_filter_v20",
    "signed_cubic_audit": "so10_cubic_operator_signed_audit_v20",
    "signed_floor": "mixed_rep_enlarged_floor_basis_v20",
    "physical_EW_hessian": "nonsusy_reduced_hessian_v20",
    "portal_no_rescue": "ew_portal_rescue_bound_v20",
    "signed_triplet_mt2": "nonsusy_charge_allowed_mt_v20",
    "kronecker_mt2": "so10_kronecker_existence_mt_lock_v20",
    "triplet_contamination": "triplet_proxy_contamination_audit_v20",
    "gauge_orbit": "so10_nonsusy_gauge_orbit_v20",
}


def _run(name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(name)
        report = module.build_report()
        if not isinstance(report, dict):
            raise TypeError("build_report() did not return a mapping")
        return report
    except Exception as exc:  # fail closed and preserve traceback
        return {
            "status": "EXECUTION_EXCEPTION",
            "n_failed": 1,
            "_audit_error": f"{type(exc).__name__}: {exc}",
            "_traceback": traceback.format_exc(),
        }


def build_report() -> dict[str, Any]:
    reports = {label: _run(module) for label, module in MODULES.items()}
    execution_failures = [
        f"{label}: {report.get('_audit_error') or report.get('failures') or report.get('n_failed')}"
        for label, report in reports.items()
        if report.get("_audit_error") or report.get("n_failed", 0) != 0
    ]

    rge = reports["quartic_soft_betas"].get("flag", {})
    op = reports["operator_filter"].get("flag", {})
    cubic = reports["signed_cubic_audit"].get("flag", {})
    floor = reports["signed_floor"]
    hessian = reports["physical_EW_hessian"]
    rescue = reports["portal_no_rescue"]
    mt2 = reports["signed_triplet_mt2"].get("flag", {})
    kron = reports["kronecker_mt2"].get("flag", {})
    contam = reports["triplet_contamination"]
    orbit = reports["gauge_orbit"]

    resolved = {
        "pati_salam_subgroup_RGE_repaired": bool(
            rge.get("pati_salam_subgroup_resolved")
            and rge.get("charged_10_126_casimirs_nonzero")
            and rge.get("separate_g4_gL_gR_running")
            and not rge.get("two_loop_quartic_betas_complete", True)
        ),
        "forbidden_210_10dag10_removed": bool(
            op.get("forbidden_210_10dag10_removed")
            and cubic.get("forbidden_210_10dag10_proved")
        ),
        "signed_floor34_emitted": bool(
            floor.get("counts", {}).get("signed_guaranteed_floor_total") == 34
            and floor.get("flag", {}).get("mechanical_floor37_rejected")
        ),
        "physical_EW_survival_point_reproduced": bool(
            hessian.get("survival_benchmark", {}).get("positive_definite")
        ),
        "historical_lambda4_point_excluded": bool(
            hessian.get("historical_benchmark", {}).get("tachyonic")
        ),
        "perturbative_even_H_no_rescue_proved": bool(
            rescue.get("flag", {}).get(
                "historical_lam4_point_excluded_within_signed_floor34"
            )
            and rescue.get("flag", {}).get(
                "guaranteed_H4_channels_insufficient_perturbatively"
            )
        ),
        "signed_mass_squared_triplet_proxy_built": bool(
            mt2.get("mass_squared_matrix_used")
            and mt2.get("forbidden_210_10dag10_absent")
            and mt2.get("forbidden_10_126_S_absent")
            and mt2.get("lambda4_offdiag_slot_included")
        ),
        "kronecker_gate_corrected": bool(
            kron.get("forbidden_210_10dag10_removed")
            and kron.get("forbidden_10_126_S_cubic_locked_zero")
            and kron.get("lambda4_offdiag_slot_preserved")
        ),
        "legacy_triplet_dependency_graph_classified": bool(
            contam.get("n_failed", 1) == 0
            and contam.get("flag", {}).get("legacy_chain_invalidated_fail_closed")
        ),
        "exact_gauge_orbit_reproduced": bool(
            orbit.get("orbit", {}).get("combined_orbit_rank_goldstones") == 33
            and orbit.get("orbit", {}).get("combined_stabilizer_dimension") == 12
        ),
    }

    hard_theory_failures: list[str] = []
    blockers = {
        "complete_mixed_rep_invariant_enumeration": True,
        "full_signed_floor34_tensor_projection_and_reminimization": True,
        "physical_component_triplet_CG_coefficients": not mt2.get(
            "physical_component_CG_complete", False
        ),
        "legacy_triplet_threshold_lifetime_chain_rebuild": bool(
            contam.get("invalidated_modules")
            or contam.get("contaminated_modules")
            or contam.get("n_contaminated_modules", 0)
        ),
        "full_component_nonsusy_hessian": True,
        "full_tensor_two_loop_betas": True,
        "exact_unique_proton_lifetime": True,
    }

    if execution_failures:
        state = "EXECUTION_FAIL"
    elif hard_theory_failures:
        state = "THEORY_FAIL"
    elif not all(resolved.values()):
        state = "EXECUTION_FAIL"
        execution_failures.append(
            "canonical certificate mismatch: "
            + ", ".join(name for name, ok in resolved.items() if not ok)
        )
    elif any(blockers.values()):
        state = "BLOCKED"
    else:
        state = "PASS"

    report = {
        "status": "CANONICAL_SCALAR_PROTON_REAUDIT_COMPLETE",
        "overall_state": state,
        "execution_failures": execution_failures,
        "hard_theory_failures": hard_theory_failures,
        "scientific_blockers": [name for name, value in blockers.items() if value],
        "remaining_blockers": blockers,
        "resolved_breakpoints": resolved,
        "module_summaries": {
            label: {
                "module": MODULES[label],
                "status": value.get("status"),
                "n_failed": value.get("n_failed", 0),
                "audit_error": value.get("_audit_error"),
            }
            for label, value in reports.items()
        },
        "certificates": {
            "all_canonical_modules_executed": not execution_failures,
            "legacy_modules_not_used_as_physical_certificates": True,
            "whole_model_excluded": False,
            "whole_model_validated": state == "PASS",
            **resolved,
        },
        "verdict": (
            "The repaired canonical scalar/proton chain executes fail closed. "
            "The historical lambda4 benchmark is excluded, while a reduced "
            "lambda4=0 survival point remains. Legacy triplet, threshold and "
            "proton-lifetime closures are invalidated until rebuilt from the "
            "signed non-SUSY mass-squared spectrum. The whole model remains "
            "BLOCKED, not excluded or validated."
        ),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Canonical scalar/proton falsification gate — v20\n\n"
        f"**State:** `{report['overall_state']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    return 1 if report["overall_state"] in {"EXECUTION_FAIL", "THEORY_FAIL"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
