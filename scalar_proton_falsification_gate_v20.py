#!/usr/bin/env python3
"""Independent fail-closed re-audit of the current v20 scalar/proton stack.

This gate is intentionally stricter than checking that each upstream module
returns ``n_failed == 0``.  A green software test means that the implemented
calculation is internally reproducible; it does not prove that the adopted
SO(10) invariant basis, non-SUSY component spectrum, vacuum catalogue, or
proton-decay amplitude is complete.

The whole theory may be marked FAIL only by a demonstrated mathematical
contradiction or by an exact, complete proton-decay calculation below the
experimental bound.  Missing external tensor validation, live SARAH/PyR@TE,
near-null modes, or non-unique flavour inputs remain BLOCKED.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SCALAR_PROTON_FALSIFICATION_GATE_V20.json"
OUT_MD = ROOT / "SCALAR_PROTON_FALSIFICATION_GATE_V20.md"

# These are the highest-level current-main packages relevant to the requested
# scalar-potential/vacuum/proton-decay falsification.  Their own build_report
# calls traverse the lower-level stack.
MODULES: dict[str, str] = {
    "baseline_scalar_proton": "scalar_vacuum_proton_decay_v20",
    "pure_210_tensor_basis": "promote_210n_tensor_basis_uniqueness_v20",
    "mixed_rep_hilbert": "mixed_rep_hilbert_series_v20",
    "quartic_soft_betas": "quartic_soft_betas_v20",
    "sarah_pyrate_model": "sarah_pyrate_210n_model_file_v20",
    "exact_xy_masses": "exact_xy_masses_component_vacuum_v20",
    "inter_rep_triplet_mixing": "inter_rep_10_126_mixing_v20",
    "component_hessian_extrema": "component_hessian_competing_extrema_v20",
    "mixed_full_hessian": "mixed_210_126_10_hilbert_hessian_v20",
    "tau_p_full_stack": "tau_p_full_stack_uniqueness_v20",
    "tau_p_hessian_closure": "tau_p_hessian_residual_closure_v20",
    "pq_null_lam4_lift": "pq_null_lam4_portal_lift_v20",
}


def _json_default(obj: Any) -> Any:
    try:
        import numpy as np
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
    except Exception:
        pass
    if isinstance(obj, complex):
        return {"re": obj.real, "im": obj.imag}
    raise TypeError(f"not JSON serializable: {type(obj).__name__}")


def _run_report(module_name: str) -> dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, "build_report", None)
        if not callable(fn):
            return {
                "_audit_error": "missing build_report()",
                "status": "AUDIT_IMPORT_FAILED",
                "n_failed": 1,
            }
        report = fn()
        if not isinstance(report, dict):
            return {
                "_audit_error": f"build_report returned {type(report).__name__}",
                "status": "AUDIT_REPORT_INVALID",
                "n_failed": 1,
            }
        return report
    except Exception as exc:
        return {
            "_audit_error": f"{type(exc).__name__}: {exc}",
            "_traceback": traceback.format_exc(),
            "status": "AUDIT_EXECUTION_EXCEPTION",
            "n_failed": 1,
        }


def _values(obj: Any, key: str) -> list[Any]:
    out: list[Any] = []
    if isinstance(obj, dict):
        for k, value in obj.items():
            if k == key:
                out.append(value)
            out.extend(_values(value, key))
    elif isinstance(obj, list):
        for value in obj:
            out.extend(_values(value, key))
    return out


def _first_number(obj: Any, *keys: str) -> float | None:
    for key in keys:
        for value in _values(obj, key):
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                return float(value)
    return None


def _any_true(obj: Any, key: str) -> bool:
    return any(value is True for value in _values(obj, key))


def _all_true_mapping(obj: Any, key: str) -> bool | None:
    vals = _values(obj, key)
    for value in vals:
        if isinstance(value, dict) and value:
            return all(v is True for v in value.values())
    return None


def build_report() -> dict[str, Any]:
    reports = {label: _run_report(module) for label, module in MODULES.items()}

    execution_failures: list[str] = []
    for label, report in reports.items():
        n_failed = report.get("n_failed", 0)
        if report.get("_audit_error") or not isinstance(n_failed, int) or n_failed != 0:
            execution_failures.append(
                f"{label}: {report.get('_audit_error') or report.get('failures') or n_failed}"
            )

    sarah = reports["sarah_pyrate_model"]
    tau_full = reports["tau_p_full_stack"]
    tau_hess = reports["tau_p_hessian_closure"]
    pq_lift = reports["pq_null_lam4_lift"]
    mixed_hess = reports["mixed_full_hessian"]
    mixed_hilbert = reports["mixed_rep_hilbert"]

    live_sarah = _any_true(sarah, "live_sarah_or_pyrate_executable_run")
    exact_unique = _any_true(tau_hess, "exact_unique_proton_lifetime")
    selected_tau = _first_number(
        tau_hess, "selected_tau_e_years", "exact_combined_channel_lifetime_years"
    )
    limit = 2.4e34
    try:
        base_mod = importlib.import_module("scalar_vacuum_proton_decay_v20")
        limit = float(getattr(base_mod, "SK_EPI0_LIMIT_YR", limit))
    except Exception:
        pass

    hessian_closed = _all_true_mapping(
        tau_hess, "hessian_residuals_closed"
    )
    exact_pq_kernel_lifted = _any_true(
        pq_lift, "pq_null_exact_kernel_lifted_by_lam4"
    )
    selected_lam4_clears = _any_true(
        pq_lift, "selected_lam4_clears_gut_null_tol"
    )
    cal_g_soft_mode = _any_true(pq_lift, "cal_G_soft_mode_documented")
    mixed_spectrum_positive = _any_true(mixed_hess, "all_physical_positive")
    unfiltered_molien_closed = _any_true(
        mixed_hilbert, "mixed_rep_unfiltered_molien_haar_series"
    )

    alpha_open = any(
        value is True
        for value in _values(tau_hess, "scalar_alpha_not_unique_from_flavour")
    )
    whole_model_flags = [
        value for report in reports.values() for value in _values(report, "whole_model_excluded")
    ]
    upstream_whole_model_excluded = any(value is True for value in whole_model_flags)

    hard_theory_failures: list[str] = []
    if hessian_closed is False:
        hard_theory_failures.append("current Hessian closure certificate is false")
    if mixed_spectrum_positive is False:
        hard_theory_failures.append("current mixed physical spectrum is not positive")
    if not exact_pq_kernel_lifted and not execution_failures:
        hard_theory_failures.append("the claimed lambda4 exact-kernel lift did not reproduce")
    if exact_unique and selected_tau is not None and selected_tau < limit:
        hard_theory_failures.append(
            "exact complete proton-decay lifetime is below the experimental limit"
        )
    if upstream_whole_model_excluded:
        hard_theory_failures.append("an upstream module explicitly excludes the whole model")

    blockers: list[str] = []
    if not live_sarah:
        blockers.append("no live SARAH/PyR@TE executable beta-function and spectrum dump")
    if not exact_unique:
        blockers.append("exact_unique_proton_lifetime remains false")
    if alpha_open:
        blockers.append("scalar proton-decay alpha/flavour input is not unique")
    if not selected_lam4_clears:
        blockers.append("selected lambda4 does not clear the repository GUT-relative null tolerance")
    if cal_g_soft_mode:
        blockers.append("gamma-independent cal-G soft/near-null mode remains")
    if unfiltered_molien_closed is not True:
        blockers.append("unfiltered mixed-representation Molien/Haar invariant proof is absent")
    if hessian_closed is not True:
        blockers.append("full Hessian/competing-extrema closure is not independently established")

    selected_point_excluded = (
        selected_tau is not None and selected_tau < limit
    )
    # A selected benchmark can fail without killing the theory when free UV or
    # flavour inputs still exist.  This distinction is enforced here.
    whole_model_excluded = bool(
        upstream_whole_model_excluded
        or (exact_unique and selected_point_excluded)
        or any("Hessian" in item or "spectrum" in item for item in hard_theory_failures)
    )

    if execution_failures:
        state = "EXECUTION_FAIL"
    elif hard_theory_failures:
        state = "THEORY_FAIL"
    elif blockers:
        state = "BLOCKED"
    else:
        state = "PASS"

    numerical = {
        "proton_limit_years": limit,
        "selected_tau_e_years": selected_tau,
        "selected_point_passes_limit": (
            None if selected_tau is None else selected_tau >= limit
        ),
        "selected_point_excluded_conditionally": selected_point_excluded,
        "M_PD_GeV": _first_number(tau_hess, "M_PD_GeV", "M_PD_mediator_GeV"),
        "lightest_triplet_mass_GeV": _first_number(
            tau_full, "lightest_MT_GeV", "lightest_abs_GeV"
        ),
        "lam4_selected": _first_number(pq_lift, "lam4_selected"),
        "lam4_critical_abs": _first_number(pq_lift, "lam4_crit_abs"),
        "pq_null_total_after_lift": _first_number(
            pq_lift.get("lifted_selected_lam4", {}), "n_pq_null_total"
        ),
        "cal_G_nulls_after_lift": _first_number(
            pq_lift.get("lifted_selected_lam4", {}), "g_n_null_below_tol"
        ),
    }

    summaries = {
        label: {
            "module": MODULES[label],
            "status": report.get("status"),
            "n_failed": report.get("n_failed", 0),
            "flags": report.get("flag", {}),
            "verdict": report.get("verdict"),
            "audit_error": report.get("_audit_error"),
        }
        for label, report in reports.items()
    }

    return {
        "status": "CURRENT_MAIN_SCALAR_PROTON_REAUDIT_COMPLETE",
        "overall_state": state,
        "execution_failures": execution_failures,
        "hard_theory_failures": hard_theory_failures,
        "scientific_blockers": blockers,
        "numerical_findings": numerical,
        "certificates": {
            "all_critical_modules_executed": not execution_failures,
            "hessian_residuals_closed_in_repository_stack": hessian_closed,
            "mixed_spectrum_positive_in_repository_stack": mixed_spectrum_positive,
            "exact_pq_kernel_lifted": exact_pq_kernel_lifted,
            "selected_lam4_clears_null_tolerance": selected_lam4_clears,
            "cal_G_soft_mode_remaining": cal_g_soft_mode,
            "live_sarah_or_pyrate_run": live_sarah,
            "unfiltered_molien_haar_closed": unfiltered_molien_closed,
            "exact_unique_proton_lifetime": exact_unique,
            "whole_model_excluded": whole_model_excluded,
            "whole_model_validated": state == "PASS",
        },
        "module_summaries": summaries,
        "verdict": (
            "The latest main branch is internally testable and has closed several prior "
            "conditional subproblems, but it has not reached an externally validated, "
            "tensor-complete scalar vacuum and exact unique proton-decay prediction. "
            "A selected-point failure is not promoted to whole-model death while the "
            "documented UV/flavour/spectrum residuals remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    n = report["numerical_findings"]
    c = report["certificates"]
    lines = [
        "# Current-main scalar/proton re-audit — v20",
        "",
        f"**Overall state:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Numerical findings",
        "",
    ]
    for key, value in n.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Certificates", ""])
    for key, value in c.items():
        lines.append(f"- `{key}`: **{value}**")
    lines.extend(["", "## Scientific blockers", ""])
    for item in report["scientific_blockers"] or ["none"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Hard failures", ""])
    for item in report["hard_theory_failures"] or ["none"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Execution failures", ""])
    for item in report["execution_failures"] or ["none"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(
        json.dumps(report, indent=2, default=_json_default) + "\n", encoding="utf-8"
    )
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, default=_json_default))
    if report["overall_state"] in {"EXECUTION_FAIL", "THEORY_FAIL"}:
        return 1
    if args.require_complete and report["overall_state"] != "PASS":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
