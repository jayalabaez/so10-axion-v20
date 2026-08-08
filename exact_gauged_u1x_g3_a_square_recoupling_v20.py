#!/usr/bin/env python3
"""Exact source binding for the constructive G3 A-square recoupling.

Let ``M(Phi)`` be the Hermitian operator on the physical 126bar defined by
the live cubic invariant ``Sigma^dag M(Phi) Sigma``.  This module certifies

    Sigma^dag M(Phi)^2 Sigma =
        40 I_1 + 72 I_45 + 28 I_210
        - 8 I_770 - 12 I_5940 + 12 I_8910.

The calculation never reconstructs irrational floating-point entries.  It
builds the SO(10) generator action, the C-contraction tensor, and the cubic
operator directly as integer/Gaussian-integer arrays.  The pure-channel
projectors are exact ``Fraction`` polynomials in the pair Casimir.  Six
deterministic integer field witnesses give a nonsingular rational evaluation
matrix; because the exact Bose census makes this invariant space
six-dimensional, the unique exact solution proves the recoupling identity.

This closes only the A-square identity.  It does not by itself prove the full
Hessian source binding or close G3.
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
import exact_phisigma_bose_channel_census_v20 as census_source
import exact_phisigma_casimir_projectors_v20 as projector_source
import live_g2_canonical_486_field_chart_v20 as chart

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.md"

CHANNELS = ("1", "45", "210", "770", "5940", "8910")
EXPECTED_WEIGHTS = (40, 72, 28, -8, -12, 12)
WITNESS_SEEDS = (1, 2, 3, 4, 5, 6)
THREE_INDICES = tuple(itertools.combinations(range(10), 3))
THREE_INDEX = {indices: index for index, indices in enumerate(THREE_INDICES)}

RECORDED_WITNESS_MATRIX = (
    ("25384/21", "-124/35", "-116/3", "-1051/15", "-2902/21", "5849/105"),
    ("7772/7", "-4/5", "1324/15", "-2692/15", "-2939/15", "19178/105"),
    ("1180", "132/35", "-356/5", "-251/5", "41086/105", "1123/3"),
    ("6985/7", "516/35", "-332/5", "-118", "-6728/105", "-2533/105"),
    ("1275", "64/35", "-368/15", "737/15", "4612/35", "2334/5"),
    ("7830/7", "-64/35", "312/5", "919/5", "-48997/105", "47008/105"),
)
RECORDED_TARGET = (49_900, 52_804, 45_676, 40_540, 54_072, 55_860)
RECORDED_DETERMINANT = Fraction(-232_879_691_451_546_176, 23_625)


def _as_integer(value: complex) -> tuple[int, int]:
    real = int(round(float(complex(value).real)))
    imaginary = int(round(float(complex(value).imag)))
    if complex(value) != complex(real, imaginary):
        raise ArithmeticError(f"non-Gaussian-integer source entry: {value!r}")
    return real, imaginary


@lru_cache(maxsize=1)
def integer_generators() -> tuple[sparse.csr_matrix, ...]:
    """Build the 210 generator matrices directly over the integers."""
    index = {indices: position for position, indices in enumerate(chart.PHI_INDICES)}
    output: list[sparse.csr_matrix] = []
    for a, b in itertools.combinations(range(10), 2):
        rows: list[int] = []
        columns: list[int] = []
        values: list[int] = []
        for column, indices in enumerate(chart.PHI_INDICES):
            action = direct.generator_action({indices: 1.0 + 0.0j}, a, b)
            for target, coefficient in action.items():
                real, imaginary = _as_integer(coefficient)
                if imaginary:
                    raise ArithmeticError("real 210 generator acquired an imaginary entry")
                rows.append(index[target])
                columns.append(column)
                values.append(real)
        output.append(
            sparse.csr_matrix(
                (np.asarray(values, dtype=np.int64), (rows, columns)),
                shape=(chart.PHI_DIM, chart.PHI_DIM),
                dtype=np.int64,
            )
        )
    return tuple(output)


@lru_cache(maxsize=1)
def integer_contraction_tensor() -> tuple[np.ndarray, np.ndarray]:
    """Return real/imaginary integer parts of C[v,p,A]."""
    real = np.zeros((10, chart.PHI_DIM, chart.SIGMA_COMPLEX_DIM), dtype=np.int8)
    imaginary = np.zeros_like(real)
    sigma_basis = chart.sigma_basis()
    for phi_index, indices in enumerate(chart.PHI_INDICES):
        phi = {indices: 1.0 + 0.0j}
        for sigma_index, sigma in enumerate(sigma_basis):
            image = direct.contract(phi, sigma)
            for vector_index in range(10):
                re, im = _as_integer(image.get((vector_index,), 0.0))
                real[vector_index, phi_index, sigma_index] = re
                imaginary[vector_index, phi_index, sigma_index] = im
    return real, imaginary


def _double_interior_table() -> tuple[np.ndarray, np.ndarray]:
    real = np.zeros((10, 10, chart.SIGMA_COMPLEX_DIM, len(THREE_INDICES)), dtype=np.int8)
    imaginary = np.zeros_like(real)
    for first in range(10):
        for second in range(10):
            if first == second:
                continue
            for state_index, state in enumerate(chart.sigma_basis()):
                form = direct.interior(direct.interior(state, first), second)
                for indices, value in form.items():
                    re, im = _as_integer(value)
                    real[first, second, state_index, THREE_INDEX[indices]] = re
                    imaginary[first, second, state_index, THREE_INDEX[indices]] = im
    return real, imaginary


@lru_cache(maxsize=1)
def integer_cubic_operators() -> tuple[np.ndarray, np.ndarray]:
    """Return exact Gaussian-integer M[p,A,B] for the cubic invariant."""
    table_real, table_imaginary = _double_interior_table()
    real = np.zeros(
        (chart.PHI_DIM, chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM),
        dtype=np.int16,
    )
    imaginary = np.zeros_like(real)

    def product(first: int, second: int, third: int, fourth: int) -> tuple[np.ndarray, np.ndarray]:
        xr = table_real[first, second].astype(np.int64)
        xi = table_imaginary[first, second].astype(np.int64)
        yr = table_real[third, fourth].astype(np.int64)
        yi = table_imaginary[third, fourth].astype(np.int64)
        # conj(X) @ Y.T
        return xr @ yr.T + xi @ yi.T, xr @ yi.T - xi @ yr.T

    for phi_index, (a, b, c, d) in enumerate(chart.PHI_INDICES):
        first_r, first_i = product(a, b, c, d)
        second_r, second_i = product(a, c, b, d)
        third_r, third_i = product(a, d, b, c)
        real[phi_index] = 2 * (first_r - second_r + third_r)
        imaginary[phi_index] = 2 * (first_i - second_i + third_i)
    return real, imaginary


def deterministic_integer_fields(seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return dense, reproducible integer Phi and Gaussian-integer Sigma."""
    state = int(seed)
    values: list[int] = []
    for _ in range(chart.PHI_DIM + 2 * chart.SIGMA_COMPLEX_DIM):
        state = (1_103_515_245 * state + 12_345) & 0x7FFF_FFFF
        values.append(state % 3 - 1)
    vector = np.asarray(values, dtype=np.int64)
    return (
        vector[: chart.PHI_DIM],
        vector[chart.PHI_DIM : chart.PHI_DIM + chart.SIGMA_COMPLEX_DIM],
        vector[chart.PHI_DIM + chart.SIGMA_COMPLEX_DIM :],
    )


def integer_pair_casimir(pair: np.ndarray) -> np.ndarray:
    value = np.asarray(pair, dtype=np.int64)
    output = np.zeros_like(value)
    for generator in integer_generators():
        output += (generator @ value) @ generator.T
    return output


def exact_witness(seed: int) -> dict[str, Any]:
    phi, sigma_real, sigma_imaginary = deterministic_integer_fields(seed)
    contraction_real, contraction_imaginary = integer_contraction_tensor()
    c_real = (
        np.einsum("vpa,a->vp", contraction_real, sigma_real, optimize=True)
        - np.einsum("vpa,a->vp", contraction_imaginary, sigma_imaginary, optimize=True)
    )
    c_imaginary = (
        np.einsum("vpa,a->vp", contraction_real, sigma_imaginary, optimize=True)
        + np.einsum("vpa,a->vp", contraction_imaginary, sigma_real, optimize=True)
    )
    kernel_real = c_real.T @ c_real + c_imaginary.T @ c_imaginary
    kernel_imaginary = c_real.T @ c_imaginary - c_imaginary.T @ c_real

    pair = np.outer(phi, phi)
    casimir_scalars: list[int] = []
    maximum_power_entry = 0
    maximum_sum_bound = 0
    for power in range(8):
        maximum_power_entry = max(maximum_power_entry, int(np.max(np.abs(pair))))
        bound = int(np.max(np.abs(pair))) * int(np.max(np.abs(kernel_real))) * pair.size
        maximum_sum_bound = max(maximum_sum_bound, bound)
        if bound >= 2**62:
            raise OverflowError("the exact int64 Casimir contraction bound is unsafe")
        imaginary_residual = int(np.sum(pair * kernel_imaginary, dtype=np.int64))
        if imaginary_residual:
            raise ArithmeticError("a real Phi pair produced an imaginary invariant")
        casimir_scalars.append(int(np.sum(pair * kernel_real, dtype=np.int64)))
        if power != 7:
            pair = integer_pair_casimir(pair)

    channel_values: list[Fraction] = []
    for channel in CHANNELS:
        polynomial = projector_source.projector_polynomial(
            projector_source.COMMON_CHANNEL_EIGENVALUES[channel]
        )
        channel_values.append(
            sum(
                (coefficient * value for coefficient, value in zip(polynomial, casimir_scalars, strict=True)),
                Fraction(0),
            )
        )

    operator_real, operator_imaginary = integer_cubic_operators()
    matrix_real = np.tensordot(phi, operator_real, axes=(0, 0))
    matrix_imaginary = np.tensordot(phi, operator_imaginary, axes=(0, 0))
    image_real = matrix_real @ sigma_real - matrix_imaginary @ sigma_imaginary
    image_imaginary = matrix_real @ sigma_imaginary + matrix_imaginary @ sigma_real
    target = sum(int(value) ** 2 for value in image_real) + sum(
        int(value) ** 2 for value in image_imaginary
    )
    residual = sum(
        Fraction(weight) * value
        for weight, value in zip(EXPECTED_WEIGHTS, channel_values, strict=True)
    ) - target
    return {
        "seed": seed,
        "channel_values": tuple(channel_values),
        "A_squared": target,
        "expected_weight_residual": residual,
        "maximum_abs_casimir_power_entry": maximum_power_entry,
        "maximum_int64_sum_bound": maximum_sum_bound,
    }


def fraction_determinant(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    work = [list(row) for row in matrix]
    determinant = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            determinant *= -1
        value = work[column][column]
        determinant *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column], strict=True)
            ]
    return determinant


def solve_exact(matrix: tuple[tuple[Fraction, ...], ...], target: tuple[int, ...]) -> tuple[Fraction, ...]:
    size = len(matrix)
    work = [list(row) + [Fraction(value)] for row, value in zip(matrix, target, strict=True)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        value = work[column][column]
        work[column] = [entry / value for entry in work[column]]
        for row in range(size):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(work[row], work[column], strict=True)
            ]
    return tuple(work[row][-1] for row in range(size))


def recorded_certificate() -> dict[str, Any]:
    matrix = tuple(tuple(Fraction(value) for value in row) for row in RECORDED_WITNESS_MATRIX)
    determinant = fraction_determinant(matrix)
    solution = solve_exact(matrix, RECORDED_TARGET)
    residuals = tuple(
        sum(weight * value for weight, value in zip(solution, row, strict=True)) - target
        for row, target in zip(matrix, RECORDED_TARGET, strict=True)
    )
    return {
        "source_arithmetic": "Z[i] tensors plus Fraction Casimir polynomials",
        "invariant_space_dimension": 6,
        "multiplicity_one_channels": CHANNELS,
        "witness_seeds": WITNESS_SEEDS,
        "witness_matrix": matrix,
        "A_squared_targets": RECORDED_TARGET,
        "witness_determinant": determinant,
        "unique_weights": solution,
        "identity_residuals": residuals,
        "source_binding_exact": True,
        "proof_grade": True,
    }


def recompute_exact_certificate() -> dict[str, Any]:
    witnesses = tuple(exact_witness(seed) for seed in WITNESS_SEEDS)
    matrix = tuple(tuple(row["channel_values"]) for row in witnesses)
    target = tuple(int(row["A_squared"]) for row in witnesses)
    result = recorded_certificate()
    result.update(
        {
            "recomputed": True,
            "witness_matrix": matrix,
            "A_squared_targets": target,
            "witness_determinant": fraction_determinant(matrix),
            "unique_weights": solve_exact(matrix, target),
            "identity_residuals": tuple(row["expected_weight_residual"] for row in witnesses),
            "source_tensor_counts": {
                "generator_nonzero_entries": sum(matrix.nnz for matrix in integer_generators()),
                "C_Gaussian_nonzero_entries": int(
                    np.count_nonzero(integer_contraction_tensor()[0] | integer_contraction_tensor()[1])
                ),
                "M_Gaussian_nonzero_entries": int(
                    np.count_nonzero(integer_cubic_operators()[0] | integer_cubic_operators()[1])
                ),
            },
            "maximum_abs_casimir_power_entry": max(
                int(row["maximum_abs_casimir_power_entry"]) for row in witnesses
            ),
            "maximum_int64_sum_bound": max(
                int(row["maximum_int64_sum_bound"]) for row in witnesses
            ),
        }
    )
    return result


def build_report(*, recompute: bool = False) -> dict[str, Any]:
    certificate = recompute_exact_certificate() if recompute else recorded_certificate()
    census = census_source.build_report() if recompute else None
    checks = {
        "exact_Bose_channel_count_is_six": certificate["invariant_space_dimension"] == 6,
        "six_witness_evaluation_matrix_is_nonsingular": certificate["witness_determinant"] != 0,
        "recorded_exact_determinant_matches": certificate["witness_determinant"] == RECORDED_DETERMINANT,
        "unique_exact_weights_match_A_square_identity": certificate["unique_weights"] == tuple(map(Fraction, EXPECTED_WEIGHTS)),
        "all_exact_witness_residuals_vanish": all(value == 0 for value in certificate["identity_residuals"]),
        "recomputed_sources_match_recorded_witness": (not recompute) or (
            certificate["witness_matrix"]
            == tuple(tuple(Fraction(value) for value in row) for row in RECORDED_WITNESS_MATRIX)
            and certificate["A_squared_targets"] == RECORDED_TARGET
        ),
        "upstream_exact_census_passes": (not recompute) or (census is not None and census["n_failed"] == 0),
        "G3_not_closed_by_recoupling_alone": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": "EXACT_A_SQUARE_RECOUPLING_CERTIFIED" if not failures else "A_SQUARE_RECOUPLING_FAILED",
        "overall_state": "CLOSED_SUBPROBLEM" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certificate": certificate,
        "identity": (
            "||M(Phi)Sigma||^2=40 I1+72 I45+28 I210-8 I770-12 I5940+12 I8910"
        ),
        "flags": {
            "A_square_recoupling_exactly_source_bound": not failures,
            "complete_potential_BFB_exactly_certified": False,
            "full_Hessian_exactly_source_bound": False,
            "strict_local_minimum_certified": False,
            "G3_closed": False,
        },
        "remaining_scope": (
            "The full P+Delta Hessian still needs direct exact-source assembly; "
            "this finite invariant identity alone does not certify rank 448."
        ),
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    return value


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact G3 A-square recoupling certificate -- v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["identity"]
        + "\n\n"
        + "The six exact witnesses have a nonzero rational determinant and "
        "fix the unique weights `(40,72,28,-8,-12,12)`. This closes the "
        "recoupling subproblem only; the full exact Hessian source binding and "
        "G3 remain open.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recompute", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(recompute=args.recompute)
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
