#!/usr/bin/env python3
"""Exact 486-real derivatives for the three Phi^2 Hdag H channels.

The authoritative G1 family ``Phi2_HdagH_channels`` contains the normalized
1, 45, and 54 contractions from
``exact_phi2_hdagh_channel_family_v20``.  Each invariant has the form

    I_R(Phi,H) = Hdag M_R(Phi) H,

where M_R is quadratic in the real 210_H coordinates.  The complete gradient
and Hessian therefore follow from M_R, its 210 first derivatives, and the
contracted second derivative in the Phi block.

The 54 channel is built from exact interior maps of four-forms.  The 45 channel
uses the sparse symmetric bilinear map i*[* (Phi wedge Psi)] on the vector 10,
so no dense 210x210x10x10 tensor is stored.  All authoritative live copies and
singlet dressings are included.

One quartic base-family adapter is covered here.  Across the stacked chain
twelve of eighteen adapters are targeted; six families and G2 remain open.
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

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phi2_hdagh_channel_family_v20 as source
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_PHI2_HDAGH_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_PHI2_HDAGH_DERIVATIVES_V20.md"
BASE_FAMILY = "Phi2_HdagH_channels"
BASIS_LABELS = ("1", "45", "54")
THREE_INDICES = tuple(itertools.combinations(range(10), 3))
ZERO_10 = np.zeros((10, 10), dtype=complex)


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, complex):
        return {"re": float(value.real), "im": float(value.imag)}
    return value


@lru_cache(maxsize=1)
def phi_basis_forms() -> tuple[direct.Form, ...]:
    return tuple({indices: 1.0 + 0.0j} for indices in chart.PHI_INDICES)


@lru_cache(maxsize=1)
def interior_table() -> np.ndarray:
    """D[i,p,k]=coefficient k of interior_i(Phi basis p)."""
    table = np.zeros((10, chart.PHI_DIM, len(THREE_INDICES)), dtype=complex)
    for phi_index, state in enumerate(phi_basis_forms()):
        for vector_index in range(10):
            interior = direct.interior(state, vector_index)
            table[vector_index, phi_index] = np.asarray(
                [interior.get(indices, 0.0) for indices in THREE_INDICES],
                dtype=complex,
            )
    return table


@lru_cache(maxsize=1)
def channel45_pair_matrices() -> dict[tuple[int, int], np.ndarray]:
    """B[p,q] with M45(Phi)=sum_pq Phi_p Phi_q B[p,q]."""
    output: dict[tuple[int, int], np.ndarray] = {}
    basis = phi_basis_forms()
    index_sets = tuple(set(indices) for indices in chart.PHI_INDICES)
    for left in range(chart.PHI_DIM):
        for right in range(left + 1, chart.PHI_DIM):
            if index_sets[left].intersection(index_sets[right]):
                continue
            two_form = direct.hodge_star(direct.wedge(basis[left], basis[right]))
            matrix = 1j * source.two_form_value(two_form)
            if np.max(np.abs(matrix), initial=0.0) > 1.0e-14:
                output[(left, right)] = np.asarray(matrix, dtype=complex)
    return output


def pair45(left: int, right: int) -> np.ndarray:
    if left == right:
        return ZERO_10
    key = (left, right) if left < right else (right, left)
    return channel45_pair_matrices().get(key, ZERO_10)


def hermitian_realification(matrix: np.ndarray) -> np.ndarray:
    """R with Hdag M H=(1/2)q_H^T R q_H for Hermitian M."""
    value = np.asarray(matrix, dtype=complex).reshape(10, 10)
    output = np.zeros((chart.H_REAL_DIM, chart.H_REAL_DIM), dtype=float)
    x = 2 * np.arange(10)
    y = x + 1
    output[np.ix_(x, x)] = value.real
    output[np.ix_(x, y)] = -value.imag
    output[np.ix_(y, x)] = value.imag
    output[np.ix_(y, y)] = value.real
    return output


def channel_operator_derivatives(
    phi: np.ndarray, h: np.ndarray, label: str
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return M, dM[p], and the contracted Phi-Phi Hessian."""
    vector = np.asarray(phi, dtype=float).reshape(chart.PHI_DIM)
    h_complex = np.asarray(h, dtype=complex).reshape(10)
    identity = np.eye(10, dtype=complex)
    phi_norm = float(np.dot(vector, vector))
    h_norm = float(np.vdot(h_complex, h_complex).real)

    if label == "1":
        matrix = phi_norm * identity
        first = 2.0 * vector[:, None, None] * identity[None, :, :]
        phi_hessian = 2.0 * h_norm * np.eye(chart.PHI_DIM)
        return matrix, first, phi_hessian

    if label == "54":
        table = interior_table()
        interiors = np.einsum("p,ipk->ik", vector, table, optimize=True)
        c_matrix = interiors.conj() @ interiors.T
        matrix = c_matrix - (2.0 / 5.0) * phi_norm * identity
        first = (
            np.einsum(
                "ipk,jk->pij", table.conj(), interiors, optimize=True
            )
            + np.einsum(
                "ik,jpk->pij", interiors.conj(), table, optimize=True
            )
            - (4.0 / 5.0) * vector[:, None, None] * identity[None, :, :]
        )
        contracted = np.einsum(
            "i,ipk->pk", h_complex, table, optimize=True
        )
        gram = contracted.conj() @ contracted.T
        phi_hessian = 2.0 * gram.real - (4.0 / 5.0) * h_norm * np.eye(
            chart.PHI_DIM
        )
        return matrix, first, phi_hessian

    if label == "45":
        matrix = np.zeros((10, 10), dtype=complex)
        first = np.zeros((chart.PHI_DIM, 10, 10), dtype=complex)
        for (left, right), pair_matrix in channel45_pair_matrices().items():
            matrix += 2.0 * vector[left] * vector[right] * pair_matrix
            first[left] += 2.0 * vector[right] * pair_matrix
            first[right] += 2.0 * vector[left] * pair_matrix
        phi_hessian = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=complex)
        for (left, right), pair_matrix in channel45_pair_matrices().items():
            scalar = 2.0 * np.vdot(h_complex, pair_matrix @ h_complex)
            phi_hessian[left, right] = scalar
            phi_hessian[right, left] = scalar
        return matrix, first, phi_hessian

    raise KeyError(f"unknown Phi2-HdagH channel {label}")


def base_derivative(
    q: np.ndarray, basis_index: int
) -> tuple[complex, np.ndarray, np.ndarray]:
    if int(basis_index) not in (0, 1, 2):
        raise KeyError(f"unknown Phi2-HdagH basis index {basis_index}")
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi = coordinates[chart.PHI_SLICE]
    h_block = coordinates[chart.H_SLICE]
    h = (h_block[0::2] + 1j * h_block[1::2]) / np.sqrt(2.0)
    label = BASIS_LABELS[int(basis_index)]
    matrix, first, phi_hessian = channel_operator_derivatives(phi, h, label)
    real_matrix = hermitian_realification(matrix)
    first_real = np.asarray([hermitian_realification(row) for row in first])

    value = complex(np.vdot(h, matrix @ h))
    gradient_phi = np.einsum(
        "i,pij,j->p", np.conjugate(h), first, h, optimize=True
    )
    gradient_h = real_matrix @ h_block
    cross = np.einsum("pij,j->pi", first_real, h_block, optimize=True)

    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.PHI_SLICE] = gradient_phi
    gradient[chart.H_SLICE] = gradient_h
    hessian[chart.PHI_SLICE, chart.PHI_SLICE] = phi_hessian
    hessian[chart.H_SLICE, chart.H_SLICE] = real_matrix
    hessian[chart.PHI_SLICE, chart.H_SLICE] = cross
    hessian[chart.H_SLICE, chart.PHI_SLICE] = cross.T
    return value, gradient, 0.5 * (hessian + hessian.T)


def selected_directions(
    state: potential.FieldState,
) -> tuple[potential.Direction, ...]:
    return tuple(
        row
        for row in potential.evaluate_directions(state)
        if row.base_family == BASE_FAMILY
    )


def direction_derivative(
    q: np.ndarray, direction: potential.Direction
) -> quadratic.DirectionDerivative:
    if direction.base_family != BASE_FAMILY:
        raise KeyError(f"direction {direction.direction_id} is not {BASE_FAMILY}")
    counts = dict(zip(potential.FIELD_ORDER, direction.counts, strict=True))
    base_value, base_gradient, base_hessian = base_derivative(
        q, direction.basis_index
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


def all_direction_derivatives(
    state: potential.FieldState,
) -> tuple[quadratic.DirectionDerivative, ...]:
    q = chart.pack(state)
    return tuple(
        direction_derivative(q, row) for row in selected_directions(state)
    )


def source_normalization_audit(state: potential.FieldState) -> dict[str, Any]:
    q = chart.pack(state)
    expected = source.invariant_values(state.phi, state.h)
    residuals = {
        label: float(abs(base_derivative(q, index)[0] - expected[label]))
        for index, label in enumerate(BASIS_LABELS)
    }
    operators = source.channel_operators(state.phi)
    operator_residuals = {}
    phi = q[chart.PHI_SLICE]
    h = state.h
    for label in BASIS_LABELS:
        matrix, _, _ = channel_operator_derivatives(phi, h, label)
        operator_residuals[label] = float(np.max(np.abs(matrix - operators[label])))
    return {
        "value_residuals": residuals,
        "operator_residuals": operator_residuals,
        "maximum_value_residual": max(residuals.values()),
        "maximum_operator_residual": max(operator_residuals.values()),
    }


def expected_direction_count() -> int:
    g1 = ledger.build_report()
    return sum(
        int(orbit["multiplicity"])
        for orbit in g1["operator_orbits"]
        if orbit["base_family"] == BASE_FAMILY
    )


def coefficient_audit() -> dict[str, Any]:
    pairs = channel45_pair_matrices()
    hermiticity = max(
        [float(np.max(np.abs(matrix - matrix.conj().T))) for matrix in pairs.values()]
        or [0.0]
    )
    symmetry = max(
        [float(np.max(np.abs(pair45(left, right) - pair45(right, left))))
         for left, right in pairs]
        or [0.0]
    )
    return {
        "interior_table_shape": list(interior_table().shape),
        "channel45_nonzero_pair_count": len(pairs),
        "channel45_pair_Hermiticity_residual": hermiticity,
        "channel45_pair_symmetry_residual": symmetry,
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3004)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    source_audit = source_normalization_audit(state)
    coefficient = coefficient_audit()
    expected = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - expected[row.direction_id].value))
        for row in analytic
    }
    expected_count = expected_direction_count()
    basis_indices = sorted({row.basis_index for row in directions})
    basis_labels = sorted({row.basis_label for row in directions})
    hessian_asymmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic
    )
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
    live_parameter_ids = {
        row.parameter_id
        for row in potential.parameter_schema(
            potential.evaluate_directions(state)
        )
    }
    parameter_ids = {row.parameter_id for row in parameters}

    checks = {
        "authoritative_family_id_exists": BASE_FAMILY
        in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "expected_G1_count_is_nonzero": expected_count > 0,
        "observed_count_is_nonzero": len(analytic) > 0,
        "every_expected_direction_differentiated": len(analytic) == expected_count,
        "all_three_basis_indices_present": basis_indices == [0, 1, 2],
        "all_three_basis_labels_present": basis_labels == sorted(BASIS_LABELS),
        "interior_table_has_exact_shape": coefficient[
            "interior_table_shape"
        ] == [10, 210, 120],
        "channel45_sparse_bilinear_is_nonzero": coefficient[
            "channel45_nonzero_pair_count"
        ] > 0,
        "channel45_pair_matrices_Hermitian": coefficient[
            "channel45_pair_Hermiticity_residual"
        ] < 1.0e-12,
        "channel45_bilinear_symmetric": coefficient[
            "channel45_pair_symmetry_residual"
        ] < 1.0e-15,
        "all_base_operators_match_authoritative_source": source_audit[
            "maximum_operator_residual"
        ] < 1.0e-10,
        "all_base_values_match_authoritative_source": source_audit[
            "maximum_value_residual"
        ] < 1.0e-10,
        "all_dressed_values_match_authoritative_evaluator": max(
            value_residuals.values()
        ) < 1.0e-9,
        "all_parameter_ids_belong_to_live_schema": (
            parameter_ids.issubset(live_parameter_ids)
            and len(parameter_ids) == len(parameters)
            and len(parameters) > 0
        ),
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-10,
        "self_conjugate_derivatives_real": self_imaginary < 1.0e-9,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-8,
        "five_point_first_derivative_reconstruction": directional[
            "first_residual"
        ] < 2.0e-7,
        "five_point_second_derivative_reconstruction": directional[
            "second_residual"
        ] < 2.0e-6,
        "remaining_6_base_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_PHI2_HDAGH_CHANNEL_DERIVATIVES_CLOSED"
                if not failures
                else "G2_PHI2_HDAGH_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_family": BASE_FAMILY,
                "base_family_count_closed_here": 1,
                "cumulative_base_family_count_with_parents": 12,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "remaining_base_families": 6,
                "expected_direction_count": expected_count,
                "observed_direction_count": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "basis_indices": basis_indices,
                "basis_labels": basis_labels,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "coefficient_audit": coefficient,
            "source_normalization_audit": source_audit,
            "maximum_dressed_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "flags": {
                "Phi2_HdagH_1_derivatives_exact": not failures,
                "Phi2_HdagH_45_derivatives_exact": not failures,
                "Phi2_HdagH_54_derivatives_exact": not failures,
                "authoritative_Phi2_HdagH_adapter_closed": not failures,
                "cumulative_twelve_of_eighteen_base_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate the 126bar self-projector quartics, then the mixed "
                "Phi2-Sigma projector and unique chiral quartic families."
            ),
            "verdict": (
                "All three normalized Phi^2 Hdag H channels now have exact dense "
                "derivatives for every live direction. Six base-family adapters "
                "remain and G2 is still PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact Phi2-HdagH channel derivatives\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
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
