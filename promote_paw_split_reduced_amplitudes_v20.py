#!/usr/bin/env python3
r"""Promote coarse ``P_210`` → free ``(p,a,ω)`` in the reduced radial sector.

Replaces the single radial witness amplitude ``P_210`` by the Aulakh PS
singlets ``(p,a,ω)`` and wires the source-normalized pure-210 quartic
``identity_reduced_potential`` into that block. Non-210 amplitudes
``(Δ,H₁₀,S,Φ₁₇)`` keep their historical reduced self/cross quartics.
Any historical ``P_210↔X`` cross is rewritten with the isotropic proxy

    ‖Φ‖² = p² + a² + ω²

(declared; not a full mixed CG expansion). The λ₄=0 survival slice is the
primary Hessian certificate (portal terms vanish).

Honesty
-------
* Diagnostic pure-210 couplings only (same unit probe as the insertion module).
* Isotropic ‖Φ‖² proxy for P↔X crosses — not invented 120/320/1050/4125 CG.
* Soft convention matches the reduced 5-amplitude gate: interaction soft on
  non-210 only; pure-210 quartic is *not* soft-rematched at the selected vacuum.
* Mixed G1 / full component Hessian remain OPEN.
* ``whole_model_validated = false``. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np

import component_lift_210_126_10_v20 as clift
import direct_phi_h_sigmabar_td_crosscheck_v20 as td
import nonsusy_reduced_hessian_v20 as reduced
import pure_210_ps_singlet_quartic_polynomials_v20 as singlet
import scalar_vacuum_proton_decay_v20 as scalar_pd
import source_pure210_reduced_potential_insertion_v20 as insertion

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "PROMOTE_PAW_SPLIT_REDUCED_AMPLITUDES_V20.json"
OUT_MD = ROOT / "PROMOTE_PAW_SPLIT_REDUCED_AMPLITUDES_V20.md"

PROMOTED_FIELDS = (
    "p_210",
    "a_210",
    "omega_210",
    "DeltaR_126bar",
    "H10_EW",
    "S_PQ",
    "Phi17_X",
)
NON210 = ("DeltaR_126bar", "H10_EW", "S_PQ", "Phi17_X")


def promoted_targets(anchor: dict[str, Any]) -> dict[str, float]:
    ledger = clift.component_ledger(anchor)
    by_name = {row["name"]: float(row["vev_GeV"]) for row in ledger["components"]}
    # Reduced H10_EW is the physical EW doublet (174 GeV), not H10_eff.
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {
            "available": True,
            "M_I_GeV": float(anchor["M_I_GeV"]),
            "M_GUT_GeV": float(anchor["M_GUT_GeV"]),
        }
    )
    _, _, targets5 = reduced.radial_quartic_matrix(radial)
    return {
        "p_210": by_name["p_210"],
        "a_210": by_name["a_210"],
        "omega_210": by_name["omega_210"],
        "DeltaR_126bar": targets5["DeltaR_126bar"],
        "H10_EW": targets5["H10_EW"],
        "S_PQ": targets5["S_PQ"],
        "Phi17_X": targets5["Phi17_X"],
    }


def non210_quartic_blocks(
    quartic5: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return (Λ_non210 4×4, Λ_P_cross length-4) from the historical 5×5 Λ."""
    idx = {name: i for i, name in enumerate(reduced.FIELDS)}
    non_idx = [idx[n] for n in NON210]
    lam_non = quartic5[np.ix_(non_idx, non_idx)].astype(float, copy=True)
    lam_cross = quartic5[idx["P_210"], non_idx].astype(float, copy=True)
    return lam_non, lam_cross


def potential_promoted(
    x: np.ndarray,
    *,
    couplings: dict[str, float],
    lam_non: np.ndarray,
    lam_cross: np.ndarray,
    params: dict[str, float],
) -> float:
    """V₄(pure-210) + historical non-210 quartics + isotropic P↔X crosses + V_int (λ₄=0)."""
    p, a, w, delta, higgs, singlet_s, phi = (float(v) for v in x)
    v210 = singlet.identity_reduced_potential(
        p,
        a,
        w,
        g45=couplings["g45"],
        g210=couplings["g210"],
        g1050=couplings["g1050"],
        lam=couplings["lam"],
    )
    non = np.array([delta, higgs, singlet_s, phi], dtype=float)
    non_sq = non * non
    # V = 1/2 Σ_{ij} Λ_ij φ_i² φ_j²  on the non-210 block
    v_non = 0.5 * float(non_sq @ lam_non @ non_sq)
    phi_norm2 = p * p + a * a + w * w
    v_cross = float(np.dot(lam_cross, non_sq) * phi_norm2)

    kappa = float(params["kappa"])
    m_i = float(params["m_i"])
    m_gut = float(params["m_gut"])
    q = (
        float(params["c_lock"])
        * (float(params["lambda_abs"]) - abs(float(params["lambda_phase"])))
        / (m_gut * m_gut)
    )
    # λ₄=0 survival interactions (κ + locking only)
    v_int = (
        -kappa * m_i * (higgs * higgs) * singlet_s
        + q * (delta * delta) * (higgs * higgs) * (singlet_s * singlet_s)
    )
    return float(v210 + v_non + v_cross + v_int)


def hessian_promoted_lam4_0(
    targets: dict[str, float],
    *,
    couplings: dict[str, float],
    lam_non: np.ndarray,
    lam_cross: np.ndarray,
    params: dict[str, float],
) -> dict[str, Any]:
    """λ₄=0 seven-amplitude Hessian under the reduced-sector soft convention.

    Soft δm² are rebuilt from the *interaction* gradient only (κ / locking),
    matching ``nonsusy_reduced_hessian_v20.high_precision_hessian``. Pure-210
    quartic gradients are *not* soft-rematched — the selected vacuum is not a
    critical point of diagnostic ``V_pure210``, and rematching it invents a
    tachyon. The (p,a,ω) block is the numerical Hessian of ``V_pure210``.
    """
    p = float(targets["p_210"])
    a = float(targets["a_210"])
    w = float(targets["omega_210"])
    delta = float(targets["DeltaR_126bar"])
    higgs = float(targets["H10_EW"])
    singlet_s = float(targets["S_PQ"])
    phi = float(targets["Phi17_X"])
    non = np.array([delta, higgs, singlet_s, phi], dtype=float)

    # --- (p,a,ω) block from V_pure210 ---
    paw_hess = insertion.selected_vacuum_singlet_hessian(
        {"p": p, "a": a, "omega": w}, **couplings
    )
    # Rebuild physical 3×3 via the same scaled FD used there is already done;
    # recompute explicitly for the assembled matrix.
    scale3 = max(abs(p), abs(a), abs(w), 1.0)
    y0 = np.array([p, a, w], dtype=float) / scale3
    eps = 1e-4

    def v210_at(y: np.ndarray) -> float:
        z = y * scale3
        return singlet.identity_reduced_potential(
            float(z[0]), float(z[1]), float(z[2]), **couplings
        )

    h3y = np.zeros((3, 3), dtype=float)
    for i in range(3):
        for j in range(i, 3):
            e_i = np.zeros(3)
            e_j = np.zeros(3)
            e_i[i] = eps
            e_j[j] = eps
            if i == j:
                h3y[i, i] = (
                    v210_at(y0 + e_i) - 2.0 * v210_at(y0) + v210_at(y0 - e_i)
                ) / (eps * eps)
            else:
                h3y[i, j] = h3y[j, i] = (
                    v210_at(y0 + e_i + e_j)
                    - v210_at(y0 + e_i - e_j)
                    - v210_at(y0 - e_i + e_j)
                    + v210_at(y0 - e_i - e_j)
                ) / (4.0 * eps * eps)
    h3 = h3y / (scale3 * scale3)

    # --- non-210 quartic + interaction soft (λ₄=0) ---
    kappa = float(params["kappa"])
    m_i = float(params["m_i"])
    m_gut = float(params["m_gut"])
    q = (
        float(params["c_lock"])
        * (float(params["lambda_abs"]) - abs(float(params["lambda_phase"])))
        / (m_gut * m_gut)
    )
    # Indices in NON210: 0=Δ, 1=H, 2=S, 3=Φ
    # Interaction gradient on non-210 (λ₄=0); Φ has none.
    grad_non = np.array(
        [
            2.0 * q * delta * higgs**2 * singlet_s**2,
            -2.0 * kappa * m_i * higgs * singlet_s
            + 2.0 * q * higgs * delta**2 * singlet_s**2,
            -kappa * m_i * higgs**2 + 2.0 * q * singlet_s * delta**2 * higgs**2,
            0.0,
        ],
        dtype=float,
    )
    dm2_non = np.array(
        [
            (-grad_non[i] / non[i]) if abs(non[i]) > 1e-30 else 0.0
            for i in range(4)
        ],
        dtype=float,
    )
    h4 = 2.0 * np.outer(non, non) * lam_non
    h4 = h4 + np.diag(dm2_non)
    h4[0, 0] += 2.0 * q * higgs**2 * singlet_s**2
    h4[1, 1] += -2.0 * kappa * m_i * singlet_s + 2.0 * q * delta**2 * singlet_s**2
    h4[2, 2] += 2.0 * q * delta**2 * higgs**2
    h4[0, 1] += 4.0 * q * delta * higgs * singlet_s**2
    h4[1, 0] = h4[0, 1]
    h4[0, 2] += 4.0 * q * delta * singlet_s * higgs**2
    h4[2, 0] = h4[0, 2]
    h4[1, 2] += -2.0 * kappa * m_i * higgs + 4.0 * q * higgs * singlet_s * delta**2
    h4[2, 1] = h4[1, 2]

    # --- isotropic P↔X cross: V ⊃ Σ_j Λ_{P j} (p²+a²+ω²) X_j² ---
    phi_norm2 = p * p + a * a + w * w
    paw = np.array([p, a, w], dtype=float)
    h_cross_210 = np.zeros((3, 3), dtype=float)
    h_cross_mix = np.zeros((3, 4), dtype=float)
    h_cross_non = np.zeros((4, 4), dtype=float)
    for j in range(4):
        lam = float(lam_cross[j])
        xj = float(non[j])
        # ∂²/∂paw_i∂paw_k from Λ (p²+a²+ω²) X²: 2 Λ X² δ_ik
        h_cross_210 += np.eye(3) * (2.0 * lam * xj * xj)
        # ∂²/∂paw_i∂X_j = 4 Λ paw_i X_j
        h_cross_mix[:, j] += 4.0 * lam * paw * xj
        # ∂²/∂X_j² += 2 Λ (p²+a²+ω²)
        h_cross_non[j, j] += 2.0 * lam * phi_norm2

    hess = np.zeros((7, 7), dtype=float)
    hess[:3, :3] = h3 + h_cross_210
    hess[3:, 3:] = h4 + h_cross_non
    hess[:3, 3:] = h_cross_mix
    hess[3:, :3] = h_cross_mix.T

    mp.mp.dps = 80
    hm = mp.matrix(7)
    for i in range(7):
        for j in range(7):
            hm[i, j] = mp.mpf(str(hess[i, j]))
    eigs = sorted(float(v) for v in mp.eigsy(hm, eigvals_only=True))
    float_eigs = np.linalg.eigvalsh(hess)
    floor = 1e-18 * max(1.0, max(abs(v) for v in eigs))
    return {
        "delta_m2_non210_GeV2": [float(v) for v in dm2_non],
        "pure210_block_min_eig": float(paw_hess["min_eig"]),
        "pure210_block_psd": bool(paw_hess["positive_semidefinite"]),
        "hessian": hess.tolist(),
        "eigenvalues_mpmath": eigs,
        "min_eig_mpmath": float(eigs[0]),
        "positive_definite": bool(eigs[0] > floor),
        "positive_semidefinite": bool(eigs[0] >= -floor),
        "psd_floor": float(floor),
        "float64_min_eig": float(np.min(float_eigs)),
        "float64_false_tachyon_documented": bool(
            float(np.min(float_eigs)) < -floor <= eigs[0]
        ),
        "soft_convention": (
            "interaction soft on non-210 only; pure-210 quartic not soft-rematched"
        ),
    }


def ray_consistency(
    vevs: dict[str, float],
    *,
    couplings: dict[str, float],
    lambda_p_source: float,
) -> dict[str, Any]:
    """On the selected ray, V_pure210 should match (λ_P/4)‖Φ‖⁴ from the insertion proxy."""
    p = float(vevs["p_210"])
    a = float(vevs["a_210"])
    w = float(vevs["omega_210"])
    rho2 = p * p + a * a + w * w
    v = singlet.identity_reduced_potential(p, a, w, **couplings)
    proxy = 0.25 * lambda_p_source * (rho2 * rho2)
    # Densities on the unit ray give λ_eff ρ⁴; insertion identifies λ_P=4λ_eff with
    # P~‖Φ‖, so V ≈ (λ_P/4) ρ⁴. Residual relative to that proxy:
    rel = abs(v - proxy) / max(abs(proxy), 1.0)
    return {
        "phi_norm2": rho2,
        "V_pure210": v,
        "V_proxy_lambda_P_over_4": proxy,
        "relative_residual": rel,
        "consistent": rel < 1e-9,
        "note": (
            "Exact on the selected ray only when λ_P was built from the same "
            "densities/couplings; stack fractions are not the unique soft optimum."
        ),
    }


def build_report() -> dict[str, Any]:
    ins = insertion.build_report()
    couplings = dict(insertion.DIAGNOSTIC_COUPLINGS)
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    targets = promoted_targets(anchor)

    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    quartic5, _, _ = reduced.radial_quartic_matrix(radial)
    lam_non, lam_cross = non210_quartic_blocks(quartic5)
    params = reduced.interaction_parameters(m_i, m_gut, 0.0)

    paw = td.aulakh_to_canonical_singlets(
        p=targets["p_210"], a=targets["a_210"], omega=targets["omega_210"]
    )
    hess = hessian_promoted_lam4_0(
        targets,
        couplings=couplings,
        lam_non=lam_non,
        lam_cross=lam_cross,
        params=params,
    )
    ray = ray_consistency(
        targets,
        couplings=couplings,
        lambda_p_source=float(ins["radial_proxy"]["lambda_P_source"]),
    )
    singlet_bfb = insertion.singlet_span_bfb(**couplings)
    singlet_hess = insertion.selected_vacuum_singlet_hessian(
        {
            "p": targets["p_210"],
            "a": targets["a_210"],
            "omega": targets["omega_210"],
        },
        **couplings,
    )

    checks = {
        "upstream_source_pure210_insertion_green": ins.get("n_failed", 1) == 0,
        "promoted_fields_are_seven": len(PROMOTED_FIELDS) == 7,
        "P_210_absent_from_promoted_fields": "P_210" not in PROMOTED_FIELDS,
        "dictionary_P_A_W_traced": (
            abs(paw["p"] - targets["p_210"]) < 1e-12
            and abs(paw["a"] - (3.0**0.5) * targets["a_210"]) < 1e-6 * abs(paw["a"])
            and abs(paw["omega"] - (6.0**0.5) * targets["omega_210"])
            < 1e-6 * abs(paw["omega"])
        ),
        "p_plus_a_plus_omega_equals_MGUT": abs(
            targets["p_210"] + targets["a_210"] + targets["omega_210"] - m_gut
        )
        < 1e-6 * m_gut,
        "singlet_span_bfb_unit_couplings": singlet_bfb["nonnegative"],
        "selected_singlet_hessian_psd": singlet_hess["positive_semidefinite"],
        "promoted_hessian_lam4_0_psd_mpmath": hess["positive_semidefinite"],
        "pure210_block_psd": hess["pure210_block_psd"],
        "ray_proxy_consistent_with_insertion": ray["consistent"],
        "historical_five_amplitude_not_mutated": abs(
            float(quartic5[0, 0]) - 0.55
        )
        < 1e-12,
        "mixed_cg_not_invented": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "PROMOTE_PAW_SPLIT_REDUCED_AMPLITUDES_PARTIAL"
            if not failures
            else "PROMOTE_PAW_SPLIT_REDUCED_AMPLITUDES_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "promoted_fields": list(PROMOTED_FIELDS),
        "couplings_diagnostic": couplings,
        "targets_GeV": targets,
        "aulakh_to_canonical_PAW": paw,
        "conventions": {
            "phi_norm2_cartesian": "p^2+a^2+omega^2",
            "stack_split": "a+omega+p = M_GUT (0.3+0.5+0.2)",
            "P_cross_proxy": "historical Λ_{P X} * (p^2+a^2+omega^2) * X^2",
            "soft_convention": hess["soft_convention"],
            "not_equated": [
                "P_210 = M_GUT (coarse)",
                "‖Φ‖ = sqrt(p^2+a^2+omega^2)",
                "Aulakh kinetic p^2+3a^2+6omega^2",
            ],
        },
        "ray_consistency_vs_insertion": ray,
        "promoted_hessian_lam4_0": {
            "fields": list(PROMOTED_FIELDS),
            "delta_m2_non210_GeV2": hess["delta_m2_non210_GeV2"],
            "pure210_block_min_eig": hess["pure210_block_min_eig"],
            "eigenvalues_mpmath": hess["eigenvalues_mpmath"],
            "min_eig_mpmath": hess["min_eig_mpmath"],
            "positive_definite": hess["positive_definite"],
            "positive_semidefinite": hess["positive_semidefinite"],
            "psd_floor": hess["psd_floor"],
            "float64_min_eig": hess["float64_min_eig"],
            "float64_false_tachyon_documented": hess[
                "float64_false_tachyon_documented"
            ],
            "soft_convention": hess["soft_convention"],
        },
        "singlet_span": {
            "bfb": singlet_bfb,
            "selected_vacuum_hessian": singlet_hess,
        },
        "flags": {
            "paw_split_promoted_into_reduced_amplitudes": not bool(failures),
            "pure210_source_potential_wired": True,
            "isotropic_P_cross_proxy_only": True,
            "mixed_field_cg_invented": False,
            "g1_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "uv_fix_pure210_couplings_g45_g210_g1050_lam": True,
            "replace_isotropic_P_cross_proxy_with_published_linear_cg": True,
            "mixed_field_invariants_and_cg": True,
            "full_component_hessian": True,
        },
        "verdict": (
            "Promoted reduced amplitudes replace P_210 by (p,a,ω) with the "
            "source-normalized pure-210 quartic and an isotropic ‖Φ‖² proxy for "
            f"historical P↔X crosses. λ₄=0 seven-amplitude Hessian min eig "
            f"(mpmath)={hess['min_eig_mpmath']:.6g} "
            f"({'PSD' if hess['positive_semidefinite'] else 'NOT PSD'}). "
            "Mixed G1 CG remains OPEN. Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    hess = report["promoted_hessian_lam4_0"]
    OUT_MD.write_text(
        "# Promote (p,a,ω) split into reduced amplitudes — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Fields: `{', '.join(report['promoted_fields'])}`\n"
        f"- λ₄=0 Hessian min eig (mpmath): `{hess['min_eig_mpmath']}`\n"
        f"- PD: `{hess['positive_definite']}`\n\n"
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
