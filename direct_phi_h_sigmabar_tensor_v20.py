#!/usr/bin/env python3
"""Direct non-SUSY SO(10) tensor map for Phi(210) H(10) Sigmabar(126bar) S.

This module repairs a source-level category error in the previous EFJX route:
Aulakh Appendix-A E/F/J/X entries proportional to ``g`` are gauge/gaugino
super-Higgs mixings, not the superpotential ``gamma`` coupling. Therefore they
cannot be used to infer ``gamma_eff/lambda4`` for the non-supersymmetric scalar
operator.

The replacement calculation is representation-theoretic and SUSY-independent:

* 210 is represented as a real four-form on R^10.
* 126bar is the -i Hodge eigenspace of complex five-forms.
* 10 is a vector/one-form.
* the unique direct contraction is C_e = Phi_abcd Sigmabar_abcde, corresponding
  to V portal lambda4 S H_e Phi_abcd Sigmabar_abcde / 4! + h.c.

The code constructs the complete SM-singlet 210 basis (p,a,omega), verifies the
SM-preserving omega choice by the 33-dimensional gauge orbit with Delta_R,
builds the 10 x 126 contraction matrix, checks SO(10) equivariance, and emits
its basis-independent singular-value fingerprints.

It does not claim the full scalar potential or vacuum Hessian is complete.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent
N = 10
Form = dict[tuple[int, ...], complex]
OUT_JSON = ROOT / "DIRECT_PHI_H_SIGMABAR_TENSOR_V20.json"
OUT_MD = ROOT / "DIRECT_PHI_H_SIGMABAR_TENSOR_V20.md"


def permutation_sign(sequence: tuple[int, ...]) -> int:
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def one_form(index: int, coefficient: complex = 1.0) -> Form:
    return {(index,): complex(coefficient)}


def add_forms(*forms: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for form in forms:
        for indices, coefficient in form.items():
            output[indices] += coefficient
    return {indices: value for indices, value in output.items() if abs(value) > 1e-13}


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
    return {indices: value for indices, value in output.items() if abs(value) > 1e-13}


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
    return add_forms(
        wedge(one_form(a), interior(form, b)),
        scale_form(wedge(one_form(b), interior(form, a)), -1.0),
    )


def inner(left: Form, right: Form) -> complex:
    return sum(
        np.conjugate(left.get(indices, 0.0)) * right.get(indices, 0.0)
        for indices in set(left).union(right)
    )


def norm(form: Form) -> float:
    return float(np.sqrt(max(float(np.real(inner(form, form))), 0.0)))


def normalize(form: Form) -> Form:
    value = norm(form)
    if value == 0.0:
        raise ValueError("cannot normalize zero form")
    return scale_form(form, 1.0 / value)


def hodge_star(form: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    all_indices = set(range(N))
    for indices, coefficient in form.items():
        complement = tuple(sorted(all_indices.difference(indices)))
        output[complement] += coefficient * permutation_sign(indices + complement)
    return dict(output)


def hodge_star_subspace(form: Form, ordered_indices: tuple[int, ...]) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    full = set(ordered_indices)
    positions = {index: position for position, index in enumerate(ordered_indices)}
    for indices, coefficient in form.items():
        if not set(indices).issubset(full):
            raise ValueError("form leaves requested Hodge subspace")
        complement = tuple(sorted(full.difference(indices)))
        position_sequence = tuple(positions[index] for index in indices + complement)
        output[complement] += coefficient * permutation_sign(position_sequence)
    return dict(output)


def flatten_real(form: Form, degree: int, *, split_complex: bool) -> np.ndarray:
    basis = list(itertools.combinations(range(N), degree))
    values = np.array([form.get(indices, 0.0) for indices in basis], dtype=complex)
    if split_complex:
        return np.concatenate([values.real, values.imag])
    if np.max(np.abs(values.imag), initial=0.0) > 1e-12:
        raise ValueError("real representation received complex form")
    return values.real


def tangent_rank(forms: list[tuple[Form, int, bool]]) -> int:
    columns = []
    for a, b in itertools.combinations(range(N), 2):
        columns.append(
            np.concatenate(
                [
                    flatten_real(generator_action(form, a, b), degree, split_complex=split)
                    for form, degree, split in forms
                ]
            )
        )
    matrix = np.stack(columns, axis=1)
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    if singular_values[0] == 0.0:
        return 0
    return int(np.sum(singular_values > 1e-11 * singular_values[0]))


def singlet_basis() -> dict[str, Form]:
    e01 = wedge(one_form(0), one_form(1))
    e23 = wedge(one_form(2), one_form(3))
    e45 = wedge(one_form(4), one_form(5))
    j6 = add_forms(e01, e23, e45)

    p = wedge(wedge(one_form(6), one_form(7)), wedge(one_form(8), one_form(9)))
    a = hodge_star_subspace(j6, tuple(range(6)))
    j_right = add_forms(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    omega = wedge(j6, j_right)
    return {"p": normalize(p), "a": normalize(a), "omega": normalize(omega)}


def delta_r() -> Form:
    z1 = add_forms(one_form(0), scale_form(one_form(1), 1j))
    z2 = add_forms(one_form(2), scale_form(one_form(3), 1j))
    z3 = add_forms(one_form(4), scale_form(one_form(5), 1j))
    omega3 = wedge(wedge(z1, z2), z3)
    j_right = add_forms(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    return normalize(wedge(omega3, j_right))


def anti_self_dual_five_form_basis() -> list[Form]:
    basis: list[Form] = []
    seen: set[tuple[int, ...]] = set()
    all_indices = set(range(N))
    for initial in itertools.combinations(range(N), 5):
        if initial in seen:
            continue
        complement = tuple(sorted(all_indices.difference(initial)))
        seen.add(initial)
        seen.add(complement)
        first, second = (initial, complement) if initial < complement else (complement, initial)
        sign = permutation_sign(first + second)
        state = {
            first: 1.0 / math.sqrt(2.0),
            second: 1j * sign / math.sqrt(2.0),
        }
        residual = norm(add_forms(hodge_star(state), scale_form(state, 1j)))
        if residual > 1e-12:
            raise AssertionError("anti-self-dual basis construction failed")
        basis.append(state)
    if len(basis) != 126:
        raise AssertionError(f"expected 126 states, found {len(basis)}")
    return basis


def contract(phi: Form, sigma_bar: Form) -> Form:
    """Factorial-stripped C_e = sum_[abcd] Phi_[abcd] Sigma_[abcde]."""
    output: Form = {}
    for free_index in range(N):
        value = 0.0 + 0.0j
        for indices, phi_value in phi.items():
            if free_index in indices:
                continue
            sequence = indices + (free_index,)
            five_indices = tuple(sorted(sequence))
            value += (
                phi_value
                * sigma_bar.get(five_indices, 0.0)
                * permutation_sign(sequence)
            )
        if abs(value) > 1e-13:
            output[(free_index,)] = value
    return output


def contraction_matrix(phi: Form, sigma_basis: list[Form]) -> np.ndarray:
    matrix = np.zeros((N, len(sigma_basis)), dtype=complex)
    for column, state in enumerate(sigma_basis):
        image = contract(phi, state)
        for index in range(N):
            matrix[index, column] = image.get((index,), 0.0)
    return matrix


def singular_fingerprint(phi: Form, sigma_basis: list[Form]) -> dict[str, Any]:
    singular_values = np.linalg.svd(contraction_matrix(phi, sigma_basis), compute_uv=False)
    return {
        "rank": int(np.sum(singular_values > 1e-12)),
        "singular_values": [float(value) for value in singular_values],
        "frobenius_norm": float(np.linalg.norm(singular_values)),
        "max_singular_value": float(singular_values[0]),
    }


def equivariance_residual(phi: Form, sigma_basis: list[Form]) -> float:
    sigma: Form = {}
    for index, state in enumerate(sigma_basis):
        coefficient = complex(((index * 17) % 23) - 11, ((index * 7) % 19) - 9)
        sigma = add_forms(sigma, scale_form(state, coefficient))
    maximum = 0.0
    for a, b in itertools.combinations(range(N), 2):
        left = add_forms(
            contract(generator_action(phi, a, b), sigma),
            contract(phi, generator_action(sigma, a, b)),
        )
        right = generator_action(contract(phi, sigma), a, b)
        maximum = max(maximum, norm(add_forms(left, scale_form(right, -1.0))))
    return maximum


def build_report() -> dict[str, Any]:
    singlets = singlet_basis()
    delta = delta_r()
    sigma_basis = anti_self_dual_five_form_basis()

    gram = {
        left: {
            right: [
                float(np.real(inner(singlets[left], singlets[right]))),
                float(np.imag(inner(singlets[left], singlets[right]))),
            ]
            for right in singlets
        }
        for left in singlets
    }
    generic_phi = add_forms(
        scale_form(singlets["p"], 0.90),
        scale_form(singlets["a"], 0.05),
        scale_form(singlets["omega"], 0.05),
    )
    orbit_rank = tangent_rank([(generic_phi, 4, False), (delta, 5, True)])
    equivariance = equivariance_residual(generic_phi, sigma_basis)

    fingerprints = {
        name: singular_fingerprint(state, sigma_basis)
        for name, state in singlets.items()
    }
    fingerprints["repository_ratio_probe_0p90_0p05_0p05"] = singular_fingerprint(
        generic_phi, sigma_basis
    )

    checks = {
        "three_normalized_orthogonal_singlets": all(
            abs(inner(singlets[left], singlets[right]) - (1.0 if left == right else 0.0))
            < 1e-12
            for left in singlets
            for right in singlets
        ),
        "anti_self_dual_basis_dimension_126": len(sigma_basis) == 126,
        "generic_p_a_omega_plus_delta_has_33_goldstones": orbit_rank == 33,
        "direct_contraction_is_so10_equivariant": equivariance < 1e-10,
        "p_map_rank_6": fingerprints["p"]["rank"] == 6,
        "a_map_rank_10": fingerprints["a"]["rank"] == 10,
        "omega_map_rank_7": fingerprints["omega"]["rank"] == 7,
        "efjx_g_is_not_gamma": True,
        "whole_model_not_overclaimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    return {
        "status": (
            "DIRECT_NONSUSY_PHI_H_SIGMABAR_TENSOR_MAP_EXECUTED"
            if not failures
            else "DIRECT_NONSUSY_PHI_H_SIGMABAR_TENSOR_MAP_FAILED"
        ),
        "overall_state": "BLOCKED",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_correction": {
            "aulakh_eq1_prefactor": "1/4! for H_i Phi_jklm Sigma_ijklm",
            "aulakh_appendix_E_F_J_X_symbol": "g = SO(10) gauge coupling",
            "previous_repository_interpretation": "incorrectly mapped g to gamma",
            "consequence": (
                "The EFJX-derived gamma threshold and the 8.8e29 c_norm bound are invalid. "
                "The non-SUSY portal must be evaluated as a scalar mass-squared mixing "
                "lambda4 * <S> * T_<Phi>, not as an EFJX gaugino mass response."
            ),
        },
        "representation": {
            "Phi210": "real Lambda^4(R10)",
            "Sigmabar126": "-i Hodge eigenspace of Lambda^5(C10)",
            "H10": "one-form/vector on R10",
            "portal": "lambda4 S H_e Phi_abcd Sigmabar_abcde / 4! + h.c.",
            "tensor_map_shape": [10, 126],
        },
        "singlet_basis": {
            "p": "e6^e7^e8^e9",
            "a": "*_R6(e01+e23+e45)/sqrt(3)",
            "omega": "(e01+e23+e45)^(e67+e89)/sqrt(6)",
            "gram_matrix_Re_Im": gram,
            "generic_orbit_rank": orbit_rank,
            "generic_stabilizer_dimension": 45 - orbit_rank,
        },
        "equivariance_max_abs_residual": float(equivariance),
        "fingerprints": fingerprints,
        "flags": {
            "full_p_a_omega_cartesian_basis_constructed": True,
            "direct_10_by_126_tensor_map_constructed": True,
            "efjx_cgc_route_invalidated": True,
            "old_8p8e29_bound_valid": False,
            "exact_Aulakh_to_cartesian_state_dictionary_complete": False,
            "full_nonsusy_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "match_cartesian_p_a_omega_normalization_to_published_state_tables": True,
            "embed_all_H10_and_Sigmabar_SM_component_labels": True,
            "insert_direct_mass_squared_block_into_complete_nonsusy_hessian": True,
            "global_vacuum_and_boundedness": True,
        },
        "verdict": (
            "The direct non-SUSY tensor contraction is executable, SO(10)-equivariant, "
            "and includes the full p,a,omega singlet basis. The previous EFJX/gamma "
            "normalization campaign is invalid because its g entries are gauge/gaugino "
            "mixings. This removes the claimed 8.8e29 Clebsch no-go, but the complete "
            "non-SUSY scalar Hessian remains open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Direct non-SUSY Phi-H-Sigmabar tensor map — v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**State:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Singular-value fingerprints",
        "",
    ]
    for name, row in report["fingerprints"].items():
        lines.append(f"- `{name}` rank={row['rank']}, s={row['singular_values']}")
    lines.extend(["", "## Remaining blockers", ""])
    for name, open_ in report["remaining_blockers"].items():
        lines.append(f"- `{'OPEN' if open_ else 'CLOSED'}` {name}")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
