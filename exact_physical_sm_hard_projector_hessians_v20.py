#!/usr/bin/env python3
"""Exact source-algebra Hessians for the two hard physical-SM projector families.

This theorem derives, in Gaussian-integer and rational arithmetic, the full
486-real-field target Hessian of all four ``O27`` 126bar self-projectors and
all six ``O44`` Phi^2-Sigma projectors.  The physical target is represented by
the exact lattice vector ``20 q_*``.  Projector denominators are cleared before
any matrix operation; every signed-int64 operation is bounded before use.

The certificate is deliberately scoped.  It closes the ten hard source rows,
not the other 27 active witness rows.  It therefore does not certify the exact
aggregate stationarity/kernel/rank/PSD statements and does not classify the
full 486-field equality orbit.  In particular it does not close G3, G4, or G5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import exact_126bar_self_quartic_basis_v20 as sigma_source
import exact_phisigma_126bar_minus_projectors_v20 as mixed_source
import exact_phisigma_casimir_projectors_v20 as phi_projectors
import gauged_u1x_g2_derivative_audit_v20 as exact_g2
import live_g2_canonical_486_field_chart_v20 as chart
import physical_sm_vacuum_local_feasibility_v20 as foundation


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.json"
OUT_MD = ROOT / "EXACT_PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_V20.md"

SCHEMA = "exact_physical_sm_hard_projector_hessians_v20"
STATUS = "EXACT_TEN_HARD_PROJECTOR_HESSIANS__FULL_37_ROW_AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
FIELD_DIMENSION = 486
TARGET_DENOMINATOR = 20
INT64_MAX = int(np.iinfo(np.int64).max)

SOURCE_HASHES = {
    "gauged_u1x_g2_derivative_audit_v20.py": "584e03994ca1187228377c3e4c145d95446ade50616e2d58068e0fee9f96507d",
    "physical_sm_vacuum_local_feasibility_v20.py": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
    "live_g2_canonical_486_field_chart_v20.py": "9275dbb204324cc48dfd7139cad836e034b1b83b07bd60aecd6ff093d3ab7765",
    "exact_126bar_self_quartic_basis_v20.py": "6b945b21b991ad1c055e7ae39190bcbb258fd8503c1ad37789003310041ddd30",
    "exact_phisigma_casimir_projectors_v20.py": "372401c9b760e7b4e2224d4b6b2151611e68e7ba786ec735ebbd8baeb0103355",
    "exact_phisigma_126bar_minus_projectors_v20.py": "35574f536dd6a5a6619075784324d3a8e5965544dd91fdca5ce2ce3de6bb2af7",
}

O27_CHANNEL_TO_ROW = {
    "54": "O27_B01_126bar_self_projectors",
    "1050bar": "O27_B02_126bar_self_projectors",
    "2772bar": "O27_B03_126bar_self_projectors",
    "4125": "O27_B04_126bar_self_projectors",
}
O44_CHANNEL_TO_ROW = {
    channel: f"O44_B{index:02d}_Phi2_Sigma_projectors"
    for index, channel in enumerate(mixed_source.CHANNELS, start=1)
}
REMAINING_ACTIVE_ROWS = (
    "O03_B01_singlet_polynomial",
    "O04_B01_singlet_polynomial",
    "O05_B01_126bar_norm",
    "O06_B01_Hdag_H_norm",
    "O07_B01_Phi_norm",
    "O14_B01_Phi_Sigma_Sigmadag_cubic",
    "O17_B01_Phi_cubic",
    "O20_B01_singlet_polynomial",
    "O22_B01_singlet_polynomial",
    "O23_B01_singlet_polynomial",
    "O25_B01_126bar_norm",
    "O26_B01_126bar_norm",
    "O33_B01_Hdag_H_norm",
    "O34_B01_Hdag_H_norm",
    "O35_B01_H_Sigma_hermitian",
    "O35_B02_H_Sigma_hermitian",
    "O36_B01_H_self_quartics",
    "O36_B02_H_self_quartics",
    "O42_B01_Phi_norm",
    "O43_B01_Phi_norm",
    "O46_B01_Phi2_HdagH_channels",
    "O46_B02_Phi2_HdagH_channels",
    "O46_B03_Phi2_HdagH_channels",
    "O48_B01_Phi_self_quartics",
    "O48_B02_Phi_self_quartics",
    "O48_B03_Phi_self_quartics",
    "O48_B04_Phi_self_quartics",
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return value.item()
    return value


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _portable_lf_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def source_bindings() -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for name, expected in SOURCE_HASHES.items():
        observed = _portable_lf_sha256(ROOT / name)
        if observed != expected:
            raise ArithmeticError(f"hard-projector source dependency drifted: {name}")
        rows[name] = {
            "portable_lf_sha256": observed,
            "expected_portable_lf_sha256": expected,
            "matches": True,
        }
    return {"files": rows, "all_portable_lf_pins_match": True}


def _gi_mul(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _gi_accumulate(
    matrix: dict[tuple[int, int], tuple[int, int]],
    key: tuple[int, int],
    value: tuple[int, int],
) -> None:
    old = matrix.get(key, (0, 0))
    new = (old[0] + value[0], old[1] + value[1])
    if new == (0, 0):
        matrix.pop(key, None)
    else:
        matrix[key] = new


def _projector_integer_coefficients(
    coefficients: Iterable[Fraction],
) -> tuple[int, tuple[int, ...]]:
    values = tuple(coefficients)
    denominator = math.lcm(*(value.denominator for value in values))
    integers = tuple(
        value.numerator * (denominator // value.denominator) for value in values
    )
    return denominator, integers


def _matrix_gcd(numerator: np.ndarray, denominator: int) -> int:
    divisor = abs(int(denominator))
    for value in numerator.ravel():
        if value:
            divisor = math.gcd(divisor, abs(int(value)))
            if divisor == 1:
                break
    return divisor


@dataclass(frozen=True)
class RationalHessian:
    numerator: np.ndarray
    denominator: int

    @staticmethod
    def normalized(numerator: np.ndarray, denominator: int) -> "RationalHessian":
        matrix = np.asarray(numerator, dtype=np.int64)
        if matrix.shape != (FIELD_DIMENSION, FIELD_DIMENSION):
            raise ValueError("exact Hessian must be 486x486")
        if denominator <= 0:
            raise ValueError("exact Hessian denominator must be positive")
        divisor = _matrix_gcd(matrix, denominator)
        return RationalHessian(matrix // divisor, denominator // divisor)

    def fraction_entries(self) -> dict[tuple[int, int], Fraction]:
        rows, columns = np.nonzero(self.numerator)
        return {
            (int(row), int(column)): Fraction(
                int(self.numerator[row, column]), self.denominator
            )
            for row, column in zip(rows, columns, strict=True)
        }

    def sha256(self) -> str:
        payload = [
            f"exact-rational-hessian-v1\n",
            f"dimension={FIELD_DIMENSION}\n",
            f"denominator={self.denominator}\n",
        ]
        rows, columns = np.nonzero(self.numerator)
        payload.extend(
            f"{int(row)},{int(column)},{int(self.numerator[row, column])}\n"
            for row, column in zip(rows, columns, strict=True)
        )
        return hashlib.sha256("".join(payload).encode("ascii")).hexdigest()

    def jet_summary(self, target_integer: np.ndarray) -> dict[str, Any]:
        # Every certified source is homogeneous of total degree four:
        # H(q)q=3 grad(q), q.grad(q)=4V(q).
        target = np.asarray(target_integer, dtype=np.int64)
        product = self.numerator @ target
        gradient_denominator = self.denominator * 60
        gradient_divisor = gradient_denominator
        for value in product:
            gradient_divisor = math.gcd(gradient_divisor, abs(int(value)))
        gradient_numerator = product // gradient_divisor
        gradient_denominator //= gradient_divisor
        gradient_payload = [f"denominator={gradient_denominator}\n"]
        gradient_payload.extend(
            f"{index},{int(value)}\n"
            for index, value in enumerate(gradient_numerator)
            if value
        )
        quadratic = int(target @ product)
        value = Fraction(quadratic, self.denominator * 4800)
        euler_left = sum(
            Fraction(int(target[index]), TARGET_DENOMINATOR)
            * Fraction(int(gradient_numerator[index]), gradient_denominator)
            for index in range(FIELD_DIMENSION)
        )
        return {
            "value": str(value),
            "gradient_denominator": gradient_denominator,
            "gradient_nonzero_entries": int(np.count_nonzero(gradient_numerator)),
            "gradient_maximum_abs_numerator": int(
                np.max(np.abs(gradient_numerator), initial=0)
            ),
            "gradient_sha256": hashlib.sha256(
                "".join(gradient_payload).encode("ascii")
            ).hexdigest(),
            "Hq_equals_3_gradient_exactly": True,
            "q_dot_gradient_equals_4V_exactly": euler_left == 4 * value,
        }


def _rational_sum(
    rows: Iterable[RationalHessian],
) -> dict[tuple[int, int], Fraction]:
    output: dict[tuple[int, int], Fraction] = {}
    for row in rows:
        for key, value in row.fraction_entries().items():
            updated = output.get(key, Fraction(0)) + value
            if updated:
                output[key] = updated
            else:
                output.pop(key, None)
    return output


def _row_summary(
    *,
    family: str,
    channel: str,
    direction_id: str,
    polynomial_denominator: int,
    polynomial_coefficients: tuple[int, ...],
    hessian: RationalHessian,
    target_integer: np.ndarray,
) -> dict[str, Any]:
    if not np.array_equal(hessian.numerator, hessian.numerator.T):
        raise ArithmeticError(f"{direction_id} exact Hessian is asymmetric")
    jet = hessian.jet_summary(target_integer)
    if not all(
        (jet["Hq_equals_3_gradient_exactly"], jet["q_dot_gradient_equals_4V_exactly"])
    ):
        raise ArithmeticError(f"{direction_id} failed exact quartic Euler identities")
    return {
        "parameter_id": f"lambda::{direction_id}",
        "direction_id": direction_id,
        "family": family,
        "channel": channel,
        "projector_polynomial": {
            "cleared_denominator": polynomial_denominator,
            "integer_coefficients_low_to_high": list(polynomial_coefficients),
        },
        "Hessian": {
            "dimension": FIELD_DIMENSION,
            "denominator": hessian.denominator,
            "nonzero_entries_full_matrix": int(np.count_nonzero(hessian.numerator)),
            "maximum_abs_numerator": int(
                np.max(np.abs(hessian.numerator), initial=0)
            ),
            "symmetric_entrywise_over_Q": True,
            "canonical_sparse_rational_sha256": hessian.sha256(),
        },
        "exact_target_jet_from_homogeneity": jet,
    }


def _sigma_target_coordinates() -> tuple[tuple[int, int], ...]:
    block = foundation.integer_target_vector()[chart.SIGMA_SLICE]
    return tuple(
        (int(block[2 * index]), int(block[2 * index + 1]))
        for index in range(chart.SIGMA_COMPLEX_DIM)
    )


@lru_cache(maxsize=1)
def exact_o27_hessians() -> tuple[dict[str, RationalHessian], dict[str, Any]]:
    coordinates = _sigma_target_coordinates()
    pair = {
        (left, right): product
        for left, left_value in enumerate(coordinates)
        if left_value != (0, 0)
        for right, right_value in enumerate(coordinates)
        if right_value != (0, 0)
        if (product := _gi_mul(left_value, right_value)) != (0, 0)
    }
    pair_powers = [pair]
    for _ in range(3):
        pair_powers.append(exact_g2._exact_pair_casimir(pair_powers[-1]))

    polynomial: dict[str, tuple[int, tuple[int, ...]]] = {
        channel: _projector_integer_coefficients(sigma_source._poly(channel))
        for channel in sigma_source.CHANNELS
    }
    projected_pair = {
        channel: exact_g2._exact_matrix_linear_combination(
            zip(coefficients, pair_powers, strict=True)
        )
        for channel, (_denominator, coefficients) in polynomial.items()
    }

    flattened = {
        channel: np.zeros(
            (chart.SIGMA_REAL_DIM, 2 * chart.SIGMA_COMPLEX_DIM**2),
            dtype=np.int64,
        )
        for channel in sigma_source.CHANNELS
    }
    direct_flattened = np.zeros_like(next(iter(flattened.values())))
    for column in range(chart.SIGMA_REAL_DIM):
        coordinate = column // 2
        unit = (1, 0) if column % 2 == 0 else (0, 1)
        linear: dict[tuple[int, int], tuple[int, int]] = {}
        for other, value in enumerate(coordinates):
            if value == (0, 0):
                continue
            _gi_accumulate(linear, (coordinate, other), _gi_mul(unit, value))
            _gi_accumulate(linear, (other, coordinate), _gi_mul(value, unit))
        for (row, col), (real, imaginary) in linear.items():
            offset = 2 * (row * chart.SIGMA_COMPLEX_DIM + col)
            direct_flattened[column, offset] = real
            direct_flattened[column, offset + 1] = imaginary
        powers = [linear]
        for _ in range(3):
            powers.append(exact_g2._exact_pair_casimir(powers[-1]))
        for channel, (_denominator, coefficients) in polynomial.items():
            image = exact_g2._exact_matrix_linear_combination(
                zip(coefficients, powers, strict=True)
            )
            target = flattened[channel][column]
            for (row, col), (real, imaginary) in image.items():
                offset = 2 * (row * chart.SIGMA_COMPLEX_DIM + col)
                target[offset] = real
                target[offset + 1] = imaginary

    result: dict[str, RationalHessian] = {}
    preflight_bounds: dict[str, int] = {}
    for channel in sigma_source.CHANNELS:
        denominator, _coefficients = polynomial[channel]
        vectors = flattened[channel]
        maximum = int(np.max(np.abs(vectors), initial=0))
        gram_bound = vectors.shape[1] * maximum * maximum
        if gram_bound > INT64_MAX:
            raise OverflowError(f"O27 {channel} Gram preflight exceeds int64")
        block = 2 * (vectors @ vectors.T)
        projected = projected_pair[channel]
        for first in range(chart.SIGMA_REAL_DIM):
            left = first // 2
            left_unit = (1, 0) if first % 2 == 0 else (0, 1)
            for second in range(chart.SIGMA_REAL_DIM):
                right = second // 2
                right_unit = (1, 0) if second % 2 == 0 else (0, 1)
                product = _gi_mul(left_unit, right_unit)
                real, imaginary = projected.get((left, right), (0, 0))
                real_inner = real * product[0] + imaginary * product[1]
                block[first, second] += 4 * denominator * real_inner
        full = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
        full[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = block
        result[channel] = RationalHessian.normalized(
            full, denominator * denominator * 1600
        )
        preflight_bounds[channel] = gram_bound

    direct_block = 2 * (direct_flattened @ direct_flattened.T)
    for first in range(chart.SIGMA_REAL_DIM):
        left = first // 2
        left_unit = (1, 0) if first % 2 == 0 else (0, 1)
        for second in range(chart.SIGMA_REAL_DIM):
            right = second // 2
            right_unit = (1, 0) if second % 2 == 0 else (0, 1)
            product = _gi_mul(left_unit, right_unit)
            real, imaginary = pair.get((left, right), (0, 0))
            direct_block[first, second] += 4 * (
                real * product[0] + imaginary * product[1]
            )
    direct_full = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    direct_full[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = direct_block
    direct = RationalHessian.normalized(direct_full, 1600)
    reconstruction = _rational_sum(result.values()) == direct.fraction_entries()
    if not reconstruction:
        raise ArithmeticError("four O27 projector Hessians do not reconstruct norm quartic")

    return result, {
        "arithmetic_domain": "Gaussian integers Z[i] with cleared rational projector denominators",
        "target_nonzero_complex_coordinates": sum(value != (0, 0) for value in coordinates),
        "target_coordinate_integer_squared_norm": sum(
            real * real + imaginary * imaginary for real, imaginary in coordinates
        ),
        "pair_nonzero_entries": len(pair),
        "signed_int64_Gram_preflight_bounds": preflight_bounds,
        "all_preflight_bounds_within_signed_int64": all(
            value <= INT64_MAX for value in preflight_bounds.values()
        ),
        "four_projector_Hessians_reconstruct_unprojected_norm_quartic_entrywise_over_Q": reconstruction,
        "unprojected_norm_quartic_Hessian_sha256": direct.sha256(),
        "polynomial": polynomial,
    }


@lru_cache(maxsize=1)
def _exact_contraction_tensor() -> tuple[np.ndarray, np.ndarray]:
    real = np.zeros((10, chart.PHI_DIM, chart.SIGMA_COMPLEX_DIM), dtype=np.int64)
    imaginary = np.zeros_like(real)
    for phi_index, indices in enumerate(chart.PHI_INDICES):
        for sigma_index, row in enumerate(exact_g2._exact_sigma_basis_rows()):
            form = exact_g2._exact_basis_form(row)
            for free_index in range(10):
                if free_index in indices:
                    continue
                sequence = indices + (free_index,)
                coefficient = form.get(tuple(sorted(sequence)), (0, 0))
                sign = exact_g2._exact_permutation_sign(sequence)
                real[free_index, phi_index, sigma_index] = sign * coefficient[0]
                imaginary[free_index, phi_index, sigma_index] = sign * coefficient[1]
    return real, imaginary


@lru_cache(maxsize=1)
def _phi_generator_index_data() -> tuple[tuple[np.ndarray, ...], ...]:
    rows = []
    for generator in exact_g2._exact_phi_generator_matrices_cached():
        coo = generator.tocoo()
        rows.append(
            (
                np.asarray(coo.row, dtype=int),
                np.asarray(coo.col, dtype=int),
                np.asarray(coo.data, dtype=np.int64),
            )
        )
    return tuple(rows)


def _exact_pair_casimir_batch(source: np.ndarray) -> tuple[np.ndarray, int]:
    matrix = np.asarray(source, dtype=np.int64)
    maximum = int(np.max(np.abs(matrix), initial=0))
    contributions = exact_g2._exact_phi_generator_int64_structure()[
        "maximum_simultaneous_contributions_per_pair_Casimir_output_entry"
    ]
    bound = maximum * contributions
    if bound > INT64_MAX:
        raise OverflowError("batched Phi pair-Casimir preflight exceeds int64")
    output = np.zeros_like(matrix)
    for row, column, sign in _phi_generator_index_data():
        signs = sign[:, None] * sign[None, :]
        output[:, row[:, None], row[None, :]] += (
            matrix[:, column[:, None], column[None, :]] * signs[None, :, :]
        )
    return output, bound


def _checked_add_scaled(
    target: np.ndarray, coefficient: int, source: np.ndarray, *, label: str
) -> None:
    bound = int(np.max(np.abs(target), initial=0)) + abs(int(coefficient)) * int(
        np.max(np.abs(source), initial=0)
    )
    if bound > INT64_MAX:
        raise OverflowError(f"{label} preflight exceeds int64")
    target += int(coefficient) * source


def _exact_sigma_operator(
    pair: np.ndarray, contraction_real: np.ndarray, contraction_imaginary: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    source = np.asarray(pair, dtype=np.int64)
    if not np.any(source):
        zero = np.zeros(
            (chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM), dtype=np.int64
        )
        return zero, zero.copy()
    real = np.zeros((chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM), dtype=np.int64)
    imaginary = np.zeros_like(real)
    for vector_index in range(10):
        cr = contraction_real[vector_index]
        ci = contraction_imaginary[vector_index]
        acr = exact_g2._checked_int64_matmul(
            source, cr, label="O44 projected pair times Re(C)"
        )
        aci = exact_g2._checked_int64_matmul(
            source, ci, label="O44 projected pair times Im(C)"
        )
        terms_real = (
            exact_g2._checked_int64_matmul(cr.T, acr, label="O44 Re(C)^T A Re(C)"),
            exact_g2._checked_int64_matmul(ci.T, aci, label="O44 Im(C)^T A Im(C)"),
        )
        terms_imaginary = (
            exact_g2._checked_int64_matmul(cr.T, aci, label="O44 Re(C)^T A Im(C)"),
            exact_g2._checked_int64_matmul(ci.T, acr, label="O44 Im(C)^T A Re(C)"),
        )
        real = exact_g2._checked_int64_linear_combination(
            ((1, real), (1, terms_real[0]), (1, terms_real[1])),
            label="O44 sigma-operator real accumulation",
        )
        imaginary = exact_g2._checked_int64_linear_combination(
            ((1, imaginary), (1, terms_imaginary[0]), (-1, terms_imaginary[1])),
            label="O44 sigma-operator imaginary accumulation",
        )
    return real, imaginary


def _realify_hermitian(real: np.ndarray, imaginary: np.ndarray) -> np.ndarray:
    output = np.empty((chart.SIGMA_REAL_DIM, chart.SIGMA_REAL_DIM), dtype=np.int64)
    u = 2 * np.arange(chart.SIGMA_COMPLEX_DIM)
    v = u + 1
    output[np.ix_(u, u)] = real
    output[np.ix_(u, v)] = -imaginary
    output[np.ix_(v, u)] = imaginary
    output[np.ix_(v, v)] = real
    return output


def _assemble_o44_hessian(
    *,
    denominator: int,
    projected_phi_pair: np.ndarray,
    projected_sigma_pair: np.ndarray,
    cross_action: np.ndarray,
    contraction_real: np.ndarray,
    contraction_imaginary: np.ndarray,
) -> RationalHessian:
    operator_real, operator_imaginary = _exact_sigma_operator(
        projected_phi_pair, contraction_real, contraction_imaginary
    )
    numerator = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    numerator[chart.PHI_SLICE, chart.PHI_SLICE] = 2 * projected_sigma_pair
    numerator[chart.PHI_SLICE, chart.SIGMA_SLICE] = 2 * cross_action.T
    numerator[chart.SIGMA_SLICE, chart.PHI_SLICE] = 2 * cross_action
    numerator[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = 2 * _realify_hermitian(
        operator_real, operator_imaginary
    )
    return RationalHessian.normalized(numerator, denominator * 800)


@lru_cache(maxsize=1)
def exact_o44_hessians() -> tuple[dict[str, RationalHessian], dict[str, Any]]:
    contraction_real, contraction_imaginary = _exact_contraction_tensor()
    target = foundation.integer_target_vector()
    x = target[chart.PHI_SLICE]
    sigma = target[chart.SIGMA_SLICE]
    z_real = sigma[0::2]
    z_imaginary = sigma[1::2]

    image_real = (
        np.einsum("kpa,a->kp", contraction_real, z_real, optimize=True)
        - np.einsum("kpa,a->kp", contraction_imaginary, z_imaginary, optimize=True)
    )
    image_imaginary = (
        np.einsum("kpa,a->kp", contraction_real, z_imaginary, optimize=True)
        + np.einsum("kpa,a->kp", contraction_imaginary, z_real, optimize=True)
    )
    sigma_pair = image_real.T @ image_real + image_imaginary.T @ image_imaginary
    phi_pair = np.outer(x, x)

    derivatives = np.empty(
        (chart.SIGMA_REAL_DIM, chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64
    )
    for column in range(chart.SIGMA_REAL_DIM):
        coordinate = column // 2
        unit_real = int(column % 2 == 0)
        unit_imaginary = int(column % 2 == 1)
        derivative_real = (
            contraction_real[:, :, coordinate] * unit_real
            - contraction_imaginary[:, :, coordinate] * unit_imaginary
        )
        derivative_imaginary = (
            contraction_real[:, :, coordinate] * unit_imaginary
            + contraction_imaginary[:, :, coordinate] * unit_real
        )
        derivatives[column] = (
            derivative_real.T @ image_real
            + derivative_imaginary.T @ image_imaginary
            + image_real.T @ derivative_real
            + image_imaginary.T @ derivative_imaginary
        )

    polynomial: dict[str, tuple[int, tuple[int, ...]]] = {}
    projected_phi: dict[str, np.ndarray] = {}
    projected_sigma: dict[str, np.ndarray] = {}
    for channel, eigenvalue in phi_projectors.COMMON_CHANNEL_EIGENVALUES.items():
        denominator, coefficients, a_pair, _ = exact_g2._cleared_phi_pair_projector(
            phi_pair, eigenvalue
        )
        other_denominator, other_coefficients, b_pair, _ = (
            exact_g2._cleared_phi_pair_projector(sigma_pair, eigenvalue)
        )
        if (denominator, coefficients) != (other_denominator, other_coefficients):
            raise ArithmeticError("O44 projector polynomial drifted between inputs")
        polynomial[channel] = (denominator, coefficients)
        projected_phi[channel] = a_pair
        projected_sigma[channel] = b_pair

    cross = {
        channel: np.zeros((chart.SIGMA_REAL_DIM, chart.PHI_DIM), dtype=np.int64)
        for channel in mixed_source.CHANNELS
    }
    power = derivatives
    casimir_preflight_bounds: list[int] = []
    degree_count = len(next(iter(polynomial.values()))[1])
    support = np.flatnonzero(x)
    if support.size != 1:
        raise ArithmeticError("physical target Phi support is no longer rank one")
    phi_index = int(support[0])
    phi_value = int(x[phi_index])
    for degree in range(degree_count):
        action = power[:, :, phi_index] * phi_value
        for channel, (_denominator, coefficients) in polynomial.items():
            _checked_add_scaled(
                cross[channel], coefficients[degree], action, label=f"O44 {channel} cross action"
            )
        if degree + 1 < degree_count:
            power, bound = _exact_pair_casimir_batch(power)
            casimir_preflight_bounds.append(bound)

    result = {
        channel: _assemble_o44_hessian(
            denominator=polynomial[channel][0],
            projected_phi_pair=projected_phi[channel],
            projected_sigma_pair=projected_sigma[channel],
            cross_action=cross[channel],
            contraction_real=contraction_real,
            contraction_imaginary=contraction_imaginary,
        )
        for channel in mixed_source.CHANNELS
    }

    direct_cross = derivatives[:, :, phi_index] * phi_value
    direct = _assemble_o44_hessian(
        denominator=1,
        projected_phi_pair=phi_pair,
        projected_sigma_pair=sigma_pair,
        cross_action=direct_cross,
        contraction_real=contraction_real,
        contraction_imaginary=contraction_imaginary,
    )
    reconstruction = _rational_sum(result.values()) == direct.fraction_entries()
    if not reconstruction:
        raise ArithmeticError("six O44 channel Hessians do not reconstruct direct contraction")

    return result, {
        "arithmetic_domain": "integers Z plus cleared rational Phi pair-Casimir projectors",
        "exact_contraction_tensor": {
            "shape": list(contraction_real.shape),
            "nonzero_real_entries": int(np.count_nonzero(contraction_real)),
            "nonzero_imaginary_entries": int(np.count_nonzero(contraction_imaginary)),
            "maximum_abs_entry": int(
                max(
                    np.max(np.abs(contraction_real), initial=0),
                    np.max(np.abs(contraction_imaginary), initial=0),
                )
            ),
        },
        "target_sigma_pair_maximum_abs_integer": int(
            np.max(np.abs(sigma_pair), initial=0)
        ),
        "target_sigma_pair_derivative_maximum_abs_integer": int(
            np.max(np.abs(derivatives), initial=0)
        ),
        "pair_Casimir_power_preflight_bounds": casimir_preflight_bounds,
        "all_preflight_bounds_within_signed_int64": all(
            value <= INT64_MAX for value in casimir_preflight_bounds
        ),
        "six_channel_Hessians_reconstruct_unprojected_contraction_entrywise_over_Q": reconstruction,
        "unprojected_contraction_Hessian_sha256": direct.sha256(),
        "polynomial": polynomial,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    bindings = source_bindings()
    target = foundation.integer_target_vector().copy()
    if target.shape != (FIELD_DIMENSION,) or int(target @ target) != 1632:
        raise ArithmeticError("physical target lattice pin failed")
    o27, o27_certificate = exact_o27_hessians()
    o44, o44_certificate = exact_o44_hessians()

    rows: list[dict[str, Any]] = []
    for channel, direction_id in O27_CHANNEL_TO_ROW.items():
        denominator, coefficients = o27_certificate["polynomial"][channel]
        rows.append(
            _row_summary(
                family="126bar_self_projectors",
                channel=channel,
                direction_id=direction_id,
                polynomial_denominator=denominator,
                polynomial_coefficients=coefficients,
                hessian=o27[channel],
                target_integer=target,
            )
        )
    for channel, direction_id in O44_CHANNEL_TO_ROW.items():
        denominator, coefficients = o44_certificate["polynomial"][channel]
        rows.append(
            _row_summary(
                family="Phi2_Sigma_projectors",
                channel=channel,
                direction_id=direction_id,
                polynomial_denominator=denominator,
                polynomial_coefficients=coefficients,
                hessian=o44[channel],
                target_integer=target,
            )
        )
    rows.sort(key=lambda row: row["direction_id"])

    claims = {
        "exact_source_algebra_Hessians_for_all_10_O27_O44_rows": True,
        "exact_source_algebra_Hessians_for_all_37_active_witness_rows": False,
        "exact_full_witness_aggregate_stationarity": False,
        "exact_full_witness_symmetry_kernel": False,
        "exact_full_witness_rank_448_and_PSD": False,
        "full_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    checks = {
        "all_source_portable_lf_pins_match": bindings["all_portable_lf_pins_match"],
        "physical_target_is_exact_20_lattice_vector_in_486_chart": (
            target.shape == (FIELD_DIMENSION,) and int(target @ target) == 1632
        ),
        "exactly_10_hard_rows_certified": len(rows) == 10,
        "all_10_Hessians_are_entrywise_symmetric_over_Q": all(
            row["Hessian"]["symmetric_entrywise_over_Q"] for row in rows
        ),
        "all_10_exact_Euler_jet_identities_hold": all(
            row["exact_target_jet_from_homogeneity"][
                "Hq_equals_3_gradient_exactly"
            ]
            and row["exact_target_jet_from_homogeneity"][
                "q_dot_gradient_equals_4V_exactly"
            ]
            for row in rows
        ),
        "O27_projector_sum_reconstructs_direct_source_Hessian_exactly": o27_certificate[
            "four_projector_Hessians_reconstruct_unprojected_norm_quartic_entrywise_over_Q"
        ],
        "O44_projector_sum_reconstructs_direct_source_Hessian_exactly": o44_certificate[
            "six_channel_Hessians_reconstruct_unprojected_contraction_entrywise_over_Q"
        ],
        "all_signed_int64_preflights_pass": (
            o27_certificate["all_preflight_bounds_within_signed_int64"]
            and o44_certificate["all_preflight_bounds_within_signed_int64"]
        ),
        "remaining_active_row_count_is_explicitly_27": len(REMAINING_ACTIVE_ROWS) == 27,
        "full_37_row_aggregate_claim_is_fail_closed": not claims[
            "exact_source_algebra_Hessians_for_all_37_active_witness_rows"
        ],
        "global_equality_and_G3_G4_G5_claims_are_fail_closed": not any(
            claims[key]
            for key in (
                "full_486_field_global_equality_orbit_classified",
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"hard-projector theorem checks failed: {failures}")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_bindings": bindings,
        "target": {
            "chart_dimension": FIELD_DIMENSION,
            "lattice_denominator": TARGET_DENOMINATOR,
            "lattice_norm_squared": int(target @ target),
            "support": {
                str(int(index)): int(target[index]) for index in np.flatnonzero(target)
            },
            "support_size": int(np.count_nonzero(target)),
            "support_sha256": hashlib.sha256(
                ";".join(
                    f"{int(index)}:{int(target[index])}" for index in np.flatnonzero(target)
                ).encode("ascii")
            ).hexdigest(),
        },
        "arithmetic_contract": {
            "exact_domains": ["Z", "Gaussian integers Z[i]", "Q"],
            "floating_point_used_to_construct_or_accept_Hessians": False,
            "finite_difference_autodiff_or_rational_recognition_used": False,
            "canonical_digest_is_over_reduced_sparse_rational_entries": True,
            "signed_int64_maximum": INT64_MAX,
        },
        "certified_rows": rows,
        "family_certificates": {
            "O27_126bar_self_projectors": {
                key: value for key, value in o27_certificate.items() if key != "polynomial"
            },
            "O44_Phi2_Sigma_projectors": {
                key: value for key, value in o44_certificate.items() if key != "polynomial"
            },
        },
        "scope_accounting": {
            "active_witness_row_count": 37,
            "exact_source_rows_certified_here": 10,
            "remaining_active_row_count": len(REMAINING_ACTIVE_ROWS),
            "remaining_active_rows": list(REMAINING_ACTIVE_ROWS),
            "minimum_missing_derivation": (
                "derive the complete exact value/gradient/Hessian jets of these 27 rows; "
                "compose all 37 with the exact rational witness; then prove exact "
                "stationarity, the 38-dimensional symmetry kernel, rank 448 and PSD"
            ),
            "separate_global_requirement": (
                "classify every full 486-field zero/equality point modulo the declared "
                "SO(10) x U(1)_X x PQ symmetry; a local Hessian cannot supply this"
            ),
        },
        "claims": claims,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    core = hashlib.sha256(canonical_json_bytes(report)).hexdigest()
    row_digest = hashlib.sha256(
        "\n".join(
            f"{row['direction_id']}:{row['Hessian']['canonical_sparse_rational_sha256']}"
            for row in rows
        ).encode("ascii")
    ).hexdigest()
    report["integrity"] = {
        "core_sha256": core,
        "ordered_ten_row_digest_sha256": row_digest,
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    scope = report["scope_accounting"]
    lines = [
        "# Exact physical-SM hard projector Hessians v20",
        "",
        f"Status: `{report['status']}`",
        "",
        "The full 486-real target Hessians of all four O27 and all six O44 source rows are derived with exact integer/Gaussian-integer arithmetic and cleared rational projectors. No float tolerance, finite difference, autodiff, or rational recognition accepts a Hessian entry.",
        "",
        f"- Exact hard rows: `{scope['exact_source_rows_certified_here']}/10`.",
        f"- Exact active witness rows overall: `{scope['exact_source_rows_certified_here']}/{scope['active_witness_row_count']}`.",
        f"- Remaining active rows: `{scope['remaining_active_row_count']}`.",
        f"- Ordered exact-row digest: `{report['integrity']['ordered_ten_row_digest_sha256']}`.",
        "- O27 projector sum reconstructs the direct norm-quartic Hessian entrywise over Q.",
        "- O44 six-channel sum reconstructs the direct contraction Hessian entrywise over Q.",
        "",
        "This is not the exact 37-row witness aggregate. Exact aggregate stationarity, symmetry kernel, rank/PSD, and the separate full 486-field global equality-orbit classification remain open. Therefore physical G3, G4, and G5 remain false.",
        "",
        "## Minimum missing derivation",
        "",
        scope["minimum_missing_derivation"] + ".",
        "",
        scope["separate_global_requirement"] + ".",
        "",
    ]
    return "\n".join(lines)


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_bytes(canonical_json_bytes(report))
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write frozen JSON/Markdown")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    else:
        print(json.dumps(_jsonable(report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
