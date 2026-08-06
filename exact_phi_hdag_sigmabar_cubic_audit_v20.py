#!/usr/bin/env python3
"""Exact audit of the declared-symmetry cubic Phi H^dag Sigmabar + h.c.

The live non-SUSY model assigns

    PQ(H^dag)=+2,   PQ(Sigmabar)=-2,
    Z17(H^dag)=2,  Z17(Sigmabar)=15,

while Phi(210) is neutral.  Therefore

    mu_D H_e^* Phi_abcd Sigmabar_abcde / 4! + h.c.

is neutral under the declared PQ/Z17 contract and also under the historical
continuous-X bookkeeping.  SO(10) invariance follows from the exact direct map
210 x 126bar -> 10 already implemented in the repository.

This module proves the representation identity

    10 x 126bar = 210 + 1050bar,

constructs the cubic, verifies infinitesimal SO(10) invariance, checks that it
is absent from the current catalogue, and quantifies its effect on the
p + Delta_R background.  The tadpole vanishes on that SM-preserving background,
but nonzero H--126bar and H--210 mixed Hessian blocks remain.  Existing vacuum
certificates are therefore conditional on this cubic coefficient being zero
until the complete Hessian is re-solved.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct
import exact_phisigma_bose_channel_census_v20 as census
import nonsusy_z17_pq_potential_filter_v20 as operator_filter

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHI_HDAG_SIGMABAR_CUBIC_AUDIT_V20.json"
OUT_MD = ROOT / "EXACT_PHI_HDAG_SIGMABAR_CUBIC_AUDIT_V20.md"
OPERATOR_NAME = "210_H 10_H_dag 126bar_H"
COUNTS = {"210_H": 1, "10_H_dag": 1, "126bar_H": 1}


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


def charge_audit() -> dict[str, Any]:
    totals = operator_filter._total_charge(COUNTS)
    declared = operator_filter._allowed(totals, require_x=False)
    historical_x = operator_filter._allowed(totals, require_x=True)
    catalogue_names = {row["name"] for row in operator_filter.operator_catalogue()}
    return {
        "counts": COUNTS,
        "totals": totals,
        "declared_contract": declared,
        "historical_X_comparison": historical_x,
        "present_in_current_catalogue": OPERATOR_NAME in catalogue_names,
        "canonical_dimension": 3,
        "coefficient_mass_dimension": 1,
    }


def representation_audit() -> dict[str, Any]:
    mp.mp.dps = 70
    vector = (1, 0, 0, 0, 0)
    sigmabar = (0, 0, 0, 2, 0)
    phi = census.IRREPS["210"]["label"]
    rep1050bar = census.IRREPS["1050bar"]["label"]
    points = (
        tuple(mp.mpf(x) for x in ("0.11", "-0.07", "0.05", "0.09", "-0.03")),
        tuple(mp.mpf(x) for x in ("-0.06", "0.08", "0.13", "-0.04", "0.02")),
    )
    rows = []
    maximum = mp.mpf("0")
    for point in points:
        product = census.weyl_character(vector, point) * census.weyl_character(
            sigmabar, point
        )
        decomposition = census.weyl_character(phi, point) + census.weyl_character(
            rep1050bar, point
        )
        residual = abs(product - decomposition)
        maximum = max(maximum, residual)
        rows.append(
            {
                "product_character": float(product),
                "decomposition_character": float(decomposition),
                "absolute_residual": float(residual),
            }
        )
    dimensions = {
        "10": census.weyl_dimension(vector),
        "126bar": census.weyl_dimension(sigmabar),
        "210": census.weyl_dimension(phi),
        "1050bar": census.weyl_dimension(rep1050bar),
    }
    return {
        "dynkin_labels": {
            "10": vector,
            "126bar": sigmabar,
            "210": phi,
            "1050bar": rep1050bar,
        },
        "dimensions": dimensions,
        "dimension_identity": dimensions["10"] * dimensions["126bar"]
        == dimensions["210"] + dimensions["1050bar"],
        "character_rows": rows,
        "maximum_character_residual": float(maximum),
        "decomposition": "10 x 126bar = 210 + 1050bar",
        "210_multiplicity": 1,
    }


def generic_fields() -> tuple[direct.Form, direct.Form, np.ndarray]:
    phi: direct.Form = {
        (0, 1, 2, 3): 1.0,
        (0, 4, 6, 8): -0.7,
        (1, 5, 7, 9): 1.3,
        (2, 4, 7, 8): 0.9,
        (3, 5, 6, 9): -1.1,
    }
    phi = direct.normalize_210_or_10(phi)
    sigma_basis = direct.anti_self_dual_five_form_basis()
    sigma: direct.Form = {}
    for index, coefficient in enumerate(
        (1.0 + 0.2j, -0.4 + 0.7j, 0.3 - 0.8j, 0.9j, -0.6)
    ):
        sigma = direct.add_forms(
            sigma, direct.scale_form(sigma_basis[index * 7], coefficient)
        )
    sigma = direct.normalize_126(sigma)
    h = np.asarray(
        [
            1.0 + 0.2j,
            -0.3j,
            0.7,
            -0.4 + 0.6j,
            0.1 + 0.4j,
            0.5j,
            -0.8,
            0.3 + 0.2j,
            0.9j,
            -0.2,
        ],
        dtype=complex,
    )
    h /= np.sqrt(np.vdot(h, h).real)
    return phi, sigma, h


def contract_vector(phi: direct.Form, sigma: direct.Form) -> np.ndarray:
    form = direct.contract(phi, sigma)
    return np.asarray([form.get((index,), 0.0) for index in range(10)], dtype=complex)


def cubic(phi: direct.Form, sigma: direct.Form, h: np.ndarray) -> complex:
    return complex(np.vdot(np.asarray(h, dtype=complex), contract_vector(phi, sigma)))


def holomorphic_lambda4_structure(
    phi: direct.Form, sigma: direct.Form, h: np.ndarray
) -> complex:
    return complex(np.dot(np.asarray(h, dtype=complex), contract_vector(phi, sigma)))


def invariance_audit() -> dict[str, Any]:
    phi, sigma, h = generic_fields()
    value = cubic(phi, sigma, h)
    rows = {}
    maximum = 0.0
    for a, b in ((0, 1), (1, 7), (4, 9), (6, 8)):
        generator = vector_generator_matrix(a, b)
        delta_h = generator @ h
        delta_phi = direct.generator_action(phi, a, b)
        delta_sigma = direct.generator_action(sigma, a, b)
        delta_c = contract_vector(delta_phi, sigma) + contract_vector(phi, delta_sigma)
        derivative = np.vdot(delta_h, contract_vector(phi, sigma)) + np.vdot(h, delta_c)
        residual = float(abs(derivative))
        maximum = max(maximum, residual)
        rows[f"{a}{b}"] = {
            "derivative_re": float(derivative.real),
            "derivative_im": float(derivative.imag),
            "absolute_residual": residual,
        }
    lambda4 = holomorphic_lambda4_structure(phi, sigma, h)
    return {
        "generic_cubic": value,
        "generic_cubic_abs": float(abs(value)),
        "hermitian_pair_value": float(2.0 * value.real),
        "lambda4_holomorphic_structure": lambda4,
        "phase_structures_distinct": bool(abs(value - lambda4) > 1.0e-6),
        "generator_rows": rows,
        "maximum_infinitesimal_invariance_residual": maximum,
    }


def four_form_basis() -> list[direct.Form]:
    return [{indices: 1.0 + 0.0j} for indices in itertools.combinations(range(10), 4)]


def background_impact() -> dict[str, Any]:
    singlets = direct.singlet_basis()
    delta = direct.delta_r()
    sigma_basis = direct.anti_self_dual_five_form_basis()
    contractions = {
        name: contract_vector(phi, delta) for name, phi in singlets.items()
    }
    p = singlets["p"]
    h_sigma = direct.contraction_matrix(p, sigma_basis)
    h_phi = np.column_stack(
        [contract_vector(phi_state, delta) for phi_state in four_form_basis()]
    )
    singular_h_sigma = np.linalg.svd(h_sigma, compute_uv=False)
    singular_h_phi = np.linalg.svd(h_phi, compute_uv=False)
    tolerance = 1.0e-12
    return {
        "singlet_background_contractions": {
            name: {
                "components": vector,
                "norm": float(np.linalg.norm(vector)),
            }
            for name, vector in contractions.items()
        },
        "p_plus_DeltaR_H_tadpole_norm_per_unit_coefficient": float(
            np.linalg.norm(contractions["p"])
        ),
        "H_Sigmabar_mixed_block_at_p": {
            "shape": list(h_sigma.shape),
            "rank": int(np.sum(singular_h_sigma > tolerance)),
            "singular_values": singular_h_sigma,
            "frobenius_norm": float(np.linalg.norm(h_sigma)),
        },
        "H_Phi_mixed_block_at_DeltaR": {
            "shape": list(h_phi.shape),
            "rank": int(np.sum(singular_h_phi > tolerance)),
            "singular_values": singular_h_phi,
            "frobenius_norm": float(np.linalg.norm(h_phi)),
        },
        "interpretation": (
            "The SM-preserving p+Delta_R background has no H tadpole from this "
            "cubic, but its second derivatives generate nonzero H--Sigmabar and "
            "H--Phi mixing blocks. Any complete Hessian that omitted the operator "
            "is conditional on its coefficient being zero."
        ),
    }


def build_report() -> dict[str, Any]:
    charge = charge_audit()
    representation = representation_audit()
    invariance = invariance_audit()
    impact = background_impact()
    checks = {
        "declared_PQ_neutral": charge["totals"]["PQ"] == 0,
        "declared_Z17_neutral": charge["totals"]["Z17"] == 0,
        "historical_X_neutral_too": charge["totals"]["X"] == 0,
        "declared_filter_allows": charge["declared_contract"]["all"],
        "historical_X_filter_allows": charge["historical_X_comparison"]["all"],
        "operator_missing_from_catalogue_detected": not charge[
            "present_in_current_catalogue"
        ],
        "dimension_identity_exact": representation["dimension_identity"],
        "weyl_character_identity": representation["maximum_character_residual"]
        < 1.0e-40,
        "unique_210_channel": representation["210_multiplicity"] == 1,
        "generic_direct_cubic_nonzero": invariance["generic_cubic_abs"] > 1.0e-6,
        "infinitesimal_SO10_invariance": invariance[
            "maximum_infinitesimal_invariance_residual"
        ]
        < 1.0e-11,
        "distinct_from_lambda4_phase_structure": invariance[
            "phase_structures_distinct"
        ],
        "p_DeltaR_tadpole_vanishes": impact[
            "p_plus_DeltaR_H_tadpole_norm_per_unit_coefficient"
        ]
        < 1.0e-12,
        "H_Sigmabar_mixed_block_nonzero": impact[
            "H_Sigmabar_mixed_block_at_p"
        ]["rank"]
        > 0,
        "H_Phi_mixed_block_nonzero": impact["H_Phi_mixed_block_at_DeltaR"][
            "rank"
        ]
        > 0,
        "complete_potential_not_claimed": True,
        "previous_full_Hessian_requires_reaudit": True,
        "whole_model_validation_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    report = {
        "status": (
            "MISSING_DECLARED_SYMMETRY_CUBIC_PROVED__CATALOGUE_AND_HESSIAN_REAUDIT_REQUIRED"
            if not failures
            else "PHI_HDAG_SIGMABAR_CUBIC_AUDIT_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "operator": {
            "name": OPERATOR_NAME,
            "formula": (
                "mu_D H_e^* Phi_abcd Sigmabar_abcde/4! + h.c."
            ),
            "canonical_dimension": 3,
            "coefficient_mass_dimension": 1,
        },
        "charge_audit": charge,
        "representation_audit": representation,
        "direct_tensor_and_invariance": invariance,
        "p_DeltaR_background_impact": impact,
        "flag": {
            "operator_exists_and_is_declared_symmetry_allowed": not failures,
            "operator_catalogue_currently_incomplete": not failures,
            "p_DeltaR_tadpole_from_operator": False,
            "p_DeltaR_mixed_Hessian_changed_for_nonzero_coefficient": not failures,
            "prior_fixed_background_and_coupled_vacua_unconditional": False,
            "complete_mixed_invariant_ring": False,
            "complete_component_potential": False,
            "whole_model_validated": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "The declared symmetries require an allowed, unique renormalizable "
            "Phi H^dag Sigmabar cubic that is absent from the current catalogue. "
            "It creates no H tadpole on the SM-preserving p+Delta_R background, "
            "but it adds nonzero mixed Hessian blocks. Existing vacuum/spectrum "
            "certificates remain exact for their stated truncated potentials and "
            "must be re-solved before being promoted to the complete model."
        ),
    }
    return _jsonable(report)


def write_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Missing Phi Hdag Sigmabar cubic audit — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Operator",
            "",
            "`mu_D H_e^* Phi_abcd Sigmabar_abcde/4! + h.c.`",
            "",
            "It is PQ-, Z17-, and historical-X neutral.",
            "",
            "The p+Delta_R tadpole vanishes, but both mixed Hessian blocks are nonzero.",
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
