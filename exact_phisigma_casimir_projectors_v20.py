#!/usr/bin/env python3
"""Pure-irrep Phi-Sigma quartic triplet matrices from pair Casimir projectors.

The Bose-symmetric census proves that the Hermitian

    210_H 210_H 126bar_H^dag 126bar_H

sector has six multiplicity-one common irreps: 1, 45, 210, 770, 5940 and
8910.  This module resolves the remaining recoupling problem without guessing
component coefficients.

Let K=sum_A T_A tensor T_A act on Sym^2(210).  In the repository generator
normalization, K has eigenvalue

    kappa_Q = (2 C2(210)-C2(Q))/2 = (48-C2(Q))/2.

Lagrange polynomials in K give exact spectral projectors.  Applying those
projectors to the already verified invariant

    I_C = ||C_Phi Sigma||^2

isolates one invariant in every common irrep.  The common irreps are
multiplicity one and the projected seed is explicitly nonzero in all six, so
these projected invariants form a complete pure-irrep basis.  The 770 shares
its quadratic-Casimir eigenvalue with 1050+1050bar in Sym^2(210), but those
representations are absent from 126 x 126bar; Schur orthogonality therefore
leaves only the 770 pairing in I_C.

For each pure channel the code exports the exact numerical quadratic-polynomial
coefficients in p,a,omega for the canonical triplet blocks

    Y=-1/3: (t2),
    Y=+1/3: (t2bar,t4bar).

The normalization convention is inherited from the decomposition
I_C=sum_Q I_Q.  Independent couplings may multiply the six I_Q.  This closes
the Phi-Sigma quartic triplet component matrices, not the full scalar
potential, all 210 component sectors, or the physical threshold spectrum.
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_triplet_clebsch_v20 as triplets
import exact_phisigma_bose_channel_census_v20 as census
import exact_portal_norm_square_triplet_channel_v20 as exact_c

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHISIGMA_CASIMIR_PROJECTORS_V20.json"
OUT_MD = ROOT / "EXACT_PHISIGMA_CASIMIR_PROJECTORS_V20.md"

FOUR_INDICES = tuple(itertools.combinations(range(10), 4))
FOUR_INDEX = {indices: position for position, indices in enumerate(FOUR_INDICES)}
FOUR_BASIS = tuple({indices: 1.0 + 0.0j} for indices in FOUR_INDICES)
GENERATOR_LABELS = tuple(itertools.combinations(range(10), 2))

# All distinct K eigenvalues in Sym^2(210).  The value 6 contains
# 770+1050+1050bar; only 770 can pair with 126x126bar.
SPECTRAL_EIGENVALUES = {
    "1": Fraction(24),
    "45": Fraction(16),
    "54": Fraction(14),
    "210": Fraction(12),
    "770_plus_1050_plus_1050bar": Fraction(6),
    "4125": Fraction(0),
    "5940": Fraction(2),
    "8910": Fraction(-4),
}
COMMON_CHANNEL_EIGENVALUES = {
    "1": Fraction(24),
    "45": Fraction(16),
    "210": Fraction(12),
    "770": Fraction(6),
    "5940": Fraction(2),
    "8910": Fraction(-4),
}
NONCOMMON_EIGENVALUES = {"54": Fraction(14), "4125": Fraction(0)}
MONOMIALS = ("p2", "a2", "omega2", "p_a", "p_omega", "a_omega")


def _form_to_vector(form: direct.Form) -> np.ndarray:
    return np.asarray([form.get(indices, 0.0) for indices in FOUR_INDICES], dtype=complex)


@lru_cache(maxsize=1)
def generator_matrices() -> tuple[sparse.csr_matrix, ...]:
    matrices: list[sparse.csr_matrix] = []
    for a, b in GENERATOR_LABELS:
        rows: list[int] = []
        columns: list[int] = []
        values: list[float] = []
        for column, state in enumerate(FOUR_BASIS):
            action = direct.generator_action(state, a, b)
            for indices, value in action.items():
                if abs(value.imag) > 1.0e-13:
                    raise AssertionError("real 210 generator acquired an imaginary entry")
                rows.append(FOUR_INDEX[indices])
                columns.append(column)
                values.append(float(value.real))
        matrices.append(
            sparse.csr_matrix(
                (values, (rows, columns)), shape=(210, 210), dtype=float
            )
        )
    return tuple(matrices)


def pair_casimir(pair_matrix: np.ndarray) -> np.ndarray:
    pair = np.asarray(pair_matrix, dtype=complex)
    if pair.shape != (210, 210):
        raise ValueError("pair matrix must be 210x210")
    result = np.zeros_like(pair)
    for generator in generator_matrices():
        left = generator @ pair
        result += (generator @ left.T).T
    return result


def _poly_multiply_linear(
    coefficients: list[Fraction], root: Fraction
) -> list[Fraction]:
    output = [Fraction(0)] * (len(coefficients) + 1)
    for degree, coefficient in enumerate(coefficients):
        output[degree] -= root * coefficient
        output[degree + 1] += coefficient
    return output


def projector_polynomial(target: Fraction) -> tuple[Fraction, ...]:
    eigenvalues = tuple(dict.fromkeys(SPECTRAL_EIGENVALUES.values()))
    if target not in eigenvalues:
        raise KeyError(target)
    coefficients = [Fraction(1)]
    denominator = Fraction(1)
    for other in eigenvalues:
        if other == target:
            continue
        coefficients = _poly_multiply_linear(coefficients, other)
        denominator *= target - other
    return tuple(coefficient / denominator for coefficient in coefficients)


def casimir_powers(pair_matrix: np.ndarray) -> tuple[np.ndarray, ...]:
    powers = [np.asarray(pair_matrix, dtype=complex)]
    for _ in range(len(set(SPECTRAL_EIGENVALUES.values())) - 1):
        powers.append(pair_casimir(powers[-1]))
    return tuple(powers)


def project_from_powers(
    powers: tuple[np.ndarray, ...], target: Fraction
) -> np.ndarray:
    coefficients = projector_polynomial(target)
    if len(coefficients) != len(powers):
        raise AssertionError("projector degree and Casimir powers disagree")
    result = np.zeros_like(powers[0])
    for coefficient, power in zip(coefficients, powers):
        result += float(coefficient) * power
    return 0.5 * (result + result.T)


def _singlet_vectors() -> dict[str, np.ndarray]:
    forms = direct.singlet_basis()
    return {name: _form_to_vector(forms[name]) for name in ("p", "a", "omega")}


def monomial_pair_matrices() -> dict[str, np.ndarray]:
    vectors = _singlet_vectors()
    p, a, omega = vectors["p"], vectors["a"], vectors["omega"]
    return {
        "p2": np.outer(p, p),
        "a2": np.outer(a, a),
        "omega2": np.outer(omega, omega),
        "p_a": np.outer(p, a) + np.outer(a, p),
        "p_omega": np.outer(p, omega) + np.outer(omega, p),
        "a_omega": np.outer(a, omega) + np.outer(omega, a),
    }


@lru_cache(maxsize=1)
def projected_monomials() -> dict[str, dict[str, np.ndarray]]:
    result: dict[str, dict[str, np.ndarray]] = {
        name: {} for name in SPECTRAL_EIGENVALUES
    }
    for monomial, pair in monomial_pair_matrices().items():
        powers = casimir_powers(pair)
        for eigenspace, eigenvalue in SPECTRAL_EIGENVALUES.items():
            result[eigenspace][monomial] = project_from_powers(powers, eigenvalue)
    return result


@lru_cache(maxsize=1)
def aligned_triplet_forms() -> dict[str, dict[int, direct.Form]]:
    return exact_c._aligned_triplet_forms()


@lru_cache(maxsize=None)
def contraction_map(name: str, weight: int) -> np.ndarray:
    state = aligned_triplet_forms()[name][weight]
    matrix = np.zeros((10, 210), dtype=complex)
    for column, phi_state in enumerate(FOUR_BASIS):
        image = direct.contract(phi_state, state)
        for row in range(10):
            matrix[row, column] = image.get((row,), 0.0)
    return matrix


@lru_cache(maxsize=1)
def triplet_kernels() -> dict[int, dict[str, np.ndarray]]:
    result: dict[int, dict[str, np.ndarray]] = {}
    for weight in range(3):
        maps = {
            "t2": contraction_map("t2_triplet", weight),
            "t2bar": contraction_map("t2bar_antitriplet", weight),
            "t4bar": contraction_map("t4bar_antitriplet", weight),
        }
        result[weight] = {
            "u_00": maps["t2"].conj().T @ maps["t2"],
            "v_00": maps["t2bar"].conj().T @ maps["t2bar"],
            "v_01": maps["t2bar"].conj().T @ maps["t4bar"],
            "v_10": maps["t4bar"].conj().T @ maps["t2bar"],
            "v_11": maps["t4bar"].conj().T @ maps["t4bar"],
        }
    return result


def _evaluate_kernel(pair: np.ndarray, kernel: np.ndarray) -> complex:
    return complex(np.sum(np.asarray(pair) * np.asarray(kernel)))


def blocks_from_pair(pair: np.ndarray, weight: int) -> dict[str, np.ndarray]:
    kernels = triplet_kernels()[weight]
    return {
        "A_u_sigma_GeV2": np.asarray(
            [[_evaluate_kernel(pair, kernels["u_00"])]], dtype=complex
        ),
        "A_v_sigma_GeV2": np.asarray(
            [
                [
                    _evaluate_kernel(pair, kernels["v_00"]),
                    _evaluate_kernel(pair, kernels["v_01"]),
                ],
                [
                    _evaluate_kernel(pair, kernels["v_10"]),
                    _evaluate_kernel(pair, kernels["v_11"]),
                ],
            ],
            dtype=complex,
        ),
    }


def pure_channel_coefficients() -> dict[str, dict[str, dict[str, np.ndarray]]]:
    projected = projected_monomials()
    result: dict[str, dict[str, dict[str, np.ndarray]]] = {}
    spectral_name = {
        "1": "1",
        "45": "45",
        "210": "210",
        "770": "770_plus_1050_plus_1050bar",
        "5940": "5940",
        "8910": "8910",
    }
    for channel, eigenspace in spectral_name.items():
        result[channel] = {}
        for monomial in MONOMIALS:
            by_weight = [
                blocks_from_pair(projected[eigenspace][monomial], weight)
                for weight in range(3)
            ]
            result[channel][monomial] = {
                key: sum(row[key] for row in by_weight) / 3.0
                for key in ("A_u_sigma_GeV2", "A_v_sigma_GeV2")
            }
    return result


def evaluate_channel_blocks(
    channel: str, p: float, a: float, omega: float
) -> dict[str, np.ndarray]:
    coefficients = pure_channel_coefficients()[channel]
    monomial_values = {
        "p2": p * p,
        "a2": a * a,
        "omega2": omega * omega,
        "p_a": p * a,
        "p_omega": p * omega,
        "a_omega": a * omega,
    }
    return {
        key: sum(
            monomial_values[name] * coefficients[name][key]
            for name in MONOMIALS
        )
        for key in ("A_u_sigma_GeV2", "A_v_sigma_GeV2")
    }


def _random_overlap_audit() -> dict[str, float]:
    rng = np.random.default_rng(20260806)
    phi = rng.normal(size=210)
    phi /= np.linalg.norm(phi)
    pair = np.outer(phi, phi)
    powers = casimir_powers(pair)

    basis126 = triplets._hodge_basis("+i")
    left_coefficients = rng.normal(size=126) + 1j * rng.normal(size=126)
    right_coefficients = rng.normal(size=126) + 1j * rng.normal(size=126)
    left_coefficients /= np.linalg.norm(left_coefficients)
    right_coefficients /= np.linalg.norm(right_coefficients)
    left_sigma = triplets._form(left_coefficients, basis126)
    right_sigma = triplets._form(right_coefficients, basis126)

    def map_for(state: direct.Form) -> np.ndarray:
        matrix = np.zeros((10, 210), dtype=complex)
        for column, phi_state in enumerate(FOUR_BASIS):
            image = direct.contract(phi_state, state)
            for row in range(10):
                matrix[row, column] = image.get((row,), 0.0)
        return matrix

    kernel = map_for(left_sigma).conj().T @ map_for(right_sigma)
    result: dict[str, float] = {}
    for channel, eigenvalue in COMMON_CHANNEL_EIGENVALUES.items():
        projected = project_from_powers(powers, eigenvalue)
        result[channel] = float(abs(_evaluate_kernel(projected, kernel)))
    for channel, eigenvalue in NONCOMMON_EIGENVALUES.items():
        projected = project_from_powers(powers, eigenvalue)
        result[f"noncommon_{channel}"] = float(
            abs(_evaluate_kernel(projected, kernel))
        )
    return result


def _complex_payload(value: complex) -> dict[str, float]:
    return {"re": float(np.real(value)), "im": float(np.imag(value))}


def _matrix_payload(matrix: np.ndarray) -> list[list[dict[str, float]]]:
    return [
        [_complex_payload(complex(value)) for value in row]
        for row in np.asarray(matrix, dtype=complex)
    ]


def _coefficient_payload(
    coefficients: dict[str, dict[str, dict[str, np.ndarray]]]
) -> dict[str, Any]:
    return {
        channel: {
            monomial: {
                key: _matrix_payload(block)
                for key, block in rows.items()
            }
            for monomial, rows in channel_rows.items()
        }
        for channel, channel_rows in coefficients.items()
    }


def build_report() -> dict[str, Any]:
    generators = generator_matrices()
    generator_antisymmetry = max(
        float(np.max(np.abs((generator + generator.T).data), initial=0.0))
        for generator in generators
    )
    casimir = sum((generator @ generator for generator in generators), sparse.csr_matrix((210, 210)))
    casimir_residual = casimir + 24.0 * sparse.eye(210, format="csr")
    casimir_max = float(np.max(np.abs(casimir_residual.data), initial=0.0))

    projected = projected_monomials()
    completeness = 0.0
    spectral_residual = 0.0
    for monomial, original in monomial_pair_matrices().items():
        reconstructed = sum(
            (projected[eigenspace][monomial] for eigenspace in SPECTRAL_EIGENVALUES),
            np.zeros((210, 210), dtype=complex),
        )
        completeness = max(completeness, float(np.max(np.abs(reconstructed - original))))
        for eigenspace, eigenvalue in SPECTRAL_EIGENVALUES.items():
            state = projected[eigenspace][monomial]
            spectral_residual = max(
                spectral_residual,
                float(np.max(np.abs(pair_casimir(state) - float(eigenvalue) * state))),
            )

    coefficients = pure_channel_coefficients()
    p, a, omega = 0.9, 0.4, 0.7
    channel_blocks = {
        channel: evaluate_channel_blocks(channel, p, a, omega)
        for channel in COMMON_CHANNEL_EIGENVALUES
    }
    reconstructed = {
        key: sum(
            (blocks[key] for blocks in channel_blocks.values()),
            np.zeros_like(next(iter(channel_blocks.values()))[key]),
        )
        for key in ("A_u_sigma_GeV2", "A_v_sigma_GeV2")
    }
    analytic = exact_c.analytic_sigma_blocks(p, a, omega)
    reconstruction_residual = max(
        float(np.max(np.abs(reconstructed[key] - analytic[key])))
        for key in analytic
    )

    color_spread = 0.0
    hermiticity = 0.0
    noncommon_triplet = 0.0
    benchmark_pair = sum(
        value * monomial_pair_matrices()[name]
        for name, value in {
            "p2": p * p,
            "a2": a * a,
            "omega2": omega * omega,
            "p_a": p * a,
            "p_omega": p * omega,
            "a_omega": a * omega,
        }.items()
    )
    benchmark_powers = casimir_powers(benchmark_pair)
    for channel, eigenvalue in COMMON_CHANNEL_EIGENVALUES.items():
        state = project_from_powers(benchmark_powers, eigenvalue)
        rows = [blocks_from_pair(state, weight) for weight in range(3)]
        average = {
            key: sum(row[key] for row in rows) / 3.0
            for key in ("A_u_sigma_GeV2", "A_v_sigma_GeV2")
        }
        color_spread = max(
            color_spread,
            max(
                float(np.max(np.abs(row[key] - average[key])))
                for row in rows
                for key in average
            ),
        )
        hermiticity = max(
            hermiticity,
            max(
                float(np.max(np.abs(row["A_v_sigma_GeV2"] - row["A_v_sigma_GeV2"].conj().T)))
                for row in rows
            ),
        )
    for eigenvalue in NONCOMMON_EIGENVALUES.values():
        state = project_from_powers(benchmark_powers, eigenvalue)
        for weight in range(3):
            rows = blocks_from_pair(state, weight)
            noncommon_triplet = max(
                noncommon_triplet,
                float(np.max(np.abs(rows["A_u_sigma_GeV2"]))),
                float(np.max(np.abs(rows["A_v_sigma_GeV2"]))),
            )

    overlap = _random_overlap_audit()
    common_minimum_overlap = min(
        overlap[channel] for channel in COMMON_CHANNEL_EIGENVALUES
    )
    noncommon_random_max = max(
        overlap["noncommon_54"], overlap["noncommon_4125"]
    )

    casimir_values = {
        name: float((Fraction(48) - Fraction(
            sum(
                coordinate * (coordinate + 2 * census.RHO[index])
                for index, coordinate in enumerate(census.label_to_e(census.IRREPS[name]["label"]))
            )
        )) / 2)
        for name in ("1", "45", "54", "210", "770", "4125", "5940", "8910")
    }
    checks = {
        "forty_five_generators_constructed": len(generators) == 45,
        "generators_antisymmetric": generator_antisymmetry < 1.0e-12,
        "210_quadratic_Casimir_is_24": casimir_max < 1.0e-12,
        "pair_Casimir_eigenvalues_match_D5_labels": all(
            abs(casimir_values[name] - float(value)) < 1.0e-12
            for name, value in {
                "1": 24,
                "45": 16,
                "54": 14,
                "210": 12,
                "770": 6,
                "4125": 0,
                "5940": 2,
                "8910": -4,
            }.items()
        ),
        "spectral_projectors_complete": completeness < 1.0e-9,
        "spectral_projectors_have_correct_eigenvalues": spectral_residual < 1.0e-8,
        "noncommon_54_and_4125_triplet_pairings_vanish": noncommon_triplet < 1.0e-9,
        "random_noncommon_pairings_vanish": noncommon_random_max < 1.0e-9,
        "seed_overlaps_all_six_common_channels": common_minimum_overlap > 1.0e-10,
        "pure_channel_sum_reconstructs_C_contraction": reconstruction_residual < 1.0e-9,
        "three_color_weights_degenerate": color_spread < 1.0e-9,
        "pure_channel_triplet_matrices_hermitian": hermiticity < 1.0e-9,
        "six_pure_channel_polynomial_matrices_exported": set(coefficients)
        == set(COMMON_CHANNEL_EIGENVALUES),
        "full_scalar_potential_not_claimed": True,
        "physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_PHISIGMA_PURE_IRREP_TRIPLET_MATRICES_DERIVED"
            if not failures
            else "EXACT_PHISIGMA_CASIMIR_PROJECTORS_FAILED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "normalization_convention": (
            "I_C=||C_Phi Sigma||^2=sum_Q I_Q; independent couplings multiply "
            "the six projector-normalized I_Q"
        ),
        "spectral_data": {
            "C2_210": 24,
            "pair_Casimir_eigenvalues": casimir_values,
            "770_degeneracy_note": (
                "kappa=6 also contains 1050+1050bar in Sym2(210), but those "
                "irreps are absent from 126x126bar and therefore do not pair"
            ),
            "projector_completeness_max_abs_residual": completeness,
            "projector_eigen_max_abs_residual": spectral_residual,
            "generator_antisymmetry_residual": generator_antisymmetry,
            "representation_Casimir_residual": casimir_max,
        },
        "overlap_audit": {
            "deterministic_random_pairings": overlap,
            "minimum_common_channel_overlap": common_minimum_overlap,
            "maximum_noncommon_channel_overlap": noncommon_random_max,
        },
        "triplet_reconstruction": {
            "benchmark": {"p": p, "a": a, "omega": omega},
            "pure_channel_blocks": {
                channel: {
                    key: _matrix_payload(matrix)
                    for key, matrix in blocks.items()
                }
                for channel, blocks in channel_blocks.items()
            },
            "reconstructed_C_blocks": {
                key: _matrix_payload(matrix)
                for key, matrix in reconstructed.items()
            },
            "analytic_C_blocks": {
                key: _matrix_payload(matrix)
                for key, matrix in analytic.items()
            },
            "maximum_reconstruction_residual": reconstruction_residual,
            "maximum_color_weight_spread": color_spread,
            "maximum_hermiticity_residual": hermiticity,
            "maximum_noncommon_triplet_pairing": noncommon_triplet,
        },
        "quadratic_polynomial_coefficients": _coefficient_payload(coefficients),
        "newly_closed_subproblem": {
            "C_contraction_recoupled_into_all_six_pure_irreps": not failures,
            "three_previously_missing_independent_directions_constructed": not failures,
            "all_PhiSigma_quartic_triplet_component_matrices": not failures,
        },
        "remaining_blockers": {
            "extend_pure_projectors_to_all_210_component_sectors": True,
            "complete_component_scalar_potential": True,
            "unique_gauge_quotiented_vacuum": True,
            "positive_full_component_Hessian": True,
            "physical_threshold_spectrum": True,
            "component_level_two_loop_matching": True,
            "exact_unique_proton_lifetime": True,
        },
        "flag": {
            "all_PhiSigma_quartic_triplet_Clebsches_complete": not failures,
            "all_PhiSigma_quartic_all_component_Clebsches_complete": False,
            "complete_component_potential": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "Quadratic-Casimir projectors recouple the exact C-contraction into "
            "all six multiplicity-one pure PhiSigma irreps. The canonical triplet "
            "matrices for 1,45,210,770,5940 and 8910 are now exported as exact "
            "quadratic polynomials in p,a,omega."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact Phi–Sigma Casimir projectors — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "- Pure channels: `1,45,210,770,5940,8910`.",
            "- All six canonical triplet matrices are quadratic polynomials in `p,a,omega`.",
            "- The complete all-component potential and physical spectrum remain open.",
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
