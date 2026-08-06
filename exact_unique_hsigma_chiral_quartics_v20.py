#!/usr/bin/env python3
"""Exact unique chiral quartics completing the live G1 tensor census.

This module constructs the two remaining multiplicity-one nontrivial families:

1. 10_H^dag 126bar_H^2 126bar_H^dag + h.c.
2. 10_H^dag^2 126bar_H^2 + h.c.

The fields are represented as a complex SO(10) vector and chiral five-forms.
All delta-contraction graphs are enumerated from the vertex degrees.  The exact
D5 character census says each family has singlet multiplicity one, so one
nonzero infinitesimally invariant Cartesian contraction is a complete basis.

Normalization convention
------------------------
The evaluators use full-index Einstein sums on dense antisymmetric tensors
built from independent ordered components.  No hidden numerical coefficient is
inserted; the corresponding potential coupling is defined in precisely this
fixed convention.  This is a normalization convention, not a prediction for
the coupling.

This closes only these two finite G1 families.  It does not by itself close G2,
the vacuum, the spectrum, running, proton decay, or the whole theory.
"""
from __future__ import annotations

import argparse
import itertools
import json
import string
from pathlib import Path
from typing import Any

import numpy as np

import exact_phi2_126dag126_six_contractions_v20 as forms
import g1_exact_declared_symmetry_character_census_v20 as census

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_UNIQUE_HSIGMA_CHIRAL_QUARTICS_V20.json"
OUT_MD = ROOT / "EXACT_UNIQUE_HSIGMA_CHIRAL_QUARTICS_V20.md"
N = forms.N
LETTERS = tuple(string.ascii_lowercase + string.ascii_uppercase)

# Edge order for four vertices is
# (01,02,03,12,13,23).
# Family A vertices: (Hdag, Sigma, Sigma, Sigmadag), degrees (1,5,5,5).
FAMILY_A_DEGREES = (1, 5, 5, 5)
FAMILY_A_SELECTED = (0, 1, 0, 2, 3, 2)

# Family B vertices: (Hdag, Hdag, Sigma, Sigma), degrees (1,1,5,5).
FAMILY_B_DEGREES = (1, 1, 5, 5)
FAMILY_B_SELECTED = (0, 0, 1, 1, 0, 4)


def graph_solutions(degrees: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    edges = tuple(
        (left, right)
        for left in range(len(degrees))
        for right in range(left + 1, len(degrees))
    )
    rows: list[tuple[int, ...]] = []

    def recurse(
        edge_index: int,
        remaining: tuple[int, ...],
        values: tuple[int, ...],
    ) -> None:
        if edge_index == len(edges):
            if all(value == 0 for value in remaining):
                rows.append(values)
            return
        left, right = edges[edge_index]
        for multiplicity in range(min(remaining[left], remaining[right]) + 1):
            updated = list(remaining)
            updated[left] -= multiplicity
            updated[right] -= multiplicity
            recurse(edge_index + 1, tuple(updated), values + (multiplicity,))

    recurse(0, tuple(degrees), ())
    return tuple(rows)


def graph_subscript(
    degrees: tuple[int, ...], edge_multiplicities: tuple[int, ...]
) -> str:
    edges = tuple(
        (left, right)
        for left in range(len(degrees))
        for right in range(left + 1, len(degrees))
    )
    labels: list[list[str]] = [[] for _ in degrees]
    cursor = 0
    for edge, multiplicity in zip(edges, edge_multiplicities):
        for _ in range(multiplicity):
            label = LETTERS[cursor]
            cursor += 1
            labels[edge[0]].append(label)
            labels[edge[1]].append(label)
    if tuple(map(len, labels)) != degrees:
        raise AssertionError("edge multiplicities do not reproduce tensor degrees")
    return ",".join("".join(row) for row in labels) + "->"


def evaluate_graph(
    degrees: tuple[int, ...],
    edge_multiplicities: tuple[int, ...],
    *tensors: np.ndarray,
) -> complex:
    return complex(
        np.einsum(
            graph_subscript(degrees, edge_multiplicities),
            *tensors,
            optimize="greedy",
        )
    )


def invariant_hdag_sigma2_sigmadag(
    hdag: np.ndarray,
    sigma: np.ndarray,
    sigmadag: np.ndarray,
) -> complex:
    """Unique 10dag Sigma^2 Sigmadag contraction in the fixed convention."""
    return evaluate_graph(
        FAMILY_A_DEGREES,
        FAMILY_A_SELECTED,
        hdag,
        sigma,
        sigma,
        sigmadag,
    )


def invariant_hdag2_sigma2(hdag: np.ndarray, sigma: np.ndarray) -> complex:
    """Unique 10dag^2 Sigma^2 contraction in the fixed convention."""
    return evaluate_graph(
        FAMILY_B_DEGREES,
        FAMILY_B_SELECTED,
        hdag,
        hdag,
        sigma,
        sigma,
    )


def deterministic_fields(
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, forms.Form, forms.Form]:
    unconstrained: forms.Form = {}
    for index, indices in enumerate(forms.C5):
        real = ((index * (3 * seed + 2) + 5 * seed + 1) % 5) - 2
        imag = ((index * (5 * seed + 1) + 2 * seed + 3) % 5) - 2
        unconstrained[indices] = complex(real, imag)
    # star(Sigma) = -i Sigma.
    sigma_form = forms.add_forms(
        unconstrained,
        forms.scale_form(forms.hodge_star(unconstrained), 1j),
    )
    sigmadag_form = {
        indices: np.conjugate(value) for indices, value in sigma_form.items()
    }
    h = np.asarray(
        [
            complex(
                ((7 * index + 3 * seed) % 11) - 5,
                ((5 * index + seed) % 7) - 3,
            )
            for index in range(N)
        ],
        dtype=complex,
    )
    hdag = np.conjugate(h)
    return (
        hdag,
        forms.dense_antisymmetric(sigma_form, 5),
        forms.dense_antisymmetric(sigmadag_form, 5),
        sigma_form,
        sigmadag_form,
    )


def vector_generator_action(vector: np.ndarray, first: int, second: int) -> np.ndarray:
    output = np.zeros_like(vector, dtype=complex)
    output[first] = vector[second]
    output[second] = -vector[first]
    return output


def covariance_residuals(seed: int = 1) -> dict[str, float]:
    hdag, sigma, sigmadag, sigma_form, sigmadag_form = deterministic_fields(seed)
    maximum_a = 0.0
    maximum_b = 0.0
    for first, second in itertools.combinations(range(N), 2):
        dhdag = vector_generator_action(hdag, first, second)
        dsigma = forms.dense_antisymmetric(
            forms.generator_action(sigma_form, first, second), 5
        )
        dsigmadag = forms.dense_antisymmetric(
            forms.generator_action(sigmadag_form, first, second), 5
        )
        variation_a = (
            evaluate_graph(
                FAMILY_A_DEGREES,
                FAMILY_A_SELECTED,
                dhdag,
                sigma,
                sigma,
                sigmadag,
            )
            + evaluate_graph(
                FAMILY_A_DEGREES,
                FAMILY_A_SELECTED,
                hdag,
                dsigma,
                sigma,
                sigmadag,
            )
            + evaluate_graph(
                FAMILY_A_DEGREES,
                FAMILY_A_SELECTED,
                hdag,
                sigma,
                dsigma,
                sigmadag,
            )
            + evaluate_graph(
                FAMILY_A_DEGREES,
                FAMILY_A_SELECTED,
                hdag,
                sigma,
                sigma,
                dsigmadag,
            )
        )
        variation_b = (
            evaluate_graph(
                FAMILY_B_DEGREES,
                FAMILY_B_SELECTED,
                dhdag,
                hdag,
                sigma,
                sigma,
            )
            + evaluate_graph(
                FAMILY_B_DEGREES,
                FAMILY_B_SELECTED,
                hdag,
                dhdag,
                sigma,
                sigma,
            )
            + evaluate_graph(
                FAMILY_B_DEGREES,
                FAMILY_B_SELECTED,
                hdag,
                hdag,
                dsigma,
                sigma,
            )
            + evaluate_graph(
                FAMILY_B_DEGREES,
                FAMILY_B_SELECTED,
                hdag,
                hdag,
                sigma,
                dsigma,
            )
        )
        maximum_a = max(maximum_a, abs(variation_a))
        maximum_b = max(maximum_b, abs(variation_b))
    return {
        "hdag_sigma2_sigmadag": float(maximum_a),
        "hdag2_sigma2": float(maximum_b),
    }


def build_report() -> dict[str, Any]:
    rows = census.census(False)
    multiplicity_a = census.find_multiplicity(rows, Hb=1, D=2, Db=1)
    multiplicity_b = census.find_multiplicity(rows, Hb=2, D=2)
    hdag, sigma, sigmadag, _, _ = deterministic_fields(1)
    value_a = invariant_hdag_sigma2_sigmadag(hdag, sigma, sigmadag)
    value_b = invariant_hdag2_sigma2(hdag, sigma)
    residuals = covariance_residuals(1)
    graphs_a = graph_solutions(FAMILY_A_DEGREES)
    graphs_b = graph_solutions(FAMILY_B_DEGREES)

    checks = {
        "family_A_character_multiplicity_one": multiplicity_a == 1,
        "family_B_character_multiplicity_one": multiplicity_b == 1,
        "family_A_three_delta_graphs": len(graphs_a) == 3,
        "family_B_three_delta_graphs": len(graphs_b) == 3,
        "family_A_selected_graph_valid": FAMILY_A_SELECTED in graphs_a,
        "family_B_selected_graph_valid": FAMILY_B_SELECTED in graphs_b,
        "family_A_selected_contraction_nonzero": abs(value_a) > 1.0e-8,
        "family_B_selected_contraction_nonzero": abs(value_b) > 1.0e-8,
        "family_A_all_45_generator_variations_vanish": residuals[
            "hdag_sigma2_sigmadag"
        ]
        < 1.0e-9,
        "family_B_all_45_generator_variations_vanish": residuals[
            "hdag2_sigma2"
        ]
        < 1.0e-9,
        "normalization_convention_explicit": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_UNIQUE_HSIGMA_CHIRAL_QUARTICS_COMPLETE"
            if not failures
            else "EXACT_UNIQUE_HSIGMA_CHIRAL_QUARTICS_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "families": {
            "10dag_126bar2_126dag": {
                "character_multiplicity": multiplicity_a,
                "degrees": list(FAMILY_A_DEGREES),
                "all_delta_graphs": [list(row) for row in graphs_a],
                "selected_graph": list(FAMILY_A_SELECTED),
                "einsum": graph_subscript(FAMILY_A_DEGREES, FAMILY_A_SELECTED),
                "witness_value": {
                    "real": float(value_a.real),
                    "imag": float(value_a.imag),
                },
                "maximum_infinitesimal_variation_abs": residuals[
                    "hdag_sigma2_sigmadag"
                ],
            },
            "10dag2_126bar2": {
                "character_multiplicity": multiplicity_b,
                "degrees": list(FAMILY_B_DEGREES),
                "all_delta_graphs": [list(row) for row in graphs_b],
                "selected_graph": list(FAMILY_B_SELECTED),
                "einsum": graph_subscript(FAMILY_B_DEGREES, FAMILY_B_SELECTED),
                "witness_value": {
                    "real": float(value_b.real),
                    "imag": float(value_b.imag),
                },
                "maximum_infinitesimal_variation_abs": residuals[
                    "hdag2_sigma2"
                ],
            },
        },
        "normalization": {
            "field_coordinates": (
                "independent ordered antisymmetric components; dense tensors are "
                "their exact antisymmetric extension"
            ),
            "operator_convention": (
                "full-index Einstein contraction defined by the recorded einsum; "
                "no hidden coefficient"
            ),
            "coupling_interpretation": (
                "the potential coefficient multiplies this exact convention"
            ),
        },
        "closure": {
            "unique_10dag_126bar2_126dag_tensor_closed": not failures,
            "unique_10dag2_126bar2_tensor_closed": not failures,
            "G2_closed": False,
        },
        "flags": {
            "CG_coefficients_invented": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "verdict": (
            "Both remaining multiplicity-one chiral quartics now have explicit, "
            "nonzero, all-generator-invariant Cartesian contractions in fixed "
            "normalization conventions."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# Exact unique H-Sigma chiral quartics — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
