#!/usr/bin/env python3
"""Exact 486-real derivatives for the six Phi^2 Sigma Sigmadag projector channels.

The authoritative live evaluator uses the pure-irrep projector path

    I_c = sigma^dagger O_c(Phi) sigma,
    O_c = full_sigma_operator(Pi_c(phi phi^T)),

not the graph six-contraction basis.  The Frobenius dual

    Q = sum_v (B_v sigma)(B_v sigma)^dagger,
    I_c = phi^T Pi_c(Q) phi

makes the Phi block a plain quadratic form at fixed Sigma, while the Sigma
block remains the Hermitian quadratic form defined by O_c.  Cross derivatives
use the linearized pair map through Pi_c and full_sigma_operator.

This closes one quartic base-family adapter only.  G2 and downstream gates stay
fail-closed.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import exact_phisigma_126bar_minus_projectors_v20 as projector_source
import exact_phisigma_casimir_projectors_v20 as casimir
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_PHI2_SIGMA_SIGMADAG_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_PHI2_SIGMA_SIGMADAG_DERIVATIVES_V20.md"
BASE_FAMILY = "Phi2_Sigma_Sigmadag"
BASIS_LABELS = potential.PHISIGMA_ORDER


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


def hermitian_realification(matrix: np.ndarray) -> np.ndarray:
    """R with z^dagger M z = (1/2) q^T R q for Hermitian M and z=(x+iy)/sqrt(2)."""
    value = np.asarray(matrix, dtype=complex)
    dim = value.shape[0]
    output = np.zeros((2 * dim, 2 * dim), dtype=float)
    x = 2 * np.arange(dim)
    y = x + 1
    output[np.ix_(x, x)] = value.real
    output[np.ix_(x, y)] = -value.imag
    output[np.ix_(y, x)] = value.imag
    output[np.ix_(y, y)] = value.real
    return output


def sigma_density_matrix(sigma: np.ndarray) -> np.ndarray:
    """Q with I=<P,Q> for I=sum_v w^dagger P w, w=B_v sigma."""
    vector = np.asarray(sigma, dtype=complex).reshape(chart.SIGMA_COMPLEX_DIM)
    tensor = projector_source.full_contraction_tensor()
    density = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=complex)
    for block in tensor:
        image = block @ vector
        density += np.outer(np.conjugate(image), image)
    return 0.5 * (density + density.conj().T)


def project_channel(pair: np.ndarray, label: str) -> np.ndarray:
    eigenvalue = casimir.COMMON_CHANNEL_EIGENVALUES[label]
    powers = casimir.casimir_powers(np.asarray(pair, dtype=complex))
    return casimir.project_from_powers(powers, eigenvalue)


def base_derivative(
    q: np.ndarray, basis_index: int
) -> tuple[complex, np.ndarray, np.ndarray]:
    index = int(basis_index)
    if index not in range(len(BASIS_LABELS)):
        raise KeyError(f"unknown {BASE_FAMILY} basis index {basis_index}")
    label = BASIS_LABELS[index]
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi = coordinates[chart.PHI_SLICE].astype(float, copy=False)
    sigma_block = coordinates[chart.SIGMA_SLICE]
    sigma = chart._unpack_complex_interleaved(sigma_block)

    pair = np.outer(phi, phi)
    projected_pair = project_channel(pair, label)
    operator = projector_source.full_sigma_operator(projected_pair)
    density = sigma_density_matrix(sigma)
    mass = np.real(project_channel(density, label))

    value = complex(float(phi @ mass @ phi))
    operator_value = complex(np.vdot(sigma, operator @ sigma))
    if abs(value - operator_value) > 1.0e-8:
        raise AssertionError(
            f"{label} dual/operator residual {abs(value - operator_value)}"
        )

    real_operator = hermitian_realification(operator)
    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient[chart.PHI_SLICE] = 2.0 * (mass @ phi)
    gradient[chart.SIGMA_SLICE] = real_operator @ sigma_block
    hessian[chart.PHI_SLICE, chart.PHI_SLICE] = 2.0 * mass
    hessian[chart.SIGMA_SLICE, chart.SIGMA_SLICE] = real_operator

    eye = np.eye(chart.PHI_DIM)
    for phi_index in range(chart.PHI_DIM):
        variation = np.outer(phi, eye[phi_index]) + np.outer(eye[phi_index], phi)
        d_operator = projector_source.full_sigma_operator(
            project_channel(variation, label)
        )
        cross = hermitian_realification(d_operator) @ sigma_block
        hessian[chart.PHI_SLICE.start + phi_index, chart.SIGMA_SLICE] = cross
        hessian[chart.SIGMA_SLICE, chart.PHI_SLICE.start + phi_index] = cross
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


def expected_direction_count() -> int:
    return sum(
        int(orbit["multiplicity"])
        for orbit in ledger.build_report()["operator_orbits"]
        if orbit["base_family"] == BASE_FAMILY
    )


def source_normalization_audit(state: potential.FieldState) -> dict[str, Any]:
    q = chart.pack(state)
    dense = potential._dense_state(state)
    expected = potential._phi2_sigma_pure_values(state, dense)
    residuals = {
        label: float(abs(base_derivative(q, index)[0] - expected[index]))
        for index, label in enumerate(BASIS_LABELS)
    }
    return {
        "source_values": expected,
        "residuals": residuals,
        "maximum_residual": max(residuals.values()),
    }


def base_support_audit(q: np.ndarray) -> dict[str, dict[str, float]]:
    active = np.zeros(chart.TOTAL_DIM, dtype=bool)
    active[chart.PHI_SLICE] = True
    active[chart.SIGMA_SLICE] = True
    inactive = ~active
    output: dict[str, dict[str, float]] = {}
    for index, label in enumerate(BASIS_LABELS):
        _, gradient, hessian = base_derivative(q, index)
        output[label] = {
            "inactive_gradient_residual": float(
                np.max(np.abs(gradient[inactive]), initial=0.0)
            ),
            "inactive_Hessian_residual": float(
                max(
                    np.max(np.abs(hessian[inactive, :]), initial=0.0),
                    np.max(np.abs(hessian[:, inactive]), initial=0.0),
                )
            ),
        }
    return output


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3606)
    q = chart.pack(state)
    directions = selected_directions(state)
    analytic = all_direction_derivatives(state)
    parameters = quadratic.parameter_derivatives(analytic)
    directional = quadratic.five_point_directional_audit(
        state, parameters, quadratic.deterministic_coefficients(parameters)
    )
    expected = {row.direction_id: row for row in directions}
    value_residuals = {
        row.direction_id: float(abs(row.value - expected[row.direction_id].value))
        for row in analytic
    }
    basis_indices = sorted({row.basis_index for row in directions})
    basis_labels = [row.basis_label for row in sorted(directions, key=lambda r: r.basis_index)]
    expected_count = expected_direction_count()
    normalization = source_normalization_audit(state)
    support = base_support_audit(q)
    support_residual = max(max(row.values()) for row in support.values())
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
    checks = {
        "authoritative_family_id_exists": BASE_FAMILY
        in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "expected_G1_direction_count_is_nonzero": expected_count > 0,
        "observed_direction_count_matches_G1": len(analytic) == expected_count,
        "all_basis_indices_present": basis_indices == list(range(len(BASIS_LABELS))),
        "all_basis_labels_present": basis_labels == list(BASIS_LABELS),
        "projector_values_match_authoritative_source": normalization[
            "maximum_residual"
        ]
        < 1.0e-10,
        "all_values_match_authoritative_evaluator": max(value_residuals.values())
        < 1.0e-10,
        "base_derivatives_supported_only_on_Phi_Sigma": support_residual < 1.0e-10,
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-10,
        "self_conjugate_derivatives_real": self_imaginary < 1.0e-9,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-8,
        "five_point_first_derivative_reconstruction": directional["first_residual"]
        < 2.0e-6,
        "five_point_second_derivative_reconstruction": directional["second_residual"]
        < 2.0e-5,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_PHI2_SIGMA_SIGMADAG_DERIVATIVES_CLOSED"
                if not failures
                else "G2_PHI2_SIGMA_SIGMADAG_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_family": BASE_FAMILY,
                "base_family_count_closed_here": 1,
                "base_family_count_total": len(ledger.BASE_FAMILIES),
                "expected_direction_count": expected_count,
                "observed_direction_count": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "basis_indices": basis_indices,
                "basis_labels": basis_labels,
                "real_field_dimension": chart.TOTAL_DIM,
                "Hessian_shape": [chart.TOTAL_DIM, chart.TOTAL_DIM],
            },
            "projector_normalization_audit": normalization,
            "base_support_audit": support,
            "maximum_base_support_residual": support_residual,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "maximum_self_conjugate_imaginary_residual": self_imaginary,
            "directional_reconstruction": directional,
            "flags": {
                "authoritative_Phi2_Sigma_Sigmadag_adapter_closed": not failures,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "verdict": (
                "The six Phi^2--Sigma projector channels now have exact dense "
                "486-real derivatives via the dual Casimir identity. G2 remains "
                "PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact Phi2 Sigma Sigmadag derivatives\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
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
