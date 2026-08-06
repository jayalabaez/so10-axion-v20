#!/usr/bin/env python3
"""Exact 486-real derivatives for both H--126bar Hermitian quartics.

The authoritative G1 family ``H_Sigma_hermitian`` contains

    I_1  = (Hdag H) K_Sigma,
    I_45 = <J_H^(45), J_Sigma^(45)>,

with K_Sigma=(1/2)<Sigma,Sigma>.  The 45 channel is constructed from the exact
anti-Hermitian SO(10) generator matrices in the complex 10 and kinetic-
orthonormal physical 126bar bases.  Each current is a complex quadratic form in
canonical real coordinates; their Hermitian contraction therefore has exact
product-rule gradients and Hessians.

All authoritative live directions and singlet dressings are included.  This
closes one quartic base-family adapter only.  Across the stacked chain eleven
of eighteen adapters are targeted; seven families and G2 remain open.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_mixed_45_triplet_channel_v20 as current45
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_HSIGMA_HERMITIAN_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_HSIGMA_HERMITIAN_DERIVATIVES_V20.md"
BASE_FAMILY = "H_Sigma_hermitian"
BASIS_LABELS = ("channel_1", "channel_45")
PAIRS = tuple(current45.PAIRS)


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


def conjugate_form(form: direct.Form) -> direct.Form:
    return {indices: np.conjugate(value) for indices, value in form.items()}


@lru_cache(maxsize=1)
def h_generator_matrices() -> np.ndarray:
    return np.asarray(
        [current45.generator_matrix(*pair) for pair in PAIRS],
        dtype=complex,
    )


@lru_cache(maxsize=1)
def sigma_generator_matrices() -> np.ndarray:
    basis = chart.sigma_basis()
    matrices = np.empty(
        (len(PAIRS), chart.SIGMA_COMPLEX_DIM, chart.SIGMA_COMPLEX_DIM),
        dtype=complex,
    )
    for generator_index, pair in enumerate(PAIRS):
        for source_index, source_state in enumerate(basis):
            image = current45.generator_action(source_state, *pair)
            matrices[generator_index, :, source_index] = np.asarray(
                [
                    direct.sigma_kinetic_inner(target_state, image)
                    for target_state in basis
                ],
                dtype=complex,
            )
    return matrices


def canonical_quadratic_hessian(matrix: np.ndarray) -> np.ndarray:
    """H such that zdag A z=(1/2)q^T H q for z=(x+i y)/sqrt(2)."""
    value = np.asarray(matrix, dtype=complex)
    dimension = value.shape[0]
    if value.shape != (dimension, dimension):
        raise ValueError("quadratic matrix must be square")
    c = np.zeros((2 * dimension, 2 * dimension), dtype=complex)
    x = 2 * np.arange(dimension)
    y = x + 1
    c[np.ix_(x, x)] = 0.5 * value
    c[np.ix_(x, y)] = 0.5j * value
    c[np.ix_(y, x)] = -0.5j * value
    c[np.ix_(y, y)] = 0.5 * value
    return c + c.T


@lru_cache(maxsize=1)
def current_hessians() -> tuple[np.ndarray, np.ndarray]:
    h = np.asarray(
        [canonical_quadratic_hessian(matrix) for matrix in h_generator_matrices()]
    )
    sigma = np.asarray(
        [
            canonical_quadratic_hessian(matrix)
            for matrix in sigma_generator_matrices()
        ]
    )
    return h, sigma


def _channel_1_derivative(q: np.ndarray) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    h = coordinates[chart.H_SLICE]
    sigma = coordinates[chart.SIGMA_SLICE]
    n_h = 0.5 * float(np.dot(h, h))
    n_sigma = 0.5 * float(np.dot(sigma, sigma))
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.H_SLICE] = n_sigma * h
    gradient[chart.SIGMA_SLICE] = n_h * sigma
    hessian[chart.H_SLICE, chart.H_SLICE] = n_sigma * np.eye(chart.H_REAL_DIM)
    hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = n_h * np.eye(
        chart.SIGMA_REAL_DIM
    )
    cross = np.outer(h, sigma)
    hessian[chart.H_SLICE, chart.SIGMA_SLICE] = cross
    hessian[chart.SIGMA_SLICE, chart.H_SLICE] = cross.T
    return complex(n_h * n_sigma), gradient, hessian


def _channel_45_derivative(q: np.ndarray) -> tuple[complex, np.ndarray, np.ndarray]:
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    h = coordinates[chart.H_SLICE]
    sigma = coordinates[chart.SIGMA_SLICE]
    h_matrices, sigma_matrices = current_hessians()
    h_currents = 0.5 * np.einsum("i,gij,j->g", h, h_matrices, h, optimize=True)
    sigma_currents = 0.5 * np.einsum(
        "i,gij,j->g", sigma, sigma_matrices, sigma, optimize=True
    )
    h_images = np.einsum("gij,j->gi", h_matrices, h, optimize=True)
    sigma_images = np.einsum(
        "gij,j->gi", sigma_matrices, sigma, optimize=True
    )
    value = np.vdot(h_currents, sigma_currents)
    gradient_h = np.einsum(
        "g,gi->i", sigma_currents, np.conjugate(h_images), optimize=True
    )
    gradient_sigma = np.einsum(
        "g,gi->i", np.conjugate(h_currents), sigma_images, optimize=True
    )
    hessian_h = np.einsum(
        "g,gij->ij", sigma_currents, np.conjugate(h_matrices), optimize=True
    )
    hessian_sigma = np.einsum(
        "g,gij->ij", np.conjugate(h_currents), sigma_matrices, optimize=True
    )
    cross = np.einsum(
        "gi,gj->ij", np.conjugate(h_images), sigma_images, optimize=True
    )

    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.H_SLICE] = gradient_h
    gradient[chart.SIGMA_SLICE] = gradient_sigma
    hessian[chart.H_SLICE, chart.H_SLICE] = hessian_h
    hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = hessian_sigma
    hessian[chart.H_SLICE, chart.SIGMA_SLICE] = cross
    hessian[chart.SIGMA_SLICE, chart.H_SLICE] = cross.T
    return complex(value), gradient, 0.5 * (hessian + hessian.T)


def base_derivative(
    q: np.ndarray, basis_index: int
) -> tuple[complex, np.ndarray, np.ndarray]:
    if int(basis_index) == 0:
        return _channel_1_derivative(q)
    if int(basis_index) == 1:
        return _channel_45_derivative(q)
    raise KeyError(f"unknown H-Sigma basis index {basis_index}")


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


def direct_source_values(state: potential.FieldState) -> dict[str, complex]:
    h_form = {
        (index,): complex(value)
        for index, value in enumerate(state.h)
        if abs(value) > 1.0e-14
    }
    h_current = current45.hermitian_current_45(h_form, kinetic_factor=1.0)
    sigma_current = current45.hermitian_current_45(
        state.sigma, kinetic_factor=0.5
    )
    return {
        "channel_1": complex(
            np.vdot(state.h, state.h)
            * direct.sigma_kinetic_inner(state.sigma, state.sigma)
        ),
        "channel_45": complex(direct.tensor_inner(h_current, sigma_current)),
    }


def expected_direction_count() -> int:
    g1 = ledger.build_report()
    return sum(
        int(orbit["multiplicity"])
        for orbit in g1["operator_orbits"]
        if orbit["base_family"] == BASE_FAMILY
    )


def generator_audit() -> dict[str, Any]:
    h = h_generator_matrices()
    sigma = sigma_generator_matrices()
    h_anti = float(np.max(np.abs(h + np.swapaxes(h.conj(), 1, 2))))
    sigma_anti = float(
        np.max(np.abs(sigma + np.swapaxes(sigma.conj(), 1, 2)))
    )
    h_hess, sigma_hess = current_hessians()
    return {
        "generator_count": len(PAIRS),
        "H_shape": list(h.shape),
        "Sigma_shape": list(sigma.shape),
        "H_anti_Hermiticity_residual": h_anti,
        "Sigma_anti_Hermiticity_residual": sigma_anti,
        "H_current_Hessian_symmetry_residual": float(
            np.max(np.abs(h_hess - np.swapaxes(h_hess, 1, 2)))
        ),
        "Sigma_current_Hessian_symmetry_residual": float(
            np.max(np.abs(sigma_hess - np.swapaxes(sigma_hess, 1, 2)))
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(2904)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    coefficients = quadratic.deterministic_coefficients(parameters)
    directional = quadratic.five_point_directional_audit(
        state, parameters, coefficients
    )
    source_values = direct_source_values(state)
    base_value_residuals = {
        label: float(abs(base_derivative(q, index)[0] - source_values[label]))
        for index, label in enumerate(BASIS_LABELS)
    }
    expected = {row.direction_id: row for row in directions}
    dressed_value_residuals = {
        row.direction_id: float(abs(row.value - expected[row.direction_id].value))
        for row in analytic
    }
    expected_count = expected_direction_count()
    basis_indices = sorted({row.basis_index for row in directions})
    basis_labels = sorted({row.basis_label for row in directions})
    generators = generator_audit()
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
        "both_basis_indices_present": basis_indices == [0, 1],
        "both_basis_labels_present": basis_labels == sorted(BASIS_LABELS),
        "45_H_generators_anti_Hermitian": generators[
            "H_anti_Hermiticity_residual"
        ] < 1.0e-12,
        "45_Sigma_generators_anti_Hermitian": generators[
            "Sigma_anti_Hermiticity_residual"
        ] < 1.0e-11,
        "current_real_coordinate_Hessians_symmetric": max(
            generators["H_current_Hessian_symmetry_residual"],
            generators["Sigma_current_Hessian_symmetry_residual"],
        ) < 1.0e-12,
        "both_base_values_match_direct_current_source": max(
            base_value_residuals.values()
        ) < 1.0e-9,
        "all_dressed_values_match_authoritative_evaluator": max(
            dressed_value_residuals.values()
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
        "remaining_7_base_families_not_claimed": True,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_HSIGMA_HERMITIAN_DERIVATIVES_CLOSED"
                if not failures
                else "G2_HSIGMA_HERMITIAN_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_family": BASE_FAMILY,
                "base_family_count_closed_here": 1,
                "cumulative_base_family_count_with_parents": 11,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "remaining_base_families": 7,
                "expected_direction_count": expected_count,
                "observed_direction_count": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "basis_indices": basis_indices,
                "basis_labels": basis_labels,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "generator_audit": generators,
            "base_source_value_residuals": base_value_residuals,
            "maximum_base_source_value_residual": max(
                base_value_residuals.values()
            ),
            "maximum_dressed_value_residual": max(
                dressed_value_residuals.values()
            ),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "flags": {
                "H_Sigma_channel_1_derivatives_exact": not failures,
                "H_Sigma_channel_45_derivatives_exact": not failures,
                "authoritative_H_Sigma_adapter_closed": not failures,
                "cumulative_eleven_of_eighteen_base_adapters_closed": not failures,
                "all_64_direction_gradients_complete": False,
                "all_64_direction_Hessians_complete": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate Phi2_HdagH_channels, then the remaining 126bar and "
                "Phi projector quartics."
            ),
            "verdict": (
                "Both H--126bar Hermitian quartics now have exact dense derivatives "
                "from the canonical 45-current representation. Seven base-family "
                "adapters remain and G2 is still PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact H--126bar Hermitian quartic derivatives\n\n"
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
