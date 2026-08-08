#!/usr/bin/env python3
"""Dense G2 derivative audit for the manuscript's gauged U(1)_X contract.

The historical exact compiler contains 64 invariant directions and 91 real
parameters because it also retained an ungauged-X counterfactual.  This audit
does not rebuild that compiler.  It selects the exact-X-neutral 44 directions
and 51 real parameters identified by :mod:`gauged_u1x_scalar_contract_v20`,
then evaluates their component values, gradients and Hessians on the canonical
486-real physical-hierarchy chart.

The audit also checks the SO(10) and U(1)_X Ward identities and supplies exact
Gaussian-integer/rational pair-Casimir proofs for three projector-zero gradient
columns used by the stationarity bridge.  A symmetry/Ward factorization proves
that the full gradient matrix has rank at most 13, while an exact nonzero 13x13
minor bound to the compiler gradients proves rank at least 13.  Thus the
stationarity rank/nullity are exactly 13/38; float64 SVD is retained only as a
diagnostic.  An elementary rational stationary coefficient witness makes the
differentiated U(1)_X Ward identity ``H @ (T q) = 0`` applicable and guards
against reconstructing a false nullspace from ill-scaled SVD rows.  It is not a
stability, boundedness, global-minimum, or phenomenology result: G3 and the
later gates remain open.

Full generation is intentionally expensive (roughly one minute on a typical
developer machine) because every selected 486 x 486 Hessian is evaluated.
"""
from __future__ import annotations

import argparse
import importlib
import itertools
import json
import math
import time
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_self_source
import exact_gauged_u1x_stationarity_rank_certificate_v20 as exact_rank_source
import exact_phisigma_casimir_projectors_v20 as phi_pair_source
import g1_exact_declared_symmetry_character_census_v20 as census
import gauged_u1x_scalar_contract_v20 as contract
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_derivative_coverage_ledger_v20 as g2
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json"
OUT_MD = ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EXPECTED_DIRECTION_COUNT = 44
EXPECTED_PARAMETER_COUNT = 51
EXPECTED_REAL_FIELD_DIMENSION = 486

# Charges of the independent complex coordinates in the canonical real chart.
# Phi210 is real and X neutral, so its block has no U(1)_X rotation.
U1X_CHARGES = {
    "Phi210": 0,
    "H10": -2,
    "Sigma126bar": -2,
    "S": 4,
    "Phi17": 17,
}

VALUE_ATOL = 1.0e-9
HESSIAN_SYMMETRY_ATOL = 1.0e-9
WARD_RELATIVE_TOLERANCE = 1.0e-10
NORMALIZED_RANK_TOLERANCE = 1.0e-10

# On the selected hierarchy direction three first variations vanish exactly.
# The 54 and 1050bar Sigma-self projections follow from a Z[i] Delta_R pair
# identity.  The mixed Phi^2 Sigma^dag Sigma 210 channel follows from exact
# integer four-form generators: P_210(pp)=0 and P_210(M_DeltaR)p=0.  The dense
# float path leaves cancellation residues, so only these three independently
# certified columns are replaced by exact zeros.
ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS = (
    "lambda::O27_B01_126bar_self_projectors",
    "lambda::O27_B02_126bar_self_projectors",
    "lambda::O44_B03_Phi2_Sigma_projectors",
)
ANALYTIC_ZERO_GRADIENT_ATOL = 1.0e-27
STATIONARITY_RTOL = 2.0e-8
EXPECTED_PROMOTED_STATIONARITY_RANK = 13
EXPECTED_PROMOTED_STATIONARITY_NULLITY = 38

GaussianInteger = tuple[int, int]
ExactForm = dict[tuple[int, ...], GaussianInteger]
ExactMatrix = dict[tuple[int, int], GaussianInteger]
_GI_ZERO: GaussianInteger = (0, 0)
_GI_ONE: GaussianInteger = (1, 0)
_GI_I: GaussianInteger = (0, 1)
_INT64_MAX = int(np.iinfo(np.int64).max)
_INT64_MIN = int(np.iinfo(np.int64).min)


def _checked_int64_array(value: Any, *, label: str) -> np.ndarray:
    """Convert an integer array only after proving every entry fits int64.

    In particular, object/unsigned arrays are inspected as Python integers
    before conversion, so the validation itself cannot wrap.
    """
    source = np.asarray(value)
    if source.dtype == np.dtype(np.int64):
        if np.any(source == _INT64_MIN):
            raise OverflowError(
                f"{label} contains INT64_MIN, whose absolute proof bound "
                "does not fit signed int64"
            )
        return source
    if source.dtype.kind not in "iuO":
        raise TypeError(f"{label} must contain integers, got {source.dtype}")
    for raw in source.flat:
        if not isinstance(raw, (int, np.integer)) or isinstance(raw, (bool, np.bool_)):
            raise TypeError(f"{label} contains a non-integer entry {raw!r}")
        item = int(raw)
        if item < _INT64_MIN or item > _INT64_MAX:
            raise OverflowError(f"{label} contains an entry outside signed int64")
    return np.asarray(source, dtype=np.int64)


def _int64_max_abs(value: Any, *, label: str) -> int:
    source = _checked_int64_array(value, label=label)
    return int(np.max(np.abs(source), initial=0))


def _int64_linear_combination_bound(
    terms: Iterable[tuple[int, np.ndarray]], *, label: str
) -> int:
    prepared = tuple((int(coefficient), matrix) for coefficient, matrix in terms)
    return sum(
        abs(coefficient)
        * _int64_max_abs(matrix, label=f"{label} term {index}")
        for index, (coefficient, matrix) in enumerate(prepared)
    )


def _checked_int64_linear_combination(
    terms: Iterable[tuple[int, np.ndarray]], *, label: str
) -> np.ndarray:
    prepared = tuple(
        (int(coefficient), _checked_int64_array(matrix, label=f"{label} term {index}"))
        for index, (coefficient, matrix) in enumerate(terms)
    )
    if not prepared:
        raise ValueError(f"{label} requires at least one term")
    shape = prepared[0][1].shape
    if any(matrix.shape != shape for _coefficient, matrix in prepared):
        raise ValueError(f"{label} terms have inconsistent shapes")
    envelope = _int64_linear_combination_bound(prepared, label=label)
    if envelope > _INT64_MAX:
        raise OverflowError(
            f"{label} preflight envelope {envelope} exceeds signed int64"
        )
    output = np.zeros(shape, dtype=np.int64)
    for coefficient, matrix in prepared:
        output += coefficient * matrix
    return output


def _int64_matmul_bound(
    left: Any, right: Any, *, label: str
) -> int:
    first = _checked_int64_array(left, label=f"{label} left")
    second = _checked_int64_array(right, label=f"{label} right")
    if first.ndim != 2 or second.ndim != 2 or first.shape[1] != second.shape[0]:
        raise ValueError(f"{label} requires compatible two-dimensional matrices")
    return (
        int(first.shape[1])
        * _int64_max_abs(first, label=f"{label} left")
        * _int64_max_abs(second, label=f"{label} right")
    )


def _checked_int64_matmul(
    left: Any, right: Any, *, label: str
) -> np.ndarray:
    first = _checked_int64_array(left, label=f"{label} left")
    second = _checked_int64_array(right, label=f"{label} right")
    envelope = _int64_matmul_bound(first, second, label=label)
    if envelope > _INT64_MAX:
        raise OverflowError(
            f"{label} preflight envelope {envelope} exceeds signed int64"
        )
    return np.asarray(first @ second, dtype=np.int64)


def _exact_integer_frobenius_pairing(left: Any, right: Any) -> int:
    """Return ``sum_ij left_ij right_ji`` with Python-integer accumulation."""
    first = _checked_int64_array(left, label="Frobenius left")
    second = _checked_int64_array(right, label="Frobenius right")
    if first.shape != second.shape:
        raise ValueError("Frobenius matrices must have the same shape")
    return sum(
        int(first[row, column]) * int(second[column, row])
        for row in range(first.shape[0])
        for column in range(first.shape[1])
    )


def _gi_add(left: GaussianInteger, right: GaussianInteger) -> GaussianInteger:
    return left[0] + right[0], left[1] + right[1]


def _gi_multiply(
    left: GaussianInteger, right: GaussianInteger
) -> GaussianInteger:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _gi_scale(value: GaussianInteger, coefficient: int) -> GaussianInteger:
    return value[0] * coefficient, value[1] * coefficient


def _exact_permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[first] > sequence[second]
        for first in range(len(sequence))
        for second in range(first + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def _exact_form_add(*forms: ExactForm) -> ExactForm:
    output: ExactForm = {}
    for form in forms:
        for indices, coefficient in form.items():
            value = _gi_add(output.get(indices, _GI_ZERO), coefficient)
            if value == _GI_ZERO:
                output.pop(indices, None)
            else:
                output[indices] = value
    return output


def _exact_form_scale(form: ExactForm, coefficient: int) -> ExactForm:
    return {
        indices: value
        for indices, raw in form.items()
        if (value := _gi_scale(raw, coefficient)) != _GI_ZERO
    }


def _exact_one_form(
    index: int, coefficient: GaussianInteger = _GI_ONE
) -> ExactForm:
    return {(index,): coefficient}


def _exact_wedge(left: ExactForm, right: ExactForm) -> ExactForm:
    output: ExactForm = {}
    for left_indices, left_value in left.items():
        for right_indices, right_value in right.items():
            if set(left_indices).intersection(right_indices):
                continue
            sequence = left_indices + right_indices
            indices = tuple(sorted(sequence))
            coefficient = _gi_scale(
                _gi_multiply(left_value, right_value),
                _exact_permutation_sign(sequence),
            )
            value = _gi_add(output.get(indices, _GI_ZERO), coefficient)
            if value == _GI_ZERO:
                output.pop(indices, None)
            else:
                output[indices] = value
    return output


def _exact_interior(form: ExactForm, index: int) -> ExactForm:
    output: ExactForm = {}
    for indices, coefficient in form.items():
        if index not in indices:
            continue
        position = indices.index(index)
        reduced = indices[:position] + indices[position + 1 :]
        output[reduced] = _gi_scale(
            coefficient, -1 if position % 2 else 1
        )
    return output


def _exact_generator_action(form: ExactForm, first: int, second: int) -> ExactForm:
    return _exact_form_add(
        _exact_wedge(_exact_one_form(first), _exact_interior(form, second)),
        _exact_form_scale(
            _exact_wedge(_exact_one_form(second), _exact_interior(form, first)),
            -1,
        ),
    )


@lru_cache(maxsize=1)
def _exact_sigma_basis_rows() -> tuple[
    tuple[tuple[int, ...], tuple[int, ...], int], ...
]:
    rows: list[tuple[tuple[int, ...], tuple[int, ...], int]] = []
    seen: set[tuple[int, ...]] = set()
    all_indices = set(range(10))
    for initial in itertools.combinations(range(10), 5):
        if initial in seen:
            continue
        complement = tuple(sorted(all_indices.difference(initial)))
        seen.add(initial)
        seen.add(complement)
        first, second = (
            (initial, complement)
            if initial < complement
            else (complement, initial)
        )
        rows.append((first, second, _exact_permutation_sign(first + second)))
    if len(rows) != chart.SIGMA_COMPLEX_DIM:
        raise AssertionError("exact anti-self-dual basis must have dimension 126")
    return tuple(rows)


def _exact_basis_form(
    row: tuple[tuple[int, ...], tuple[int, ...], int]
) -> ExactForm:
    first, second, sign = row
    return {first: _GI_ONE, second: (0, sign)}


@lru_cache(maxsize=1)
def _exact_sigma_first_lookup() -> dict[tuple[int, ...], int]:
    return {
        first: index
        for index, (first, _second, _sign) in enumerate(_exact_sigma_basis_rows())
    }


def _exact_sigma_coordinates(form: ExactForm) -> dict[int, GaussianInteger]:
    lookup = _exact_sigma_first_lookup()
    coordinates = {
        lookup[indices]: coefficient
        for indices, coefficient in form.items()
        if indices in lookup and coefficient != _GI_ZERO
    }
    reconstructed: ExactForm = {}
    basis = _exact_sigma_basis_rows()
    for index, coefficient in coordinates.items():
        reconstructed = _exact_form_add(
            reconstructed,
            {
                indices: _gi_multiply(coefficient, value)
                for indices, value in _exact_basis_form(basis[index]).items()
            },
        )
    if reconstructed != form:
        raise AssertionError("form is not exactly in the canonical 126bar basis")
    return coordinates


def _exact_unnormalized_delta_r() -> ExactForm:
    z1 = _exact_form_add(_exact_one_form(0), _exact_one_form(1, _GI_I))
    z2 = _exact_form_add(_exact_one_form(2), _exact_one_form(3, _GI_I))
    z3 = _exact_form_add(_exact_one_form(4), _exact_one_form(5, _GI_I))
    omega3 = _exact_wedge(_exact_wedge(z1, z2), z3)
    j_right = _exact_form_add(
        _exact_wedge(_exact_one_form(6), _exact_one_form(7)),
        _exact_wedge(_exact_one_form(8), _exact_one_form(9)),
    )
    return _exact_wedge(omega3, j_right)


@lru_cache(maxsize=1)
def exact_sigma_chart_convention_certificate() -> dict[str, Any]:
    """Bind the exact Z[i] basis and Delta_R to the live compiler chart."""
    exact_basis = tuple(
        {
            indices: complex(value[0], value[1])
            for indices, value in _exact_basis_form(row).items()
        }
        for row in _exact_sigma_basis_rows()
    )
    compiler_basis = chart.sigma_basis()
    basis_mismatch_indices = [
        index
        for index, (exact, observed) in enumerate(
            zip(exact_basis, compiler_basis, strict=True)
        )
        if exact != observed
    ]

    delta = _exact_unnormalized_delta_r()
    coordinates = _exact_sigma_coordinates(delta)
    exact_kinetic_norm_squared = sum(
        real * real + imaginary * imaginary
        for real, imaginary in coordinates.values()
    )
    normalization = 1.0 / math.sqrt(float(exact_kinetic_norm_squared))
    expected_delta = {
        indices: normalization * complex(value[0], value[1])
        for indices, value in delta.items()
    }
    compiler_delta = direct.delta_r()
    delta_support_matches = set(expected_delta) == set(compiler_delta)
    delta_component_residual = max(
        (
            abs(expected_delta.get(indices, 0.0) - compiler_delta.get(indices, 0.0))
            for indices in set(expected_delta).union(compiler_delta)
        ),
        default=0.0,
    )

    expected_coordinates = np.zeros(chart.SIGMA_COMPLEX_DIM, dtype=complex)
    for index, value in coordinates.items():
        expected_coordinates[index] = normalization * complex(value[0], value[1])
    compiler_coordinates = chart.sigma_coordinates(compiler_delta)
    coordinate_residual = float(
        np.max(np.abs(expected_coordinates - compiler_coordinates), initial=0.0)
    )
    checks = {
        "all_126_exact_basis_forms_equal_chart_sigma_basis_entrywise": (
            len(exact_basis) == len(compiler_basis) == 126
            and not basis_mismatch_indices
        ),
        "exact_Delta_R_kinetic_norm_squared_is_8": (
            exact_kinetic_norm_squared == 8
        ),
        "direct_Delta_R_support_matches_exact_form": delta_support_matches,
        "direct_Delta_R_equals_exact_form_divided_by_sqrt8": (
            delta_component_residual == 0.0
        ),
        "chart_Delta_R_coordinates_equal_exact_coordinates_divided_by_sqrt8": (
            coordinate_residual == 0.0
        ),
        "direct_Delta_R_has_unit_canonical_kinetic_norm": math.isclose(
            direct.sigma_kinetic_norm(compiler_delta),
            1.0,
            rel_tol=0.0,
            abs_tol=2.0e-15,
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_SIGMA_CHART_CONVENTION_BOUND"
            if not failures
            else "EXACT_SIGMA_CHART_CONVENTION_MISMATCH"
        ),
        "binding_scope": (
            "exact Gaussian-integer support/order/phases plus the live direct "
            "compiler's canonical 1/sqrt(8) Delta_R normalization"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "basis_dimension": len(exact_basis),
        "basis_mismatch_indices": basis_mismatch_indices,
        "exact_Delta_R_kinetic_norm_squared": exact_kinetic_norm_squared,
        "direct_Delta_R_normalization": "exact unnormalized Delta_R / sqrt(8)",
        "direct_Delta_R_support_matches": delta_support_matches,
        "direct_Delta_R_max_abs_component_residual": float(
            delta_component_residual
        ),
        "chart_Delta_R_max_abs_coordinate_residual": coordinate_residual,
    }


@lru_cache(maxsize=1)
def _exact_sigma_generator_columns() -> tuple[
    tuple[tuple[tuple[int, GaussianInteger], ...], ...], ...
]:
    basis = _exact_sigma_basis_rows()
    generators = []
    for first, second in itertools.combinations(range(10), 2):
        columns = []
        for row in basis:
            coordinates = _exact_sigma_coordinates(
                _exact_generator_action(_exact_basis_form(row), first, second)
            )
            columns.append(tuple(sorted(coordinates.items())))
        generators.append(tuple(columns))
    return tuple(generators)


def _exact_matrix_accumulate(
    output: ExactMatrix,
    indices: tuple[int, int],
    coefficient: GaussianInteger,
) -> None:
    value = _gi_add(output.get(indices, _GI_ZERO), coefficient)
    if value == _GI_ZERO:
        output.pop(indices, None)
    else:
        output[indices] = value


def _exact_pair_casimir(matrix: ExactMatrix) -> ExactMatrix:
    """Apply K(X)_il=sum_a,j,k T^a_ij X_jk T^a_lk in Z[i]."""
    output: ExactMatrix = {}
    for generator in _exact_sigma_generator_columns():
        for (left, right), coefficient in matrix.items():
            for first, left_generator in generator[left]:
                partial = _gi_multiply(left_generator, coefficient)
                for second, right_generator in generator[right]:
                    _exact_matrix_accumulate(
                        output,
                        (first, second),
                        _gi_multiply(partial, right_generator),
                    )
    return output


def _exact_matrix_linear_combination(
    terms: Iterable[tuple[int, ExactMatrix]],
) -> ExactMatrix:
    output: ExactMatrix = {}
    for weight, matrix in terms:
        for indices, coefficient in matrix.items():
            _exact_matrix_accumulate(
                output, indices, _gi_scale(coefficient, int(weight))
            )
    return output


def _exact_matrix_integer_squared_norm(matrix: ExactMatrix) -> int:
    return sum(real * real + imaginary * imaginary for real, imaginary in matrix.values())


@lru_cache(maxsize=1)
def exact_delta_r_projector_zero_certificate() -> dict[str, Any]:
    """Prove the Delta_R 54/1050bar projected pairs vanish in exact Z[i]."""
    convention = exact_sigma_chart_convention_certificate()
    delta = _exact_unnormalized_delta_r()
    coordinates = _exact_sigma_coordinates(delta)
    pair: ExactMatrix = {
        (left, right): product
        for left, left_value in coordinates.items()
        for right, right_value in coordinates.items()
        if (product := _gi_multiply(left_value, right_value)) != _GI_ZERO
    }
    first_power = _exact_pair_casimir(pair)
    second_power = _exact_pair_casimir(first_power)
    third_power = _exact_pair_casimir(second_power)
    powers = (pair, first_power, second_power, third_power)

    annihilator = _exact_matrix_linear_combination(
        ((1, second_power), (4, first_power), (-5, pair))
    )
    projector_matrices: dict[str, tuple[int, ExactMatrix]] = {}
    projector_rows: dict[str, Any] = {}
    for channel in sigma_self_source.CHANNELS:
        coefficients = sigma_self_source._poly(channel)
        denominator = math.lcm(*(value.denominator for value in coefficients))
        integer_coefficients = tuple(
            value.numerator * (denominator // value.denominator)
            for value in coefficients
        )
        numerator = _exact_matrix_linear_combination(
            zip(integer_coefficients, powers, strict=True)
        )
        kappa = sigma_self_source.KAPPA[channel]
        if kappa.denominator != 1:
            raise AssertionError("pair-Casimir eigenvalue must be integral here")
        eigen_residual = _exact_matrix_linear_combination(
            (
                (1, _exact_pair_casimir(numerator)),
                (-kappa.numerator, numerator),
            )
        )
        projector_matrices[channel] = (denominator, numerator)
        projector_rows[channel] = {
            "pair_Casimir_eigenvalue": str(kappa),
            "cleared_denominator": denominator,
            "integer_polynomial_coefficients_low_to_high": list(
                integer_coefficients
            ),
            "projected_pair_nonzero_entries": len(numerator),
            "projected_pair_integer_squared_norm_numerator": (
                _exact_matrix_integer_squared_norm(numerator)
            ),
            "projected_pair_exactly_zero": not numerator,
            "projector_eigen_equation_exactly_satisfied": not eigen_residual,
        }

    common_denominator = math.lcm(
        *(denominator for denominator, _matrix in projector_matrices.values())
    )
    reconstruction_terms = [
        (common_denominator // denominator, matrix)
        for denominator, matrix in projector_matrices.values()
    ]
    reconstruction_terms.append((-common_denominator, pair))
    reconstruction = _exact_matrix_linear_combination(reconstruction_terms)
    generators = _exact_sigma_generator_columns()
    generator_nonzero_entries = sum(
        len(column) for generator in generators for column in generator
    )

    parameter_channel_map = {
        ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS[0]: "54",
        ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS[1]: "1050bar",
    }
    checks = {
        "exact_basis_and_Delta_R_are_bound_to_live_compiler_chart": convention[
            "certified"
        ],
        "canonical_126bar_basis_dimension_is_126": (
            len(_exact_sigma_basis_rows()) == 126
        ),
        "exact_delta_R_has_16_form_components_and_8_coordinates": (
            len(delta) == 16 and len(coordinates) == 8
        ),
        "all_45_generators_constructed_in_exact_basis": len(generators) == 45,
        "pair_Casimir_eigenvalues_match_projector_source": {
            channel: sigma_self_source.KAPPA[channel]
            for channel in sigma_self_source.CHANNELS
        }
        == {
            "54": 15,
            "1050bar": 7,
            "4125": 1,
            "2772bar": -5,
        },
        "Delta_R_pair_exactly_obeys_K2_plus_4K_minus_5": not annihilator,
        "all_projector_eigen_equations_hold_exactly": all(
            row["projector_eigen_equation_exactly_satisfied"]
            for row in projector_rows.values()
        ),
        "four_projectors_reconstruct_Delta_R_pair_exactly": not reconstruction,
        "54_projected_pair_is_exactly_zero": projector_rows["54"][
            "projected_pair_exactly_zero"
        ],
        "1050bar_projected_pair_is_exactly_zero": projector_rows["1050bar"][
            "projected_pair_exactly_zero"
        ],
        "4125_and_2772bar_projected_pairs_are_nonzero": (
            not projector_rows["4125"]["projected_pair_exactly_zero"]
            and not projector_rows["2772bar"]["projected_pair_exactly_zero"]
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_DELTA_R_54_1050BAR_PROJECTOR_ZERO_CERTIFIED"
            if not failures
            else "EXACT_DELTA_R_PROJECTOR_ZERO_CERTIFICATE_FAILED"
        ),
        "arithmetic_domain": "Gaussian integers Z[i]; rational projector denominators cleared",
        "source_representation": (
            "canonical anti-self-dual five-form basis and pair-Casimir projectors "
            "from exact_126bar_self_quartic_basis_v20"
        ),
        "normalization_scope": (
            "unnormalized Delta_R is used; linear projector vanishing is invariant "
            "under every nonzero complex rescaling, including the physical VEV"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "compiler_chart_convention_binding": convention,
        "canonical_basis_dimension": len(_exact_sigma_basis_rows()),
        "exact_delta_R": {
            "form_component_count": len(delta),
            "nonzero_coordinate_count": len(coordinates),
            "coordinate_integer_squared_norm": sum(
                real * real + imaginary * imaginary
                for real, imaginary in coordinates.values()
            ),
            "nonzero_coordinates": [
                {
                    "index": index,
                    "gaussian_integer": [value[0], value[1]],
                }
                for index, value in sorted(coordinates.items())
            ],
        },
        "exact_generators": {
            "count": len(generators),
            "nonzero_entries": generator_nonzero_entries,
            "maximum_nonzero_entries_per_column": max(
                len(column) for generator in generators for column in generator
            ),
        },
        "Delta_R_pair": {
            "nonzero_entries": len(pair),
            "annihilating_polynomial": "(K-1)(K+5)=K^2+4K-5",
            "annihilator_residual_nonzero_entries": len(annihilator),
            "annihilator_residual_integer_squared_norm": (
                _exact_matrix_integer_squared_norm(annihilator)
            ),
        },
        "projectors": projector_rows,
        "projector_reconstruction": {
            "common_denominator": common_denominator,
            "residual_nonzero_entries": len(reconstruction),
            "residual_integer_squared_norm": (
                _exact_matrix_integer_squared_norm(reconstruction)
            ),
        },
        "parameter_channel_map": parameter_channel_map,
        "gradient_implication": {
            "invariant": "I_R(z)=||P_R(z z^T)||_F^2",
            "first_variation": (
                "dI_R=2 Re <P_R(zz^T), P_R(dz z^T+z dz^T)>"
            ),
            "exact_projected_pair_zero_implies_full_real_gradient_zero": True,
            "certified_parameter_ids": list(parameter_channel_map),
        },
    }


@lru_cache(maxsize=1)
def _exact_phi_generator_matrices_cached() -> tuple[sparse.csr_matrix, ...]:
    """Return the 45 Lambda^4(R^10) generators with exact integer entries."""
    indices = chart.phi_indices()
    lookup = {row: index for index, row in enumerate(indices)}
    output: list[sparse.csr_matrix] = []
    for first, second in itertools.combinations(range(10), 2):
        rows: list[int] = []
        columns: list[int] = []
        values: list[int] = []
        for column, source in enumerate(indices):
            action = _exact_generator_action({source: _GI_ONE}, first, second)
            for target, (real, imaginary) in action.items():
                if imaginary != 0:
                    raise AssertionError("real 210 generator is not integral-real")
                rows.append(lookup[target])
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
def _exact_phi_generator_int64_structure() -> dict[str, int]:
    """Return the exact sparsity bounds used before every Phi Casimir step."""
    generators = _exact_phi_generator_matrices_cached()
    maximum_entry = max(
        (
            max((abs(int(value)) for value in generator.data), default=0)
            for generator in generators
        ),
        default=0,
    )
    maximum_row_nnz = max(
        (
            int(np.max(generator.getnnz(axis=1), initial=0))
            for generator in generators
        ),
        default=0,
    )
    maximum_column_nnz = max(
        (
            int(np.max(generator.getnnz(axis=0), initial=0))
            for generator in generators
        ),
        default=0,
    )
    row_activity = np.stack(
        [
            np.asarray(generator.getnnz(axis=1) > 0, dtype=np.int16)
            for generator in generators
        ]
    )
    simultaneous_contributions = row_activity.T @ row_activity
    return {
        "generator_count": len(generators),
        "maximum_abs_generator_entry": maximum_entry,
        "maximum_nonzero_entries_per_generator_row": maximum_row_nnz,
        "maximum_nonzero_entries_per_generator_column": maximum_column_nnz,
        "active_generators_per_basis_row_minimum": int(
            np.min(np.sum(row_activity, axis=0), initial=len(generators))
        ),
        "active_generators_per_basis_row_maximum": int(
            np.max(np.sum(row_activity, axis=0), initial=0)
        ),
        "maximum_simultaneous_contributions_per_pair_Casimir_output_entry": int(
            np.max(simultaneous_contributions, initial=0)
        ),
    }


def _exact_phi_pair_casimir(matrix: np.ndarray) -> np.ndarray:
    """Apply the exact integer pair Casimir on 210x210 real matrices."""
    source = _checked_int64_array(matrix, label="Phi pair-Casimir input")
    if source.shape != (chart.PHI_DIM, chart.PHI_DIM):
        raise ValueError("Phi pair matrix must have shape 210x210")
    structure = _exact_phi_generator_int64_structure()
    if not (
        structure["maximum_abs_generator_entry"] == 1
        and structure["maximum_nonzero_entries_per_generator_row"] <= 1
        and structure["maximum_nonzero_entries_per_generator_column"] <= 1
    ):
        raise AssertionError("Phi generator sparsity no longer supports the int64 proof")
    input_maximum = _int64_max_abs(source, label="Phi pair-Casimir input")
    envelope = (
        input_maximum
        * structure[
            "maximum_simultaneous_contributions_per_pair_Casimir_output_entry"
        ]
    )
    if envelope > _INT64_MAX:
        raise OverflowError(
            "Phi pair-Casimir preflight envelope "
            f"{envelope} exceeds signed int64"
        )
    output = np.zeros_like(source)
    for generator in _exact_phi_generator_matrices_cached():
        output += np.asarray(generator @ source @ generator.T, dtype=np.int64)
    return output


def _cleared_phi_pair_projector(
    matrix: np.ndarray, target: Fraction
) -> tuple[int, tuple[int, ...], np.ndarray, tuple[int, ...]]:
    coefficients = phi_pair_source.projector_polynomial(target)
    denominator = math.lcm(*(value.denominator for value in coefficients))
    integer_coefficients = tuple(
        value.numerator * (denominator // value.denominator)
        for value in coefficients
    )
    current = _checked_int64_array(matrix, label="cleared Phi projector input")
    powers = [current]
    power_maxima = [int(np.max(np.abs(current), initial=0))]
    for _coefficient in integer_coefficients[1:]:
        current = _exact_phi_pair_casimir(current)
        powers.append(current)
        power_maxima.append(int(np.max(np.abs(current), initial=0)))
    integer_envelope = sum(
        abs(coefficient) * maximum
        for coefficient, maximum in zip(
            integer_coefficients, power_maxima, strict=True
        )
    )
    if integer_envelope > _INT64_MAX:
        raise OverflowError("cleared Phi projector exceeds int64 proof domain")
    numerator = _checked_int64_linear_combination(
        zip(integer_coefficients, powers, strict=True),
        label="cleared Phi projector polynomial",
    )
    return denominator, integer_coefficients, numerator, tuple(power_maxima)


def _exact_delta_contraction_gram() -> tuple[np.ndarray, int]:
    """Return Re(C(Delta_R)^dag C(Delta_R)) exactly over Z."""
    delta = _exact_unnormalized_delta_r()
    real = np.zeros((10, chart.PHI_DIM), dtype=np.int64)
    imaginary = np.zeros((10, chart.PHI_DIM), dtype=np.int64)
    for column, indices in enumerate(chart.phi_indices()):
        for free_index in range(10):
            if free_index in indices:
                continue
            sequence = indices + (free_index,)
            five = tuple(sorted(sequence))
            coefficient = delta.get(five, _GI_ZERO)
            sign = _exact_permutation_sign(sequence)
            real[free_index, column] = sign * coefficient[0]
            imaginary[free_index, column] = sign * coefficient[1]
    real_gram = _checked_int64_matmul(
        real.T, real, label="Delta_R real contraction Gram"
    )
    imaginary_gram = _checked_int64_matmul(
        imaginary.T, imaginary, label="Delta_R imaginary contraction Gram"
    )
    gram = _checked_int64_linear_combination(
        ((1, real_gram), (1, imaginary_gram)),
        label="Delta_R contraction Gram",
    )
    nonzero = int(np.count_nonzero(real) + np.count_nonzero(imaginary))
    return gram, nonzero


@lru_cache(maxsize=1)
def _exact_p24_four_times_with_safety() -> tuple[np.ndarray, dict[str, Any]]:
    """Return 4*P_24 and preflight bounds for every dense int64 operation."""
    labels = tuple(itertools.combinations(range(10), 2))
    lookup = {label: index for index, label in enumerate(labels)}
    generators = _exact_phi_generator_matrices_cached()
    operation_bounds: dict[str, int] = {}

    def checked_combination(
        terms: Iterable[tuple[int, np.ndarray]], *, label: str
    ) -> np.ndarray:
        prepared = tuple(terms)
        operation_bounds[label] = _int64_linear_combination_bound(
            prepared, label=label
        )
        return _checked_int64_linear_combination(prepared, label=label)

    def checked_product(
        left: np.ndarray, right: np.ndarray, *, label: str
    ) -> np.ndarray:
        operation_bounds[label] = _int64_matmul_bound(left, right, label=label)
        return _checked_int64_matmul(left, right, label=label)

    def generator_combination(
        terms: dict[tuple[int, int], int], *, label: str
    ) -> np.ndarray:
        return checked_combination(
            (
                (coefficient, generators[lookup[generator_label]].toarray())
                for generator_label, coefficient in terms.items()
            ),
            label=label,
        )

    su3 = (
        generator_combination(
            {(0, 1): 1, (2, 3): -1}, label="SU3 generator 0"
        ),
        generator_combination(
            {(2, 3): 1, (4, 5): -1}, label="SU3 generator 1"
        ),
        generator_combination(
            {(0, 2): 1, (1, 3): 1}, label="SU3 generator 2"
        ),
        generator_combination(
            {(0, 3): 1, (1, 2): -1}, label="SU3 generator 3"
        ),
        generator_combination(
            {(0, 4): 1, (1, 5): 1}, label="SU3 generator 4"
        ),
        generator_combination(
            {(0, 5): 1, (1, 4): -1}, label="SU3 generator 5"
        ),
        generator_combination(
            {(2, 4): 1, (3, 5): 1}, label="SU3 generator 6"
        ),
        generator_combination(
            {(2, 5): 1, (3, 4): -1}, label="SU3 generator 7"
        ),
    )
    diagonal_first, diagonal_second, *off_diagonal = su3
    # The coefficient-space Gram is [[2,-1],[-1,2]] plus 2 I_6.
    # Therefore C6=6*C_SU3 is the following exact integer matrix.
    diagonal_products = (
        checked_product(
            diagonal_first, diagonal_first, label="SU3 diagonal product 00"
        ),
        checked_product(
            diagonal_first, diagonal_second, label="SU3 diagonal product 01"
        ),
        checked_product(
            diagonal_second, diagonal_first, label="SU3 diagonal product 10"
        ),
        checked_product(
            diagonal_second, diagonal_second, label="SU3 diagonal product 11"
        ),
    )
    off_diagonal_products = tuple(
        checked_product(
            generator, generator, label=f"SU3 off-diagonal square {index}"
        )
        for index, generator in enumerate(off_diagonal)
    )
    casimir_times_six = checked_combination(
        (
            (-4, diagonal_products[0]),
            (-2, diagonal_products[1]),
            (-2, diagonal_products[2]),
            (-4, diagonal_products[3]),
            *((-3, matrix) for matrix in off_diagonal_products),
        ),
        label="C6 construction",
    )
    identity = np.eye(chart.PHI_DIM, dtype=np.int64)
    electric = generators[lookup[(8, 9)]].toarray()
    # C6 spectrum is {0,16,36,40}.  I+Q^2 selects Q^2=0.  The
    # spectral denominator 40*(40-16)*(40-36)=3840 simplifies to
    # quarter-integer entries, so numerator/960 is exactly 4P_24.
    c_minus_16 = checked_combination(
        ((1, casimir_times_six), (-16, identity)), label="C6 minus 16I"
    )
    c_minus_36 = checked_combination(
        ((1, casimir_times_six), (-36, identity)), label="C6 minus 36I"
    )
    electric_squared = checked_product(
        electric, electric, label="electric generator square"
    )
    neutral_selector = checked_combination(
        ((1, identity), (1, electric_squared)), label="I plus Q squared"
    )
    first_polynomial_product = checked_product(
        casimir_times_six, c_minus_16, label="P24 polynomial product 1"
    )
    second_polynomial_product = checked_product(
        first_polynomial_product,
        c_minus_36,
        label="P24 polynomial product 2",
    )
    numerator = checked_product(
        second_polynomial_product,
        neutral_selector,
        label="P24 polynomial product 3",
    )
    if np.any(numerator % 960):
        raise AssertionError("P24 did not simplify to quarter-integer entries")
    projector_times_four = numerator // 960
    if not np.array_equal(projector_times_four, projector_times_four.T):
        raise AssertionError("P24 is not symmetric")
    projector_square = checked_product(
        projector_times_four,
        projector_times_four,
        label="P24 idempotence square",
    )
    four_projector = checked_combination(
        ((4, projector_times_four),), label="four times P24"
    )
    if not np.array_equal(projector_square, four_projector):
        raise AssertionError("P24 is not exactly idempotent")
    safety = {
        "storage_domain": "signed int64 after Python-integer preflight bounds",
        "signed_int64_maximum": _INT64_MAX,
        "operation_preflight_bounds": operation_bounds,
        "maximum_operation_preflight_bound": max(
            operation_bounds.values(), default=0
        ),
        "all_preflight_bounds_fit_signed_int64": all(
            bound <= _INT64_MAX for bound in operation_bounds.values()
        ),
    }
    safety["certified"] = safety["all_preflight_bounds_fit_signed_int64"]
    projector_times_four.setflags(write=False)
    return projector_times_four, safety


def _exact_p24_four_times() -> np.ndarray:
    """Return a copy of exact ``4*P_24`` after all int64 preflights pass."""
    return _exact_p24_four_times_with_safety()[0].copy()


@lru_cache(maxsize=1)
def _exact_phi_witness_integer_matrices() -> dict[str, Any]:
    """Build the three exact Phi Hessians shared by proof and compiler binding."""
    p_index = chart.phi_indices().index((6, 7, 8, 9))
    p = np.zeros(chart.PHI_DIM, dtype=np.int64)
    p[p_index] = 1
    pair = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64)
    pair[p_index, p_index] = 1
    identity = np.eye(chart.PHI_DIM, dtype=np.int64)

    j0_gradient = _checked_int64_linear_combination(
        ((4, p),), label="J0 gradient"
    )
    j0_hessian = _checked_int64_linear_combination(
        ((4, identity), (8, pair)), label="J0 Hessian"
    )
    j2_image = _exact_phi_pair_casimir(_exact_phi_pair_casimir(pair))
    j2_gradient = _checked_int64_linear_combination(
        ((4, j2_image[:, p_index]),), label="J2 gradient"
    )
    j2_hessian = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64)
    for column in range(chart.PHI_DIM):
        linear_pair = np.zeros_like(pair)
        linear_pair[p_index, column] += 1
        linear_pair[column, p_index] += 1
        linear_image = _exact_phi_pair_casimir(
            _exact_phi_pair_casimir(linear_pair)
        )
        j2_hessian[:, column] = _checked_int64_linear_combination(
            (
                (4, linear_image[:, p_index]),
                (4, j2_image[:, column]),
            ),
            label=f"J2 Hessian column {column}",
        )
    phi_norm_gradient = _checked_int64_linear_combination(
        ((2, p),), label="Phi norm gradient"
    )
    phi_norm_hessian = _checked_int64_linear_combination(
        ((2, identity),), label="Phi norm Hessian"
    )
    witness_gradient_times_four = _checked_int64_linear_combination(
        (
            (40, phi_norm_gradient),
            (4, j0_gradient),
            (-1, j2_gradient),
        ),
        label="stationary witness gradient times four",
    )
    hessians = {
        "lambda::O07_B01_Phi_norm": phi_norm_hessian,
        "lambda::O48_B01_Phi_self_quartics": j0_hessian,
        "lambda::O48_B02_Phi_self_quartics": j2_hessian,
    }
    for matrix in (*hessians.values(), witness_gradient_times_four):
        matrix.setflags(write=False)
    return {
        "p_index": p_index,
        "pair": pair,
        "gradients": {
            "lambda::O07_B01_Phi_norm": phi_norm_gradient,
            "lambda::O48_B01_Phi_self_quartics": j0_gradient,
            "lambda::O48_B02_Phi_self_quartics": j2_gradient,
        },
        "hessians": hessians,
        "witness_gradient_times_four": witness_gradient_times_four,
    }


@lru_cache(maxsize=1)
def exact_phi_projector_and_stationary_witness_certificate() -> dict[str, Any]:
    """Certify the O44/B03 zero, P24, and a rational stationary witness."""
    phi_indices = chart.phi_indices()
    p_index = phi_indices.index((6, 7, 8, 9))
    pair = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=np.int64)
    pair[p_index, p_index] = 1
    denominator, coefficients, projected_pair, pair_power_maxima = (
        _cleared_phi_pair_projector(pair, Fraction(12))
    )
    delta_gram, contraction_nonzero = _exact_delta_contraction_gram()
    (
        delta_denominator,
        delta_coefficients,
        projected_delta,
        delta_power_maxima,
    ) = _cleared_phi_pair_projector(delta_gram, Fraction(12))
    if (delta_denominator, delta_coefficients) != (denominator, coefficients):
        raise AssertionError("inconsistent cleared 210 projector")

    projector_times_four, p24_safety = _exact_p24_four_times_with_safety()
    witness_matrices = _exact_phi_witness_integer_matrices()
    witness_gradient_times_four = witness_matrices[
        "witness_gradient_times_four"
    ]

    def projector_trace(hessian: np.ndarray) -> int:
        numerator = _exact_integer_frobenius_pairing(
            projector_times_four, hessian
        )
        if numerator % 4:
            raise AssertionError("P24 Hessian trace is not integral")
        return numerator // 4

    trace_coefficients = {
        parameter_id: projector_trace(hessian)
        for parameter_id, hessian in witness_matrices["hessians"].items()
    }
    witness_trace = (
        10 * trace_coefficients["lambda::O07_B01_Phi_norm"]
        + trace_coefficients["lambda::O48_B01_Phi_self_quartics"]
        - trace_coefficients["lambda::O48_B02_Phi_self_quartics"] // 4
    )
    generator_structure = _exact_phi_generator_int64_structure()
    casimir_multiplicity = generator_structure[
        "maximum_simultaneous_contributions_per_pair_Casimir_output_entry"
    ]
    pair_step_bounds = [
        casimir_multiplicity * maximum for maximum in pair_power_maxima[:-1]
    ]
    delta_step_bounds = [
        casimir_multiplicity * maximum for maximum in delta_power_maxima[:-1]
    ]
    pair_projector_envelope = sum(
        abs(coefficient) * maximum
        for coefficient, maximum in zip(
            coefficients, pair_power_maxima, strict=True
        )
    )
    delta_projector_envelope = sum(
        abs(coefficient) * maximum
        for coefficient, maximum in zip(
            coefficients, delta_power_maxima, strict=True
        )
    )
    int64_safety = {
        "storage_domain": "signed int64 after Python-integer preflight bounds",
        "signed_int64_maximum": _INT64_MAX,
        "Phi_generator_structure": generator_structure,
        "pair_Casimir_bound_formula": (
            "max_abs(K(M)) <= 24 max_abs(M), because every generator has at "
            "most one +/-1 entry per row/column and at most 24 generators "
            "contribute to any output entry"
        ),
        "pp_pair_Casimir_step_preflight_bounds": pair_step_bounds,
        "Delta_pair_Casimir_step_preflight_bounds": delta_step_bounds,
        "pp_cleared_projector_preflight_envelope": pair_projector_envelope,
        "Delta_cleared_projector_preflight_envelope": (
            delta_projector_envelope
        ),
        "P24_dense_operation_safety": p24_safety,
    }
    int64_safety["maximum_preflight_bound"] = max(
        (
            *pair_step_bounds,
            *delta_step_bounds,
            pair_projector_envelope,
            delta_projector_envelope,
            p24_safety["maximum_operation_preflight_bound"],
        ),
        default=0,
    )
    int64_safety["certified"] = bool(
        generator_structure["generator_count"] == 45
        and generator_structure["maximum_abs_generator_entry"] == 1
        and generator_structure[
            "maximum_nonzero_entries_per_generator_row"
        ]
        == 1
        and generator_structure[
            "maximum_nonzero_entries_per_generator_column"
        ]
        == 1
        and casimir_multiplicity == 24
        and int64_safety["maximum_preflight_bound"] <= _INT64_MAX
        and p24_safety["certified"]
    )
    checks = {
        "all_45_integer_Phi_generators_constructed": (
            len(_exact_phi_generator_matrices_cached()) == 45
        ),
        "all_pair_Casimir_projector_and_P24_int64_operations_are_preflight_safe": (
            int64_safety["certified"]
        ),
        "cleared_210_projector_coefficients_match": coefficients
        == (0, 258048, -152832, -32, 8024, -1140, 58, -1),
        "P210_pp_is_exactly_zero": not np.any(projected_pair),
        "P210_Delta_pair_annihilates_p_on_right": not np.any(
            projected_delta[:, p_index]
        ),
        "P210_Delta_pair_annihilates_p_on_left": not np.any(
            projected_delta[p_index, :]
        ),
        "P210_Delta_pair_is_nonzero": bool(np.any(projected_delta)),
        "P24_is_quarter_integer_symmetric_idempotent": bool(
            np.array_equal(projector_times_four, projector_times_four.T)
            and np.array_equal(
                _checked_int64_matmul(
                    projector_times_four,
                    projector_times_four,
                    label="P24 certificate idempotence square",
                ),
                _checked_int64_linear_combination(
                    ((4, projector_times_four),),
                    label="P24 certificate four times projector",
                ),
            )
        ),
        "P24_rank_and_trace_are_24": int(np.trace(projector_times_four)) == 96,
        "stationary_witness_gradient_is_exactly_zero": not np.any(
            witness_gradient_times_four
        ),
        "stationary_witness_respects_4pi_box": 10.0 < 4.0 * math.pi,
        "stationary_witness_P24_trace_is_positive_288": witness_trace == 288,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_PHI210_210_ZERO_P24_AND_WITNESS_CERTIFIED"
            if not failures
            else "EXACT_PHI210_PROJECTOR_CERTIFICATE_FAILED"
        ),
        "arithmetic_domain": "Z[i] contractions; integer generators; rational projectors",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "integer_arithmetic_safety": int64_safety,
        "O44_B03_210_gradient_zero": {
            "parameter_id": "lambda::O44_B03_Phi2_Sigma_projectors",
            "channel": "210",
            "pair_Casimir_eigenvalue": "12",
            "cleared_denominator": denominator,
            "integer_polynomial_coefficients_low_to_high": list(coefficients),
            "P210_pp_numerator_nonzero_entries": int(
                np.count_nonzero(projected_pair)
            ),
            "P210_Delta_pair_numerator_nonzero_entries": int(
                np.count_nonzero(projected_delta)
            ),
            "P210_Delta_pair_numerator_max_abs_entry": int(
                np.max(np.abs(projected_delta), initial=0)
            ),
            "P210_Delta_pair_p_column_max_abs_entry": int(
                np.max(np.abs(projected_delta[:, p_index]), initial=0)
            ),
            "P210_Delta_pair_p_row_max_abs_entry": int(
                np.max(np.abs(projected_delta[p_index, :]), initial=0)
            ),
            "Delta_contraction_Gaussian_nonzero_entries": contraction_nonzero,
            "pp_power_maxima": list(pair_power_maxima),
            "Delta_pair_power_maxima": list(delta_power_maxima),
            "gradient_implication": (
                "d_phi I=2 P210(M_Delta)p=0 and d_Sigma I is proportional "
                "to P210(pp)=0"
            ),
            "certified": bool(
                not np.any(projected_pair)
                and not np.any(projected_delta[:, p_index])
                and not np.any(projected_delta[p_index, :])
            ),
        },
        "P24": {
            "representation": "Phi210",
            "unbroken_sector": "C_SU3=20/3 and Q^2=0",
            "formula": "C6(C6-16I)(C6-36I)(I+Q^2)/3840, C6=6 C_SU3",
            "entry_domain": "(1/4) Z",
            "rank": int(np.trace(projector_times_four)) // 4,
            "trace": int(np.trace(projector_times_four)) // 4,
            "idempotence_exact": checks[
                "P24_is_quarter_integer_symmetric_idempotent"
            ],
        },
        "stationary_witness": {
            "coefficients": {
                "lambda::O07_B01_Phi_norm": "10",
                "lambda::O48_B01_Phi_self_quartics": "1",
                "lambda::O48_B02_Phi_self_quartics": "-1/4",
            },
            "all_unlisted_coefficients": "0",
            "only_tadpole_identity": "2*10 + 4*1 + 96*(-1/4) = 0",
            "normalization_parameter_id": "lambda::O48_B01_Phi_self_quartics",
            "normalization_value": "1",
            "maximum_abs_coupling": "10",
            "strictly_inside_4pi_box": checks[
                "stationary_witness_respects_4pi_box"
            ],
            "P24_trace_coefficients": trace_coefficients,
            "P24_trace": witness_trace,
            "gradient_exactly_zero": checks[
                "stationary_witness_gradient_is_exactly_zero"
            ],
        },
    }


def _compiled_stationary_witness_p24_binding(
    parameter_rows: tuple[derivatives.ParameterDerivative, ...],
    compiled_witness_hessian: np.ndarray,
) -> dict[str, Any]:
    """Bind the exact 288 trace to the actual dense compiler Hessians."""
    exact_certificate = exact_phi_projector_and_stationary_witness_certificate()
    exact_data = _exact_phi_witness_integer_matrices()
    exact_hessians = exact_data["hessians"]
    projector_times_four = _exact_p24_four_times()
    by_id = {row.parameter_id: row for row in parameter_rows}
    missing = sorted(set(exact_hessians).difference(by_id))

    compiler_traces: dict[str, float] = {}
    maximum_phi_entry_residuals: dict[str, float] = {}
    maximum_outside_phi_entries: dict[str, float] = {}
    full_entrywise_matches: dict[str, bool] = {}
    for parameter_id, exact_hessian in exact_hessians.items():
        if parameter_id not in by_id:
            continue
        compiled = np.asarray(by_id[parameter_id].hessian, dtype=float)
        if compiled.shape != (chart.TOTAL_DIM, chart.TOTAL_DIM):
            maximum_phi_entry_residuals[parameter_id] = float("inf")
            maximum_outside_phi_entries[parameter_id] = float("inf")
            full_entrywise_matches[parameter_id] = False
            continue
        phi_block = compiled[chart.PHI_SLICE, chart.PHI_SLICE]
        outside = compiled.copy()
        outside[chart.PHI_SLICE, chart.PHI_SLICE] = 0.0
        maximum_phi_entry_residuals[parameter_id] = float(
            np.max(np.abs(phi_block - exact_hessian), initial=0.0)
        )
        maximum_outside_phi_entries[parameter_id] = float(
            np.max(np.abs(outside), initial=0.0)
        )
        full_entrywise_matches[parameter_id] = bool(
            np.array_equal(phi_block, exact_hessian)
            and not np.any(outside)
        )
        compiler_traces[parameter_id] = float(
            np.sum(projector_times_four.astype(float) * phi_block.T) / 4.0
        )

    exact_combination_numerator = _checked_int64_linear_combination(
        (
            (40, exact_hessians["lambda::O07_B01_Phi_norm"]),
            (4, exact_hessians["lambda::O48_B01_Phi_self_quartics"]),
            (-1, exact_hessians["lambda::O48_B02_Phi_self_quartics"]),
        ),
        label="stationary witness Hessian times four",
    )
    if np.any(exact_combination_numerator % 4):
        raise AssertionError("exact stationary witness Hessian is not integral")
    exact_combination = exact_combination_numerator // 4
    compiled_combination = np.asarray(compiled_witness_hessian, dtype=float)
    compiled_phi_combination = compiled_combination[
        chart.PHI_SLICE, chart.PHI_SLICE
    ]
    compiled_outside_phi = compiled_combination.copy()
    compiled_outside_phi[chart.PHI_SLICE, chart.PHI_SLICE] = 0.0
    combination_max_abs_residual = float(
        np.max(
            np.abs(compiled_phi_combination - exact_combination), initial=0.0
        )
    )
    combination_outside_phi_max_abs = float(
        np.max(np.abs(compiled_outside_phi), initial=0.0)
    )
    compiler_combination_trace = float(
        np.sum(
            projector_times_four.astype(float)
            * compiled_phi_combination.T
        )
        / 4.0
    )
    expected_traces = exact_certificate["stationary_witness"][
        "P24_trace_coefficients"
    ]
    trace_residuals = {
        parameter_id: abs(compiler_traces.get(parameter_id, float("inf")) - expected)
        for parameter_id, expected in expected_traces.items()
    }
    checks = {
        "all_three_witness_parameter_Hessians_are_present": not missing,
        "all_three_compiler_Hessians_equal_exact_integer_Hessians_entrywise": (
            len(full_entrywise_matches) == 3
            and all(full_entrywise_matches.values())
        ),
        "compiled_P24_trace_coefficients_equal_48_96_1152": (
            compiler_traces
            == {
                "lambda::O07_B01_Phi_norm": 48.0,
                "lambda::O48_B01_Phi_self_quartics": 96.0,
                "lambda::O48_B02_Phi_self_quartics": 1152.0,
            }
        ),
        "compiled_witness_Hessian_equals_exact_combination_entrywise": (
            combination_max_abs_residual == 0.0
            and combination_outside_phi_max_abs == 0.0
        ),
        "compiled_witness_P24_trace_is_exactly_288": (
            compiler_combination_trace == 288.0
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_P24_TRACE_BOUND_TO_DENSE_COMPILER"
            if not failures
            else "EXACT_P24_TRACE_COMPILER_BINDING_FAILED"
        ),
        "binding_scope": (
            "the three exact integer Phi Hessians are compared entrywise with "
            "the actual 486x486 adapter outputs before tracing their compiled "
            "stationary combination against exact 4P24"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "certified": not failures,
        "missing_parameter_ids": missing,
        "compiler_P24_trace_coefficients": compiler_traces,
        "exact_P24_trace_coefficients": expected_traces,
        "trace_coefficient_abs_residuals": trace_residuals,
        "per_parameter_max_abs_Phi_Hessian_residual": (
            maximum_phi_entry_residuals
        ),
        "per_parameter_max_abs_outside_Phi_Hessian_entry": (
            maximum_outside_phi_entries
        ),
        "per_parameter_full_entrywise_match": full_entrywise_matches,
        "compiled_witness_Hessian_max_abs_residual": (
            combination_max_abs_residual
        ),
        "compiled_witness_Hessian_max_abs_outside_Phi_entry": (
            combination_outside_phi_max_abs
        ),
        "compiled_witness_P24_trace": compiler_combination_trace,
        "exact_witness_P24_trace": exact_certificate["stationary_witness"][
            "P24_trace"
        ],
    }


def _fraction_determinant(matrix: list[list[Fraction]]) -> Fraction:
    value = [row.copy() for row in matrix]
    determinant = Fraction(1)
    for column in range(len(value)):
        pivot = next(
            (row for row in range(column, len(value)) if value[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            value[column], value[pivot] = value[pivot], value[column]
            determinant *= -1
        pivot_value = value[column][column]
        determinant *= pivot_value
        for index in range(column, len(value)):
            value[column][index] /= pivot_value
        for row in range(column + 1, len(value)):
            factor = value[row][column]
            for index in range(column, len(value)):
                value[row][index] -= factor * value[column][index]
    return determinant


@lru_cache(maxsize=1)
def exact_stationarity_rank_lower_bound_certificate() -> dict[str, Any]:
    """Expose the exact rank certificate through the historical G2 API."""
    report = exact_rank_source.build_report()
    lower = report["rank_lower_certificate"]
    upper = report["rank_upper_certificate"]
    determinant_nonzero = bool(
        lower["certified"]
        and lower["row_scaled_minor"]["determinant_nonzero_assumption"]
        == "h != 0"
    )
    return {
        "arithmetic_domain": lower["arithmetic_domain"],
        "row_count": len(lower["coordinate_rows"]),
        "column_count": len(lower["parameter_columns"]),
        "coordinate_rows": lower["coordinate_rows"],
        "parameter_columns": lower["parameter_columns"],
        "determinant_nonzero": determinant_nonzero,
        "determinant": lower["row_scaled_minor"]["determinant"],
        "determinant_factorization": lower["delicate_O31_explanation"],
        "certified_rank_lower_bound": 13 if determinant_nonzero else 0,
        "certified_rank_upper_bound": upper["rank_upper_bound"],
        "exact_rank_upper_bound_certified": upper["certified"],
        "exact_rank_13_certified": report["certified"],
        "exact_nullity_38_certified": report["certified"],
        "exact_rank_factorization": upper["factorization"],
        "exact_rank_certificate": report,
        "compiler_binding_required_for_G2_promotion": True,
        "missing_for_exact_rank": None if report["certified"] else report["failures"],
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


@lru_cache(maxsize=1)
def _contract_selection_cached() -> tuple[
    tuple[dict[str, Any], ...], tuple[str, ...], dict[str, Any]
]:
    report = contract.build_report()
    rows = tuple(report["gauged_directions"])
    parameter_ids = tuple(str(item) for item in report["gauged_parameter_ids"])
    return rows, parameter_ids, report


def contract_selection() -> dict[str, Any]:
    """Return the authoritative direction/parameter selection without G2 work."""
    rows, parameter_ids, report = _contract_selection_cached()
    return {
        "model_contract_id": report["model_contract_id"],
        "direction_ids": tuple(str(row["direction_id"]) for row in rows),
        "parameter_ids": parameter_ids,
        "base_families": tuple(sorted({str(row["base_family"]) for row in rows})),
        "direction_count": len(rows),
        "parameter_count": len(parameter_ids),
        "real_field_dimension": chart.TOTAL_DIM,
    }


@lru_cache(maxsize=1)
def _u1x_generator_matrix_cached() -> np.ndarray:
    generator = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    charged_blocks = (
        (chart.H_SLICE, U1X_CHARGES["H10"]),
        (chart.SIGMA_SLICE, U1X_CHARGES["Sigma126bar"]),
        (chart.S_SLICE, U1X_CHARGES["S"]),
        (chart.X_SLICE, U1X_CHARGES["Phi17"]),
    )
    for block, charge in charged_blocks:
        if (block.stop - block.start) % 2:
            raise AssertionError("complex chart blocks must contain real/imaginary pairs")
        for real_index in range(block.start, block.stop, 2):
            imaginary_index = real_index + 1
            generator[real_index, imaginary_index] = -float(charge)
            generator[imaginary_index, real_index] = float(charge)
    generator.setflags(write=False)
    return generator


def u1x_generator_matrix() -> np.ndarray:
    """Return T for delta q = T q in the interleaved real/imaginary chart."""
    return _u1x_generator_matrix_cached().copy()


def u1x_tangent(state: potential.FieldState) -> np.ndarray:
    """Return the full 486-real U(1)_X orbit tangent at ``state``."""
    return _u1x_generator_matrix_cached() @ chart.pack(state)


def _complex_generator_real_chart(matrix: np.ndarray) -> np.ndarray:
    """Convert a complex-linear generator to the interleaved real chart."""
    source = np.asarray(matrix, dtype=complex)
    output = np.zeros((2 * source.shape[0], 2 * source.shape[1]), dtype=float)
    output[0::2, 0::2] = source.real
    output[0::2, 1::2] = -source.imag
    output[1::2, 0::2] = source.imag
    output[1::2, 1::2] = source.real
    return output


@lru_cache(maxsize=1)
def _so10_generator_matrices_cached() -> tuple[np.ndarray, ...]:
    """Return all 45 SO(10) generators in the canonical 486-real chart."""
    phi_indices = chart.phi_indices()
    phi_lookup = {indices: index for index, indices in enumerate(phi_indices)}
    sigma_basis = chart.sigma_basis()
    generators: list[np.ndarray] = []
    for first, second in itertools.combinations(range(10), 2):
        generator = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)

        for column, indices in enumerate(phi_indices):
            variation = direct.generator_action({indices: 1.0}, first, second)
            for target, value in variation.items():
                coefficient = complex(value)
                if abs(coefficient.imag) > 1.0e-12:
                    raise ValueError("real 210 generator acquired an imaginary entry")
                generator[phi_lookup[target], column] = coefficient.real

        vector = np.zeros((chart.H_COMPLEX_DIM, chart.H_COMPLEX_DIM), dtype=complex)
        vector[first, second] = 1.0
        vector[second, first] = -1.0
        generator[chart.H_SLICE, chart.H_SLICE] = _complex_generator_real_chart(
            vector
        )

        sigma = np.empty(
            (chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM), dtype=complex
        )
        for column, basis_form in enumerate(sigma_basis):
            variation = direct.generator_action(basis_form, first, second)
            sigma[:, column] = chart.sigma_coordinates(variation)
        generator[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = (
            _complex_generator_real_chart(sigma)
        )

        generator.setflags(write=False)
        generators.append(generator)
    return tuple(generators)


def so10_generator_matrices() -> tuple[np.ndarray, ...]:
    """Return copies of the 45 canonical SO(10) generator matrices."""
    return tuple(matrix.copy() for matrix in _so10_generator_matrices_cached())


def physical_hierarchy_state() -> potential.FieldState:
    """Reproduce the canonical GUT/intermediate/EW/Phi17 hierarchy state."""
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        raise RuntimeError("unification anchor is unavailable")
    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    h[6] = 174.0 / m_gut
    return potential.FieldState(
        phi=direct.scale_form(direct.singlet_basis()["p"], 1.0),
        h=h,
        sigma=direct.scale_form(direct.delta_r(), m_i / m_gut),
        s=complex(m_i / m_gut),
        x=complex(1.0e17 / m_gut),
    ).validated()


def _physical_hierarchy_metadata(state: potential.FieldState) -> dict[str, Any]:
    anchor = scalar_pd._unification_anchor()
    q = chart.pack(state)
    return {
        "source": "canonical physical hierarchy used by the existing G3 bridge",
        "M_GUT_GeV": float(anchor["M_GUT_GeV"]),
        "M_I_GeV": float(anchor["M_I_GeV"]),
        "h_EW_GeV": 174.0,
        "Phi17_scale_GeV": 1.0e17,
        "coordinate_shape": list(q.shape),
        "coordinate_norm": float(np.linalg.norm(q)),
        "block_norms": {
            "Phi210": float(np.linalg.norm(q[chart.PHI_SLICE])),
            "H10": float(np.linalg.norm(q[chart.H_SLICE])),
            "Sigma126bar": float(np.linalg.norm(q[chart.SIGMA_SLICE])),
            "S": float(np.linalg.norm(q[chart.S_SLICE])),
            "Phi17": float(np.linalg.norm(q[chart.X_SLICE])),
        },
    }


def _adapter_modules_by_family() -> dict[str, Any]:
    output: dict[str, Any] = {}
    for _adapter_name, families, adapter in g2.ADAPTERS:
        module = importlib.import_module(adapter.__module__)
        if not callable(getattr(module, "direction_derivative", None)):
            raise AttributeError(
                f"{adapter.__module__} has no callable direction_derivative"
            )
        for family in families:
            if family in output:
                raise AssertionError(f"multiple exact G2 adapters own {family}")
            output[family] = module
    return output


def _dense_shape_audit(rows: Iterable[Any], *, id_attribute: str) -> dict[str, Any]:
    per_row: dict[str, Any] = {}
    bad_value_shapes: list[str] = []
    bad_gradient_shapes: list[str] = []
    bad_hessian_shapes: list[str] = []
    nonfinite: list[str] = []
    asymmetry: dict[str, float] = {}
    for row in rows:
        row_id = str(getattr(row, id_attribute))
        value = np.asarray(row.value)
        gradient = np.asarray(row.gradient)
        hessian = np.asarray(row.hessian)
        if value.shape != ():
            bad_value_shapes.append(row_id)
        if gradient.shape != (chart.TOTAL_DIM,):
            bad_gradient_shapes.append(row_id)
        if hessian.shape != (chart.TOTAL_DIM, chart.TOTAL_DIM):
            bad_hessian_shapes.append(row_id)
        finite = bool(
            np.all(np.isfinite(value.real))
            and np.all(np.isfinite(value.imag))
            and np.all(np.isfinite(gradient.real))
            and np.all(np.isfinite(gradient.imag))
            and np.all(np.isfinite(hessian.real))
            and np.all(np.isfinite(hessian.imag))
        )
        if not finite:
            nonfinite.append(row_id)
        hessian_asymmetry = (
            float(np.max(np.abs(hessian - hessian.T), initial=0.0))
            if hessian.shape == (chart.TOTAL_DIM, chart.TOTAL_DIM)
            else float("inf")
        )
        asymmetry[row_id] = hessian_asymmetry
        per_row[row_id] = {
            "value_shape": list(value.shape),
            "gradient_shape": list(gradient.shape),
            "Hessian_shape": list(hessian.shape),
            "finite": finite,
            "Hessian_max_abs_asymmetry": hessian_asymmetry,
        }
    return {
        "row_count": len(per_row),
        "bad_value_shapes": bad_value_shapes,
        "bad_gradient_shapes": bad_gradient_shapes,
        "bad_Hessian_shapes": bad_hessian_shapes,
        "nonfinite_rows": nonfinite,
        "maximum_Hessian_asymmetry": max(asymmetry.values(), default=0.0),
        "per_row": per_row,
    }


def _normalized_rank(
    matrix: np.ndarray, *, analytically_zero_columns: Iterable[int] = ()
) -> dict[str, Any]:
    value = np.asarray(matrix, dtype=float).copy()
    zeroed = tuple(sorted(set(int(index) for index in analytically_zero_columns)))
    if zeroed:
        value[:, list(zeroed)] = 0.0
    norms = np.linalg.norm(value, axis=0)
    active = norms > 0.0
    normalized = value[:, active] / norms[active] if np.any(active) else value[:, :0]
    singular = (
        np.linalg.svd(normalized, compute_uv=False)
        if normalized.size
        else np.asarray([], dtype=float)
    )
    threshold = (
        NORMALIZED_RANK_TOLERANCE * float(singular[0]) if singular.size else 0.0
    )
    rank = int(np.sum(singular > threshold))
    return {
        "rank": rank,
        "nullity_in_full_parameter_space": int(value.shape[1] - rank),
        "active_column_count": int(np.sum(active)),
        "zero_column_count": int(np.sum(~active)),
        "column_norms": norms,
        "minimum_active_column_norm": (
            float(np.min(norms[active])) if np.any(active) else 0.0
        ),
        "maximum_column_norm": float(np.max(norms, initial=0.0)),
        "singular_values": singular,
        "relative_singular_value_tolerance": NORMALIZED_RANK_TOLERANCE,
        "singular_value_threshold": threshold,
        "active_mask": active,
        "normalized_matrix": normalized,
        "matrix_after_analytic_zero_promotion": value,
        "analytically_zeroed_column_indices": zeroed,
    }


def _ward_audit(
    direction_rows: tuple[derivatives.DirectionDerivative, ...],
    parameter_rows: tuple[derivatives.ParameterDerivative, ...],
    state: potential.FieldState,
) -> dict[str, Any]:
    q = chart.pack(state)
    generator = _u1x_generator_matrix_cached()
    tangent = generator @ q
    tangent_norm = float(np.linalg.norm(tangent))
    tiny = np.finfo(float).tiny

    so10_orbit = chart.gauge_orbit_matrix(state)
    so10_generators = _so10_generator_matrices_cached()
    so10_matrix_orbit = np.column_stack(
        [generator @ q for generator in so10_generators]
    )
    so10_norms = np.linalg.norm(so10_orbit, axis=0)
    so10_active = so10_norms > 0.0
    so10_unit = so10_orbit[:, so10_active] / so10_norms[so10_active]
    so10_singular = np.linalg.svd(so10_unit, compute_uv=False)
    so10_rank = int(
        np.sum(so10_singular > NORMALIZED_RANK_TOLERANCE * so10_singular[0])
    )

    def row_residual(row: Any) -> dict[str, float]:
        gradient = np.asarray(row.gradient)
        hessian = np.asarray(row.hessian)
        gradient_norm = float(np.linalg.norm(gradient))
        hessian_norm = float(np.linalg.norm(hessian, ord="fro"))
        u1x_first_abs = float(abs(np.dot(gradient, tangent)))
        u1x_first_relative = u1x_first_abs / max(
            gradient_norm * tangent_norm, tiny
        )
        differentiated = hessian @ tangent + generator.T @ gradient
        differentiated_abs = float(np.linalg.norm(differentiated))
        differentiated_relative = differentiated_abs / max(
            hessian_norm * tangent_norm
            + max(abs(charge) for charge in U1X_CHARGES.values()) * gradient_norm,
            tiny,
        )
        so10_projection = so10_unit.T @ gradient
        so10_abs = float(np.max(np.abs(so10_projection), initial=0.0))
        so10_relative = so10_abs / max(gradient_norm, tiny)
        so10_differentiated = hessian @ so10_orbit + np.column_stack(
            [generator.T @ gradient for generator in so10_generators]
        )
        so10_differentiated_norms = np.linalg.norm(
            so10_differentiated, axis=0
        )
        # A p-form SO(10) generator has operator norm no larger than p in
        # this direct tensor realization; the largest matter block is the
        # chiral five-form Sigma representation.
        so10_differentiated_scales = (
            hessian_norm * so10_norms + 5.0 * gradient_norm
        )
        so10_differentiated_relative = float(
            np.max(
                so10_differentiated_norms
                / np.maximum(so10_differentiated_scales, tiny),
                initial=0.0,
            )
        )
        return {
            "gradient_norm": gradient_norm,
            "Hessian_frobenius_norm": hessian_norm,
            "U1X_first_Ward_abs_residual": u1x_first_abs,
            "U1X_first_Ward_relative_residual": u1x_first_relative,
            "U1X_differentiated_Ward_abs_residual": differentiated_abs,
            "U1X_differentiated_Ward_relative_residual": differentiated_relative,
            "SO10_first_Ward_abs_residual": so10_abs,
            "SO10_first_Ward_relative_residual": so10_relative,
            "SO10_differentiated_Ward_max_abs_residual": float(
                np.max(so10_differentiated_norms, initial=0.0)
            ),
            "SO10_differentiated_Ward_max_relative_residual": (
                so10_differentiated_relative
            ),
        }

    direction = {row.direction_id: row_residual(row) for row in direction_rows}
    parameter = {row.parameter_id: row_residual(row) for row in parameter_rows}

    def maximum(field: str, rows: dict[str, dict[str, float]]) -> float:
        return max((entry[field] for entry in rows.values()), default=0.0)

    return {
        "U1X_generator": {
            "shape": list(generator.shape),
            "charges": U1X_CHARGES,
            "antisymmetry_max_abs_residual": float(
                np.max(np.abs(generator + generator.T), initial=0.0)
            ),
            "Phi210_block_max_abs_entry": float(
                np.max(np.abs(generator[chart.PHI_SLICE, :]), initial=0.0)
            ),
            "nonzero_matrix_entries": int(np.count_nonzero(generator)),
        },
        "U1X_tangent": {
            "shape": list(tangent.shape),
            "norm": tangent_norm,
            "block_norms": {
                "Phi210": float(np.linalg.norm(tangent[chart.PHI_SLICE])),
                "H10": float(np.linalg.norm(tangent[chart.H_SLICE])),
                "Sigma126bar": float(np.linalg.norm(tangent[chart.SIGMA_SLICE])),
                "S": float(np.linalg.norm(tangent[chart.S_SLICE])),
                "Phi17": float(np.linalg.norm(tangent[chart.X_SLICE])),
            },
        },
        "SO10_orbit": {
            "shape": list(so10_orbit.shape),
            "nonzero_columns": int(np.sum(so10_active)),
            "column_normalized_rank_diagnostic": so10_rank,
            "generator_count": len(so10_generators),
            "maximum_generator_antisymmetry_residual": max(
                float(np.max(np.abs(generator + generator.T), initial=0.0))
                for generator in so10_generators
            ),
            "generator_action_max_abs_residual": float(
                np.max(np.abs(so10_matrix_orbit - so10_orbit), initial=0.0)
            ),
            "rank_is_not_a_G3_claim": True,
        },
        "maximum_direction_U1X_first_Ward_relative_residual": maximum(
            "U1X_first_Ward_relative_residual", direction
        ),
        "maximum_direction_U1X_differentiated_Ward_relative_residual": maximum(
            "U1X_differentiated_Ward_relative_residual", direction
        ),
        "maximum_direction_SO10_first_Ward_relative_residual": maximum(
            "SO10_first_Ward_relative_residual", direction
        ),
        "maximum_direction_SO10_differentiated_Ward_relative_residual": maximum(
            "SO10_differentiated_Ward_max_relative_residual", direction
        ),
        "maximum_parameter_U1X_first_Ward_relative_residual": maximum(
            "U1X_first_Ward_relative_residual", parameter
        ),
        "maximum_parameter_U1X_differentiated_Ward_relative_residual": maximum(
            "U1X_differentiated_Ward_relative_residual", parameter
        ),
        "maximum_parameter_SO10_first_Ward_relative_residual": maximum(
            "SO10_first_Ward_relative_residual", parameter
        ),
        "maximum_parameter_SO10_differentiated_Ward_relative_residual": maximum(
            "SO10_differentiated_Ward_max_relative_residual", parameter
        ),
        "per_direction": direction,
        "per_parameter": parameter,
    }


def _stationary_hessian_audit(
    parameter_rows: tuple[derivatives.ParameterDerivative, ...],
    tangent: np.ndarray,
    generator: np.ndarray,
    state: potential.FieldState,
) -> dict[str, Any]:
    raw_matrix = np.column_stack([row.gradient for row in parameter_rows])
    sigma_zero_certificate = exact_delta_r_projector_zero_certificate()
    phi_certificate = exact_phi_projector_and_stationary_witness_certificate()
    rank_lower_bound = exact_stationarity_rank_lower_bound_certificate()
    exact_rank_certificate = exact_rank_source.build_report()
    compiler_minor_binding = exact_rank_source.compiler_minor_binding(
        parameter_rows, state
    )
    exact_informed_constraints = (
        exact_rank_source.exact_informed_stationarity_constraints(
            parameter_rows, include_arrays=False
        )
    )
    exact_rank_certified = bool(
        exact_rank_certificate["certified"]
        and compiler_minor_binding["certified"]
    )
    all_zero_certificates_present = bool(
        sigma_zero_certificate["certified"]
        and phi_certificate["certified"]
        and phi_certificate["O44_B03_210_gradient_zero"]["certified"]
    )
    by_id = {row.parameter_id: index for index, row in enumerate(parameter_rows)}
    missing_analytic_ids = sorted(
        set(ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS).difference(by_id)
    )
    analytic_indices = (
        tuple(
            by_id[parameter_id]
            for parameter_id in ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS
            if parameter_id in by_id
        )
        if all_zero_certificates_present
        else ()
    )
    raw_rank = _normalized_rank(raw_matrix)
    promoted_rank = _normalized_rank(
        raw_matrix, analytically_zero_columns=analytic_indices
    )
    promoted_matrix = np.asarray(
        promoted_rank["matrix_after_analytic_zero_promotion"], dtype=float
    )
    analytic_raw_norms = {
        parameter_rows[index].parameter_id: float(np.linalg.norm(raw_matrix[:, index]))
        for index in analytic_indices
    }

    rank = int(promoted_rank["rank"])
    coefficient = np.zeros(len(parameter_rows), dtype=float)
    witness_coefficients = {
        "lambda::O07_B01_Phi_norm": 10.0,
        "lambda::O48_B01_Phi_self_quartics": 1.0,
        "lambda::O48_B02_Phi_self_quartics": -0.25,
    }
    missing_witness_ids = sorted(set(witness_coefficients).difference(by_id))
    for parameter_id, value in witness_coefficients.items():
        if parameter_id in by_id:
            coefficient[by_id[parameter_id]] = value
    coefficient_scale = float(np.max(np.abs(coefficient), initial=0.0))
    witness_source = "exact_rational_Phi_stationary_witness"

    promoted_gradient = promoted_matrix @ coefficient
    raw_gradient = raw_matrix @ coefficient
    promoted_relative_residual = float(
        np.linalg.norm(promoted_gradient)
        / max(
            np.linalg.norm(promoted_matrix, ord="fro")
            * np.linalg.norm(coefficient),
            np.finfo(float).tiny,
        )
    )
    component_envelope = np.sum(
        np.abs(raw_matrix) * np.abs(coefficient)[None, :], axis=1
    )
    mixed_tolerance = (
        ANALYTIC_ZERO_GRADIENT_ATOL + STATIONARITY_RTOL * component_envelope
    )
    mixed_ratios = np.abs(raw_gradient) / mixed_tolerance
    maximum_mixed_ratio = float(np.max(mixed_ratios, initial=0.0))

    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for row, value in zip(parameter_rows, coefficient, strict=True):
        if value != 0.0:
            hessian += value * np.asarray(row.hessian, dtype=float)
    hessian = 0.5 * (hessian + hessian.T)
    compiled_p24_binding = _compiled_stationary_witness_p24_binding(
        parameter_rows, hessian
    )
    hessian_norm = float(np.linalg.norm(hessian, ord="fro"))
    tangent_norm = float(np.linalg.norm(tangent))
    reduced_residual = hessian @ tangent
    reduced_abs = float(np.linalg.norm(reduced_residual))
    reduced_relative = reduced_abs / max(
        hessian_norm * tangent_norm, np.finfo(float).tiny
    )
    full_differentiated = reduced_residual + generator.T @ raw_gradient
    full_differentiated_relative = float(
        np.linalg.norm(full_differentiated)
        / max(
            hessian_norm * tangent_norm
            + max(abs(charge) for charge in U1X_CHARGES.values())
            * np.linalg.norm(raw_gradient),
            np.finfo(float).tiny,
        )
    )
    support = {
        row.parameter_id: float(value)
        for row, value in zip(parameter_rows, coefficient, strict=True)
        if abs(value) > 1.0e-12
    }
    stationarity_applicable = bool(
        not missing_witness_ids
        and phi_certificate["stationary_witness"]["gradient_exactly_zero"]
        and compiled_p24_binding["certified"]
        and coefficient_scale > 0.0
        and promoted_relative_residual < WARD_RELATIVE_TOLERANCE
        and maximum_mixed_ratio <= 1.0
    )
    return {
        "purpose": (
            "nonzero stationary witness solely for the U1X stationary-Hessian "
            "Ward identity; not a G3 stability or vacuum certificate"
        ),
        "raw_dense_rank_diagnostic": {
            "rank": raw_rank["rank"],
            "nullity": raw_rank["nullity_in_full_parameter_space"],
            "active_columns": raw_rank["active_column_count"],
            "minimum_active_column_norm": raw_rank["minimum_active_column_norm"],
            "maximum_column_norm": raw_rank["maximum_column_norm"],
            "singular_values": raw_rank["singular_values"],
            "threshold": raw_rank["singular_value_threshold"],
            "certified": False,
            "note": (
                "Unit-normalizing floating cancellation residues creates the raw "
                "rank-14 direction. Exact Z[i]/integer projector certificates "
                "prove that all three named source columns are identically zero."
            ),
        },
        "analytic_zero_promotion": {
            "parameter_ids": list(ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS),
            "missing_parameter_ids": missing_analytic_ids,
            "raw_gradient_norms": analytic_raw_norms,
            "absolute_zero_tolerance": ANALYTIC_ZERO_GRADIENT_ATOL,
            "all_raw_residues_below_legacy_absolute_zero_tolerance": all(
                value <= ANALYTIC_ZERO_GRADIENT_ATOL
                for value in analytic_raw_norms.values()
            )
            and not missing_analytic_ids,
            "raw_residue_magnitudes_are_not_used_for_zero_promotion": True,
            "symbolic_exact_zero_proof_present": all_zero_certificates_present,
            "certification_scope": (
                "exact Gaussian-integer pair-Casimir proof for the 54 and "
                "1050bar Sigma-self pairs plus an exact integer/rational proof "
                "for the mixed Phi-Sigma 210 channel"
            ),
            "scope": "first variations at the pure Delta_R hierarchy state only",
            "exact_projector_zero_certificate": sigma_zero_certificate,
            "exact_phi_210_gradient_zero_certificate": phi_certificate[
                "O44_B03_210_gradient_zero"
            ],
            "exact_phi_projector_and_witness_certificate": phi_certificate,
        },
        "promoted_stationarity_matrix": {
            "shape": list(promoted_matrix.shape),
            "rank": rank,
            "nullity": promoted_rank["nullity_in_full_parameter_space"],
            "active_columns": promoted_rank["active_column_count"],
            "zero_columns": promoted_rank["zero_column_count"],
            "minimum_active_column_norm": promoted_rank[
                "minimum_active_column_norm"
            ],
            "maximum_column_norm": promoted_rank["maximum_column_norm"],
            "singular_values": promoted_rank["singular_values"],
            "relative_singular_value_tolerance": NORMALIZED_RANK_TOLERANCE,
            "threshold": promoted_rank["singular_value_threshold"],
            "exact_projector_zero_corrected_normalized_SVD_rank_13": bool(
                all_zero_certificates_present
                and rank == EXPECTED_PROMOTED_STATIONARITY_RANK
                and promoted_rank["nullity_in_full_parameter_space"]
                == EXPECTED_PROMOTED_STATIONARITY_NULLITY
            ),
            "exact_rank_lower_bound": rank_lower_bound[
                "certified_rank_lower_bound"
            ],
            "exact_nonzero_13x13_minor_certified": rank_lower_bound[
                "determinant_nonzero"
            ],
            "exact_rank_lower_bound_certificate": rank_lower_bound,
            "numerical_rank_upper_diagnostic": rank,
            "exact_rank_upper_bound": exact_rank_certificate[
                "rank_upper_certificate"
            ]["rank_upper_bound"],
            "exact_rank_upper_bound_certified": exact_rank_certified,
            "stationarity_rank_13_exactly_certified": exact_rank_certified,
            "stationarity_nullity_38_exactly_certified": exact_rank_certified,
            "exact_rank_certificate_missing": not exact_rank_certified,
            "exact_rank_13_nullity_38_certificate": exact_rank_certificate,
            "exact_compiler_minor_binding": compiler_minor_binding,
            "exact_informed_13_row_constraint_representation": (
                exact_informed_constraints
            ),
            "certification_note": (
                "The exact symmetry/Ward factorization A=L A[pivots,:] proves "
                "rank <= 13 for all 486 rows. The exact nonzero 13x13 minor "
                "proves rank >= 13, and its 169 entries are bound by coordinate "
                "and parameter ID to the actual compiler gradients. Therefore "
                "rank/nullity are exactly 13/38; float64 SVD is diagnostic only."
            ),
        },
        "witness_source": witness_source,
        "witness_missing_parameter_ids": missing_witness_ids,
        "exact_stationary_witness_certificate": phi_certificate[
            "stationary_witness"
        ],
        "exact_P24_trace_dense_compiler_binding": compiled_p24_binding,
        "witness_support_at_1e-12": support,
        "witness_nonzero_support_count": len(support),
        "promoted_stationarity_relative_residual": promoted_relative_residual,
        "raw_dense_stationarity_max_abs_residual": float(
            np.max(np.abs(raw_gradient), initial=0.0)
        ),
        "raw_dense_stationarity_mixed_atol": ANALYTIC_ZERO_GRADIENT_ATOL,
        "raw_dense_stationarity_mixed_rtol": STATIONARITY_RTOL,
        "raw_dense_stationarity_maximum_mixed_tolerance_ratio": maximum_mixed_ratio,
        "stationary_Hessian_Ward_applicable": stationarity_applicable,
        "stationary_Hessian_U1X_abs_residual": reduced_abs,
        "stationary_Hessian_U1X_relative_residual": reduced_relative,
        "full_differentiated_U1X_relative_residual": full_differentiated_relative,
        "Hessian_frobenius_norm": hessian_norm,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    started = time.perf_counter()
    contract_rows, contract_parameter_ids, contract_report = (
        _contract_selection_cached()
    )
    selected_direction_ids = tuple(
        str(row["direction_id"]) for row in contract_rows
    )
    selected_direction_id_set = set(selected_direction_ids)
    state = physical_hierarchy_state()
    q = chart.pack(state)

    value_started = time.perf_counter()
    all_live_directions = potential.evaluate_directions(state)
    value_seconds = time.perf_counter() - value_started
    all_live_ids = [row.direction_id for row in all_live_directions]
    live_by_id = {row.direction_id: row for row in all_live_directions}
    missing_direction_ids = sorted(selected_direction_id_set.difference(live_by_id))
    duplicate_live_ids = sorted(
        {direction_id for direction_id in all_live_ids if all_live_ids.count(direction_id) > 1}
    )
    if missing_direction_ids:
        raise KeyError(f"gauged directions absent from exact compiler: {missing_direction_ids}")
    selected_live_directions = tuple(
        live_by_id[direction_id] for direction_id in selected_direction_ids
    )

    owners = _adapter_modules_by_family()
    derivative_started = time.perf_counter()
    direction_rows = tuple(
        owners[row.base_family].direction_derivative(q, row)
        for row in selected_live_directions
    )
    derivative_seconds = time.perf_counter() - derivative_started
    parameter_rows = derivatives.parameter_derivatives(direction_rows)
    observed_parameter_ids = tuple(row.parameter_id for row in parameter_rows)

    direction_shapes = _dense_shape_audit(
        direction_rows, id_attribute="direction_id"
    )
    parameter_shapes = _dense_shape_audit(
        parameter_rows, id_attribute="parameter_id"
    )
    value_lookup = {row.direction_id: row.value for row in selected_live_directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - value_lookup[row.direction_id]))
        for row in direction_rows
    }
    live_parameter_values = potential.coefficient_jacobian(selected_live_directions)
    parameter_value_residuals = {
        row.parameter_id: float(
            abs(row.value - live_parameter_values[row.parameter_id])
        )
        for row in parameter_rows
    }

    contract_by_id = {str(row["direction_id"]): row for row in contract_rows}
    neutrality_rows: dict[str, Any] = {}
    for row in selected_live_directions:
        independent_charge = census.charge(row.counts)
        declared_charge = contract_by_id[row.direction_id]["charge"]
        neutrality_rows[row.direction_id] = {
            "independent_exact_X_charge": int(independent_charge["X"]),
            "contract_exact_X_charge": int(declared_charge["X"]),
            "exactly_X_neutral": independent_charge["X"] == declared_charge["X"] == 0,
        }

    ward = _ward_audit(direction_rows, parameter_rows, state)
    tangent = _u1x_generator_matrix_cached() @ q
    stationary = _stationary_hessian_audit(
        parameter_rows, tangent, _u1x_generator_matrix_cached(), state
    )
    sigma_zero_certificate = stationary["analytic_zero_promotion"][
        "exact_projector_zero_certificate"
    ]
    phi_certificate = stationary["analytic_zero_promotion"][
        "exact_phi_projector_and_witness_certificate"
    ]
    certified_parameter_ids = set(
        sigma_zero_certificate["gradient_implication"][
            "certified_parameter_ids"
        ]
    )
    certified_parameter_ids.add(
        phi_certificate["O44_B03_210_gradient_zero"]["parameter_id"]
    )
    contract_parameter_channel_map = {
        parameter_id: str(row["basis_label"])
        for row in contract_rows
        for parameter_id in row["parameter_ids"]
        if parameter_id in certified_parameter_ids
    }

    checks = {
        "upstream_scalar_contract_integrity_passes": contract_report["n_failed"] == 0,
        "model_contract_id_is_gauged_u1x_phi17_v20": (
            contract_report["model_contract_id"] == MODEL_CONTRACT_ID
        ),
        "selected_direction_count_is_44": len(direction_rows)
        == EXPECTED_DIRECTION_COUNT,
        "selected_parameter_count_is_51": len(parameter_rows)
        == EXPECTED_PARAMETER_COUNT,
        "canonical_real_field_dimension_is_486": chart.TOTAL_DIM
        == EXPECTED_REAL_FIELD_DIMENSION,
        "selected_direction_ids_equal_contract_in_order": tuple(
            row.direction_id for row in direction_rows
        )
        == selected_direction_ids,
        "selected_parameter_ids_equal_contract_in_order": observed_parameter_ids
        == contract_parameter_ids,
        "all_18_families_have_exact_adapter_owners": (
            len({row.base_family for row in selected_live_directions}) == 18
            and set(row.base_family for row in selected_live_directions).issubset(owners)
        ),
        "full_compiler_direction_ids_are_unique": not duplicate_live_ids,
        "all_44_direction_values_are_scalars": not direction_shapes[
            "bad_value_shapes"
        ],
        "all_44_direction_gradients_have_shape_486": not direction_shapes[
            "bad_gradient_shapes"
        ],
        "all_44_direction_Hessians_have_shape_486x486": not direction_shapes[
            "bad_Hessian_shapes"
        ],
        "all_44_direction_derivatives_are_finite": not direction_shapes[
            "nonfinite_rows"
        ],
        "all_44_direction_Hessians_are_symmetric": direction_shapes[
            "maximum_Hessian_asymmetry"
        ]
        < HESSIAN_SYMMETRY_ATOL,
        "all_51_parameter_values_are_scalars": not parameter_shapes[
            "bad_value_shapes"
        ],
        "all_51_parameter_gradients_have_shape_486": not parameter_shapes[
            "bad_gradient_shapes"
        ],
        "all_51_parameter_Hessians_have_shape_486x486": not parameter_shapes[
            "bad_Hessian_shapes"
        ],
        "all_51_parameter_derivatives_are_finite": not parameter_shapes[
            "nonfinite_rows"
        ],
        "all_51_parameter_Hessians_are_symmetric": parameter_shapes[
            "maximum_Hessian_asymmetry"
        ]
        < HESSIAN_SYMMETRY_ATOL,
        "all_direction_values_match_exact_live_evaluator": max(
            value_residuals.values(), default=0.0
        )
        < VALUE_ATOL,
        "all_parameter_values_match_exact_live_evaluator": max(
            parameter_value_residuals.values(), default=0.0
        )
        < VALUE_ATOL,
        "every_selected_direction_is_independently_exact_X_neutral": all(
            row["exactly_X_neutral"] for row in neutrality_rows.values()
        ),
        "U1X_generator_is_486x486_and_antisymmetric": (
            ward["U1X_generator"]["shape"] == [486, 486]
            and ward["U1X_generator"]["antisymmetry_max_abs_residual"] == 0.0
        ),
        "U1X_tangent_is_nonzero_and_Phi210_neutral": (
            ward["U1X_tangent"]["norm"] > 0.0
            and ward["U1X_tangent"]["block_norms"]["Phi210"] == 0.0
        ),
        "all_44_direction_first_U1X_Ward_identities_pass": ward[
            "maximum_direction_U1X_first_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "all_44_direction_differentiated_U1X_Ward_identities_pass": ward[
            "maximum_direction_U1X_differentiated_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "all_44_direction_first_SO10_Ward_identities_pass": ward[
            "maximum_direction_SO10_first_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "SO10_generator_matrices_reproduce_the_orbit": (
            ward["SO10_orbit"]["generator_count"] == 45
            and ward["SO10_orbit"]["maximum_generator_antisymmetry_residual"]
            < WARD_RELATIVE_TOLERANCE
            and ward["SO10_orbit"]["generator_action_max_abs_residual"]
            < WARD_RELATIVE_TOLERANCE
        ),
        "all_44_direction_differentiated_SO10_Ward_identities_pass": ward[
            "maximum_direction_SO10_differentiated_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "all_51_parameter_first_U1X_Ward_identities_pass": ward[
            "maximum_parameter_U1X_first_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "all_51_parameter_differentiated_U1X_Ward_identities_pass": ward[
            "maximum_parameter_U1X_differentiated_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "all_51_parameter_first_SO10_Ward_identities_pass": ward[
            "maximum_parameter_SO10_first_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "all_51_parameter_differentiated_SO10_Ward_identities_pass": ward[
            "maximum_parameter_SO10_differentiated_Ward_relative_residual"
        ]
        < WARD_RELATIVE_TOLERANCE,
        "exact_three_projector_zero_gradient_certificates_pass": (
            sigma_zero_certificate["n_failed"] == 0
            and sigma_zero_certificate["certified"]
            and phi_certificate["n_failed"] == 0
            and phi_certificate["certified"]
            and phi_certificate["O44_B03_210_gradient_zero"]["certified"]
        ),
        "exact_Sigma_basis_and_Delta_R_conventions_match_live_compiler_chart": (
            sigma_zero_certificate["compiler_chart_convention_binding"][
                "certified"
            ]
        ),
        "all_exact_Phi_int64_matrix_operations_have_preflight_bounds": (
            phi_certificate["integer_arithmetic_safety"]["certified"]
        ),
        "exact_zero_parameter_channel_map_matches_gauged_contract": (
            contract_parameter_channel_map
            == {
                **sigma_zero_certificate["parameter_channel_map"],
                phi_certificate["O44_B03_210_gradient_zero"][
                    "parameter_id"
                ]: "210",
            }
        ),
        "analytic_zero_promotion_uses_proofs_not_magnitude_thresholds": stationary[
            "analytic_zero_promotion"
        ]["raw_residue_magnitudes_are_not_used_for_zero_promotion"],
        "exact_projector_zero_corrected_normalized_SVD_rank_is_13": stationary[
            "promoted_stationarity_matrix"
        ]["rank"]
        == EXPECTED_PROMOTED_STATIONARITY_RANK,
        "exact_projector_zero_corrected_normalized_SVD_nullity_is_38": stationary[
            "promoted_stationarity_matrix"
        ]["nullity"]
        == EXPECTED_PROMOTED_STATIONARITY_NULLITY,
        "stationarity_rank_13_is_exactly_certified": stationary[
            "promoted_stationarity_matrix"
        ]["stationarity_rank_13_exactly_certified"],
        "exact_nonzero_13x13_minor_proves_rank_at_least_13": (
            stationary["promoted_stationarity_matrix"][
                "exact_nonzero_13x13_minor_certified"
            ]
            and stationary["promoted_stationarity_matrix"][
                "exact_rank_lower_bound"
            ]
            == 13
        ),
        "exact_rank_upper_bound_13_factorization_is_certified": stationary[
            "promoted_stationarity_matrix"
        ]["exact_rank_upper_bound_certified"],
        "compiler_gradients_are_bound_to_the_exact_nonzero_13x13_minor": stationary[
            "promoted_stationarity_matrix"
        ]["exact_compiler_minor_binding"]["certified"],
        "exact_informed_13_row_constraints_are_well_conditioned": stationary[
            "promoted_stationarity_matrix"
        ]["exact_informed_13_row_constraint_representation"]["certified"],
        "exact_rational_stationary_witness_matches_dense_gradient": (
            stationary["witness_source"]
            == "exact_rational_Phi_stationary_witness"
            and stationary["raw_dense_stationarity_max_abs_residual"] == 0.0
            and stationary["exact_stationary_witness_certificate"][
                "P24_trace"
            ]
            == 288
        ),
        "exact_P24_trace_288_is_bound_to_compiled_dense_Hessian": stationary[
            "exact_P24_trace_dense_compiler_binding"
        ]["certified"],
        "nonzero_stationary_witness_passes_mixed_tadpole_tolerance": (
            stationary["witness_nonzero_support_count"] > 0
            and stationary[
                "raw_dense_stationarity_maximum_mixed_tolerance_ratio"
            ]
            <= 1.0
        ),
        "stationary_Hessian_U1X_Ward_identity_passes_when_applicable": (
            stationary["stationary_Hessian_Ward_applicable"]
            and stationary["stationary_Hessian_U1X_relative_residual"]
            < WARD_RELATIVE_TOLERANCE
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    elapsed = time.perf_counter() - started
    return _jsonable(
        {
            "model_contract_id": MODEL_CONTRACT_ID,
            "status": (
                "GAUGED_U1X_G2_DERIVATIVE_AUDIT_PASSED__G3_OPEN"
                if not failures
                else "GAUGED_U1X_G2_DERIVATIVE_AUDIT_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "authoritative_for_manuscript_G2_scalar_contract": True,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "counts": {
                "invariant_directions": len(direction_rows),
                "real_parameters": len(parameter_rows),
                "base_tensor_families": len(
                    {row.base_family for row in selected_live_directions}
                ),
                "real_field_dimension": chart.TOTAL_DIM,
                "gradient_entries_per_parameter": chart.TOTAL_DIM,
                "Hessian_shape_per_parameter": [chart.TOTAL_DIM, chart.TOTAL_DIM],
                "symmetric_Hessian_entries_per_parameter": chart.SYMMETRIC_HESSIAN_ENTRIES,
            },
            "selection": {
                "source": "gauged_u1x_scalar_contract_v20.build_report",
                "direction_ids": list(selected_direction_ids),
                "parameter_ids": list(observed_parameter_ids),
                "excluded_historical_direction_count": len(all_live_directions)
                - len(direction_rows),
            },
            "physical_hierarchy_state": _physical_hierarchy_metadata(state),
            "exact_X_neutrality": neutrality_rows,
            "exact_value_crosscheck": {
                "maximum_direction_value_abs_residual": max(
                    value_residuals.values(), default=0.0
                ),
                "maximum_parameter_value_abs_residual": max(
                    parameter_value_residuals.values(), default=0.0
                ),
                "per_direction": value_residuals,
                "per_parameter": parameter_value_residuals,
            },
            "direction_dense_shape_finiteness_symmetry": direction_shapes,
            "parameter_dense_shape_finiteness_symmetry": parameter_shapes,
            "Ward_identities": ward,
            "stationary_Hessian_bridge": stationary,
            "upstream_contract_implementation_note": {
                "implementation_matches_manuscript": contract_report[
                    "implementation_matches_manuscript"
                ],
                "implementation_mismatches": contract_report[
                    "implementation_mismatches"
                ],
            },
            "performance": {
                "heavy_generation_required": True,
                "exact_value_evaluation_seconds": value_seconds,
                "exact_dense_derivative_evaluation_seconds": derivative_seconds,
                "total_seconds": elapsed,
            },
            "flags": {
                "G2_gauged_u1x_derivatives_certified": not failures,
                "raw_dense_rank_14_is_certified": False,
                "exact_Delta_R_projector_zero_certificate": (
                    sigma_zero_certificate["certified"]
                ),
                "exact_three_structural_zero_gradient_certificates": bool(
                    sigma_zero_certificate["certified"]
                    and phi_certificate["certified"]
                ),
                "exact_Sigma_conventions_bound_to_live_compiler_chart": bool(
                    sigma_zero_certificate[
                        "compiler_chart_convention_binding"
                    ]["certified"]
                ),
                "exact_Phi_int64_preflight_safety_certified": bool(
                    phi_certificate["integer_arithmetic_safety"]["certified"]
                ),
                "exact_projector_zero_corrected_normalized_SVD_rank_13": bool(
                    not failures
                    and stationary["promoted_stationarity_matrix"][
                        "exact_projector_zero_corrected_normalized_SVD_rank_13"
                    ]
                ),
                "stationarity_rank_13_exactly_certified": bool(
                    stationary["promoted_stationarity_matrix"][
                        "stationarity_rank_13_exactly_certified"
                    ]
                ),
                "stationarity_nullity_38_exactly_certified": bool(
                    stationary["promoted_stationarity_matrix"][
                        "stationarity_nullity_38_exactly_certified"
                    ]
                ),
                "stationarity_rank_lower_bound_13_exactly_certified": bool(
                    stationary["promoted_stationarity_matrix"][
                        "exact_nonzero_13x13_minor_certified"
                    ]
                ),
                "stationarity_rank_upper_bound_13_exactly_certified": bool(
                    stationary["promoted_stationarity_matrix"][
                        "exact_rank_upper_bound_certified"
                    ]
                ),
                "stationarity_rank_upper_bound_13_only_numerical": False,
                "compiler_gradients_bound_to_exact_nonzero_13x13_minor": bool(
                    stationary["promoted_stationarity_matrix"][
                        "exact_compiler_minor_binding"
                    ]["certified"]
                ),
                "exact_informed_13_row_constraint_representation_ready": bool(
                    stationary["promoted_stationarity_matrix"][
                        "exact_informed_13_row_constraint_representation"
                    ]["certified"]
                ),
                "promoted_rank_13_numerical_policy_reproduced": False,
                "remaining_nonzero_columns_ranked_by_normalized_SVD": True,
                "exact_stationary_witness_regression_passes": bool(
                    stationary["raw_dense_stationarity_max_abs_residual"] == 0.0
                    and stationary[
                        "exact_P24_trace_dense_compiler_binding"
                    ]["certified"]
                ),
                "exact_P24_trace_288_bound_to_compiled_dense_Hessian": bool(
                    stationary["exact_P24_trace_dense_compiler_binding"][
                        "certified"
                    ]
                ),
                "stationary_witness_is_only_a_Ward_identity_bridge": True,
                "G3_closed": False,
                "joint_so10_u1x_rank_37_certified": False,
                "massive_quotient_dimension_448_certified": False,
                "current_fixed_vacuum_validated": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
            },
            "scientific_scope": (
                "This closes the dense derivative audit only for the exact-X-neutral "
                "44-direction/51-parameter scalar contract. The exact Z[i] "
                "pair-Casimir certificates prove the 54, 1050bar, and mixed-210 "
                "gradient columns vanish without applying a magnitude threshold. "
                "Their exact Sigma basis/Delta_R conventions are bound to the "
                "live chart, and every dense int64 projector operation is guarded "
                "by a Python-integer preflight bound. The exact P24 trace 288 is "
                "also bound entrywise to the actual compiled witness Hessian. "
                "A nonzero exact 13x13 minor bound entry-by-entry to the compiler "
                "proves stationarity rank >= 13. The exact stabilizer/Ward "
                "factorization A=L A[pivots,:] proves rank <= 13 across all 486 "
                "rows, hence rank/nullity are exactly 13/38. The normalized "
                "float64 SVD is retained only as a diagnostic. The exact "
                "rational stationary witness "
                "(10,1,-1/4) is used solely to test the U(1)_X Hessian Ward "
                "identity and to prevent reuse of an ill-scaled SVD nullspace. "
                "G3 still requires Hessian classification, boundedness, competing "
                "extrema, and global-vacuum analysis."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    counts = report["counts"]
    stationary = report["stationary_Hessian_bridge"]
    OUT_MD.write_text(
        "# Gauged U(1)_X G2 derivative audit - v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"- exact-X-neutral directions: `{counts['invariant_directions']}`\n"
        f"- real parameters: `{counts['real_parameters']}`\n"
        f"- real field coordinates: `{counts['real_field_dimension']}`\n"
        f"- promoted stationarity rank/nullity diagnostic: "
        f"`{stationary['promoted_stationarity_matrix']['rank']}/"
        f"{stationary['promoted_stationarity_matrix']['nullity']}`\n"
        f"- exact 54/1050bar/mixed-210 projector-zero certificates: "
        f"`{stationary['analytic_zero_promotion']['symbolic_exact_zero_proof_present']}`\n"
        f"- failed checks: `{report['n_failed']}`\n\n"
        + report["scientific_scope"]
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
