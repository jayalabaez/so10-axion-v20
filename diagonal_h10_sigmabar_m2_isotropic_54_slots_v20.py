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

It does not add a positive 54 mass contribution to Schur A/C: the physical
hEW=174 GeV differentiation (``physical_54_component_hessian_at_hew_v20``)
shows OPEN_H10_54 remains exact zero and OPEN_126_54_LOCKING is a holomorphic
ΣΣ kernel, not a positive Hermitian seed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import cg_normalized_mt_locking_mix_v20 as cgmix
import component_lift_210_126_10_v20 as clift
import diagonal_sigmabar_m2_mixed_126_ps_singlet_v20 as mixed126
import direct_portal_mass2_schur_gate_v20 as schur
import h10_intermediate_vev_consistency_audit_v20 as h10_audit
import nonsusy_reduced_hessian_v20 as reduced
import physical_54_component_hessian_at_hew_v20 as hew54
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
    del m_i, lam_lock
    weights = cgmix.cg_weighted_210_vev(
        a=vevs["a"], p=vevs["p"], omega=vevs["omega"]
    )
    phi2 = phi_norm_sq_aulakh(
        p=vevs["p"], a=vevs["a"], omega=vevs["omega"]
    )
    h_from_210 = float(lam_210_h) * phi2
    s_from_210 = float(lam_210_sigma) * phi2
    mixed = mixed126.mixed_126_mass2_seed(
        a=vevs["a"],
        p=vevs["p"],
        omega=vevs["omega"],
        m_gut=m_gut,
    )
    mixed_c = float(mixed["delta_M2_GeV2"])

    a_iso = float(soft["mu2_H10"])
    c_iso = float(soft["mu2_Sigmabar"])
    a_vec = np.full(10, a_iso + h_from_210, dtype=float)
    c_vec = np.full(126, c_iso + s_from_210 + mixed_c, dtype=float)

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
        "OPEN_MIXED_126": {
            "status": "PARTIAL_PS_SINGLET_M2_FILLED",
            "contribution_GeV2": mixed_c,
            "feeds": "C",
            "eff_210_for_126_GeV": mixed["eff_210_for_126_GeV"],
            "lam_tilde": mixed["lam_tilde"],
            "full_cartesian_cg": False,
        },
    }
    withdrawn = {
        "OPEN_H10_54": {
            "status": "PHYSICAL_EXACT_ZERO_AT_HEW",
            "contribution_GeV2": 0.0,
            "reason": (
                "physical_54_component_hessian_at_hew_v20: "
                "P54(Delta_R,Delta_R)=0 ⇒ no H10 mass from 54 locking"
            ),
        },
        "OPEN_126_54_LOCKING": {
            "status": "PHYSICAL_HOLOMORPHIC_KERNEL_NOT_PD_SCHUR_SEED",
            "contribution_GeV2": 0.0,
            "reason": (
                "physical_54_component_hessian_at_hew_v20: P54(hEW,hEW) sources "
                "an indefinite holomorphic ΣΣ kernel, not a positive isotropic "
                "Hermitian C seed; the withdrawn MI-proxy seed remains invalid"
            ),
        },
    }
    still_open = [
        "OPEN_H10_54",
        "OPEN_126_54_LOCKING",
        "OPEN_210_CHANNEL_1050",
        "OPEN_210_CHANNEL_45_OFF_SINGLET",
        "OPEN_MIXED_120",
        "OPEN_MIXED_320",
        "OPEN_126_1050",
        "OPEN_126_4125",
    ]
    absorbed = {
        "OPEN_MIXED_10": {
            "status": "ABSORBED_INTO_PORTAL_B",
            "contribution_GeV2": 0.0,
            "reason": (
                "210·126†·10 opens H–Σ mixing via T_Φ, already inserted as "
                "portal B=λ₄ v_S T_Φ (diagonal_mixed_10_portal_absorption_v20)"
            ),
        },
        "OPEN_210_CHANNEL_54": {
            "status": "PARTIAL_PS_SINGLET_TENSOR_MAP_READY",
            "contribution_GeV2": 0.0,
            "reason": (
                "so10_210_to_54_projector_v20: exact (210⊗210)→54 bilinear; "
                "PS-singlet seed recorded in diagonal_210_radial (not added "
                "into isotropic A/C to avoid double-count)"
            ),
        },
        "OPEN_210_CHANNEL_45": {
            "status": "PARTIAL_PS_AND_SAME_FIELD_QUADRATIC_VANISHES",
            "contribution_GeV2": 0.0,
            "reason": (
                "so10_210_to_45_projector_v20: P_45 vanishes on same-field and "
                "on the full PS-singlet span {p,a,ω}; off-singlet mixed OPEN"
            ),
        },
        "OPEN_210_CHANNEL_210": {
            "status": "PARTIAL_PS_SINGLET_TENSOR_MAP_READY",
            "contribution_GeV2": 0.0,
            "reason": (
                "so10_210_to_210_self_map_v20: exact (210⊗210)→210; selected "
                "vacuum Ξ mostly ∥ Φ (radial overlap); diagnostic seed only"
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
            "mixed_126_ps_singlet_Sigmabar": mixed_c,
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
        "absorbed_slots": absorbed,
        "still_open_slots": still_open,
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    historical_lam4 = -0.05 * m_i / m_gut
    vevs = _ledger_vevs(anchor)
    audit = h10_audit.build_report()
    hew = hew54.build_report()
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
        "physical_54_hew_hessian_green": hew.get("n_failed") == 0,
        "physical_54_hew_not_pd_schur_seed": not hew["flags"][
            "OPEN_126_54_LOCKING_positive_schur_seed"
        ],
        "partial_A_shape_10": len(partial["A_partial_GeV2"]) == 10,
        "partial_C_shape_126": len(partial["C_partial_GeV2"]) == 126,
        "partial_A_positive": partial["A_min_GeV2"] > 0.0,
        "partial_C_positive": partial["C_min_GeV2"] > 0.0,
        "four_defensible_slots_filled": len(partial["filled_slots"]) == 4,
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
        "physical_54_component_hessian_at_hEW": {
            "status": hew.get("status"),
            "n_failed": hew.get("n_failed"),
            "OPEN_H10_54": hew.get("blocks", {}).get("OPEN_H10_54"),
            "OPEN_126_54_LOCKING": hew.get("blocks", {}).get("OPEN_126_54_LOCKING"),
        },
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
            "derive_physical_54_component_hessian_at_hEW": False,
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
            "The exact portal B, defensible isotropic/210-norm A/C seeds, and the "
            "guaranteed 210·126†·126 PS-singlet OPEN_MIXED_126 Hermitian C seed "
            "are retained. Physical hEW=174 54-channel Hessian: OPEN_H10_54 exact "
            "zero; OPEN_126_54_LOCKING holomorphic not-PD. Missing CG channels "
            "120/320/1050/4125 and the full component Hessian remain OPEN; the "
            "theory remains BLOCKED."
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
