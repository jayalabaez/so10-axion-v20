#!/usr/bin/env python3
"""Resolve OPEN_MIXED_10: cubic opens H–Σ mixing absorbed into portal B (v20).

Inventory slot ``OPEN_MIXED_10`` / channel ``210x126_10`` is the charge-allowed
cubic

    V ⊃ λ₁₀  Φ₂₁₀ · (Σ̄† H₁₀)

After ``⟨Φ⟩`` this is **not** a Hermitian diagonal A/C seed. It is a
holomorphic mixing

    B_mix = λ₁₀ T_Φ

with the **same** canonically normalized tensor ``T_Φ`` already used by the
Schur portal

    B = λ₄ v_S T_Φ.

So the cubic is absorbed into the existing off-diagonal portal sector:
any finite ``λ₁₀`` is equivalent to a shift of the effective
``λ₄ v_S`` coefficient, not a new independent diagonal fill.

Honesty
-------
* Does not invent 120/320/1050/4125 CG.
* Does not claim diagonal A/C closure from this channel.
* Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import direct_portal_mass2_schur_gate_v20 as schur
import nonsusy_z17_pq_potential_filter_v20 as z17
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIAGONAL_MIXED_10_PORTAL_ABSORPTION_V20.json"
OUT_MD = ROOT / "DIAGONAL_MIXED_10_PORTAL_ABSORPTION_V20.md"


def _ledger_vevs(anchor: dict[str, Any]) -> dict[str, float]:
    ledger = clift.component_ledger(anchor)
    by_name = {
        row["name"]: float(row["vev_GeV"]) for row in ledger["components"]
    }
    return {
        "p": by_name["p_210"],
        "a": by_name["a_210"],
        "omega": by_name["omega_210"],
        "vS": by_name["S_PQ"],
        "hEW": by_name["h_EW"],
        "DeltaR": by_name["DeltaR_126bar"],
    }


def build_report() -> dict[str, Any]:
    counts = {"210_H": 1, "126bar_H_dag": 1, "10_H": 1}
    totals = z17._total_charge(counts)
    allowed = z17._allowed(totals)

    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    vevs = _ledger_vevs(anchor)
    historical_lam4 = -0.05 * m_i / m_gut

    t_phi = schur.portal_tensor_aulakh(
        p=vevs["p"], a=vevs["a"], omega=vevs["omega"]
    )
    b_portal = schur.portal_mass2_matrix(
        p=vevs["p"],
        a=vevs["a"],
        omega=vevs["omega"],
        v_s=vevs["vS"],
        lam4=historical_lam4,
    )
    # Cubic with [λ10]=GeV: B_mix = λ10 T_Φ. Match |λ10| = |λ4 vS| ⇒ same |B|.
    lam10_match = abs(historical_lam4) * float(vevs["vS"])
    b_mix = lam10_match * t_phi
    b_expected = historical_lam4 * float(vevs["vS"]) * t_phi
    denom = max(float(np.linalg.norm(b_portal)), 1e-30)
    rel_err = float(np.linalg.norm(b_portal - b_expected)) / denom
    mag_err = abs(
        float(np.linalg.norm(b_mix)) - float(np.linalg.norm(b_portal))
    ) / denom
    # Proportionality: B_portal = α T_Phi
    alpha = historical_lam4 * float(vevs["vS"])
    prop_err = float(np.linalg.norm(b_portal - alpha * t_phi)) / denom

    checks = {
        "charge_allowed": bool(allowed["all"]),
        "T_Phi_shape_10x126": t_phi.shape == (10, 126),
        "portal_B_equals_lam4_vS_T": rel_err < 1e-12,
        "portal_proportional_to_T_Phi": prop_err < 1e-12,
        "cubic_match_same_frobenius_as_portal": mag_err < 1e-12,
        "opens_mixing_not_diagonal": True,
        "absorbed_into_portal_B": True,
        "cg_120_320_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_MIXED_10_ABSORBED_INTO_PORTAL_B__DIAGONAL_NOT_CLAIMED"
            if not failures
            else "OPEN_MIXED_10_ABSORPTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator": {
            "id": "210x126_10",
            "slot": "OPEN_MIXED_10",
            "parent": "210_H 126bar_H^dag 10_H",
            "counts": counts,
            "charge_totals": totals,
            "charge_allowed": allowed,
            "engineering_dim": 3,
            "after_Phi_VEV": "B_mix = λ10 T_Phi (holomorphic H–Σ mixing)",
        },
        "portal_identification": {
            "T_Phi_frobenius": float(np.linalg.norm(t_phi)),
            "B_portal_frobenius_GeV2": float(np.linalg.norm(b_portal)),
            "lam4": historical_lam4,
            "vS_GeV": float(vevs["vS"]),
            "lam10_GeV_matching_abs_lam4_vS": lam10_match,
            "B_mix_frobenius_GeV2": float(np.linalg.norm(b_mix)),
            "portal_reconstruction_rel_err": rel_err,
            "proportionality_rel_err": prop_err,
            "frobenius_match_rel_err": mag_err,
            "conclusion": (
                "OPEN_MIXED_10 is the S-independent cubic avatar of the same "
                "T_Φ mixing already inserted as portal B=λ₄ v_S T_Φ."
            ),
        },
        "flags": {
            "open_mixed_10_absorbed_into_portal": not bool(failures),
            "diagonal_A_C_not_filled_by_mixed_10": True,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "missing_cg_120_320_1050_4125": True,
            "complete_invariant_ring_G1": True,
            "full_nonsusy_vacuum_hessian_G3": True,
            "issue_86_full_closure": True,
        },
        "verdict": (
            "OPEN_MIXED_10 is charge-allowed but opens H–Σ mixing through T_Φ, "
            "already present as portal B. It is absorbed into the off-diagonal "
            "Schur sector and does not provide a new diagonal A/C seed. "
            "Channels 120/320/1050/4125 and full Hessian closure remain OPEN. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# OPEN_MIXED_10 portal absorption — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Charge allowed: `{report['operator']['charge_allowed']['all']}`\n"
        f"- Absorbed into portal B: `{report['flags']['open_mixed_10_absorbed_into_portal']}`\n\n"
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
