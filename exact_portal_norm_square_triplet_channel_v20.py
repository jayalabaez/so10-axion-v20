#!/usr/bin/env python3
"""Exact positive-semidefinite portal norm-square triplet channel (v20).

The verified direct tensor map

    C_Phi : 126bar -> 10,
    (C_Phi Sigma)_e = (1/4!) Phi_abcd Sigma_abcde,

defines the Hermitian quartic contraction

    V ⊃ lambda_PhiSigma_C ||C_Phi Sigma||^2.

This is one exact higher-channel combination inside
210dag210·126bardag126bar.  In the canonical triplet basis and for real
Pati-Salam singlet coordinates,

    x_minus = p-a/sqrt(3),
    x_plus  = p+a/sqrt(3),
    y       = 2 omega/sqrt(3),

its charge-sector blocks are

    Y=-1/3, basis (t2):
        [x_minus^2],

    Y=+1/3, basis (t2bar,t4bar):
        [[x_plus^2, x_plus*y],
         [x_plus*y, y^2]].

The positive-sector block is rank one.  The corresponding C Cdag operator on
10_H has colour eigenvalues x_minus^2 for T10 and x_plus^2+y^2 for T10bar,
so Cdag C and C Cdag have the same nonzero spectrum exactly.

This closes one contraction, not the complete set of higher Phi-Sigma irreps.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_triplet_clebsch_v20 as triplets

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PORTAL_NORM_SQUARE_TRIPLET_CHANNEL_V20.json"
OUT_MD = ROOT / "EXACT_PORTAL_NORM_SQUARE_TRIPLET_CHANNEL_V20.md"


def analytic_coefficients(p: float, a: float, omega: float) -> dict[str, float]:
    root3 = math.sqrt(3.0)
    return {
        "x_minus_GeV": float(p - a / root3),
        "x_plus_GeV": float(p + a / root3),
        "y_GeV": float(2.0 * omega / root3),
    }


def analytic_sigma_blocks(
    p: float, a: float, omega: float
) -> dict[str, np.ndarray]:
    c = analytic_coefficients(p, a, omega)
    xm, xp, y = c["x_minus_GeV"], c["x_plus_GeV"], c["y_GeV"]
    return {
        "A_u_sigma_GeV2": np.asarray([[xm * xm]], dtype=complex),
        "A_v_sigma_GeV2": np.asarray(
            [[xp * xp, xp * y], [xp * y, y * y]], dtype=complex
        ),
    }


def _aligned_triplet_forms() -> dict[str, dict[int, direct.Form]]:
    basis = triplets._hodge_basis("+i")
    classified = triplets._classified_triplets()
    left = triplets._left_color_basis()
    singlets = direct.singlet_basis()
    specifications = {
        "t2_triplet": ("p", left["triplet"]),
        "t2bar_antitriplet": ("p", left["antitriplet"]),
        "t4bar_antitriplet": ("omega", left["antitriplet"]),
    }
    result: dict[str, dict[int, direct.Form]] = {}
    for name, (reference, left_states) in specifications.items():
        result[name] = {}
        for weight in range(3):
            aligned = triplets._aligned_vector(
                classified[name][weight],
                singlets[reference],
                left_states[weight],
                basis,
            )
            result[name][weight] = triplets._form(aligned, basis)
    return result


def sigma_blocks_from_tensor(
    p: float, a: float, omega: float
) -> dict[str, Any]:
    phi_basis = direct.singlet_basis()
    phi = direct.add_forms(
        direct.scale_form(phi_basis["p"], p),
        direct.scale_form(phi_basis["a"], a),
        direct.scale_form(phi_basis["omega"], omega),
    )
    states = _aligned_triplet_forms()
    by_weight: list[dict[str, np.ndarray]] = []
    for weight in range(3):
        out_t2 = direct.contract(phi, states["t2_triplet"][weight])
        out_t2bar = direct.contract(phi, states["t2bar_antitriplet"][weight])
        out_t4bar = direct.contract(phi, states["t4bar_antitriplet"][weight])
        u = np.asarray(
            [[direct.tensor_inner(out_t2, out_t2)]], dtype=complex
        )
        outputs = (out_t2bar, out_t4bar)
        v = np.asarray(
            [
                [direct.tensor_inner(left, right) for right in outputs]
                for left in outputs
            ],
            dtype=complex,
        )
        by_weight.append({"A_u_sigma_GeV2": u, "A_v_sigma_GeV2": v})
    return {
        "by_weight": by_weight,
        "A_u_sigma_GeV2": sum(row["A_u_sigma_GeV2"] for row in by_weight) / 3.0,
        "A_v_sigma_GeV2": sum(row["A_v_sigma_GeV2"] for row in by_weight) / 3.0,
    }


def h_color_eigenvalues_from_tensor(
    p: float, a: float, omega: float
) -> dict[str, list[float]]:
    phi_basis = direct.singlet_basis()
    phi = direct.add_forms(
        direct.scale_form(phi_basis["p"], p),
        direct.scale_form(phi_basis["a"], a),
        direct.scale_form(phi_basis["omega"], omega),
    )
    sigma_basis = triplets._hodge_basis("+i")
    left = triplets._left_color_basis()
    result: dict[str, list[float]] = {"triplet": [], "antitriplet": []}
    for branch in result:
        for h_state in left[branch]:
            value = 0.0
            for sigma in sigma_basis:
                output = direct.contract(phi, sigma)
                coupling = direct.tensor_inner(h_state, output)
                value += float(abs(coupling) ** 2)
            result[branch].append(value)
    return result


def build_report() -> dict[str, Any]:
    p, a, omega = 0.9, 0.4, 0.7
    analytic = analytic_sigma_blocks(p, a, omega)
    numeric = sigma_blocks_from_tensor(p, a, omega)
    u_residual = float(
        np.max(np.abs(numeric["A_u_sigma_GeV2"] - analytic["A_u_sigma_GeV2"]))
    )
    v_residual = float(
        np.max(np.abs(numeric["A_v_sigma_GeV2"] - analytic["A_v_sigma_GeV2"]))
    )
    weight_spread = max(
        max(
            float(np.max(np.abs(row[key] - numeric[key])))
            for row in numeric["by_weight"]
        )
        for key in ("A_u_sigma_GeV2", "A_v_sigma_GeV2")
    )

    h_eigen = h_color_eigenvalues_from_tensor(p, a, omega)
    c = analytic_coefficients(p, a, omega)
    expected_h_triplet = c["x_minus_GeV"] ** 2
    expected_h_antitriplet = c["x_plus_GeV"] ** 2 + c["y_GeV"] ** 2
    h_triplet_residual = max(abs(value - expected_h_triplet) for value in h_eigen["triplet"])
    h_antitriplet_residual = max(
        abs(value - expected_h_antitriplet) for value in h_eigen["antitriplet"]
    )

    eig_u = np.linalg.eigvalsh(analytic["A_u_sigma_GeV2"])
    eig_v = np.linalg.eigvalsh(analytic["A_v_sigma_GeV2"])
    nonzero_sigma = sorted(
        [float(value) for value in np.concatenate([eig_u, eig_v]) if value > 1e-12]
    )
    nonzero_h = sorted([expected_h_triplet, expected_h_antitriplet])
    spectrum_residual = max(abs(x - y) for x, y in zip(nonzero_sigma, nonzero_h))
    determinant_v = float(np.linalg.det(analytic["A_v_sigma_GeV2"]).real)

    checks = {
        "tensor_matches_analytic_u_block": u_residual < 1e-12,
        "tensor_matches_analytic_v_block": v_residual < 1e-12,
        "three_color_weights_degenerate": weight_spread < 1e-12,
        "positive_semidefinite_u": float(eig_u[0]) >= -1e-12,
        "positive_semidefinite_v": float(eig_v[0]) >= -1e-12,
        "positive_sector_rank_one": abs(determinant_v) < 1e-12 and eig_v[-1] > 0.0,
        "H_triplet_eigenvalue_matches": h_triplet_residual < 1e-10,
        "H_antitriplet_eigenvalue_matches": h_antitriplet_residual < 1e-10,
        "CdagC_CCdag_nonzero_spectra_match": spectrum_residual < 1e-10,
        "specific_contraction_not_full_irrep_family": True,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_PORTAL_NORM_SQUARE_TRIPLET_CHANNEL_DERIVED__HIGHER_IRREPS_OPEN"
            if not failures
            else "EXACT_PORTAL_NORM_SQUARE_TRIPLET_CHANNEL_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator_convention": (
            "V contains lambda_PhiSigma_C ||C_Phi Sigma||^2 with the canonical "
            "direct contraction C_Phi used by the lambda4 portal."
        ),
        "analytic_coefficients": c,
        "exact_sigma_blocks": {
            "basis_u": ["t2"],
            "basis_v": ["t2bar", "t4bar"],
            "A_u_formula": "[[x_minus^2]]",
            "A_v_formula": "[[x_plus^2,x_plus*y],[x_plus*y,y^2]]",
            "A_u_GeV2": analytic["A_u_sigma_GeV2"].real.tolist(),
            "A_v_GeV2": analytic["A_v_sigma_GeV2"].real.tolist(),
            "positive_sector_rank": 1,
            "positive_sector_determinant": determinant_v,
        },
        "exact_H_crosscheck": {
            "T10_triplet_eigenvalue_GeV2": expected_h_triplet,
            "T10bar_antitriplet_eigenvalue_GeV2": expected_h_antitriplet,
            "tensor_triplet_values": h_eigen["triplet"],
            "tensor_antitriplet_values": h_eigen["antitriplet"],
            "nonzero_spectrum_residual": spectrum_residual,
        },
        "numerical_residuals": {
            "u_block": u_residual,
            "v_block": v_residual,
            "weight_spread": weight_spread,
            "H_triplet": h_triplet_residual,
            "H_antitriplet": h_antitriplet_residual,
        },
        "newly_closed_subproblem": {
            "exact_CPhi_dagger_CPhi_triplet_block": not failures,
            "exact_t2bar_t4bar_quartic_mixing": not failures,
            "positive_semidefinite_rank_structure": not failures,
            "CCdag_CdagC_spectrum_match": not failures,
        },
        "remaining_blockers": {
            "other_independent_PhiSigma_irrep_contractions": True,
            "10dag10_126bardag126bar_background_insertions": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
        },
        "flag": {
            "exact_portal_norm_square_channel_closed": not failures,
            "exact_quartic_t2bar_t4bar_mixing_derived": not failures,
            "all_PhiSigma_anisotropic_channels_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The exact positive-semidefinite C_Phi dagger C_Phi contraction is "
            "derived. It fixes the t2 diagonal and the full rank-one t2bar/t4bar "
            "quartic block, including its off-diagonal mixing. Other independent "
            "Phi-Sigma irreps and the full vacuum remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact portal norm-square triplet channel — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- `A_u(t2) = x_minus^2`",
            "- `A_v(t2bar,t4bar) = outer((x_plus,y),(x_plus,y))`",
            "- The positive-charge block is positive semidefinite and rank one.",
            "- Other independent `Phi-Sigma` irreps remain open.",
            "",
        ]
    )


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, complex):
        return {"re": float(obj.real), "im": float(obj.imag)}
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2, default=_json_default) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
