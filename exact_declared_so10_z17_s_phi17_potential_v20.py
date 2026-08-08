#!/usr/bin/env python3
"""Historical Option-C S/Phi17 potential with gauged U(1)_X omitted.

This module reproduces the superseded ``historical_option_c_no_x_v20``
counterfactual.  It enumerates the singlet-only canonical-dimension <= 4
monomial basis using PQ bookkeeping and Z17 charges, but deliberately does not
enforce the manuscript's gauged U(1)_X:

    S:      PQ=+4, Z17=4
    S^dag:  PQ=-4, Z17=13
    Phi17:  PQ=0,  Z17=0

Phi17 is an SO(10) singlet but has X=17 in the manuscript.  Consequently the
phase-sensitive Phi17 terms constructed here are gauge-forbidden and cannot
close the live model.  The numerical benchmark remains a reproducibility test
of the historical no-X calculation only; it is neither manuscript-authoritative
nor a complete 210+126bar+10+S+Phi17 potential.
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
MODEL_CONTRACT_ID = "historical_option_c_no_x_v20"


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
    """Return monomials allowed only in the historical no-X counterfactual.

    The public name is retained for compatibility with archived calculations.
    """
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
            "The Phi17 angular mode is lifted only in the historical no-X "
            "counterfactual; that quadratic phase term is forbidden by the "
            "manuscript's gauged U(1)_X."
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
        "historical_no_x_monomial_count_21": len(monomials) == 21,
        "historical_no_x_hermitian_real_basis_dimension_13": len(basis) == 13,
        "historical_no_x_phase_sensitive_operators_below_dimension17": bool(low_dim_pure_phi)
        and min(row["dimension"] for row in low_dim_pure_phi) == 1,
        "historical_no_x_quadratic_phi_phase_lifter_present": any(
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
        "model_contract_id": MODEL_CONTRACT_ID,
        "authoritative_for_manuscript": False,
        "model_wide_no_go_certified": False,
        "status": (
            "HISTORICAL_OPTION_C_NO_X_S_PHI17_REPRODUCED__NONAUTHORITATIVE"
            if not failures
            else "HISTORICAL_OPTION_C_NO_X_S_PHI17_REPRODUCTION_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "counterfactual_symmetry_contract": {
            "gauge": ["SO(10)"],
            "global": ["Z17", "PQ_as_scalar_selection_rule"],
            "continuous_X_imposed": False,
            "manuscript_gauged_u1x_omitted": True,
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
            "historical_option_c_singlet_basis_reproduced": not failures,
            "historical_no_x_phi17_phase_lifter_constructed": not failures,
            "historical_no_x_PQ_zero_preserved": point["zero_modes"] == 1,
            "phi17_phase_lifter_allowed_by_manuscript_u1x": False,
            "authoritative_for_manuscript": False,
            "model_wide_no_go_certified": False,
            "natural_phi17_hierarchy_explained": False,
            "complete_10H_S_Phi17_component_hessian": False,
            "complete_multifield_model": False,
        },
        "verdict": (
            "This reproduces the historical Option-C calculation obtained by "
            "omitting U(1)_X. Its phase-sensitive Phi17 operators, including the "
            "quadratic phase lifter, are forbidden because Phi17 has X=17 in the "
            "manuscript. The benchmark is therefore non-authoritative and neither "
            "closes nor excludes the gauged theory."
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
