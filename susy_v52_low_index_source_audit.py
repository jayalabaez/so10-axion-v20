#!/usr/bin/env python3
"""V52 exact low-Dynkin-index Spin(10) source-sector audit.

This module tests a lean renormalizable N=1 source sector

    E(54) + A(45) + C(16) + Cbar(bar16)

in an explicit 131-complex-coordinate Cartesian chart.  The superpotential is

    W = 1/2 mE Tr(E^2) + 1/3 lambda Tr(E^3)
        - 1/4 mA Tr(A^2) - 1/2 kappa Tr(E A^2)
        + Cbar^T [mC I + eta rho_16(A)] C.

It is the matrix-normalized version of the standard renormalizable
54+45+16+bar16 source superpotential.  The audited rational witness is

    mE=9/5, lambda=kappa=1, mA=11, eta=-3 i/10, mC=27/20,
    E0=diag(2,2,2,2,2,2,-3,-3,-3,-3),
    A0=J01+J23+J45+3 J67+3 J89,
    C0=Cbar0=10 e_15,

where ``Jab`` is the real antisymmetric vector generator and ``e_15`` is the
pure-spinor SU(5)-singlet state in the repository's locked negative-chirality
Clifford basis.

Every F term and D moment vanishes exactly.  The Spin(10) orbit has rank 33,
so the stabilizer has dimension 12, as required for the Standard Model.  The
full holomorphic Hessian has rank 98 and nullity 33; its kernel is exactly the
complexified broken-gauge orbit.  These statements are certified over F_37
with i -> 6 and by exact Gaussian-integer Ward products.

This is a source-sector result, not a complete G2 closure.  A 16-Higgs breaks
B-L by one unit, so it does not provide the renormalizable 16_F 16_F 126_H
Majorana operator and does not preserve matter parity automatically.  It also
does not by itself implement missing-partner doublet-triplet splitting.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np

import exact_normalized_so10_yukawa_cgcs_v20 as yukawa


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V52_LOW_INDEX_SOURCE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V52_LOW_INDEX_SOURCE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v52_low_index_source_audit.py"

STATUS = (
    "V52_EXACT_RENORMALIZABLE_54_45_16_BAR16_SOURCE_WITNESS__"
    "F_AND_D_FLAT__SPIN10_ORBIT_RANK33_STABILIZER12__"
    "FULL_131_HESSIAN_RANK98_NULLITY33_AND_KERNEL_EQUALS_GAUGE_ORBIT__"
    "SOURCE_DYNKIN_INDEX24__PERTURBATIVE_SOURCE_REPLACEMENT__"
    "SEESAW_MATTER_PARITY_AND_MISSING_PARTNER_OBLIGATIONS_OPEN__"
    "NO_G2_CLAUSE_PROMOTED"
)

MODULAR_PRIME = 37
MODULAR_I = 6
S_DIM = 54
A_DIM = 45
SPIN_DIM = 16
TOTAL_DIM = 54 + 45 + 16 + 16
HESSIAN_DENOMINATOR = 20
ORBIT_DENOMINATOR = 10

LITERATURE = {
    "renormalizable_SM_vacuum": "https://arxiv.org/abs/hep-ph/0202278",
    "spinor_tensor_coupling": "https://arxiv.org/abs/hep-th/0109116",
    "perturbative_minimal_sector": "https://arxiv.org/abs/0707.3300",
    "lean_45_spinor_thresholds": "https://arxiv.org/abs/1904.11697",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    body = copy.deepcopy(dict(value))
    body.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _gaussian_integer(matrix: np.ndarray, *, label: str) -> np.ndarray:
    value = np.asarray(matrix, dtype=np.complex128)
    real = np.rint(value.real).astype(np.int64)
    imag = np.rint(value.imag).astype(np.int64)
    residual = max(
        float(np.max(np.abs(value.real - real), initial=0.0)),
        float(np.max(np.abs(value.imag - imag), initial=0.0)),
    )
    if residual > 1.0e-12:
        raise ArithmeticError(f"{label} left Gaussian-integer lattice: {residual}")
    return real.astype(np.complex128) + 1j * imag.astype(np.complex128)


def _max_abs(matrix: np.ndarray) -> float:
    return float(np.max(np.abs(matrix), initial=0.0))


def symmetric_traceless_basis() -> tuple[np.ndarray, ...]:
    """Integer basis for complex symmetric traceless 10 by 10 matrices."""
    result: list[np.ndarray] = []
    for index in range(9):
        matrix = np.zeros((10, 10), dtype=np.complex128)
        matrix[index, index] = 1
        matrix[9, 9] = -1
        result.append(matrix)
    for first in range(10):
        for second in range(first + 1, 10):
            matrix = np.zeros((10, 10), dtype=np.complex128)
            matrix[first, second] = 1
            matrix[second, first] = 1
            result.append(matrix)
    if len(result) != S_DIM:
        raise AssertionError(len(result))
    return tuple(result)


def antisymmetric_basis() -> tuple[np.ndarray, ...]:
    result: list[np.ndarray] = []
    for first in range(10):
        for second in range(first + 1, 10):
            matrix = np.zeros((10, 10), dtype=np.complex128)
            matrix[first, second] = 1
            matrix[second, first] = -1
            result.append(matrix)
    if len(result) != A_DIM:
        raise AssertionError(len(result))
    return tuple(result)


def spin_generators() -> tuple[np.ndarray, ...]:
    twice = yukawa.twice_spin_generators(-1)
    return tuple(
        np.asarray(twice[(first, second)], dtype=np.complex128) / 2
        for first in range(10)
        for second in range(first + 1, 10)
    )


def make_witness(b: float, r: float, v: float) -> dict[str, Any]:
    """Build an F-flat singlet witness from three nonzero rational inputs."""
    if b == r or v == 0:
        raise ValueError("need b != r and v != 0")
    s0 = np.diag([2] * 6 + [-3] * 4).astype(np.complex128)
    a_num = np.zeros((10, 10), dtype=np.complex128)
    for pair, coefficient in (
        ((0, 1), b), ((2, 3), b), ((4, 5), b),
        ((6, 7), r), ((8, 9), r),
    ):
        first, second = pair
        a_num[first, second] = coefficient
        a_num[second, first] = -coefficient
    c0 = np.zeros(SPIN_DIM, dtype=np.complex128)
    c0[15] = v
    b0 = c0.copy()
    m_a = (-6 * r - 4 * b) / (b - r)
    spinor_force = -(m_a + 4) * b
    eta = 2j * spinor_force / (v * v)
    m_c = -spinor_force * (3 * b + 2 * r) / (v * v)
    return {
        "mE": 1 - (b * b - r * r) / 10,
        "lambda": 1,
        "mA": m_a,
        "kappa": 1,
        "eta": eta,
        "mC": m_c,
        "S0": s0,
        "A_num": a_num,
        "A0": a_num,
        "C0": c0,
        "barC0": b0,
    }


def witness() -> dict[str, Any]:
    return make_witness(1, 3, 10)


def rho(matrix: np.ndarray) -> np.ndarray:
    result = np.zeros((SPIN_DIM, SPIN_DIM), dtype=np.complex128)
    generators = spin_generators()
    index = 0
    for first in range(10):
        for second in range(first + 1, 10):
            result += matrix[first, second] * generators[index]
            index += 1
    return result


def f_term_numerators() -> dict[str, np.ndarray]:
    """Return exact Gaussian-integer numerators for all 131 directional F terms."""
    data = witness()
    s0, a0 = data["S0"], data["A0"]
    c0, b0 = data["C0"], data["barC0"]
    s_values = []
    for variation in symmetric_traceless_basis():
        value = (
            data["mE"] * np.trace(s0 @ variation)
            + data["lambda"] * np.trace(s0 @ s0 @ variation)
            - 0.5 * data["kappa"] * np.trace(variation @ a0 @ a0)
        )
        s_values.append(value)
    a_values = []
    for variation in antisymmetric_basis():
        value = (
            -0.5 * data["mA"] * np.trace(a0 @ variation)
            -0.5 * data["kappa"] * np.trace(s0 @ (a0 @ variation + variation @ a0))
            + data["eta"] * (b0.T @ rho(variation) @ c0)
        )
        a_values.append(value)
    k0 = data["mC"] * np.eye(SPIN_DIM) + data["eta"] * rho(a0)
    c_values = b0.T @ k0
    b_values = k0 @ c0
    return {
        "S_F_x400": _gaussian_integer(400 * np.asarray(s_values), label="400 F_S"),
        "A_F_x400": _gaussian_integer(400 * np.asarray(a_values), label="400 F_A"),
        "C_F_x400": _gaussian_integer(400 * np.asarray(c_values), label="400 F_C"),
        "barC_F_x400": _gaussian_integer(400 * np.asarray(b_values), label="400 F_barC"),
    }


def d_moment_numerator() -> np.ndarray:
    """Compact-generator moment vector; all entries vanish exactly.

    Real S and A Cartan witnesses have zero moments in their real tensor
    representations.  The conjugate spinor acts by -T^T, cancelling C.
    We nevertheless compute all four contributions explicitly.
    """
    data = witness()
    s0, a0 = data["S0"], data["A0"]
    c0, b0 = data["C0"], data["barC0"]
    values = []
    for vector_t, spin_t in zip(antisymmetric_basis(), spin_generators(), strict=True):
        delta_s = vector_t @ s0 - s0 @ vector_t
        delta_a = vector_t @ a0 - a0 @ vector_t
        tensor_moment = np.trace(s0.conjugate().T @ delta_s) - 0.5 * np.trace(
            a0.conjugate().T @ delta_a
        )
        spin_moment = c0.conjugate().T @ spin_t @ c0
        conjugate_moment = b0.conjugate().T @ (-spin_t.T) @ b0
        values.append(tensor_moment + spin_moment + conjugate_moment)
    return _gaussian_integer(50 * np.asarray(values), label="50 D")


def hessian_numerator() -> np.ndarray:
    """Return 20 H as an exact 131 by 131 Gaussian-integer matrix."""
    data = witness()
    s0, a0 = data["S0"], data["A0"]
    c0, b0 = data["C0"], data["barC0"]
    s_basis = symmetric_traceless_basis()
    a_basis = antisymmetric_basis()
    t_basis = spin_generators()
    hessian = np.zeros((TOTAL_DIM, TOTAL_DIM), dtype=np.complex128)
    s_slice = slice(0, S_DIM)
    a_slice = slice(S_DIM, S_DIM + A_DIM)
    c_slice = slice(S_DIM + A_DIM, S_DIM + A_DIM + SPIN_DIM)
    b_slice = slice(S_DIM + A_DIM + SPIN_DIM, TOTAL_DIM)

    for row, left in enumerate(s_basis):
        for column, right in enumerate(s_basis):
            hessian[row, column] = data["mE"] * np.trace(left @ right) + data["lambda"] * np.trace(
                s0 @ (left @ right + right @ left)
            )

    for row, left in enumerate(a_basis):
        rr = S_DIM + row
        for column, right in enumerate(a_basis):
            cc = S_DIM + column
            hessian[rr, cc] = -0.5 * data["mA"] * np.trace(left @ right) - 0.5 * data["kappa"] * np.trace(
                s0 @ (left @ right + right @ left)
            )

    for row, left in enumerate(s_basis):
        for column, right in enumerate(a_basis):
            value = -0.5 * data["kappa"] * np.trace(left @ (a0 @ right + right @ a0))
            hessian[row, S_DIM + column] = value
            hessian[S_DIM + column, row] = value

    for column, spin_t in enumerate(t_basis):
        a_index = S_DIM + column
        ac = data["eta"] * (b0.T @ spin_t)
        ab = data["eta"] * (spin_t @ c0)
        hessian[a_index, c_slice] = ac
        hessian[c_slice, a_index] = ac
        hessian[a_index, b_slice] = ab
        hessian[b_slice, a_index] = ab

    k0 = data["mC"] * np.eye(SPIN_DIM) + data["eta"] * rho(a0)
    hessian[c_slice, b_slice] = k0.T
    hessian[b_slice, c_slice] = k0
    numerator = _gaussian_integer(
        HESSIAN_DENOMINATOR * hessian, label="5 Hessian"
    )
    if not np.array_equal(numerator, numerator.T):
        raise ArithmeticError("Hessian numerator is not complex symmetric")
    return numerator


def _symmetric_coordinates(matrix: np.ndarray) -> np.ndarray:
    values = np.empty(S_DIM, dtype=np.complex128)
    values[:9] = np.diag(matrix)[:9]
    cursor = 9
    for first in range(10):
        for second in range(first + 1, 10):
            values[cursor] = matrix[first, second]
            cursor += 1
    reconstructed = sum(
        (coefficient * basis for coefficient, basis in zip(values, symmetric_traceless_basis(), strict=True)),
        np.zeros((10, 10), dtype=np.complex128),
    )
    if _max_abs(reconstructed - matrix) > 1.0e-12:
        raise ArithmeticError("symmetric coordinate extraction failed")
    return values


def _antisymmetric_coordinates(matrix: np.ndarray) -> np.ndarray:
    return np.asarray(
        [matrix[first, second] for first in range(10) for second in range(first + 1, 10)],
        dtype=np.complex128,
    )


def orbit_numerator() -> np.ndarray:
    """Return 10 Q for the 45 Spin(10) tangent columns."""
    data = witness()
    s0, a0 = data["S0"], data["A0"]
    c0, b0 = data["C0"], data["barC0"]
    columns = []
    for vector_t, spin_t in zip(antisymmetric_basis(), spin_generators(), strict=True):
        delta_s = vector_t @ s0 - s0 @ vector_t
        delta_a = vector_t @ a0 - a0 @ vector_t
        delta_c = spin_t @ c0
        delta_b = -spin_t.T @ b0
        columns.append(
            np.concatenate(
                (_symmetric_coordinates(delta_s), _antisymmetric_coordinates(delta_a), delta_c, delta_b)
            )
        )
    return _gaussian_integer(
        ORBIT_DENOMINATOR * np.column_stack(columns), label="10 orbit"
    )


def _modular_matrix(matrix: np.ndarray) -> np.ndarray:
    integer = _gaussian_integer(matrix, label="modular input")
    real = np.rint(integer.real).astype(np.int64)
    imag = np.rint(integer.imag).astype(np.int64)
    return (real + MODULAR_I * imag) % MODULAR_PRIME


def modular_rank(matrix: np.ndarray, prime: int = MODULAR_PRIME) -> int:
    value = np.asarray(matrix, dtype=np.int64).copy() % prime
    rows, columns = value.shape
    rank = 0
    for column in range(columns):
        pivots = np.flatnonzero(value[rank:, column])
        if not len(pivots):
            continue
        pivot = rank + int(pivots[0])
        if pivot != rank:
            value[[rank, pivot]] = value[[pivot, rank]]
        value[rank] = value[rank] * pow(int(value[rank, column]), -1, prime) % prime
        for row in range(rows):
            if row != rank and value[row, column]:
                value[row] = (value[row] - value[row, column] * value[rank]) % prime
        rank += 1
        if rank == rows:
            break
    return rank


def gaussian_matrix_sha(matrix: np.ndarray) -> str:
    integer = _gaussian_integer(matrix, label="hash matrix")
    real = np.ascontiguousarray(np.rint(integer.real).astype("<i8"))
    imag = np.ascontiguousarray(np.rint(integer.imag).astype("<i8"))
    digest = hashlib.sha256()
    digest.update(canonical_bytes({"shape": list(integer.shape), "encoding": "gaussian-int64-real-then-imag"}))
    digest.update(b"\0")
    digest.update(real.tobytes(order="C"))
    digest.update(imag.tobytes(order="C"))
    return digest.hexdigest()


def build_report() -> dict[str, Any]:
    f_terms = f_term_numerators()
    d_terms = d_moment_numerator()
    hessian = hessian_numerator()
    orbit = orbit_numerator()
    orbit_rank = modular_rank(_modular_matrix(orbit))
    hessian_rank = modular_rank(_modular_matrix(hessian))
    ps_breaking_rank = modular_rank(_modular_matrix(orbit[:S_DIM]))
    spinor_breaking_rank = modular_rank(_modular_matrix(orbit[S_DIM + A_DIM :]))
    ps_spinor_intersection_rank = modular_rank(
        _modular_matrix(np.vstack((orbit[:S_DIM], orbit[S_DIM + A_DIM :])))
    )
    ward = hessian @ orbit
    ward_max = _max_abs(ward)

    source_index = 12 + 8 + 2 + 2
    three_family_index = 3 * 2
    electroweak_ten_index = 1
    c2_adjoint = 8
    beta_with_three_families_and_ten = (
        source_index + three_family_index + electroweak_ten_index - 3 * c2_adjoint
    )
    gut_coupling = 0.73
    landau_ratio = math.exp(
        8 * math.pi**2 / (beta_with_three_families_and_ten * gut_coupling**2)
    )

    all_f_zero = all(np.count_nonzero(value) == 0 for value in f_terms.values())
    payload: dict[str, Any] = {
        "schema": "susy-v52-low-index-source-audit-v1",
        "status": STATUS,
        "candidate": {
            "representations": ["54", "45", "16", "bar16"],
            "complex_coordinates": TOTAL_DIM,
            "superpotential": (
                "W=(mE/2)Tr(E^2)+(lambda/3)Tr(E^3)"
                "-(mA/4)Tr(A^2)-(kappa/2)Tr(E A^2)"
                "+barC^T[mC I+eta rho16(A)]C"
            ),
            "renormalizable": True,
            "literature": LITERATURE,
        },
        "exact_witness": {
            "parameters": {
                "mE": "9/5", "lambda": "1", "mA": "11", "kappa": "1",
                "eta": "-3*i/10", "mC": "27/20",
            },
            "E0_diagonal": [2] * 6 + [-3] * 4,
            "A0_nonzero_upper_entries": {
                "01": "1", "23": "1", "45": "1",
                "67": "3", "89": "3",
            },
            "C0": "10 times negative-chirality Clifford basis vector e15",
            "barC0": "10 times dual basis vector e15",
            "F_terms_all_zero": bool(all_f_zero),
            "F_nonzero_counts": {key: int(np.count_nonzero(value)) for key, value in f_terms.items()},
            "D_terms_all_zero": bool(np.count_nonzero(d_terms) == 0),
            "D_nonzero_count": int(np.count_nonzero(d_terms)),
        },
        "exact_local_geometry": {
            "orbit_shape": list(orbit.shape),
            "orbit_denominator": ORBIT_DENOMINATOR,
            "orbit_rank_mod37": orbit_rank,
            "stabilizer_dimension": 45 - orbit_rank,
            "unbroken_group": "SU(3)c x SU(2)L x U(1)Y (Lie-algebra dimension 12)",
            "E54_orbit_rank": ps_breaking_rank,
            "E54_stabilizer": "Spin(6)xSpin(4), dimension 21",
            "spinor_pair_orbit_rank": spinor_breaking_rank,
            "spinor_pair_stabilizer": "SU(5), dimension 24",
            "E54_plus_spinor_pair_orbit_rank": ps_spinor_intersection_rank,
            "intersection_identification": "[Spin(6)xSpin(4)] intersection SU(5) = SU(3)c x SU(2)L x U(1)Y",
            "hessian_shape": list(hessian.shape),
            "hessian_denominator": HESSIAN_DENOMINATOR,
            "hessian_rank_mod37": hessian_rank,
            "hessian_nullity_mod37": TOTAL_DIM - hessian_rank,
            "ward_product_exactly_zero": bool(ward_max == 0),
            "ward_product_max_abs": ward_max,
            "kernel_equals_broken_gauge_orbit": bool(
                orbit_rank == 33 and hessian_rank == 98 and ward_max == 0
            ),
            "exact_rank_lemma": (
                "mod-37 ranks lower-bound ranks over Q(i); exact H*Q=0 gives "
                "rank(H)+rank(Q)<=131. The lower bounds 98+33=131 saturate "
                "this inequality, proving both characteristic-zero ranks and ker(H)=im(Q)."
            ),
            "orbit_numerator_sha256": gaussian_matrix_sha(orbit),
            "hessian_numerator_sha256": gaussian_matrix_sha(hessian),
        },
        "perturbativity": {
            "dynkin_convention": "T(10)=1, C2(45)=8",
            "indices": {"T54": 12, "T45": 8, "T16": 2, "Tbar16": 2},
            "source_sum_T": source_index,
            "v51_Higgs_source_T": 126,
            "Higgs_source_reduction_factor_vs_v51": 126 / source_index,
            "v51_whole_source_site_T_including_link_inventory": 316,
            "architectural_site_to_lean_source_ratio_apples_oranges": 316 / source_index,
            "one_loop_b_source_only": source_index - 3 * c2_adjoint,
            "one_loop_b_with_three_16_families_and_one_10H": beta_with_three_families_and_ten,
            "g_at_matching_witness": gut_coupling,
            "landau_pole_over_matching_scale_if_b_positive": landau_ratio,
            "above_100x_matching_scale": bool(landau_ratio > 100),
            "scope_caveat": "does not include the separate moose/link and mediator field indices",
        },
        "anomaly_ledger": {
            "Spin10_local_cubic": "zero; Spin(10) has no perturbative cubic gauge anomaly and 16+bar16 is vectorlike",
            "Spin10_global": "no four-dimensional Witten anomaly for Spin(10)",
            "optional_U1F_assignment": {"54": 0, "45": 0, "16": 1, "bar16": -1},
            "optional_U1F_Spin10_squared": 2 - 2,
            "optional_gravity_squared_U1F": 16 - 16,
            "optional_U1F_cubed": 16 - 16,
            "integration_caveat": (
                "with only this pair, an independently gauged U(1)F leaves one diagonal "
                "combination with the Spin(10) singlet Cartan unbroken; a charged singlet "
                "or other sector is required to reproduce a fully broken V50 U(1)F"
            ),
        },
        "phenomenology_fail_closed": {
            "full_Higgs_Hessian": "absent; the exact rank-98 result covers only the 54+45+16+bar16 GUT-breaking source",
            "renormalizable_type_I_seesaw": "absent",
            "reason": "16_F x 16_F contains 10+120+126, not a source 16; Majorana mass needs a dimension-five operator or a 126bar",
            "matter_parity": "not automatic because the 16-Higgs VEV has odd B-L",
            "missing_partner": "not supplied by 54+45+16+bar16 alone",
            "doublet_triplet": "requires a separate audited 10/16 Higgs mass matrix and proton-decay analysis",
            "flavour_fit": "absent; no charged-fermion or neutrino Yukawa fit is claimed",
            "threshold_unification": "source beta coefficient only; split multiplet thresholds have not been matched",
            "possible_repair": "vectorlike singlet fermion mediators can UV-complete (16_F bar16_H)^2/M, but their flavor, parity, and matching are not audited here",
        },
        "gate_effect": {
            "G2": "OPEN",
            "clause_promotions": [],
            "reason": "new action is not yet matched to the frozen V50 action and does not provide final C5/C7 Wilson data",
            "scientific_verdict": "exact viable low-index source replacement; not a complete theory",
        },
        "source_manifest": {
            "source_files": {
                name: sha256_file(ROOT / name)
                for name in (
                    "susy_v52_low_index_source_audit.py",
                    "test_susy_v52_low_index_source_audit.py",
                    "exact_normalized_so10_yukawa_cgcs_v20.py",
                )
            }
        },
    }
    payload["core_sha256"] = canonical_sha(payload)
    return payload


def render_markdown(report: Mapping[str, Any]) -> str:
    geometry = report["exact_local_geometry"]
    perturbativity = report["perturbativity"]
    return f"""# SUSY V52 low-index source audit

Status: `{report['status']}`

Core SHA-256: `{report['core_sha256']}`

## Outcome

V52 contains a genuinely lean, renormalizable source candidate:
`54 + 45 + 16 + bar16`, with only 131 complex source coordinates and total
source Dynkin index 24.  The explicit rational witness in the JSON certificate
is exactly F-flat and D-flat.  Its Spin(10) orbit has rank
`{geometry['orbit_rank_mod37']}`, leaving the 12-dimensional Standard-Model
stabilizer.  The complete 131 by 131 holomorphic Hessian has rank
`{geometry['hessian_rank_mod37']}` and nullity
`{geometry['hessian_nullity_mod37']}`.  Its kernel is exactly the broken-gauge
orbit; there is no additional local chiral source modulus.

This certifies a source-sector replacement, not a complete theory and not a G2
closure.

## Exact action and witness

```text
W = (mE/2) Tr(E^2) + (lambda/3) Tr(E^3)
    - (mA/4) Tr(A^2) - (kappa/2) Tr(E A^2)
    + barC^T [mC I + eta rho16(A)] C

mE=9/5, lambda=kappa=1, mA=11, eta=-3 i/10, mC=27/20
E0 = diag(2,2,2,2,2,2,-3,-3,-3,-3)
A0 = J01+J23+J45+3 J67+3 J89
C0=barC0=10 e15
```

All 131 directional F terms and all 45 compact D moments vanish.  In the
repository-locked Clifford basis, `20 H` and `10 Q` are Gaussian-integer
matrices.  The exact Ward product `(20 H)(10 Q)` vanishes entry by entry.
Reduction modulo 37 with `i -> 6` gives lower bounds 98 and 33 for the two
characteristic-zero ranks.  Exact `H Q=0` gives the opposite joint bound
`rank(H)+rank(Q)<=131`; saturation proves both ranks and that the kernel
contains nothing else.

## Perturbativity improvement

The Higgs-source index falls from V51's 126 to
`{perturbativity['source_sum_T']}`, a factor of
`{perturbativity['Higgs_source_reduction_factor_vs_v51']:.3f}`.  V51's 316 is
a whole source-site inventory including link fields and is therefore only an
apples/oranges architectural comparison.  The lean source-only one-loop
coefficient is zero.  Including three matter 16s and one electroweak 10 gives
`b={perturbativity['one_loop_b_with_three_16_families_and_one_10H']}`;
at `g=0.73` its formal one-loop pole is
`{perturbativity['landau_pole_over_matching_scale_if_b_positive']:.6g}` times
the matching scale.  This removes the source-side perturbativity failure, but
does not include any separate link/moose or mediator inventory.

## Phenomenological cost

Replacing `126+bar126` by `16+bar16` removes the renormalizable right-handed
Majorana operator.  A dimension-five seesaw completion is required.  The odd
`B-L` spinor VEV also does not leave matter parity automatic.  Finally, this
source set alone is not a missing-partner mechanism: the electroweak 10/spinor
doublet and color-triplet mass matrices, proton decay, and threshold matching
still need an explicit audit.

## Primary-source anchors

The general renormalizable invariant set and generic Standard-Model branch are
described in [Buccella and Savoy](https://arxiv.org/abs/hep-ph/0202278).
The explicit `bar16 x 16 x 45` tensor channel is derived in
[Nath and Syed](https://arxiv.org/abs/hep-th/0109116).  The motivation and
running advantage of low-index SUSY SO(10) Higgs sectors are discussed by
[Wiesenfeldt and Willenbrock](https://arxiv.org/abs/0707.3300); a later
threshold study of the lean adjoint-spinor route is
[Haba, Mimura and Yamada](https://arxiv.org/abs/1904.11697).

## Gate decision

No G2 clause is promoted.  This is a new action and has not been matched to the
frozen V50 boundary action or its final C5/C7 Wilson array.  The narrow result
is stronger and useful: an exact, locally isolated, perturbative source
replacement exists, and the remaining obstruction has moved from source
geometry to seesaw/parity, doublet-triplet, link, and matching physics.
"""


def validate_report(report: Mapping[str, Any]) -> None:
    if canonical_sha(report) != report.get("core_sha256"):
        raise AssertionError("core hash mismatch")
    witness_report = report["exact_witness"]
    geometry = report["exact_local_geometry"]
    if MODULAR_I * MODULAR_I % MODULAR_PRIME != MODULAR_PRIME - 1:
        raise AssertionError("modular i is not a square root of -1")
    if not witness_report["F_terms_all_zero"] or not witness_report["D_terms_all_zero"]:
        raise AssertionError("witness is not supersymmetric")
    if geometry["orbit_rank_mod37"] != 33 or geometry["stabilizer_dimension"] != 12:
        raise AssertionError("wrong little group rank")
    if (
        geometry["E54_orbit_rank"],
        geometry["spinor_pair_orbit_rank"],
        geometry["E54_plus_spinor_pair_orbit_rank"],
    ) != (24, 21, 33):
        raise AssertionError("PS/SU5 intersection ranks failed")
    if geometry["hessian_rank_mod37"] != 98 or geometry["hessian_nullity_mod37"] != 33:
        raise AssertionError("wrong Hessian rank")
    if not geometry["ward_product_exactly_zero"] or not geometry["kernel_equals_broken_gauge_orbit"]:
        raise AssertionError("Ward/kernel certificate failed")
    if report["perturbativity"]["source_sum_T"] != 24:
        raise AssertionError("wrong source Dynkin index")
    if report["gate_effect"]["clause_promotions"]:
        raise AssertionError("fail-closed audit cannot promote G2")


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> dict[str, Any]:
    report = build_report()
    validate_report(report)
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise AssertionError("generated artifacts are missing")
    disk = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if disk != report:
        raise AssertionError("JSON artifact is stale")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise AssertionError("Markdown artifact is stale")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        report = write_artifacts()
    elif args.check:
        report = check_artifacts()
    else:
        report = build_report()
        validate_report(report)
    print(report["status"])
    print(report["core_sha256"])


if __name__ == "__main__":
    main()
