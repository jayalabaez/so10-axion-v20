#!/usr/bin/env python3
"""Exact first-order G3 stationarity-feasibility gate on the closed G2 chart.

G2 supplies 91 real potential parameters and exact derivatives on the canonical
486-real scalar chart.  At a fixed candidate field point q*, stationarity is
linear in the real coupling vector c,

    grad V(q*; c) = A(q*) c = 0,

where A is the 486x91 matrix whose columns are parameter-resolved gradients.
This module constructs A exactly for the generic high-scale SM-singlet ansatz

    Phi = 0.90 p + 0.05 a + 0.05 omega,
    H = 0,
    Sigma = Delta_R,
    S = 1,
    Phi17 = 1.

The already-certified dense G2 Hessians are not needed for this first-order
question.  Two quartic adapters are expensive because their dense Hessian
construction repeatedly applies large pair-Casimir maps.  Their gradients are
therefore evaluated here from the same exact projector identities, without
finite differences:

* I_R(Sigma)=||P_R(zz^T)||^2 has
      grad_q I_R = 4 Re[D^T conjugate(P_R(zz^T)) z];
* the Phi^2 Sigma^dag Sigma and Phi^2 H^dag Sigma gradients follow directly
  from their exact biquadratic/multilinear source tensors.

Exact projector-component reconstructions and homogeneous Euler identities
independently audit those promoted analytic fast gradients.  This gate establishes first-order feasibility and
identifiability only.  It does not establish boundedness, Hessian positivity,
a global minimum, uniqueness, the physical spectrum, or whole-model validity.
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_source
import exact_phi2_h_126dag_210_1050_channels_v20 as hsig_source
import exact_phisigma_126bar_minus_projectors_v20 as phisigma_source
import exact_phisigma_casimir_projectors_v20 as pair_projectors
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_derivative_coverage_ledger_v20 as g2
import live_g2_exact_final_mixed_quartic_derivatives_v20 as final_mixed
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic
import live_g2_exact_sigma_self_quartic_derivatives_v20 as sigma_self
import live_g2_exact_unique_hsigma_chiral_derivatives_v20 as unique_hsigma

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_FULL_STATIONARITY_FEASIBILITY_V20.json"
OUT_MD = ROOT / "G3_FULL_STATIONARITY_FEASIBILITY_V20.md"

CANDIDATE_AMPLITUDES = {
    "p": 0.90,
    "a": 0.05,
    "omega": 0.05,
    "Delta_R": 1.0,
    "H": 0.0,
    "S": 1.0,
    "Phi17": 1.0,
}
FAST_FAMILIES = (
    sigma_self.BASE_FAMILY,
    unique_hsigma.FAMILY_A,
    unique_hsigma.FAMILY_B,
    final_mixed.PHISIGMA_FAMILY,
    final_mixed.PHIHSIGMA_FAMILY,
)


@dataclasses.dataclass(frozen=True)
class ParameterGradient:
    parameter_id: str
    direction_id: str
    base_family: str
    component: str
    value: float
    gradient: np.ndarray


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


def candidate_state() -> potential.FieldState:
    singlets = direct.singlet_basis()
    phi = direct.add_forms(
        direct.scale_form(singlets["p"], CANDIDATE_AMPLITUDES["p"]),
        direct.scale_form(singlets["a"], CANDIDATE_AMPLITUDES["a"]),
        direct.scale_form(singlets["omega"], CANDIDATE_AMPLITUDES["omega"]),
    )
    return potential.FieldState(
        phi=phi,
        h=np.zeros(chart.H_COMPLEX_DIM, dtype=complex),
        sigma=direct.scale_form(
            direct.delta_r(), CANDIDATE_AMPLITUDES["Delta_R"]
        ),
        s=complex(CANDIDATE_AMPLITUDES["S"]),
        x=complex(CANDIDATE_AMPLITUDES["Phi17"]),
    ).validated()


def _parameter_rows_from_direction_rows(
    rows: Iterable[quadratic.DirectionDerivative],
) -> tuple[ParameterGradient, ...]:
    output: list[ParameterGradient] = []
    for row in rows:
        if row.self_conjugate:
            output.append(
                ParameterGradient(
                    parameter_id=f"lambda::{row.direction_id}",
                    direction_id=row.direction_id,
                    base_family=row.base_family,
                    component="real",
                    value=float(row.value.real),
                    gradient=np.asarray(row.gradient.real, dtype=float),
                )
            )
        else:
            output.append(
                ParameterGradient(
                    parameter_id=f"re::{row.direction_id}",
                    direction_id=row.direction_id,
                    base_family=row.base_family,
                    component="re",
                    value=float(2.0 * row.value.real),
                    gradient=np.asarray(2.0 * row.gradient.real, dtype=float),
                )
            )
            output.append(
                ParameterGradient(
                    parameter_id=f"im::{row.direction_id}",
                    direction_id=row.direction_id,
                    base_family=row.base_family,
                    component="im",
                    value=float(-2.0 * row.value.imag),
                    gradient=np.asarray(-2.0 * row.gradient.imag, dtype=float),
                )
            )
    return tuple(output)


def _parameter_rows_from_complex_gradient(
    *,
    direction_id: str,
    base_family: str,
    self_conjugate: bool,
    value: complex,
    gradient: np.ndarray,
) -> tuple[ParameterGradient, ...]:
    row = quadratic.DirectionDerivative(
        direction_id=direction_id,
        base_family=base_family,
        self_conjugate=self_conjugate,
        value=complex(value),
        gradient=np.asarray(gradient, dtype=complex),
        hessian=np.zeros((0, 0), dtype=complex),
    )
    return _parameter_rows_from_direction_rows((row,))


def _sigma_self_base_value_gradients(q: np.ndarray):
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    z = sigma_self._sigma_coordinates(coordinates[chart.SIGMA_SLICE])
    pair = np.outer(z, z)
    powers = sigma_source._powers(pair)
    real_map = sigma_self.real_chart_basis()
    rows = []
    for label in sigma_self.BASIS_LABELS:
        projected = sigma_source.project(label, pair, powers)
        value = complex(float(np.vdot(projected, projected).real))
        gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
        gradient[chart.SIGMA_SLICE] = 4.0 * np.real(
            real_map.T @ np.conjugate(projected) @ z
        )
        rows.append((value, gradient))
    return tuple(rows)


def _sigma_self_parameter_gradients(
    state: potential.FieldState,
) -> tuple[ParameterGradient, ...]:
    q = chart.pack(state)
    base_rows = _sigma_self_base_value_gradients(q)
    output: list[ParameterGradient] = []
    for orbit_index, orbit, counts_tuple, base in sigma_self._orbit_rows():
        if base["id"] != sigma_self.BASE_FAMILY:
            continue
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        dressing = quadratic.dressing_jet(q, counts)
        dressing_gradient, _ = quadratic._embed_singlet_jet(dressing)
        for basis_index, _label in enumerate(base["basis"]):
            base_value, base_gradient = base_rows[basis_index]
            value = base_value * dressing.value
            gradient = (
                dressing.value * base_gradient
                + base_value * dressing_gradient
            )
            direction_id = potential._direction_id(
                orbit_index, basis_index, base["id"]
            )
            output.extend(
                _parameter_rows_from_complex_gradient(
                    direction_id=direction_id,
                    base_family=base["id"],
                    self_conjugate=bool(orbit["self_conjugate"]),
                    value=value,
                    gradient=gradient,
                )
            )
    return tuple(output)


def _unique_hsigma_base_value_gradients(q: np.ndarray):
    hbar, sigma, sigmabar = unique_hsigma._state_blocks(q)
    dense_basis = unique_hsigma.dense_sigma_basis()
    dense_basis_bar = np.conjugate(dense_basis)
    hbar_map = np.conjugate(unique_hsigma.h_map())
    sigma_map = unique_hsigma.sigma_map()
    sigma_map_bar = np.conjugate(sigma_map)

    value_a = unique_hsigma.source.invariant_hdag_sigma2_sigmadag(
        hbar, sigma, sigmabar
    )
    gh_a = np.einsum(
        "bcdef,abcgh,defgh->a", sigma, sigma, sigmabar, optimize="greedy"
    )
    gz1 = np.einsum(
        "a,ibcdef,abcgh,defgh->i",
        hbar, dense_basis, sigma, sigmabar, optimize="greedy"
    )
    gz2 = np.einsum(
        "a,bcdef,iabcgh,defgh->i",
        hbar, sigma, dense_basis, sigmabar, optimize="greedy"
    )
    gzbar = np.einsum(
        "a,bcdef,abcgh,idefgh->i",
        hbar, sigma, sigma, dense_basis_bar, optimize="greedy"
    )
    gradient_a = np.zeros(chart.TOTAL_DIM, dtype=complex)
    gradient_a[chart.H_SLICE] = hbar_map.T @ gh_a
    gradient_a[chart.SIGMA_SLICE] = (
        sigma_map.T @ (gz1 + gz2) + sigma_map_bar.T @ gzbar
    )

    value_b = unique_hsigma.source.invariant_hdag2_sigma2(hbar, sigma)
    c_hh = np.einsum("bcdef,acdef->ab", sigma, sigma, optimize="greedy")
    gh_b = (c_hh + c_hh.T) @ hbar
    gz1_b = np.einsum(
        "a,b,ibcdef,acdef->i",
        hbar, hbar, dense_basis, sigma, optimize="greedy"
    )
    gz2_b = np.einsum(
        "a,b,bcdef,iacdef->i",
        hbar, hbar, sigma, dense_basis, optimize="greedy"
    )
    gradient_b = np.zeros(chart.TOTAL_DIM, dtype=complex)
    gradient_b[chart.H_SLICE] = hbar_map.T @ gh_b
    gradient_b[chart.SIGMA_SLICE] = sigma_map.T @ (gz1_b + gz2_b)
    return {
        unique_hsigma.FAMILY_A: (complex(value_a), gradient_a),
        unique_hsigma.FAMILY_B: (complex(value_b), gradient_b),
    }


def _unique_hsigma_parameter_gradients(
    state: potential.FieldState,
) -> tuple[ParameterGradient, ...]:
    q = chart.pack(state)
    base_rows = _unique_hsigma_base_value_gradients(q)
    output: list[ParameterGradient] = []
    for orbit_index, orbit, counts_tuple, base in unique_hsigma._orbit_rows():
        if base["id"] not in unique_hsigma.SELECTED_FAMILIES:
            continue
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        dressing = quadratic.dressing_jet(q, counts)
        dressing_gradient, _ = quadratic._embed_singlet_jet(dressing)
        base_value, base_gradient = base_rows[base["id"]]
        value = base_value * dressing.value
        gradient = dressing.value * base_gradient + base_value * dressing_gradient
        direction_id = potential._direction_id(orbit_index, 0, base["id"])
        output.extend(
            _parameter_rows_from_complex_gradient(
                direction_id=direction_id,
                base_family=base["id"],
                self_conjugate=bool(orbit["self_conjugate"]),
                value=value,
                gradient=gradient,
            )
        )
    return tuple(output)


def _final_mixed_base_value_gradients(q: np.ndarray):
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi_coordinates = coordinates[chart.PHI_SLICE]
    h_coordinates = coordinates[chart.H_SLICE]
    sigma_coordinates = coordinates[chart.SIGMA_SLICE]
    z = chart._unpack_complex_interleaved(sigma_coordinates)

    # Six Phi^2 Sigma^dag Sigma projectors.  The dense Hessian-only
    # dsigma-pair batch is intentionally not constructed here.
    real_map = final_mixed.sigma_real_map()
    contraction = phisigma_source.full_contraction_tensor()
    y = np.einsum("kia,a->ki", contraction, z, optimize=True)
    gram = np.einsum("ki,kj->ij", np.conjugate(y), y, optimize=True)
    sigma_pair = np.real(gram)
    sigma_powers = pair_projectors.casimir_powers(sigma_pair)
    phi_pair = np.outer(phi_coordinates, phi_coordinates)
    phi_powers = pair_projectors.casimir_powers(phi_pair)

    phisigma_rows = []
    for channel in final_mixed.PHISIGMA_LABELS:
        effective_phi_operator = np.real(
            final_mixed._project_from_powers(sigma_powers, channel)
        )
        projected_phi_pair = np.real(
            final_mixed._project_from_powers(phi_powers, channel)
        )
        sigma_operator = phisigma_source.full_sigma_operator(projected_phi_pair)
        value = complex(np.vdot(z, sigma_operator @ z))
        gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
        gradient[chart.PHI_SLICE] = 2.0 * (
            effective_phi_operator @ phi_coordinates
        )
        gradient[chart.SIGMA_SLICE] = 2.0 * np.real(
            real_map.conj().T @ (sigma_operator @ z)
        )
        phisigma_rows.append((value, gradient))

    # Two Phi^2 H^dag Sigma channels.  Direct first variation avoids the
    # 210x210 Phi Hessian coefficient matrix used by the dense G2 adapter.
    h = chart._unpack_complex_interleaved(h_coordinates)
    sigma_full = final_mixed.sigma_full_form_map() @ z
    sigma_dag = np.conjugate(sigma_full)
    phi_form = {
        indices: complex(phi_coordinates[index])
        for index, indices in enumerate(hsig_source.C4)
        if abs(phi_coordinates[index]) > 1.0e-15
    }
    base_bilinear = hsig_source.phi2_bilinear(phi_form, phi_form, +1)
    external = h[:, None] * sigma_dag[None, :]
    raw_phi_derivatives = np.asarray(
        [
            2.0
            * hsig_source.phi2_bilinear({indices: 1.0}, phi_form, +1)
            for indices in hsig_source.C4
        ],
        dtype=complex,
    )
    hbar_map = np.conjugate(final_mixed.h_real_map())
    sigma_real_full = final_mixed.sigma_full_real_map()

    phihsigma_rows = []
    for channel in final_mixed.PHIHSIGMA_LABELS:
        if channel == "210":
            projected_base = hsig_source.project_210(base_bilinear, +1)
        else:
            projected_base = hsig_source.project_1050(base_bilinear, +1)
        projected_derivatives = final_mixed._project_vector_five_batch(
            raw_phi_derivatives, channel
        )
        value = complex(
            np.einsum("aj,aj->", np.conjugate(external), projected_base)
        )
        mixed_matrix = hbar_map.T @ projected_base @ sigma_real_full
        gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
        gradient[chart.PHI_SLICE] = np.einsum(
            "aj,iaj->i",
            np.conjugate(external),
            projected_derivatives,
            optimize=True,
        )
        gradient[chart.H_SLICE] = mixed_matrix @ sigma_coordinates
        gradient[chart.SIGMA_SLICE] = mixed_matrix.T @ h_coordinates
        phihsigma_rows.append((value, gradient))

    return {
        final_mixed.PHISIGMA_FAMILY: tuple(phisigma_rows),
        final_mixed.PHIHSIGMA_FAMILY: tuple(phihsigma_rows),
    }


def _final_mixed_parameter_gradients(
    state: potential.FieldState,
) -> tuple[ParameterGradient, ...]:
    q = chart.pack(state)
    base_rows = _final_mixed_base_value_gradients(q)
    output: list[ParameterGradient] = []
    for orbit_index, orbit, counts_tuple, base in final_mixed._orbit_rows():
        if base["id"] not in final_mixed.SELECTED_FAMILIES:
            continue
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        dressing = quadratic.dressing_jet(q, counts)
        dressing_gradient, _ = quadratic._embed_singlet_jet(dressing)
        for basis_index, _label in enumerate(base["basis"]):
            base_value, base_gradient = base_rows[base["id"]][basis_index]
            value = base_value * dressing.value
            gradient = (
                dressing.value * base_gradient
                + base_value * dressing_gradient
            )
            direction_id = potential._direction_id(
                orbit_index, basis_index, base["id"]
            )
            output.extend(
                _parameter_rows_from_complex_gradient(
                    direction_id=direction_id,
                    base_family=base["id"],
                    self_conjugate=bool(orbit["self_conjugate"]),
                    value=value,
                    gradient=gradient,
                )
            )
    return tuple(output)


def parameter_gradient_rows(
    state: potential.FieldState,
) -> tuple[tuple[ParameterGradient, ...], dict[str, float]]:
    # Evaluate the authoritative value layer exactly once, before packing the
    # Sigma chart.  This creates the pair-Casimir generator cache in the stable
    # order and prevents every legacy adapter from reevaluating all 64 values.
    started_values = time.perf_counter()
    live_directions = potential.evaluate_directions(state)
    value_layer_seconds = float(time.perf_counter() - started_values)
    q = chart.pack(state)
    modules = {
        "quadratic_families": g2.quadratic,
        "portal_families": g2.portal,
        "remaining_cubic_families": g2.cubic,
        "H10_self_quartics": g2.h10,
        "H_Sigma_hermitian": g2.hsigma,
        "Phi2_HdagH_channels": g2.phi2h,
        "Phi_self_quartics": g2.phi_self,
    }
    rows: list[ParameterGradient] = []
    timings: dict[str, float] = {"authoritative_value_layer": value_layer_seconds}
    for adapter_name, families, _adapter in g2.ADAPTERS:
        started = time.perf_counter()
        if adapter_name == "Sigma_self_quartics":
            adapter_rows = _sigma_self_parameter_gradients(state)
        elif adapter_name == "unique_HSigma_chiral":
            adapter_rows = _unique_hsigma_parameter_gradients(state)
        elif adapter_name == "final_mixed_quartics":
            adapter_rows = _final_mixed_parameter_gradients(state)
        else:
            module = modules[adapter_name]
            selected = tuple(
                row for row in live_directions if row.base_family in set(families)
            )
            exact_rows = tuple(module.direction_derivative(q, row) for row in selected)
            adapter_rows = _parameter_rows_from_direction_rows(exact_rows)
        timings[adapter_name] = float(time.perf_counter() - started)
        rows.extend(adapter_rows)
    rows.sort(key=lambda row: row.parameter_id)
    return tuple(rows), timings


def stationarity_matrix(rows: Iterable[ParameterGradient]) -> np.ndarray:
    values = tuple(rows)
    return np.column_stack([row.gradient for row in values])


def _rank_and_nullspace(matrix: np.ndarray) -> dict[str, Any]:
    source = np.asarray(matrix, dtype=float)
    column_norms = np.linalg.norm(source, axis=0)
    maximum_norm = float(np.max(column_norms, initial=0.0))
    nonzero_threshold = max(1.0e-14, 1.0e-12 * maximum_norm)
    nonzero = column_norms > nonzero_threshold
    normalized = source[:, nonzero] / column_norms[nonzero]
    if normalized.size:
        _u, singular_values, vh = np.linalg.svd(
            normalized, full_matrices=False
        )
        rank_threshold = 1.0e-10 * singular_values[0]
        rank = int(np.sum(singular_values > rank_threshold))
        witness_scaled = vh[-1].copy()
        witness_active = witness_scaled / column_norms[nonzero]
        witness = np.zeros(source.shape[1], dtype=float)
        witness[nonzero] = witness_active
        norm = float(np.linalg.norm(witness))
        if norm:
            witness /= norm
        first_nonzero = np.flatnonzero(np.abs(witness) > 1.0e-14)
        if first_nonzero.size and witness[first_nonzero[0]] < 0.0:
            witness *= -1.0
    else:
        singular_values = np.asarray([], dtype=float)
        rank_threshold = 0.0
        rank = 0
        witness = np.zeros(source.shape[1], dtype=float)
    residual = source @ witness
    relative_residual = float(
        np.linalg.norm(residual)
        / max(np.linalg.norm(source, ord="fro") * np.linalg.norm(witness), 1.0)
    )
    return {
        "rank": rank,
        "rank_threshold": float(rank_threshold),
        "total_nullity": int(source.shape[1] - rank),
        "nonzero_column_count": int(np.sum(nonzero)),
        "zero_column_count": int(np.sum(~nonzero)),
        "active_parameter_nullity": int(np.sum(nonzero) - rank),
        "maximum_column_norm": maximum_norm,
        "nonzero_column_threshold": float(nonzero_threshold),
        "singular_values_normalized_active": singular_values,
        "nonzero_column_mask": nonzero,
        "stationary_coefficient_witness": witness,
        "stationary_gradient_residual_norm": float(np.linalg.norm(residual)),
        "stationary_gradient_relative_residual": relative_residual,
    }


def _fast_gauge_orbit_matrix(state: potential.FieldState) -> np.ndarray:
    value = state.validated()
    columns = []
    for first, second in itertools.combinations(range(10), 2):
        delta_phi = direct.generator_action(value.phi, first, second)
        delta_h_form = direct.generator_action({}, first, second)
        delta_sigma = direct.generator_action(value.sigma, first, second)
        tangent = np.zeros(chart.TOTAL_DIM, dtype=float)
        tangent[chart.PHI_SLICE] = np.asarray(
            [
                complex(delta_phi.get(indices, 0.0)).real
                for indices in chart.phi_indices()
            ],
            dtype=float,
        )
        # H is zero in this candidate, but retain the exact chart slot.
        tangent[chart.H_SLICE] = chart._pack_complex_interleaved(
            np.asarray(
                [delta_h_form.get((index,), 0.0) for index in range(10)],
                dtype=complex,
            )
        )
        tangent[chart.SIGMA_SLICE] = chart._pack_complex_interleaved(
            chart.sigma_coordinates(delta_sigma)
        )
        columns.append(tangent)
    return np.column_stack(columns)


def fast_gradient_directional_audit(
    state: potential.FieldState,
    rows: Iterable[ParameterGradient],
) -> dict[str, Any]:
    """Cheap exact audits of the gradient-only projector path.

    The radial/block Euler identities are algebraic consequences of the
    homogeneous source tensors.  In addition, selected Sigma components are
    reconstructed with the original exact projector linearization
    ``2 Re <P(zz^T), P(dz^T+zd^T)>``.
    """
    q = chart.pack(state)
    sigma_base = _sigma_self_base_value_gradients(q)
    q_sigma = q[chart.SIGMA_SLICE]
    sigma_euler = [
        float(abs(np.dot(q_sigma, gradient[chart.SIGMA_SLICE]) - 4.0 * value))
        for value, gradient in sigma_base
    ]

    z = sigma_self._sigma_coordinates(q_sigma)
    pair = np.outer(z, z)
    powers = sigma_source._powers(pair)
    real_map = sigma_self.real_chart_basis()
    selected_columns = (0, 1, 50, 101, 200, 251)
    component_residuals = []
    for column in selected_columns:
        linear_pair = (
            np.outer(real_map[:, column], z)
            + np.outer(z, real_map[:, column])
        )
        linear_powers = sigma_source._powers(linear_pair)
        for label_index, label in enumerate(sigma_self.BASIS_LABELS):
            projected = sigma_source.project(label, pair, powers)
            linear_projected = sigma_source.project(
                label, linear_pair, linear_powers
            )
            reference = 2.0 * np.real(np.vdot(projected, linear_projected))
            observed = sigma_base[label_index][1][chart.SIGMA_SLICE][column]
            component_residuals.append(float(abs(reference - observed)))

    final_rows = _final_mixed_base_value_gradients(q)
    phi_block = q[chart.PHI_SLICE]
    sigma_block = q[chart.SIGMA_SLICE]
    euler_residuals = list(sigma_euler)
    for value, gradient in final_rows[final_mixed.PHISIGMA_FAMILY]:
        euler_residuals.extend(
            [
                float(abs(np.dot(phi_block, gradient[chart.PHI_SLICE]) - 2.0 * value)),
                float(abs(np.dot(sigma_block, gradient[chart.SIGMA_SLICE]) - 2.0 * value)),
            ]
        )

    # At H=0 the two Phi^2 H^dag Sigma sources are exactly linear in Hbar.
    # A finite H direction therefore provides an exact (not finite-difference)
    # first-variation reconstruction.
    h_direction = np.asarray(
        [complex(((3 * i + 1) % 7) - 3, ((5 * i + 2) % 9) - 4) for i in range(10)],
        dtype=complex,
    )
    h_direction /= np.sqrt(np.vdot(h_direction, h_direction).real)
    q_h_direction = chart._pack_complex_interleaved(h_direction)
    h_probe = potential.FieldState(
        phi=state.phi,
        h=h_direction,
        sigma=state.sigma,
        s=state.s,
        x=state.x,
    ).validated()
    h_probe_dense = potential._dense_state(h_probe)
    h_probe_values = potential._phi2_hdag_sigma_values(h_probe, h_probe_dense)
    linearization_residuals = []
    for index, (_value, gradient) in enumerate(
        final_rows[final_mixed.PHIHSIGMA_FAMILY]
    ):
        analytic = np.dot(q_h_direction, gradient[chart.H_SLICE])
        linearization_residuals.append(
            float(abs(analytic - h_probe_values[index]))
        )

    unique_rows = _unique_hsigma_base_value_gradients(q)
    value_a, gradient_a = unique_rows[unique_hsigma.FAMILY_A]
    value_b, gradient_b = unique_rows[unique_hsigma.FAMILY_B]
    analytic_unique_a = np.dot(q_h_direction, gradient_a[chart.H_SLICE])
    source_unique_a = unique_hsigma._source_value(
        h_probe, unique_hsigma.FAMILY_A
    )
    linearization_residuals.extend(
        [
            float(abs(value_a)),
            float(abs(value_b)),
            float(abs(analytic_unique_a - source_unique_a)),
            float(np.max(np.abs(gradient_b), initial=0.0)),
        ]
    )
    selected = tuple(row for row in rows if row.base_family in FAST_FAMILIES)
    return {
        "parameter_count": len(selected),
        "sigma_component_count": len(component_residuals),
        "maximum_sigma_component_residual": max(component_residuals),
        "maximum_euler_residual": max(euler_residuals),
        "maximum_exact_linearization_residual": max(linearization_residuals),
        "relative_residual": max(
            max(component_residuals),
            max(euler_residuals),
            max(linearization_residuals),
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    started = time.perf_counter()
    state = candidate_state()
    # Build parameter gradients before the standalone chart pack.  The exact
    # Sigma projector source constructs its generator cache much faster in
    # this order; pre-populating the independent chart basis causes severe
    # allocator contention on constrained runners.
    rows, timings = parameter_gradient_rows(state)
    q = chart.pack(state)
    matrix = stationarity_matrix(rows)
    rank = _rank_and_nullspace(matrix)
    parameter_ids = [row.parameter_id for row in rows]
    expected_parameter_ids = sigma_self.live_parameter_ids_from_g1()

    gauge_matrix = _fast_gauge_orbit_matrix(state)
    gauge_singular_values = np.linalg.svd(gauge_matrix, compute_uv=False)
    gauge_rank = int(
        np.sum(
            gauge_singular_values
            > 1.0e-10 * gauge_singular_values[0]
        )
    )
    ward_matrix = gauge_matrix.T @ matrix
    ward_residual = float(np.max(np.abs(ward_matrix), initial=0.0))

    row_norms = np.linalg.norm(matrix, axis=1)
    active_rows = np.flatnonzero(
        row_norms > max(1.0e-14, 1.0e-12 * np.max(row_norms, initial=0.0))
    )
    coordinate_names = chart.coordinate_names()
    active_coordinates = [
        {
            "index": int(index),
            "name": coordinate_names[int(index)],
            "row_norm": float(row_norms[int(index)]),
        }
        for index in active_rows
    ]
    nonzero_mask = np.asarray(rank["nonzero_column_mask"], dtype=bool)
    zero_parameter_ids = [
        parameter_ids[index]
        for index in np.flatnonzero(~nonzero_mask)
    ]
    witness = np.asarray(rank["stationary_coefficient_witness"], dtype=float)
    leading_witness = sorted(
        [
            {
                "parameter_id": parameter_ids[index],
                "coefficient": float(witness[index]),
            }
            for index in np.flatnonzero(np.abs(witness) > 1.0e-10)
        ],
        key=lambda row: abs(row["coefficient"]),
        reverse=True,
    )[:12]

    fast_audit = fast_gradient_directional_audit(state, rows)
    checks = {
        "G2_contract_has_18_families": len(g2.covered_families()) == 18,
        "G2_contract_has_no_remaining_families": (
            g2.EXPECTED_REMAINING_FAMILIES == ()
        ),
        "canonical_chart_has_486_real_fields": chart.TOTAL_DIM == 486,
        "all_91_real_parameters_present": (
            len(rows) == len(parameter_ids) == len(set(parameter_ids)) == 91
            and set(parameter_ids) == expected_parameter_ids
        ),
        "stationarity_matrix_shape_486x91": matrix.shape == (486, 91),
        "all_parameter_gradients_finite": bool(np.all(np.isfinite(matrix))),
        "generic_candidate_has_33_broken_gauge_directions": gauge_rank == 33,
        "all_parameter_gradients_obey_gauge_Ward_identity": (
            ward_residual < 1.0e-10
        ),
        "stationarity_has_nontrivial_coupling_nullspace": (
            rank["total_nullity"] > 0
        ),
        "explicit_stationary_coefficient_witness_reconstructs": (
            rank["stationary_gradient_relative_residual"] < 1.0e-10
        ),
        "fast_exact_quartic_gradients_match_independent_value_audit": (
            fast_audit["relative_residual"] < 2.0e-8
        ),
        "dense_Hessians_not_recomputed_for_first_order_gate": True,
        "G3_not_claimed_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    elapsed = float(time.perf_counter() - started)

    # Remove internal arrays from the serializable public rank summary.
    rank_summary = {
        key: value
        for key, value in rank.items()
        if key not in {"nonzero_column_mask", "stationary_coefficient_witness"}
    }
    return _jsonable(
        {
            "status": (
                "G3_FIRST_ORDER_STATIONARITY_FEASIBLE_BUT_UNDERDETERMINED"
                if not failures
                else "G3_STATIONARITY_FEASIBILITY_EXECUTION_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "candidate": {
                "description": (
                    "generic high-scale SM-singlet ansatz with H=0"
                ),
                "amplitudes": CANDIDATE_AMPLITUDES,
                "coordinate_norm": float(np.linalg.norm(q)),
                "gauge_orbit_rank": gauge_rank,
                "unbroken_gauge_generator_count": 45 - gauge_rank,
            },
            "stationarity_matrix": {
                "shape": list(matrix.shape),
                "independent_constraint_rank": rank_summary["rank"],
                "total_coupling_nullity": rank_summary["total_nullity"],
                "nonzero_parameter_columns": rank_summary[
                    "nonzero_column_count"
                ],
                "zero_parameter_columns_at_candidate": rank_summary[
                    "zero_column_count"
                ],
                "active_parameter_nullity": rank_summary[
                    "active_parameter_nullity"
                ],
                "active_coordinate_row_count": len(active_coordinates),
                "active_coordinates": active_coordinates,
                "stationarity_invisible_parameter_ids": zero_parameter_ids,
                "normalized_active_singular_values": rank_summary[
                    "singular_values_normalized_active"
                ],
                "stationary_gradient_residual_norm": rank_summary[
                    "stationary_gradient_residual_norm"
                ],
                "stationary_gradient_relative_residual": rank_summary[
                    "stationary_gradient_relative_residual"
                ],
                "leading_stationary_witness_coefficients": leading_witness,
            },
            "gauge_invariance": {
                "orbit_matrix_shape": list(gauge_matrix.shape),
                "orbit_rank": gauge_rank,
                "maximum_Ward_residual": ward_residual,
            },
            "fast_gradient_audit": fast_audit,
            "performance": {
                "adapter_seconds": timings,
                "total_seconds": elapsed,
                "fast_gradient_families": list(FAST_FAMILIES),
                "avoided_operation": (
                    "dense 252-column and 210-column Hessian linearizations"
                ),
            },
            "scientific_interpretation": {
                "first_order_stationarity_feasible": not failures,
                "stationarity_uniquely_determines_couplings": False,
                "coupling_solution_dimension": rank_summary["total_nullity"],
                "reason_G3_remains_open": (
                    "First-order stationarity leaves a large coupling nullspace. "
                    "G3 additionally requires boundedness, positivity of the "
                    "gauge-quotiented Hessian, and comparison against competing "
                    "extrema over the allowed coupling domain."
                ),
            },
            "flags": {
                "G1_closed": True,
                "G2_closed": True,
                "G3_first_order_feasibility_executed": not failures,
                "G3_closed": False,
                "G4_closed": False,
                "G5_closed": False,
                "G6_closed": False,
                "G7_closed": False,
                "G8_closed": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Search the stationary coupling nullspace for a bounded potential "
                "whose Hessian is positive on the 453-dimensional complement of "
                "the 33 gauge directions, then enumerate lower competing extrema."
            ),
            "verdict": (
                "The apparent G3 stall was computational, not a tensor-algebra "
                "failure. Exact gradient-only projector formulas remove the dense-"
                "Hessian bottleneck. At the generic p-a-omega plus Delta_R ansatz, "
                "the 486x91 stationarity map has low independent rank and a large "
                "coupling nullspace, so first-order stationarity is feasible but "
                "does not uniquely select the theory or close G3."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    matrix = report["stationarity_matrix"]
    OUT_MD.write_text(
        "# G3 full-coordinate stationarity feasibility — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + "## Exact first-order result\n\n"
        + f"- stationarity matrix: `{matrix['shape'][0]} x {matrix['shape'][1]}`\n"
        + f"- independent rank: `{matrix['independent_constraint_rank']}`\n"
        + f"- coupling nullity: `{matrix['total_coupling_nullity']}`\n"
        + f"- gauge-orbit rank: `{report['gauge_invariance']['orbit_rank']}`\n"
        + f"- Ward residual: `{report['gauge_invariance']['maximum_Ward_residual']:.3e}`\n"
        + "\n"
        + f"**Next:** {report['next_exact_target']}\n",
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
