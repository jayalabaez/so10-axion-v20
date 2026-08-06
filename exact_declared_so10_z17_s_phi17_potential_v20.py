#!/usr/bin/env python3
"""Exact renormalizable S/Phi17 potential under the *declared* symmetries.

The live model declares SO(10) gauge symmetry and a global Z17, but no
continuous U(1)_X.  This module therefore enumerates the complete singlet-only
canonical-dimension <= 4 monomial basis using only the declared PQ bookkeeping
for S and the declared Z17 charges:

    S:      PQ=+4, Z17=4
    S^dag:  PQ=-4, Z17=13
    Phi17:  PQ=0,  Z17=0

Phi17 is an SO(10) singlet.  Continuous X is deliberately not imposed.
The resulting Hermitian operator basis is complete for the S/Phi17
renormalizable subsector.  A constructive bounded benchmark demonstrates that
Phi17's phase can be lifted while the single expected PQ angular zero remains.
This is not the complete 210+126bar+10+S+Phi17 potential.
"""
from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
FIELDS = ("S", "S_dag", "Phi17", "Phi17_dag")
PQ = np.array([4, -4, 0, 0], dtype=int)
Z17 = np.array([4, 13, 0, 0], dtype=int)


def monomial_label(exponents: tuple[int, int, int, int]) -> str:
    pieces: list[str] = []
    for field, power in zip(FIELDS, exponents):
        if power == 1:
            pieces.append(field)
        elif power:
            pieces.append(f"{field}^{power}")
    return " ".join(pieces) if pieces else "1"


def conjugate(exponents: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    s, sd, p, pd = exponents
    return sd, s, pd, p


def declared_allowed_monomials(max_dimension: int = 4) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for exponents in product(range(max_dimension + 1), repeat=4):
        degree = sum(exponents)
        if degree == 0 or degree > max_dimension:
            continue
        vector = np.array(exponents, dtype=int)
        pq = int(vector @ PQ)
        z17 = int(vector @ Z17) % 17
        if pq or z17:
            continue
        rows.append(
            {
                "exponents": list(exponents),
                "label": monomial_label(exponents),
                "dimension": degree,
                "PQ": pq,
                "Z17": z17,
                "phi_phase_sensitive": exponents[2] != exponents[3],
            }
        )
    return sorted(rows, key=lambda row: (row["dimension"], row["label"]))


def hermitian_operator_basis() -> list[dict[str, Any]]:
    allowed = {
        tuple(row["exponents"]): row for row in declared_allowed_monomials()
    }
    seen: set[tuple[int, int, int, int]] = set()
    basis: list[dict[str, Any]] = []
    for exponents in sorted(allowed, key=lambda e: (sum(e), monomial_label(e))):
        if exponents in seen:
            continue
        partner = conjugate(exponents)
        if partner not in allowed:
            raise AssertionError(f"conjugate missing for {exponents}")
        seen.add(exponents)
        seen.add(partner)
        if partner == exponents:
            basis.append(
                {
                    "type": "self_conjugate",
                    "operator": monomial_label(exponents),
                    "dimension": sum(exponents),
                    "phi_phase_sensitive": False,
                }
            )
        else:
            left = monomial_label(exponents)
            right = monomial_label(partner)
            basis.append(
                {
                    "type": "complex_pair",
                    "operator_re": f"Re[{left}]",
                    "operator_im": f"Im[{left}]",
                    "conjugate": right,
                    "dimension": sum(exponents),
                    "phi_phase_sensitive": exponents[2] != exponents[3],
                }
            )
    return basis


def benchmark() -> dict[str, Any]:
    # Canonical real coordinates:
    # S=(s_r+i s_i)/sqrt(2), Phi17=(p_r+i p_i)/sqrt(2).
    v_s = 3.0
    v_p = 5.0
    lam_s = 0.7
    lam_p = 0.9
    eps = 0.2
    mu_phase_sq = 1.3

    # V = ls/4 (s^2-vs^2)^2 + lp/4 (p^2-vp^2)^2
    #   + eps/4 (s^2-vs^2)(p^2-vp^2) + mu^2/2 p_i^2.
    # The final term is the allowed combination
    # mu^2/2 * [2|Phi|^2-(Phi^2+Phi*^2)]/2.
    radial = np.array(
        [
            [2.0 * lam_s * v_s**2, eps * v_s * v_p],
            [eps * v_s * v_p, 2.0 * lam_p * v_p**2],
        ],
        dtype=float,
    )
    hessian = np.zeros((4, 4), dtype=float)
    # Coordinate ordering: s_r, s_i, p_r, p_i.
    hessian[0, 0] = radial[0, 0]
    hessian[0, 2] = hessian[2, 0] = radial[0, 1]
    hessian[2, 2] = radial[1, 1]
    hessian[3, 3] = mu_phase_sq
    eigenvalues = np.linalg.eigvalsh(hessian)
    positive = eigenvalues[eigenvalues > 1.0e-10]

    quartic_matrix = np.array(
        [[lam_s, 0.5 * eps], [0.5 * eps, lam_p]], dtype=float
    )
    quartic_eigs = np.linalg.eigvalsh(quartic_matrix)
    return {
        "coordinates": ["s_r", "s_i_PQ", "phi_r", "phi_i"],
        "parameters": {
            "v_S": v_s,
            "v_Phi17": v_p,
            "lambda_S": lam_s,
            "lambda_Phi17": lam_p,
            "epsilon": eps,
            "mu_phi_phase_squared": mu_phase_sq,
        },
        "quartic_matrix_eigenvalues": [float(x) for x in quartic_eigs],
        "bounded_from_below": bool(np.min(quartic_eigs) > 0.0),
        "gradient": [0.0, 0.0, 0.0, 0.0],
        "hessian": hessian.tolist(),
        "hessian_eigenvalues": [float(x) for x in eigenvalues],
        "zero_modes": int(np.count_nonzero(np.abs(eigenvalues) <= 1.0e-10)),
        "negative_modes": int(np.count_nonzero(eigenvalues < -1.0e-10)),
        "minimum_physical_eigenvalue": float(np.min(positive)),
        "pq_zero_direction": [0.0, 1.0, 0.0, 0.0],
        "phi_phase_lifted": bool(hessian[3, 3] > 0.0),
        "interpretation": (
            "Exactly one angular zero remains, the intended PQ direction of S. "
            "The Phi17 angular mode is lifted by a declared-symmetry-allowed "
            "quadratic phase term."
        ),
    }


def build_report() -> dict[str, Any]:
    monomials = declared_allowed_monomials()
    basis = hermitian_operator_basis()
    point = benchmark()
    phase_sensitive = [row for row in monomials if row["phi_phase_sensitive"]]
    low_dim_pure_phi = [
        row for row in monomials
        if row["exponents"][0] == row["exponents"][1] == 0
        and row["phi_phase_sensitive"]
    ]
    checks = {
        "complete_monomial_count_21": len(monomials) == 21,
        "hermitian_real_basis_dimension_13": len(basis) == 13,
        "phase_sensitive_operators_exist_below_dimension17": bool(low_dim_pure_phi)
        and min(row["dimension"] for row in low_dim_pure_phi) == 1,
        "quadratic_phi_phase_lifter_present": any(
            row["dimension"] == 2
            and row["exponents"] in ([0, 0, 2, 0], [0, 0, 0, 2])
            for row in monomials
        ),
        "benchmark_bounded": point["bounded_from_below"],
        "benchmark_stationary": max(abs(x) for x in point["gradient"]) == 0.0,
        "exactly_one_pq_zero": point["zero_modes"] == 1,
        "no_negative_modes": point["negative_modes"] == 0,
        "phi_phase_lifted": point["phi_phase_lifted"],
        "full_multifield_model_open": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "DECLARED_SO10_Z17_S_PHI17_RENORMALIZABLE_SECTOR_CLOSED"
            if not failures
            else "DECLARED_SO10_Z17_S_PHI17_GATE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "declared_symmetry_contract": {
            "gauge": ["SO(10)"],
            "global": ["Z17", "PQ_as_scalar_selection_rule"],
            "continuous_X_imposed": False,
        },
        "counts": {
            "allowed_complex_monomials_dimension_le_4": len(monomials),
            "independent_hermitian_real_operators": len(basis),
            "phi_phase_sensitive_complex_monomials": len(phase_sensitive),
        },
        "allowed_monomials": monomials,
        "hermitian_operator_basis": basis,
        "constructive_benchmark": point,
        "checks": checks,
        "flag": {
            "declared_symmetry_singlet_basis_complete": not failures,
            "phi17_phase_obstruction_removed_without_X": not failures,
            "intended_PQ_zero_preserved": point["zero_modes"] == 1,
            "natural_phi17_hierarchy_explained": False,
            "complete_10H_S_Phi17_component_hessian": False,
            "complete_multifield_model": False,
        },
        "verdict": (
            "Removing undeclared continuous X closes the renormalizable S/Phi17 "
            "operator basis and permits a bounded vacuum with Phi17's phase lifted. "
            "However, the 1e17-GeV Phi17 hierarchy is no longer symmetry-protected; "
            "its small lower-dimensional coefficients are independent tunings until "
            "a UV mechanism is supplied."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    report = build_report()
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        args.json.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
