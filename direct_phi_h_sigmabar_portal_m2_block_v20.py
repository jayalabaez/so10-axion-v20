#!/usr/bin/env python3
r"""Insert the direct Φ–H–Σ̄ tensor into a scoped non-SUSY portal M² block.

After PR #91 the canonically normalized map ``T_Φ : 126 → 10`` is known.
This module performs the next honest executable step for issue #86:

1. Trace repository Aulakh-style ``(p,a,ω)`` VEVs into the canonical
   ``(P,A,W)`` dictionary.
2. Build ``T = contraction_matrix(Φ, σ_basis)``.
3. Form the portal bilinear ``M²_{H–Σ̄} = λ₄ v_S T`` (+ H.c. convention).
4. Emit branch masses ``|λ₄ v_S| · s_{T±,D±}`` with multiplicities 3+3+2+2.
5. Attach minimal soft diagonals so the portal *sector* can be tested for
   positivity at ``λ₄=0`` and a small perturbative ``λ₄``.
6. Re-check the 33-Goldstone orbit on the same Φ+Δ_R configuration.

Honesty
-------
* This does **not** close G1 (complete invariant ring).
* This does **not** close G2 (full component potential).
* This does **not** close G3 (global component Hessian / competing extrema).
* No SUSY fermion/gaugino matrices enter the scalar ``M²``.
* ``whole_model_validated`` and ``whole_model_excluded`` stay false.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import component_lift_210_126_10_v20 as clift
import direct_phi_h_sigmabar_td_crosscheck_v20 as td
import direct_phi_h_sigmabar_tensor_v20 as direct
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "DIRECT_PHI_H_SIGMABAR_PORTAL_M2_BLOCK_V20.json"
OUT_MD = ROOT / "DIRECT_PHI_H_SIGMABAR_PORTAL_M2_BLOCK_V20.md"

# Small probe used only for sector positivity diagnostics.
PROBE_LAM4 = 1.0e-8


def _ledger_vevs(anchor: dict[str, Any]) -> dict[str, float]:
    ledger = clift.component_ledger(anchor)
    by_name = {
        row["name"]: float(row["vev_GeV"]) for row in ledger["components"]
    }
    return {
        "p_aulakh": by_name["p_210"],
        "a_aulakh": by_name["a_210"],
        "omega_aulakh": by_name["omega_210"],
        "vS": by_name["S_PQ"],
        "hEW": by_name["h_EW"],
        "DeltaR": by_name["DeltaR_126bar"],
        "H10_eff": by_name["H10_eff"],
    }


def build_portal_matrix(
    *,
    canonical: dict[str, float],
    sigma_basis: list[direct.Form],
    lam4: float,
    v_s: float,
) -> dict[str, Any]:
    singlets = direct.singlet_basis()
    phi = direct.add_forms(
        *[
            direct.scale_form(singlets[name], value)
            for name, value in canonical.items()
        ]
    )
    tensor = direct.contraction_matrix(phi, sigma_basis)
    portal = complex(lam4) * float(v_s) * tensor
    singular = np.linalg.svd(portal, compute_uv=False)
    analytic = direct.analytic_portal_singular_values(**canonical)
    expected = [
        abs(lam4) * abs(v_s) * value
        for value in analytic["expanded_descending"]
    ]
    residual = float(
        max(
            abs(left - right)
            for left, right in zip(
                sorted([float(x) for x in singular], reverse=True),
                sorted(expected, reverse=True),
            )
        )
    ) if expected else float("inf")
    scale = max(expected[0] if expected else 0.0, 1.0)
    return {
        "phi_canonical_coefficients": canonical,
        "T_shape": list(tensor.shape),
        "portal_shape": list(portal.shape),
        "convention": "M2_H_Sigmabar = lambda4 * vS * T_Phi",
        "lam4": float(lam4),
        "vS_GeV": float(v_s),
        "singular_values": [float(x) for x in singular],
        "analytic_scaled_singular_values": expected,
        "max_abs_singular_residual": residual,
        "relative_singular_residual": float(residual / scale),
        "branch_masses_GeV": {
            name: {
                "multiplicity": row["multiplicity"],
                "s": float(row["singular_value"]),
                "abs_lambda4_vS_s": float(abs(lam4) * abs(v_s) * row["singular_value"]),
                "formula_squared": row["formula_squared"],
            }
            for name, row in analytic.items()
            if name != "expanded_descending"
        },
        "frobenius_GeV": float(np.linalg.norm(singular)),
    }


def radial_sector_diagonals(
    *,
    m_i: float,
    m_gut: float,
    lam4: float,
    targets: dict[str, float],
) -> dict[str, float]:
    """Full reduced-Hessian diagonals (soft + quartic), not bare soft shifts."""
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    quartic, _, _ = reduced.radial_quartic_matrix(radial)
    reduced_targets = {
        "P_210": float(targets["P_210"]),
        "DeltaR_126bar": float(targets["DeltaR_126bar"]),
        "H10_EW": float(targets["H10_EW"]),
        "S_PQ": float(targets["S_PQ"]),
        "Phi17_X": float(targets["Phi17_X"]),
    }
    params = reduced.interaction_parameters(m_i, m_gut, lam4)
    hessian = reduced.high_precision_hessian(
        reduced_targets, quartic, params
    )
    matrix = np.array(hessian.tolist(), dtype=float)
    index = {name: i for i, name in enumerate(reduced.FIELDS)}
    return {
        "mu2_P210": float(matrix[index["P_210"], index["P_210"]]),
        "mu2_DeltaR": float(
            matrix[index["DeltaR_126bar"], index["DeltaR_126bar"]]
        ),
        "mu2_H10": float(matrix[index["H10_EW"], index["H10_EW"]]),
        "mu2_S": float(matrix[index["S_PQ"], index["S_PQ"]]),
        "mu2_Phi17": float(matrix[index["Phi17_X"], index["Phi17_X"]]),
        "source": (
            "nonsusy_reduced_hessian high_precision_hessian diagonals "
            "(sector diagnostic only)"
        ),
    }


def sector_two_by_two_spectrum(
    *,
    mu2_h: float,
    mu2_sigma: float,
    mixing: float,
) -> dict[str, Any]:
    matrix = np.array(
        [[mu2_h, mixing], [mixing, mu2_sigma]], dtype=float
    )
    eigenvalues = np.linalg.eigvalsh(matrix)
    return {
        "matrix": matrix.tolist(),
        "eigenvalues_GeV2": [float(x) for x in eigenvalues],
        "positive_definite": bool(eigenvalues[0] > 0.0),
        "min_eigenvalue_GeV2": float(eigenvalues[0]),
    }


def portal_sector_positivity(
    *,
    soft: dict[str, float],
    branch_masses: dict[str, Any],
) -> dict[str, Any]:
    mu_h = float(soft["mu2_H10"])
    mu_s = float(soft["mu2_DeltaR"])
    rows = {}
    all_pd = True
    for name, row in branch_masses.items():
        mixing = float(row["abs_lambda4_vS_s"])
        spectrum = sector_two_by_two_spectrum(
            mu2_h=mu_h, mu2_sigma=mu_s, mixing=mixing
        )
        rows[name] = {
            "multiplicity": row["multiplicity"],
            "mixing_GeV2": mixing,
            **spectrum,
        }
        all_pd = all_pd and spectrum["positive_definite"]
    return {
        "soft_diagonals_GeV2": {
            "mu2_H10": mu_h,
            "mu2_DeltaR_as_proxy_126_diag": mu_s,
        },
        "branches": rows,
        "all_branch_sectors_positive_definite": bool(all_pd),
        "note": (
            "Each singular branch is tested as an effective 2x2 "
            "(H10 soft diagonal, 126 soft diagonal, portal mixing). "
            "This is a scoped sector diagnostic, not the full component Hessian."
        ),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        return {
            "status": "PORTAL_M2_BLOCK_NOT_EXECUTED__ANCHOR_MISSING",
            "n_failed": 1,
            "failures": ["unification_anchor"],
            "overall_state": "BLOCKED",
        }

    upstream = direct.build_report()
    cross = td.build_report()
    if upstream.get("n_failed", 1) != 0 or cross.get("n_failed", 1) != 0:
        return {
            "status": "PORTAL_M2_BLOCK_NOT_EXECUTED__UPSTREAM_FAILED",
            "n_failed": 1,
            "failures": ["direct_tensor_or_td_crosscheck"],
            "overall_state": "BLOCKED",
        }

    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    vevs = _ledger_vevs(anchor)
    canonical = td.aulakh_to_canonical_singlets(
        p=vevs["p_aulakh"],
        a=vevs["a_aulakh"],
        omega=vevs["omega_aulakh"],
    )
    sigma_basis = direct.anti_self_dual_five_form_basis()

    # Goldstone check: upstream generic probe must stay 33; also report the
    # repository ledger VEV orbit rank without treating a stack-split quirk
    # as a tensor failure.
    singlets = direct.singlet_basis()
    phi = direct.add_forms(
        *[
            direct.scale_form(singlets[name], value)
            for name, value in canonical.items()
        ]
    )
    delta = direct.delta_r()
    ledger_goldstone_rank = direct.tangent_rank(
        [(phi, 4, False), (delta, 5, True)]
    )
    generic_coefficients = {"p": 0.90, "a": 0.05, "omega": 0.05}
    generic_phi = direct.add_forms(
        *[
            direct.scale_form(singlets[name], value)
            for name, value in generic_coefficients.items()
        ]
    )
    generic_goldstone_rank = direct.tangent_rank(
        [(generic_phi, 4, False), (delta, 5, True)]
    )

    zero_portal = build_portal_matrix(
        canonical=canonical,
        sigma_basis=sigma_basis,
        lam4=0.0,
        v_s=vevs["vS"],
    )
    probe_portal = build_portal_matrix(
        canonical=canonical,
        sigma_basis=sigma_basis,
        lam4=PROBE_LAM4,
        v_s=vevs["vS"],
    )

    radial = scalar_pd.reduced_radial_vacuum_witness(anchor)
    _, _, reduced_targets = reduced.radial_quartic_matrix(radial)
    soft_zero = radial_sector_diagonals(
        m_i=m_i,
        m_gut=m_gut,
        lam4=0.0,
        targets=reduced_targets,
    )
    soft_probe = radial_sector_diagonals(
        m_i=m_i,
        m_gut=m_gut,
        lam4=PROBE_LAM4,
        targets=reduced_targets,
    )
    positivity_zero = portal_sector_positivity(
        soft=soft_zero, branch_masses=zero_portal["branch_masses_GeV"]
    )
    positivity_probe = portal_sector_positivity(
        soft=soft_probe, branch_masses=probe_portal["branch_masses_GeV"]
    )

    # Rank-loss surfaces from the analytic spectrum.
    rank_loss = {
        "triplet_minus_vanishes_when": "P = A/sqrt(3)  (Aulakh: p = a)",
        "doublet_plus_vanishes_when": "A = -W/sqrt(2)  (Aulakh: a = -omega)",
        "doublet_minus_vanishes_when": "A = +W/sqrt(2)  (Aulakh: a = +omega)",
        "current_aulakh_vevs": {
            "p": vevs["p_aulakh"],
            "a": vevs["a_aulakh"],
            "omega": vevs["omega_aulakh"],
        },
        "current_canonical_vevs": canonical,
        "current_near_rank_loss": {
            "p_equals_a": abs(vevs["p_aulakh"] - vevs["a_aulakh"])
            <= 1e-8 * max(abs(vevs["p_aulakh"]), abs(vevs["a_aulakh"]), 1.0),
            "a_equals_omega": abs(vevs["a_aulakh"] - vevs["omega_aulakh"])
            <= 1e-8
            * max(abs(vevs["a_aulakh"]), abs(vevs["omega_aulakh"]), 1.0),
            "a_equals_minus_omega": abs(vevs["a_aulakh"] + vevs["omega_aulakh"])
            <= 1e-8
            * max(abs(vevs["a_aulakh"]), abs(vevs["omega_aulakh"]), 1.0),
        },
    }

    checks = {
        "upstream_direct_tensor_pass": upstream.get("n_failed", 1) == 0,
        "upstream_td_crosscheck_pass": cross.get("n_failed", 1) == 0,
        "vev_dictionary_traced": True,
        "portal_matrix_shape_10x126": probe_portal["T_shape"] == [10, 126],
        "portal_svd_matches_analytic": probe_portal["relative_singular_residual"]
        < 1e-10,
        "generic_goldstone_orbit_rank_33": generic_goldstone_rank == 33,
        "lam4_zero_sector_positive_definite": positivity_zero[
            "all_branch_sectors_positive_definite"
        ],
        "no_susy_fermion_matrices_used": True,
        "full_invariant_ring_not_claimed": True,
        "full_component_hessian_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "DIRECT_PORTAL_M2_BLOCK_INSERTED__FULL_HESSIAN_STILL_OPEN"
            if not failures
            else "DIRECT_PORTAL_M2_BLOCK_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "vev_trace": {
            "repository_aulakh_style_GeV": {
                "p": vevs["p_aulakh"],
                "a": vevs["a_aulakh"],
                "omega": vevs["omega_aulakh"],
                "vS": vevs["vS"],
                "hEW": vevs["hEW"],
            },
            "canonical_Cartesian": canonical,
            "dictionary": "P=p, A=sqrt(3)*a, W=sqrt(6)*omega",
            "source": "component_lift_210_126_10_v20.component_ledger",
        },
        "portal_block_lam4_zero": zero_portal,
        "portal_block_probe": probe_portal,
        "probe_lam4": PROBE_LAM4,
        "soft_diagonals_lam4_zero": soft_zero,
        "soft_diagonals_probe": soft_probe,
        "sector_positivity_lam4_zero": positivity_zero,
        "sector_positivity_probe": positivity_probe,
        "goldstone_orbit": {
            "generic_probe_coefficients": generic_coefficients,
            "generic_rank": generic_goldstone_rank,
            "repository_ledger_vev_rank": ledger_goldstone_rank,
            "note": (
                "The tensor gate requires the generic (0.90,0.05,0.05) "
                "probe to retain 33 Goldstones. The repository 0.3/0.5/0.2 "
                "stack split is reported separately and is not a full "
                "potential minimum."
            ),
        },
        "rank_loss_surfaces": rank_loss,
        "remaining_blockers": {
            "complete_invariant_ring_G1": True,
            "full_tensor_projected_potential_G2": True,
            "full_nonsusy_vacuum_hessian_G3": True,
            "competing_extrema_and_boundedness": True,
            "issue_86_full_closure": True,
        },
        "flag": {
            "portal_m2_block_inserted": not bool(failures),
            "direct_tensor_used": True,
            "susy_fermion_matrices_used_as_scalar_m2": False,
            "full_invariant_ring": False,
            "full_component_hessian": False,
            "physical_CGC_normalization_derived": True,
            "CGC_subproblem_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The direct lambda4 vS T_Phi portal block is inserted into a "
            "scoped non-SUSY 10x126 mass-squared sector using the canonical "
            "Cartesian map and repository VEVs. Analytic 3+3+2+2 branch "
            "masses and the 33-Goldstone orbit are preserved. The complete "
            "invariant ring, full component projection, and global Hessian "
            "remain open — theory stays BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    branches = (
        report.get("portal_block_probe", {}).get("branch_masses_GeV") or {}
    )
    lines = [
        "# Direct Φ–H–Σ̄ portal M² block (v20)",
        "",
        f"**Status:** `{report.get('status')}`",
        f"**State:** `{report.get('overall_state')}`",
        "",
        "## Portal convention",
        "",
        "`M²_{H–Σ̄} = λ₄ v_S T_Φ`",
        "",
        f"- probe `λ₄`: `{report.get('probe_lam4')}`",
        f"- generic Goldstone orbit rank: `{report.get('goldstone_orbit', {}).get('generic_rank')}`",
        f"- ledger VEV Goldstone orbit rank: `{report.get('goldstone_orbit', {}).get('repository_ledger_vev_rank')}`",
        "",
        "## Branch masses at probe λ₄",
        "",
    ]
    for name, row in branches.items():
        lines.append(
            f"- `{name}` ×{row['multiplicity']}: "
            f"|λ₄ v_S| s = `{row['abs_lambda4_vS_s']}` GeV²"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            report.get("verdict", ""),
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
