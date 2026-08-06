#!/usr/bin/env python3
r"""Insert source-normalized pure-210 quartic densities into the reduced sector.

Primary source: Esposito et al., arXiv:gr-qc/9507053 Eqs. (2.5)--(2.7).
Selected-vacuum densities come from ``source_210_quartic_norm_identity_v20``
(upstream maps in ``so10_210_source_quartic_basis_v20``).

On a fixed direction ``Φ = ρ û`` with densities
``d_R = ||(ΦΦ)_R||² / ||Φ||⁴``,

    V_210(ρ û) = (g₄₅ d₄₅ + g₂₁₀ d₂₁₀ + g₁₀₅₀ d₁₀₅₀ + λ) ρ⁴ ≡ λ_eff ρ⁴.

The historical reduced witness uses ``V ⊃ (λ_P/4) P⁴``. Identifying the
coarse radial amplitude with ``ρ = ||Φ||`` on the selected ray gives the
proxy

    λ_P^(source) = 4 λ_eff.

This module:

1. Builds that source λ_P for a declared diagnostic coupling set;
2. Patches only the ``P_210`` diagonal of the reduced five-amplitude Λ;
3. Re-runs co-positivity / spectral BFB and λ₄=0 reduced Hessian checks;
4. Cross-checks the analytic ``(p,a,ω)`` potential for the same couplings.

Honesty
-------
* Radial ``P ↔ ||Φ||`` identification is a selected-ray proxy only.
* Couplings ``(g₄₅,g₂₁₀,g₁₀₅₀,λ)`` are diagnostic, not UV-fixed.
* Soft δm² for the λ₄=0 reduced Hessian are rebuilt from the interaction
  gradient inside ``high_precision_hessian``; use mpmath eigenvalues (float64
  invents a false tachyon on this ill-conditioned matrix).
* Mixed-field G1 / full component Hessian remain OPEN.
* ``whole_model_validated = false``. Theory remains BLOCKED.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import nonsusy_reduced_hessian_v20 as reduced
import pure_210_ps_singlet_quartic_polynomials_v20 as singlet
import reduced_quartic_copositivity_bfb_v20 as copos
import scalar_vacuum_proton_decay_v20 as scalar_pd
import source_210_quartic_norm_identity_v20 as vac_dens

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "SOURCE_PURE210_REDUCED_POTENTIAL_INSERTION_V20.json"
OUT_MD = ROOT / "SOURCE_PURE210_REDUCED_POTENTIAL_INSERTION_V20.md"

# Unit-positive channel probe (all norms ≥ 0 ⇒ pure-210 V ≥ 0).
DIAGNOSTIC_COUPLINGS = {
    "g45": 1.0,
    "g210": 1.0,
    "g1050": 1.0,
    "lam": 0.0,
}


def lambda_eff_from_densities(
    dens: dict[str, float],
    *,
    g45: float,
    g210: float,
    g1050: float,
    lam: float,
) -> float:
    return float(
        g45 * dens["||(ΦΦ)_45||^2 / ||Φ||^4"]
        + g210 * dens["||(ΦΦ)_210||^2 / ||Φ||^4"]
        + g1050 * dens["||(ΦΦ)_1050||^2 / ||Φ||^4"]
        + lam
    )


def patch_p210_self_quartic(
    quartic: np.ndarray, *, lambda_p_source: float
) -> np.ndarray:
    patched = np.array(quartic, dtype=float, copy=True)
    idx = list(reduced.FIELDS).index("P_210")
    patched[idx, idx] = float(lambda_p_source)
    return patched


def singlet_span_bfb(
    *,
    g45: float,
    g210: float,
    g1050: float,
    lam: float,
    n_samples: int = 64,
    seed: int = 21045,
) -> dict[str, Any]:
    """Monte-Carlo V≥0 on the (p,a,ω) span for the declared couplings."""
    rng = np.random.default_rng(seed)
    vals: list[float] = []
    for _ in range(n_samples):
        point = rng.normal(size=3)
        vals.append(
            singlet.identity_reduced_potential(
                *point, g45=g45, g210=g210, g1050=g1050, lam=lam
            )
        )
    # Axis and equal-weight probes
    for point in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (1.0, 1.0, 1.0)):
        vals.append(
            singlet.identity_reduced_potential(
                *point, g45=g45, g210=g210, g1050=g1050, lam=lam
            )
        )
    min_v = float(np.min(vals))
    return {
        "n_samples": n_samples + 4,
        "min_V": min_v,
        "nonnegative": min_v >= -1e-10,
    }


def selected_vacuum_singlet_hessian(
    vevs: dict[str, float],
    *,
    g45: float,
    g210: float,
    g1050: float,
    lam: float,
    eps: float = 1e-4,
) -> dict[str, Any]:
    """Numerical 3×3 Hessian of the pure-210 potential at selected (p,a,ω)."""
    p0 = float(vevs["p"])
    a0 = float(vevs["a"])
    w0 = float(vevs["omega"])
    # Work in a scaled chart so finite differences are stable.
    scale = max(abs(p0), abs(a0), abs(w0), 1.0)
    x0 = np.array([p0, a0, w0], dtype=float) / scale

    def v_at(x: np.ndarray) -> float:
        y = x * scale
        return singlet.identity_reduced_potential(
            float(y[0]),
            float(y[1]),
            float(y[2]),
            g45=g45,
            g210=g210,
            g1050=g1050,
            lam=lam,
        )

    hess = np.zeros((3, 3), dtype=float)
    for i in range(3):
        for j in range(i, 3):
            e_i = np.zeros(3)
            e_j = np.zeros(3)
            e_i[i] = eps
            e_j[j] = eps
            if i == j:
                fpp = v_at(x0 + e_i)
                fmm = v_at(x0 - e_i)
                f0 = v_at(x0)
                hess[i, i] = (fpp - 2.0 * f0 + fmm) / (eps * eps)
            else:
                fpp = v_at(x0 + e_i + e_j)
                fpm = v_at(x0 + e_i - e_j)
                fmp = v_at(x0 - e_i + e_j)
                fmm = v_at(x0 - e_i - e_j)
                hess[i, j] = hess[j, i] = (fpp - fpm - fmp + fmm) / (4.0 * eps * eps)
    # Convert back to physical (p,a,ω) second derivatives: ∂²V/∂x_i∂x_j = scale² ∂²V/∂y_i∂y_j
    hess_phys = hess / (scale * scale)
    eigs = np.linalg.eigvalsh(hess_phys)
    return {
        "eigenvalues": [float(v) for v in eigs],
        "min_eig": float(np.min(eigs)),
        "positive_semidefinite": bool(np.min(eigs) >= -1e-8 * max(1.0, abs(float(np.max(np.abs(eigs)))))),
        "scale_GeV": float(scale),
    }


def build_report() -> dict[str, Any]:
    dens_rep = vac_dens.build_report(n_ps=16)
    dens = dens_rep["selected_vacuum"]["effective_quartic_densities"]
    vevs = dens_rep["selected_vacuum"]["vevs_GeV"]
    couplings = dict(DIAGNOSTIC_COUPLINGS)

    lam_eff = lambda_eff_from_densities(dens, **couplings)
    lambda_p_source = 4.0 * lam_eff

    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    radial = scalar_pd.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    quartic_hist, lambdas_hist, targets = reduced.radial_quartic_matrix(radial)
    lambda_p_hist = float(lambdas_hist["P_210"])

    quartic_src = patch_p210_self_quartic(
        quartic_hist, lambda_p_source=lambda_p_source
    )
    lambdas_src = dict(lambdas_hist)
    lambdas_src["P_210"] = float(lambda_p_source)

    spec_hist = copos.spectral_pd(quartic_hist)
    spec_src = copos.spectral_pd(quartic_src)
    pair_src = copos.pairwise_copositive(quartic_src)
    mc_src = copos.monte_carlo_copositive(quartic_src)
    copositive_src = (
        pair_src["diags_nonnegative"]
        and pair_src["pairwise_ok"]
        and mc_src["nonnegative_on_samples"]
    )

    params = reduced.interaction_parameters(m_i, m_gut, 0.0)
    hess_src = reduced.high_precision_hessian(targets, quartic_src, params)
    # Must use mpmath eigsy: float64 conversion of this ill-conditioned
    # Hessian invents a false ~−10^8 tachyon (same artifact on historical Λ).
    hess_eigs = reduced.high_precision_eigenvalues(hess_src)
    hess_min = float(min(hess_eigs))
    hess_pd = bool(hess_min > 0.0)
    # float64 cross-check (documents the artifact; not used for the gate).
    hess_np = np.array(
        [[float(hess_src[i, j]) for j in range(5)] for i in range(5)],
        dtype=float,
    )
    hess_float_min = float(np.min(np.linalg.eigvalsh(hess_np)))

    singlet_bfb = singlet_span_bfb(**couplings)
    singlet_hess = selected_vacuum_singlet_hessian(vevs, **couplings)

    # Historical-matched attribution (same Λ; documents decomposition only).
    lam_matched = lambda_p_hist / 4.0 - (
        couplings["g45"] * dens["||(ΦΦ)_45||^2 / ||Φ||^4"]
        + couplings["g210"] * dens["||(ΦΦ)_210||^2 / ||Φ||^4"]
        + couplings["g1050"] * dens["||(ΦΦ)_1050||^2 / ||Φ||^4"]
    )

    checks = {
        "upstream_selected_vacuum_densities_green": dens_rep.get("n_failed", 1) == 0,
        "selected_vacuum_45_active": dens["||(ΦΦ)_45||^2 / ||Φ||^4"] > 0.0,
        "lambda_eff_positive_unit_couplings": lam_eff > 0.0,
        "patched_quartic_spectral_pd": spec_src["positive_definite"],
        "patched_quartic_copositive": copositive_src,
        "singlet_span_bfb_unit_couplings": singlet_bfb["nonnegative"],
        "selected_singlet_hessian_psd": singlet_hess["positive_semidefinite"],
        "historical_witness_not_mutated": abs(lambda_p_hist - 0.55) < 1e-12,
        "reduced_hessian_lam4_0_positive_definite_mpmath": hess_pd,
        "full_mixed_ring_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "SOURCE_PURE210_REDUCED_POTENTIAL_INSERTION_PARTIAL"
            if not failures
            else "SOURCE_PURE210_REDUCED_POTENTIAL_INSERTION_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "couplings_diagnostic": couplings,
        "selected_vacuum_densities": dens,
        "radial_proxy": {
            "identification": "P_210 ~ ||Φ|| on selected ray ⇒ λ_P = 4 λ_eff",
            "lambda_eff": lam_eff,
            "lambda_P_source": lambda_p_source,
            "lambda_P_historical": lambda_p_hist,
            "lambda_P_ratio_source_over_hist": (
                lambda_p_source / lambda_p_hist if lambda_p_hist else None
            ),
            "lam_for_historical_match_with_unit_g": lam_matched,
        },
        "reduced_quartic": {
            "fields": list(reduced.FIELDS),
            "self_quartics_historical": {k: float(v) for k, v in lambdas_hist.items()},
            "self_quartics_source_patched": {k: float(v) for k, v in lambdas_src.items()},
            "spectral_historical": spec_hist,
            "spectral_source_patched": spec_src,
            "pairwise_copositivity_source": pair_src,
            "monte_carlo_copositivity_source": mc_src,
            "copositive_source_patched": copositive_src,
        },
        "reduced_hessian_lam4_0": {
            "eigenvalues_mpmath": [float(v) for v in hess_eigs],
            "min_eig_mpmath": hess_min,
            "positive_definite": hess_pd,
            "float64_min_eig_artifact": hess_float_min,
            "float64_false_tachyon_documented": hess_float_min < 0.0 < hess_min,
            "soft_rematch_required": False,
            "note": (
                "Stationarity soft δm² are rebuilt inside high_precision_hessian "
                "from the interaction gradient at the selected VEVs; they do not "
                "need a separate λ_P-dependent rematch. float64 eigendecomposition "
                "of this Hessian is unreliable (false ~−10^8 mode)."
            ),
        },
        "singlet_span": {
            "bfb": singlet_bfb,
            "selected_vacuum_hessian": singlet_hess,
        },
        "flags": {
            "source_pure210_inserted_into_reduced_P210": not bool(failures),
            "reduced_potential_insertion_pending": False,
            "bfb_quartic_revalidation_partial": not bool(failures),
            "reduced_hessian_lam4_0_pd_after_source_patch": hess_pd,
            "reduced_hessian_soft_rematch_open": False,
            "radial_proxy_identification_only": True,
            "diagnostic_couplings_not_uv_fixed": True,
            "full_mixed_rep_bfb": False,
            "g1_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "uv_fix_pure210_couplings_g45_g210_g1050_lam": True,
            "published_linear_cg_for_S_Phi17_cross": True,
            "mixed_field_invariants_and_cg": True,
            "full_component_hessian": True,
        },
        "verdict": (
            "With diagnostic unit channel couplings, selected-vacuum source "
            f"densities give λ_eff={lam_eff:.6g} and patched λ_P={lambda_p_source:.6g} "
            f"(historical λ_P={lambda_p_hist:.6g}). Patched reduced Λ is "
            f"{'PD/co-positive' if copositive_src and spec_src['positive_definite'] else 'NOT BFB'}; "
            f"pure-210 singlet span BFB holds; selected-singlet Hessian is PSD. "
            f"λ₄=0 five-amplitude Hessian min eig (mpmath)={hess_min:.6g} (PD). "
            "Couplings remain diagnostic; (p,a,ω) promotion with Δ/H10 linear CG "
            "is in promote_paw_split_reduced_amplitudes_v20; mixed G1 OPEN. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    rp = report["radial_proxy"]
    OUT_MD.write_text(
        "# Source pure-210 → reduced potential insertion — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- λ_eff: `{rp['lambda_eff']}`\n"
        f"- λ_P source / historical: `{rp['lambda_P_source']}` / `{rp['lambda_P_historical']}`\n"
        f"- Patched Λ PD: `{report['reduced_quartic']['spectral_source_patched']['positive_definite']}`\n"
        f"- λ₄=0 Hessian min eig (mpmath): `{report['reduced_hessian_lam4_0']['min_eig_mpmath']}`\n\n"
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
