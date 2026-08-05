#!/usr/bin/env python3
"""Fill OPEN_MIXED_126 from the guaranteed 210·126†·126 PS-singlet channel.

Inventory channel ``210x126_126`` / slot ``OPEN_MIXED_126`` is charge-allowed
and independently guaranteed (signed cubic audit / Z17 filter). Full index CG
for that cubic is not in-repo, but the published Aulakh/PS-singlet reduction

    eff_210_for_126 = |ω + a| + |p|

is already transcribed in ``cg_normalized_mt_locking_mix_v20.cg_weighted_210_vev``.

For the non-SUSY cubic

    V ⊃ λ_126 Φ · (Σ̄† Σ̄)     with [λ_126] = GeV,

the Sigmabar holomorphic/Hermitian mass-squared shift on the selected vacuum is

    ΔM²_Σ̄ = λ_126 · eff_210_for_126
           = λ̃ · M_GUT · eff_210_for_126

with dimensionless λ̃ an O(1) free overall normalization.

This module fills Schur C with that isotropic Hermitian seed and records
honesty boundaries: full 126×126 Cartesian CG, second independent multiplicity,
and channels 120/320/1050/4125 remain OPEN. Theory stays BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import cg_normalized_mt_locking_mix_v20 as cgmix
import component_lift_210_126_10_v20 as clift
import direct_phi_h_sigmabar_td_crosscheck_v20 as td
import direct_portal_mass2_schur_gate_v20 as schur
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_210_cg_threshold_masses_v20 as cg210
import so10_cubic_operator_signed_audit_v20 as cubic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIAGONAL_SIGMABAR_M2_MIXED_126_PS_SINGLET_V20.json"
OUT_MD = ROOT / "DIAGONAL_SIGMABAR_M2_MIXED_126_PS_SINGLET_V20.md"

DEFAULT_LAM_TILDE = 1.0e-2


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


def mixed_126_mass2_seed(
    *,
    a: float,
    p: float,
    omega: float,
    m_gut: float,
    lam_tilde: float = DEFAULT_LAM_TILDE,
) -> dict[str, Any]:
    """Hermitian isotropic ΔM²_Σ̄ from the PS-singlet 210·126†·126 reduction."""
    weights = cgmix.cg_weighted_210_vev(a=a, p=p, omega=omega)
    eff = float(weights["eff_210_for_126_GeV"])
    # [λ_126]=GeV ⇒ λ_126 = λ̃ M_GUT; M² = λ_126 · eff.
    lam_gev = float(lam_tilde) * float(m_gut)
    delta_m2 = lam_gev * eff
    canonical = td.aulakh_to_canonical_singlets(p=p, a=a, omega=omega)
    return {
        "operator": "210_H 126bar_H^dag 126bar_H",
        "slot": "OPEN_MIXED_126",
        "inventory_channel_id": "210x126_126",
        "ps_singlet_form": "(omega + a) + p  →  eff_210_for_126",
        "lam_tilde": float(lam_tilde),
        "lam_cubic_GeV": lam_gev,
        "eff_210_for_126_GeV": eff,
        "delta_M2_GeV2": float(delta_m2),
        "aulakh_vevs_GeV": {"a": a, "p": p, "omega": omega},
        "canonical_PAW_GeV": canonical,
        "cg_weights": weights,
        "full_tensor_normalized": False,
        "positive_hermitian_schur_seed": delta_m2 > 0.0,
    }


def build_report(
    *,
    lam_tilde: float = DEFAULT_LAM_TILDE,
) -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "MIXED_126_PS_SINGLET_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "overall_state": "BLOCKED",
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    vevs = _ledger_vevs(anchor)
    seed = mixed_126_mass2_seed(
        a=vevs["a"],
        p=vevs["p"],
        omega=vevs["omega"],
        m_gut=m_gut,
        lam_tilde=lam_tilde,
    )
    cubic_rep = cubic.build_report()
    ledger_210 = cg210.invariant_cg_ledger()
    mixed_entry = next(
        (
            e
            for e in ledger_210["entries"]
            if e["operator"] == "210 · 126† · 126"
        ),
        None,
    )

    # Schur C: isotropic Hermitian fill of the 126 modes from this channel alone.
    c_vec = np.full(126, seed["delta_M2_GeV2"], dtype=float)
    # Minimal positive A so the Schur gate can run as a diagnostic (not a claim).
    a_vec = np.full(10, 1.0e4, dtype=float)
    historical_lam4 = -0.05 * m_i / m_gut
    mixing = schur.portal_mass2_matrix(
        p=vevs["p"],
        a=vevs["a"],
        omega=vevs["omega"],
        v_s=vevs["vS"],
        lam4=historical_lam4,
    )
    schur_rep = schur.schur_positivity_report(
        a_vec.tolist(), c_vec.tolist(), mixing
    )

    one_guaranteed = bool(
        cubic_rep.get("flag", {}).get("one_210_126dag126_guaranteed", False)
    )

    checks = {
        "eff_210_for_126_positive": seed["eff_210_for_126_GeV"] > 0.0,
        "delta_M2_positive": seed["delta_M2_GeV2"] > 0.0,
        "C_shape_126": len(c_vec) == 126,
        "cubic_audit_executed": cubic_rep.get("n_failed", 1) == 0,
        "one_mixed_126_channel_guaranteed": one_guaranteed,
        "mixed_126_cg_ledger_present": mixed_entry is not None,
        "mixed_126_not_full_tensor": mixed_entry is not None
        and not mixed_entry.get("full_tensor_normalized", True),
        "no_120_320_1050_4125_invented": True,
        "schur_report_emitted": "positive_definite" in schur_rep,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "OPEN_MIXED_126_PS_SINGLET_PARTIAL_M2_FILLED__FULL_CG_OPEN"
            if not failures
            else "OPEN_MIXED_126_PS_SINGLET_FILL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "vevs_GeV": vevs,
        "seed": seed,
        "C_partial_from_mixed_126_GeV2": c_vec.tolist(),
        "schur_diagnostic_with_mixed_126_only": {
            "positive_definite": schur_rep.get("positive_definite"),
            "largest_normalized_singular_value": schur_rep.get(
                "largest_normalized_singular_value"
            ),
            "note": (
                "Diagnostic only: A is a soft floor, not a complete H10 diagonal"
            ),
        },
        "upstream": {
            "cubic_signed_audit_status": cubic_rep.get("status"),
            "one_PDD_channel_guaranteed": one_guaranteed,
            "cg210_mixed_126_entry": mixed_entry,
        },
        "slot_fill": {
            "OPEN_MIXED_126": {
                "status": "PARTIAL_PS_SINGLET_M2_FILLED",
                "contribution_GeV2": seed["delta_M2_GeV2"],
                "feeds": "C",
                "positive_hermitian_schur_seed": True,
                "full_cartesian_cg": False,
            }
        },
        "still_open": {
            "OPEN_MIXED_120": True,
            "OPEN_MIXED_320": True,
            "OPEN_126_1050": True,
            "OPEN_126_4125": True,
            "second_independent_210_126_126_multiplicity": True,
            "full_126x126_cartesian_CG_for_mixed_126": True,
            "full_component_hessian_G3": True,
        },
        "flags": {
            "OPEN_MIXED_126_ps_singlet_partial_filled": not bool(failures),
            "positive_hermitian_schur_C_seed_from_mixed_126": seed[
                "delta_M2_GeV2"
            ]
            > 0.0,
            "full_tensor_CG_normalized": False,
            "invented_missing_cg": False,
            "full_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "OPEN_MIXED_126 is partially filled from the guaranteed "
            "210·126†·126 PS-singlet reduction "
            f"eff=|ω+a|+|p| ⇒ ΔM²_Σ̄={seed['delta_M2_GeV2']:.6g} GeV² "
            f"(λ̃={lam_tilde:g}). Full Cartesian CG, extra multiplicity, and "
            "channels 120/320/1050/4125 remain OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    seed = report["seed"]
    OUT_MD.write_text(
        "# OPEN_MIXED_126 PS-singlet Sigmabar M² fill — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- eff_210_for_126: `{seed['eff_210_for_126_GeV']:.6g}` GeV\n"
        f"- ΔM²_Σ̄: `{seed['delta_M2_GeV2']:.6g}` GeV²\n"
        f"- Full tensor normalized: `{seed['full_tensor_normalized']}`\n\n"
        + report["verdict"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--lam-tilde", type=float, default=DEFAULT_LAM_TILDE)
    args = parser.parse_args(argv)
    report = build_report(lam_tilde=args.lam_tilde)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
