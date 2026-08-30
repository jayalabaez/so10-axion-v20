#!/usr/bin/env python3
"""Exact source Hessians for the last six active physical-SM witness rows.

This module derives O14, both O35 channels, and all three O46 channels in
integer/Gaussian-integer/rational arithmetic at the exact lattice target
``20 q_*``.  Combined with the hard-10 and easy-21 theorems, all 37 active
source Hessians are then available.  Aggregate stationarity/kernel/rank/PSD
and the separate global equality-orbit classification are not claimed here.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_physical_sm_easy_21_hessians_v20 as easy
import exact_physical_sm_hard_projector_hessians_v20 as hard
import gauged_u1x_g2_derivative_audit_v20 as exact_g2
import live_g2_canonical_486_field_chart_v20 as chart
import physical_sm_vacuum_local_feasibility_v20 as foundation


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.json"
OUT_MD = ROOT / "EXACT_PHYSICAL_SM_LAST_SIX_HESSIANS_V20.md"
SCHEMA = "exact_physical_sm_last_six_hessians_v20"
STATUS = "EXACT_LAST_SIX_SOURCE_HESSIANS__ALL_37_ROWS_AVAILABLE__AGGREGATE_AND_GLOBAL_EQUALITY_OPEN"
FIELD_DIMENSION = 486
TARGET_DENOMINATOR = 20
INT64_MAX = int(np.iinfo(np.int64).max)

SOURCE_HASHES = {
    "exact_physical_sm_hard_projector_hessians_v20.py": "2ac49af04f3bbec17a4e616c82898de6a0710ddcfa3462d7ec8d59dad69de27e",
    "exact_physical_sm_easy_21_hessians_v20.py": "e8b6fcf9bc459ee4c05a74d41cae6d9a82680de88683ba5ffcc4ceb30fe73311",
    "physical_sm_vacuum_local_feasibility_v20.py": "629ea8c45f101f82b6b4e963fd1fb19dcc5735fe52a1d8efb1fb0812dbaa565c",
    "gauged_u1x_g2_derivative_audit_v20.py": "584e03994ca1187228377c3e4c145d95446ade50616e2d58068e0fee9f96507d",
    "live_g2_canonical_486_field_chart_v20.py": "9275dbb204324cc48dfd7139cad836e034b1b83b07bd60aecd6ff093d3ab7765",
    "live_g2_exact_remaining_cubic_derivatives_v20.py": "83502cf47b5f859328c723de0edbd8018825e94e09a1001461dee22751244276",
    "live_g2_exact_hsigma_hermitian_derivatives_v20.py": "813ea0828fa7ff903c9ef77686a2b8d0ef16d22a40cac03cd5a6336762486291",
    "live_g2_exact_phi2_hdagh_derivatives_v20.py": "eed5996a1458370b1a6d30b268c0bd3ba155d25d1da5f08d50eeadb6cee6734e",
    "exact_mixed_45_triplet_channel_v20.py": "3ac36a491014d59bb4d08a0939e63cd7d5bde8aa9c7cde0bfc4b491521c1073c",
    "exact_phi2_hdagh_channel_family_v20.py": "42f347e5d8cb8d378f737425d7b152cc71e678627b8a2128b8faba0ce41261cf",
}

ROWS = {
    "O14_B01_Phi_Sigma_Sigmadag_cubic": ("Phi_Sigma_Sigmadag_cubic", "unique", 3),
    "O35_B01_H_Sigma_hermitian": ("H_Sigma_hermitian", "1", 4),
    "O35_B02_H_Sigma_hermitian": ("H_Sigma_hermitian", "45", 4),
    "O46_B01_Phi2_HdagH_channels": ("Phi2_HdagH_channels", "1", 4),
    "O46_B02_Phi2_HdagH_channels": ("Phi2_HdagH_channels", "45", 4),
    "O46_B03_Phi2_HdagH_channels": ("Phi2_HdagH_channels", "54", 4),
}


def _portable_lf_sha256(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def source_bindings() -> dict[str, Any]:
    rows = {}
    for name, expected in SOURCE_HASHES.items():
        observed = _portable_lf_sha256(ROOT / name)
        if observed != expected:
            raise ArithmeticError(f"last-six dependency drifted: {name}")
        rows[name] = {"portable_lf_sha256": observed, "matches": True}
    return {"files": rows, "all_portable_lf_pins_match": True}


def _gi_mul(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _gi_add(*values: tuple[int, int]) -> tuple[int, int]:
    return (sum(value[0] for value in values), sum(value[1] for value in values))


def _gi_scale(value: tuple[int, int], scale: int) -> tuple[int, int]:
    return (scale * value[0], scale * value[1])


def _exact_interior(
    form: dict[tuple[int, ...], tuple[int, int]], index: int
) -> dict[tuple[int, ...], tuple[int, int]]:
    output = {}
    for indices, coefficient in form.items():
        if index not in indices:
            continue
        position = indices.index(index)
        output[indices[:position] + indices[position + 1 :]] = _gi_scale(
            coefficient, -1 if position % 2 else 1
        )
    return output


@lru_cache(maxsize=1)
def _double_interior_tables() -> tuple[np.ndarray, np.ndarray]:
    triples = tuple(itertools.combinations(range(10), 3))
    lookup = {indices: index for index, indices in enumerate(triples)}
    real = np.zeros((10, 10, chart.SIGMA_COMPLEX_DIM, len(triples)), dtype=np.int64)
    imaginary = np.zeros_like(real)
    for first in range(10):
        for second in range(10):
            if first == second:
                continue
            for sigma_index, row in enumerate(exact_g2._exact_sigma_basis_rows()):
                form = exact_g2._exact_basis_form(row)
                image = _exact_interior(_exact_interior(form, first), second)
                for indices, value in image.items():
                    real[first, second, sigma_index, lookup[indices]] = value[0]
                    imaginary[first, second, sigma_index, lookup[indices]] = value[1]
    return real, imaginary


def _conj_left_matvec(
    ar: np.ndarray, ai: np.ndarray, br: np.ndarray, bi: np.ndarray, zr: np.ndarray, zi: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    # conj(A) @ (B.T @ z)
    vr = br.T @ zr - bi.T @ zi
    vi = br.T @ zi + bi.T @ zr
    real = ar @ vr + ai @ vi
    imaginary = ar @ vi - ai @ vr
    return real, imaginary


def _conj_left_matmul(
    ar: np.ndarray, ai: np.ndarray, br: np.ndarray, bi: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    return ar @ br.T + ai @ bi.T, ar @ bi.T - ai @ br.T


def _phi_sigma_operator_action(
    indices: tuple[int, int, int, int], zr: np.ndarray, zi: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    real, imaginary = _double_interior_tables()
    a, b, c, d = indices
    terms = (
        (1, (a, b), (c, d)),
        (-1, (a, c), (b, d)),
        (1, (a, d), (b, c)),
    )
    output_real = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=np.int64)
    output_imaginary = np.zeros_like(output_real)
    for sign, left, right in terms:
        tr, ti = _conj_left_matvec(
            real[left], imaginary[left], real[right], imaginary[right], zr, zi
        )
        output_real += 2 * sign * tr
        output_imaginary += 2 * sign * ti
    return output_real, output_imaginary


def _phi_sigma_operator_matrix(
    indices: tuple[int, int, int, int]
) -> tuple[np.ndarray, np.ndarray]:
    real, imaginary = _double_interior_tables()
    a, b, c, d = indices
    terms = (
        (1, (a, b), (c, d)),
        (-1, (a, c), (b, d)),
        (1, (a, d), (b, c)),
    )
    output_real = np.zeros((chart.SIGMA_COMPLEX_DIM,) * 2, dtype=np.int64)
    output_imaginary = np.zeros_like(output_real)
    for sign, left, right in terms:
        tr, ti = _conj_left_matmul(
            real[left], imaginary[left], real[right], imaginary[right]
        )
        output_real += 2 * sign * tr
        output_imaginary += 2 * sign * ti
    return output_real, output_imaginary


def _realify_hermitian(real: np.ndarray, imaginary: np.ndarray) -> np.ndarray:
    dimension = real.shape[0]
    output = np.empty((2 * dimension, 2 * dimension), dtype=np.int64)
    u = 2 * np.arange(dimension)
    v = u + 1
    output[np.ix_(u, u)] = real
    output[np.ix_(u, v)] = -imaginary
    output[np.ix_(v, u)] = imaginary
    output[np.ix_(v, v)] = real
    return output


def exact_o14(target: np.ndarray) -> tuple[hard.RationalHessian, dict[str, Any]]:
    sigma = target[chart.SIGMA_SLICE]
    zr = sigma[0::2]
    zi = sigma[1::2]
    phi = target[chart.PHI_SLICE]
    numerator = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    cross = np.empty((chart.PHI_DIM, chart.SIGMA_REAL_DIM), dtype=np.int64)
    for index, indices in enumerate(chart.PHI_INDICES):
        action_real, action_imaginary = _phi_sigma_operator_action(indices, zr, zi)
        cross[index, 0::2] = action_real
        cross[index, 1::2] = action_imaginary
    numerator[chart.PHI_SLICE, chart.SIGMA_SLICE] = cross
    numerator[chart.SIGMA_SLICE, chart.PHI_SLICE] = cross.T
    support = np.flatnonzero(phi)
    if support.size != 1:
        raise ArithmeticError("O14 target Phi support drifted")
    operator_real, operator_imaginary = _phi_sigma_operator_matrix(
        chart.PHI_INDICES[int(support[0])]
    )
    operator_real *= int(phi[int(support[0])])
    operator_imaginary *= int(phi[int(support[0])])
    numerator[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = _realify_hermitian(
        operator_real, operator_imaginary
    )
    matrix = hard.RationalHessian.normalized(numerator, 20)
    return matrix, {
        "double_interior_table_shape": list(_double_interior_tables()[0].shape),
        "operator_Hermitian_exactly": np.array_equal(operator_real, operator_real.T)
        and np.array_equal(operator_imaginary, -operator_imaginary.T),
        "integer_cross_maximum_abs": int(np.max(np.abs(cross), initial=0)),
    }


def _generator_realification(real: np.ndarray, imaginary: np.ndarray) -> np.ndarray:
    # If G is anti-Hermitian, the existing quadratic-current Hessian is i R.
    dimension = real.shape[0]
    output = np.zeros((2 * dimension, 2 * dimension), dtype=np.int64)
    u = 2 * np.arange(dimension)
    v = u + 1
    output[np.ix_(u, u)] = imaginary
    output[np.ix_(v, v)] = imaginary
    output[np.ix_(u, v)] = real
    output[np.ix_(v, u)] = real.T
    if not np.array_equal(output, output.T):
        raise ArithmeticError("current realification is not symmetric")
    return output


@lru_cache(maxsize=1)
def _current_real_hessians() -> tuple[tuple[np.ndarray, np.ndarray], ...]:
    output = []
    sigma_columns = exact_g2._exact_sigma_generator_columns()
    for generator_index, (first, second) in enumerate(itertools.combinations(range(10), 2)):
        h_real = np.zeros((10, 10), dtype=np.int64)
        h_real[first, second] = 1
        h_real[second, first] = -1
        h_imaginary = np.zeros_like(h_real)
        sigma_real = np.zeros((chart.SIGMA_COMPLEX_DIM,) * 2, dtype=np.int64)
        sigma_imaginary = np.zeros_like(sigma_real)
        for column, entries in enumerate(sigma_columns[generator_index]):
            for row, (real, imaginary) in entries:
                sigma_real[row, column] = real
                sigma_imaginary[row, column] = imaginary
        output.append(
            (
                _generator_realification(h_real, h_imaginary),
                _generator_realification(sigma_real, sigma_imaginary),
            )
        )
    return tuple(output)


def _quadratic_matrix_jet(
    matrix: np.ndarray, indices: np.ndarray, target: np.ndarray
) -> easy.SparseJet:
    block = target[indices]
    image = matrix @ block
    value = Fraction(int(block @ image), 800)
    gradient = {
        int(indices[local]): Fraction(int(value), 20)
        for local, value in enumerate(image)
        if value
    }
    hessian = {
        (int(indices[row]), int(indices[column])): Fraction(int(matrix[row, column]))
        for row, column in zip(*np.nonzero(matrix), strict=True)
    }
    return easy.SparseJet(value, gradient, hessian)


def _sum_jets(jets: list[easy.SparseJet]) -> easy.SparseJet:
    value = sum((jet.value for jet in jets), Fraction(0))
    gradient: dict[int, Fraction] = {}
    hessian: dict[tuple[int, int], Fraction] = {}
    for jet in jets:
        for key, item in jet.gradient.items():
            easy._add_fraction(gradient, key, item)
        for key, item in jet.hessian.items():
            easy._add_fraction(hessian, key, item)
    return easy.SparseJet(value, gradient, hessian)


def exact_o35(target: np.ndarray) -> tuple[dict[str, hard.RationalHessian], dict[str, Any]]:
    factors = easy._factor_jets(target)
    channel_1 = easy._rational_hessian_from_entries(
        easy._multiply(factors["H"], factors["Sigma"]).hessian
    )
    h_indices = np.arange(chart.H_SLICE.start, chart.H_SLICE.stop)
    sigma_indices = np.arange(chart.SIGMA_SLICE.start, chart.SIGMA_SLICE.stop)
    products = []
    for h_matrix, sigma_matrix in _current_real_hessians():
        products.append(
            easy._multiply(
                _quadratic_matrix_jet(h_matrix, h_indices, target),
                _quadratic_matrix_jet(sigma_matrix, sigma_indices, target),
            )
        )
    channel_45_jet = _sum_jets(products)
    channel_45 = easy._rational_hessian_from_entries(channel_45_jet.hessian)
    return {
        "O35_B01_H_Sigma_hermitian": channel_1,
        "O35_B02_H_Sigma_hermitian": channel_45,
    }, {
        "exact_SO10_generator_count": len(products),
        "current_domain": "Gaussian-integer anti-Hermitian generators realified to integer symmetric quadratic-current Hessians",
        "channel_45_target_value_direct": str(channel_45_jet.value),
    }


@lru_cache(maxsize=1)
def _phi_interior_table() -> np.ndarray:
    triples = tuple(itertools.combinations(range(10), 3))
    lookup = {indices: index for index, indices in enumerate(triples)}
    output = np.zeros((10, chart.PHI_DIM, len(triples)), dtype=np.int64)
    for phi_index, indices in enumerate(chart.PHI_INDICES):
        for vector_index in indices:
            position = indices.index(vector_index)
            reduced = indices[:position] + indices[position + 1 :]
            output[vector_index, phi_index, lookup[reduced]] = -1 if position % 2 else 1
    return output


def _h_realification(real: np.ndarray, imaginary: np.ndarray | None = None) -> np.ndarray:
    imag = np.zeros_like(real) if imaginary is None else imaginary
    dimension = real.shape[0]
    output = np.zeros((2 * dimension, 2 * dimension), dtype=np.int64)
    x = 2 * np.arange(dimension)
    y = x + 1
    output[np.ix_(x, x)] = real
    output[np.ix_(x, y)] = -imag
    output[np.ix_(y, x)] = imag
    output[np.ix_(y, y)] = real
    return output


@lru_cache(maxsize=1)
def _phi_45_pair_matrices() -> dict[tuple[int, int], np.ndarray]:
    output = {}
    sets = tuple(set(indices) for indices in chart.PHI_INDICES)
    all_indices = set(range(10))
    for left in range(chart.PHI_DIM):
        for right in range(left + 1, chart.PHI_DIM):
            if sets[left].intersection(sets[right]):
                continue
            sequence = chart.PHI_INDICES[left] + chart.PHI_INDICES[right]
            union = tuple(sorted(sequence))
            complement = tuple(sorted(all_indices.difference(union)))
            coefficient = exact_g2._exact_permutation_sign(sequence)
            coefficient *= exact_g2._exact_permutation_sign(union + complement)
            first, second = complement
            matrix = np.zeros((10, 10), dtype=np.int64)
            matrix[first, second] = coefficient
            matrix[second, first] = -coefficient
            output[(left, right)] = matrix
    return output


def _exact_o46_45(target: np.ndarray) -> hard.RationalHessian:
    phi = target[chart.PHI_SLICE]
    h = target[chart.H_SLICE]
    numerator = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    phi_block = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64)
    cross = np.zeros((chart.PHI_DIM, chart.H_REAL_DIM), dtype=np.int64)
    for (left, right), antisymmetric in _phi_45_pair_matrices().items():
        realification = _h_realification(
            np.zeros_like(antisymmetric), antisymmetric
        )
        scalar = int(h @ realification @ h)
        phi_block[left, right] = scalar
        phi_block[right, left] = scalar
        if phi[left]:
            cross[right] += 2 * int(phi[left]) * (realification @ h)
        if phi[right]:
            cross[left] += 2 * int(phi[right]) * (realification @ h)
    numerator[chart.PHI_SLICE, chart.PHI_SLICE] = phi_block
    numerator[chart.PHI_SLICE, chart.H_SLICE] = cross
    numerator[chart.H_SLICE, chart.PHI_SLICE] = cross.T
    return hard.RationalHessian.normalized(numerator, 400)


def _exact_o46_54(target: np.ndarray) -> hard.RationalHessian:
    phi = target[chart.PHI_SLICE]
    h = target[chart.H_SLICE]
    table = _phi_interior_table()
    interiors = np.einsum("p,ipk->ik", phi, table, optimize=True)
    phi_norm_integer = int(phi @ phi)
    h_norm_integer = int(h @ h)
    m5 = 5 * (interiors @ interiors.T) - 2 * phi_norm_integer * np.eye(10, dtype=np.int64)
    numerator = np.zeros((FIELD_DIMENSION, FIELD_DIMENSION), dtype=np.int64)
    numerator[chart.H_SLICE, chart.H_SLICE] = _h_realification(m5)

    cross = np.empty((chart.PHI_DIM, chart.H_REAL_DIM), dtype=np.int64)
    for index in range(chart.PHI_DIM):
        derivative = (
            table[:, index, :] @ interiors.T
            + interiors @ table[:, index, :].T
        )
        first5 = 5 * derivative - 4 * int(phi[index]) * np.eye(10, dtype=np.int64)
        cross[index] = _h_realification(first5) @ h
    numerator[chart.PHI_SLICE, chart.H_SLICE] = cross
    numerator[chart.H_SLICE, chart.PHI_SLICE] = cross.T

    w_real = h[0::2]
    w_imaginary = h[1::2]
    contracted_real = np.einsum("i,ipk->pk", w_real, table, optimize=True)
    contracted_imaginary = np.einsum("i,ipk->pk", w_imaginary, table, optimize=True)
    gram = contracted_real @ contracted_real.T + contracted_imaginary @ contracted_imaginary.T
    phi_block = 5 * gram - 2 * h_norm_integer * np.eye(chart.PHI_DIM, dtype=np.int64)
    numerator[chart.PHI_SLICE, chart.PHI_SLICE] = phi_block
    return hard.RationalHessian.normalized(numerator, 2000)


def exact_o46(target: np.ndarray) -> tuple[dict[str, hard.RationalHessian], dict[str, Any]]:
    factors = easy._factor_jets(target)
    channel_1 = easy._rational_hessian_from_entries(
        easy._multiply(factors["Phi"], factors["H"]).hessian
    )
    channel_45 = _exact_o46_45(target)
    channel_54 = _exact_o46_54(target)
    return {
        "O46_B01_Phi2_HdagH_channels": channel_1,
        "O46_B02_Phi2_HdagH_channels": channel_45,
        "O46_B03_Phi2_HdagH_channels": channel_54,
    }, {
        "exact_Phi_interior_table_shape": list(_phi_interior_table().shape),
        "exact_nonzero_45_pair_matrices": len(_phi_45_pair_matrices()),
        "channel_domains": {
            "1": "rational norm product",
            "45": "integer Hodge-dual wedge and imaginary antisymmetric vector operator",
            "54": "integer interior Gram with trace subtraction denominator 5",
        },
    }


def exact_rows() -> tuple[dict[str, hard.RationalHessian], dict[str, Any]]:
    target = foundation.integer_target_vector()
    o14, c14 = exact_o14(target)
    o35, c35 = exact_o35(target)
    o46, c46 = exact_o46(target)
    rows = {"O14_B01_Phi_Sigma_Sigmadag_cubic": o14, **o35, **o46}
    return rows, {"O14": c14, "O35": c35, "O46": c46}


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    bindings = source_bindings()
    target = foundation.integer_target_vector()
    matrices, family_certificates = exact_rows()
    rows = []
    for direction_id, (family, label, degree) in ROWS.items():
        matrix = matrices[direction_id]
        jet = easy._homogeneous_jet_summary(matrix, target, degree)
        if not jet["q_dot_gradient_equals_degree_times_value_exactly"]:
            raise ArithmeticError(f"{direction_id} Euler identity failed")
        rows.append(
            {
                "parameter_id": f"lambda::{direction_id}",
                "direction_id": direction_id,
                "family": family,
                "basis_label": label,
                "Hessian": {
                    "dimension": FIELD_DIMENSION,
                    "denominator": matrix.denominator,
                    "nonzero_entries_full_matrix": int(np.count_nonzero(matrix.numerator)),
                    "maximum_abs_numerator": int(np.max(np.abs(matrix.numerator), initial=0)),
                    "symmetric_entrywise_over_Q": np.array_equal(matrix.numerator, matrix.numerator.T),
                    "canonical_sparse_rational_sha256": matrix.sha256(),
                },
                "exact_target_jet_from_homogeneity": jet,
            }
        )
    rows.sort(key=lambda row: row["direction_id"])
    claims = {
        "exact_last_six_source_Hessians": True,
        "all_37_active_source_Hessians_available_across_three_theorems": True,
        "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here": False,
        "full_486_field_global_equality_orbit_classified": False,
        "physical_SM_G3_closed": False,
        "physical_SM_G4_closed": False,
        "physical_SM_G5_closed": False,
    }
    checks = {
        "source_pins_match": bindings["all_portable_lf_pins_match"],
        "exactly_six_rows": len(rows) == 6,
        "all_Hessians_symmetric": all(row["Hessian"]["symmetric_entrywise_over_Q"] for row in rows),
        "all_exact_Euler_identities": all(
            row["exact_target_jet_from_homogeneity"]["q_dot_gradient_equals_degree_times_value_exactly"]
            for row in rows
        ),
        "O14_operator_Hermitian": family_certificates["O14"]["operator_Hermitian_exactly"],
        "all_G3_G4_G5_and_global_claims_fail_closed": not any(
            claims[key]
            for key in (
                "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here",
                "full_486_field_global_equality_orbit_classified",
                "physical_SM_G3_closed",
                "physical_SM_G4_closed",
                "physical_SM_G5_closed",
            )
        ),
    }
    failures = [key for key, value in checks.items() if not value]
    if failures:
        raise ArithmeticError(f"last-six checks failed: {failures}")
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "model_contract_id": hard.MODEL_CONTRACT_ID,
        "source_bindings": bindings,
        "arithmetic_contract": {
            "domains": ["Z", "Gaussian integers Z[i]", "Q"],
            "floating_point_used_to_construct_or_accept_Hessians": False,
            "finite_difference_autodiff_or_rational_recognition_used": False,
        },
        "certified_rows": rows,
        "family_certificates": family_certificates,
        "scope_accounting": {
            "hard_rows": 10,
            "easy_rows": 21,
            "last_rows": 6,
            "total_active_source_Hessians_available": 37,
            "next_exact_step": "compose all exact jets with the rational witness and prove aggregate stationarity, 38-mode kernel, rank 448 and PSD",
            "separate_open_step": "classify the complete 486-field equality locus modulo declared continuous and discrete symmetries",
        },
        "claims": claims,
        "checks": checks,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
    }
    report["integrity"] = {
        "core_sha256": hashlib.sha256(hard.canonical_json_bytes(report)).hexdigest(),
        "ordered_six_row_digest_sha256": hashlib.sha256(
            "\n".join(
                f"{row['direction_id']}:{row['Hessian']['canonical_sparse_rational_sha256']}"
                for row in rows
            ).encode("ascii")
        ).hexdigest(),
    }
    return report


def render_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        (
            "# Exact physical-SM last six Hessians v20",
            "",
            f"Status: `{report['status']}`",
            "",
            "O14, O35 (1/45), and O46 (1/45/54) now have exact full 486-real source Hessians. Across the hard-10, easy-21, and this six-row theorem, all 37 active source Hessians are available.",
            "",
            f"Ordered digest: `{report['integrity']['ordered_six_row_digest_sha256']}`.",
            "",
            "The exact weighted aggregate proof and the separate full global equality-orbit classification remain open here. G3, G4, and G5 remain false.",
            "",
        )
    )


def write_outputs(report: dict[str, Any]) -> None:
    OUT_JSON.write_bytes(hard.canonical_json_bytes(report))
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_outputs(report)
    else:
        print(json.dumps(hard._jsonable(report), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
