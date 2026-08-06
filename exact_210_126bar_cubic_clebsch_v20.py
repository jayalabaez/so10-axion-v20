#!/usr/bin/env python3
"""Exact cubic 210·126bar†·126bar triplet Clebsches (v20).

The previous exact gate derived the direct Phi-H-Sigmabar portal. This module
uses the same canonical five-form states to construct the independent cubic
non-SUSY invariant

    mu_eta Phi_abcd Sigma*_{abmnp} Sigma_{cdmnp} + permutations,

with ``mu_eta`` of mass dimension one. The fully antisymmetrized reduced
contraction is SO(10)-invariant and Hermitian for real Phi.

On the canonically phase-aligned (t2bar,t4bar) antitriplet sector it gives

    p      -> [[0,0],[0,2]]
    a      -> [[0,0],[0,2/sqrt(3)]]
    omega  -> [[0,4/sqrt(3)],[4/sqrt(3),0]]

in the normalized Cartesian singlet basis. Under
P=p, A=sqrt(3)a, W=sqrt(6)omega these become the published component
structures 2(p+a) and 4 sqrt(2) omega, independently of a SUSY mass matrix.

This closes one nontrivial diagonal/intra-126 Clebsch family only. The full
non-SUSY potential contains additional independent norm and tensor channels;
the complete physical M^2 and proton lifetime remain open.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_triplet_clebsch_v20 as triplet

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_210_126BAR_CUBIC_CLEBSCH_V20.json"
OUT_MD = ROOT / "EXACT_210_126BAR_CUBIC_CLEBSCH_V20.md"


def _double_interior(form: direct.Form, first: int, second: int) -> direct.Form:
    return direct.interior(direct.interior(form, first), second)


def cubic_invariant(
    phi: direct.Form,
    left: direct.Form,
    right: direct.Form,
) -> complex:
    """Canonical independent-component 210·126bar†·126bar contraction.

    The factor two is fixed by the canonical 126 kinetic convention and makes
    the Cartesian result translate directly to 2(p+a) and 4sqrt(2)omega in
    the Aulakh P/A/W convention.
    """
    total = 0.0 + 0.0j
    for indices, phi_value in phi.items():
        a, b, c, d = indices
        antisymmetrized = (
            direct.tensor_inner(
                _double_interior(left, a, b),
                _double_interior(right, c, d),
            )
            - direct.tensor_inner(
                _double_interior(left, a, c),
                _double_interior(right, b, d),
            )
            + direct.tensor_inner(
                _double_interior(left, a, d),
                _double_interior(right, b, c),
            )
        )
        total += 2.0 * phi_value * antisymmetrized
    return total


def _aligned_states() -> dict[str, dict[int, np.ndarray]]:
    basis = triplet._hodge_basis("+i")
    classified = triplet._classified_triplets()
    left = triplet._left_color_basis()
    singlets = direct.singlet_basis()
    result: dict[str, dict[int, np.ndarray]] = {
        "t2_triplet": {},
        "t2bar_antitriplet": {},
        "t4bar_antitriplet": {},
    }
    for index in range(3):
        result["t2_triplet"][index] = triplet._aligned_vector(
            classified["t2_triplet"][index],
            singlets["p"],
            left["triplet"][index],
            basis,
        )
        result["t2bar_antitriplet"][index] = triplet._aligned_vector(
            classified["t2bar_antitriplet"][index],
            singlets["p"],
            left["antitriplet"][index],
            basis,
        )
        result["t4bar_antitriplet"][index] = triplet._aligned_vector(
            classified["t4bar_antitriplet"][index],
            singlets["omega"],
            left["antitriplet"][index],
            basis,
        )
    return result


def _sector_matrices() -> dict[str, Any]:
    basis = triplet._hodge_basis("+i")
    states = _aligned_states()
    singlets = direct.singlet_basis()
    per_weight: dict[str, list[np.ndarray]] = {name: [] for name in singlets}
    t2_triplet_per_weight: dict[str, list[complex]] = {
        name: [] for name in singlets
    }

    for weight in range(3):
        t2bar = triplet._form(states["t2bar_antitriplet"][weight], basis)
        t4bar = triplet._form(states["t4bar_antitriplet"][weight], basis)
        t2 = triplet._form(states["t2_triplet"][weight], basis)
        for name, phi in singlets.items():
            matrix = np.array(
                [
                    [
                        cubic_invariant(phi, t2bar, t2bar),
                        cubic_invariant(phi, t2bar, t4bar),
                    ],
                    [
                        cubic_invariant(phi, t4bar, t2bar),
                        cubic_invariant(phi, t4bar, t4bar),
                    ],
                ],
                dtype=complex,
            )
            per_weight[name].append(matrix)
            t2_triplet_per_weight[name].append(
                cubic_invariant(phi, t2, t2)
            )

    averaged: dict[str, Any] = {}
    maximum_spread = 0.0
    maximum_hermiticity = 0.0
    for name, matrices in per_weight.items():
        mean = sum(matrices) / float(len(matrices))
        spread = max(float(np.max(np.abs(matrix - mean))) for matrix in matrices)
        hermiticity = max(
            float(np.max(np.abs(matrix - matrix.conj().T)))
            for matrix in matrices
        )
        maximum_spread = max(maximum_spread, spread)
        maximum_hermiticity = max(maximum_hermiticity, hermiticity)
        averaged[name] = {
            "basis": ["t2bar", "t4bar"],
            "matrix": [
                [float(np.real_if_close(value).real) for value in row]
                for row in mean
            ],
            "max_color_weight_spread": spread,
            "max_hermiticity_residual": hermiticity,
        }

    maximum_t2_triplet = max(
        float(abs(value))
        for values in t2_triplet_per_weight.values()
        for value in values
    )
    return {
        "antitriplet_sector": averaged,
        "t2_triplet_diagonal_values": {
            name: [float(np.real_if_close(value).real) for value in values]
            for name, values in t2_triplet_per_weight.items()
        },
        "maximum_color_weight_spread": maximum_spread,
        "maximum_hermiticity_residual": maximum_hermiticity,
        "maximum_t2_triplet_entry": maximum_t2_triplet,
    }


def _invariance_residual() -> float:
    basis = triplet._hodge_basis("+i")
    left_vector = np.asarray(
        [complex((17 * i) % 23 - 11, (7 * i) % 19 - 9) for i in range(126)]
    )
    right_vector = np.asarray(
        [complex((11 * i) % 29 - 14, (5 * i) % 17 - 8) for i in range(126)]
    )
    left_vector /= np.linalg.norm(left_vector)
    right_vector /= np.linalg.norm(right_vector)
    left = triplet._form(left_vector, basis)
    right = triplet._form(right_vector, basis)
    singlets = direct.singlet_basis()
    phi = direct.add_forms(
        direct.scale_form(singlets["p"], 0.7),
        direct.scale_form(singlets["a"], 0.2),
        direct.scale_form(singlets["omega"], -0.3),
    )
    maximum = 0.0
    for a, b in ((0, 1), (0, 6), (6, 8), (2, 7), (4, 9)):
        residual = (
            cubic_invariant(direct.generator_action(phi, a, b), left, right)
            + cubic_invariant(
                phi, direct.generator_action(left, a, b), right
            )
            + cubic_invariant(
                phi, left, direct.generator_action(right, a, b)
            )
        )
        maximum = max(maximum, float(abs(residual)))
    return maximum


def build_report() -> dict[str, Any]:
    sector = _sector_matrices()
    matrices = sector["antitriplet_sector"]
    root3 = math.sqrt(3.0)
    expected = {
        "p": np.array([[0.0, 0.0], [0.0, 2.0]]),
        "a": np.array([[0.0, 0.0], [0.0, 2.0 / root3]]),
        "omega": np.array(
            [[0.0, 4.0 / root3], [4.0 / root3, 0.0]]
        ),
    }
    matrix_residuals = {
        name: float(
            np.max(np.abs(np.asarray(matrices[name]["matrix"]) - target))
        )
        for name, target in expected.items()
    }
    invariance = _invariance_residual()

    checks = {
        "so10_invariance": invariance < 1.0e-10,
        "hermitian_for_real_singlets": sector[
            "maximum_hermiticity_residual"
        ]
        < 1.0e-10,
        "color_weight_independent": sector["maximum_color_weight_spread"]
        < 1.0e-10,
        "t2_triplet_unshifted_by_this_cubic": sector[
            "maximum_t2_triplet_entry"
        ]
        < 1.0e-10,
        "p_matrix_exact": matrix_residuals["p"] < 1.0e-10,
        "a_matrix_exact": matrix_residuals["a"] < 1.0e-10,
        "omega_matrix_exact": matrix_residuals["omega"] < 1.0e-10,
        "dimensionful_nonsusy_coefficient_recorded": True,
        "not_using_susy_mass_matrix_as_scalar_m2": True,
        "full_diagonal_cg_not_claimed": True,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return {
        "status": (
            "EXACT_210_126BAR_CUBIC_TRIPLET_CLEBSCH_DERIVED__FULL_POTENTIAL_OPEN"
            if not failures
            else "EXACT_210_126BAR_CUBIC_CLEBSCH_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator": {
            "name": "210_H 126bar_H^dag 126bar_H",
            "potential_coefficient": "mu_eta",
            "coefficient_mass_dimension": 1,
            "component_mass_squared_scaling": "mu_eta * <210>",
            "contraction": (
                "2 Phi_abcd [<i_b i_a Sigma_L, i_d i_c Sigma_R> "
                "- <i_c i_a Sigma_L, i_d i_b Sigma_R> "
                "+ <i_d i_a Sigma_L, i_c i_b Sigma_R>]"
            ),
        },
        "so10_invariance_max_residual": invariance,
        "sector_matrices_cartesian": sector,
        "expected_matrix_residuals": matrix_residuals,
        "aulakh_coordinate_translation": {
            "P": "p",
            "A": "sqrt(3)*a",
            "W": "sqrt(6)*omega",
            "t4bar_diagonal": "2*(p+a)",
            "t2bar_t4bar_mixing_magnitude": "4*sqrt(2)*omega",
            "phase_note": (
                "The exact phase-aligned Cartesian matrix is real symmetric; "
                "the published i factor is removable by component rephasing."
            ),
        },
        "newly_closed_subproblem": {
            "t4bar_diagonal_clebsch_from_210_126dag126": True,
            "t2bar_t4bar_intra126_clebsch": True,
            "canonical_normalization_used": True,
        },
        "remaining_blockers": {
            "all_norm_product_and_independent_tensor_channels": True,
            "10_H_diagonal_component_clebsches": True,
            "complete_126bar_charge_sector_hessian": True,
            "mixing_relevant_210_component_states": True,
            "stationary_positive_full_vacuum": True,
            "physical_threshold_spectrum": True,
            "unique_proton_lifetime": True,
        },
        "flag": {
            "exact_210_126bar_cubic_contraction_derived": not failures,
            "t4bar_diagonal_clebsch_derived": not failures,
            "t2bar_t4bar_mixing_clebsch_derived": not failures,
            "published_eta_magnitude_structure_reproduced": not failures,
            "uses_susy_mass_matrix_as_nonsusy_scalar_m2": False,
            "full_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "The exact SO(10)-invariant cubic contraction gives the normalized "
            "t4bar diagonal 2(p+a/sqrt(3)) and t2bar-t4bar mixing "
            "4 omega/sqrt(3), translating to 2(p+a) and 4sqrt(2)omega. "
            "This closes the nontrivial 210·126bar†·126bar triplet Clebsches, "
            "but not the complete potential or physical M2 spectrum."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    matrices = report["sector_matrices_cartesian"]["antitriplet_sector"]
    return "\n".join(
        [
            "# Exact 210·126bar†·126bar triplet Clebsches — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Cartesian (t2bar,t4bar) matrices",
            "",
            f"- p: `{matrices['p']['matrix']}`",
            f"- a: `{matrices['a']['matrix']}`",
            f"- omega: `{matrices['omega']['matrix']}`",
            "",
            "The cubic coefficient mu_eta has mass dimension one; physical "
            "mass-squared entries scale as mu_eta times the 210 VEV.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
