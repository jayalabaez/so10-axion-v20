#!/usr/bin/env python3
"""Unified arbitrary-component evaluator for all 64 live G1 directions.

The live SO(10)+PQ+Z17 census contains 48 Hermitian-conjugacy orbits and 64
independent invariant coefficients through degree four. G1 fixes a normalized
tensor basis for every direction, but those tensors previously lived in
separate modules and coordinate conventions.

This module binds the eighteen undressed base families to one common field
state:

* Phi: real SO(10) four-form (210_H);
* H: complex length-10 vector (10_H);
* Sigma: canonical -i-Hodge five-form (126bar_H);
* S and Phi17: ordinary complex singlets.

It evaluates the 34 undressed tensor directions, applies the exact singlet
dressings of all 48 live orbits, and returns 64 complex operator values. A
coupling schema then assembles a manifestly real potential: self-conjugate
orbits have real couplings, while paired orbits contribute 2 Re(c O).

This closes an arbitrary-component value-level G2 subgate. It does not yet
provide the complete 590-real gradient/Hessian, a nonzero electroweak vacuum,
a global minimum, thresholds, two-loop running, or proton decay.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as sigma_self
import exact_210_126bar_cubic_clebsch_v20 as phi_sigma_cubic
import exact_210_self_invariant_basis_v20 as phi_self
import exact_h10_self_quartic_family_v20 as h_self
import exact_mixed_45_triplet_channel_v20 as mixed45
import exact_phi2_h_126dag_210_1050_channels_v20 as phi2_hsigma
import exact_phi2_hdagh_channel_family_v20 as phi2_hh
import exact_phisigma_126bar_minus_projectors_v20 as phisigma
import exact_phisigma_casimir_projectors_v20 as pair_projectors
import exact_unique_hsigma_chiral_quartics_v20 as unique
import g1_exact_declared_symmetry_character_census_v20 as census
import live_g1_tensor_closure_ledger_v20 as ledger

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_ALL64_COMPONENT_POTENTIAL_V20.json"
OUT_MD = ROOT / "LIVE_G2_ALL64_COMPONENT_POTENTIAL_V20.md"

BASE_DIRECTION_COUNT = 34
LIVE_DIRECTION_COUNT = 64
LIVE_REAL_PARAMETER_COUNT = 91


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


def conjugate_form(form: direct.Form) -> direct.Form:
    return {indices: np.conjugate(value) for indices, value in form.items()}


def vector_form(vector: np.ndarray) -> direct.Form:
    values = np.asarray(vector, dtype=complex).reshape(10)
    return {
        (index,): complex(value)
        for index, value in enumerate(values)
        if abs(value) > 1.0e-14
    }


def contracted_vector(phi: direct.Form, sigma: direct.Form) -> np.ndarray:
    image = direct.contract(phi, sigma)
    return np.asarray([image.get((index,), 0.0) for index in range(10)], dtype=complex)


def sigma_projector_values(sigma: direct.Form) -> dict[str, float]:
    basis = sigma_self._basis()
    coordinates = np.asarray(
        [direct.sigma_kinetic_inner(state, sigma) for state in basis],
        dtype=complex,
    )
    raw = sigma_self.quartics(coordinates)
    return {
        "54": raw["54"],
        "1050bar": raw["1050bar"],
        "2772bar": raw["2772bar"],
        "4125": raw["4125"],
    }


def hsigma_hermitian_values(h: np.ndarray, sigma: direct.Form) -> dict[str, float]:
    h_vector = np.asarray(h, dtype=complex).reshape(10)
    h_norm = float(np.vdot(h_vector, h_vector).real)
    sigma_norm = float(np.real(direct.sigma_kinetic_inner(sigma, sigma)))
    h_current = mixed45.hermitian_current_45(
        vector_form(h_vector), kinetic_factor=1.0
    )
    sigma_current = mixed45.hermitian_current_45(
        sigma, kinetic_factor=0.5
    )
    current = direct.tensor_inner(h_current, sigma_current)
    return {
        "1": h_norm * sigma_norm,
        "45": float(np.real_if_close(current).real),
    }


def phi2_sigma_values(phi: direct.Form, sigma: direct.Form) -> dict[str, float]:
    phi_vector = pair_projectors._form_to_vector(phi)
    if np.max(np.abs(phi_vector.imag), initial=0.0) > 1.0e-12:
        raise ValueError("Phi must be a real 210 four-form")
    pair = np.outer(phi_vector.real, phi_vector.real)
    powers = pair_projectors.casimir_powers(pair)
    sigma_vector = phisigma.sigma_coordinates(sigma)
    values: dict[str, float] = {}
    for channel in phisigma.CHANNELS:
        projected_pair = pair_projectors.project_from_powers(
            powers, pair_projectors.COMMON_CHANNEL_EIGENVALUES[channel]
        )
        operator = phisigma.full_sigma_operator(projected_pair)
        value = np.vdot(sigma_vector, operator @ sigma_vector)
        if abs(value.imag) > 1.0e-9:
            raise AssertionError(f"Phi2-Sigma {channel} invariant is not real")
        values[channel] = float(value.real)
    return values


def phi2_hdag_sigma_values(
    phi: direct.Form, h: np.ndarray, sigma: direct.Form
) -> dict[str, complex]:
    """Evaluate the ledger orientation Phi^2 Hdag Sigma.

    The source module constructs the conjugate orientation Phi^2 H Sigmadag in
    the +i chiral space. We evaluate that normalized source tensor and complex
    conjugate it, yielding the ledger's Hdag-Sigma representative.
    """
    h_vector = np.asarray(h, dtype=complex).reshape(10)
    sigma_dagger = conjugate_form(sigma)
    sigma_vector = phi2_hsigma.five_to_vector(sigma_dagger)
    external = h_vector[:, None] * sigma_vector[None, :]
    raw = phi2_hsigma.phi2_bilinear(phi, phi, +1)
    projectors = {
        "210": lambda tensor: phi2_hsigma.project_210(tensor, +1),
        "1050": lambda tensor: phi2_hsigma.project_1050(tensor, +1),
    }
    output: dict[str, complex] = {}
    for name, projector in projectors.items():
        source_value = np.vdot(projector(raw), projector(external))
        output[name] = complex(np.conjugate(source_value))
    return output


def base_direction_values(
    *,
    phi: direct.Form,
    h: np.ndarray,
    sigma: direct.Form,
) -> dict[tuple[int, ...], list[complex]]:
    """Return all 34 undressed values in the G1 ledger basis order."""
    h_vector = np.asarray(h, dtype=complex).reshape(10)
    hdag = np.conjugate(h_vector)
    sigma_dagger = conjugate_form(sigma)

    phi_quartics = phi_self.quartic_invariants(phi)
    sigma_quartics = sigma_projector_values(sigma)
    h_quartics = h_self.invariants(h_vector)
    hsigma = hsigma_hermitian_values(h_vector, sigma)
    phi_sigma = phi2_sigma_values(phi, sigma)
    phi_hh = phi2_hh.invariant_values(phi, h_vector)
    phi_hsigma = phi2_hdag_sigma_values(phi, h_vector, sigma)

    sigma_dense = unique.forms.dense_antisymmetric(sigma, 5)
    sigma_dagger_dense = unique.forms.dense_antisymmetric(sigma_dagger, 5)

    values: dict[tuple[int, ...], list[complex]] = {
        (0, 0, 0, 0, 0): [1.0 + 0.0j],
        (0, 0, 0, 1, 1): [
            complex(direct.sigma_kinetic_inner(sigma, sigma))
        ],
        (0, 0, 2, 0, 0): [complex(np.dot(hdag, hdag))],
        (0, 1, 1, 0, 0): [complex(np.vdot(h_vector, h_vector))],
        (2, 0, 0, 0, 0): [complex(phi_self.quadratic_invariant(phi))],
        (1, 0, 0, 1, 1): [
            complex(phi_sigma_cubic.cubic_invariant(phi, sigma, sigma))
        ],
        (1, 0, 1, 0, 1): [
            complex(np.vdot(h_vector, contracted_vector(phi, sigma_dagger)))
        ],
        (1, 0, 1, 1, 0): [
            complex(np.vdot(h_vector, contracted_vector(phi, sigma)))
        ],
        (3, 0, 0, 0, 0): [complex(phi_self.cubic_invariant(phi))],
        (0, 0, 0, 2, 2): [
            complex(sigma_quartics[name])
            for name in ("54", "1050bar", "2772bar", "4125")
        ],
        (0, 0, 1, 2, 1): [
            unique.invariant_hdag_sigma2_sigmadag(
                hdag, sigma_dense, sigma_dagger_dense
            )
        ],
        (0, 0, 2, 2, 0): [
            unique.invariant_hdag2_sigma2(hdag, sigma_dense)
        ],
        (0, 1, 1, 1, 1): [complex(hsigma[name]) for name in ("1", "45")],
        (0, 2, 2, 0, 0): [
            complex(h_quartics[name]) for name in ("I_1", "I_54")
        ],
        (2, 0, 0, 1, 1): [
            complex(phi_sigma[name])
            for name in ("1", "45", "210", "770", "5940", "8910")
        ],
        (2, 0, 1, 1, 0): [
            phi_hsigma[name] for name in ("210", "1050")
        ],
        (2, 1, 1, 0, 0): [
            complex(phi_hh[name]) for name in ("1", "45", "54")
        ],
        (4, 0, 0, 0, 0): [
            complex(phi_quartics[name]) for name in ("J0", "J2", "J3", "J4")
        ],
    }
    expected_keys = set(ledger.BASE_FAMILIES)
    if set(values) != expected_keys:
        raise AssertionError(
            f"base evaluator keys differ from G1 ledger: {set(values) ^ expected_keys}"
        )
    for key, row in values.items():
        expected = int(ledger.BASE_FAMILIES[key]["multiplicity"])
        if len(row) != expected:
            raise AssertionError(f"{key}: expected {expected} values, got {len(row)}")
    return values


def singlet_factor(counts: dict[str, int], *, s: complex, phi17: complex) -> complex:
    return complex(
        complex(s) ** int(counts.get("S", 0))
        * np.conjugate(complex(s)) ** int(counts.get("Sb", 0))
        * complex(phi17) ** int(counts.get("X", 0))
        * np.conjugate(complex(phi17)) ** int(counts.get("Xb", 0))
    )


def operator_directions(
    *,
    phi: direct.Form,
    h: np.ndarray,
    sigma: direct.Form,
    s: complex,
    phi17: complex,
) -> list[dict[str, Any]]:
    base = base_direction_values(phi=phi, h=h, sigma=sigma)
    rows = census.census(False)
    orbits = census.orbits(rows)
    directions: list[dict[str, Any]] = []
    for orbit in orbits:
        orbit_key = tuple(int(value) for value in orbit["orbit_key"])
        key = orbit_key[:5]
        counts = dict(zip(census.FIELD_ORDER, orbit_key))
        factor = singlet_factor(counts, s=s, phi17=phi17)
        base_meta = ledger.BASE_FAMILIES[key]
        values = base[key]
        for index, (basis_name, value) in enumerate(
            zip(base_meta["basis"], values, strict=True)
        ):
            identifier = f"{orbit['representative']}::{basis_name}"
            directions.append(
                {
                    "id": identifier,
                    "representative": orbit["representative"],
                    "members": list(orbit["members"]),
                    "degree": int(orbit["degree"]),
                    "base_key": list(key),
                    "base_family": base_meta["id"],
                    "basis_index": index,
                    "basis_name": basis_name,
                    "self_conjugate": len(orbit["members"]) == 1,
                    "coupling_kind": (
                        "real" if len(orbit["members"]) == 1 else "complex"
                    ),
                    "singlet_factor": factor,
                    "operator_value": complex(value) * factor,
                }
            )
    return directions


def coupling_schema(directions: list[dict[str, Any]]) -> dict[str, Any]:
    real = sum(row["coupling_kind"] == "real" for row in directions)
    complex_count = sum(row["coupling_kind"] == "complex" for row in directions)
    return {
        "directions": len(directions),
        "real_couplings": real,
        "complex_couplings": complex_count,
        "real_parameters": real + 2 * complex_count,
        "entries": [
            {"id": row["id"], "kind": row["coupling_kind"]}
            for row in directions
        ],
    }


def potential_value(
    directions: list[dict[str, Any]], couplings: dict[str, complex]
) -> dict[str, Any]:
    missing = sorted(set(row["id"] for row in directions) - set(couplings))
    extra = sorted(set(couplings) - set(row["id"] for row in directions))
    if missing or extra:
        raise ValueError(f"coupling mismatch: missing={missing}, extra={extra}")
    contributions: dict[str, float] = {}
    total = 0.0
    for row in directions:
        coefficient = complex(couplings[row["id"]])
        operator = complex(row["operator_value"])
        if row["self_conjugate"]:
            if abs(coefficient.imag) > 1.0e-12:
                raise ValueError(f"self-conjugate coupling must be real: {row['id']}")
            if abs(operator.imag) > 1.0e-8:
                raise AssertionError(
                    f"self-conjugate operator is not real: {row['id']}={operator}"
                )
            contribution = float(coefficient.real * operator.real)
        else:
            contribution = float(2.0 * np.real(coefficient * operator))
        contributions[row["id"]] = contribution
        total += contribution
    return {"value": float(total), "contributions": contributions}


def deterministic_state() -> dict[str, Any]:
    singlets = direct.singlet_basis()
    phi = direct.normalize_210_or_10(
        direct.add_forms(
            singlets["p"],
            direct.scale_form(singlets["a"], 0.37),
            direct.scale_form(singlets["omega"], -0.29),
            {(0, 2, 5, 9): 0.23},
        )
    )
    h = np.asarray(
        [
            complex(((7 * i) % 13 - 6) / 7.0, ((5 * i) % 11 - 5) / 9.0)
            for i in range(10)
        ],
        dtype=complex,
    )
    h /= np.sqrt(np.vdot(h, h).real)
    sigma_basis = direct.anti_self_dual_five_form_basis()
    sigma = direct.normalize_126(
        direct.add_forms(
            direct.delta_r(),
            direct.scale_form(sigma_basis[7], 0.21 - 0.13j),
            direct.scale_form(sigma_basis[29], -0.17 + 0.09j),
        )
    )
    return {
        "phi": phi,
        "h": h,
        "sigma": sigma,
        "s": 0.73 + 0.19j,
        "phi17": -0.41 + 0.27j,
    }


def deterministic_couplings(directions: list[dict[str, Any]]) -> dict[str, complex]:
    output: dict[str, complex] = {}
    for index, row in enumerate(directions):
        real = ((17 * index) % 23 - 11) / 37.0
        imag = ((11 * index) % 19 - 9) / 41.0
        output[row["id"]] = complex(real, 0.0 if row["self_conjugate"] else imag)
    return output


def build_report() -> dict[str, Any]:
    g1 = ledger.build_report()
    state = deterministic_state()
    base = base_direction_values(
        phi=state["phi"], h=state["h"], sigma=state["sigma"]
    )
    directions = operator_directions(**state)
    schema = coupling_schema(directions)
    couplings = deterministic_couplings(directions)
    potential = potential_value(directions, couplings)

    base_count = sum(len(row) for row in base.values())
    identifiers = [row["id"] for row in directions]
    finite_values = all(
        np.isfinite(complex(row["operator_value"]).real)
        and np.isfinite(complex(row["operator_value"]).imag)
        for row in directions
    )
    self_real_residual = max(
        [
            abs(complex(row["operator_value"]).imag)
            for row in directions
            if row["self_conjugate"]
        ]
        or [0.0]
    )
    reconstructed = float(sum(potential["contributions"].values()))

    checks = {
        "G1_ledger_executes": g1["n_failed"] == 0,
        "all_18_base_families_bound": set(base) == set(ledger.BASE_FAMILIES),
        "undressed_direction_count_is_34": base_count == BASE_DIRECTION_COUNT,
        "live_direction_count_is_64": len(directions) == LIVE_DIRECTION_COUNT,
        "direction_identifiers_unique": len(set(identifiers)) == len(identifiers),
        "all_direction_values_finite": finite_values,
        "self_conjugate_operator_values_real": self_real_residual < 1.0e-8,
        "coupling_schema_has_91_real_parameters": (
            schema["real_parameters"] == LIVE_REAL_PARAMETER_COUNT
        ),
        "potential_is_manifestly_real_and_finite": np.isfinite(potential["value"]),
        "potential_equals_sum_of_direction_contributions": (
            abs(potential["value"] - reconstructed) < 1.0e-10
        ),
        "complete_gradient_Hessian_not_claimed": True,
        "electroweak_vacuum_not_claimed": True,
        "whole_model_not_validated": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return _jsonable(
        {
            "status": (
                "LIVE_G2_ALL64_VALUE_EVALUATOR_ASSEMBLED__DERIVATIVES_OPEN"
                if not failures
                else "LIVE_G2_ALL64_VALUE_EVALUATOR_FAILED"
            ),
            "overall_state": "PARTIAL",
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "checks": checks,
            "counts": {
                "base_families": len(base),
                "undressed_directions": base_count,
                "hermitian_orbits": len(census.orbits(census.census(False))),
                "live_directions": len(directions),
                "real_couplings": schema["real_couplings"],
                "complex_couplings": schema["complex_couplings"],
                "real_parameters": schema["real_parameters"],
            },
            "field_convention": {
                "Phi": "real independent-component four-form, canonical 210 norm",
                "H": "complex length-10 vector",
                "Sigma": "canonical kinetic-normalized -i-Hodge five-form",
                "S": "complex scalar",
                "Phi17": "complex scalar",
            },
            "base_family_ids": {
                ",".join(str(item) for item in key): ledger.BASE_FAMILIES[key]["id"]
                for key in ledger.BASE_FAMILIES
            },
            "coupling_schema": schema,
            "deterministic_potential_value": potential["value"],
            "maximum_self_conjugate_imaginary_residual": self_real_residual,
            "flags": {
                "all_18_base_evaluators_bound": not failures,
                "all_34_undressed_directions_evaluable": not failures,
                "all_64_live_directions_evaluable": not failures,
                "manifestly_real_91_parameter_potential_value": not failures,
                "complete_G2_component_potential_value_evaluator": not failures,
                "complete_G2_gradient": False,
                "complete_G2_Hessian": False,
                "nonzero_electroweak_backreaction": False,
                "global_vacuum": False,
                "whole_model_validated": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Define one canonical 590-real coordinate vector and derive/verify "
                "the complete gradient and Hessian of this 64-direction potential."
            ),
            "verdict": (
                "All 64 live normalized operator directions are now bound to one "
                "arbitrary-component value evaluator with the exact 91-real-parameter "
                "Hermitian coupling schema. This closes the value-level G2 assembly "
                "subgate only; complete derivatives and vacuum analysis remain open."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Live G2 all-64 component potential evaluator\n\n"
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
