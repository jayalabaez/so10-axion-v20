#!/usr/bin/env python3
"""Exact 486-real derivatives for Phi^2 Hdag Sigma in the 210 and 1050 channels.

The live ledger orientation is the conjugate of the natural source pairing

    V_R = <P_R(B), P_R(E)>,
    I_R = conjugate(V_R),

with B = phi2_bilinear(Phi, Phi), E = H ⊗ Sigma^dag, and P_210 = J J^dag / 3,
P_1050 = I - P_210.  At fixed Sigma/H the Phi block is the real quadratic form
defined by the polarized bilinear; H and Sigma enter linearly through E.

G2 and downstream gates remain fail-closed.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np

import exact_phi2_h_126dag_210_1050_channels_v20 as source
import exact_phisigma_casimir_projectors_v20 as casimir
import live_g1_tensor_closure_ledger_v20 as ledger
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as quadratic

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_EXACT_PHI2_HDAG_SIGMA_DERIVATIVES_V20.json"
OUT_MD = ROOT / "LIVE_G2_EXACT_PHI2_HDAG_SIGMA_DERIVATIVES_V20.md"
BASE_FAMILY = "Phi2_Hdag_Sigma"
BASIS_LABELS = ("210", "1050")
PROJECTORS: tuple[Callable[[np.ndarray, int], np.ndarray], ...] = (
    source.project_210,
    source.project_1050,
)


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
def basis_bilinear_tables() -> tuple[np.ndarray, ...]:
    """Sparse-friendly cache of phi2_bilinear(e_a, e_b) for a <= b."""
    tables: list[np.ndarray | None] = [None] * (chart.PHI_DIM * (chart.PHI_DIM + 1) // 2)
    index = 0
    for left in range(chart.PHI_DIM):
        left_form = {casimir.FOUR_INDICES[left]: 1.0 + 0.0j}
        for right in range(left, chart.PHI_DIM):
            right_form = {casimir.FOUR_INDICES[right]: 1.0 + 0.0j}
            tables[index] = source.phi2_bilinear(left_form, right_form, +1)
            index += 1
    return tuple(tables)  # type: ignore[return-value]


def _pair_index(left: int, right: int) -> int:
    if right < left:
        left, right = right, left
    return left * chart.PHI_DIM - left * (left - 1) // 2 + (right - left)


def mass_matrix(force: np.ndarray) -> np.ndarray:
    """M with <bilinear(phi,phi), F> = phi^T M phi for real phi."""
    tables = basis_bilinear_tables()
    matrix = np.zeros((chart.PHI_DIM, chart.PHI_DIM), dtype=complex)
    for left in range(chart.PHI_DIM):
        for right in range(left, chart.PHI_DIM):
            value = np.vdot(tables[_pair_index(left, right)], force)
            matrix[left, right] = value
            matrix[right, left] = value
    return matrix


@lru_cache(maxsize=1)
def sigma_dag_jacobian() -> np.ndarray:
    """Complex Jacobian d(five_to_vector(conj(sigma)))/d q_sigma."""
    jacobian = np.zeros((len(source.C5), chart.SIGMA_REAL_DIM), dtype=complex)
    for column in range(chart.SIGMA_REAL_DIM):
        coordinates = np.zeros(chart.SIGMA_REAL_DIM, dtype=float)
        coordinates[column] = 1.0
        sigma = chart.sigma_from_coordinates(
            chart._unpack_complex_interleaved(coordinates)
        )
        jacobian[:, column] = source.five_to_vector(
            potential.conjugate_form(sigma)
        )
    return jacobian


def base_derivative(
    q: np.ndarray, basis_index: int
) -> tuple[complex, np.ndarray, np.ndarray]:
    index = int(basis_index)
    if index not in (0, 1):
        raise KeyError(f"unknown {BASE_FAMILY} basis index {basis_index}")
    coordinates = np.asarray(q, dtype=float).reshape(chart.TOTAL_DIM)
    phi = coordinates[chart.PHI_SLICE].astype(float, copy=False)
    h_block = coordinates[chart.H_SLICE]
    h = chart._unpack_complex_interleaved(h_block)
    sigma = chart.sigma_from_coordinates(
        chart._unpack_complex_interleaved(coordinates[chart.SIGMA_SLICE])
    )
    sigma_dag = potential.conjugate_form(sigma)
    sigma_dag_vector = source.five_to_vector(sigma_dag)

    state_phi = {
        indices: complex(phi[offset])
        for offset, indices in enumerate(casimir.FOUR_INDICES)
        if abs(phi[offset]) > 1.0e-15
    }
    bilinear = source.phi2_bilinear(state_phi, state_phi, +1)
    external = h[:, None] * sigma_dag_vector[None, :]
    projector = PROJECTORS[index]
    projected_bilinear = projector(bilinear, +1)
    projected_external = projector(external, +1)
    source_value = complex(np.vdot(projected_bilinear, projected_external))
    value = complex(np.conjugate(source_value))
    force = projector(external, +1)
    mass = mass_matrix(force)

    # Phi block of V = phi^T mass phi; I = conj(V).
    value_phi = complex(phi @ mass @ phi)
    if abs(value_phi - source_value) > 1.0e-8:
        raise AssertionError(
            f"{BASIS_LABELS[index]} phi-quadratic residual {abs(value_phi - source_value)}"
        )

    gradient = np.zeros(chart.TOTAL_DIM, dtype=complex)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=complex)
    gradient_phi_V = 2.0 * (mass @ phi)
    gradient[chart.PHI_SLICE] = np.conjugate(gradient_phi_V)
    hessian[chart.PHI_SLICE, chart.PHI_SLICE] = np.conjugate(2.0 * mass)

    # V = sum_k h_k * vdot(G[k], sd) with G = P(B).
    G = projected_bilinear
    u = np.asarray(
        [np.vdot(G[vector_index], sigma_dag_vector) for vector_index in range(10)],
        dtype=complex,
    )
    # dV/dx_k = u_k/sqrt(2), dV/dy_k = i u_k/sqrt(2); I = conj(V).
    scale = 1.0 / np.sqrt(2.0)
    for vector_index in range(10):
        gradient[chart.H_SLICE.start + 2 * vector_index] = np.conjugate(
            scale * u[vector_index]
        )
        gradient[chart.H_SLICE.start + 2 * vector_index + 1] = np.conjugate(
            1j * scale * u[vector_index]
        )

    # V = sum_alpha sd_alpha * vdot(G[:,alpha], h)
    dual = np.asarray(
        [np.vdot(G[:, alpha], h) for alpha in range(len(source.C5))],
        dtype=complex,
    )
    sigma_jac = sigma_dag_jacobian()
    gradient_sigma_V = sigma_jac.conj().T @ dual
    # Wait: V = sum_alpha sd_alpha * r_alpha with r_alpha = vdot(G[:,alpha], h)
    # Actually vdot(G[:,alpha], h) = sum_k conj(G[k,alpha]) h_k
    # V = sum_{k,alpha} conj(G[k,alpha]) h_k sd_alpha = sum_alpha sd_alpha * sum_k conj(G[k,alpha]) h_k
    # so r_alpha = sum_k conj(G[k,alpha]) h_k = vdot(G[:,alpha], h) yes.
    # dV/dq = sum_alpha r_alpha * d sd_alpha / dq = sigma_jac.T @ r  (no conj on jac if r weights sd)
    gradient_sigma_V = sigma_jac.T @ dual
    gradient[chart.SIGMA_SLICE] = np.conjugate(gradient_sigma_V)

    # Mixed / equal-field Hessians from product rule on V = <P(B), E>.
    # Phi-H: d/dphi_a of u_k = vdot(P(dB_a)[k], sd); dB_a = 2 bilinear(e_a, phi)
    tables = basis_bilinear_tables()
    for phi_index in range(chart.PHI_DIM):
        dB = np.zeros_like(bilinear)
        for other in range(chart.PHI_DIM):
            dB += 2.0 * phi[other] * tables[_pair_index(phi_index, other)]
        dG = projector(dB, +1)
        du = np.asarray(
            [np.vdot(dG[vector_index], sigma_dag_vector) for vector_index in range(10)],
            dtype=complex,
        )
        for vector_index in range(10):
            hessian[
                chart.PHI_SLICE.start + phi_index,
                chart.H_SLICE.start + 2 * vector_index,
            ] = np.conjugate(scale * du[vector_index])
            hessian[
                chart.H_SLICE.start + 2 * vector_index,
                chart.PHI_SLICE.start + phi_index,
            ] = np.conjugate(scale * du[vector_index])
            hessian[
                chart.PHI_SLICE.start + phi_index,
                chart.H_SLICE.start + 2 * vector_index + 1,
            ] = np.conjugate(1j * scale * du[vector_index])
            hessian[
                chart.H_SLICE.start + 2 * vector_index + 1,
                chart.PHI_SLICE.start + phi_index,
            ] = np.conjugate(1j * scale * du[vector_index])
        d_dual = np.asarray(
            [np.vdot(dG[:, alpha], h) for alpha in range(len(source.C5))],
            dtype=complex,
        )
        cross_sigma = np.conjugate(sigma_jac.T @ d_dual)
        hessian[chart.PHI_SLICE.start + phi_index, chart.SIGMA_SLICE] = cross_sigma
        hessian[chart.SIGMA_SLICE, chart.PHI_SLICE.start + phi_index] = cross_sigma

    # H-Sigma cross and H-H / Sigma-Sigma from V = h · (jac_parts).
    # V = sum_k h_k (G[k] vdot sd) = sum_k,alpha conj(G[k,alpha]) h_k sd_alpha
    # Pure H Hessian vanishes (linear in h). Pure Sigma Hessian vanishes (linear in sd).
    # Cross: d^2 V / (dh_k d q_i) = conj(G[k]) · d sd / dq_i
    for vector_index in range(10):
        row = np.conjugate(G[vector_index])  # coefficients of sd in u_k's vdot sense?
        # u_k = vdot(G[k], sd) = sum_alpha conj(G[k,alpha]) sd_alpha
        # du_k / dq = sigma_jac.T @ conj(G[k]) ? 
        # d u_k / dq = sum_alpha conj(G[k,alpha]) * d sd_alpha/dq = sigma_jac.T @ conj(G[k,:])
        du_dq = sigma_jac.T @ np.conjugate(G[vector_index])
        hessian[chart.H_SLICE.start + 2 * vector_index, chart.SIGMA_SLICE] = np.conjugate(
            scale * du_dq
        )
        hessian[chart.SIGMA_SLICE, chart.H_SLICE.start + 2 * vector_index] = np.conjugate(
            scale * du_dq
        )
        hessian[
            chart.H_SLICE.start + 2 * vector_index + 1, chart.SIGMA_SLICE
        ] = np.conjugate(1j * scale * du_dq)
        hessian[
            chart.SIGMA_SLICE, chart.H_SLICE.start + 2 * vector_index + 1
        ] = np.conjugate(1j * scale * du_dq)

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
    expected = potential._phi2_hdag_sigma_values(state, dense)
    residuals = {
        label: float(abs(base_derivative(q, index)[0] - expected[index]))
        for index, label in enumerate(BASIS_LABELS)
    }
    return {
        "source_values": expected,
        "residuals": residuals,
        "maximum_residual": max(residuals.values()),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    state = potential.deterministic_state(3707)
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
    basis_labels = [
        row.basis_label for row in sorted(directions, key=lambda row: row.basis_index)
    ]
    normalization = source_normalization_audit(state)
    hessian_asymmetry = max(
        float(np.max(np.abs(row.hessian - row.hessian.T))) for row in analytic
    )
    checks = {
        "authoritative_family_id_exists": BASE_FAMILY
        in {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "observed_direction_count_matches_G1": len(analytic)
        == expected_direction_count(),
        "basis_labels_match": basis_labels == list(BASIS_LABELS),
        "values_match_authoritative_source": normalization["maximum_residual"]
        < 1.0e-10,
        "all_values_match_authoritative_evaluator": max(value_residuals.values())
        < 1.0e-10,
        "all_dense_Hessians_symmetric": hessian_asymmetry < 1.0e-10,
        "five_point_value_reconstruction": directional["value_residual"] < 1.0e-8,
        "five_point_first_derivative_reconstruction": directional["first_residual"]
        < 5.0e-6,
        "five_point_second_derivative_reconstruction": directional["second_residual"]
        < 5.0e-5,
        "G2_not_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "G2_EXACT_PHI2_HDAG_SIGMA_DERIVATIVES_CLOSED"
                if not failures
                else "G2_PHI2_HDAG_SIGMA_DERIVATIVES_FAILED"
            ),
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "coverage": {
                "base_family": BASE_FAMILY,
                "expected_direction_count": expected_direction_count(),
                "observed_direction_count": len(analytic),
                "parameter_count_closed_here": len(parameters),
                "basis_labels": basis_labels,
                "real_field_dimension": chart.TOTAL_DIM,
            },
            "projector_normalization_audit": normalization,
            "maximum_direction_value_residual": max(value_residuals.values()),
            "maximum_Hessian_asymmetry": hessian_asymmetry,
            "directional_reconstruction": directional,
            "flags": {
                "authoritative_Phi2_Hdag_Sigma_adapter_closed": not failures,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "verdict": (
                "The Phi^2 Hdag Sigma 210/1050 channels now have exact dense "
                "486-real derivatives in the ledger conjugation convention. G2 "
                "remains PARTIAL."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Exact Phi2 Hdag Sigma derivatives\n\n"
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
