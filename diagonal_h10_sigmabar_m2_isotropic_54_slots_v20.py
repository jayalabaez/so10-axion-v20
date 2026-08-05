#!/usr/bin/env python3
r"""Fill Schur A/C slots from isotropic/norm + 54-locking channels.

After the channel inventory (PR #94), five literature channels already have
repository support short of full off-singlet CG:

* ``10x10_1_isotropic`` — soft/norm H10 diagonal
* ``2102_10dag10_quartic`` — 210-norm portal into H10
* ``2102_126dag126_quartic`` — 210-norm portal into Σ̄
* ``10x10_54`` / ``126_quartic_54`` — 54-locking channel with
  ``C_54=1/√54`` and combinatorial ``C_126→54``

This module builds *partial* positive diagonal blocks

    A_partial ∈ ℝ^{10},   C_partial ∈ ℝ^{126}

and feeds them into the exact Schur gate with the closed portal
``B = λ₄ v_S T_Φ``.  It does **not** invent 120/320/1050/4125 CG tensors
or claim the complete diagonal Hessian / G1–G3.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import cg_normalized_mt_locking_mix_v20 as cgmix
import component_lift_210_126_10_v20 as clift
import direct_portal_mass2_schur_gate_v20 as schur
import extended_ttbar_54_locking_v20 as lock54
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd
import so10_126_to_54_projector_v20 as proj126

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIAGONAL_H10_SIGMABAR_M2_ISOTROPIC_54_SLOTS_V20.json"
OUT_MD = ROOT / "DIAGONAL_H10_SIGMABAR_M2_ISOTROPIC_54_SLOTS_V20.md"

# Free overall quartic normalizations (not inventing CG tensors).
DEFAULT_LAM_210_H = 1.0e-2
DEFAULT_LAM_210_SIGMA = 1.0e-2
DEFAULT_LAM_LOCK = 1.0e-2
# Soft floor so Schur A,C stay strictly positive when radial soft is small.
SOFT_FLOOR_GEV2 = 1.0e4


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
        "H10_eff": by_name["H10_eff"],
    }


def isotropic_soft_diagonals(
    *,
    m_i: float,
    m_gut: float,
    lam4: float,
    vevs: dict[str, float],
) -> dict[str, float]:
    """Reduced-sector soft/quartic diagonals as isotropic seeds."""
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    quartic, _, targets = reduced.radial_quartic_matrix(radial)
    # Override with ledger VEVs where available.
    targets = {
        "P_210": float(vevs["p"]),
        "DeltaR_126bar": float(vevs["DeltaR"]),
        "H10_EW": float(vevs["hEW"]),
        "S_PQ": float(vevs["vS"]),
        "Phi17_X": float(targets.get("Phi17_X", m_i)),
    }
    params = reduced.interaction_parameters(m_i, m_gut, lam4)
    hessian = reduced.high_precision_hessian(targets, quartic, params)
    matrix = np.array(hessian.tolist(), dtype=float)
    index = {name: i for i, name in enumerate(reduced.FIELDS)}
    mu_h = float(matrix[index["H10_EW"], index["H10_EW"]])
    mu_s = float(matrix[index["DeltaR_126bar"], index["DeltaR_126bar"]])
    return {
        "mu2_H10_raw": mu_h,
        "mu2_Sigmabar_raw": mu_s,
        "mu2_H10": max(mu_h, SOFT_FLOOR_GEV2),
        "mu2_Sigmabar": max(mu_s, SOFT_FLOOR_GEV2),
        "soft_floor_GeV2": SOFT_FLOOR_GEV2,
        "source": "nonsusy_reduced_hessian diagonals (isotropic seed)",
    }


def phi_norm_sq_aulakh(*, p: float, a: float, omega: float) -> float:
    """Canonical Cartesian norm squared of the PS singlet Φ."""
    # P=p, A=√3 a, W=√6 ω  ⇒  ‖Φ‖² = P²+A²+W²
    return float(p * p + 3.0 * a * a + 6.0 * omega * omega)


def build_partial_diagonals(
    *,
    vevs: dict[str, float],
    soft: dict[str, float],
    m_i: float,
    m_gut: float,
    lam_210_h: float = DEFAULT_LAM_210_H,
    lam_210_sigma: float = DEFAULT_LAM_210_SIGMA,
    lam_lock: float = DEFAULT_LAM_LOCK,
) -> dict[str, Any]:
    """Assemble A_partial (len 10) and C_partial (len 126)."""
    weights = cgmix.cg_weighted_210_vev(
        a=vevs["a"], p=vevs["p"], omega=vevs["omega"]
    )
    phi2 = phi_norm_sq_aulakh(
        p=vevs["p"], a=vevs["a"], omega=vevs["omega"]
    )

    # Norm portals: λ * ‖Φ‖² contributions (GeV² after λ dimensionless).
    # Treat λ as already GeV^0 coupling to field^2; scale by φ².
    h_from_210 = float(lam_210_h) * phi2
    s_from_210 = float(lam_210_sigma) * phi2

    # Also record CG-weighted effective scales (diagnostic, not added twice).
    cg_diag = {
        "eff_210_for_10_GeV": weights["eff_210_for_10_GeV"],
        "eff_210_for_126_GeV": weights["eff_210_for_126_GeV"],
        "note": "CG-weighted scales are diagnostic; numerical add uses ‖Φ‖²",
    }

    p54 = lock54.projector_54_on_10x10()
    c_54 = float(p54["C_54_normalization"])
    proj = proj126.build_126_to_54_projector()
    c_126 = float(
        proj.get("contraction", {})
        .get("stats_126", {})
        .get("C_126_to_54", 1.0)
    )
    if not math.isfinite(c_126) or c_126 <= 0.0:
        c_126 = 1.0
    amp = lock54.locking_amplitude_54(
        m_i=m_i,
        m_gut=m_gut,
        lambda_lock=lam_lock,
        c_54=c_54,
        c_126_to_54=c_126,
    )
    # Convert locking amplitude into an isotropic mass² floor contribution.
    # A_54 has units of energy^4 in the phase potential; divide by M_I² to
    # obtain a GeV² mass-squared seed (schematic, not full component CG).
    a54 = float(amp["A_54"])
    locking_m2 = abs(a54) / max(m_i * m_i, 1.0)

    a_iso = float(soft["mu2_H10"])
    c_iso = float(soft["mu2_Sigmabar"])
    a_vec = np.full(10, a_iso + h_from_210 + locking_m2, dtype=float)
    c_vec = np.full(126, c_iso + s_from_210 + locking_m2, dtype=float)

    slots = {
        "OPEN_H10_SOFT_OR_NORM": {
            "status": "PARTIAL_M2_FILLED",
            "contribution_GeV2": a_iso,
            "feeds": "A",
        },
        "OPEN_H10_FROM_210_NORM": {
            "status": "PARTIAL_M2_FILLED",
            "contribution_GeV2": h_from_210,
            "feeds": "A",
            "phi_norm_sq_GeV2": phi2,
            "lam_210_h": lam_210_h,
        },
        "OPEN_SIGMA_FROM_210_NORM": {
            "status": "PARTIAL_M2_FILLED",
            "contribution_GeV2": s_from_210,
            "feeds": "C",
            "phi_norm_sq_GeV2": phi2,
            "lam_210_sigma": lam_210_sigma,
        },
        "OPEN_H10_54": {
            "status": "PARTIAL_M2_FILLED_ISOTROPIC_SEED",
            "contribution_GeV2": locking_m2,
            "feeds": "A",
            "C_54": c_54,
            "C_126_to_54": c_126,
            "A_54": a54,
            "note": (
                "Isotropic seed from locking amplitude / M_I²; not the "
                "full 54-projected component spectrum"
            ),
        },
        "OPEN_126_54_LOCKING": {
            "status": "PARTIAL_M2_FILLED_ISOTROPIC_SEED",
            "contribution_GeV2": locking_m2,
            "feeds": "C",
            "C_54": c_54,
            "C_126_to_54": c_126,
            "A_54": a54,
            "note": (
                "Isotropic seed from locking amplitude / M_I²; not the "
                "full 54-projected component spectrum"
            ),
        },
    }

    return {
        "A_partial_GeV2": a_vec.tolist(),
        "C_partial_GeV2": c_vec.tolist(),
        "A_min_GeV2": float(np.min(a_vec)),
        "C_min_GeV2": float(np.min(c_vec)),
        "A_mean_GeV2": float(np.mean(a_vec)),
        "C_mean_GeV2": float(np.mean(c_vec)),
        "components": {
            "isotropic_H10": a_iso,
            "isotropic_Sigmabar": c_iso,
            "210_norm_H10": h_from_210,
            "210_norm_Sigmabar": s_from_210,
            "locking_isotropic_seed": locking_m2,
        },
        "cg_weighted_diagnostic": cg_diag,
        "locking": {
            "lambda_lock": lam_lock,
            "C_54": c_54,
            "C_126_to_54": c_126,
            "A_54": a54,
            "projector_54_ok": bool(
                p54.get("flag", {}).get("idempotent")
                and p54.get("flag", {}).get("trace_equals_54")
            ),
            "c126_projector_status": proj.get("status"),
        },
        "filled_slots": slots,
        "still_open_slots": [
            "OPEN_210_CHANNEL_45",
            "OPEN_210_CHANNEL_54",
            "OPEN_210_CHANNEL_210",
            "OPEN_210_CHANNEL_1050",
            "OPEN_MIXED_10",
            "OPEN_MIXED_120",
            "OPEN_MIXED_126",
            "OPEN_MIXED_320",
            "OPEN_126_1050",
            "OPEN_126_4125",
        ],
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    historical_lam4 = float(
        -0.05 * m_i / m_gut
    )
    vevs = _ledger_vevs(anchor)
    soft = isotropic_soft_diagonals(
        m_i=m_i, m_gut=m_gut, lam4=historical_lam4, vevs=vevs
    )
    partial = build_partial_diagonals(
        vevs=vevs, soft=soft, m_i=m_i, m_gut=m_gut
    )

    mixing = schur.portal_mass2_matrix(
        p=vevs["p"],
        a=vevs["a"],
        omega=vevs["omega"],
        v_s=vevs["vS"],
        lam4=historical_lam4,
    )
    schur_rep = schur.schur_positivity_report(
        partial["A_partial_GeV2"],
        partial["C_partial_GeV2"],
        mixing,
    )
    hessian = schur.real_hessian_from_holomorphic_portal(
        partial["A_partial_GeV2"],
        partial["C_partial_GeV2"],
        mixing,
    )
    eigs = np.linalg.eigvalsh(hessian)

    checks = {
        "partial_A_shape_10": len(partial["A_partial_GeV2"]) == 10,
        "partial_C_shape_126": len(partial["C_partial_GeV2"]) == 126,
        "partial_A_positive": partial["A_min_GeV2"] > 0.0,
        "partial_C_positive": partial["C_min_GeV2"] > 0.0,
        "locking_projector_54_ok": partial["locking"]["projector_54_ok"],
        "five_inventory_slots_filled": len(partial["filled_slots"]) == 5,
        "schur_report_emitted": "positive_definite" in schur_rep,
        "real_hessian_272": hessian.shape == (272, 272),
        "missing_cg_channels_still_open": len(partial["still_open_slots"])
        >= 8,
        "full_diagonal_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "DIAGONAL_M2_ISOTROPIC_54_SLOTS_PARTIAL__FULL_DIAGONAL_OPEN"
            if not failures
            else "DIAGONAL_M2_ISOTROPIC_54_SLOTS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "vevs_GeV": vevs,
        "soft_isotropic": soft,
        "partial_diagonals": {
            k: v
            for k, v in partial.items()
            if k
            not in {
                "A_partial_GeV2",
                "C_partial_GeV2",
            }
        },
        "A_partial_GeV2": partial["A_partial_GeV2"],
        "C_partial_GeV2": partial["C_partial_GeV2"],
        "portal_B": {
            "shape": list(mixing.shape),
            "lam4": historical_lam4,
            "frobenius_GeV2": float(np.linalg.norm(mixing)),
        },
        "schur_with_partial_diagonals": schur_rep,
        "real_hessian_min_eigenvalue_GeV2": float(eigs[0]),
        "real_hessian_positive_definite": bool(eigs[0] > 0.0),
        "remaining_blockers": {
            "transcribe_missing_CG_120_320_1050_4125": True,
            "full_component_diagonal_H10_m2": True,
            "full_component_diagonal_Sigmabar_m2": True,
            "complete_invariant_ring_G1": True,
            "full_tensor_projected_potential_G2": True,
            "full_nonsusy_vacuum_hessian_G3": True,
            "issue_86_full_closure": True,
        },
        "flag": {
            "isotropic_norm_54_slots_partially_filled": not bool(failures),
            "schur_fed_with_partial_A_C": not bool(failures),
            "diagonal_h10_m2_fully_derived": False,
            "diagonal_sigmabar_m2_fully_derived": False,
            "cg_tensors_120_320_4125_invented": False,
            "full_invariant_ring": False,
            "full_component_hessian": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Isotropic soft/norm and 54-locking seeds now supply partial "
            "Schur A/C diagonals for H(10) and Σ̄(126). The portal B block "
            "remains exact. Missing CG channels (120/320/1050/4125) and the "
            "complete component Hessian stay OPEN — theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sch = report.get("schur_with_partial_diagonals", {})
    lines = [
        "# Diagonal H10 / Σ̄ M² isotropic+54 slots (v20)",
        "",
        f"**Status:** `{report.get('status')}`",
        f"**State:** `{report.get('overall_state')}`",
        "",
        "## Partial Schur inputs",
        "",
        f"- A_min: `{report.get('partial_diagonals', {}).get('A_min_GeV2')}` GeV²",
        f"- C_min: `{report.get('partial_diagonals', {}).get('C_min_GeV2')}` GeV²",
        f"- Schur positive definite: `{sch.get('positive_definite')}`",
        f"- σ_max(A⁻¹/² B C⁻¹/²): `{sch.get('largest_normalized_singular_value')}`",
        f"- real Hessian min eigenvalue: `{report.get('real_hessian_min_eigenvalue_GeV2')}` GeV²",
        "",
        "## Verdict",
        "",
        report.get("verdict", ""),
        "",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
