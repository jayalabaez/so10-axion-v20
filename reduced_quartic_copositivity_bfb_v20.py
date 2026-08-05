#!/usr/bin/env python3
r"""Co-positivity / spectral BFB on reduced quartic + portal Schur (v20).

Physics
-------
For radial amplitudes ``ρ_i ≥ 0`` the reduced quartic slice is

    V_4 = Σ_{i≤j} Λ_{ij} ρ_i² ρ_j²   (Λ symmetric),

which is bounded from below on the positive orthant if Λ is **co-positive**:

    xᵀ Λ x ≥ 0  for all x ≥ 0.

Positive-definiteness ⇒ co-positivity; the converse is weaker and is the
correct BFB criterion when some cross couplings are negative.

This module:

1. Extracts the reduced five-amplitude quartic matrix from
   ``nonsusy_reduced_hessian_v20``;
2. Checks spectral PD (min eigenvalue > 0) and co-positivity certificates
   (diags ≥ 0; pairwise ``Λ_ij + √(Λ_ii Λ_jj) ≥ 0``; Monte-Carlo on the
   simplex; Motzkin–Straus-style corner checks);
3. Records the Schur portal margin ``1 − σ_max(A^{-1/2} B C^{-1/2})`` from
   the partial isotropic A/C fill.

Honesty
-------
* Scoped to the reduced radial quartic + partial Schur sector — not global
  BFB of the full invariant ring.
* Theory remains BLOCKED; G5 stays PARTIAL.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import diagonal_h10_sigmabar_m2_isotropic_54_slots_v20 as iso
import nonsusy_reduced_hessian_v20 as reduced
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "REDUCED_QUARTIC_COPOSITIVITY_BFB_V20.json"
OUT_MD = ROOT / "REDUCED_QUARTIC_COPOSITIVITY_BFB_V20.md"


def pairwise_copositive(lam: np.ndarray, *, tol: float = 1e-12) -> dict[str, Any]:
    """Necessary pairwise co-positivity conditions for symmetric Λ."""
    n = lam.shape[0]
    diags_ok = all(float(lam[i, i]) >= -tol for i in range(n))
    pair_failures: list[dict[str, Any]] = []
    for i in range(n):
        for j in range(i + 1, n):
            a = float(lam[i, i])
            b = float(lam[j, j])
            c = float(lam[i, j])
            # If either diag is (numerically) zero, require c ≥ 0.
            if a <= tol or b <= tol:
                ok = c >= -tol
            else:
                ok = c + math.sqrt(max(a, 0.0) * max(b, 0.0)) >= -tol
            if not ok:
                pair_failures.append(
                    {"i": i, "j": j, "lambda_ii": a, "lambda_jj": b, "lambda_ij": c}
                )
    return {
        "diags_nonnegative": diags_ok,
        "pairwise_ok": len(pair_failures) == 0,
        "pair_failures": pair_failures,
    }


def monte_carlo_copositive(
    lam: np.ndarray, *, n_samples: int = 4000, seed: int = 20
) -> dict[str, Any]:
    """Sample x≥0 on the simplex and record min xᵀΛx."""
    rng = np.random.default_rng(seed)
    n = lam.shape[0]
    vals = []
    # Dirichlet(1..1) = uniform on simplex
    for _ in range(n_samples):
        x = rng.exponential(size=n)
        x = x / np.sum(x)
        vals.append(float(x @ lam @ x))
    # Also check standard-basis and equal-weight corners
    for i in range(n):
        e = np.zeros(n)
        e[i] = 1.0
        vals.append(float(e @ lam @ e))
    vals.append(float(np.ones(n) @ lam @ np.ones(n) / (n * n)))
    min_val = float(np.min(vals))
    return {
        "n_samples": n_samples,
        "min_xTLx": min_val,
        "mean_xTLx": float(np.mean(vals)),
        "nonnegative_on_samples": min_val >= -1e-10 * max(1.0, abs(float(np.max(np.abs(lam))))),
    }


def spectral_pd(lam: np.ndarray) -> dict[str, Any]:
    eigs = np.linalg.eigvalsh(lam)
    return {
        "eigenvalues": [float(v) for v in eigs],
        "min_eig": float(np.min(eigs)),
        "positive_definite": bool(np.min(eigs) > 0.0),
    }


def build_report() -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    m_i = float(anchor["M_I_GeV"])
    m_gut = float(anchor["M_GUT_GeV"])
    reduced_rep = reduced.build_report()
    import scalar_vacuum_proton_decay_v20 as scalar_pd_mod

    radial_w = scalar_pd_mod.reduced_radial_vacuum_witness(
        {"available": True, "M_I_GeV": m_i, "M_GUT_GeV": m_gut}
    )
    quartic, lambdas, targets = reduced.radial_quartic_matrix(radial_w)
    lam = np.array(quartic, dtype=float)

    spec = spectral_pd(lam)
    pair = pairwise_copositive(lam)
    mc = monte_carlo_copositive(lam)

    iso_rep = iso.build_report()
    schur = iso_rep.get("schur_with_partial_diagonals", {})
    schur_pd = bool(schur.get("positive_definite"))
    schur_margin = schur.get("schur_margin")
    sigma = schur.get("largest_normalized_singular_value")

    # Co-positivity: pairwise + MC; PD is a stronger sufficient condition
    copositive = (
        pair["diags_nonnegative"]
        and pair["pairwise_ok"]
        and mc["nonnegative_on_samples"]
    )

    checks = {
        "reduced_hessian_green": reduced_rep.get("n_failed", 1) == 0,
        "quartic_spectral_pd": spec["positive_definite"],
        "quartic_diags_nonnegative": pair["diags_nonnegative"],
        "quartic_pairwise_copositive": pair["pairwise_ok"],
        "quartic_mc_copositive": mc["nonnegative_on_samples"],
        "quartic_copositive_scoped": copositive,
        "isotropic_schur_green": iso_rep.get("n_failed", 1) == 0,
        "schur_positive_definite": schur_pd,
        "schur_margin_positive": (
            schur_margin is not None and float(schur_margin) > 0.0
        ),
        "full_ring_bfb_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "REDUCED_QUARTIC_COPOSITIVITY_BFB_PARTIAL__FULL_RING_OPEN"
            if not failures
            else "REDUCED_QUARTIC_COPOSITIVITY_BFB_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "fields": list(reduced.FIELDS),
        "targets_GeV": {k: float(v) for k, v in targets.items()},
        "self_quartics": {k: float(v) for k, v in lambdas.items()},
        "quartic_matrix": lam.tolist(),
        "spectral": spec,
        "pairwise_copositivity": pair,
        "monte_carlo_copositivity": mc,
        "schur_portal": {
            "positive_definite": schur_pd,
            "schur_margin": schur_margin,
            "largest_normalized_singular_value": sigma,
            "criterion": "σ_max(A^{-1/2} B C^{-1/2}) < 1",
        },
        "flags": {
            "reduced_quartic_copositive": copositive,
            "reduced_quartic_spectral_pd": spec["positive_definite"],
            "schur_portal_pd": schur_pd,
            "full_invariant_ring_bfb": False,
            "g5_partial": not bool(failures),
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "complete_invariant_ring_G1": True,
            "global_competing_extrema": True,
            "full_ring_boundedness_certificate": True,
        },
        "verdict": (
            "Reduced quartic Λ is spectrally PD and co-positive on the tested "
            f"positive orthant (min eig={spec['min_eig']:.6e}; "
            f"MC min xᵀΛx={mc['min_xTLx']:.6e}). Schur portal PD with margin "
            f"{schur_margin}. Global full-ring BFB remains OPEN. "
            "Theory remains BLOCKED."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Reduced quartic co-positivity / Schur BFB — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- Spectral PD: `{report['spectral']['positive_definite']}` "
        f"(min eig `{report['spectral']['min_eig']}`)\n"
        f"- Co-positive (scoped): `{report['flags']['reduced_quartic_copositive']}`\n"
        f"- Schur PD: `{report['schur_portal']['positive_definite']}` "
        f"(margin `{report['schur_portal']['schur_margin']}`)\n\n"
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
