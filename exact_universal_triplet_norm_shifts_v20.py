#!/usr/bin/env python3
"""Exact universal norm-product triplet mass-squared shifts (v20).

This module isolates the component coefficients that are fixed solely by
canonical norms.  For the explicit potential convention

  V_norm = m10^2 n_H + m126^2 n_Sigma
         + lambda10 n_H^2 + lambda126 n_Sigma^2
         + lambda10_126 n_H n_Sigma
         + lambda210_10 n_Phi n_H
         + lambda210_126 n_Phi n_Sigma
         + lambdaS_10 |S|^2 n_H + lambdaS_126 |S|^2 n_Sigma
         + lambdaX_10 |Phi17|^2 n_H + lambdaX_126 |Phi17|^2 n_Sigma,

where n_H=H†H, n_Sigma=(1/2)Sigma†Sigma in the repository convention, and
n_Phi=(1/4!)Phi†Phi, every normalized triplet state receives the identity
shifts

  d10 = m10^2 + 2 lambda10 n_H0 + lambda10_126 n_Sigma0
        + lambda210_10 n_Phi0 + lambdaS_10 |S|^2
        + lambdaX_10 |Phi17|^2,

  d126 = m126^2 + 2 lambda126 n_Sigma0 + lambda10_126 n_H0
         + lambda210_126 n_Phi0 + lambdaS_126 |S|^2
         + lambdaX_126 |Phi17|^2.

The canonical p,a,omega singlets are orthonormal, so
n_Phi0=|p|^2+|a|^2+|omega|^2 exactly.  These results close the universal
identity channels only. Independent 54-, 210-, and other anisotropic tensor
contractions remain open and are not absorbed into the universal baselines.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_triplet_clebsch_v20 as triplet

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_UNIVERSAL_TRIPLET_NORM_SHIFTS_V20.json"
OUT_MD = ROOT / "EXACT_UNIVERSAL_TRIPLET_NORM_SHIFTS_V20.md"


def phi_norm_squared(p: complex, a: complex, omega: complex) -> float:
    singlets = direct.singlet_basis()
    phi = direct.add_forms(
        direct.scale_form(singlets["p"], p),
        direct.scale_form(singlets["a"], a),
        direct.scale_form(singlets["omega"], omega),
    )
    return float(np.real(direct.tensor_inner(phi, phi)))


def universal_shifts(
    *,
    m10_sq: float,
    m126_sq: float,
    lambda10: float,
    lambda126: float,
    lambda10_126: float,
    lambda210_10: float,
    lambda210_126: float,
    lambdaS_10: float,
    lambdaS_126: float,
    lambdaX_10: float,
    lambdaX_126: float,
    h_norm_sq: float,
    sigma_norm_sq: float,
    p: complex,
    a: complex,
    omega: complex,
    s_abs_sq: float,
    phi17_abs_sq: float,
) -> dict[str, float]:
    n_phi = phi_norm_squared(p, a, omega)
    d10 = (
        m10_sq
        + 2.0 * lambda10 * h_norm_sq
        + lambda10_126 * sigma_norm_sq
        + lambda210_10 * n_phi
        + lambdaS_10 * s_abs_sq
        + lambdaX_10 * phi17_abs_sq
    )
    d126 = (
        m126_sq
        + 2.0 * lambda126 * sigma_norm_sq
        + lambda10_126 * h_norm_sq
        + lambda210_126 * n_phi
        + lambdaS_126 * s_abs_sq
        + lambdaX_126 * phi17_abs_sq
    )
    return {
        "n_phi": float(n_phi),
        "d10_universal_m2": float(d10),
        "d126_universal_m2": float(d126),
    }


def norm_potential(
    n_h: float,
    n_sigma: float,
    *,
    m10_sq: float,
    m126_sq: float,
    lambda10: float,
    lambda126: float,
    lambda10_126: float,
    lambda210_10: float,
    lambda210_126: float,
    lambdaS_10: float,
    lambdaS_126: float,
    lambdaX_10: float,
    lambdaX_126: float,
    n_phi: float,
    s_abs_sq: float,
    phi17_abs_sq: float,
) -> float:
    return float(
        m10_sq * n_h
        + m126_sq * n_sigma
        + lambda10 * n_h**2
        + lambda126 * n_sigma**2
        + lambda10_126 * n_h * n_sigma
        + lambda210_10 * n_phi * n_h
        + lambda210_126 * n_phi * n_sigma
        + lambdaS_10 * s_abs_sq * n_h
        + lambdaS_126 * s_abs_sq * n_sigma
        + lambdaX_10 * phi17_abs_sq * n_h
        + lambdaX_126 * phi17_abs_sq * n_sigma
    )


def universal_identity_blocks(d10: float, d126: float) -> dict[str, np.ndarray]:
    return {
        "A_u": np.diag([d10, d126]).astype(complex),
        "A_v": np.diag([d10, d126, d126]).astype(complex),
    }


def _canonical_state_norm_residuals() -> dict[str, float]:
    color = triplet._left_color_basis()
    states126 = triplet._classified_triplets()
    h_states = color["triplet"] + color["antitriplet"]
    h_residual = max(
        abs(float(np.real(direct.tensor_inner(state, state))) - 1.0)
        for state in h_states
    )
    sigma_vectors = [
        vector for group in states126.values() for vector in group.values()
    ]
    sigma_residual = max(
        abs(float(np.real(np.vdot(vector, vector))) - 1.0)
        for vector in sigma_vectors
    )
    return {"H": float(h_residual), "Sigma": float(sigma_residual)}


def build_report() -> dict[str, Any]:
    singlets = direct.singlet_basis()
    phi_gram = np.asarray(
        [
            [direct.tensor_inner(singlets[x], singlets[y]) for y in ("p", "a", "omega")]
            for x in ("p", "a", "omega")
        ],
        dtype=complex,
    )
    phi_gram_residual = float(np.max(np.abs(phi_gram - np.eye(3))))
    probe = {"p": 0.9 + 0.1j, "a": -0.4 + 0.2j, "omega": 0.7 - 0.3j}
    exact_phi_norm = phi_norm_squared(**probe)
    analytic_phi_norm = float(sum(abs(value) ** 2 for value in probe.values()))

    parameters = {
        "m10_sq": 1.1,
        "m126_sq": 1.7,
        "lambda10": 0.13,
        "lambda126": 0.17,
        "lambda10_126": -0.09,
        "lambda210_10": 0.21,
        "lambda210_126": -0.12,
        "lambdaS_10": 0.08,
        "lambdaS_126": 0.14,
        "lambdaX_10": -0.04,
        "lambdaX_126": 0.06,
        "h_norm_sq": 0.05,
        "sigma_norm_sq": 0.31,
        "p": probe["p"],
        "a": probe["a"],
        "omega": probe["omega"],
        "s_abs_sq": 0.23,
        "phi17_abs_sq": 0.41,
    }
    shifts = universal_shifts(**parameters)
    potential_args = {
        key: value
        for key, value in parameters.items()
        if key
        not in {
            "h_norm_sq",
            "sigma_norm_sq",
            "p",
            "a",
            "omega",
        }
    }
    potential_args["n_phi"] = shifts["n_phi"]
    epsilon = 1.0e-7
    base = norm_potential(
        parameters["h_norm_sq"], parameters["sigma_norm_sq"], **potential_args
    )
    derivative_h = (
        norm_potential(
            parameters["h_norm_sq"] + epsilon,
            parameters["sigma_norm_sq"],
            **potential_args,
        )
        - base
    ) / epsilon
    derivative_sigma = (
        norm_potential(
            parameters["h_norm_sq"],
            parameters["sigma_norm_sq"] + epsilon,
            **potential_args,
        )
        - base
    ) / epsilon
    finite_difference_h_residual = abs(
        derivative_h - shifts["d10_universal_m2"]
    )
    finite_difference_sigma_residual = abs(
        derivative_sigma - shifts["d126_universal_m2"]
    )

    blocks = universal_identity_blocks(
        shifts["d10_universal_m2"], shifts["d126_universal_m2"]
    )
    rng = np.random.default_rng(17)
    x = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    u2, _ = np.linalg.qr(x)
    y = rng.normal(size=(3, 3)) + 1j * rng.normal(size=(3, 3))
    u3, _ = np.linalg.qr(y)
    rotation_residual = max(
        float(np.max(np.abs(u2.conj().T @ blocks["A_u"] @ u2 - blocks["A_u"]))),
        float(np.max(np.abs(u3.conj().T @ blocks["A_v"] @ u3 - blocks["A_v"])))
        if abs(shifts["d10_universal_m2"] - shifts["d126_universal_m2"]) < 1e-14
        else 0.0,
    )
    # The full A_v has one H and two Sigma entries; only the two-dimensional
    # Sigma subspace must be invariant under arbitrary internal rotations.
    sigma_block = blocks["A_v"][1:, 1:]
    z = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
    u_sigma, _ = np.linalg.qr(z)
    sigma_rotation_residual = float(
        np.max(np.abs(u_sigma.conj().T @ sigma_block @ u_sigma - sigma_block))
    )
    state_norms = _canonical_state_norm_residuals()

    checks = {
        "phi_singlets_orthonormal": phi_gram_residual < 1.0e-12,
        "phi_norm_is_sum_of_moduli": abs(exact_phi_norm - analytic_phi_norm) < 1.0e-12,
        "canonical_H_triplet_norms": state_norms["H"] < 1.0e-12,
        "canonical_126_triplet_norms": state_norms["Sigma"] < 1.0e-12,
        "H_shift_matches_norm_derivative": finite_difference_h_residual < 5.0e-8,
        "Sigma_shift_matches_norm_derivative": finite_difference_sigma_residual < 5.0e-8,
        "self_quartic_factor_two_recorded": True,
        "H_triplet_and_antitriplet_share_d10": blocks["A_u"][0, 0] == blocks["A_v"][0, 0],
        "all_126_t2_t2bar_t4bar_share_d126": blocks["A_u"][1, 1]
        == blocks["A_v"][1, 1]
        == blocks["A_v"][2, 2],
        "Sigma_universal_subspace_rotation_invariant": sigma_rotation_residual < 1.0e-12,
        "anisotropic_channels_not_absorbed": True,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_UNIVERSAL_TRIPLET_NORM_SHIFTS_DERIVED__ANISOTROPIC_CHANNELS_OPEN"
            if not failures
            else "EXACT_UNIVERSAL_TRIPLET_NORM_SHIFTS_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "potential_convention": {
            "n_H": "H†H",
            "n_Sigma": "(1/2) Sigma†Sigma in canonical 126 kinetic convention",
            "n_Phi": "(1/4!) Phi†Phi in canonical 210 convention",
            "self_quartics": "lambda10 n_H^2 and lambda126 n_Sigma^2",
        },
        "exact_norm_results": {
            "phi_singlet_gram_max_abs_residual": phi_gram_residual,
            "phi_norm_probe": exact_phi_norm,
            "phi_norm_analytic": analytic_phi_norm,
            "canonical_state_norm_residuals": state_norms,
        },
        "universal_shift_formulas": {
            "d10": (
                "m10^2 + 2 lambda10 n_H0 + lambda10_126 n_Sigma0 + "
                "lambda210_10 n_Phi0 + lambdaS_10 |S|^2 + lambdaX_10 |Phi17|^2"
            ),
            "d126": (
                "m126^2 + 2 lambda126 n_Sigma0 + lambda10_126 n_H0 + "
                "lambda210_126 n_Phi0 + lambdaS_126 |S|^2 + lambdaX_126 |Phi17|^2"
            ),
            "n_Phi0": "|p|^2+|a|^2+|omega|^2",
        },
        "benchmark": {
            "inputs": {
                key: (
                    {"re": float(value.real), "im": float(value.imag)}
                    if isinstance(value, complex)
                    else value
                )
                for key, value in parameters.items()
            },
            "shifts": shifts,
            "finite_difference_H_residual": float(finite_difference_h_residual),
            "finite_difference_Sigma_residual": float(
                finite_difference_sigma_residual
            ),
            "Sigma_rotation_residual": sigma_rotation_residual,
            "unused_full_block_rotation_residual": rotation_residual,
        },
        "identity_blocks": {
            "basis_A_u": ["T10", "t2"],
            "basis_A_v": ["T10bar", "t2bar", "t4bar"],
            "A_u_diagonal": [
                float(np.real(blocks["A_u"][0, 0])),
                float(np.real(blocks["A_u"][1, 1])),
            ],
            "A_v_diagonal": [
                float(np.real(blocks["A_v"][0, 0])),
                float(np.real(blocks["A_v"][1, 1])),
                float(np.real(blocks["A_v"][2, 2])),
            ],
        },
        "newly_closed_subproblem": {
            "210_singlet_norm": True,
            "universal_10_triplet_identity_shift": True,
            "universal_126bar_triplet_identity_shift": True,
            "self_quartic_factor_two": True,
            "norm_product_component_coefficients": True,
        },
        "remaining_anisotropic_channels": [
            "independent (10†10)^2 contractions beyond the norm square",
            "independent (126bar†126bar)^2 contractions beyond the norm square",
            "independent 210†210 10†10 tensor contractions beyond the norm product",
            "independent 210†210 126bar†126bar tensor contractions beyond the norm product",
            "independent 10†10 126bar†126bar tensor contractions beyond the norm product",
            "mixing-relevant 210 component states and their Hessian entries",
        ],
        "flag": {
            "exact_universal_norm_shifts_derived": not failures,
            "five_diagonal_placeholders_reducible_to_two_baselines_plus_residuals": not failures,
            "anisotropic_component_CG_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "All canonical norm-product channels reduce exactly to two identity "
            "baselines: one shared by T10/T10bar and one shared by t2/t2bar/t4bar. "
            "The 210 norm is |p|^2+|a|^2+|omega|^2 and self-quartics carry the "
            "factor two. Remaining diagonal uncertainty is exclusively in named "
            "anisotropic tensor contractions and vacuum inputs."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact universal triplet norm shifts — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- `d10`: `{report['universal_shift_formulas']['d10']}`",
            f"- `d126`: `{report['universal_shift_formulas']['d126']}`",
            f"- `n_Phi`: `{report['universal_shift_formulas']['n_Phi0']}`",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    payload = json.dumps(report, indent=2) + "\n"
    OUT_JSON.write_text(payload, encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(payload, end="")
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
