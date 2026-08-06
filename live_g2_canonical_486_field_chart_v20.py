#!/usr/bin/env python3
"""Canonical 486-real physical scalar chart for the live G2 potential.

The corrected G2 value layer evaluates arbitrary fields but deliberately did
not claim a complete field-coordinate derivative.  This module fixes the one
canonical real chart required before gradients and Hessians can be defined:

  Phi_210     : 210 real independent four-form components,
  H_10        : 10 complex components = 20 canonical real coordinates,
  Sigma_126bar: 126 complex coefficients in the physical -i Hodge basis
                 = 252 canonical real coordinates,
  S           : 1 complex singlet = 2 canonical real coordinates,
  Phi17       : 1 complex singlet = 2 canonical real coordinates.

Total: 210 + 20 + 252 + 2 + 2 = 486 real coordinates.

For each complex coefficient z the chart uses z=(x+i y)/sqrt(2).  The 210
four-form basis and the physical 126bar basis already obey the repository's
kinetic conventions.  Therefore the scalar kinetic quadratic form is exactly

  K_2 = 1/2 q^T q

in this chart.  Pack/unpack are exact inverse maps, Sigma never leaves the
physical -i Hodge eigenspace, and infinitesimal SO(10) generator actions can be
represented as 486-real tangent vectors.

This closes the field-chart layer of G2 only.  The complete 486-entry gradient
and 486x486 Hessian of all 91 parameters remain open.
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import live_g2_arbitrary_component_potential_values_v20 as potential

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_CANONICAL_486_FIELD_CHART_V20.json"
OUT_MD = ROOT / "LIVE_G2_CANONICAL_486_FIELD_CHART_V20.md"

PHI_DIM = 210
H_COMPLEX_DIM = 10
H_REAL_DIM = 20
SIGMA_COMPLEX_DIM = 126
SIGMA_REAL_DIM = 252
S_REAL_DIM = 2
X_REAL_DIM = 2
TOTAL_DIM = PHI_DIM + H_REAL_DIM + SIGMA_REAL_DIM + S_REAL_DIM + X_REAL_DIM
SYMMETRIC_HESSIAN_ENTRIES = TOTAL_DIM * (TOTAL_DIM + 1) // 2
SQRT2 = float(np.sqrt(2.0))

PHI_SLICE = slice(0, PHI_DIM)
H_SLICE = slice(PHI_SLICE.stop, PHI_SLICE.stop + H_REAL_DIM)
SIGMA_SLICE = slice(H_SLICE.stop, H_SLICE.stop + SIGMA_REAL_DIM)
S_SLICE = slice(SIGMA_SLICE.stop, SIGMA_SLICE.stop + S_REAL_DIM)
X_SLICE = slice(S_SLICE.stop, S_SLICE.stop + X_REAL_DIM)

# Stable public ordering shared by every analytic derivative adapter.  The
# function below is retained for existing callers; both APIs return the same
# immutable object and therefore cannot silently drift apart.
PHI_INDICES = tuple(itertools.combinations(range(direct.N), 4))
if len(PHI_INDICES) != PHI_DIM:
    raise AssertionError(
        f"expected {PHI_DIM} independent Phi components, found {len(PHI_INDICES)}"
    )


@dataclasses.dataclass(frozen=True)
class ChartBlock:
    name: str
    start: int
    stop: int
    real_dimension: int
    representation: str
    coordinate_convention: str


BLOCKS = (
    ChartBlock(
        "Phi210",
        PHI_SLICE.start,
        PHI_SLICE.stop,
        PHI_DIM,
        "real SO(10) four-form",
        "independent ordered components Phi_abcd",
    ),
    ChartBlock(
        "H10",
        H_SLICE.start,
        H_SLICE.stop,
        H_REAL_DIM,
        "complex SO(10) vector",
        "H_i=(x_i+i y_i)/sqrt(2), interleaved x_i,y_i",
    ),
    ChartBlock(
        "Sigma126bar",
        SIGMA_SLICE.start,
        SIGMA_SLICE.stop,
        SIGMA_REAL_DIM,
        "complex physical -i Hodge five-form",
        "Sigma=sum_i (x_i+i y_i)/sqrt(2) e_i, interleaved",
    ),
    ChartBlock(
        "S",
        S_SLICE.start,
        S_SLICE.stop,
        S_REAL_DIM,
        "complex singlet",
        "S=(x+i y)/sqrt(2)",
    ),
    ChartBlock(
        "Phi17",
        X_SLICE.start,
        X_SLICE.stop,
        X_REAL_DIM,
        "complex singlet",
        "Phi17=(x+i y)/sqrt(2)",
    ),
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
def phi_indices() -> tuple[tuple[int, ...], ...]:
    return PHI_INDICES


@lru_cache(maxsize=1)
def sigma_basis() -> tuple[direct.Form, ...]:
    basis = tuple(direct.anti_self_dual_five_form_basis())
    if len(basis) != SIGMA_COMPLEX_DIM:
        raise AssertionError(f"expected 126 physical Sigma states, found {len(basis)}")
    return basis


def coordinate_names() -> tuple[str, ...]:
    names: list[str] = []
    names.extend("Phi[" + ",".join(map(str, indices)) + "]" for indices in phi_indices())
    for index in range(H_COMPLEX_DIM):
        names.extend((f"H[{index}].x", f"H[{index}].y"))
    for index in range(SIGMA_COMPLEX_DIM):
        names.extend((f"Sigma[{index}].x", f"Sigma[{index}].y"))
    names.extend(("S.x", "S.y", "Phi17.x", "Phi17.y"))
    if len(names) != TOTAL_DIM:
        raise AssertionError(f"expected {TOTAL_DIM} coordinate names, found {len(names)}")
    return tuple(names)


def _pack_complex_interleaved(values: np.ndarray) -> np.ndarray:
    source = np.asarray(values, dtype=complex).reshape(-1)
    output = np.empty(2 * source.size, dtype=float)
    output[0::2] = SQRT2 * source.real
    output[1::2] = SQRT2 * source.imag
    return output


def _unpack_complex_interleaved(values: np.ndarray) -> np.ndarray:
    source = np.asarray(values, dtype=float).reshape(-1)
    if source.size % 2:
        raise ValueError("interleaved complex block must have even length")
    return (source[0::2] + 1j * source[1::2]) / SQRT2


def sigma_coordinates(form: direct.Form) -> np.ndarray:
    return np.asarray(
        [direct.sigma_kinetic_inner(state, form) for state in sigma_basis()],
        dtype=complex,
    )


def sigma_from_coordinates(values: np.ndarray) -> direct.Form:
    coordinates = np.asarray(values, dtype=complex).reshape(SIGMA_COMPLEX_DIM)
    result: direct.Form = {}
    for coefficient, state in zip(coordinates, sigma_basis()):
        if abs(coefficient) > 1.0e-15:
            result = direct.add_forms(
                result, direct.scale_form(state, complex(coefficient))
            )
    return result


def pack(state: potential.FieldState, *, tolerance: float = 1.0e-10) -> np.ndarray:
    value = state.validated()
    phi_values = np.asarray(
        [value.phi.get(indices, 0.0) for indices in phi_indices()],
        dtype=complex,
    )
    phi_imaginary_residual = float(np.max(np.abs(phi_values.imag), initial=0.0))
    if phi_imaginary_residual > tolerance:
        raise ValueError(
            "Phi210 is a real representation; imaginary component residual "
            f"{phi_imaginary_residual} exceeds tolerance"
        )

    sigma_values = sigma_coordinates(value.sigma)
    sigma_reconstruction = sigma_from_coordinates(sigma_values)
    sigma_residual = direct.sigma_kinetic_norm(
        direct.add_forms(value.sigma, direct.scale_form(sigma_reconstruction, -1.0))
    )
    if sigma_residual > tolerance:
        raise ValueError(
            "Sigma contains components outside the canonical physical basis: "
            f"residual={sigma_residual}"
        )

    output = np.empty(TOTAL_DIM, dtype=float)
    output[PHI_SLICE] = phi_values.real
    output[H_SLICE] = _pack_complex_interleaved(value.h)
    output[SIGMA_SLICE] = _pack_complex_interleaved(sigma_values)
    output[S_SLICE] = _pack_complex_interleaved(np.asarray([value.s]))
    output[X_SLICE] = _pack_complex_interleaved(np.asarray([value.x]))
    return output


def unpack(coordinates: np.ndarray) -> potential.FieldState:
    q = np.asarray(coordinates, dtype=float).reshape(-1)
    if q.size != TOTAL_DIM:
        raise ValueError(f"expected {TOTAL_DIM} real coordinates, got {q.size}")
    if not np.all(np.isfinite(q)):
        raise ValueError("field coordinates must be finite")

    phi = {
        indices: complex(q[PHI_SLICE][index])
        for index, indices in enumerate(phi_indices())
        if abs(q[PHI_SLICE][index]) > 1.0e-15
    }
    h = _unpack_complex_interleaved(q[H_SLICE])
    sigma = sigma_from_coordinates(
        _unpack_complex_interleaved(q[SIGMA_SLICE])
    )
    s = complex(_unpack_complex_interleaved(q[S_SLICE])[0])
    x = complex(_unpack_complex_interleaved(q[X_SLICE])[0])
    return potential.FieldState(phi=phi, h=h, sigma=sigma, s=s, x=x).validated()


def kinetic_quadratic(state: potential.FieldState) -> float:
    value = state.validated()
    phi_norm_squared = float(np.real(direct.tensor_inner(value.phi, value.phi)))
    h_norm_squared = float(np.vdot(value.h, value.h).real)
    sigma_norm_squared = float(
        np.real(direct.sigma_kinetic_inner(value.sigma, value.sigma))
    )
    return float(
        0.5 * phi_norm_squared
        + h_norm_squared
        + sigma_norm_squared
        + abs(value.s) ** 2
        + abs(value.x) ** 2
    )


def coordinate_kinetic_quadratic(coordinates: np.ndarray) -> float:
    q = np.asarray(coordinates, dtype=float).reshape(TOTAL_DIM)
    return float(0.5 * np.dot(q, q))


def _vector_form(vector: np.ndarray) -> direct.Form:
    values = np.asarray(vector, dtype=complex).reshape(10)
    return {
        (index,): complex(value)
        for index, value in enumerate(values)
        if abs(value) > 1.0e-15
    }


def _form_vector(form: direct.Form) -> np.ndarray:
    return np.asarray(
        [form.get((index,), 0.0) for index in range(10)], dtype=complex
    )


def gauge_tangent(
    state: potential.FieldState, first: int, second: int
) -> np.ndarray:
    if not (0 <= first < second < 10):
        raise ValueError("generator requires 0 <= first < second < 10")
    value = state.validated()
    delta_phi = direct.generator_action(value.phi, first, second)
    delta_h = _form_vector(
        direct.generator_action(_vector_form(value.h), first, second)
    )
    delta_sigma = direct.generator_action(value.sigma, first, second)
    variation = potential.FieldState(
        phi=delta_phi,
        h=delta_h,
        sigma=delta_sigma,
        s=0.0j,
        x=0.0j,
    )
    return pack(variation)


def gauge_orbit_matrix(state: potential.FieldState) -> np.ndarray:
    return np.column_stack(
        [
            gauge_tangent(state, first, second)
            for first, second in itertools.combinations(range(10), 2)
        ]
    )


def chart_audit(seed: int = 486) -> dict[str, Any]:
    state = potential.deterministic_state(seed)
    q = pack(state)
    reconstructed = unpack(q)
    q_roundtrip = pack(reconstructed)

    directions_original = potential.evaluate_directions(state)
    directions_roundtrip = potential.evaluate_directions(reconstructed)
    direction_residual = max(
        abs(left.value - right.value)
        for left, right in zip(directions_original, directions_roundtrip)
    )

    rng = np.random.default_rng(seed + 1)
    random_q = rng.normal(size=TOTAL_DIM)
    random_state = unpack(random_q)
    random_roundtrip = pack(random_state)

    sigma_chirality_residual = direct.tensor_norm(
        direct.add_forms(
            direct.hodge_star(reconstructed.sigma),
            direct.scale_form(reconstructed.sigma, 1j),
        )
    )
    sigma_basis_gram = np.asarray(
        [
            [direct.sigma_kinetic_inner(left, right) for right in sigma_basis()]
            for left in sigma_basis()
        ],
        dtype=complex,
    )

    orbit = gauge_orbit_matrix(state)
    singular_values = np.linalg.svd(orbit, compute_uv=False)
    orbit_rank = int(np.sum(singular_values > 1.0e-10))
    gauge_norm_residual = float(np.max(np.abs(q @ orbit)))

    block_coverage = [False] * TOTAL_DIM
    for block in BLOCKS:
        for index in range(block.start, block.stop):
            if block_coverage[index]:
                raise AssertionError(f"coordinate {index} covered twice")
            block_coverage[index] = True

    return {
        "dimensions": {
            "Phi210": PHI_DIM,
            "H10": H_REAL_DIM,
            "Sigma126bar": SIGMA_REAL_DIM,
            "S": S_REAL_DIM,
            "Phi17": X_REAL_DIM,
            "total": TOTAL_DIM,
            "symmetric_Hessian_entries": SYMMETRIC_HESSIAN_ENTRIES,
        },
        "blocks": BLOCKS,
        "coordinate_name_count": len(coordinate_names()),
        "all_coordinates_covered_once": all(block_coverage),
        "deterministic_roundtrip_residual": float(
            np.max(np.abs(q_roundtrip - q))
        ),
        "random_roundtrip_residual": float(
            np.max(np.abs(random_roundtrip - random_q))
        ),
        "deterministic_kinetic_residual": abs(
            kinetic_quadratic(state) - coordinate_kinetic_quadratic(q)
        ),
        "random_kinetic_residual": abs(
            kinetic_quadratic(random_state)
            - coordinate_kinetic_quadratic(random_q)
        ),
        "sigma_basis_orthonormality_residual": float(
            np.max(np.abs(sigma_basis_gram - np.eye(SIGMA_COMPLEX_DIM)))
        ),
        "sigma_chirality_residual": sigma_chirality_residual,
        "all_64_direction_roundtrip_residual": float(direction_residual),
        "generic_gauge_orbit_rank": orbit_rank,
        "gauge_norm_invariance_residual": gauge_norm_residual,
        "gauge_singular_values": singular_values,
    }


def build_report() -> dict[str, Any]:
    value_layer = potential.build_report()
    audit = chart_audit()
    checks = {
        "corrected_value_layer_executes": value_layer["n_failed"] == 0,
        "dimension_is_exactly_486": audit["dimensions"]["total"] == 486,
        "symmetric_Hessian_has_118341_entries": (
            audit["dimensions"]["symmetric_Hessian_entries"] == 118341
        ),
        "five_blocks_cover_every_coordinate_once": audit[
            "all_coordinates_covered_once"
        ],
        "486_unique_coordinate_names": (
            audit["coordinate_name_count"] == 486
            and len(set(coordinate_names())) == 486
        ),
        "deterministic_pack_unpack_exact": audit[
            "deterministic_roundtrip_residual"
        ] < 1.0e-12,
        "random_pack_unpack_exact": audit["random_roundtrip_residual"] < 1.0e-12,
        "deterministic_kinetic_metric_identity": audit[
            "deterministic_kinetic_residual"
        ] < 1.0e-12,
        "random_kinetic_metric_identity": audit["random_kinetic_residual"] < 1.0e-10,
        "physical_sigma_basis_orthonormal": audit[
            "sigma_basis_orthonormality_residual"
        ] < 1.0e-12,
        "physical_sigma_chirality_preserved": audit[
            "sigma_chirality_residual"
        ] < 1.0e-12,
        "all_64_values_invariant_under_chart_roundtrip": audit[
            "all_64_direction_roundtrip_residual"
        ] < 1.0e-10,
        "generic_SO10_orbit_has_rank_45": audit[
            "generic_gauge_orbit_rank"
        ] == 45,
        "gauge_action_preserves_kinetic_norm": audit[
            "gauge_norm_invariance_residual"
        ] < 1.0e-10,
        "complete_gradient_not_claimed": True,
        "complete_Hessian_not_claimed": True,
        "G2_not_closed": True,
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
            "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "audit": audit,
            "coordinate_names": coordinate_names(),
            "flags": {
                "canonical_486_real_chart_closed": not failures,
                "pack_unpack_exact": not failures,
                "identity_kinetic_metric": not failures,
                "physical_126bar_chirality_preserved": not failures,
                "SO10_tangent_map_available": not failures,
                "complete_486_gradient": False,
                "complete_486x486_Hessian": False,
                "G2_closed": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Differentiate every one of the 64 direction values with "
                "respect to this canonical chart, beginning with exact analytic "
                "gradients and Hessians for the 18 base tensor families."
            ),
            "verdict": (
                "The physical scalar space now has one exact canonical "
                "486-real coordinate chart with identity kinetic metric, exact "
                "pack/unpack, physical 126bar chirality, and SO(10) tangents. "
                "G2 remains partial until all 64 values are differentiated."
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
