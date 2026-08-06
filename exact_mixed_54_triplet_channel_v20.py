#!/usr/bin/env python3
"""Exact mixed 54-channel projection for the v20 triplet sector.

This module closes the first common anisotropic channel in

    210†210 · 10†10,
    210†210 · 126bar†126bar,
    10†10   · 126bar†126bar.

Conventions
-----------
For a canonically normalized k-form X, define the Hermitian rank-two tensor

    M_ab[X] = c_k <i_a X, i_b X>,

with c_4=c_1=1 and c_5=1/2 for the repository's
K_126=(1/(2*5!)) Sigma†Sigma convention.  The 54 projection is the real
symmetric traceless part

    Q_54[X] = Re(M_(ab)) - Tr(M)/10 delta_ab.

For the normalized real 210 singlet

    Phi = p P + a A + omega W,

this gives exactly

    Q_54[Phi] = diag(q_c,...,q_c,q_w,...,q_w),

with six colour entries and four weak entries,

    q_c = -2 p^2/5 + 4 a^2/15 - omega^2/15,
    q_w =  3 p^2/5 - 2 a^2/5  + omega^2/10.

Consequently the invariant convention

    V ⊃ lambda_PhiH_54 Q_54[Phi]:Q_54[H]

shifts every 10_H colour triplet/antitriplet by lambda_PhiH_54*q_c.

A second exact result follows from middle-form chirality: for every complex
self-dual or anti-self-dual five-form in ten Euclidean dimensions,

    Q_54[Sigma] = 0.

This is the vanishing stress-tensor identity for a chiral middle form.  Thus
Hermitian 126bar†126bar has no 54 component.  The 54 occurring in
126bar x 126bar is the separate holomorphic bilinear already constructed by
``so10_126_to_54_projector_v20``; it must not be confused with the Hermitian
quartics above.

Scope
-----
This closes only the shared Hermitian 54 channel.  Other anisotropic channels
and all mixing-relevant 210 component states remain open.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_10h_squared_s_bterm_v20 as h10
import exact_126bar_triplet_clebsch_v20 as triplets

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_MIXED_54_TRIPLET_CHANNEL_V20.json"
OUT_MD = ROOT / "EXACT_MIXED_54_TRIPLET_CHANNEL_V20.md"


def _rank2_bilinear(
    left: direct.Form,
    right: direct.Form,
    *,
    kinetic_factor: float,
) -> np.ndarray:
    matrix = np.zeros((direct.N, direct.N), dtype=complex)
    for a in range(direct.N):
        left_a = direct.interior(left, a)
        for b in range(direct.N):
            matrix[a, b] = kinetic_factor * direct.tensor_inner(
                left_a, direct.interior(right, b)
            )
    return matrix


def project_54_from_bilinear(matrix: np.ndarray) -> np.ndarray:
    """Real symmetric traceless projection in the SO(10) vector indices."""
    matrix = np.asarray(matrix, dtype=complex)
    symmetric_real = 0.5 * (matrix + matrix.T)
    symmetric_real = np.real_if_close(symmetric_real, tol=1000).real
    return symmetric_real - np.trace(symmetric_real) * np.eye(10) / 10.0


def phi_54(phi: direct.Form) -> np.ndarray:
    return project_54_from_bilinear(
        _rank2_bilinear(phi, phi, kinetic_factor=1.0)
    )


def h_54(h: direct.Form) -> np.ndarray:
    return project_54_from_bilinear(
        _rank2_bilinear(h, h, kinetic_factor=1.0)
    )


def sigma_hermitian_54(sigma: direct.Form) -> np.ndarray:
    return project_54_from_bilinear(
        _rank2_bilinear(sigma, sigma, kinetic_factor=0.5)
    )


def phi_singlet(p: float, a: float, omega: float) -> direct.Form:
    basis = direct.singlet_basis()
    return direct.add_forms(
        direct.scale_form(basis["p"], p),
        direct.scale_form(basis["a"], a),
        direct.scale_form(basis["omega"], omega),
    )


def analytic_phi_54_coefficients(
    p: float, a: float, omega: float
) -> dict[str, float]:
    q_color = (
        -2.0 * p * p / 5.0
        + 4.0 * a * a / 15.0
        - omega * omega / 15.0
    )
    q_weak = (
        3.0 * p * p / 5.0
        - 2.0 * a * a / 5.0
        + omega * omega / 10.0
    )
    return {
        "q_color_GeV2": float(q_color),
        "q_weak_GeV2": float(q_weak),
    }


def analytic_phi_54_matrix(p: float, a: float, omega: float) -> np.ndarray:
    coefficients = analytic_phi_54_coefficients(p, a, omega)
    return np.diag(
        [coefficients["q_color_GeV2"]] * 6
        + [coefficients["q_weak_GeV2"]] * 4
    )


def channel_contraction(left_54: np.ndarray, right_54: np.ndarray) -> float:
    return float(np.sum(np.asarray(left_54) * np.asarray(right_54)))


def h_component_coefficient(
    p: float, a: float, omega: float, h_state: direct.Form
) -> float:
    return channel_contraction(phi_54(phi_singlet(p, a, omega)), h_54(h_state))


def _generator_matrix(a: int, b: int) -> np.ndarray:
    matrix = np.zeros((10, 10), dtype=float)
    matrix[a, b] = 1.0
    matrix[b, a] = -1.0
    return matrix


def _covariance_residual(
    form: direct.Form,
    *,
    kinetic_factor: float,
    a: int,
    b: int,
) -> float:
    base = project_54_from_bilinear(
        _rank2_bilinear(form, form, kinetic_factor=kinetic_factor)
    )
    variation = project_54_from_bilinear(
        _rank2_bilinear(
            direct.generator_action(form, a, b),
            form,
            kinetic_factor=kinetic_factor,
        )
        + _rank2_bilinear(
            form,
            direct.generator_action(form, a, b),
            kinetic_factor=kinetic_factor,
        )
    )
    generator = _generator_matrix(a, b)
    expected = generator @ base - base @ generator
    return float(np.max(np.abs(variation - expected)))


def _random_chiral_sigma(seed: int) -> direct.Form:
    rng = np.random.default_rng(seed)
    basis = triplets._hodge_basis("+i")
    coefficients = rng.normal(size=126) + 1j * rng.normal(size=126)
    coefficients /= np.linalg.norm(coefficients)
    return triplets._form(coefficients, basis)


def _classified_triplet_forms() -> dict[str, list[direct.Form]]:
    basis = triplets._hodge_basis("+i")
    classified = triplets._classified_triplets()
    return {
        name: [triplets._form(vector, basis) for vector in states.values()]
        for name, states in classified.items()
    }


def build_report() -> dict[str, Any]:
    p, a, omega = 0.9, 0.4, 0.7
    phi = phi_singlet(p, a, omega)
    numeric_q = phi_54(phi)
    analytic_q = analytic_phi_54_matrix(p, a, omega)
    q_residual = float(np.max(np.abs(numeric_q - analytic_q)))
    coefficients = analytic_phi_54_coefficients(p, a, omega)

    pair_basis = h10.complex_pair_basis()
    h_coefficients: dict[str, list[float]] = {"plus": [], "minus": []}
    for branch in ("plus", "minus"):
        for state in pair_basis[branch]:
            h_coefficients[branch].append(
                h_component_coefficient(p, a, omega, state)
            )

    color_values = h_coefficients["plus"][:3] + h_coefficients["minus"][:3]
    weak_values = h_coefficients["plus"][3:] + h_coefficients["minus"][3:]

    basis126 = triplets._hodge_basis("+i")
    basis_sigma_residual = max(
        float(np.max(np.abs(sigma_hermitian_54(state))))
        for state in basis126
    )
    random_sigma_residual = max(
        float(np.max(np.abs(sigma_hermitian_54(_random_chiral_sigma(seed)))))
        for seed in range(5)
    )
    classified = _classified_triplet_forms()
    classified_residuals = {
        name: max(
            float(np.max(np.abs(sigma_hermitian_54(state))))
            for state in states
        )
        for name, states in classified.items()
    }

    covariance_phi = max(
        _covariance_residual(phi, kinetic_factor=1.0, a=x, b=y)
        for x, y in ((0, 1), (0, 6), (2, 7), (4, 9), (6, 8))
    )
    covariance_h = max(
        _covariance_residual(
            pair_basis["plus"][0], kinetic_factor=1.0, a=x, b=y
        )
        for x, y in ((0, 1), (0, 6), (2, 7), (4, 9), (6, 8))
    )

    phi_norm = float(np.real(direct.tensor_inner(phi, phi)))
    trace_rank2 = float(
        np.trace(_rank2_bilinear(phi, phi, kinetic_factor=1.0)).real
    )

    checks = {
        "phi_54_symmetric": float(np.max(np.abs(numeric_q - numeric_q.T))) < 1e-12,
        "phi_54_traceless": abs(float(np.trace(numeric_q))) < 1e-12,
        "phi_rank2_trace_equals_4_norm": abs(trace_rank2 - 4.0 * phi_norm) < 1e-12,
        "analytic_phi_54_formula": q_residual < 1e-12,
        "six_color_entries_equal": max(color_values) - min(color_values) < 1e-12,
        "four_weak_entries_equal": max(weak_values) - min(weak_values) < 1e-12,
        "color_coefficient_matches_qc": max(
            abs(value - coefficients["q_color_GeV2"]) for value in color_values
        )
        < 1e-12,
        "weak_coefficient_matches_qw": max(
            abs(value - coefficients["q_weak_GeV2"]) for value in weak_values
        )
        < 1e-12,
        "phi_projector_covariant": covariance_phi < 1e-12,
        "h_projector_covariant": covariance_h < 1e-12,
        "chiral_126_basis_Hermitian_54_vanishes": basis_sigma_residual < 1e-12,
        "random_chiral_126_Hermitian_54_vanishes": random_sigma_residual < 1e-12,
        "classified_triplet_Hermitian_54_vanishes": max(
            classified_residuals.values()
        )
        < 1e-12,
        "holomorphic_126x126_54_kept_separate": True,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_MIXED_54_TRIPLET_CHANNEL_DERIVED__OTHER_ANISOTROPIC_CHANNELS_OPEN"
            if not failures
            else "EXACT_MIXED_54_TRIPLET_CHANNEL_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator_convention": {
            "PhiH_54": "lambda_PhiH_54 Q54[Phi]:Q54[H]",
            "PhiSigma_54": "lambda_PhiSigma_54 Q54[Phi]:Q54[Sigma]",
            "HSigma_54": "lambda_HSigma_54 Q54[H]:Q54[Sigma]",
        },
        "exact_phi_54": {
            "basis_order": ["colour"] * 6 + ["weak"] * 4,
            "q_color_formula": "-2 p^2/5 + 4 a^2/15 - omega^2/15",
            "q_weak_formula": "3 p^2/5 - 2 a^2/5 + omega^2/10",
            "trace_identity": "6 q_color + 4 q_weak = 0",
            "benchmark": coefficients,
            "matrix_max_abs_residual": q_residual,
        },
        "triplet_component_result": {
            "T10_Ym13": "lambda_PhiH_54 * q_color",
            "T10bar_Yp13": "lambda_PhiH_54 * q_color",
            "all_three_color_weights_equal": True,
            "weak_10_components": "lambda_PhiH_54 * q_weak",
        },
        "chiral_126_identity": {
            "Hermitian_Q54_126bar": 0.0,
            "basis_max_abs_residual": basis_sigma_residual,
            "random_max_abs_residual": random_sigma_residual,
            "classified_triplet_residuals": classified_residuals,
            "consequence_PhiSigma_Hermitian_54": "identically zero",
            "consequence_HSigma_Hermitian_54": "identically zero",
            "holomorphic_126bar_times_126bar_54": "nonzero separate channel",
        },
        "covariance": {
            "Phi_max_abs_residual": covariance_phi,
            "H_max_abs_residual": covariance_h,
        },
        "newly_closed_subproblem": {
            "210dag210_to_54_on_singlet_vacuum": not failures,
            "210dag210_10dag10_54_triplet_Clebsch": not failures,
            "126bardag126bar_Hermitian_54_vanishing_theorem": not failures,
            "210dag210_126bardag126bar_54_channel_eliminated": not failures,
            "10dag10_126bardag126bar_54_channel_eliminated": not failures,
        },
        "remaining_blockers": {
            "non54_210dag210_10dag10_channels": True,
            "non54_210dag210_126bardag126bar_channels": True,
            "holomorphic_10_126bar_54_channels_with_charge_dressing": True,
            "all_mixing_relevant_210_states": True,
            "complete_component_potential": True,
            "unique_full_vacuum_and_Hessian": True,
            "physical_threshold_spectrum": True,
        },
        "flag": {
            "exact_shared_Hermitian_54_channel_closed": not failures,
            "PhiH_54_triplet_shift_derived": not failures,
            "PhiSigma_Hermitian_54_exists": False,
            "HSigma_Hermitian_54_exists": False,
            "all_anisotropic_channels_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The shared Hermitian 54 channel is exact. 210†210 gives the block-"
            "diagonal q_color/q_weak tensor and shifts both 10_H triplet charges "
            "by q_color. A chiral 126bar has identically zero Hermitian 54, so "
            "the corresponding Phi†Phi Sigma†Sigma and H†H Sigma†Sigma 54 "
            "channels vanish rather than remain unknown."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    exact = report["exact_phi_54"]
    return "\n".join(
        [
            "# Exact mixed 54 triplet channel — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- `q_color = {exact['q_color_formula']}`",
            f"- `q_weak = {exact['q_weak_formula']}`",
            "- `Q54[126bar†126bar] = 0` for a chiral five-form.",
            "- Other anisotropic channels remain open.",
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
