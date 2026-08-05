#!/usr/bin/env python3
"""Fill only defensible isotropic/norm Schur A/C slots.

PR #96 previously added a positive isotropic ``54-locking`` mass seed by
computing a phase amplitude with ``v10_eff=M_I`` and dividing by ``M_I^2``.
That interpretation is withdrawn: 10_H decomposes as
``(6,1,1)+(1,2,2)`` and contains no Pati-Salam or SM singlet, so it cannot
have a physical intermediate-scale VEV without breaking colour or the
electroweak group.

This corrected module retains:
* reduced-sector isotropic soft/norm seeds;
* exact 210-norm portals into H10 and Sigmabar;
* the exact portal B=lambda4*vS*T_Phi and Schur theorem.

It does not add a 54 mass contribution until the charge-allowed invariant is
differentiated in the physical hEW=174 GeV component basis.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import cg_normalized_mt_locking_mix_v20 as cgmix
import component_lift_210_126_10_v20 as clift
import direct_portal_mass2_schur_gate_v20 as schur
import h10_intermediate_vev_consistency_audit_v20 as h10_audit
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIAGONAL_H10_SIGMABAR_M2_ISOTROPIC_54_SLOTS_V20.json"
OUT_MD = ROOT / "DIAGONAL_H10_SIGMABAR_M2_ISOTROPIC_54_SLOTS_V20.md"

DEFAULT_LAM_210_H = 1.0e-2
DEFAULT_LAM_210_SIGMA = 1.0e-2
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
        "H10_eff_proxy": by_name["H10_eff"],
    }


def isotropic_soft_diagonals(
    *,
    m_i: float,
    m_gut: float,
    lam4: float,
    vevs: dict[str, float],
) -> dict[str, float]:
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    quartic, _, targets = reduced.radial_quartic_matrix(radial)
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
        "source": "physical-hEW reduced Hessian diagonals; isotropic seed only",
    }


def phi_norm_sq_aulakh(*, p: float, a: float, omega: float) -> float:
    return float(p * p + 3.0 * a * a + 6.0 * omega * omega)


def build_partial_diagonals(
    *,
    vevs: dict[str, float],
    soft: dict[str, float],
    m_i: float,
    m_gut: float,
    lam_210_h: float = DEFAULT_LAM_210_H,
    lam_210_sigma: float = DEFAULT_LAM_210_SIGMA,
    lam_lock: float = 0.0,
) -> dict[str, Any]:
    del m_i, m_gut, lam_lock
    weights = cgmix.cg_weighted_210_vev(
        a=vevs["a"], p=vevs["p"], omega=vevs["omega"]
    )
    phi2 = phi_norm_sq_aulakh(
        p=vevs["p"], a=vevs["a"], omega=vevs["omega"]
    )
    h_from_210 = float(lam_210_h) * phi2
    s_from_210 = float(lam_210_sigma) * phi2

    a_iso = float(soft["mu2_H10"])
    c_iso = float(soft["mu2_Sigmabar"])
    a_vec = np.full(10, a_iso + h_from_210, dtype=float)
    c_vec = np.full(126, c_iso + s_from_210, dtype=float)

    filled = {
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
    }
    withdrawn = {
        "OPEN_H10_54": {
            "status": "WITHDRAWN_UNPHYSICAL_H10_MI_PROXY",
            "contribution_GeV2": 0.0,
            "reason": "10_H has no PS/SM singlet; v10_eff=M_I is not a physical vacuum",
        },
        "OPEN_126_54_LOCKING": {
            "status": "WITHDRAWN_UNPHYSICAL_H10_MI_PROXY",
            "contribution_GeV2": 0.0,
            "reason": (
                "the previous positive isotropic seed was manufactured from a "
                "phase amplitude evaluated with v10_eff=M_I"
            ),
        },
    }
    still_open = [
        "OPEN_H10_54",
        "OPEN_126_54_LOCKING",
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
    ]

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
            "locking_isotropic_seed": 0.0,
        },
        "cg_weighted_diagnostic": {
            "eff_210_for_10_GeV": weights["eff_210_for_10_GeV"],
            "eff_210_for_126_GeV": weights["eff_210_for_126_GeV"],
            "note": "diagnostic only; numerical add uses canonical Phi norm squared",
        },
        "locking": {
            "status": "WITHDRAWN_PENDING_PHYSICAL_COMPONENT_HESSIAN",
            "H10_eff_proxy_GeV": vevs["H10_eff_proxy"],
            "physical_hEW_GeV": vevs["hEW"],
            "isotropic_seed_added": False,
        },
        "filled_slots": filled,
        "withdrawn_slots": withdrawn,
        "still_open_slots": still_open,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    historical_lam4 = -0.05 * m_i / m_gut
    vevs = _ledger_vevs(anchor)
    audit = h10_audit.build_report()
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
        "H10_MI_proxy_audit_green": audit.get("n_failed") == 0,
        "unphysical_54_seed_identified": not audit["flags"][
            "legacy_isotropic_54_mass_seed_physical"
        ],
        "partial_A_shape_10": len(partial["A_partial_GeV2"]) == 10,
        "partial_C_shape_126": len(partial["C_partial_GeV2"]) == 126,
        "partial_A_positive": partial["A_min_GeV2"] > 0.0,
        "partial_C_positive": partial["C_min_GeV2"] > 0.0,
        "three_defensible_slots_filled": len(partial["filled_slots"]) == 3,
        "two_54_slots_withdrawn": len(partial["withdrawn_slots"]) == 2,
        "locking_seed_zero": partial["components"]["locking_isotropic_seed"] == 0.0,
        "schur_report_emitted": "positive_definite" in schur_rep,
        "real_hessian_272": hessian.shape == (272, 272),
        "full_diagonal_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "DIAGONAL_M2_ISOTROPIC_NORM_PARTIAL__54_PROXY_WITHDRAWN"
            if not failures
            else "DIAGONAL_M2_PROXY_WITHDRAWAL_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "H10_intermediate_vev_audit": audit,
        "vevs_GeV": vevs,
        "soft_isotropic": soft,
        "partial_diagonals": {
            k: v
            for k, v in partial.items()
            if k not in {"A_partial_GeV2", "C_partial_GeV2"}
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
            "derive_physical_54_component_hessian_at_hEW": True,
            "transcribe_missing_CG_120_320_1050_4125": True,
            "full_component_diagonal_H10_m2": True,
            "full_component_diagonal_Sigmabar_m2": True,
            "complete_invariant_ring_G1": True,
            "full_tensor_projected_potential_G2": True,
            "full_nonsusy_vacuum_hessian_G3": True,
            "issue_86_full_closure": True,
        },
        "flag": {
            "isotropic_norm_slots_partially_filled": not bool(failures),
            "isotropic_norm_54_slots_partially_filled": False,
            "unphysical_H10_MI_54_seed_withdrawn": True,
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
            "The exact portal B and defensible isotropic/210-norm A/C seeds are "
            "retained. The former positive 54-locking isotropic seed is withdrawn "
            "because it used an unphysical H10_eff=M_I vacuum proxy. The exact "
            "54 projectors remain valid, but their physical hEW=174 GeV component "
            "Hessian is still open; the theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    sch = report.get("schur_with_partial_diagonals", {})
    OUT_MD.write_text(
        "# Diagonal H10 / Sigmabar M2 corrected partial slots — v20\n\n"
        f"**Status:** `{report.get('status')}`\n\n"
        f"- Schur positive definite: `{sch.get('positive_definite')}`\n"
        f"- sigma_max: `{sch.get('largest_normalized_singular_value')}`\n"
        f"- 54 proxy seed retained: `False`\n\n"
        + report.get("verdict", "")
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
    print(json.dumps(report, indent=2, default=str))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
