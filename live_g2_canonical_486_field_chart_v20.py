#!/usr/bin/env python3
"""Canonical reversible 486-real chart for the live G2 scalar fields.

The physical scalar space is

    210_H(real) + 10_H(complex) + 126bar_H(complex chiral)
    + S(complex) + Phi17(complex)

and therefore has

    210 + 20 + 252 + 2 + 2 = 486

real coordinates. The chart uses the independent real four-form components of
210_H and the canonical split z=(x+i y)/sqrt(2) for every complex coefficient.
For 126bar_H, the complex coefficients multiply the exact kinetic-orthonormal
126-state -i-Hodge basis from ``direct_phi_h_sigmabar_tensor_v20``.

The coordinate metric is fixed by

    (1/2) q.q = (1/2)<Phi,Phi> + Hdag H
                  + <Sigma,Sigma>_126 + |S|^2 + |Phi17|^2.

This module closes the coordinate-chart subgate only. It does not claim the
complete gradient, Hessian, stationarity solution, global minimum, or G2.
"""
from __future__ import annotations

import argparse
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import live_g2_arbitrary_component_potential_values_v20 as values

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_CANONICAL_486_FIELD_CHART_V20.json"
OUT_MD = ROOT / "LIVE_G2_CANONICAL_486_FIELD_CHART_V20.md"

SQRT2 = float(np.sqrt(2.0))
PHI_INDICES = tuple(itertools.combinations(range(10), 4))
PHI_DIM = len(PHI_INDICES)
H_COMPLEX_DIM = 10
SIGMA_COMPLEX_DIM = 126
S_COMPLEX_DIM = 1
X_COMPLEX_DIM = 1

PHI_SLICE = slice(0, 210)
H_SLICE = slice(210, 230)
SIGMA_SLICE = slice(230, 482)
S_SLICE = slice(482, 484)
X_SLICE = slice(484, 486)
REAL_DIMENSION = 486
SYMMETRIC_HESSIAN_ENTRIES = REAL_DIMENSION * (REAL_DIMENSION + 1) // 2


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


@lru_cache(maxsize=1)
def sigma_basis() -> tuple[direct.Form, ...]:
    basis = tuple(direct.anti_self_dual_five_form_basis())
    if len(basis) != SIGMA_COMPLEX_DIM:
        raise AssertionError(f"expected 126 chiral states, found {len(basis)}")
    return basis


def interleave_complex(coefficients: np.ndarray) -> np.ndarray:
    value = np.asarray(coefficients, dtype=complex).reshape(-1)
    output = np.empty(2 * value.size, dtype=float)
    output[0::2] = SQRT2 * value.real
    output[1::2] = SQRT2 * value.imag
    return output


def deinterleave_complex(coordinates: np.ndarray) -> np.ndarray:
    value = np.asarray(coordinates, dtype=float).reshape(-1)
    if value.size % 2:
        raise ValueError("complex coordinate block must have even length")
    return (value[0::2] + 1j * value[1::2]) / SQRT2


def sigma_coefficients(sigma: direct.Form) -> np.ndarray:
    return np.asarray(
        [direct.sigma_kinetic_inner(state, sigma) for state in sigma_basis()],
        dtype=complex,
    )


def sigma_from_coefficients(coefficients: np.ndarray) -> direct.Form:
    value = np.asarray(coefficients, dtype=complex).reshape(SIGMA_COMPLEX_DIM)
    output: direct.Form = {}
    for coefficient, state in zip(value, sigma_basis(), strict=True):
        if abs(coefficient) > 1.0e-15:
            output = direct.add_forms(
                output, direct.scale_form(state, complex(coefficient))
            )
    return output


def pack(state: values.FieldState) -> np.ndarray:
    field = state.validated()
    coordinates = np.empty(REAL_DIMENSION, dtype=float)
    coordinates[PHI_SLICE] = np.asarray(
        [complex(field.phi.get(index, 0.0)).real for index in PHI_INDICES],
        dtype=float,
    )
    coordinates[H_SLICE] = interleave_complex(field.h)
    coordinates[SIGMA_SLICE] = interleave_complex(
        sigma_coefficients(field.sigma)
    )
    coordinates[S_SLICE] = interleave_complex(np.asarray([field.s]))
    coordinates[X_SLICE] = interleave_complex(np.asarray([field.x]))
    return coordinates


def unpack(coordinates: np.ndarray) -> values.FieldState:
    vector = np.asarray(coordinates, dtype=float).reshape(-1)
    if vector.size != REAL_DIMENSION:
        raise ValueError(
            f"expected {REAL_DIMENSION} real coordinates, got {vector.size}"
        )
    phi = {
        index: complex(vector[PHI_SLICE][position])
        for position, index in enumerate(PHI_INDICES)
        if abs(vector[PHI_SLICE][position]) > 1.0e-15
    }
    h = deinterleave_complex(vector[H_SLICE])
    sigma = sigma_from_coefficients(
        deinterleave_complex(vector[SIGMA_SLICE])
    )
    s = complex(deinterleave_complex(vector[S_SLICE])[0])
    x = complex(deinterleave_complex(vector[X_SLICE])[0])
    return values.FieldState(phi=phi, h=h, sigma=sigma, s=s, x=x).validated()


def coordinate_labels() -> tuple[str, ...]:
    labels = ["Phi_" + "".join(str(index) for index in indices) for indices in PHI_INDICES]
    for index in range(H_COMPLEX_DIM):
        labels.extend((f"sqrt2_Re_H_{index}", f"sqrt2_Im_H_{index}"))
    for index in range(SIGMA_COMPLEX_DIM):
        labels.extend(
            (f"sqrt2_Re_SigmaBasis_{index}", f"sqrt2_Im_SigmaBasis_{index}")
        )
    labels.extend(("sqrt2_Re_S", "sqrt2_Im_S"))
    labels.extend(("sqrt2_Re_Phi17", "sqrt2_Im_Phi17"))
    if len(labels) != REAL_DIMENSION:
        raise AssertionError("coordinate label count mismatch")
    return tuple(labels)


def field_kinetic_quadratic(state: values.FieldState) -> float:
    field = state.validated()
    return float(
        0.5 * np.real(direct.tensor_inner(field.phi, field.phi))
        + np.real(np.vdot(field.h, field.h))
        + np.real(direct.sigma_kinetic_inner(field.sigma, field.sigma))
        + abs(field.s) ** 2
        + abs(field.x) ** 2
    )


def coordinate_kinetic_quadratic(coordinates: np.ndarray) -> float:
    vector = np.asarray(coordinates, dtype=float).reshape(-1)
    if vector.size != REAL_DIMENSION:
        raise ValueError("coordinate vector has wrong dimension")
    return float(0.5 * np.dot(vector, vector))


def form_residual(left: direct.Form, right: direct.Form) -> float:
    return direct.tensor_norm(
        direct.add_forms(left, direct.scale_form(right, -1.0))
    )


def state_roundtrip_audit(state: values.FieldState) -> dict[str, float]:
    source = state.validated()
    restored = unpack(pack(source))
    return {
        "Phi_residual": form_residual(source.phi, restored.phi),
        "H_residual": float(np.max(np.abs(source.h - restored.h))),
        "Sigma_raw_residual": form_residual(source.sigma, restored.sigma),
        "Sigma_kinetic_residual": direct.sigma_kinetic_norm(
            direct.add_forms(
                source.sigma, direct.scale_form(restored.sigma, -1.0)
            )
        ),
        "S_residual": float(abs(source.s - restored.s)),
        "Phi17_residual": float(abs(source.x - restored.x)),
    }


def sigma_basis_audit() -> dict[str, Any]:
    basis = sigma_basis()
    gram = np.asarray(
        [
            [direct.sigma_kinetic_inner(left, right) for right in basis]
            for left in basis
        ],
        dtype=complex,
    )
    chirality_residual = max(
        direct.tensor_norm(
            direct.add_forms(
                direct.hodge_star(state), direct.scale_form(state, 1j)
            )
        )
        for state in basis
    )
    return {
        "dimension": len(basis),
        "Gram_residual": float(
            np.max(np.abs(gram - np.eye(SIGMA_COMPLEX_DIM)))
        ),
        "maximum_minus_i_Hodge_residual": float(chirality_residual),
    }


def selected_one_hot_roundtrip_audit() -> dict[str, Any]:
    indices = (0, 209, 210, 229, 230, 481, 482, 483, 484, 485)
    residuals: dict[str, float] = {}
    for index in indices:
        coordinate = np.zeros(REAL_DIMENSION, dtype=float)
        coordinate[index] = 1.0
        residuals[str(index)] = float(
            np.max(np.abs(pack(unpack(coordinate)) - coordinate))
        )
    return {
        "indices": list(indices),
        "residuals": residuals,
        "maximum_residual": max(residuals.values()),
    }


def direction_value_roundtrip_audit(state: values.FieldState) -> dict[str, Any]:
    source = values.evaluate_directions(state.validated())
    restored = values.evaluate_directions(unpack(pack(state)))
    if [row.direction_id for row in source] != [row.direction_id for row in restored]:
        raise AssertionError("direction order changed under coordinate roundtrip")
    residuals = {
        left.direction_id: float(abs(left.value - right.value))
        for left, right in zip(source, restored, strict=True)
    }
    return {
        "direction_count": len(source),
        "maximum_abs_residual": max(residuals.values()),
        "per_direction_abs_residual": residuals,
    }


def potential_from_coordinates(
    coordinates: np.ndarray,
    coefficients: Mapping[str, float],
) -> float:
    directions = values.evaluate_directions(unpack(coordinates))
    return values.potential_value(directions, coefficients)


def build_report() -> dict[str, Any]:
    state = values.deterministic_state(486)
    coordinates = pack(state)
    restored = unpack(coordinates)
    roundtrip = state_roundtrip_audit(state)
    basis = sigma_basis_audit()
    one_hot = selected_one_hot_roundtrip_audit()
    direction_roundtrip = direction_value_roundtrip_audit(state)
    field_metric = field_kinetic_quadratic(state)
    coordinate_metric = coordinate_kinetic_quadratic(coordinates)
    restored_chirality = direct.tensor_norm(
        direct.add_forms(
            direct.hodge_star(restored.sigma),
            direct.scale_form(restored.sigma, 1j),
        )
    )
    parameters = values.parameter_schema(values.evaluate_directions(state))
    coefficients = values.deterministic_coefficients(parameters)
    source_potential = values.potential_value(
        values.evaluate_directions(state), coefficients
    )
    coordinate_potential = potential_from_coordinates(coordinates, coefficients)

    checks = {
        "Phi_independent_dimension_is_210": PHI_DIM == 210,
        "H_real_dimension_is_20": H_SLICE.stop - H_SLICE.start == 20,
        "Sigma_real_dimension_is_252": SIGMA_SLICE.stop - SIGMA_SLICE.start == 252,
        "singlet_real_dimension_is_4": (
            S_SLICE.stop - S_SLICE.start + X_SLICE.stop - X_SLICE.start
        )
        == 4,
        "total_real_dimension_is_486": coordinates.size == REAL_DIMENSION == 486,
        "symmetric_Hessian_entries_are_118341": SYMMETRIC_HESSIAN_ENTRIES == 118341,
        "coordinate_labels_complete_and_unique": (
            len(coordinate_labels()) == 486 and len(set(coordinate_labels())) == 486
        ),
        "Sigma_basis_is_126_dimensional": basis["dimension"] == 126,
        "Sigma_basis_kinetic_orthonormal": basis["Gram_residual"] < 1.0e-12,
        "Sigma_basis_has_physical_minus_i_chirality": basis[
            "maximum_minus_i_Hodge_residual"
        ]
        < 1.0e-12,
        "state_roundtrip_exact": max(roundtrip.values()) < 1.0e-11,
        "selected_one_hot_coordinates_roundtrip": one_hot[
            "maximum_residual"
        ]
        < 1.0e-12,
        "restored_Sigma_stays_physical": restored_chirality < 1.0e-11,
        "kinetic_metric_matches_half_Euclidean_norm": abs(
            field_metric - coordinate_metric
        )
        < 1.0e-11,
        "all_64_direction_values_survive_roundtrip": (
            direction_roundtrip["direction_count"] == 64
            and direction_roundtrip["maximum_abs_residual"] < 1.0e-9
        ),
        "91_parameter_potential_survives_roundtrip": abs(
            source_potential - coordinate_potential
        )
        < 1.0e-9,
        "complete_gradient_not_claimed": True,
        "complete_Hessian_not_claimed": True,
        "G2_not_claimed_closed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "LIVE_G2_CANONICAL_486_FIELD_CHART_CLOSED__DERIVATIVES_OPEN"
                if not failures
                else "LIVE_G2_CANONICAL_486_FIELD_CHART_FAILED"
            ),
            "overall_state": "PARTIAL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "dimensions": {
                "Phi_real": 210,
                "H_real": 20,
                "Sigma_real": 252,
                "S_real": 2,
                "Phi17_real": 2,
                "total_real": REAL_DIMENSION,
                "gradient_entries": REAL_DIMENSION,
                "symmetric_Hessian_entries": SYMMETRIC_HESSIAN_ENTRIES,
            },
            "slices": {
                "Phi": [PHI_SLICE.start, PHI_SLICE.stop],
                "H": [H_SLICE.start, H_SLICE.stop],
                "Sigma": [SIGMA_SLICE.start, SIGMA_SLICE.stop],
                "S": [S_SLICE.start, S_SLICE.stop],
                "Phi17": [X_SLICE.start, X_SLICE.stop],
            },
            "complex_coordinate_convention": "z=(x+i y)/sqrt(2)",
            "kinetic_metric": {
                "field_quadratic": field_metric,
                "coordinate_half_norm_squared": coordinate_metric,
                "absolute_residual": abs(field_metric - coordinate_metric),
            },
            "Sigma_basis_audit": basis,
            "state_roundtrip": roundtrip,
            "selected_one_hot_roundtrip": one_hot,
            "direction_value_roundtrip": direction_roundtrip,
            "potential_roundtrip_residual": abs(
                source_potential - coordinate_potential
            ),
            "flags": {
                "canonical_486_real_chart_complete": not failures,
                "pack_unpack_reversible": not failures,
                "physical_chirality_preserved": not failures,
                "kinetic_metric_fixed": not failures,
                "all_64_values_connected_to_chart": not failures,
                "all_91_parameters_connected_to_chart": not failures,
                "complete_field_gradient": False,
                "complete_field_Hessian": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate each of the 64 operator values with respect to this "
                "canonical 486-real chart, preserving per-direction provenance."
            ),
            "verdict": (
                "The complete physical scalar field now has one reversible, "
                "kinetic-metric-consistent 486-real coordinate chart. All 64 "
                "operator values and the 91-parameter potential survive the "
                "roundtrip. G2 remains PARTIAL because the full gradient and "
                "Hessian have not yet been emitted."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Live G2 canonical 486-real field chart\n\n"
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
