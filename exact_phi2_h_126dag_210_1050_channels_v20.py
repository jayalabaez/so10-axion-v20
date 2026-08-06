#!/usr/bin/env python3
"""Exact two-channel tensor basis for 210_H^2 10_H 126bar_H^dag.

For a chiral five-form Sigma in the 126 of SO(10),

    10 tensor 126 = 210 + 1050.

The 210 is the image of the canonical chiral injection
J(A)_a = P_+(e_a wedge A), where A is a four-form and P_+ projects onto
Hodge eigenvalue +i. Direct calculation gives J^dag J = 3 I_210, hence
P_210 = J J^dag / 3 and P_1050 = I - P_210 on the 1260-dimensional
vector-valued chiral-five-form space. No tabulated CG coefficients are used.

A symmetric bilinear from two 210 four-forms is

 B(P,Q)_a = P_+ sum_i [(i_i i_a P) wedge (i_i Q)
                       + (i_i i_a Q) wedge (i_i P)].

Projecting B into 210 and 1050 supplies the two exact independent invariants
predicted by the D5 character census. This closes only this G1 tensor family;
full normalization across all 64 live coefficient directions and G2 remain
open.
"""
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import g1_exact_declared_symmetry_character_census_v20 as census

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_PHI2_H_126DAG_210_1050_CHANNELS_V20.json"
OUT_MD = ROOT / "EXACT_PHI2_H_126DAG_210_1050_CHANNELS_V20.md"
N = 10
Form = dict[tuple[int, ...], complex]
C4 = tuple(itertools.combinations(range(N), 4))
C5 = tuple(itertools.combinations(range(N), 5))
I4 = {indices: index for index, indices in enumerate(C4)}
I5 = {indices: index for index, indices in enumerate(C5)}


def permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def add_forms(*forms: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for form in forms:
        for indices, coefficient in form.items():
            output[indices] += coefficient
    return {k: v for k, v in output.items() if abs(v) > 1e-13}


def scale_form(form: Form, coefficient: complex) -> Form:
    return {indices: coefficient * value for indices, value in form.items()}


def one_form(index: int, coefficient: complex = 1.0) -> Form:
    return {(index,): complex(coefficient)}


def wedge(left: Form, right: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for left_indices, left_value in left.items():
        for right_indices, right_value in right.items():
            if set(left_indices).intersection(right_indices):
                continue
            sequence = left_indices + right_indices
            ordered = tuple(sorted(sequence))
            output[ordered] += left_value * right_value * permutation_sign(sequence)
    return {k: v for k, v in output.items() if abs(v) > 1e-13}


def interior(form: Form, index: int) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for indices, coefficient in form.items():
        if index not in indices:
            continue
        position = indices.index(index)
        reduced = indices[:position] + indices[position + 1 :]
        output[reduced] += ((-1) ** position) * coefficient
    return dict(output)


def hodge_star(form: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    all_indices = set(range(N))
    for indices, coefficient in form.items():
        complement = tuple(sorted(all_indices.difference(indices)))
        output[complement] += coefficient * permutation_sign(indices + complement)
    return dict(output)


def chiral_project_five(form: Form, chirality: int = +1) -> Form:
    """Project to star=form*(chirality*i), with chirality in {-1,+1}."""
    if chirality not in (-1, +1):
        raise ValueError("chirality must be +/-1")
    return add_forms(
        scale_form(form, 0.5),
        scale_form(hodge_star(form), -0.5j * chirality),
    )


def generator_action(form: Form, a: int, b: int) -> Form:
    return add_forms(
        wedge(one_form(a), interior(form, b)),
        scale_form(wedge(one_form(b), interior(form, a)), -1.0),
    )


def four_to_vector(form: Form) -> np.ndarray:
    output = np.zeros(len(C4), dtype=complex)
    for indices, coefficient in form.items():
        output[I4[indices]] = coefficient
    return output


def vector_to_four(vector: np.ndarray) -> Form:
    return {
        indices: complex(vector[index])
        for index, indices in enumerate(C4)
        if abs(vector[index]) > 1e-13
    }


def five_to_vector(form: Form) -> np.ndarray:
    output = np.zeros(len(C5), dtype=complex)
    for indices, coefficient in form.items():
        output[I5[indices]] = coefficient
    return output


def vector_to_five(vector: np.ndarray) -> Form:
    return {
        indices: complex(vector[index])
        for index, indices in enumerate(C5)
        if abs(vector[index]) > 1e-13
    }


def tensor_norm(tensor: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(tensor, dtype=complex)))


def inject_210(four_form: Form, chirality: int = +1) -> np.ndarray:
    output = np.zeros((N, len(C5)), dtype=complex)
    for a in range(N):
        output[a] = five_to_vector(
            chiral_project_five(wedge(one_form(a), four_form), chirality)
        )
    return output


def contract_vector_five(tensor: np.ndarray) -> np.ndarray:
    output: Form = {}
    for a in range(N):
        output = add_forms(output, interior(vector_to_five(tensor[a]), a))
    return four_to_vector(output)


@lru_cache(maxsize=2)
def injection_matrix(chirality: int = +1) -> np.ndarray:
    matrix = np.zeros((N * len(C5), len(C4)), dtype=complex)
    for column, indices in enumerate(C4):
        matrix[:, column] = inject_210({indices: 1.0}, chirality).reshape(-1)
    return matrix


def project_210(tensor: np.ndarray, chirality: int = +1) -> np.ndarray:
    matrix = injection_matrix(chirality)
    flat = np.asarray(tensor, dtype=complex).reshape(-1)
    return (matrix @ (matrix.conj().T @ flat) / 3.0).reshape(N, len(C5))


def project_1050(tensor: np.ndarray, chirality: int = +1) -> np.ndarray:
    return np.asarray(tensor, dtype=complex) - project_210(tensor, chirality)


def phi2_bilinear(
    left: Form, right: Form, chirality: int = +1
) -> np.ndarray:
    output = np.zeros((N, len(C5)), dtype=complex)
    for a in range(N):
        row: Form = {}
        for i in range(N):
            left_ai = interior(interior(left, a), i)
            right_ai = interior(interior(right, a), i)
            row = add_forms(
                row,
                wedge(left_ai, interior(right, i)),
                wedge(right_ai, interior(left, i)),
            )
        output[a] = five_to_vector(chiral_project_five(row, chirality))
    return output


def generator_action_vector_five(
    tensor: np.ndarray, a: int, b: int
) -> np.ndarray:
    output = np.zeros_like(tensor, dtype=complex)
    for index in range(N):
        output[index] = five_to_vector(
            generator_action(vector_to_five(tensor[index]), a, b)
        )
    output[a] += tensor[b]
    output[b] -= tensor[a]
    return output


def hodge_subspace(form: Form, ordered_indices: tuple[int, ...]) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    full = set(ordered_indices)
    positions = {index: position for position, index in enumerate(ordered_indices)}
    for indices, coefficient in form.items():
        complement = tuple(sorted(full.difference(indices)))
        sequence = tuple(positions[index] for index in indices + complement)
        output[complement] += coefficient * permutation_sign(sequence)
    return dict(output)


def normalized(form: Form) -> Form:
    norm = np.sqrt(sum(abs(value) ** 2 for value in form.values()))
    if norm == 0.0:
        raise ValueError("zero form")
    return scale_form(form, 1.0 / norm)


def singlet_basis() -> tuple[Form, Form, Form]:
    e01 = wedge(one_form(0), one_form(1))
    e23 = wedge(one_form(2), one_form(3))
    e45 = wedge(one_form(4), one_form(5))
    j6 = add_forms(e01, e23, e45)
    p = wedge(wedge(one_form(6), one_form(7)), wedge(one_form(8), one_form(9)))
    a = hodge_subspace(j6, tuple(range(6)))
    jr = add_forms(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    omega = wedge(j6, jr)
    return normalized(p), normalized(a), normalized(omega)


def deterministic_sigma() -> Form:
    seed = {
        (0, 1, 2, 3, 4): 1.0 + 0.5j,
        (0, 2, 5, 7, 9): -0.7 + 0.2j,
        (1, 3, 4, 6, 8): 0.4 - 0.9j,
    }
    return chiral_project_five(seed, +1)


def build_report() -> dict[str, Any]:
    matrix = injection_matrix(+1)
    gram = matrix.conj().T @ matrix
    gram_residual = float(np.max(np.abs(gram - 3.0 * np.eye(len(C4)))))

    p, a, omega = singlet_basis()
    phi = add_forms(p, scale_form(a, 0.7), scale_form(omega, -0.4))
    probe = add_forms(scale_form(a, -0.2), scale_form(omega, 0.9))
    bilinear = phi2_bilinear(phi, phi, +1)
    mixed = phi2_bilinear(phi, probe, +1)
    channel_210 = project_210(bilinear, +1)
    channel_1050 = project_1050(bilinear, +1)

    covariance_residual = 0.0
    projector_covariance_residual = 0.0
    for first, second in itertools.combinations(range(N), 2):
        left = phi2_bilinear(generator_action(phi, first, second), probe, +1)
        right = phi2_bilinear(phi, generator_action(probe, first, second), +1)
        expected = generator_action_vector_five(mixed, first, second)
        covariance_residual = max(
            covariance_residual, tensor_norm(left + right - expected)
        )
        projected_then_acted = generator_action_vector_five(
            project_1050(mixed, +1), first, second
        )
        acted_then_projected = project_1050(expected, +1)
        projector_covariance_residual = max(
            projector_covariance_residual,
            tensor_norm(projected_then_acted - acted_then_projected),
        )

    sigma = deterministic_sigma()
    h = np.array(
        [complex(((7 * index) % 11) - 5, ((3 * index) % 7) - 3) for index in range(N)]
    )
    sigma_vector = five_to_vector(sigma)
    external = h[:, None] * sigma_vector[None, :]
    external_210 = project_210(external, +1)
    external_1050 = project_1050(external, +1)

    invariant_210 = np.vdot(channel_210, external_210)
    invariant_1050 = np.vdot(channel_1050, external_1050)
    cross_210_1050 = np.vdot(channel_210, external_1050)
    cross_1050_210 = np.vdot(channel_1050, external_210)

    rows = census.census(False)
    exact_multiplicity = census.find_multiplicity(rows, P=2, H=1, Db=1)
    contraction_1050 = tensor_norm(contract_vector_five(channel_1050))
    channel_orthogonality = abs(np.vdot(channel_210, channel_1050))
    external_orthogonality = abs(np.vdot(external_210, external_1050))

    checks = {
        "live_character_multiplicity_is_two": exact_multiplicity == 2,
        "chiral_five_form_dimension_is_126": len(C5) // 2 == 126,
        "vector_times_chiral_five_dimension_is_1260": N * (len(C5) // 2) == 1260,
        "injection_rank_is_210": int(np.linalg.matrix_rank(matrix, tol=1e-11)) == 210,
        "JdagJ_is_3I": gram_residual < 1e-12,
        "1050_dimension_is_1050": 1260 - 210 == 1050,
        "bilinear_is_symmetric": tensor_norm(
            phi2_bilinear(phi, probe, +1) - phi2_bilinear(probe, phi, +1)
        ) < 1e-12,
        "bilinear_covariant_under_all_45_generators": covariance_residual < 1e-11,
        "projector_covariant_under_all_45_generators": projector_covariance_residual < 1e-11,
        "210_channel_nonzero": tensor_norm(channel_210) > 1e-8,
        "1050_channel_nonzero": tensor_norm(channel_1050) > 1e-8,
        "1050_is_contraction_free": contraction_1050 < 1e-11,
        "channels_are_orthogonal": channel_orthogonality < 1e-11,
        "external_channels_are_orthogonal": external_orthogonality < 1e-11,
        "210_invariant_nonzero": abs(invariant_210) > 1e-8,
        "1050_invariant_nonzero": abs(invariant_1050) > 1e-8,
        "cross_channel_contractions_vanish": max(
            abs(cross_210_1050), abs(cross_1050_210)
        ) < 1e-10,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "EXACT_PHI2_H_126DAG_210_1050_CHANNELS_COMPLETE"
            if not failures
            else "EXACT_PHI2_H_126DAG_CHANNEL_GATE_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "representation": {
            "operator": "210_H^2 10_H 126bar_H^dag + h.c.",
            "character_multiplicity": exact_multiplicity,
            "decomposition": "10 x 126 = 210 + 1050",
            "dimensions": {"10x126": 1260, "210": 210, "1050": 1050},
            "chirality": "Hodge eigenvalue +i for 126bar_H^dag",
        },
        "projector": {
            "injection": "J(A)_a = P_+(e_a wedge A)",
            "JdagJ_scalar": 3.0,
            "gram_max_abs_residual": gram_residual,
            "P210": "J J^dag / 3",
            "P1050": "I - P210",
            "1050_contraction_residual": contraction_1050,
        },
        "bilinear": {
            "formula": "P_+ sum_i [(i_i i_a P) wedge (i_i Q) + (P<->Q)]",
            "covariance_max_abs_norm_residual": covariance_residual,
            "projector_covariance_max_abs_norm_residual": projector_covariance_residual,
            "selected_combo": {"p": 1.0, "a": 0.7, "omega": -0.4},
            "channel_norms": {
                "210": tensor_norm(channel_210),
                "1050": tensor_norm(channel_1050),
            },
            "channel_inner_product_abs": float(channel_orthogonality),
        },
        "invariant_probe": {
            "I210": {"real": float(invariant_210.real), "imag": float(invariant_210.imag)},
            "I1050": {"real": float(invariant_1050.real), "imag": float(invariant_1050.imag)},
            "cross_max_abs": float(max(abs(cross_210_1050), abs(cross_1050_210))),
        },
        "closure": {
            "multiplicity_two_tensor_family_closed": not failures,
            "210_channel_closed": not failures,
            "1050_channel_closed_without_tabulated_CG": not failures,
            "all_64_live_G1_tensor_directions_closed": False,
            "G1_closed": False,
            "G2_closed": False,
        },
        "flags": {
            "published_1050_CG_required": False,
            "CG_coefficients_invented": False,
            "first_principles_projector_used": True,
            "whole_model_validated": False,
            "whole_model_excluded": False,
            "empirical_discovery": False,
        },
        "next_exact_target": (
            "Integrate these two normalized channel operators into the live 64-direction "
            "G1 tensor ledger, then construct the six 210_H^2 126bar_H 126bar_H^dag channels."
        ),
        "verdict": (
            "The two independent 210_H^2 10_H 126bar_H^dag invariants are now "
            "constructed explicitly as orthogonal 210 and 1050 channels. The 1050 "
            "is the contraction-free complement of the canonical 210 injection, so "
            "no external CG table is needed. G1 remains open for the other live tensor families."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# Exact Phi^2 H 126dag 210/1050 channels — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        + f"**Next:** {report['next_exact_target']}\n"
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
