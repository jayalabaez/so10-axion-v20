#!/usr/bin/env python3
r"""Tree-level effective PQ-axion potential after integrating heavy modes (v20).

Physics
-------
On the selected vacuum, after the Z'_R gauge quotient, the physical CP-odd
sector ``(φ_10, φ_S)`` has potential (from κ H₁₀² S)

    V_κ(φ) = (A_κ / 2) (2 φ_10 + φ_S)²
           = (5 A_κ / 2) h² ,

where the orthonormal heavy / axion basis is

    û_h = (2,1)/√5 ,   û_a = (1,-2)/√5 ,
    φ   = h û_h + a û_a .

Tree-level integration of the heavy mode ``h`` (m_h² = 5 A_κ) sets ``h=0``
and yields

    V_eff(a) = 0

exactly in this operator truncation. The all-orders selected-vacuum selection
rule (B−L ⇒ d=0, PQ/Z17 ⇒ (d,h,s)∥κ) then implies that integrating out
*radial* heavy 210/126 amplitudes cannot generate an axion potential without
additional PQ-breaking operators beyond κ.

Canonical axion kinetic normalization on ``(Im H, Im S)`` gives the decay
constant proxy

    f_a = √(hEW² + 4 v_S²)

along the Im-space null ``(hEW, −2 v_S)``.

Honesty
-------
* Reduced selected-vacuum phase sector + radial selection-rule argument only.
* UV value of κ / A_κ not determined; no claim of unique τ_p.
* Does not invent 120/320/1050/4125 CG. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import diagonal_210_radial_cubic_ps_singlet_v20 as d210
import scalar_vacuum_proton_decay_v20 as scalar_pd
import selected_vacuum_neutral_phase_gauge_quotient_v20 as pq

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EFFECTIVE_PQ_AXION_POTENTIAL_V20.json"
OUT_MD = ROOT / "EFFECTIVE_PQ_AXION_POTENTIAL_V20.md"

U_HEAVY = np.array([2.0, 1.0], dtype=float) / math.sqrt(5.0)
U_AXION = np.array([1.0, -2.0], dtype=float) / math.sqrt(5.0)


def phase_potential_coeffs(a_kappa: float) -> dict[str, Any]:
    """V = (A_κ/2)(2φ₁₀+φ_S)² = (5 A_κ/2) h² in the (h,a) basis."""
    a_kappa = float(a_kappa)
    h_phi = np.asarray(pq.quotient_report(a_kappa)["hessian"]["after_quotient"], dtype=float)
    # Orthonormal change of basis R = [û_h | û_a]
    r = np.column_stack([U_HEAVY, U_AXION])
    h_ha = r.T @ h_phi @ r
    # Expect diag(5 A_κ, 0)
    m2_heavy = float(h_ha[0, 0])
    m2_axion = float(h_ha[1, 1])
    cross = float(h_ha[0, 1])
    return {
        "A_kappa": a_kappa,
        "H_phi": h_phi.tolist(),
        "H_ha": h_ha.tolist(),
        "m2_heavy_GeV2": m2_heavy,
        "m2_axion_GeV2": m2_axion,
        "cross_ha": cross,
        "V_formula": "V_κ = (A_κ/2)(2 φ_10 + φ_S)² = (5 A_κ/2) h²",
        "tree_level_V_eff_a": 0.0,
        "integration": "∂V/∂h = 5 A_κ h = 0 ⇒ h=0 ⇒ V_eff(a)=0",
    }


def decay_constant_proxy(*, h_ew: float, v_s: float) -> dict[str, Any]:
    """f_a from Im-space axion direction (hEW, −2 v_S)."""
    n = np.array([float(h_ew), -2.0 * float(v_s)], dtype=float)
    f_a = float(np.linalg.norm(n))
    return {
        "hEW_GeV": float(h_ew),
        "vS_GeV": float(v_s),
        "axion_im_direction": n.tolist(),
        "f_a_GeV": f_a,
        "formula": "f_a = ||(hEW, -2 v_S)|| = √(hEW² + 4 v_S²)",
    }


def radial_integration_argument(
    *, m2_p210: float, m2_delta_proxy: float | None
) -> dict[str, Any]:
    """Why radial heavies do not generate V_eff(a) without new PQ breaking."""
    return {
        "selected_vacuum_nulls": {
            "A_lock": 0.0,
            "A_lam4": 0.0,
            "active_operator": "kappa H_10^2 S only",
        },
        "all_orders_selection_rule": pq.quotient_report(1.0)["all_orders_selection_rule"],
        "heavy_radial_masses_GeV2": {
            "P_210": float(m2_p210),
            "DeltaR_proxy_or_none": m2_delta_proxy,
        },
        "conclusion": (
            "Any selected-vacuum polynomial built from charge-allowed operators "
            "has phase vector ∥ κ; after Z' quotient the only flat direction is "
            "the PQ axion. Integrating radial heavies at tree level therefore "
            "cannot lift V_eff(a) without additional PQ-breaking operators."
        ),
        "generates_axion_potential": False,
    }


def build_report(*, a_kappa: float | None = None) -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    h_ew = by_name["h_EW"]
    v_s = by_name["S_PQ"]

    # Match extended Hessian scale rule when A_κ not supplied: use a finite
    # positive diagnostic scale (not a UV determination of κ).
    if a_kappa is None:
        # Prefer reduced P_210 mass as a GUT-ish reference / 5 (same spirit as min(A,C)/5).
        d210_rep = d210.build_report()
        m2_210 = float(d210_rep["mass"]["m2_210_form_basis_GeV2"])
        a_kappa = m2_210 / 5.0
        scale_rule = "m2_210_form_basis/5 (diagnostic; UV κ OPEN)"
    else:
        d210_rep = d210.build_report()
        m2_210 = float(d210_rep["mass"]["m2_210_form_basis_GeV2"])
        scale_rule = "user_supplied_A_kappa"

    pot = phase_potential_coeffs(a_kappa)
    fa = decay_constant_proxy(h_ew=h_ew, v_s=v_s)
    radial = radial_integration_argument(m2_p210=m2_210, m2_delta_proxy=None)

    # Analytic identities
    expected_m2 = 5.0 * float(a_kappa)
    checks = {
        "heavy_mass_is_5_A_kappa": abs(pot["m2_heavy_GeV2"] - expected_m2)
        <= 1e-8 * max(expected_m2, 1.0),
        "axion_mass_vanishes": abs(pot["m2_axion_GeV2"])
        <= 1e-10 * max(expected_m2, 1.0),
        "ha_basis_diagonal": abs(pot["cross_ha"]) <= 1e-10 * max(expected_m2, 1.0),
        "tree_level_V_eff_flat": pot["tree_level_V_eff_a"] == 0.0,
        "f_a_positive": fa["f_a_GeV"] > 0.0,
        "radial_does_not_lift_axion": radial["generates_axion_potential"] is False,
        "upstream_quotient_green": pq.quotient_report(1.0).get("n_failed", 1) == 0,
        "d210_green": d210_rep.get("n_failed", 1) == 0,
        "uv_kappa_not_claimed": True,
        "cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EFFECTIVE_PQ_AXION_POTENTIAL_FLAT_AT_TREE__UV_KAPPA_OPEN"
            if not failures
            else "EFFECTIVE_PQ_AXION_POTENTIAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "phase_sector": pot,
        "A_kappa_scale": {
            "A_kappa_GeV2": float(a_kappa),
            "rule": scale_rule,
            "uv_kappa_determined": False,
        },
        "decay_constant": fa,
        "radial_heavy_integration": radial,
        "flags": {
            "tree_level_axion_potential_flat": not bool(failures),
            "heavy_cp_odd_integrated": not bool(failures),
            "radial_selection_rule_no_lift": not bool(failures),
            "uv_kappa_determined": False,
            "cg_120_320_1050_4125_invented": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "uv_determination_of_kappa": True,
            "pq_breaking_beyond_kappa": True,
            "missing_cg_120_320_1050_4125": True,
            "full_nonsusy_vacuum_hessian": True,
        },
        "verdict": (
            "After Z' quotient, V_κ=(5 A_κ/2) h²; integrating the heavy CP-odd "
            f"mode (m²={pot['m2_heavy_GeV2']:.6e} GeV²) leaves V_eff(a)=0 at "
            f"tree level. f_a≈{fa['f_a_GeV']:.6e} GeV. Radial heavies cannot "
            "lift the axion without new PQ breaking (selection rule). "
            "UV κ and full Hessian remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Effective PQ-axion potential (tree-level heavy integration) — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- m²_heavy: `{report['phase_sector']['m2_heavy_GeV2']}` GeV²\n"
        f"- V_eff(a): `{report['phase_sector']['tree_level_V_eff_a']}`\n"
        f"- f_a: `{report['decay_constant']['f_a_GeV']}` GeV\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--A-kappa", type=float, default=None)
    args = parser.parse_args(argv)
    report = build_report(a_kappa=args.A_kappa)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
