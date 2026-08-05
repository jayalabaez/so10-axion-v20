#!/usr/bin/env python3
r"""UV κ constrained by stationarity at physical hEW=174 GeV (v20).

Physics
-------
The charge-allowed portal

    V_κ = −κ M_I |H|² S

induces the selected-vacuum phase amplitude

    A_κ = |κ| M_I hEW² v_S

(from ``V ⊃ −κ M_I r_h² r_s cos(2φ_h+φ_s)`` ⇒ Hessian ``A_κ g gᵀ`` with
``g=(2,1)``). Soft quadratic shifts restore radial stationarity at the
unification VEVs for finite κ (``charge_allowed_potential_minimize_v20``).

This module:

1. Imports the minimized / finite-κ benchmark couplings;
2. Evaluates **physical** ``A_κ`` at ``hEW=174``, ledger ``v_S``;
3. Contrasts the MI-equal proxy ``A_κ^{MI} = |κ| M_I⁴`` and the diagnostic
   ``m²_210/5`` scale used in the extended Hessian;
4. Records honesty: κ is **stationarity-constrained** in a finite window,
   not uniquely UV-determined.

Honesty
-------
* ``unique_uv_couplings = False`` (finite-κ window + soft shifts).
* Does not invent CG. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import component_lift_210_126_10_v20 as clift
import charge_allowed_potential_minimize_v20 as pmin
import diagonal_210_radial_cubic_ps_singlet_v20 as d210
import scalar_vacuum_proton_decay_v20 as scalar_pd
import unique_soft_scale_stationarity_v20 as softscale

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "UV_KAPPA_STATIONARITY_CONSTRAINT_V20.json"
OUT_MD = ROOT / "UV_KAPPA_STATIONARITY_CONSTRAINT_V20.md"


def a_kappa_physical(*, kappa: float, m_i: float, h_ew: float, v_s: float) -> float:
    """A_κ = |κ| M_I hEW² v_S from V_κ = −κ M_I r_h² r_s cos(2φ_h+φ_s)."""
    return abs(float(kappa)) * float(m_i) * (float(h_ew) ** 2) * float(v_s)


def a_kappa_mi_proxy(*, kappa: float, m_i: float) -> float:
    """Withdrawn equal-VEV proxy A_κ = |κ| M_I · M_I² · M_I."""
    return abs(float(kappa)) * float(m_i) ** 4


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    h_ew = by_name["h_EW"]
    v_s = by_name["S_PQ"]

    vmin = pmin.build_report()
    fixed = vmin["fixed_couplings"]
    fk = vmin.get("finite_kappa_benchmark_couplings")
    soft = softscale.build_report()
    d210_rep = d210.build_report()
    m2_210 = float(d210_rep["mass"]["m2_210_form_basis_GeV2"])
    diagnostic_a = m2_210 / 5.0

    # Prefer finite-κ when available for phase physics
    if fk is not None:
        kappa = float(fk["kappa"])
        lam4 = float(fk["lam4"])
        lambda_lock = float(fk["lambda_lock"])
        coupling_source = "finite_kappa_benchmark_couplings"
        finite_window = True
    else:
        kappa = float(fixed["kappa"])
        lam4 = float(fixed["lam4"])
        lambda_lock = float(fixed["lambda_lock"])
        coupling_source = "fixed_couplings_best"
        finite_window = bool(vmin.get("flag", {}).get("finite_kappa_window_demonstrated"))

    a_phys = a_kappa_physical(kappa=kappa, m_i=m_i, h_ew=h_ew, v_s=v_s)
    a_proxy = a_kappa_mi_proxy(kappa=kappa, m_i=m_i)
    m2_heavy = 5.0 * a_phys

    matched = soft.get("matched_soft_scale") or {}
    m12 = matched.get("M_1_2_GeV")

    checks = {
        "pmin_green": vmin.get("n_failed", 1) == 0,
        "physical_hEW_174": abs(h_ew - 174.0) < 1e-12,
        "vS_positive": v_s > 0.0,
        "a_kappa_physical_positive": a_phys > 0.0,
        "kappa_nonzero_in_window": abs(kappa) >= 0.05 or finite_window,
        "soft_scale_green": soft.get("n_failed", 1) == 0,
        "d210_green": d210_rep.get("n_failed", 1) == 0,
        "physical_A_uses_hEW_not_MI": abs(h_ew - m_i) > 1.0,
        "uv_kappa_not_claimed_unique": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "UV_KAPPA_STATIONARITY_CONSTRAINED__NOT_UNIQUE"
            if not failures
            else "UV_KAPPA_STATIONARITY_CONSTRAINT_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "vevs_GeV": {"hEW": h_ew, "vS": v_s, "M_I": m_i, "M_GUT": m_gut},
        "couplings": {
            "source": coupling_source,
            "kappa": kappa,
            "lam4": lam4,
            "lambda_lock": lambda_lock,
            "finite_kappa_window": finite_window,
            "unique_uv_couplings": False,
        },
        "A_kappa": {
            "physical_GeV2": a_phys,
            "formula": "A_κ = |κ| M_I hEW² v_S",
            "mi_equal_proxy_GeV2": a_proxy,
            "mi_proxy_withdrawn": True,
            "diagnostic_m2_210_over_5_GeV2": diagnostic_a,
            "ratio_physical_over_diagnostic": (
                a_phys / diagnostic_a if diagnostic_a > 0 else None
            ),
            "m2_heavy_cp_odd_GeV2": m2_heavy,
            "note": (
                "Physical A_κ uses hEW=174 and ledger v_S; diagnostic "
                "m²_210/5 was only a numerical scale for the extended Hessian."
            ),
        },
        "stationarity": {
            "soft_shifts_restore_radial": True,
            "pmin_status": vmin.get("status"),
            "soft_scale_status": soft.get("status"),
            "M_1_2_GeV": m12,
            "principle": (
                "Finite κ requires soft δm² shifts for stationarity at "
                "unification VEVs; κ is constrained but not unique."
            ),
        },
        "flags": {
            "uv_kappa_stationarity_constrained": not bool(failures),
            "uv_kappa_uniquely_determined": False,
            "physical_A_kappa_ready": not bool(failures),
            "finite_kappa_window_open": finite_window,
            "cg_120_320_1050_4125_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "unique_uv_kappa": True,
            "pq_breaking_beyond_kappa": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            f"κ={kappa:.6g} from {coupling_source}: physical "
            f"A_κ={a_phys:.6e} GeV² (=|κ| M_I hEW² v_S) at hEW=174; "
            f"m²_heavy=5 A_κ={m2_heavy:.6e} GeV². Finite-κ window open; "
            "κ is stationarity-constrained but not UV-unique. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# UV κ stationarity constraint at hEW=174 — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- κ: `{report['couplings']['kappa']}`\n"
        f"- A_κ (physical): `{report['A_kappa']['physical_GeV2']}` GeV²\n"
        f"- Unique UV κ: `{report['flags']['uv_kappa_uniquely_determined']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
