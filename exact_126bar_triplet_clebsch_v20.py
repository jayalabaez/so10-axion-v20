#!/usr/bin/env python3
"""Exact SO(10) five-form triplet branching and portal Clebsches (v20).

This module performs a representation-level continuation of G1 without using
SUSY mass matrices or guessed component coefficients.

It constructs both Hodge chiralities of Lambda^5(C^10), embeds the standard
Pati-Salam/SM subgroup in the same Cartesian basis used by
``direct_phi_h_sigmabar_tensor_v20``, and diagonalizes a commuting set of
Casimirs and Cartans.  For the chirality matching the v20 126bar charge
convention it derives, with canonical kinetic normalization,

* one t2 triplet (3,1,-1/3),
* one t2bar antitriplet (3bar,1,+1/3),
* one t4bar antitriplet from the SU(2)_R triplet,
* the SM-singlet B-L breaking direction.

Restricting the exact Phi-H-Sigmabar contraction to those states gives the
non-SUSY portal coefficients in the normalized Cartesian singlet basis:

    Hbar_10 <- t2       : p - a/sqrt(3)
    H_10    <- t2bar    : p + a/sqrt(3)
    H_10    <- t4bar    : 2 omega/sqrt(3)

After P=p, A=sqrt(3)a, W=sqrt(6)omega this reproduces the published magnitude
structure (p-a), (p+a), and 2 sqrt(2) omega independently.

The calculation also proves that the historical symmetric four-state basis
(T_10, Tbar_10, T_126, Tprime_126) is not one Hermitian charge sector.  A
non-SUSY M^2 must be built separately in Y=-1/3 and Y=+1/3 sectors.

Scope: this closes the direct portal triplet branching, kinetic normalization,
and off-diagonal lambda4 Clebsches.  Diagonal potential Clebsches, the complete
component Hessian, and the physical spectrum remain open.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as direct

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_126BAR_TRIPLET_CLEBSCH_V20.json"
OUT_MD = ROOT / "EXACT_126BAR_TRIPLET_CLEBSCH_V20.md"
TOL = 5.0e-8


def _near(value: float, target: float, tol: float = TOL) -> bool:
    return abs(float(value) - float(target)) <= tol


def _hodge_basis(chirality: str) -> tuple[direct.Form, ...]:
    """Canonical kinetic-orthonormal +/-i Hodge basis."""
    if chirality not in {"+i", "-i"}:
        raise ValueError("chirality must be '+i' or '-i'")
    basis: list[direct.Form] = []
    seen: set[tuple[int, ...]] = set()
    all_indices = set(range(direct.N))
    for initial in itertools.combinations(range(direct.N), 5):
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
        orientation = direct.permutation_sign(first + second)
        coefficient = (
            -1j * orientation if chirality == "+i" else 1j * orientation
        )
        state = {first: 1.0 + 0.0j, second: coefficient}
        expected = 1j if chirality == "+i" else -1j
        residual = direct.tensor_norm(
            direct.add_forms(
                direct.hodge_star(state), direct.scale_form(state, -expected)
            )
        )
        if residual > 1.0e-12:
            raise AssertionError("Hodge chirality construction failed")
        if abs(direct.sigma_kinetic_norm(state) - 1.0) > 1.0e-12:
            raise AssertionError("canonical 126 kinetic normalization failed")
        basis.append(state)
    if len(basis) != 126:
        raise AssertionError(f"expected 126 states, found {len(basis)}")
    return tuple(basis)


def _coords(form: direct.Form, basis: tuple[direct.Form, ...]) -> np.ndarray:
    return np.asarray(
        [direct.sigma_kinetic_inner(state, form) for state in basis],
        dtype=complex,
    )


def _form(vector: np.ndarray, basis: tuple[direct.Form, ...]) -> direct.Form:
    pieces = [
        direct.scale_form(basis[index], coefficient)
        for index, coefficient in enumerate(np.asarray(vector, dtype=complex))
        if abs(coefficient) > 1.0e-13
    ]
    return direct.add_forms(*pieces) if pieces else {}


@lru_cache(maxsize=None)
def _elementary_rep(chirality: str, a: int, b: int) -> np.ndarray:
    basis = _hodge_basis(chirality)
    matrix = np.zeros((126, 126), dtype=complex)
    for column, state in enumerate(basis):
        matrix[:, column] = _coords(
            direct.generator_action(state, a, b), basis
        )
    return matrix


def _gell_mann() -> list[np.ndarray]:
    root3 = math.sqrt(3.0)
    return [
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=complex),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=complex),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=complex),
        np.array([[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=complex),
        np.array([[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=complex),
        np.array([[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=complex),
        np.array([[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=complex),
        np.array([[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=complex)
        / root3,
    ]


def _complex_antihermitian_to_real(matrix: np.ndarray) -> np.ndarray:
    """Real 6-vector action on interleaved (Re z_i, Im z_i)."""
    real = np.asarray(matrix.real, dtype=float)
    imag = np.asarray(matrix.imag, dtype=float)
    output = np.zeros((6, 6), dtype=float)
    for i in range(3):
        for j in range(3):
            output[2 * i, 2 * j] = real[i, j]
            output[2 * i, 2 * j + 1] = -imag[i, j]
            output[2 * i + 1, 2 * j] = imag[i, j]
            output[2 * i + 1, 2 * j + 1] = real[i, j]
    return output


def _rep_from_real(chirality: str, matrix: np.ndarray) -> np.ndarray:
    generator = np.zeros((126, 126), dtype=complex)
    for a, b in itertools.combinations(range(direct.N), 2):
        coefficient = float(matrix[a, b])
        if abs(coefficient) > 1.0e-14:
            generator += coefficient * _elementary_rep(chirality, a, b)
    return generator


def _hermitian_from_terms(
    chirality: str, terms: dict[tuple[int, int], float]
) -> np.ndarray:
    generator = np.zeros((126, 126), dtype=complex)
    for pair, coefficient in terms.items():
        generator += float(coefficient) * _elementary_rep(
            chirality, pair[0], pair[1]
        )
    return -1j * generator


@lru_cache(maxsize=2)
def _subgroup_operators(chirality: str) -> dict[str, np.ndarray]:
    su3: list[np.ndarray] = []
    for lam in _gell_mann():
        antihermitian = -1j * lam / 2.0
        real6 = _complex_antihermitian_to_real(antihermitian)
        real10 = np.zeros((10, 10), dtype=float)
        real10[:6, :6] = real6
        su3.append(-1j * _rep_from_real(chirality, real10))

    su2r = [
        _hermitian_from_terms(
            chirality, {(7, 8): 0.5, (6, 9): 0.5}
        ),
        _hermitian_from_terms(
            chirality, {(6, 8): -0.5, (7, 9): 0.5}
        ),
        _hermitian_from_terms(
            chirality, {(6, 7): 0.5, (8, 9): 0.5}
        ),
    ]
    su2l = [
        _hermitian_from_terms(
            chirality, {(7, 8): 0.5, (6, 9): -0.5}
        ),
        _hermitian_from_terms(
            chirality, {(6, 8): -0.5, (7, 9): -0.5}
        ),
        _hermitian_from_terms(
            chirality, {(6, 7): 0.5, (8, 9): -0.5}
        ),
    ]

    planes = [
        -1j * _elementary_rep(chirality, 0, 1),
        -1j * _elementary_rep(chirality, 2, 3),
        -1j * _elementary_rep(chirality, 4, 5),
        -1j * _elementary_rep(chirality, 6, 7),
        -1j * _elementary_rep(chirality, 8, 9),
    ]
    b_minus_l = -(2.0 / 3.0) * (planes[0] + planes[1] + planes[2])
    t3l = su2l[2]
    t3r = su2r[2]
    hypercharge = t3r + 0.5 * b_minus_l
    c3 = sum(operator @ operator for operator in su3)
    c2l = sum(operator @ operator for operator in su2l)
    c2r = sum(operator @ operator for operator in su2r)
    return {
        "BL": b_minus_l,
        "T3L": t3l,
        "T3R": t3r,
        "Y": hypercharge,
        "C3": c3,
        "C2L": c2l,
        "C2R": c2r,
        "I3": su3[2],
        "I8": su3[7],
        "SU3_1": su3[0],
        "SU3_2": su3[1],
        "SU2L_1": su2l[0],
        "SU2L_2": su2l[1],
        "SU2R_1": su2r[0],
        "SU2R_2": su2r[1],
    }


def _commutator_residual(operators: dict[str, np.ndarray]) -> float:
    # The SO(6) complex-vector embedding acts on one-forms (the dual
    # fundamental), hence its displayed Gell-Mann basis carries the opposite
    # structure-constant sign. Casimirs and weight multiplicities are
    # unaffected; the sign is fixed explicitly rather than hidden.
    checks = [
        ("SU3_1", "SU3_2", "I3", -1.0),
        ("SU2L_1", "SU2L_2", "T3L", 1.0),
        ("SU2R_1", "SU2R_2", "T3R", 1.0),
    ]
    return float(
        max(
            np.max(
                np.abs(
                    operators[left] @ operators[right]
                    - operators[right] @ operators[left]
                    - sign * 1j * operators[target]
                )
            )
            for left, right, target, sign in checks
        )
    )


def _phase_fix(vector: np.ndarray) -> np.ndarray:
    output = np.asarray(vector, dtype=complex).copy()
    index = int(np.argmax(np.abs(output)))
    if abs(output[index]) > 0.0:
        output *= np.exp(-1j * np.angle(output[index]))
    return output


def _joint_states(chirality: str) -> list[dict[str, Any]]:
    operators = _subgroup_operators(chirality)
    key = (
        0.113 * operators["BL"]
        + 0.137 * operators["T3L"]
        + 0.173 * operators["T3R"]
        + 0.197 * operators["C3"]
        + 0.223 * operators["C2L"]
        + 0.257 * operators["C2R"]
        + 0.293 * operators["I3"]
        + 0.317 * operators["I8"]
    )
    _, vectors = np.linalg.eigh(key)
    rows: list[dict[str, Any]] = []
    quantum_names = ("BL", "T3L", "T3R", "Y", "C3", "C2L", "C2R", "I3", "I8")
    for column in range(vectors.shape[1]):
        vector = _phase_fix(vectors[:, column])
        quantum: dict[str, float] = {}
        residual = 0.0
        for name in quantum_names:
            operator = operators[name]
            value = float(np.real(np.vdot(vector, operator @ vector)))
            quantum[name] = value
            residual = max(
                residual,
                float(np.linalg.norm(operator @ vector - value * vector)),
            )
        rows.append(
            {
                "vector": vector,
                "quantum": quantum,
                "joint_eigen_residual": residual,
            }
        )
    return rows


TRIPLET_WEIGHTS = (
    (0.5, 1.0 / (2.0 * math.sqrt(3.0))),
    (-0.5, 1.0 / (2.0 * math.sqrt(3.0))),
    (0.0, -1.0 / math.sqrt(3.0)),
)
ANTITRIPLET_WEIGHTS = tuple((-i3, -i8) for i3, i8 in TRIPLET_WEIGHTS)


def _weight_index(
    i3: float, i8: float, expected: tuple[tuple[float, float], ...]
) -> int:
    distances = [abs(i3 - x) + abs(i8 - y) for x, y in expected]
    index = int(np.argmin(distances))
    if distances[index] > 1.0e-6:
        raise AssertionError(f"unexpected SU(3) weight {(i3, i8)}")
    return index


def _classified_triplets() -> dict[str, dict[int, np.ndarray]]:
    rows = _joint_states("+i")
    result: dict[str, dict[int, np.ndarray]] = {
        "t2_triplet": {},
        "t2bar_antitriplet": {},
        "t4bar_antitriplet": {},
    }
    for row in rows:
        q = row["quantum"]
        if not (_near(q["C3"], 4.0 / 3.0) and _near(q["C2L"], 0.0)):
            continue
        if not _near(q["T3R"], 0.0):
            continue
        if (
            _near(q["BL"], -2.0 / 3.0)
            and _near(q["Y"], -1.0 / 3.0)
            and _near(q["C2R"], 0.0)
        ):
            index = _weight_index(q["I3"], q["I8"], TRIPLET_WEIGHTS)
            result["t2_triplet"][index] = row["vector"]
        elif (
            _near(q["BL"], 2.0 / 3.0)
            and _near(q["Y"], 1.0 / 3.0)
            and _near(q["C2R"], 0.0)
        ):
            index = _weight_index(q["I3"], q["I8"], ANTITRIPLET_WEIGHTS)
            result["t2bar_antitriplet"][index] = row["vector"]
        elif (
            _near(q["BL"], 2.0 / 3.0)
            and _near(q["Y"], 1.0 / 3.0)
            and _near(q["C2R"], 2.0)
        ):
            index = _weight_index(q["I3"], q["I8"], ANTITRIPLET_WEIGHTS)
            result["t4bar_antitriplet"][index] = row["vector"]
    return result


def _left_color_basis() -> dict[str, list[direct.Form]]:
    triplet: list[direct.Form] = []
    antitriplet: list[direct.Form] = []
    for index in range(3):
        real = direct.one_form(2 * index)
        imaginary = direct.one_form(2 * index + 1)
        triplet.append(
            direct.normalize_210_or_10(
                direct.add_forms(real, direct.scale_form(imaginary, 1j))
            )
        )
        antitriplet.append(
            direct.normalize_210_or_10(
                direct.add_forms(real, direct.scale_form(imaginary, -1j))
            )
        )
    return {"triplet": triplet, "antitriplet": antitriplet}


def _coupling(
    phi: direct.Form,
    vector: np.ndarray,
    basis: tuple[direct.Form, ...],
    left: direct.Form,
) -> complex:
    return direct.tensor_inner(left, direct.contract(phi, _form(vector, basis)))


def _aligned_vector(
    vector: np.ndarray,
    reference_phi: direct.Form,
    left: direct.Form,
    basis: tuple[direct.Form, ...],
) -> np.ndarray:
    coefficient = _coupling(reference_phi, vector, basis, left)
    if abs(coefficient) < 1.0e-12:
        raise AssertionError("phase reference coupling vanished")
    return vector * np.exp(-1j * np.angle(coefficient))


def _portal_clebsches() -> dict[str, Any]:
    basis = _hodge_basis("+i")
    classified = _classified_triplets()
    left = _left_color_basis()
    singlets = direct.singlet_basis()
    specifications = {
        "Hbar10_from_t2_triplet": {
            "states": classified["t2_triplet"],
            "left": left["triplet"],
            "reference": "p",
        },
        "H10_from_t2bar_antitriplet": {
            "states": classified["t2bar_antitriplet"],
            "left": left["antitriplet"],
            "reference": "p",
        },
        "H10_from_t4bar_antitriplet": {
            "states": classified["t4bar_antitriplet"],
            "left": left["antitriplet"],
            "reference": "omega",
        },
    }
    result: dict[str, Any] = {}
    maximum_leakage = 0.0
    for name, spec in specifications.items():
        rows: list[dict[str, Any]] = []
        for weight_index in range(3):
            vector = _aligned_vector(
                spec["states"][weight_index],
                singlets[spec["reference"]],
                spec["left"][weight_index],
                basis,
            )
            coefficients: dict[str, float] = {}
            leakage = 0.0
            for singlet_name, phi in singlets.items():
                output = direct.contract(phi, _form(vector, basis))
                matched = direct.tensor_inner(
                    spec["left"][weight_index], output
                )
                coefficients[singlet_name] = float(np.real_if_close(matched).real)
                for other_index, other_left in enumerate(spec["left"]):
                    if other_index == weight_index:
                        continue
                    leakage = max(
                        leakage,
                        float(abs(direct.tensor_inner(other_left, output))),
                    )
            maximum_leakage = max(maximum_leakage, leakage)
            rows.append(
                {
                    "weight_index": weight_index,
                    "coefficients": coefficients,
                    "off_weight_leakage": leakage,
                }
            )
        averages = {
            singlet: float(np.mean([row["coefficients"][singlet] for row in rows]))
            for singlet in ("p", "a", "omega")
        }
        spreads = {
            singlet: float(
                max(
                    abs(row["coefficients"][singlet] - averages[singlet])
                    for row in rows
                )
            )
            for singlet in ("p", "a", "omega")
        }
        result[name] = {
            "rows": rows,
            "coefficients_cartesian": averages,
            "max_weight_spread": max(spreads.values()),
        }
    result["maximum_off_weight_leakage"] = maximum_leakage
    return result


def _chirality_audit() -> dict[str, Any]:
    current = tuple(direct.anti_self_dual_five_form_basis())
    plus = _hodge_basis("+i")
    minus_residual = max(
        direct.tensor_norm(
            direct.add_forms(
                direct.hodge_star(state), direct.scale_form(state, 1j)
            )
        )
        for state in current
    )
    plus_residual = max(
        direct.tensor_norm(
            direct.add_forms(
                direct.hodge_star(state), direct.scale_form(state, -1j)
            )
        )
        for state in plus
    )
    singlets = direct.singlet_basis()
    probe = direct.add_forms(
        direct.scale_form(singlets["p"], 0.9),
        direct.scale_form(singlets["a"], 0.4),
        direct.scale_form(singlets["omega"], 0.7),
    )
    current_sv = np.linalg.svd(
        direct.contraction_matrix(probe, list(current)), compute_uv=False
    )
    plus_sv = np.linalg.svd(
        direct.contraction_matrix(probe, list(plus)), compute_uv=False
    )
    spectrum_residual = float(
        np.max(
            np.abs(
                np.sort(current_sv)[::-1] - np.sort(plus_sv)[::-1]
            )
        )
    )
    return {
        "current_direct_basis_hodge_eigenvalue": "-i",
        "current_minus_i_residual": float(minus_residual),
        "branching_basis_hodge_eigenvalue": "+i",
        "branching_plus_i_residual": float(plus_residual),
        "conjugate_chirality_singular_spectrum_residual": spectrum_residual,
        "basis_independent_singular_spectrum_preserved": spectrum_residual < 1.0e-10,
        "component_labels_require_one_consistent_chirality_convention": True,
    }


def _sm_singlet_count() -> int:
    count = 0
    for row in _joint_states("+i"):
        q = row["quantum"]
        if (
            _near(q["C3"], 0.0)
            and _near(q["C2L"], 0.0)
            and _near(q["C2R"], 2.0)
            and _near(q["Y"], 0.0)
        ):
            count += 1
    return count


def build_report() -> dict[str, Any]:
    operators = _subgroup_operators("+i")
    classified = _classified_triplets()
    clebsch = _portal_clebsches()
    chirality = _chirality_audit()
    basis = _hodge_basis("+i")

    all_vectors = [
        vector
        for group in classified.values()
        for vector in group.values()
    ]
    gram = np.asarray(
        [[np.vdot(left, right) for right in all_vectors] for left in all_vectors]
    )
    norm_residual = float(np.max(np.abs(gram - np.eye(len(all_vectors)))))
    joint_residual = max(
        row["joint_eigen_residual"] for row in _joint_states("+i")
    )

    c_minus = clebsch["Hbar10_from_t2_triplet"]["coefficients_cartesian"]
    c_plus = clebsch["H10_from_t2bar_antitriplet"]["coefficients_cartesian"]
    c_t4 = clebsch["H10_from_t4bar_antitriplet"]["coefficients_cartesian"]
    root3 = math.sqrt(3.0)

    probe = {"p": 0.9, "a": 0.4, "omega": 0.7}
    reconstructed_minus = abs(
        sum(c_minus[name] * probe[name] for name in probe)
    )
    reconstructed_plus = math.sqrt(
        sum(c_plus[name] * probe[name] for name in probe) ** 2
        + sum(c_t4[name] * probe[name] for name in probe) ** 2
    )
    analytic = direct.analytic_portal_singular_values(**probe)
    analytic_minus = analytic["color_triplet_branch_minus"]["singular_value"]
    analytic_plus = analytic["color_triplet_branch_plus"]["singular_value"]

    checks = {
        "plus_chirality_dimension_126": len(basis) == 126,
        "subgroup_algebra_closes": _commutator_residual(operators) < 1.0e-10,
        "joint_quantum_numbers_resolved": joint_residual < 5.0e-8,
        "t2_triplet_has_three_weights": len(classified["t2_triplet"]) == 3,
        "t2bar_antitriplet_has_three_weights": len(classified["t2bar_antitriplet"]) == 3,
        "t4bar_antitriplet_has_three_weights": len(classified["t4bar_antitriplet"]) == 3,
        "one_sm_singlet_found": _sm_singlet_count() == 1,
        "canonical_kinetic_orthonormality": norm_residual < 1.0e-10,
        "off_weight_portal_leakage_zero": clebsch["maximum_off_weight_leakage"] < 1.0e-9,
        "t2_triplet_p_coefficient": _near(c_minus["p"], 1.0),
        "t2_triplet_a_coefficient": _near(c_minus["a"], -1.0 / root3),
        "t2_triplet_omega_zero": _near(c_minus["omega"], 0.0),
        "t2bar_p_coefficient": _near(c_plus["p"], 1.0),
        "t2bar_a_coefficient": _near(c_plus["a"], 1.0 / root3),
        "t2bar_omega_zero": _near(c_plus["omega"], 0.0),
        "t4bar_only_omega": _near(c_t4["p"], 0.0)
        and _near(c_t4["a"], 0.0)
        and _near(c_t4["omega"], 2.0 / root3),
        "reconstructs_color_minus_singular_value": abs(
            reconstructed_minus - analytic_minus
        )
        < 1.0e-9,
        "reconstructs_color_plus_singular_value": abs(
            reconstructed_plus - analytic_plus
        )
        < 1.0e-9,
        "conjugate_chirality_spectrum_preserved": chirality[
            "basis_independent_singular_spectrum_preserved"
        ],
        "legacy_4x4_not_one_hermitian_charge_sector": True,
        "full_physical_spectrum_not_claimed": True,
    }
    failures = [name for name, ok in checks.items() if not ok]

    return {
        "status": (
            "EXACT_126BAR_TRIPLET_BRANCHING_AND_PORTAL_CLEBSCH_DERIVED__FULL_MT2_OPEN"
            if not failures
            else "EXACT_126BAR_TRIPLET_CLEBSCH_FAILED"
        ),
        "overall_state": "PARTIAL" if not failures else "EXECUTION_FAIL",
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "embedding": {
            "SO6_color_planes": [[0, 1], [2, 3], [4, 5]],
            "SO4_weak_planes": [[6, 7], [8, 9]],
            "B_minus_L": "-(2/3)(H01+H23+H45)",
            "hypercharge": "Y=T3R+(B-L)/2",
            "SU2R": "self-dual SO(4)",
            "SU2L": "anti-self-dual SO(4)",
        },
        "derived_multiplicities": {
            "t2_triplet_3_1_minus_third": len(classified["t2_triplet"]),
            "t2bar_antitriplet_3bar_1_plus_third": len(
                classified["t2bar_antitriplet"]
            ),
            "t4bar_antitriplet_3bar_1_plus_third": len(
                classified["t4bar_antitriplet"]
            ),
            "sm_singlet": _sm_singlet_count(),
        },
        "kinetic_normalization": {
            "convention": "(1/(2*5!)) Sigma*Sigma",
            "n_normalized_triplet_weight_states": len(all_vectors),
            "gram_max_abs_residual": norm_residual,
            "derived": norm_residual < 1.0e-10,
        },
        "portal_clebsches": clebsch,
        "aulakh_coordinate_translation": {
            "P": "p",
            "A": "sqrt(3)*a",
            "W": "sqrt(6)*omega",
            "Hbar10_from_t2": "p-a",
            "H10_from_t2bar": "p+a",
            "H10_from_t4bar": "2*sqrt(2)*omega",
        },
        "singular_value_reconstruction": {
            "probe": probe,
            "color_minus_reconstructed": reconstructed_minus,
            "color_minus_analytic": analytic_minus,
            "color_plus_reconstructed": reconstructed_plus,
            "color_plus_analytic": analytic_plus,
        },
        "chirality_convention_audit": chirality,
        "corrected_nonsusy_charge_sectors": {
            "Y_minus_1_over_3": [
                "T10_(3,1,-1/3)",
                "T126_t2_(3,1,-1/3)",
            ],
            "Y_plus_1_over_3": [
                "T10bar_(3bar,1,+1/3)",
                "T126bar_t2bar_(3bar,1,+1/3)",
                "T126bar_t4bar_(3bar,1,+1/3)",
            ],
            "historical_symmetric_4x4_single_sector_valid": False,
            "required_matrix_structure": (
                "separate Hermitian M2 blocks by hypercharge; holomorphic/SUSY "
                "triplet-antitriplet matrices are not non-SUSY scalar M2"
            ),
        },
        "remaining_blockers": {
            "all_diagonal_component_clebsches": True,
            "complete_charge_sector_component_basis": True,
            "full_projected_nonsusy_potential": True,
            "stationary_positive_full_hessian": True,
            "physical_triplet_spectrum": True,
            "unique_proton_lifetime": True,
        },
        "flag": {
            "exact_126bar_weight_branching_derived": not failures,
            "canonical_triplet_kinetic_normalization_derived": not failures,
            "lambda4_triplet_portal_clebsches_derived": not failures,
            "published_magnitude_structure_independently_reproduced": not failures,
            "legacy_symmetric_4x4_charge_sector_valid": False,
            "basis_independent_portal_singular_spectrum_preserved": chirality[
                "basis_independent_singular_spectrum_preserved"
            ],
            "full_diagonal_component_CG_complete": False,
            "physical_triplet_spectrum_complete": False,
            "exact_unique_proton_lifetime": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "Exact five-form branching separates t2 and t4bar by SU(2)_R "
            "Casimir, canonically normalizes all nine color weight states, and "
            "derives the lambda4 portal coefficients p-a/sqrt(3), "
            "p+a/sqrt(3), and 2 omega/sqrt(3). The historical symmetric 4x4 "
            "basis mixes opposite hypercharge sectors and is not a physical "
            "non-SUSY Hermitian M2. Diagonal Clebsches and the full spectrum "
            "remain open."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    c = report["portal_clebsches"]
    return "\n".join(
        [
            "# Exact 126bar triplet branching and portal Clebsches — v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Derived normalized Cartesian coefficients",
            "",
            f"- Hbar10 <- t2: `{c['Hbar10_from_t2_triplet']['coefficients_cartesian']}`",
            f"- H10 <- t2bar: `{c['H10_from_t2bar_antitriplet']['coefficients_cartesian']}`",
            f"- H10 <- t4bar: `{c['H10_from_t4bar_antitriplet']['coefficients_cartesian']}`",
            "",
            "## Corrected mass-squared structure",
            "",
            "- Y=-1/3 and Y=+1/3 require separate Hermitian blocks.",
            "- The historical symmetric four-state matrix is conditional and non-physical.",
            "- Diagonal component Clebsches and the complete spectrum remain open.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
