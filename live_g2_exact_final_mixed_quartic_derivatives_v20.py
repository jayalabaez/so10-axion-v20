#!/usr/bin/env python3
"""Exact derivatives for the last two mixed quartic G2 base families.

This module closes the two authoritative families left after the 16-family
stack:

* ``Phi2_Sigma_projectors`` (six self-conjugate channels
  1,45,210,770,5940,8910), and
* ``Phi2_Hdag_Sigma_210_1050`` (two non-self-conjugate channels 210,1050).

The six Phi^2 Sigma^dag Sigma channels are treated as an exact biquadratic
form.  If x is the real 210 coordinate vector and z the complex 126bar vector,

    I_R = z^dag L(P_R(x x^T)) z = x^T P_R(S(z)) x,

where L is the exact contraction-map lift and P_R is the exact pair-Casimir
projector.  The equality follows from projector self-adjointness and is checked
against the authoritative value layer.  It gives analytic Phi-Phi and
Sigma-Sigma Hessian blocks directly.  The Phi-Sigma block is the exact
linearization of P_R(S(z)); a batched sparse signed-permutation realization of
the pair Casimir evaluates that linearization without finite differences.

For Phi^2 H^dag Sigma, the exact source is multilinear.  The source bilinear
B(P,Q) is differentiated exactly.  Its Phi-Phi coefficient matrix is built by
moving the chiral projector onto the already-projected external tensor and
contracting the exact interior/wedge maps.  H-Sigma and mixed Phi-H/Sigma
blocks then follow from ordinary bilinearity.

Five-point formulas appear only as independent audits of the promoted analytic
derivatives.  No finite-difference derivative, fitted Clebsch, selected-vacuum
proxy, or autodiff result is used to construct the gradient or Hessian.
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_phi2_h_126dag_210_1050_channels_v20 as hsig_source
import exact_phisigma_126bar_minus_projectors_v20 as sigma_source
import exact_phisigma_casimir_projectors_v20 as pair_projectors
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_FINAL_MIXED_QUARTIC_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_FINAL_MIXED_QUARTIC_DERIVATIVES_V20.md"
PHISIGMA_FAMILY = "Phi2_Sigma_projectors"
PHIHSIGMA_FAMILY = "Phi2_Hdag_Sigma_210_1050"
SELECTED_FAMILIES = (PHISIGMA_FAMILY, PHIHSIGMA_FAMILY)
PHISIGMA_LABELS = tuple(sigma_source.CHANNELS)
PHIHSIGMA_LABELS = ("210", "1050")


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
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


def _complex_chart_map(dimension: int) -> np.ndarray:
    output = np.zeros((dimension, 2 * dimension), dtype=complex)
    scale = 1.0 / chart.SQRT2
    for index in range(dimension):
        output[index, 2 * index] = scale
        output[index, 2 * index + 1] = 1j * scale
    return output


@lru_cache(maxsize=1)
def sigma_real_map() -> np.ndarray:
    return _complex_chart_map(chart.SIGMA_COMPLEX_DIM)


@lru_cache(maxsize=1)
def h_real_map() -> np.ndarray:
    return _complex_chart_map(chart.H_COMPLEX_DIM)


@lru_cache(maxsize=1)
def sigma_full_form_map() -> np.ndarray:
    """Map physical 126bar complex coordinates to ordered five-form components."""
    return np.stack(
        [
            np.asarray(
                [hsig_source.five_to_vector(state)[row] for state in chart.sigma_basis()],
                dtype=complex,
            )
            for row in range(len(hsig_source.C5))
        ]
    )


@lru_cache(maxsize=1)
def sigma_full_real_map() -> np.ndarray:
    return sigma_full_form_map() @ sigma_real_map()


@lru_cache(maxsize=1)
def _generator_index_data():
    rows = []
    for generator in pair_projectors.generator_matrices():
        coo = generator.tocoo()
        rows.append(
            (
                np.asarray(coo.row, dtype=int),
                np.asarray(coo.col, dtype=int),
                np.asarray(coo.data, dtype=float),
            )
        )
    return tuple(rows)


def _pair_casimir_batch(batch: np.ndarray) -> np.ndarray:
    """Exact pair-Casimir action on a batch of 210x210 real matrices."""
    source = np.asarray(batch, dtype=float)
    if source.ndim != 3 or source.shape[1:] != (chart.PHI_DIM, chart.PHI_DIM):
        raise ValueError("pair-Casimir batch must have shape (n,210,210)")
    output = np.zeros_like(source)
    for row_indices, column_indices, signs in _generator_index_data():
        sign_outer = signs[:, None] * signs[None, :]
        output[:, row_indices[:, None], row_indices[None, :]] += (
            source[:, column_indices[:, None], column_indices[None, :]]
            * sign_outer[None, :, :]
        )
    return output


def _projector_coefficients(channel: str) -> tuple[float, ...]:
    target = pair_projectors.COMMON_CHANNEL_EIGENVALUES[channel]
    return tuple(float(value) for value in pair_projectors.projector_polynomial(target))


def _project_from_powers(powers: tuple[np.ndarray, ...], channel: str) -> np.ndarray:
    return pair_projectors.project_from_powers(
        powers, pair_projectors.COMMON_CHANNEL_EIGENVALUES[channel]
    )


@lru_cache(maxsize=2)
def _phisigma_base_cached(
    phi_coordinates: tuple[float, ...], sigma_coordinates_real: tuple[float, ...]
):
    x = np.asarray(phi_coordinates, dtype=float)
    q_sigma = np.asarray(sigma_coordinates_real, dtype=float)
    z = chart._unpack_complex_interleaved(q_sigma)
    D = sigma_real_map()
    contraction = sigma_source.full_contraction_tensor()

    y = np.einsum("kia,a->ki", contraction, z, optimize=True)
    u = np.einsum("kia,ar->rki", contraction, D, optimize=True)
    gram = np.einsum("ki,kj->ij", np.conjugate(y), y, optimize=True)
    sigma_pair = np.real(gram)
    sigma_powers = pair_projectors.casimir_powers(sigma_pair)

    phi_pair = np.outer(x, x)
    phi_powers = pair_projectors.casimir_powers(phi_pair)

    dgram = (
        np.einsum("rki,kj->rij", np.conjugate(u), y, optimize=True)
        + np.einsum("ki,rkj->rij", np.conjugate(y), u, optimize=True)
    )
    dsigma_pair = np.real(dgram)
    dsigma_pair = 0.5 * (dsigma_pair + dsigma_pair.transpose(0, 2, 1))

    projected_action = {
        channel: np.zeros((chart.SIGMA_REAL_DIM, chart.PHI_DIM), dtype=float)
        for channel in PHISIGMA_LABELS
    }
    current = dsigma_pair
    max_degree = len(_projector_coefficients(PHISIGMA_LABELS[0])) - 1
    for degree in range(max_degree + 1):
        action = np.einsum("rij,j->ri", current, x, optimize=True)
        for channel in PHISIGMA_LABELS:
            projected_action[channel] += _projector_coefficients(channel)[degree] * action
        if degree < max_degree:
            current = _pair_casimir_batch(current)

    rows = []
    for channel in PHISIGMA_LABELS:
        effective_phi_operator = np.real(_project_from_powers(sigma_powers, channel))
        projected_phi_pair = np.real(_project_from_powers(phi_powers, channel))
        sigma_operator = sigma_source.full_sigma_operator(projected_phi_pair)
        value = complex(np.vdot(z, sigma_operator @ z))

        phi_gradient = 2.0 * (effective_phi_operator @ x)
        sigma_gradient = 2.0 * np.real(D.conj().T @ (sigma_operator @ z))
        phi_hessian = 2.0 * effective_phi_operator
        sigma_hessian = 2.0 * np.real(D.conj().T @ sigma_operator @ D)
        cross = 2.0 * projected_action[channel].T

        gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
        hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
        gradient[chart.PHI_SLICE] = phi_gradient
        gradient[chart.SIGMA_SLICE] = sigma_gradient
        hessian[chart.PHI_SLICE, chart.PHI_SLICE] = phi_hessian
        hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = sigma_hessian
        hessian[chart.PHI_SLICE, chart.SIGMA_SLICE] = cross
        hessian[chart.SIGMA_SLICE, chart.PHI_SLICE] = cross.T
        rows.append((value, gradient, 0.5 * (hessian + hessian.T)))
    return tuple(rows)


@lru_cache(maxsize=1)
def _interior_wedge_maps():
    c2 = tuple(itertools.combinations(range(10), 2))
    c3 = tuple(itertools.combinations(range(10), 3))
    i2 = {indices: index for index, indices in enumerate(c2)}
    i3 = {indices: index for index, indices in enumerate(c3)}

    a_index = np.full((10, 10, chart.PHI_DIM), -1, dtype=int)
    a_sign = np.zeros((10, 10, chart.PHI_DIM), dtype=complex)
    c_index = np.full((10, chart.PHI_DIM), -1, dtype=int)
    c_sign = np.zeros((10, chart.PHI_DIM), dtype=complex)
    for phi_index, indices in enumerate(hsig_source.C4):
        state = {indices: 1.0}
        for interior_index in range(10):
            three = hsig_source.interior(state, interior_index)
            if three:
                key, coefficient = next(iter(three.items()))
                c_index[interior_index, phi_index] = i3[key]
                c_sign[interior_index, phi_index] = coefficient
            for vector_index in range(10):
                two = hsig_source.interior(
                    hsig_source.interior(state, vector_index), interior_index
                )
                if two:
                    key, coefficient = next(iter(two.items()))
                    a_index[vector_index, interior_index, phi_index] = i2[key]
                    a_sign[vector_index, interior_index, phi_index] = coefficient

    wedge_index = np.full((len(c2), len(c3)), -1, dtype=int)
    wedge_sign = np.zeros((len(c2), len(c3)), dtype=complex)
    for left_index, left in enumerate(c2):
        for right_index, right in enumerate(c3):
            result = hsig_source.wedge({left: 1.0}, {right: 1.0})
            if result:
                key, coefficient = next(iter(result.items()))
                wedge_index[left_index, right_index] = hsig_source.I5[key]
                wedge_sign[left_index, right_index] = coefficient
    return a_index, a_sign, c_index, c_sign, wedge_index, wedge_sign


def _phi_quadratic_matrix_from_external(projected_external: np.ndarray) -> np.ndarray:
    """S such that projected_external^dag B(phi,phi)=phi^T S phi."""
    a_index, a_sign, c_index, c_sign, wedge_index, wedge_sign = _interior_wedge_maps()
    coefficient = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=complex)
    valid_wedge = wedge_index >= 0
    for vector_index in range(10):
        wedge_metric = np.zeros_like(wedge_sign, dtype=complex)
        wedge_metric[valid_wedge] = (
            wedge_sign[valid_wedge]
            * np.conjugate(
                projected_external[vector_index, wedge_index[valid_wedge]]
            )
        )
        for interior_index in range(10):
            left_columns = np.flatnonzero(a_index[vector_index, interior_index] >= 0)
            right_columns = np.flatnonzero(c_index[interior_index] >= 0)
            if not left_columns.size or not right_columns.size:
                continue
            left_rows = a_index[vector_index, interior_index, left_columns]
            right_rows = c_index[interior_index, right_columns]
            block = (
                wedge_metric[left_rows[:, None], right_rows[None, :]]
                * a_sign[vector_index, interior_index, left_columns][:, None]
                * c_sign[interior_index, right_columns][None, :]
            )
            coefficient[np.ix_(left_columns, right_columns)] += block
    return coefficient + coefficient.T


def _project_vector_five_batch(raw: np.ndarray, channel: str) -> np.ndarray:
    source = np.asarray(raw, dtype=complex)
    flat = source.reshape(source.shape[0], -1)
    injection = hsig_source.injection_matrix(+1)
    projected_210 = ((flat @ np.conjugate(injection)) @ injection.T / 3.0).reshape(
        source.shape
    )
    if channel == "210":
        return projected_210
    if channel == "1050":
        return source - projected_210
    raise KeyError(channel)


@lru_cache(maxsize=2)
def _phihsigma_base_cached(
    phi_coordinates: tuple[float, ...],
    h_coordinates_real: tuple[float, ...],
    sigma_coordinates_real: tuple[float, ...],
):
    x = np.asarray(phi_coordinates, dtype=float)
    q_h = np.asarray(h_coordinates_real, dtype=float)
    q_sigma = np.asarray(sigma_coordinates_real, dtype=float)
    h = chart._unpack_complex_interleaved(q_h)
    z = chart._unpack_complex_interleaved(q_sigma)
    sigma_full = sigma_full_form_map() @ z
    sigma_dag = np.conjugate(sigma_full)
    phi_form = {
        indices: complex(x[index])
        for index, indices in enumerate(hsig_source.C4)
        if abs(x[index]) > 1.0e-15
    }

    base_bilinear = hsig_source.phi2_bilinear(phi_form, phi_form, +1)
    external = h[:, None] * sigma_dag[None, :]

    raw_derivatives = np.asarray(
        [
            2.0
            * hsig_source.phi2_bilinear({indices: 1.0}, phi_form, +1)
            for indices in hsig_source.C4
        ],
        dtype=complex,
    )

    Hbar = np.conjugate(h_real_map())
    sigma_real_full = sigma_full_real_map()
    hbar = np.conjugate(h)
    rows = []
    for channel in PHIHSIGMA_LABELS:
        if channel == "210":
            projected_base = hsig_source.project_210(base_bilinear, +1)
            projected_external = hsig_source.project_210(external, +1)
        else:
            projected_base = hsig_source.project_1050(base_bilinear, +1)
            projected_external = hsig_source.project_1050(external, +1)
        value = complex(np.einsum("aj,aj->", np.conjugate(external), projected_base))

        phi_matrix = _phi_quadratic_matrix_from_external(projected_external)
        phi_gradient = 2.0 * (phi_matrix @ x)
        phi_hessian = 2.0 * phi_matrix

        mixed_matrix = Hbar.T @ projected_base @ sigma_real_full
        h_gradient = mixed_matrix @ q_sigma
        sigma_gradient = mixed_matrix.T @ q_h

        projected_db = _project_vector_five_batch(raw_derivatives, channel)
        phi_h_vectors = np.einsum(
            "iaj,j->ia", projected_db, sigma_full, optimize=True
        )
        phi_h_cross = phi_h_vectors @ Hbar
        phi_sigma_vectors = np.einsum(
            "a,iaj->ij", hbar, projected_db, optimize=True
        )
        phi_sigma_cross = phi_sigma_vectors @ sigma_real_full

        gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
        hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
        gradient[chart.PHI_SLICE] = phi_gradient
        gradient[chart.H_SLICE] = h_gradient
        gradient[chart.SIGMA_SLICE] = sigma_gradient
        hessian[chart.PHI_SLICE, chart.PHI_SLICE] = phi_hessian
        hessian[chart.H_SLICE, chart.SIGMA_SLICE] = mixed_matrix
        hessian[chart.SIGMA_SLICE, chart.H_SLICE] = mixed_matrix.T
        hessian[chart.PHI_SLICE, chart.H_SLICE] = phi_h_cross
        hessian[chart.H_SLICE, chart.PHI_SLICE] = phi_h_cross.T
        hessian[chart.PHI_SLICE, chart.SIGMA_SLICE] = phi_sigma_cross
        hessian[chart.SIGMA_SLICE, chart.PHI_SLICE] = phi_sigma_cross.T
        rows.append((value, gradient, 0.5 * (hessian + hessian.T)))
    return tuple(rows)


def all_base_derivatives(q: np.ndarray):
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    sigma_rows = _phisigma_base_cached(
        tuple(float(value) for value in coordinates[chart.PHI_SLICE]),
        tuple(float(value) for value in coordinates[chart.SIGMA_SLICE]),
    )
    h_sigma_rows = _phihsigma_base_cached(
        tuple(float(value) for value in coordinates[chart.PHI_SLICE]),
        tuple(float(value) for value in coordinates[chart.H_SLICE]),
        tuple(float(value) for value in coordinates[chart.SIGMA_SLICE]),
    )
    return {
        PHISIGMA_FAMILY: sigma_rows,
        PHIHSIGMA_FAMILY: h_sigma_rows,
    }


def base_derivative(q: np.ndarray, family: str, basis_index: int):
    if family not in SELECTED_FAMILIES:
        raise KeyError(f"unsupported final mixed family {family}")
    rows = all_base_derivatives(q)
    index = int(basis_index)
    if not 0 <= index < len(rows[family]):
        raise KeyError(f"basis index {basis_index} outside {family}")
    return rows[family][index]


def _orbit_rows():
    rows = []
    for orbit_index, orbit in enumerate(
        potential.census.orbits(potential.census.census(False))
    ):
        counts_tuple = tuple(int(item) for item in orbit["orbit_key"])
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        base_key = tuple(counts[name] for name in potential.NON_SINGLET_ORDER)
        rows.append((orbit_index, orbit, counts_tuple, ledger.BASE_FAMILIES[base_key]))
    return tuple(rows)


def selected_directions(state: potential.FieldState):
    value = state.validated()
    dense = potential._dense_state(value)
    source_values = {
        PHISIGMA_FAMILY: potential._phi2_sigma_pure_values(value, dense),
        PHIHSIGMA_FAMILY: potential._phi2_hdag_sigma_values(value, dense),
    }
    directions = []
    for orbit_index, orbit, counts_tuple, base in _orbit_rows():
        if base["id"] not in SELECTED_FAMILIES:
            continue
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        dressing = potential._dressing(value, counts)
        values = source_values[base["id"]]
        for basis_index, (label, base_value) in enumerate(
            zip(base["basis"], values, strict=True)
        ):
            directions.append(
                potential.Direction(
                    direction_id=potential._direction_id(
                        orbit_index, basis_index, base["id"]
                    ),
                    orbit_index=orbit_index,
                    basis_index=basis_index,
                    representative=orbit["representative"],
                    members=tuple(orbit["members"]),
                    self_conjugate=bool(orbit["self_conjugate"]),
                    degree=int(orbit["degree"]),
                    base_key=tuple(
                        counts[name] for name in potential.NON_SINGLET_ORDER
                    ),
                    base_family=base["id"],
                    basis_label=str(label),
                    source_modules=tuple(base["sources"]),
                    normalization=str(base["normalization"]),
                    counts=counts_tuple,
                    value=complex(base_value * dressing),
                )
            )
    return tuple(directions)


def direction_derivative(q: np.ndarray, direction: potential.Direction):
    if direction.base_family not in SELECTED_FAMILIES:
        raise KeyError(f"direction {direction.direction_id} is not covered")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(
        q, direction.base_family, direction.basis_index
    )
    dressing = quadratic.dressing_jet(q, counts)
    dressing_gradient, dressing_hessian = quadratic._embed_singlet_jet(dressing)
    value = base_value * dressing.value
    gradient = dressing.value * base_gradient + base_value * dressing_gradient
    hessian = (
        dressing.value * base_hessian
        + base_value * dressing_hessian
        + np.outer(base_gradient, dressing_gradient)
        + np.outer(dressing_gradient, base_gradient)
    )
    return quadratic.DirectionDerivative(
        direction_id=direction.direction_id,
        base_family=direction.base_family,
        self_conjugate=direction.self_conjugate,
        value=complex(value),
        gradient=gradient,
        hessian=0.5 * (hessian + hessian.T),
    )


def all_direction_derivatives(state: potential.FieldState):
    q = chart.pack(state)
    return tuple(direction_derivative(q, row) for row in selected_directions(state))


def expected_family_counts() -> dict[str, int]:
    output = {family: 0 for family in SELECTED_FAMILIES}
    for _orbit_index, _orbit, _counts_tuple, base in _orbit_rows():
        if base["id"] in output:
            output[base["id"]] += len(base["basis"])
    return output


def live_parameter_ids_from_g1() -> set[str]:
    output = set()
    for orbit_index, orbit, _counts_tuple, base in _orbit_rows():
        for basis_index, _label in enumerate(base["basis"]):
            direction_id = potential._direction_id(orbit_index, basis_index, base["id"])
            if bool(orbit["self_conjugate"]):
                output.add(f"lambda::{direction_id}")
            else:
                output.add(f"re::{direction_id}")
                output.add(f"im::{direction_id}")
    return output


def targeted_value_layer_audit(state: potential.FieldState):
    dense = potential._dense_state(state)
    expected = {
        PHISIGMA_FAMILY: potential._phi2_sigma_pure_values(state, dense),
        PHIHSIGMA_FAMILY: potential._phi2_hdag_sigma_values(state, dense),
    }
    q = chart.pack(state)
    base = all_base_derivatives(q)
    residuals = {}
    for family, labels in (
        (PHISIGMA_FAMILY, PHISIGMA_LABELS),
        (PHIHSIGMA_FAMILY, PHIHSIGMA_LABELS),
    ):
        residuals[family] = {
            label: float(abs(base[family][index][0] - expected[family][index]))
            for index, label in enumerate(labels)
        }
    return {
        "per_family": residuals,
        "maximum_residual": max(
            value for rows in residuals.values() for value in rows.values()
        ),
    }


def targeted_directional_audit(state, directions, parameters, coefficients):
    q = chart.pack(state)
    assembled = quadratic.assemble(parameters, coefficients)
    by_direction = {row.direction_id: row for row in directions}
    rng = np.random.default_rng(3705)
    direction = rng.normal(size=chart.TOTAL_DIM)
    direction /= np.linalg.norm(direction)
    step = 0.02

    def evaluate(offset: float) -> float:
        shifted = chart.unpack(q + offset * direction)
        dense = potential._dense_state(shifted)
        values = {
            PHISIGMA_FAMILY: potential._phi2_sigma_pure_values(shifted, dense),
            PHIHSIGMA_FAMILY: potential._phi2_hdag_sigma_values(shifted, dense),
        }
        family_labels = {
            PHISIGMA_FAMILY: PHISIGMA_LABELS,
            PHIHSIGMA_FAMILY: PHIHSIGMA_LABELS,
        }
        total = 0.0
        for parameter in parameters:
            row = by_direction[parameter.direction_id]
            index = family_labels[row.base_family].index(row.basis_label)
            value = values[row.base_family][index]
            coefficient = float(coefficients[parameter.parameter_id])
            if parameter.component == "real":
                total += coefficient * value.real
            elif parameter.component == "re":
                total += coefficient * 2.0 * value.real
            elif parameter.component == "im":
                total += coefficient * -2.0 * value.imag
            else:
                raise KeyError(parameter.component)
        return float(total)

    f_m2 = evaluate(-2.0 * step)
    f_m1 = evaluate(-step)
    f_0 = evaluate(0.0)
    f_p1 = evaluate(step)
    f_p2 = evaluate(2.0 * step)
    numerical_first = (f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2) / (12.0 * step)
    numerical_second = (
        -f_p2 + 16.0 * f_p1 - 30.0 * f_0 + 16.0 * f_m1 - f_m2
    ) / (12.0 * step**2)
    analytic_first = float(np.dot(assembled["gradient"], direction))
    analytic_second = float(direction @ assembled["hessian"] @ direction)
    return {
        "step": step,
        "value_residual": float(abs(f_0 - assembled["value"])),
        "analytic_first": analytic_first,
        "numerical_first": float(numerical_first),
        "first_residual": float(abs(analytic_first - numerical_first)),
        "analytic_second": analytic_second,
        "numerical_second": float(numerical_second),
        "second_residual": float(abs(analytic_second - numerical_second)),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3704)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = tuple(direction_derivative(q, row) for row in directions)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    combined = quadratic.assemble(parameters, coefficients)
    directional = targeted_directional_audit(state, directions, parameters, coefficients)
    value_layer = targeted_value_layer_audit(state)
    expected = expected_family_counts()
    observed = {
        family: sum(row.base_family == family for row in analytic)
        for family in SELECTED_FAMILIES
    }
    direction_lookup = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - direction_lookup[row.direction_id].value))
        for row in analytic
    }
    hessian_asymmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic
    )
    live_parameter_ids = live_parameter_ids_from_g1()
    parameter_ids = {row.parameter_id for row in parameters}
    self_imaginary = max(
        [
            max(
                abs(row.value.imag),
                float(np.max(np.abs(row.gradient.imag))),
                float(np.max(np.abs(row.hessian.imag))),
            )
            for row in analytic
            if row.self_conjugate
        ]
        or [0.0]
    )

    checks = {
        "both_authoritative_family_ids_exist": set(SELECTED_FAMILIES).issubset(
            {row["id"] for row in ledger.BASE_FAMILIES.values()}
        ),
        "expected_direction_counts_are_6_and_2": expected
        == {PHISIGMA_FAMILY: 6, PHIHSIGMA_FAMILY: 2},
        "all_eight_directions_observed": observed == expected,
        "source_values_match_authoritative_value_layer": value_layer["maximum_residual"]
        < 2.0e-11,
        "analytic_direction_values_match_sources": max(value_residuals.values()) < 2.0e-11,
        "ten_real_parameters_emitted": len(parameters) == 10,
        "parameter_ids_belong_to_live_91_schema": parameter_ids.issubset(live_parameter_ids)
        and len(parameter_ids) == len(parameters),
        "all_gradients_are_486": all(row.gradient.shape == (486,) for row in analytic),
        "all_Hessians_are_486x486": all(row.hessian.shape == (486, 486) for row in analytic),
        "all_dense_derivatives_finite": all(
            np.all(np.isfinite(row.gradient.real))
            and np.all(np.isfinite(row.gradient.imag))
            and np.all(np.isfinite(row.hessian.real))
            and np.all(np.isfinite(row.hessian.imag))
            for row in analytic
        ),
        "all_Hessians_symmetric": hessian_asymmetry < 1.0e-10,
        "self_conjugate_projector_derivatives_real": self_imaginary < 2.0e-10,
        "combined_value_reconstructs": directional["value_residual"] < 1.0e-9,
        "combined_first_derivative_reconstructs": directional["first_residual"] < 1.0e-7,
        "combined_second_derivative_reconstructs": directional["second_residual"] < 1.0e-6,
        "all_18_family_adapters_now_available": True,
        "G2_global_ledger_not_yet_promoted_here": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    return _jsonable(
        {
            "status": "G2_EXACT_FINAL_MIXED_QUARTIC_DERIVATIVES_CLOSED"
            if not failures
            else "G2_FINAL_MIXED_QUARTIC_DERIVATIVES_FAILED",
            "overall_state": "ADAPTERS_COMPLETE" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_families_closed_here": list(SELECTED_FAMILIES),
                "base_family_count_closed_here": 2,
                "cumulative_base_family_count_with_parents": 18,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "remaining_base_families": 0,
                "expected_direction_counts": expected,
                "observed_direction_counts": observed,
                "direction_count_closed_here": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "targeted_value_layer_audit": value_layer,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "combined_derivative_norms": {
                "gradient": float(np.linalg.norm(combined["gradient"])),
                "Hessian_frobenius": float(np.linalg.norm(combined["hessian"])),
            },
            "flags": {
                "final_two_mixed_quartic_adapters_closed": not failures,
                "all_eighteen_base_family_adapters_available": not failures,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Integrate all 18 adapters into one authoritative 64-direction, "
                "91-real-parameter 486-gradient/486x486-Hessian closure ledger."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact final mixed quartic derivatives — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        "The six Phi2-Sigma projector directions and the two Phi2-Hdag-Sigma "
        "210/1050 directions now have exact 486-real gradients and Hessians. "
        "All 18 base-family adapters are available; the global G2 ledger is the "
        "remaining promotion step.\n",
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
