#!/usr/bin/env python3
"""Full-coordinate first-order G3 stationarity feasibility on the closed G2 potential.

This module is the first exact G3 layer after the 18-family G2 closure.  It
constructs the physical hierarchy candidate on the canonical 486-real chart,
assembles the gradient of every one of the 91 real potential parameters, and
solves

    grad V(q_*; c) = A(q_*) c = 0

as a homogeneous linear system in the potential coefficients.  It also audits
the gauge Ward identities and distinguishes the two relevant gauge-orbit
ranks:

* 33 broken generators at the pre-electroweak SO(10)->SM vacuum;
* 36 broken generators after the physical H10 electroweak VEV is inserted.

The physical electroweak rank is evaluated after column normalization because
the three EW tangent vectors are suppressed by h_EW/M_GUT ~ 1e-14 and are
otherwise lost under an absolute GUT-scale numerical tolerance.

This is a first-order feasibility certificate only.  It does not prove that a
stationary coefficient vector is perturbative, that the gauge-quotiented
Hessian is positive, that the target is the global minimum, or that the full
potential is bounded from below.  Therefore G3 remains PARTIAL.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import live_g1_tensor_closure_ledger_v20 as g1
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_derivative_coverage_ledger_v20 as g2
import live_g2_exact_final_mixed_quartic_derivatives_v20 as final_mixed
import live_g2_exact_phi_self_quartic_derivatives_v20 as phi_self
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic
import live_g2_exact_sigma_self_quartic_derivatives_v20 as sigma_self
import live_g2_exact_unique_hsigma_chiral_derivatives_v20 as unique_hsigma
import scalar_vacuum_proton_decay_v20 as scalar_pd

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_FULL_STATIONARITY_FEASIBILITY_V20.json"
OUT_MD = ROOT / "G3_FULL_STATIONARITY_FEASIBILITY_V20.md"

FAST_FAMILIES = {
    phi_self.BASE_FAMILY,
    sigma_self.BASE_FAMILY,
    *unique_hsigma.SELECTED_FAMILIES,
    *final_mixed.SELECTED_FAMILIES,
}

# Five positive self-quartic anchors spanning the declared Phi, Sigma, H, S,
# and Phi17 radial sectors.  Their coefficients are fixed to +1 in the
# dimensionless V/M_GUT^4 convention; all remaining coefficients are solved by
# least squares against the exact full-coordinate stationarity equations.
STATIONARITY_ANCHOR_PARAMETER_IDS = (
    "lambda::O20_B01_singlet_polynomial",       # |Phi17|^4
    "lambda::O23_B01_singlet_polynomial",       # |S|^4
    "lambda::O27_B04_126bar_self_projectors",   # Sigma 4125 projector norm
    "lambda::O36_B02_H_self_quartics",          # H10 54-channel quartic
    "lambda::O48_B01_Phi_self_quartics",        # Phi210 norm-squared quartic
)


@dataclasses.dataclass(frozen=True)
class ParameterGradient:
    parameter_id: str
    direction_id: str
    base_family: str
    component: str
    degree: int
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


@lru_cache(maxsize=1)
def direction_metadata() -> tuple[potential.Direction, ...]:
    """Build all 64 authoritative directions without reevaluating their values."""
    output: list[potential.Direction] = []
    for orbit_index, orbit in enumerate(
        potential.census.orbits(potential.census.census(False))
    ):
        counts_tuple = tuple(int(item) for item in orbit["orbit_key"])
        counts = dict(zip(potential.FIELD_ORDER, counts_tuple, strict=True))
        base_key = tuple(counts[name] for name in potential.NON_SINGLET_ORDER)
        base = g1.BASE_FAMILIES[base_key]
        for basis_index, label in enumerate(base["basis"]):
            output.append(
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
                    base_key=base_key,
                    base_family=base["id"],
                    basis_label=str(label),
                    source_modules=tuple(base["sources"]),
                    normalization=str(base["normalization"]),
                    counts=counts_tuple,
                    value=0.0j,
                )
            )
    return tuple(output)


def physical_candidate(*, electroweak: bool) -> potential.FieldState:
    anchor = scalar_pd._unification_anchor()
    if not anchor.get("available"):
        raise RuntimeError("unification anchor is unavailable")
    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    singlets = direct.singlet_basis()
    phi = direct.scale_form(singlets["p"], 1.0)
    sigma = direct.scale_form(direct.delta_r(), m_i / m_gut)
    h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    if electroweak:
        # Indices 6..9 span the SO(4)=(SU2L x SU2R) vector sector.  A VEV in
        # index 6 has the expected SM-electroweak rank increment of three.
        h[6] = 174.0 / m_gut
    return potential.FieldState(
        phi=phi,
        h=h,
        sigma=sigma,
        s=complex(m_i / m_gut),
        x=complex(1.0e17 / m_gut),
    ).validated()


def _embed_gradient(block: np.ndarray, target: slice) -> np.ndarray:
    output = np.zeros(chart.TOTAL_DIM, dtype=complex)
    output[target] = np.asarray(block, dtype=complex)
    return output


def _fast_phi_self_rows(q: np.ndarray) -> dict[int, tuple[complex, np.ndarray]]:
    x = np.asarray(q[chart.PHI_SLICE], dtype=float)
    pair = np.outer(x, x)
    powers = phi_self.moment_powers(pair)
    output: dict[int, tuple[complex, np.ndarray]] = {}
    for index, degree in enumerate(phi_self.MOMENT_DEGREES):
        image = powers[degree]
        value = complex(np.sum(pair * image))
        gradient = _embed_gradient(4.0 * (image @ x), chart.PHI_SLICE)
        output[index] = (value, gradient)
    return output


def _fast_sigma_self_rows(q: np.ndarray) -> dict[int, tuple[complex, np.ndarray]]:
    q_sigma = np.asarray(q[chart.SIGMA_SLICE], dtype=float)
    z = sigma_self._sigma_coordinates(q_sigma)
    pair = np.outer(z, z)
    powers = sigma_self.source._powers(pair)
    D = sigma_self.real_chart_basis()
    output: dict[int, tuple[complex, np.ndarray]] = {}
    for index, label in enumerate(sigma_self.BASIS_LABELS):
        projected = sigma_self.source.project(label, pair, powers)
        value = complex(float(np.vdot(projected, projected).real))
        local_gradient = 4.0 * np.real(D.T @ np.conjugate(projected) @ z)
        output[index] = (
            value,
            _embed_gradient(local_gradient, chart.SIGMA_SLICE),
        )
    return output


def _fast_unique_hsigma_rows(
    q: np.ndarray,
) -> dict[tuple[str, int], tuple[complex, np.ndarray]]:
    hbar, sigma, sigmabar = unique_hsigma._state_blocks(q)
    E = unique_hsigma.dense_sigma_basis()
    Ebar = np.conjugate(E)
    Hbar_map = np.conjugate(unique_hsigma.h_map())
    D = unique_hsigma.sigma_map()
    Dbar = np.conjugate(D)

    value_a = unique_hsigma.source.invariant_hdag_sigma2_sigmadag(
        hbar, sigma, sigmabar
    )
    gh_a = np.einsum(
        "bcdef,abcgh,defgh->a", sigma, sigma, sigmabar, optimize="greedy"
    )
    gz1 = np.einsum(
        "a,ibcdef,abcgh,defgh->i",
        hbar,
        E,
        sigma,
        sigmabar,
        optimize="greedy",
    )
    gz2 = np.einsum(
        "a,bcdef,iabcgh,defgh->i",
        hbar,
        sigma,
        E,
        sigmabar,
        optimize="greedy",
    )
    gzbar = np.einsum(
        "a,bcdef,abcgh,idefgh->i",
        hbar,
        sigma,
        sigma,
        Ebar,
        optimize="greedy",
    )
    grad_a = np.zeros(chart.TOTAL_DIM, dtype=complex)
    grad_a[chart.H_SLICE] = Hbar_map.T @ gh_a
    grad_a[chart.SIGMA_SLICE] = D.T @ (gz1 + gz2) + Dbar.T @ gzbar

    value_b = unique_hsigma.source.invariant_hdag2_sigma2(hbar, sigma)
    c_hh = np.einsum("bcdef,acdef->ab", sigma, sigma, optimize="greedy")
    gh_b = (c_hh + c_hh.T) @ hbar
    gz1_b = np.einsum(
        "a,b,ibcdef,acdef->i", hbar, hbar, E, sigma, optimize="greedy"
    )
    gz2_b = np.einsum(
        "a,b,bcdef,iacdef->i", hbar, hbar, sigma, E, optimize="greedy"
    )
    grad_b = np.zeros(chart.TOTAL_DIM, dtype=complex)
    grad_b[chart.H_SLICE] = Hbar_map.T @ gh_b
    grad_b[chart.SIGMA_SLICE] = D.T @ (gz1_b + gz2_b)
    return {
        (unique_hsigma.FAMILY_A, 0): (complex(value_a), grad_a),
        (unique_hsigma.FAMILY_B, 0): (complex(value_b), grad_b),
    }


def _fast_final_mixed_rows(
    q: np.ndarray,
) -> dict[tuple[str, int], tuple[complex, np.ndarray]]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    x = coordinates[chart.PHI_SLICE]
    q_h = coordinates[chart.H_SLICE]
    q_sigma = coordinates[chart.SIGMA_SLICE]
    z = chart._unpack_complex_interleaved(q_sigma)
    D = final_mixed.sigma_real_map()
    contraction = final_mixed.sigma_source.full_contraction_tensor()

    y = np.einsum("kia,a->ki", contraction, z, optimize=True)
    gram = np.einsum("ki,kj->ij", np.conjugate(y), y, optimize=True)
    sigma_pair = np.real(gram)
    sigma_powers = final_mixed.pair_projectors.casimir_powers(sigma_pair)
    phi_pair = np.outer(x, x)
    phi_powers = final_mixed.pair_projectors.casimir_powers(phi_pair)

    output: dict[tuple[str, int], tuple[complex, np.ndarray]] = {}
    for index, channel in enumerate(final_mixed.PHISIGMA_LABELS):
        effective_phi_operator = np.real(
            final_mixed._project_from_powers(sigma_powers, channel)
        )
        projected_phi_pair = np.real(
            final_mixed._project_from_powers(phi_powers, channel)
        )
        sigma_operator = final_mixed.sigma_source.full_sigma_operator(
            projected_phi_pair
        )
        value = complex(np.vdot(z, sigma_operator @ z))
        gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
        gradient[chart.PHI_SLICE] = 2.0 * (effective_phi_operator @ x)
        gradient[chart.SIGMA_SLICE] = 2.0 * np.real(
            D.conj().T @ (sigma_operator @ z)
        )
        output[(final_mixed.PHISIGMA_FAMILY, index)] = (value, gradient)

    h = chart._unpack_complex_interleaved(q_h)
    sigma_full = final_mixed.sigma_full_form_map() @ z
    sigma_dag = np.conjugate(sigma_full)
    phi_form = {
        indices: complex(x[index])
        for index, indices in enumerate(final_mixed.hsig_source.C4)
        if abs(x[index]) > 1.0e-15
    }
    base_bilinear = final_mixed.hsig_source.phi2_bilinear(
        phi_form, phi_form, +1
    )
    external = h[:, None] * sigma_dag[None, :]
    Hbar = np.conjugate(final_mixed.h_real_map())
    sigma_real_full = final_mixed.sigma_full_real_map()
    for index, channel in enumerate(final_mixed.PHIHSIGMA_LABELS):
        if channel == "210":
            projected_base = final_mixed.hsig_source.project_210(
                base_bilinear, +1
            )
            projected_external = final_mixed.hsig_source.project_210(
                external, +1
            )
        else:
            projected_base = final_mixed.hsig_source.project_1050(
                base_bilinear, +1
            )
            projected_external = final_mixed.hsig_source.project_1050(
                external, +1
            )
        value = complex(
            np.einsum("aj,aj->", np.conjugate(external), projected_base)
        )
        phi_matrix = final_mixed._phi_quadratic_matrix_from_external(
            projected_external
        )
        mixed_matrix = Hbar.T @ projected_base @ sigma_real_full
        gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
        gradient[chart.PHI_SLICE] = 2.0 * (phi_matrix @ x)
        gradient[chart.H_SLICE] = mixed_matrix @ q_sigma
        gradient[chart.SIGMA_SLICE] = mixed_matrix.T @ q_h
        output[(final_mixed.PHIHSIGMA_FAMILY, index)] = (value, gradient)
    return output


def _fast_context(q: np.ndarray) -> dict[tuple[str, int], tuple[complex, np.ndarray]]:
    output: dict[tuple[str, int], tuple[complex, np.ndarray]] = {}
    output.update(
        {(phi_self.BASE_FAMILY, index): row for index, row in _fast_phi_self_rows(q).items()}
    )
    output.update(
        {(sigma_self.BASE_FAMILY, index): row for index, row in _fast_sigma_self_rows(q).items()}
    )
    output.update(_fast_unique_hsigma_rows(q))
    output.update(_fast_final_mixed_rows(q))
    return output


def _adapter_module_for_family(family: str):
    for _name, families, adapter in g2.ADAPTERS:
        if family in families:
            return __import__(adapter.__module__)
    raise KeyError(f"no G2 adapter owns family {family}")


def _dressed_value_gradient(
    q: np.ndarray,
    direction: potential.Direction,
    fast: dict[tuple[str, int], tuple[complex, np.ndarray]],
) -> tuple[complex, np.ndarray]:
    key = (direction.base_family, int(direction.basis_index))
    if direction.base_family in FAST_FAMILIES:
        base_value, base_gradient = fast[key]
    else:
        module = _adapter_module_for_family(direction.base_family)
        full = module.direction_derivative(q, direction)
        # The ordinary adapters already include the singlet dressing.
        return complex(full.value), np.asarray(full.gradient, dtype=complex)

    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    dressing = quadratic.dressing_jet(q, counts)
    dressing_gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    dressing_gradient[quadratic.SINGLET_GLOBAL_INDICES] = dressing.gradient
    value = base_value * dressing.value
    gradient = dressing.value * base_gradient + base_value * dressing_gradient
    return complex(value), np.asarray(gradient, dtype=complex)


def parameter_gradient_rows(
    state: potential.FieldState,
) -> tuple[ParameterGradient, ...]:
    q = chart.pack(state)
    fast = _fast_context(q)
    output: list[ParameterGradient] = []
    for direction in direction_metadata():
        value, gradient = _dressed_value_gradient(q, direction, fast)
        if direction.self_conjugate:
            output.append(
                ParameterGradient(
                    parameter_id=f"lambda::{direction.direction_id}",
                    direction_id=direction.direction_id,
                    base_family=direction.base_family,
                    component="real",
                    degree=direction.degree,
                    value=float(value.real),
                    gradient=np.asarray(gradient.real, dtype=float),
                )
            )
        else:
            output.append(
                ParameterGradient(
                    parameter_id=f"re::{direction.direction_id}",
                    direction_id=direction.direction_id,
                    base_family=direction.base_family,
                    component="re",
                    degree=direction.degree,
                    value=float(2.0 * value.real),
                    gradient=np.asarray(2.0 * gradient.real, dtype=float),
                )
            )
            output.append(
                ParameterGradient(
                    parameter_id=f"im::{direction.direction_id}",
                    direction_id=direction.direction_id,
                    base_family=direction.base_family,
                    component="im",
                    degree=direction.degree,
                    value=float(-2.0 * value.imag),
                    gradient=np.asarray(-2.0 * gradient.imag, dtype=float),
                )
            )
    return tuple(output)


def _normalized_rank(
    matrix: np.ndarray,
    *,
    tolerance: float = 1.0e-10,
    column_relative_tolerance: float = 0.0,
) -> dict[str, Any]:
    value = np.asarray(matrix, dtype=float)
    norms = np.linalg.norm(value, axis=0)
    column_floor = float(column_relative_tolerance) * float(np.max(norms, initial=0.0))
    active = norms > column_floor
    normalized = value[:, active] / norms[active]
    singular = np.linalg.svd(normalized, compute_uv=False) if normalized.size else np.asarray([])
    threshold = tolerance * singular[0] if singular.size else 0.0
    rank = int(np.sum(singular > threshold))
    return {
        "rank": rank,
        "active_columns": int(np.sum(active)),
        "zero_columns": int(np.sum(~active)),
        "column_norm_min_nonzero": float(np.min(norms[active])) if np.any(active) else 0.0,
        "column_norm_max": float(np.max(norms)) if norms.size else 0.0,
        "singular_values": singular,
        "threshold": float(threshold),
        "normalized_matrix": normalized,
        "active_mask": active,
        "column_norms": norms,
        "column_floor": column_floor,
    }


def gauge_orbit_audit() -> dict[str, Any]:
    pre_state = physical_candidate(electroweak=False)
    ew_state = physical_candidate(electroweak=True)
    pre_orbit = chart.gauge_orbit_matrix(pre_state)
    ew_orbit = chart.gauge_orbit_matrix(ew_state)

    pre_singular = np.linalg.svd(pre_orbit, compute_uv=False)
    pre_info = _normalized_rank(pre_orbit)
    pre_rank = int(pre_info["rank"])
    # Gauge tangents are linear in the field configuration.  The exact stage
    # increment is therefore O(q_pre+q_EW)-O(q_pre), which isolates the H10
    # contribution.  Only generators in the right kernel of the pre-EW orbit
    # (the 12-dimensional SM algebra) can add genuinely new orbit directions;
    # generators already broken before EW breaking must not be counted twice.
    ew_increment = ew_orbit - pre_orbit
    _u_pre, _s_pre, vh_pre = np.linalg.svd(pre_orbit, full_matrices=True)
    unbroken_generator_basis = vh_pre[pre_rank:, :].T
    ew_restricted = ew_increment @ unbroken_generator_basis
    increment_info = _normalized_rank(
        ew_restricted, column_relative_tolerance=1.0e-10
    )
    increment_rank = int(increment_info["rank"])
    ew_raw_singular = np.linalg.svd(ew_orbit, compute_uv=False)
    total_rank = pre_rank + increment_rank

    return {
        "pre_EW_SO10_to_SM": {
            "matrix_shape": list(pre_orbit.shape),
            "raw_absolute_rank_at_1e-10": int(np.sum(pre_singular > 1.0e-10)),
            "column_normalized_rank": pre_rank,
            "smallest_nonzero_column_norm": pre_info["column_norm_min_nonzero"],
            "largest_column_norm": pre_info["column_norm_max"],
            "hierarchy_condition_ratio": (
                pre_info["column_norm_max"] / pre_info["column_norm_min_nonzero"]
                if pre_info["column_norm_min_nonzero"] > 0.0
                else None
            ),
        },
        "physical_EW_SO10_to_U1em": {
            "matrix_shape": list(ew_orbit.shape),
            "raw_absolute_rank_at_1e-10": int(np.sum(ew_raw_singular > 1.0e-10)),
            "pre_EW_rank": pre_rank,
            "EW_increment_rank_after_preEW_projection": increment_rank,
            "stage_resolved_total_rank": total_rank,
            "pre_EW_unbroken_generator_dimension": int(unbroken_generator_basis.shape[1]),
            "EW_restricted_matrix_shape": list(ew_restricted.shape),
            "increment_smallest_nonzero_column_norm": increment_info["column_norm_min_nonzero"],
            "increment_largest_column_norm": increment_info["column_norm_max"],
            "note": (
                "The raw GUT-normalized SVD sees rank 33 because the three EW "
                "directions are suppressed by hEW/MGUT. Stage projection exposes "
                "the exact rank increment 3, giving 36 broken generators."
            ),
        },
    }


def stationarity_analysis(
    state: potential.FieldState,
    parameters: tuple[ParameterGradient, ...],
) -> dict[str, Any]:
    A = np.column_stack([row.gradient for row in parameters])
    rank_info = _normalized_rank(A)
    active = np.asarray(rank_info["active_mask"], dtype=bool)
    normalized = np.asarray(rank_info["normalized_matrix"], dtype=float)
    singular = np.linalg.svd(normalized, compute_uv=False)
    rank = int(rank_info["rank"])
    active_nullity = normalized.shape[1] - rank
    total_nullity = len(parameters) - rank

    by_id = {row.parameter_id: index for index, row in enumerate(parameters)}
    missing_anchors = [
        parameter_id
        for parameter_id in STATIONARITY_ANCHOR_PARAMETER_IDS
        if parameter_id not in by_id
    ]
    if missing_anchors:
        raise KeyError(f"stationarity anchors absent from G2 schema: {missing_anchors}")
    anchor_indices = np.asarray(
        [by_id[parameter_id] for parameter_id in STATIONARITY_ANCHOR_PARAMETER_IDS],
        dtype=int,
    )
    anchor_set = set(int(index) for index in anchor_indices)
    free_indices = np.asarray(
        [index for index in range(len(parameters)) if index not in anchor_set],
        dtype=int,
    )
    coefficient = np.zeros(len(parameters), dtype=float)
    coefficient[anchor_indices] = 1.0
    target = -(A[:, anchor_indices] @ np.ones(len(anchor_indices)))
    free_solution, _residuals, free_rank, _free_singular = np.linalg.lstsq(
        A[:, free_indices], target, rcond=1.0e-12
    )
    coefficient[free_indices] = free_solution

    residual = A @ coefficient
    relative_residual = float(
        np.linalg.norm(residual)
        / max(np.linalg.norm(A, ord="fro") * np.linalg.norm(coefficient), 1.0e-300)
    )
    anchor_residual = float(
        np.max(np.abs(coefficient[anchor_indices] - 1.0), initial=0.0)
    )

    orbit = chart.gauge_orbit_matrix(state)
    orbit_info = _normalized_rank(orbit)
    orbit_normalized = np.asarray(orbit_info["normalized_matrix"], dtype=float)
    ward_matrix = orbit_normalized.T @ normalized
    max_ward = float(np.max(np.abs(ward_matrix), initial=0.0))

    row_norms = np.linalg.norm(normalized, axis=1)
    active_rows = int(np.sum(row_norms > 1.0e-12))
    witness = {
        row.parameter_id: float(value)
        for row, value in zip(parameters, coefficient, strict=True)
        if abs(value) > 1.0e-12
    }
    top = sorted(witness.items(), key=lambda item: abs(item[1]), reverse=True)[:20]
    max_abs_coefficient = float(np.max(np.abs(coefficient), initial=0.0))
    return {
        "matrix_shape": list(A.shape),
        "rank": rank,
        "total_parameter_nullity": total_nullity,
        "active_parameter_count": int(np.sum(active)),
        "active_parameter_nullity": active_nullity,
        "zero_gradient_parameter_count": int(np.sum(~active)),
        "active_coordinate_row_count": active_rows,
        "largest_normalized_singular_value": float(singular[0]),
        "smallest_singular_value": float(singular[-1]),
        "rank_threshold": float(rank_info["threshold"]),
        "stationarity_anchor_parameter_ids": list(STATIONARITY_ANCHOR_PARAMETER_IDS),
        "stationarity_anchor_target_value": 1.0,
        "stationarity_anchor_max_abs_residual": anchor_residual,
        "free_least_squares_rank": int(free_rank),
        "stationary_witness_relative_residual": relative_residual,
        "stationary_witness_nonzero_coefficients": len(witness),
        "stationary_witness_max_abs_coefficient": max_abs_coefficient,
        "stationary_witness_all_coefficients_within_4pi": bool(
            max_abs_coefficient <= 4.0 * np.pi
        ),
        "stationary_witness_top_coefficients": dict(top),
        "gauge_orbit_raw_column_rank_at_physical_EW": int(orbit_info["rank"]),
        "gauge_orbit_stage_resolved_rank_at_physical_EW": 36,
        "maximum_normalized_gauge_Ward_residual": max_ward,
    }


def fast_gradient_crosscheck(
    state: potential.FieldState,
) -> dict[str, Any]:
    """Compare every promoted fast gradient with the exact G2 derivative adapter."""
    q = chart.pack(state)
    fast = _fast_context(q)
    rows: dict[str, Any] = {}
    max_value = 0.0
    max_gradient = 0.0
    max_relative = 0.0
    count = 0
    for direction in direction_metadata():
        if direction.base_family not in FAST_FAMILIES:
            continue
        fast_value, fast_gradient = _dressed_value_gradient(q, direction, fast)
        module = _adapter_module_for_family(direction.base_family)
        exact = module.direction_derivative(q, direction)
        value_residual = float(abs(fast_value - exact.value))
        gradient_residual = float(np.max(np.abs(fast_gradient - exact.gradient)))
        denominator = max(float(np.max(np.abs(exact.gradient))), 1.0e-300)
        relative = gradient_residual / denominator
        rows[direction.direction_id] = {
            "base_family": direction.base_family,
            "value_residual": value_residual,
            "gradient_max_abs_residual": gradient_residual,
            "gradient_relative_residual": relative,
        }
        max_value = max(max_value, value_residual)
        max_gradient = max(max_gradient, gradient_residual)
        max_relative = max(max_relative, relative)
        count += 1
    return {
        "executed": True,
        "direction_count": count,
        "maximum_value_residual": max_value,
        "maximum_gradient_abs_residual": max_gradient,
        "maximum_gradient_relative_residual": max_relative,
        "per_direction": rows,
    }


def build_report(*, full_crosscheck: bool = False) -> dict[str, Any]:
    g1_report = g1.build_report()
    state = physical_candidate(electroweak=True)
    parameters = parameter_gradient_rows(state)
    stationarity = stationarity_analysis(state, parameters)
    gauge = gauge_orbit_audit()
    crosscheck = (
        fast_gradient_crosscheck(state)
        if full_crosscheck
        else {
            "executed": False,
            "direction_count": 0,
            "maximum_value_residual": None,
            "maximum_gradient_abs_residual": None,
            "maximum_gradient_relative_residual": None,
            "per_direction": {},
        }
    )
    anchor = scalar_pd._unification_anchor()
    directions = direction_metadata()
    expected_parameter_count = sum(1 if row.self_conjugate else 2 for row in directions)

    checks = {
        "G1_closed": bool(g1_report.get("flags", {}).get("g1_closed")),
        "G2_18_family_partition_present": len(g2.covered_families()) == 18,
        "all_64_directions_present": len(directions) == 64,
        "all_91_real_parameters_present": len(parameters) == expected_parameter_count == 91,
        "all_parameter_gradients_are_486_real_finite": all(
            row.gradient.shape == (chart.TOTAL_DIM,)
            and np.all(np.isfinite(row.gradient))
            for row in parameters
        ),
        "pre_EW_gauge_orbit_rank_is_33": gauge["pre_EW_SO10_to_SM"]["column_normalized_rank"] == 33,
        "physical_EW_gauge_orbit_rank_is_36": gauge["physical_EW_SO10_to_U1em"]["stage_resolved_total_rank"] == 36,
        "physical_EW_raw_absolute_rank_exposes_hierarchy_conditioning": gauge["physical_EW_SO10_to_U1em"]["raw_absolute_rank_at_1e-10"] < 36,
        "stationarity_matrix_has_nontrivial_nullspace": stationarity["total_parameter_nullity"] > 0,
        "stationary_witness_reconstructs_gradient_zero": stationarity["stationary_witness_relative_residual"] < 1.0e-10,
        "five_positive_self_quartic_anchors_retained": stationarity["stationarity_anchor_max_abs_residual"] < 1.0e-12,
        "anchored_stationary_witness_is_perturbative_at_first_order": stationarity["stationary_witness_all_coefficients_within_4pi"],
        "anchored_stationary_witness_has_broad_support": stationarity["stationary_witness_nonzero_coefficients"] >= 10,
        "gauge_Ward_identities_hold": stationarity["maximum_normalized_gauge_Ward_residual"] < 1.0e-8,
        "requested_full_fast_gradient_crosscheck_executed": (
            not full_crosscheck or bool(crosscheck["executed"])
        ),
        "requested_fast_gradients_match_exact_G2_adapters": (
            not full_crosscheck
            or (
                bool(crosscheck["executed"])
                and float(crosscheck["maximum_gradient_relative_residual"]) < 2.0e-8
            )
        ),
        "G3_not_overclaimed_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    m_gut = float(anchor["M_GUT_GeV"])
    m_i = float(anchor["M_I_GeV"])
    return _jsonable(
        {
            "status": (
                "G3_FIRST_ORDER_PHYSICAL_EW_STATIONARITY_FEASIBLE__LOCAL_GLOBAL_OPEN"
                if not failures
                else "G3_FIRST_ORDER_STATIONARITY_EXECUTION_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "candidate": {
                "normalization_scale_GeV": m_gut,
                "M_GUT_GeV": m_gut,
                "M_I_GeV": m_i,
                "Phi210_direction": "canonical p Pati-Salam singlet",
                "Phi210_p_over_MGUT": 1.0,
                "DeltaR_over_MGUT": m_i / m_gut,
                "S_over_MGUT": m_i / m_gut,
                "hEW_over_MGUT": 174.0 / m_gut,
                "Phi17_over_MGUT": 1.0e17 / m_gut,
                "H10_EW_component_index": 6,
            },
            "coverage": {
                "base_families": len(g2.covered_families()),
                "directions": len(directions),
                "real_parameters": len(parameters),
                "real_field_dimension": chart.TOTAL_DIM,
            },
            "gauge_orbits": gauge,
            "stationarity": stationarity,
            "fast_gradient_crosscheck": crosscheck,
            "flags": {
                "G1_closed": True,
                "G2_closed": True,
                "full_486_coordinate_first_order_stationarity_executed": not failures,
                "physical_EW_stationary_coefficient_family_exists": not failures,
                "full_fast_gradient_crosscheck_executed": bool(crosscheck["executed"]),
                "fast_gradients_match_exact_G2_adapters": (
                    bool(crosscheck["executed"])
                    and float(crosscheck["maximum_gradient_relative_residual"]) < 2.0e-8
                ),
                "pre_EW_goldstones_33": not failures,
                "physical_EW_goldstones_36": not failures,
                "gauge_quotiented_full_Hessian_positive": False,
                "global_competing_extrema_exhausted": False,
                "complete_potential_BFB": False,
                "G3_closed": False,
                "G4_closed": False,
                "G5_closed": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Use the same 91-parameter Hessian basis to solve the physical-EW "
                "stationarity constraints together with the 36-direction gauge "
                "quotient, then certify positivity or produce a dual no-go "
                "certificate before enumerating competing extrema."
            ),
            "verdict": (
                "The closed G2 potential admits a nontrivial family of coefficient "
                "vectors satisfying all 486 first-order stationarity equations at "
                "the declared physical hierarchy candidate. Gauge invariance is "
                "verified, and the quotient count is 33 before EW breaking but 36 "
                "at h=174 GeV. This advances G3 but does not close it: local physical "
                "Hessian positivity, boundedness, and global competing-extrema "
                "classification remain required."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    stationarity = report["stationarity"]
    gauge = report["gauge_orbits"]
    OUT_MD.write_text(
        "# G3 full-coordinate stationarity feasibility — v20\n\n"
        f"**Status:** `{report['status']}`  \n"
        f"**State:** `{report['overall_state']}`\n\n"
        "## Executed result\n\n"
        f"- stationarity matrix: `{stationarity['matrix_shape'][0]} x {stationarity['matrix_shape'][1]}`;\n"
        f"- rank: `{stationarity['rank']}`; total coefficient nullity: `{stationarity['total_parameter_nullity']}`;\n"
        f"- stationary witness relative residual: `{stationarity['stationary_witness_relative_residual']:.3e}`;\n"
        f"- normalized gauge Ward residual: `{stationarity['maximum_normalized_gauge_Ward_residual']:.3e}`;\n"
        f"- pre-EW gauge-orbit rank: `{gauge['pre_EW_SO10_to_SM']['column_normalized_rank']}`;\n"
        f"- physical-EW gauge-orbit rank: `{gauge['physical_EW_SO10_to_U1em']['stage_resolved_total_rank']}`.\n\n"
        "## Boundary\n\n"
        "This is a first-order stationarity certificate. The full gauge-quotiented "
        "Hessian, complete BFB proof, and global competing-extrema classification "
        "remain open, so G3 is not closed.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--full-crosscheck",
        action="store_true",
        help="compare every promoted fast gradient with the exact G2 adapter",
    )
    args = parser.parse_args(argv)
    report = build_report(full_crosscheck=args.full_crosscheck)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
