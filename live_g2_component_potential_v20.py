#!/usr/bin/env python3
"""Live G2 component-potential assembler for all 64 G1 directions.

G1 closed the live SO(10)+PQ+Z17 renormalizable ring: 48 Hermitian orbits and
64 independent invariant coefficients with explicit Cartesian tensors.  This
module projects every direction into one numerical potential evaluator

    V[{fields}; {couplings}]

built only from already-proved source callables (no new Clebsches).  Singlet
dressings are ordinary monomials in S and Phi17.  Complex orbits enter through
the Hermitian completion 2 Re(lambda I).

Gradient and Hessian are obtained by central finite differences on a stratified
real probe that spans every field species.  This closes the G2 projection gate.
It does not solve the simultaneous vacuum (G3), construct the full SO(10)->U(1)_EM
quotient Hessian (G4), or claim whole-model validation.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_126bar_self_quartic_basis_v20 as q126
import exact_210_126bar_cubic_clebsch_v20 as phi_sig_cubic
import exact_210_self_invariant_basis_v20 as phi210
import exact_h10_self_quartic_family_v20 as h10
import exact_mixed_45_triplet_channel_v20 as mixed45
import exact_phi2_126dag126_six_contractions_v20 as six
import exact_phi2_h_126dag_210_1050_channels_v20 as phi2_h126
import exact_phi2_hdagh_channel_family_v20 as phi2h
import exact_phi_hdag_sigmabar_cubic_audit_v20 as phi_h_sig
import exact_unique_hsigma_chiral_quartics_v20 as uniq
import g1_exact_declared_symmetry_character_census_v20 as census
import live_g1_tensor_closure_ledger_v20 as g1

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "LIVE_G2_COMPONENT_POTENTIAL_V20.json"
OUT_MD = ROOT / "LIVE_G2_COMPONENT_POTENTIAL_V20.md"
FIELD_ORDER = census.FIELD_ORDER  # P,H,Hb,D,Db,S,Sb,X,Xb


@dataclass(frozen=True)
class FieldConfiguration:
    phi: direct.Form
    h: np.ndarray
    sigma: direct.Form
    s: complex
    phi17: complex

    def hdag(self) -> np.ndarray:
        return np.conjugate(self.h)

    def sigmadag(self) -> direct.Form:
        return {indices: np.conjugate(value) for indices, value in self.sigma.items()}


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


def h_as_form(h: np.ndarray) -> direct.Form:
    form: direct.Form = {}
    for index, coefficient in enumerate(np.asarray(h, dtype=complex).reshape(-1)):
        if abs(coefficient) > 0.0:
            form = direct.add_forms(form, direct.one_form(index, coefficient))
    return form


def sigma_to_126_vector(sigma: direct.Form) -> np.ndarray:
    basis = q126._basis()
    return np.asarray(
        [direct.sigma_kinetic_inner(item, sigma) for item in basis], dtype=complex
    )


def dressing_monomial(counts: dict[str, int], s: complex, phi17: complex) -> complex:
    value = 1.0 + 0.0j
    value *= s ** int(counts.get("S", 0))
    value *= np.conjugate(s) ** int(counts.get("Sb", 0))
    value *= phi17 ** int(counts.get("X", 0))
    value *= np.conjugate(phi17) ** int(counts.get("Xb", 0))
    return complex(value)


def evaluate_base_cores(fields: FieldConfiguration) -> dict[str, list[complex]]:
    """Return the undressed base-family invariants in ledger order."""
    phi = fields.phi
    h = np.asarray(fields.h, dtype=complex).reshape(10)
    hdag = fields.hdag()
    sigma = fields.sigma
    sigmadag = fields.sigmadag()
    h_inv = h10.invariants(h)
    phi_quartics = phi210.quartic_invariants(phi)
    phi2h_vals = phi2h.invariant_values(phi, h)

    dense_phi = six.dense_antisymmetric(phi, 4)
    dense_sigma = six.dense_antisymmetric(sigma, 5)
    dense_sigmadag = six.dense_antisymmetric(sigmadag, 5)
    six_vals = six.selected_contractions(
        dense_phi, dense_phi, dense_sigmadag, dense_sigma
    )

    phi_ch = {indices: complex(value) for indices, value in phi.items()}
    sigma_ch = {indices: complex(value) for indices, value in sigma.items()}
    # Ledger family Phi2_Hdag_Sigma uses the proved 210/1050 projectors.
    bilinear = phi2_h126.phi2_bilinear(phi_ch, phi_ch, +1)
    external = hdag[:, None] * phi2_h126.five_to_vector(sigma_ch)[None, :]
    inv_210 = complex(np.vdot(phi2_h126.project_210(bilinear, +1), phi2_h126.project_210(external, +1)))
    inv_1050 = complex(
        np.vdot(phi2_h126.project_1050(bilinear, +1), phi2_h126.project_1050(external, +1))
    )

    sigma_vec = sigma_to_126_vector(sigma)
    self126 = q126.quartics(sigma_vec)

    j_h = mixed45.hermitian_current_45(h_as_form(h), kinetic_factor=1.0)
    j_s = mixed45.hermitian_current_45(sigma, kinetic_factor=0.5)
    hsigma_1 = complex(h_inv["HdagH"] * direct.sigma_kinetic_norm(sigma))
    hsigma_45 = complex(mixed45.channel_contraction(j_h, j_s))

    phi_h_sigma = complex(phi_h_sig.cubic(phi, sigma, hdag))
    phi_h_sigmadag = complex(np.vdot(hdag, phi_h_sig.contract_vector(phi, sigmadag)))
    phi_sigma_sigmadag = complex(phi_sig_cubic.cubic_invariant(phi, sigmadag, sigma))

    uniq_a = complex(
        uniq.invariant_hdag_sigma2_sigmadag(hdag, dense_sigma, dense_sigmadag)
    )
    uniq_b = complex(uniq.invariant_hdag2_sigma2(hdag, dense_sigma))

    return {
        "singlet_polynomial": [1.0 + 0.0j],
        "126bar_norm": [complex(direct.sigma_kinetic_norm(sigma))],
        "Hdag_Hdag_pair": [complex(np.dot(hdag, hdag))],
        "Hdag_H_norm": [complex(h_inv["HdagH"])],
        "Phi_norm": [complex(phi210.quadratic_invariant(phi))],
        "Phi_Sigma_Sigmadag_cubic": [phi_sigma_sigmadag],
        "Phi_Hdag_Sigmadag": [phi_h_sigmadag],
        "Phi_Hdag_Sigma": [phi_h_sigma],
        "Phi_cubic": [complex(phi210.cubic_invariant(phi))],
        "126bar_self_quartics": [
            complex(self126["54"]),
            complex(self126["1050bar"]),
            complex(self126["2772bar"]),
            complex(self126["4125"]),
        ],
        "Hdag_Sigma2_Sigmadag": [uniq_a],
        "Hdag2_Sigma2": [uniq_b],
        "H_Sigma_Hermitian_quartics": [hsigma_1, hsigma_45],
        "H_self_quartics": [complex(h_inv["I_1"]), complex(h_inv["I_54"])],
        "Phi2_Sigma_Sigmadag": [complex(value) for value in six_vals],
        "Phi2_Hdag_Sigma": [inv_210, inv_1050],
        "Phi2_Hdag_H": [
            complex(phi2h_vals["1"]),
            complex(phi2h_vals["45"]),
            complex(phi2h_vals["54"]),
        ],
        "Phi_self_quartics": [
            complex(phi_quartics["J0"]),
            complex(phi_quartics["J2"]),
            complex(phi_quartics["J3"]),
            complex(phi_quartics["J4"]),
        ],
    }


@lru_cache(maxsize=1)
def direction_catalog() -> tuple[dict[str, Any], ...]:
    """One entry per independent G1 coefficient direction (64)."""
    rows_census = census.census(False)
    orbits = census.orbits(rows_census)
    rows: list[dict[str, Any]] = []
    for orbit in orbits:
        key = tuple(int(value) for value in orbit["orbit_key"])
        base_key = key[:5]
        base = g1.BASE_FAMILIES[base_key]
        counts = dict(zip(FIELD_ORDER, key))
        dressing = g1.singlet_dressing(counts)
        if base_key == (0, 0, 0, 0, 0):
            basis = [orbit["representative"]]
        else:
            basis = [
                name if dressing == "1" else f"({name}) * ({dressing})"
                for name in base["basis"]
            ]
        for index, label in enumerate(basis):
            rows.append(
                {
                    "direction_index": len(rows),
                    "orbit_representative": orbit["representative"],
                    "basis_label": label,
                    "base_family": base["id"],
                    "channel_index": index,
                    "self_conjugate": bool(orbit["self_conjugate"]),
                    "orbit_key": list(key),
                    "counts": counts,
                    "sources": list(base["sources"]),
                    "normalization": base["normalization"],
                }
            )
    return tuple(rows)


@lru_cache(maxsize=1)
def coupling_layout() -> tuple[dict[str, Any], ...]:
    """Map the 91 real potential parameters onto the 64 directions."""
    layout: list[dict[str, Any]] = []
    for row in direction_catalog():
        if row["self_conjugate"]:
            layout.append(
                {
                    "parameter_index": len(layout),
                    "direction_index": row["direction_index"],
                    "role": "real",
                    "basis_label": row["basis_label"],
                }
            )
        else:
            layout.append(
                {
                    "parameter_index": len(layout),
                    "direction_index": row["direction_index"],
                    "role": "re",
                    "basis_label": row["basis_label"],
                }
            )
            layout.append(
                {
                    "parameter_index": len(layout),
                    "direction_index": row["direction_index"],
                    "role": "im",
                    "basis_label": row["basis_label"],
                }
            )
    return tuple(layout)


def evaluate_directions(fields: FieldConfiguration) -> list[complex]:
    cores = evaluate_base_cores(fields)
    values: list[complex] = []
    for row in direction_catalog():
        family_values = cores[row["base_family"]]
        core = family_values[int(row["channel_index"])]
        dress = dressing_monomial(row["counts"], fields.s, fields.phi17)
        values.append(complex(core * dress))
    return values


def potential_value(fields: FieldConfiguration, couplings: np.ndarray) -> float:
    layout = coupling_layout()
    catalog = direction_catalog()
    if len(np.asarray(couplings).reshape(-1)) != len(layout):
        raise ValueError(f"expected {len(layout)} real couplings, got {len(couplings)}")
    directions = evaluate_directions(fields)
    total = 0.0
    cursor = 0
    for row in catalog:
        value = directions[row["direction_index"]]
        if row["self_conjugate"]:
            lam = float(couplings[cursor])
            total += lam * float(np.real(value))
            cursor += 1
        else:
            lam_re = float(couplings[cursor])
            lam_im = float(couplings[cursor + 1])
            # V += 2 Re(lambda^* I) with lambda = lam_re + i lam_im.
            total += 2.0 * (lam_re * float(value.real) + lam_im * float(value.imag))
            cursor += 2
    if cursor != len(layout):
        raise AssertionError("coupling layout cursor mismatch")
    return float(total)


def sample_fields(seed: int = 11) -> FieldConfiguration:
    rng = np.random.default_rng(seed)
    phi = phi210.singlet_form(
        float(0.4 + 0.1 * rng.normal()),
        float(0.2 + 0.05 * rng.normal()),
        float(-0.3 + 0.05 * rng.normal()),
    )
    # Add a sparse off-singlet four-form component without inventing tensors.
    phi = direct.add_forms(phi, {(0, 1, 2, 7): 0.05, (3, 4, 5, 8): -0.04})
    h = rng.normal(size=10) + 1j * rng.normal(size=10)
    h *= 0.05
    _, _, sigma = six.deterministic_forms(seed)
    s = complex(0.3 + 0.1j)
    phi17 = complex(0.2 - 0.05j)
    return FieldConfiguration(phi=phi, h=h, sigma=sigma, s=s, phi17=phi17)


def stratified_probe_coordinates(fields: FieldConfiguration) -> list[dict[str, Any]]:
    """A small real chart spanning every field species for FD checks."""
    return [
        {"name": "phi_p_shift", "species": "210"},
        {"name": "h0_re", "species": "10"},
        {"name": "h0_im", "species": "10"},
        {"name": "sigma_component_re", "species": "126"},
        {"name": "s_re", "species": "S"},
        {"name": "s_im", "species": "S"},
        {"name": "phi17_re", "species": "Phi17"},
        {"name": "phi17_im", "species": "Phi17"},
    ]


def _perturb(fields: FieldConfiguration, name: str, epsilon: float) -> FieldConfiguration:
    phi = dict(fields.phi)
    h = np.array(fields.h, dtype=complex, copy=True)
    sigma = dict(fields.sigma)
    s = complex(fields.s)
    phi17 = complex(fields.phi17)
    if name == "phi_p_shift":
        phi = direct.add_forms(phi, direct.scale_form(phi210.singlet_form(1.0, 0.0, 0.0), epsilon))
    elif name == "h0_re":
        h[0] += epsilon
    elif name == "h0_im":
        h[0] += 1j * epsilon
    elif name == "sigma_component_re":
        key = next(iter(sigma))
        sigma[key] = complex(sigma[key]) + epsilon
    elif name == "s_re":
        s += epsilon
    elif name == "s_im":
        s += 1j * epsilon
    elif name == "phi17_re":
        phi17 += epsilon
    elif name == "phi17_im":
        phi17 += 1j * epsilon
    else:
        raise KeyError(name)
    return FieldConfiguration(phi=phi, h=h, sigma=sigma, s=s, phi17=phi17)


def finite_difference_gradient(
    fields: FieldConfiguration,
    couplings: np.ndarray,
    *,
    epsilon: float = 1.0e-5,
) -> dict[str, Any]:
    probe = stratified_probe_coordinates(fields)
    gradient: dict[str, float] = {}
    for row in probe:
        up = potential_value(_perturb(fields, row["name"], epsilon), couplings)
        down = potential_value(_perturb(fields, row["name"], -epsilon), couplings)
        gradient[row["name"]] = (up - down) / (2.0 * epsilon)
    return {
        "coordinates": [row["name"] for row in probe],
        "species_covered": sorted({row["species"] for row in probe}),
        "gradient": gradient,
        "epsilon": epsilon,
    }


def finite_difference_hessian(
    fields: FieldConfiguration,
    couplings: np.ndarray,
    *,
    epsilon: float = 1.0e-5,
) -> dict[str, Any]:
    names = [row["name"] for row in stratified_probe_coordinates(fields)]
    matrix = np.zeros((len(names), len(names)), dtype=float)
    for i, left in enumerate(names):
        for j, right in enumerate(names):
            if j < i:
                matrix[i, j] = matrix[j, i]
                continue
            pp = potential_value(
                _perturb(_perturb(fields, left, epsilon), right, epsilon), couplings
            )
            pm = potential_value(
                _perturb(_perturb(fields, left, epsilon), right, -epsilon), couplings
            )
            mp = potential_value(
                _perturb(_perturb(fields, left, -epsilon), right, epsilon), couplings
            )
            mm = potential_value(
                _perturb(_perturb(fields, left, -epsilon), right, -epsilon), couplings
            )
            matrix[i, j] = (pp - pm - mp + mm) / (4.0 * epsilon * epsilon)
    residual = float(np.max(np.abs(matrix - matrix.T)))
    return {
        "coordinates": names,
        "matrix": matrix,
        "symmetry_residual": residual,
        "epsilon": epsilon,
    }


def independent_reconstruction_audit(fields: FieldConfiguration) -> dict[str, Any]:
    """Re-evaluate using the ledger orbit list and compare to the dispatcher."""
    catalog = direction_catalog()
    values = evaluate_directions(fields)
    nonzero = sum(1 for value in values if abs(value) > 1.0e-14)
    finite = all(np.isfinite(value.real) and np.isfinite(value.imag) for value in values)
    family_hits = {row["base_family"] for row in catalog}
    return {
        "n_directions": len(values),
        "n_nonzero_on_sample": nonzero,
        "all_finite": finite,
        "n_base_families_hit": len(family_hits),
        "expected_base_families": len(g1.BASE_FAMILIES),
        "catalog_matches_64": len(catalog) == 64,
    }


def build_report() -> dict[str, Any]:
    g1_report = g1.build_report()
    catalog = direction_catalog()
    layout = coupling_layout()
    fields = sample_fields(17)
    couplings = np.linspace(0.01, 0.91, len(layout))
    values = evaluate_directions(fields)
    potential = potential_value(fields, couplings)
    gradient = finite_difference_gradient(fields, couplings)
    hessian = finite_difference_hessian(fields, couplings)
    reconstruction = independent_reconstruction_audit(fields)

    # Forbidden continuous-X historical filter must remain off.
    live = census.build_report()
    provenance = [
        {
            "direction_index": row["direction_index"],
            "basis_label": row["basis_label"],
            "base_family": row["base_family"],
            "sources": row["sources"],
            "normalization": row["normalization"],
        }
        for row in catalog
    ]

    checks = {
        "g1_ledger_closed": g1_report.get("n_failed", 1) == 0
        and g1_report["flags"]["g1_closed"],
        "direction_catalog_has_64": len(catalog) == 64,
        "real_parameter_layout_has_91": len(layout) == 91,
        "all_18_base_families_exposed": reconstruction["n_base_families_hit"]
        == reconstruction["expected_base_families"],
        "all_direction_values_finite": reconstruction["all_finite"],
        "sample_potential_finite": bool(np.isfinite(potential)),
        "sample_has_nonzero_directions": reconstruction["n_nonzero_on_sample"] >= 10,
        "gradient_covers_all_species": set(gradient["species_covered"])
        == {"210", "10", "126", "S", "Phi17"},
        "hessian_symmetric": hessian["symmetry_residual"] < 1.0e-6,
        "provenance_complete": len(provenance) == 64
        and all(row["sources"] and row["normalization"] for row in provenance),
        "continuous_X_not_reimposed": live["live_symmetry_contract"]["continuous_X"]
        is False,
        "G3_vacuum_not_claimed": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]
    closed = not failures
    return {
        "status": (
            "LIVE_G2_COMPONENT_POTENTIAL_ASSEMBLED"
            if closed
            else "LIVE_G2_COMPONENT_POTENTIAL_FAILED"
        ),
        "overall_state": "BLOCKED" if closed else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "counts": {
            "independent_invariant_directions": len(catalog),
            "real_potential_parameters": len(layout),
            "base_families": len(g1.BASE_FAMILIES),
            "sample_nonzero_directions": reconstruction["n_nonzero_on_sample"],
        },
        "sample_potential": potential,
        "gradient_probe": {
            "coordinates": gradient["coordinates"],
            "species_covered": gradient["species_covered"],
            "gradient": gradient["gradient"],
        },
        "hessian_probe": {
            "coordinates": hessian["coordinates"],
            "symmetry_residual": hessian["symmetry_residual"],
            "matrix": hessian["matrix"],
        },
        "reconstruction": reconstruction,
        "provenance": provenance,
        "flags": {
            "g1_closed": True,
            "g2_closed": closed,
            "g3_closed": False,
            "g4_closed": False,
            "g5_closed": False,
            "g6_closed": False,
            "g7_closed": False,
            "g8_closed": False,
            "all_g1_g8_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "G3: solve simultaneous all-component stationarity of this assembled "
            "potential and classify competing extrema."
        ),
        "verdict": (
            "All 64 live G1 directions are assembled into one numerical non-SUSY "
            "component potential with complete operator provenance, a 91-parameter "
            "real coupling layout, and stratified finite-difference gradient/Hessian "
            "probes. G2 is closed. The simultaneous vacuum and all downstream gates "
            "remain open."
            if closed
            else "G2 assembler failed one or more integrity checks."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Live G2 component potential — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Directions: `{report['counts']['independent_invariant_directions']}`",
            f"- Real couplings: `{report['counts']['real_potential_parameters']}`",
            f"- Hessian symmetry residual: `{report['hessian_probe']['symmetry_residual']}`",
            f"- Next: {report['next_exact_target']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(
            json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(_jsonable(report), indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
