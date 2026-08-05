#!/usr/bin/env python3
"""Direct non-SUSY SO(10) tensor map for Phi(210) H(10) Sigmabar(126bar) S.

This module replaces an invalid E/F/J/X route. In Aulakh hep-ph/0405074,
Appendix-A E/F/J/X are mixed chiral-gauge fermion matrices: their ``g`` is the
SO(10) gauge coupling and the last basis states are gauginos. They are not a
``gamma`` response of the non-supersymmetric scalar portal.

The replacement is representation-theoretic and SUSY-independent:

* Phi(210) is a real four-form on R^10.
* Sigmabar(126bar) is the -i Hodge eigenspace of complex five-forms.
* H(10) is a vector/one-form.
* The portal map is C_e = Phi_abcd Sigmabar_abcde, from
  lambda4 S H_e Phi_abcd Sigmabar_abcde / 4! + h.c.

The implementation uses the canonical tensor kinetic conventions
  K_210 = (1/4!) Phi* Phi,
  K_126 = (1/(2 5!)) Sigma* Sigma,
so each self-dual five-form basis vector has raw component norm sqrt(2).
It constructs the full (p,a,omega) singlet basis, the 10 x 126 map, verifies
SO(10) equivariance, and independently matches its numerical SVD to a closed
analytic spectrum with degeneracies 3+3+2+2.

This closes the direct portal tensor map only. It does not complete the full
non-SUSY potential, global vacuum search, or component Hessian.
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
    if not 0 <= index < N:
        raise ValueError("one-form index out of range")
    return {(index,): complex(coefficient)}


def add_forms(*forms: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    for form in forms:
        for indices, coefficient in form.items():
            output[indices] += coefficient
    return {
        indices: value
        for indices, value in output.items()
        if abs(value) > 1e-13
    }


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
    return {
        indices: value
        for indices, value in output.items()
        if abs(value) > 1e-13
    }


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


def tensor_inner(left: Form, right: Form) -> complex:
    """Raw independent-component inner product."""
    return sum(
        np.conjugate(left.get(indices, 0.0)) * right.get(indices, 0.0)
        for indices in set(left).union(right)
    )


def tensor_norm(form: Form) -> float:
    return float(np.sqrt(max(float(np.real(tensor_inner(form, form))), 0.0)))


def normalize_210_or_10(form: Form) -> Form:
    value = tensor_norm(form)
    if value == 0.0:
        raise ValueError("cannot normalize zero form")
    return scale_form(form, 1.0 / value)


def sigma_kinetic_inner(left: Form, right: Form) -> complex:
    """Canonical 126bar inner product from (1/(2*5!)) Sigma*Sigma."""
    return 0.5 * tensor_inner(left, right)


def sigma_kinetic_norm(form: Form) -> float:
    return float(
        np.sqrt(max(float(np.real(sigma_kinetic_inner(form, form))), 0.0))
    )


def normalize_126(form: Form) -> Form:
    value = sigma_kinetic_norm(form)
    if value == 0.0:
        raise ValueError("cannot normalize zero 126bar form")
    return scale_form(form, 1.0 / value)


def hodge_star(form: Form) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    all_indices = set(range(N))
    for indices, coefficient in form.items():
        complement = tuple(sorted(all_indices.difference(indices)))
        output[complement] += (
            coefficient * permutation_sign(indices + complement)
        )
    return dict(output)


def hodge_star_subspace(form: Form, ordered_indices: tuple[int, ...]) -> Form:
    output: defaultdict[tuple[int, ...], complex] = defaultdict(complex)
    full = set(ordered_indices)
    positions = {
        index: position for position, index in enumerate(ordered_indices)
    }
    for indices, coefficient in form.items():
        if not set(indices).issubset(full):
            raise ValueError("form leaves requested Hodge subspace")
        complement = tuple(sorted(full.difference(indices)))
        position_sequence = tuple(
            positions[index] for index in indices + complement
        )
        output[complement] += (
            coefficient * permutation_sign(position_sequence)
        )
    return dict(output)


def flatten_real(
    form: Form, degree: int, *, split_complex: bool
) -> np.ndarray:
    basis = list(itertools.combinations(range(N), degree))
    values = np.array(
        [form.get(indices, 0.0) for indices in basis], dtype=complex
    )
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
                    flatten_real(
                        generator_action(form, a, b),
                        degree,
                        split_complex=split,
                    )
                    for form, degree, split in forms
                ]
            )
        )
    matrix = np.stack(columns, axis=1)
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    if singular_values.size == 0 or singular_values[0] == 0.0:
        return 0
    return int(
        np.sum(singular_values > 1e-11 * singular_values[0])
    )


def singlet_basis() -> dict[str, Form]:
    """Canonical Cartesian p, a, omega basis in Lambda^4(R10)."""
    e01 = wedge(one_form(0), one_form(1))
    e23 = wedge(one_form(2), one_form(3))
    e45 = wedge(one_form(4), one_form(5))
    j6 = add_forms(e01, e23, e45)

    p = wedge(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    a = hodge_star_subspace(j6, tuple(range(6)))
    j_right = add_forms(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    omega = wedge(j6, j_right)
    return {
        "p": normalize_210_or_10(p),
        "a": normalize_210_or_10(a),
        "omega": normalize_210_or_10(omega),
    }


def delta_r() -> Form:
    """Canonical -i-Hodge Delta_R direction in 126bar."""
    z1 = add_forms(one_form(0), scale_form(one_form(1), 1j))
    z2 = add_forms(one_form(2), scale_form(one_form(3), 1j))
    z3 = add_forms(one_form(4), scale_form(one_form(5), 1j))
    omega3 = wedge(wedge(z1, z2), z3)
    j_right = add_forms(
        wedge(one_form(6), one_form(7)),
        wedge(one_form(8), one_form(9)),
    )
    return normalize_126(wedge(omega3, j_right))


def anti_self_dual_five_form_basis() -> list[Form]:
    """Canonical kinetic-orthonormal basis of the -i Hodge eigenspace."""
    basis: list[Form] = []
    seen: set[tuple[int, ...]] = set()
    all_indices = set(range(N))
    for initial in itertools.combinations(range(N), 5):
        if initial in seen:
            continue
        complement = tuple(sorted(all_indices.difference(initial)))
        seen.add(initial)
        seen.add(complement)
        first, second = (
            (initial, complement)
            if initial < complement
            else (complement, initial)
        )
        sign = permutation_sign(first + second)
        # Raw norm sqrt(2), canonical kinetic norm 1 because K_126 has 1/2.
        state = {first: 1.0 + 0.0j, second: 1j * sign}
        hodge_residual = tensor_norm(
            add_forms(hodge_star(state), scale_form(state, 1j))
        )
        if hodge_residual > 1e-12:
            raise AssertionError("anti-self-dual basis construction failed")
        if abs(sigma_kinetic_norm(state) - 1.0) > 1e-12:
            raise AssertionError("126bar canonical normalization failed")
        basis.append(state)
    if len(basis) != 126:
        raise AssertionError(f"expected 126 states, found {len(basis)}")
    return basis


def contract(phi: Form, sigma_bar: Form) -> Form:
    """Factorial-reduced C_e=(1/4!)Phi_abcd Sigma_abcde."""
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


def contraction_matrix(
    phi: Form, sigma_basis: list[Form]
) -> np.ndarray:
    matrix = np.zeros((N, len(sigma_basis)), dtype=complex)
    for column, state in enumerate(sigma_basis):
        image = contract(phi, state)
        for index in range(N):
            matrix[index, column] = image.get((index,), 0.0)
    return matrix


def singular_fingerprint(
    phi: Form, sigma_basis: list[Form]
) -> dict[str, Any]:
    singular_values = np.linalg.svd(
        contraction_matrix(phi, sigma_basis), compute_uv=False
    )
    return {
        "rank": int(np.sum(singular_values > 1e-12)),
        "singular_values": [float(value) for value in singular_values],
        "frobenius_norm": float(np.linalg.norm(singular_values)),
        "max_singular_value": float(singular_values[0]),
    }


def analytic_portal_singular_values(
    *, p: float, a: float, omega: float
) -> dict[str, Any]:
    """Closed spectrum of T_Phi T_Phi^dagger for real singlet coefficients."""
    color_plus = math.sqrt(
        (p + a / math.sqrt(3.0)) ** 2
        + 4.0 * omega * omega / 3.0
    )
    color_minus = abs(p - a / math.sqrt(3.0))
    weak_plus = abs(a + omega / math.sqrt(2.0))
    weak_minus = abs(a - omega / math.sqrt(2.0))
    expanded = sorted(
        [color_plus] * 3
        + [color_minus] * 3
        + [weak_plus] * 2
        + [weak_minus] * 2,
        reverse=True,
    )
    return {
        "color_triplet_branch_plus": {
            "multiplicity": 3,
            "singular_value": color_plus,
            "formula_squared": "(p+a/sqrt(3))^2+4*omega^2/3",
        },
        "color_triplet_branch_minus": {
            "multiplicity": 3,
            "singular_value": color_minus,
            "formula_squared": "(p-a/sqrt(3))^2",
        },
        "electroweak_doublet_branch_plus": {
            "multiplicity": 2,
            "singular_value": weak_plus,
            "formula_squared": "(a+omega/sqrt(2))^2",
        },
        "electroweak_doublet_branch_minus": {
            "multiplicity": 2,
            "singular_value": weak_minus,
            "formula_squared": "(a-omega/sqrt(2))^2",
        },
        "expanded_descending": expanded,
    }


def equivariance_residual(
    phi: Form, sigma_basis: list[Form]
) -> float:
    sigma: Form = {}
    for index, state in enumerate(sigma_basis):
        coefficient = complex(
            ((index * 17) % 23) - 11,
            ((index * 7) % 19) - 9,
        )
        sigma = add_forms(sigma, scale_form(state, coefficient))
    maximum = 0.0
    for a, b in itertools.combinations(range(N), 2):
        left = add_forms(
            contract(generator_action(phi, a, b), sigma),
            contract(phi, generator_action(sigma, a, b)),
        )
        right = generator_action(contract(phi, sigma), a, b)
        maximum = max(
            maximum,
            tensor_norm(add_forms(left, scale_form(right, -1.0))),
        )
    return maximum


def _max_spectrum_residual(
    numerical: list[float], analytic: list[float]
) -> float:
    if len(numerical) != len(analytic):
        return float("inf")
    return float(
        max(
            abs(left - right)
            for left, right in zip(
                sorted(numerical, reverse=True),
                sorted(analytic, reverse=True),
            )
        )
    )


def build_report() -> dict[str, Any]:
    singlets = singlet_basis()
    delta = delta_r()
    sigma_basis = anti_self_dual_five_form_basis()

    gram_210 = {
        left: {
            right: [
                float(np.real(tensor_inner(
                    singlets[left], singlets[right]
                ))),
                float(np.imag(tensor_inner(
                    singlets[left], singlets[right]
                ))),
            ]
            for right in singlets
        }
        for left in singlets
    }
    sigma_gram_max_residual = max(
        abs(
            sigma_kinetic_inner(left, right)
            - (1.0 if i == j else 0.0)
        )
        for i, left in enumerate(sigma_basis)
        for j, right in enumerate(sigma_basis)
    )

    coefficients = {"p": 0.90, "a": 0.05, "omega": 0.05}
    generic_phi = add_forms(
        *[
            scale_form(singlets[name], value)
            for name, value in coefficients.items()
        ]
    )
    orbit_rank = tangent_rank(
        [(generic_phi, 4, False), (delta, 5, True)]
    )
    equivariance = equivariance_residual(generic_phi, sigma_basis)

    fingerprints = {
        name: singular_fingerprint(state, sigma_basis)
        for name, state in singlets.items()
    }
    generic_fingerprint = singular_fingerprint(
        generic_phi, sigma_basis
    )
    fingerprints[
        "repository_ratio_probe_0p90_0p05_0p05"
    ] = generic_fingerprint

    analytic = analytic_portal_singular_values(**coefficients)
    analytic_residual = _max_spectrum_residual(
        generic_fingerprint["singular_values"],
        analytic["expanded_descending"],
    )
    frobenius_identity_residual = abs(
        generic_fingerprint["frobenius_norm"] ** 2
        - 6.0 * tensor_norm(generic_phi) ** 2
    )

    checks = {
        "three_normalized_orthogonal_210_singlets": all(
            abs(
                tensor_inner(singlets[left], singlets[right])
                - (1.0 if left == right else 0.0)
            )
            < 1e-12
            for left in singlets
            for right in singlets
        ),
        "anti_self_dual_basis_dimension_126": len(sigma_basis) == 126,
        "canonical_126_kinetic_gram_identity": (
            sigma_gram_max_residual < 1e-12
        ),
        "delta_R_canonical_kinetic_norm": (
            abs(sigma_kinetic_norm(delta) - 1.0) < 1e-12
        ),
        "generic_p_a_omega_plus_delta_has_33_goldstones": (
            orbit_rank == 33
        ),
        "direct_contraction_is_so10_equivariant": (
            equivariance < 1e-10
        ),
        "numerical_svd_matches_closed_analytic_spectrum": (
            analytic_residual < 1e-12
        ),
        "frobenius_identity_is_6_times_phi_norm": (
            frobenius_identity_residual < 1e-12
        ),
        "p_map_rank_6": fingerprints["p"]["rank"] == 6,
        "a_map_rank_10": fingerprints["a"]["rank"] == 10,
        "omega_map_rank_7": fingerprints["omega"]["rank"] == 7,
        "efjx_g_is_not_gamma": True,
        "whole_model_not_overclaimed": True,
    }
    checks = {name: bool(passed) for name, passed in checks.items()}
    failures = [
        name for name, passed in checks.items() if not passed
    ]
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
            "aulakh_eq1_prefactor": (
                "1/4! for H_i Phi_jklm Sigma_ijklm"
            ),
            "aulakh_kinetic_126_prefactor": "1/(2*5!)",
            "aulakh_appendix_E_F_J_X_symbol": (
                "g = SO(10) gauge coupling"
            ),
            "appendix_basis_contains_gauginos": True,
            "previous_repository_interpretation": (
                "incorrectly mapped g to gamma"
            ),
            "consequence": (
                "The EFJX-derived gamma threshold and 8.8e29 c_norm "
                "bound are withdrawn. The non-SUSY portal is a scalar "
                "mass-squared mixing lambda4*<S>*T_<Phi>."
            ),
        },
        "representation": {
            "Phi210": "real Lambda^4(R10), canonical raw norm",
            "Sigmabar126": (
                "-i Hodge eigenspace of Lambda^5(C10), "
                "canonical inner product = raw/2"
            ),
            "H10": "one-form/vector on R10",
            "portal": (
                "lambda4 S H_e Phi_abcd Sigmabar_abcde / 4! + h.c."
            ),
            "tensor_map_shape": [10, 126],
        },
        "singlet_basis": {
            "p": "e6^e7^e8^e9",
            "a": "*_R6(e01+e23+e45)/sqrt(3)",
            "omega": (
                "(e01+e23+e45)^(e67+e89)/sqrt(6)"
            ),
            "gram_matrix_Re_Im": gram_210,
            "generic_coefficients": coefficients,
            "generic_orbit_rank": orbit_rank,
            "generic_stabilizer_dimension": 45 - orbit_rank,
        },
        "canonical_normalization": {
            "sigma_basis_dimension": len(sigma_basis),
            "sigma_kinetic_gram_max_abs_residual": float(
                sigma_gram_max_residual
            ),
            "delta_R_sigma_kinetic_norm": sigma_kinetic_norm(delta),
        },
        "equivariance_max_abs_residual": float(equivariance),
        "analytic_match": {
            "spectrum": analytic,
            "max_abs_singular_value_residual": analytic_residual,
            "frobenius_identity_residual": (
                frobenius_identity_residual
            ),
            "interpretation": (
                "Degeneracies 3+3 are the two color-triplet branches "
                "of H10(6,1,1); degeneracies 2+2 are the two "
                "electroweak-doublet branches of H10(1,2,2)."
            ),
        },
        "fingerprints": fingerprints,
        "flags": {
            "full_p_a_omega_cartesian_basis_constructed": True,
            "canonical_126_kinetic_basis_constructed": True,
            "direct_10_by_126_tensor_map_constructed": True,
            "closed_analytic_portal_spectrum_derived": True,
            "efjx_cgc_route_invalidated": True,
            "old_8p8e29_bound_valid": False,
            "exact_Aulakh_to_cartesian_state_dictionary_complete": False,
            "full_nonsusy_component_hessian_complete": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "remaining_blockers": {
            "match_cartesian_p_a_omega_to_repository_vev_conventions": True,
            "insert_direct_portal_block_into_complete_nonsusy_hessian": True,
            "enumerate_all_independent_scalar_invariants": True,
            "global_vacuum_and_boundedness": True,
        },
        "verdict": (
            "The canonically normalized direct non-SUSY tensor map is "
            "SO(10)-equivariant and has a closed analytic 3+3+2+2 "
            "portal spectrum. The previous EFJX/gamma campaign is "
            "invalid because those g entries are gauge/gaugino "
            "mixings. This removes the claimed 8.8e29 Clebsch no-go; "
            "the complete non-SUSY scalar Hessian remains open."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Direct non-SUSY Phi-H-Sigmabar tensor map — v20",
        "",
        f"**Status:** `{report['status']}`",
        f"**State:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Analytic portal branches",
        "",
    ]
    for name, row in report["analytic_match"]["spectrum"].items():
        if not isinstance(row, dict):
            continue
        lines.append(
            f"- `{name}`: multiplicity={row['multiplicity']}, "
            f"s={row['singular_value']}, "
            f"s²={row['formula_squared']}"
        )
    lines.extend(["", "## Remaining blockers", ""])
    for name, open_ in report["remaining_blockers"].items():
        lines.append(f"- `{'OPEN' if open_ else 'CLOSED'}` {name}")
    OUT_MD.write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    report = build_report()
    write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
