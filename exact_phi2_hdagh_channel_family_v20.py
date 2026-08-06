#!/usr/bin/env python3
"""Exact renormalizable 210_H^2 10_H^dag 10_H channel family.

For a real four-form Phi in the 210 and a complex vector H in the 10,

    Sym^2(210) intersect (10bar tensor 10) = 1 + 45 + 54,

with multiplicity one in every channel.  This module constructs canonical
all-component representatives for all three channels:

    M_1(Phi)  = ||Phi||^2 I,
    M_54(Phi) = C(Phi) - (2/5)||Phi||^2 I,
    M_45(Phi) = i A(Phi),

where C_ij=<i_i Phi,i_j Phi> and A is the real antisymmetric matrix associated
with *(Phi wedge Phi).  The scalar invariants are H^dag M_Q H.

The formulas use the repository's canonical 210 and 10 kinetic conventions.
They close this finite quartic family only; the complete mixed invariant ring
and full multifield potential remain open.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phisigma_bose_channel_census_v20 as phi_census

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHI2_HDAGH_CHANNEL_FAMILY_V20.json"
OUT_MD = ROOT / "EXACT_PHI2_HDAGH_CHANNEL_FAMILY_V20.md"


def _jsonable(value: Any) -> Any:
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


def vector_generator_matrix(a: int, b: int) -> np.ndarray:
    matrix = np.zeros((10, 10), dtype=float)
    for column in range(10):
        image = direct.generator_action(direct.one_form(column), a, b)
        for (row,), coefficient in image.items():
            if abs(coefficient.imag) > 1.0e-13:
                raise AssertionError("vector generator unexpectedly complex")
            matrix[row, column] = coefficient.real
    return matrix


def _two_form_matrix(form: direct.Form) -> np.ndarray:
    matrix = np.zeros((10, 10), dtype=float)
    for (i, j), coefficient in form.items():
        if len((i, j)) != 2:
            raise AssertionError("expected a two-form")
        if abs(coefficient.imag) > 1.0e-12:
            raise AssertionError("real 210 produced complex 45 channel")
        value = float(coefficient.real)
        matrix[i, j] = value
        matrix[j, i] = -value
    return matrix


def channel_operators(phi: direct.Form) -> dict[str, np.ndarray]:
    norm2 = float(np.real(direct.tensor_inner(phi, phi)))
    contraction = np.empty((10, 10), dtype=float)
    interiors = [direct.interior(phi, index) for index in range(10)]
    for i in range(10):
        for j in range(10):
            contraction[i, j] = float(
                np.real(direct.tensor_inner(interiors[i], interiors[j]))
            )
    q54 = 0.5 * (contraction + contraction.T) - (2.0 / 5.0) * norm2 * np.eye(10)
    dual_two_form = direct.hodge_star(direct.wedge(phi, phi))
    a45 = _two_form_matrix(dual_two_form)
    return {
        "1": norm2 * np.eye(10, dtype=complex),
        "45": 1j * a45,
        "54": q54.astype(complex),
    }


def invariant_values(phi: direct.Form, h: np.ndarray) -> dict[str, float]:
    vector = np.asarray(h, dtype=complex).reshape(10)
    output: dict[str, float] = {}
    for name, matrix in channel_operators(phi).items():
        value = np.vdot(vector, matrix @ vector)
        if abs(value.imag) > 1.0e-10:
            raise AssertionError(f"{name} invariant not real: {value}")
        output[name] = float(value.real)
    return output


def generic_phi() -> direct.Form:
    phi: direct.Form = {
        (0, 1, 2, 3): 1.0,
        (0, 4, 6, 8): 2.0,
        (1, 5, 7, 9): -3.0,
        (2, 4, 7, 8): 1.5,
        (3, 5, 6, 9): -0.7,
        (0, 2, 5, 9): 0.9,
    }
    return direct.normalize_210_or_10(phi)


def representation_census() -> dict[str, Any]:
    h_endomorphism = {"1": 1, "45": 1, "54": 1}
    symmetric_210 = phi_census.SYMMETRIC_210_PRODUCT
    common = {
        name: min(h_endomorphism[name], symmetric_210[name])
        for name in h_endomorphism
        if name in symmetric_210
    }
    return {
        "Sym2_210_contains": {
            name: symmetric_210[name] for name in ("1", "45", "54")
        },
        "10bar_tensor_10": h_endomorphism,
        "common_channels": common,
        "total_multiplicity": int(sum(common.values())),
        "dimension_check_10bar_tensor_10": 1 + 45 + 54,
    }


def algebra_audit(phi: direct.Form) -> dict[str, Any]:
    operators = channel_operators(phi)
    names = ("1", "45", "54")
    gram = np.empty((3, 3), dtype=float)
    columns = []
    for i, left in enumerate(names):
        matrix = operators[left]
        columns.append(np.concatenate([matrix.real.ravel(), matrix.imag.ravel()]))
        for j, right in enumerate(names):
            gram[i, j] = float(
                np.real(np.trace(matrix.conj().T @ operators[right]))
            )
    stacked = np.column_stack(columns)
    return {
        "hermiticity_residuals": {
            name: float(np.max(np.abs(matrix - matrix.conj().T)))
            for name, matrix in operators.items()
        },
        "trace_1": {name: complex(np.trace(matrix)) for name, matrix in operators.items()},
        "hilbert_schmidt_gram": gram,
        "offdiagonal_orthogonality_residual": float(
            np.max(np.abs(gram - np.diag(np.diag(gram))))
        ),
        "operator_span_rank": int(np.linalg.matrix_rank(stacked, tol=1.0e-11)),
        "operator_norms_squared": {
            name: float(np.real(np.trace(matrix.conj().T @ matrix)))
            for name, matrix in operators.items()
        },
    }


def covariance_audit(phi: direct.Form) -> dict[str, Any]:
    generator = vector_generator_matrix(1, 7)
    tangent = direct.generator_action(phi, 1, 7)
    epsilon = 1.0e-6
    plus = direct.add_forms(phi, direct.scale_form(tangent, epsilon))
    minus = direct.add_forms(phi, direct.scale_form(tangent, -epsilon))
    operators = channel_operators(phi)
    plus_ops = channel_operators(plus)
    minus_ops = channel_operators(minus)
    residuals: dict[str, float] = {}
    relative: dict[str, float] = {}
    for name, matrix in operators.items():
        derivative = (plus_ops[name] - minus_ops[name]) / (2.0 * epsilon)
        expected = generator @ matrix - matrix @ generator
        residual = float(np.max(np.abs(derivative - expected)))
        scale = float(max(np.max(np.abs(expected)), 1.0))
        residuals[name] = residual
        relative[name] = residual / scale
    return {
        "generator": [1, 7],
        "finite_difference_epsilon": epsilon,
        "absolute_residuals": residuals,
        "relative_residuals": relative,
        "maximum_relative_residual": max(relative.values()),
    }


def p_background_audit() -> dict[str, Any]:
    p = direct.singlet_basis()["p"]
    operators = channel_operators(p)
    q54 = operators["54"].real
    expected = np.diag([-0.4] * 6 + [0.6] * 4)
    return {
        "p_norm": direct.tensor_norm(p),
        "singlet_operator_residual": float(
            np.max(np.abs(operators["1"] - np.eye(10)))
        ),
        "adjoint_45_norm": float(
            np.sqrt(np.real(np.trace(operators["45"].conj().T @ operators["45"])))
        ),
        "q54": q54,
        "q54_expected": expected,
        "q54_expected_residual": float(np.max(np.abs(q54 - expected))),
        "q54_eigenvalues": np.linalg.eigvalsh(q54),
    }


def build_report() -> dict[str, Any]:
    census = representation_census()
    phi = generic_phi()
    algebra = algebra_audit(phi)
    covariance = covariance_audit(phi)
    p_background = p_background_audit()
    h = np.asarray([1 + 0.2j, -0.4j, 0.7, 0.1 + 0.3j, -0.8, 0.5j, 0.2, -0.6j, 0.9, -0.1], dtype=complex)
    values = invariant_values(phi, h)

    checks = {
        "exactly_three_common_channels": census["common_channels"] == {"1": 1, "45": 1, "54": 1},
        "10_endomorphism_dimension_is_100": census["dimension_check_10bar_tensor_10"] == 100,
        "all_operators_hermitian": max(algebra["hermiticity_residuals"].values()) < 1.0e-12,
        "singlet_trace_only": abs(algebra["trace_1"]["45"]) < 1.0e-12 and abs(algebra["trace_1"]["54"]) < 1.0e-12,
        "channels_hilbert_schmidt_orthogonal": algebra["offdiagonal_orthogonality_residual"] < 1.0e-11,
        "three_nonzero_independent_operators": algebra["operator_span_rank"] == 3 and min(algebra["operator_norms_squared"].values()) > 1.0e-10,
        "infinitesimal_so10_covariance": covariance["maximum_relative_residual"] < 1.0e-7,
        "p_singlet_normalized": abs(p_background["p_norm"] - 1.0) < 1.0e-12,
        "p_background_45_vanishes": p_background["adjoint_45_norm"] < 1.0e-12,
        "p_background_54_exact": p_background["q54_expected_residual"] < 1.0e-12,
        "all_sample_invariants_real": all(np.isfinite(value) for value in values.values()),
        "complete_mixed_ring_not_claimed": True,
        "whole_model_validation_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report = {
        "status": (
            "EXACT_PHI2_HDAGH_1_45_54_FAMILY_CLOSED__FULL_G1_OPEN"
            if not failures
            else "EXACT_PHI2_HDAGH_CHANNEL_FAMILY_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "representation_census": census,
        "canonical_maps": {
            "1": "M1=||Phi||^2 I_10",
            "45": "M45=i A, A associated with *(Phi wedge Phi)",
            "54": "M54_ij=<i_i Phi,i_j Phi>-(2/5)||Phi||^2 delta_ij",
            "scalar_invariants": "I_Q=H^dag M_Q(Phi) H",
        },
        "generic_phi_algebra": algebra,
        "so10_covariance": covariance,
        "pati_salam_p_background": p_background,
        "sample_invariant_values": values,
        "flag": {
            "phi2_hdagh_channel_count_closed": not failures,
            "all_three_all_component_tensor_maps_constructed": not failures,
            "canonical_kinetic_conventions_used": True,
            "complete_mixed_invariant_ring": False,
            "complete_component_potential": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The complete renormalizable Hermitian 210_H^2 10_H^dag 10_H family "
            "contains exactly one singlet, one adjoint-45, and one symmetric-traceless-54 "
            "channel. Canonical all-component tensor maps are explicit, independent, "
            "Hermitian, and SO(10)-covariant. This closes one finite G1 family only."
        ),
    }
    return _jsonable(report)


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Exact 210^2 H^dag H channel family — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Channels",
            "",
            "- `1`: `||Phi||^2 H^dag H`",
            "- `45`: `H^dag i*(Phi wedge Phi) H`",
            "- `54`: `H^dag[<i_iPhi,i_jPhi>-(2/5)||Phi||^2 delta_ij]H`",
            "",
            "The complete mixed invariant ring remains open.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
