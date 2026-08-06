#!/usr/bin/env python3
"""Compile all 64 live scalar invariants on arbitrary physical fields.

The live SO(10)+PQ+Z17 ring contains 48 Hermitian-conjugacy orbits, 64
normalized invariant directions, and 91 real potential parameters through
degree four. This module evaluates every direction on one common field state

    (Phi_210, H_10, Sigma_126bar, S, Phi17),

applies the exact singlet dressing from the live G1 census, and assembles

    V = sum_self lambda_a I_a + sum_pairs 2 Re(c_a I_a).

Physical contracts are enforced at the boundary:

* Phi_210 is a real independent-component four-form;
* H_10 is a complex length-10 vector;
* Sigma_126bar is a complex five-form in the physical -i Hodge eigenspace;
* S and Phi17 are complex singlets.

The scalar chart has exactly 210+20+252+2+2 = 486 real coordinates. This module
closes only arbitrary-field values and coefficient assembly. The complete
486-entry field gradient, 486x486 Hessian, vacuum, BFB theorem, thresholds,
running, and proton decay remain open.
"""
from __future__ import annotations

import argparse
import dataclasses
import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_self
import exact_210_126bar_cubic_clebsch_v20 as phi_sigma_cubic
import exact_210_self_invariant_basis_v20 as phi_self
import exact_h10_self_quartic_family_v20 as h_self
import exact_mixed_45_triplet_channel_v20 as current45
import exact_phi2_126dag126_six_contractions_v20 as phi2_sigma_graph
import exact_phi2_h_126dag_210_1050_channels_v20 as phi2_hsigma
import exact_phi2_hdagh_channel_family_v20 as phi2_h
import exact_phisigma_126bar_minus_projectors_v20 as phi2_sigma_projector
import exact_unique_hsigma_chiral_quartics_v20 as unique_hsigma
import g1_exact_declared_symmetry_character_census_v20 as census
import live_g1_tensor_closure_ledger_v20 as ledger

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_ARBITRARY_COMPONENT_POTENTIAL_VALUES_V20.json"
OUT_MD = ROOT / "LIVE_G2_ARBITRARY_COMPONENT_POTENTIAL_VALUES_V20.md"

FIELD_ORDER = census.FIELD_ORDER
NON_SINGLET_ORDER = ("P", "H", "Hb", "D", "Db")
SIGMA_SELF_ORDER = ("54", "1050bar", "2772bar", "4125")
PHISIGMA_ORDER = ("1", "45", "210", "770", "5940", "8910")
PHIH_ORDER = ("1", "45", "54")
REAL_FIELD_DIMENSION = 210 + 20 + 252 + 2 + 2
SYMMETRIC_HESSIAN_ENTRIES = REAL_FIELD_DIMENSION * (REAL_FIELD_DIMENSION + 1) // 2


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


def vector_form(vector: np.ndarray) -> direct.Form:
    value = np.asarray(vector, dtype=complex).reshape(10)
    return {
        (index,): complex(coefficient)
        for index, coefficient in enumerate(value)
        if abs(coefficient) > 1.0e-14
    }


def _canonical_indices(indices: tuple[int, ...], degree: int) -> bool:
    return (
        len(indices) == degree
        and len(set(indices)) == degree
        and tuple(indices) == tuple(sorted(indices))
        and all(0 <= index < 10 for index in indices)
    )


@dataclasses.dataclass(frozen=True)
class FieldState:
    phi: direct.Form
    h: np.ndarray
    sigma: direct.Form
    s: complex
    x: complex

    def validated(self) -> "FieldState":
        h = np.asarray(self.h, dtype=complex)
        if h.shape != (10,):
            raise ValueError("H10 vector must have shape (10,)")
        if not all(_canonical_indices(indices, 4) for indices in self.phi):
            raise ValueError("Phi must use canonical independent four-form indices")
        phi_imaginary_residual = max(
            [abs(complex(value).imag) for value in self.phi.values()] or [0.0]
        )
        if phi_imaginary_residual > 1.0e-12:
            raise ValueError("Phi_210 is a real field; imaginary components are forbidden")
        if not all(_canonical_indices(indices, 5) for indices in self.sigma):
            raise ValueError("Sigma must use canonical independent five-form indices")
        chirality = direct.tensor_norm(
            direct.add_forms(
                direct.hodge_star(self.sigma),
                direct.scale_form(self.sigma, 1j),
            )
        )
        if chirality > 1.0e-10:
            raise ValueError("Sigma must lie in the physical -i Hodge eigenspace")
        phi = {
            indices: complex(complex(value).real)
            for indices, value in self.phi.items()
            if abs(value) > 1.0e-14
        }
        sigma = {
            indices: complex(value)
            for indices, value in self.sigma.items()
            if abs(value) > 1.0e-14
        }
        return FieldState(
            phi=phi,
            h=h.copy(),
            sigma=sigma,
            s=complex(self.s),
            x=complex(self.x),
        )


@dataclasses.dataclass(frozen=True)
class Direction:
    direction_id: str
    orbit_index: int
    basis_index: int
    representative: str
    members: tuple[str, ...]
    self_conjugate: bool
    degree: int
    base_key: tuple[int, ...]
    base_family: str
    basis_label: str
    source_modules: tuple[str, ...]
    normalization: str
    counts: tuple[int, ...]
    value: complex


@dataclasses.dataclass(frozen=True)
class Parameter:
    parameter_id: str
    direction_id: str
    component: str
    self_conjugate: bool


def deterministic_state(seed: int = 20260806) -> FieldState:
    rng = np.random.default_rng(seed)
    phi_vector = rng.normal(size=210)
    phi_vector /= np.linalg.norm(phi_vector)
    phi = {
        indices: complex(phi_vector[index])
        for index, indices in enumerate(itertools.combinations(range(10), 4))
        if abs(phi_vector[index]) > 1.0e-14
    }
    h = rng.normal(size=10) + 1j * rng.normal(size=10)
    h /= np.sqrt(np.vdot(h, h).real)
    sigma_basis = direct.anti_self_dual_five_form_basis()
    coefficients = rng.normal(size=126) + 1j * rng.normal(size=126)
    sigma: direct.Form = {}
    for coefficient, basis_state in zip(coefficients, sigma_basis, strict=True):
        sigma = direct.add_forms(
            sigma, direct.scale_form(basis_state, complex(coefficient))
        )
    sigma = direct.normalize_126(sigma)
    return FieldState(
        phi=phi,
        h=h,
        sigma=sigma,
        s=0.73 - 0.41j,
        x=-0.58 + 0.66j,
    ).validated()


def scale_state(state: FieldState, factor: float) -> FieldState:
    value = state.validated()
    return FieldState(
        phi=direct.scale_form(value.phi, factor),
        h=factor * value.h,
        sigma=direct.scale_form(value.sigma, factor),
        s=factor * value.s,
        x=factor * value.x,
    ).validated()


def _dense_state(state: FieldState) -> dict[str, Any]:
    value = state.validated()
    sigma_dag = conjugate_form(value.sigma)
    return {
        "phi_dense": phi2_sigma_graph.dense_antisymmetric(value.phi, 4),
        "sigma_dense": phi2_sigma_graph.dense_antisymmetric(value.sigma, 5),
        "sigma_dag_dense": phi2_sigma_graph.dense_antisymmetric(sigma_dag, 5),
        "sigma_dag": sigma_dag,
        "sigma_coordinates": phi2_sigma_projector.sigma_coordinates(value.sigma),
        "h_form": vector_form(value.h),
    }


def _phi2_sigma_pure_values(
    state: FieldState, dense: Mapping[str, Any]
) -> list[complex]:
    phi_vector = np.asarray(
        [state.phi.get(index, 0.0) for index in phi2_sigma_projector.projectors.FOUR_INDICES],
        dtype=complex,
    )
    if np.max(np.abs(phi_vector.imag), initial=0.0) > 1.0e-12:
        raise ValueError("Phi_210 must be real")
    pair = np.outer(phi_vector.real, phi_vector.real)
    powers = phi2_sigma_projector.projectors.casimir_powers(pair)
    sigma_vector = np.asarray(dense["sigma_coordinates"], dtype=complex)
    output: list[complex] = []
    for channel in PHISIGMA_ORDER:
        projected = phi2_sigma_projector.projectors.project_from_powers(
            powers,
            phi2_sigma_projector.projectors.COMMON_CHANNEL_EIGENVALUES[channel],
        )
        operator = phi2_sigma_projector.full_sigma_operator(projected)
        output.append(complex(np.vdot(sigma_vector, operator @ sigma_vector)))
    return output


def _phi2_hdag_sigma_values(
    state: FieldState, dense: Mapping[str, Any]
) -> list[complex]:
    """Evaluate ledger orientation Phi^2 Hdag Sigma in 210 and 1050 channels."""
    bilinear = phi2_hsigma.phi2_bilinear(state.phi, state.phi, +1)
    sigma_dag_vector = phi2_hsigma.five_to_vector(dense["sigma_dag"])
    external_source = state.h[:, None] * sigma_dag_vector[None, :]
    output: list[complex] = []
    for projector in (phi2_hsigma.project_210, phi2_hsigma.project_1050):
        source_value = np.vdot(
            projector(bilinear, +1),
            projector(external_source, +1),
        )
        output.append(complex(np.conjugate(source_value)))
    return output


def _base_values(
    state: FieldState,
    base_key: tuple[int, ...],
    dense: Mapping[str, Any],
) -> list[complex]:
    h = state.h
    sigma = state.sigma
    sigma_dag = dense["sigma_dag"]
    if base_key == (0, 0, 0, 0, 0):
        return [1.0 + 0.0j]
    if base_key == (0, 0, 0, 1, 1):
        return [complex(direct.sigma_kinetic_inner(sigma, sigma))]
    if base_key == (0, 0, 2, 0, 0):
        return [complex(np.conjugate(np.dot(h, h)))]
    if base_key == (0, 1, 1, 0, 0):
        return [complex(np.vdot(h, h))]
    if base_key == (2, 0, 0, 0, 0):
        return [complex(phi_self.quadratic_invariant(state.phi))]
    if base_key == (1, 0, 0, 1, 1):
        return [complex(phi_sigma_cubic.cubic_invariant(state.phi, sigma, sigma))]
    if base_key == (1, 0, 1, 0, 1):
        image = direct.contract(state.phi, sigma_dag)
        vector = np.asarray([image.get((index,), 0.0) for index in range(10)])
        return [complex(np.vdot(h, vector))]
    if base_key == (1, 0, 1, 1, 0):
        image = direct.contract(state.phi, sigma)
        vector = np.asarray([image.get((index,), 0.0) for index in range(10)])
        return [complex(np.vdot(h, vector))]
    if base_key == (3, 0, 0, 0, 0):
        return [complex(phi_self.cubic_invariant(state.phi))]
    if base_key == (0, 0, 0, 2, 2):
        values = sigma_self.quartics(np.asarray(dense["sigma_coordinates"]))
        return [complex(values[name]) for name in SIGMA_SELF_ORDER]
    if base_key == (0, 0, 1, 2, 1):
        return [
            complex(
                unique_hsigma.invariant_hdag_sigma2_sigmadag(
                    np.conjugate(h),
                    dense["sigma_dense"],
                    dense["sigma_dag_dense"],
                )
            )
        ]
    if base_key == (0, 0, 2, 2, 0):
        return [
            complex(
                unique_hsigma.invariant_hdag2_sigma2(
                    np.conjugate(h), dense["sigma_dense"]
                )
            )
        ]
    if base_key == (0, 1, 1, 1, 1):
        norm = complex(np.vdot(h, h) * direct.sigma_kinetic_inner(sigma, sigma))
        h_current = current45.hermitian_current_45(
            dense["h_form"], kinetic_factor=1.0
        )
        sigma_current = current45.hermitian_current_45(
            sigma, kinetic_factor=0.5
        )
        return [norm, complex(direct.tensor_inner(h_current, sigma_current))]
    if base_key == (0, 2, 2, 0, 0):
        values = h_self.invariants(h)
        return [complex(values["I_1"]), complex(values["I_54"])]
    if base_key == (2, 0, 0, 1, 1):
        return _phi2_sigma_pure_values(state, dense)
    if base_key == (2, 0, 1, 1, 0):
        return _phi2_hdag_sigma_values(state, dense)
    if base_key == (2, 1, 1, 0, 0):
        values = phi2_h.invariant_values(state.phi, h)
        return [complex(values[name]) for name in PHIH_ORDER]
    if base_key == (4, 0, 0, 0, 0):
        values = phi_self.quartic_invariants(state.phi)
        return [complex(values[name]) for name in ("J0", "J2", "J3", "J4")]
    raise KeyError(f"no G2 base adapter for {base_key}")


def _dressing(state: FieldState, counts: Mapping[str, int]) -> complex:
    return complex(
        state.s ** int(counts.get("S", 0))
        * np.conjugate(state.s) ** int(counts.get("Sb", 0))
        * state.x ** int(counts.get("X", 0))
        * np.conjugate(state.x) ** int(counts.get("Xb", 0))
    )


def _direction_id(orbit_index: int, basis_index: int, base_family: str) -> str:
    return f"O{orbit_index + 1:02d}_B{basis_index + 1:02d}_{base_family}"


def evaluate_directions(state: FieldState) -> tuple[Direction, ...]:
    value = state.validated()
    dense = _dense_state(value)
    directions: list[Direction] = []
    for orbit_index, orbit in enumerate(census.orbits(census.census(False))):
        counts_tuple = tuple(int(item) for item in orbit["orbit_key"])
        counts = dict(zip(FIELD_ORDER, counts_tuple, strict=True))
        base_key = tuple(counts[name] for name in NON_SINGLET_ORDER)
        base = ledger.BASE_FAMILIES[base_key]
        values = _base_values(value, base_key, dense)
        expected = int(orbit["so10_singlet_multiplicity"])
        if len(values) != expected or len(values) != len(base["basis"]):
            raise AssertionError(
                f"{orbit['representative']}: expected {expected} values, got {len(values)}"
            )
        dressing = _dressing(value, counts)
        for basis_index, (label, base_value) in enumerate(
            zip(base["basis"], values, strict=True)
        ):
            directions.append(
                Direction(
                    direction_id=_direction_id(orbit_index, basis_index, base["id"]),
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
                    value=complex(base_value * dressing),
                )
            )
    return tuple(directions)


def parameter_schema(directions: Iterable[Direction]) -> tuple[Parameter, ...]:
    parameters: list[Parameter] = []
    for direction in directions:
        components = ("real",) if direction.self_conjugate else ("re", "im")
        for component in components:
            prefix = "lambda" if component == "real" else component
            parameters.append(
                Parameter(
                    parameter_id=f"{prefix}::{direction.direction_id}",
                    direction_id=direction.direction_id,
                    component=component,
                    self_conjugate=direction.self_conjugate,
                )
            )
    return tuple(parameters)


def coefficient_jacobian(directions: Iterable[Direction]) -> dict[str, float]:
    output: dict[str, float] = {}
    for direction in directions:
        if direction.self_conjugate:
            output[f"lambda::{direction.direction_id}"] = float(direction.value.real)
        else:
            output[f"re::{direction.direction_id}"] = float(2.0 * direction.value.real)
            output[f"im::{direction.direction_id}"] = float(-2.0 * direction.value.imag)
    return output


def potential_value(
    directions: Iterable[Direction], coefficients: Mapping[str, float]
) -> float:
    jacobian = coefficient_jacobian(directions)
    unknown = set(coefficients).difference(jacobian)
    if unknown:
        raise KeyError(f"unknown coefficient keys: {sorted(unknown)}")
    return float(
        sum(
            float(coefficients.get(name, 0.0)) * derivative
            for name, derivative in jacobian.items()
        )
    )


def deterministic_coefficients(parameters: Iterable[Parameter]) -> dict[str, float]:
    return {
        parameter.parameter_id: (((index * 17 + 5) % 29) - 14) / 11.0
        for index, parameter in enumerate(parameters)
    }


def scaling_audit(
    state: FieldState, directions: tuple[Direction, ...]
) -> dict[str, Any]:
    factor = 1.37
    scaled = evaluate_directions(scale_state(state, factor))
    if [row.direction_id for row in scaled] != [row.direction_id for row in directions]:
        raise AssertionError("direction order changed under scaling")
    residuals: dict[str, float] = {}
    for original, transformed in zip(directions, scaled, strict=True):
        target = original.value * factor ** original.degree
        scale = max(abs(target), abs(transformed.value), 1.0)
        residuals[original.direction_id] = float(
            abs(transformed.value - target) / scale
        )
    return {
        "factor": factor,
        "maximum_relative_residual": max(residuals.values()),
        "per_direction_relative_residual": residuals,
    }


def phi2_hdag_sigma_orientation_audit(state: FieldState) -> dict[str, Any]:
    value = state.validated()
    dense = _dense_state(value)
    actual = _phi2_hdag_sigma_values(value, dense)
    bilinear = phi2_hsigma.phi2_bilinear(value.phi, value.phi, +1)
    sigma_dag_vector = phi2_hsigma.five_to_vector(dense["sigma_dag"])
    external_source = value.h[:, None] * sigma_dag_vector[None, :]
    expected = []
    source_values = []
    for projector in (phi2_hsigma.project_210, phi2_hsigma.project_1050):
        source = complex(
            np.vdot(
                projector(bilinear, +1),
                projector(external_source, +1),
            )
        )
        source_values.append(source)
        expected.append(np.conjugate(source))
    residuals = [abs(left - right) for left, right in zip(actual, expected, strict=True)]
    return {
        "source_orientation": "Phi2_H_SigmaDag",
        "ledger_orientation": "Phi2_Hdag_Sigma",
        "source_values": source_values,
        "ledger_values": actual,
        "maximum_conjugation_residual": float(max(residuals)),
    }


def graph_projector_basis_audit(state: FieldState) -> dict[str, Any]:
    value = state.validated()
    dense = _dense_state(value)
    graph_values = phi2_sigma_graph.selected_contractions(
        dense["phi_dense"],
        dense["phi_dense"],
        dense["sigma_dag_dense"],
        dense["sigma_dense"],
    )
    projector_values = _phi2_sigma_pure_values(value, dense)
    direct_label_residual = max(
        abs(complex(graph) - complex(projector))
        for graph, projector in zip(graph_values, projector_values, strict=True)
    )
    return {
        "graph_basis_dimension": len(graph_values),
        "pure_projector_basis_dimension": len(projector_values),
        "direct_relabeling_residual": float(direct_label_residual),
        "direct_graph_to_projector_relabeling_valid": bool(
            direct_label_residual < 1.0e-10
        ),
    }


def _complex_phi_rejected(state: FieldState) -> bool:
    key = next(iter(state.phi))
    phi = dict(state.phi)
    phi[key] = complex(phi[key]) + 1.0e-4j
    try:
        FieldState(phi=phi, h=state.h, sigma=state.sigma, s=state.s, x=state.x).validated()
    except ValueError:
        return True
    return False


def build_report() -> dict[str, Any]:
    g1 = ledger.build_report()
    state = deterministic_state()
    directions = evaluate_directions(state)
    parameters = parameter_schema(directions)
    jacobian = coefficient_jacobian(directions)
    coefficients = deterministic_coefficients(parameters)
    potential = potential_value(directions, coefficients)
    scaling = scaling_audit(state, directions)
    orientation = phi2_hdag_sigma_orientation_audit(state)
    basis_audit = graph_projector_basis_audit(state)

    family_counts: dict[str, int] = {}
    for direction in directions:
        family_counts[direction.base_family] = family_counts.get(direction.base_family, 0) + 1
    self_imaginary_residual = max(
        [abs(direction.value.imag) for direction in directions if direction.self_conjugate]
        or [0.0]
    )
    finite_values = all(
        np.isfinite(direction.value.real) and np.isfinite(direction.value.imag)
        for direction in directions
    )
    nonzero_families = {
        family: any(
            abs(direction.value) > 1.0e-12
            for direction in directions
            if direction.base_family == family
        )
        for family in family_counts
    }
    parameter_ids = [parameter.parameter_id for parameter in parameters]
    direction_ids = [direction.direction_id for direction in directions]
    expected_family_counts = {
        row["id"]: sum(
            int(orbit["multiplicity"])
            for orbit in g1["operator_orbits"]
            if orbit["base_family"] == row["id"]
        )
        for row in ledger.BASE_FAMILIES.values()
    }
    checks = {
        "authoritative_G1_ledger_executes": g1["n_failed"] == 0,
        "authoritative_G1_is_closed": bool(
            g1["flags"]["g1_closed"]
            and g1["closure"]["G1_invariant_ring_and_component_tensors_closed"]
        ),
        "all_48_orbits_compiled": len({row.orbit_index for row in directions}) == 48,
        "all_64_directions_compiled": len(directions) == 64,
        "all_18_base_adapters_used": set(family_counts)
        == {row["id"] for row in ledger.BASE_FAMILIES.values()},
        "family_direction_counts_match_G1": family_counts == expected_family_counts,
        "all_direction_ids_unique": len(set(direction_ids)) == 64,
        "exactly_91_real_parameters": len(parameters) == 91,
        "all_parameter_ids_unique": len(set(parameter_ids)) == 91,
        "coefficient_jacobian_has_91_entries": len(jacobian) == 91,
        "all_values_finite": finite_values,
        "every_base_family_nonzero_on_generic_state": all(nonzero_families.values()),
        "self_conjugate_values_real": self_imaginary_residual < 1.0e-9,
        "potential_value_real_and_finite": np.isfinite(potential),
        "zero_coefficients_give_zero": abs(potential_value(directions, {})) < 1.0e-15,
        "homogeneous_degree_scaling_all_64": scaling["maximum_relative_residual"] < 1.0e-8,
        "real_210_contract_enforced": _complex_phi_rejected(state),
        "Phi2_Hdag_Sigma_orientation_reconstructed": orientation[
            "maximum_conjugation_residual"
        ]
        < 1.0e-11,
        "graph_basis_not_directly_relabelled_as_projectors": not basis_audit[
            "direct_graph_to_projector_relabeling_valid"
        ],
        "complete_real_field_dimension_is_486": REAL_FIELD_DIMENSION == 486,
        "symmetric_Hessian_entries_are_118341": SYMMETRIC_HESSIAN_ENTRIES == 118341,
        "G2_field_gradient_not_claimed": True,
        "G2_field_Hessian_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "LIVE_G2_ARBITRARY_COMPONENT_POTENTIAL_VALUES_ASSEMBLED"
                if not failures
                else "LIVE_G2_ARBITRARY_COMPONENT_POTENTIAL_VALUES_FAILED"
            ),
            "overall_state": "PARTIAL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "counts": {
                "Hermitian_orbits": 48,
                "invariant_directions": len(directions),
                "real_parameters": len(parameters),
                "base_families": len(family_counts),
                "real_field_dimension": REAL_FIELD_DIMENSION,
                "symmetric_Hessian_entries": SYMMETRIC_HESSIAN_ENTRIES,
            },
            "field_conventions": {
                "Phi": "real independent-component SO(10) four-form",
                "H": "complex SO(10) vector with canonical HdagH norm",
                "Sigma": "physical -i Hodge chiral five-form with K=(1/2)<Sigma,Sigma>",
                "S": "complex PQ singlet",
                "Phi17": "complex declared-symmetry singlet",
            },
            "basis_order": direction_ids,
            "directions": directions,
            "parameter_schema": parameters,
            "coefficient_jacobian": jacobian,
            "deterministic_potential_value": potential,
            "family_direction_counts": family_counts,
            "generic_family_nonzero": nonzero_families,
            "self_conjugate_imaginary_residual": self_imaginary_residual,
            "scaling_audit": scaling,
            "Phi2_Hdag_Sigma_orientation_audit": orientation,
            "Phi2_Sigma_basis_audit": basis_audit,
            "flags": {
                "all_64_arbitrary_component_values_callable": not failures,
                "all_48_Hermitian_orbits_compiled": not failures,
                "all_91_real_parameters_compiled": not failures,
                "real_Hermitian_potential_assembled": not failures,
                "coefficient_Jacobian_exact": not failures,
                "real_210_field_enforced": not failures,
                "field_gradient_complete": False,
                "field_Hessian_complete": False,
                "G2_closed": False,
                "simultaneous_vacuum_solved": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Introduce one canonical 486-real field-coordinate vector and "
                "differentiate this 91-parameter potential to emit the complete "
                "gradient and Hessian with operator provenance."
            ),
            "verdict": (
                "All 64 normalized G1 directions evaluate on arbitrary physical "
                "fields and assemble into a real 91-parameter Hermitian potential. "
                "The real-210, chiral-126bar, projector-basis, and fragile conjugate "
                "orientation contracts are explicit. G2 remains PARTIAL until the "
                "complete 486-real gradient and Hessian are constructed."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Live G2 arbitrary-component potential values\n\n"
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
