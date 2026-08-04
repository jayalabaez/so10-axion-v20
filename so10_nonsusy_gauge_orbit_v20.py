#!/usr/bin/env python3
"""Exact SO(10) gauge-orbit and Goldstone certificate for the v20 VEVs.

Representations are constructed directly as differential forms on R^10:

* 210_H is a real four-form. The Pati-Salam singlet VEV is the oriented
  volume form on the last four coordinates.
* 126bar_H is a complex Hodge-eigenstate five-form. The Delta_R direction is
  Omega_(3,0) on R^6 times a self-dual two-form on R^4.

The generator action is implemented as e_a wedge i_b - e_b wedge i_a. No
Aulakh/MSGUT mass matrices or Clebsch tables enter. The resulting gauge orbit
has rank 33 and the common stabilizer has dimension 12, with the split
8 (SU(3)-sized) + 4 (SU(2)xU(1)-sized).
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
N = 10
Form = dict[tuple[int, ...], complex]


def permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def one_form(index: int, coefficient: complex = 1.0) -> Form:
    if not 0 <= index < N:
        raise ValueError("one-form index out of range")
    return {(index,): complex(coefficient)}


def add_forms(*forms: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for form in forms:
        for indices, coefficient in form.items():
            output[indices] += coefficient
    return {indices: value for indices, value in output.items() if abs(value) > 1e-14}


def scale_form(form: Form, coefficient: complex) -> Form:
    return {indices: coefficient * value for indices, value in form.items()}


def wedge(left: Form, right: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for left_indices, left_value in left.items():
        for right_indices, right_value in right.items():
            if set(left_indices).intersection(right_indices):
                continue
            sequence = left_indices + right_indices
            sorted_indices = tuple(sorted(sequence))
            output[sorted_indices] += (
                left_value * right_value * permutation_sign(sequence)
            )
    return {indices: value for indices, value in output.items() if abs(value) > 1e-14}


def interior(form: Form, index: int) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for indices, coefficient in form.items():
        if index not in indices:
            continue
        position = indices.index(index)
        reduced = indices[:position] + indices[position + 1 :]
        output[reduced] += ((-1) ** position) * coefficient
    return dict(output)


def generator_action(form: Form, a: int, b: int) -> Form:
    if not 0 <= a < b < N:
        raise ValueError("generator requires 0 <= a < b < 10")
    return add_forms(
        wedge(one_form(a), interior(form, b)),
        scale_form(wedge(one_form(b), interior(form, a)), -1.0),
    )


def hodge_star(form: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    all_indices = set(range(N))
    for indices, coefficient in form.items():
        complement = tuple(sorted(all_indices.difference(indices)))
        output[complement] += coefficient * permutation_sign(indices + complement)
    return dict(output)


def inner(left: Form, right: Form) -> complex:
    return sum(
        np.conjugate(left.get(indices, 0.0)) * right.get(indices, 0.0)
        for indices in set(left).union(right)
    )


def norm(form: Form) -> float:
    return float(np.sqrt(max(float(np.real(inner(form, form))), 0.0)))


def form_difference_norm(left: Form, right: Form) -> float:
    return norm(add_forms(left, scale_form(right, -1.0)))


def build_vevs() -> dict[str, Form]:
    phi_210 = wedge(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    z1 = add_forms(one_form(0), scale_form(one_form(1), 1j))
    z2 = add_forms(one_form(2), scale_form(one_form(3), 1j))
    z3 = add_forms(one_form(4), scale_form(one_form(5), 1j))
    omega_3 = wedge(wedge(z1, z2), z3)
    j_right = add_forms(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    delta_126bar = wedge(omega_3, j_right)
    return {
        "phi_210_ps": phi_210,
        "omega3_su3": omega_3,
        "j_right": j_right,
        "delta_126bar": delta_126bar,
    }


def flatten_real(form: Form, degree: int, *, split_complex: bool) -> np.ndarray:
    basis = list(itertools.combinations(range(N), degree))
    values = np.array([form.get(indices, 0.0) for indices in basis], dtype=complex)
    if split_complex:
        return np.concatenate([values.real, values.imag])
    if np.max(np.abs(values.imag), initial=0.0) > 1e-12:
        raise ValueError("real representation received complex form")
    return values.real


def generators() -> list[tuple[int, int]]:
    return list(itertools.combinations(range(N), 2))


def tangent_matrix(
    forms: list[tuple[Form, int, bool]],
    selected_generators: list[tuple[int, int]] | None = None,
) -> np.ndarray:
    selected = generators() if selected_generators is None else selected_generators
    columns = []
    for a, b in selected:
        pieces = [
            flatten_real(generator_action(form, a, b), degree, split_complex=split)
            for form, degree, split in forms
        ]
        columns.append(np.concatenate(pieces))
    return np.stack(columns, axis=1)


def svd_rank(matrix: np.ndarray, relative_tolerance: float = 1e-11) -> int:
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    if singular_values.size == 0 or singular_values[0] == 0.0:
        return 0
    return int(np.sum(singular_values > relative_tolerance * singular_values[0]))


def build_report() -> dict[str, Any]:
    vevs = build_vevs()
    phi = vevs["phi_210_ps"]
    delta = vevs["delta_126bar"]

    star_delta = hodge_star(delta)
    hodge_residual = form_difference_norm(star_delta, scale_form(delta, -1j)) / norm(delta)
    star_squared = hodge_star(star_delta)
    star_squared_residual = form_difference_norm(star_squared, scale_form(delta, -1.0)) / norm(delta)

    all_generators = generators()
    so6 = [(a, b) for a, b in all_generators if b < 6]
    so4 = [(a, b) for a, b in all_generators if a >= 6]
    cross = [(a, b) for a, b in all_generators if a < 6 <= b]
    block = so6 + so4

    phi_matrix = tangent_matrix([(phi, 4, False)])
    combined_matrix = tangent_matrix([(phi, 4, False), (delta, 5, True)])
    delta_block_matrix = tangent_matrix([(delta, 5, True)], block)
    delta_so6_matrix = tangent_matrix([(delta, 5, True)], so6)
    delta_so4_matrix = tangent_matrix([(delta, 5, True)], so4)
    phi_cross_matrix = tangent_matrix([(phi, 4, False)], cross)

    phi_orbit_rank = svd_rank(phi_matrix)
    combined_orbit_rank = svd_rank(combined_matrix)
    delta_breaking_inside_ps = svd_rank(delta_block_matrix)
    delta_so6_rank = svd_rank(delta_so6_matrix)
    delta_so4_rank = svd_rank(delta_so4_matrix)
    cross_rank = svd_rank(phi_cross_matrix)

    stabilizer = 45 - combined_orbit_rank
    so6_stabilizer = 15 - delta_so6_rank
    so4_stabilizer = 6 - delta_so4_rank

    checks = {
        "delta_is_minus_i_hodge_eigenstate": hodge_residual < 1e-12,
        "hodge_star_squared_minus_one_on_five_forms": star_squared_residual < 1e-12,
        "phi_breaks_so10_to_pati_salam": phi_orbit_rank == 24,
        "cross_generator_rank_is_24": cross_rank == 24,
        "delta_adds_nine_broken_generators_inside_ps": delta_breaking_inside_ps == 9,
        "combined_goldstone_count_is_33": combined_orbit_rank == 33,
        "combined_stabilizer_dimension_is_12": stabilizer == 12,
        "so6_stabilizer_is_su3_sized": so6_stabilizer == 8,
        "so4_stabilizer_is_su2_u1_sized": so4_stabilizer == 4,
        "broken_plus_unbroken_exhausts_so10": combined_orbit_rank + stabilizer == 45,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_SO10_GAUGE_ORBIT_33_GOLDSTONES__SM_STABILIZER"
            if not failures
            else "SO10_GAUGE_ORBIT_CERTIFICATE_FAILED"
        ),
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "representation": {
            "210_H": "real antisymmetric four-form on R10",
            "126bar_H": "complex five-form with Hodge eigenvalue -i",
            "generator_action": "e_a wedge i_b - e_b wedge i_a",
            "uses_msgut_component_matrices": False,
        },
        "vev_embedding": {
            "phi_210_ps": "e6 wedge e7 wedge e8 wedge e9",
            "delta_126bar": "(e0+i e1)(e2+i e3)(e4+i e5) wedge (e6e7+e8e9)",
            "hodge_eigenvalue": "-i",
            "hodge_relative_residual": hodge_residual,
            "hodge_squared_relative_residual": star_squared_residual,
        },
        "orbit": {
            "phi_210_orbit_rank": phi_orbit_rank,
            "phi_210_stabilizer_dimension": 45 - phi_orbit_rank,
            "cross_so6_so4_rank": cross_rank,
            "delta_breaking_inside_pati_salam": delta_breaking_inside_ps,
            "combined_orbit_rank_goldstones": combined_orbit_rank,
            "combined_stabilizer_dimension": stabilizer,
            "so6_delta_rank": delta_so6_rank,
            "so6_stabilizer_dimension": so6_stabilizer,
            "so4_delta_rank": delta_so4_rank,
            "so4_stabilizer_dimension": so4_stabilizer,
        },
        "flag": {
            "explicit_210_four_form_embedding": True,
            "explicit_126bar_hodge_five_form_embedding": True,
            "goldstone_count_33_exact": combined_orbit_rank == 33,
            "sm_sized_stabilizer_dimension_12": stabilizer == 12,
            "su3_sized_so6_stabilizer_8": so6_stabilizer == 8,
            "su2_u1_sized_so4_stabilizer_4": so4_stabilizer == 4,
            "independent_of_susy_mass_matrices": True,
            "full_component_hessian_derived": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            f"Direct differential-form representation gives orbit rank {combined_orbit_rank} and stabilizer dimension {stabilizer}. "
            f"The Pati-Salam step contributes {cross_rank} broken generators and Delta_R contributes {delta_breaking_inside_ps}, totaling 33 Goldstones. "
            "This closes the exact gauge-orbit/Goldstone-count problem, not the dynamical full-component Hessian."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    orbit = report["orbit"]
    return "\n".join(
        [
            "# Exact SO(10) gauge-orbit certificate — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            f"- Goldstone/gauge-orbit rank: {orbit['combined_orbit_rank_goldstones']}",
            f"- Stabilizer dimension: {orbit['combined_stabilizer_dimension']}",
            f"- SO(6) stabilizer dimension: {orbit['so6_stabilizer_dimension']}",
            f"- SO(4) stabilizer dimension: {orbit['so4_stabilizer_dimension']}",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    ROOT.joinpath("SO10_NONSUSY_GAUGE_ORBIT_V20_VERDICT.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    ROOT.joinpath("SO10_NONSUSY_GAUGE_ORBIT_V20.md").write_text(
        write_markdown(report), encoding="utf-8"
    )
    print(json.dumps(report, indent=2))
    return 0 if report.get("n_failed", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
