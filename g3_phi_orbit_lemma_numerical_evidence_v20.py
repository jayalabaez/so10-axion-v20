#!/usr/bin/env python3
"""Independent numerical evidence for the signed two-orbit Phi lemma (G3, v20).

Statement under test (the signed form; the literal one-orbit form is refuted
in ``exact_gauged_u1x_g3_su5_phi_orbit_lemma_v20.py``):

    every unit real four-form Phi on R^10 with
        Pi_54(Phi (x) Phi) = 0   and   Pi_4125(Phi (x) Phi) = 0
    lies in SO(10).F or in SO(10).(-F),   F = omega^omega / |omega^omega|.

Independence.  Only the standard library, numpy and scipy are imported.  The
module rebuilds from scratch, in the orthonormal component basis of
Lambda^4 R^10 (|Phi|^2 = sum_{i<j<k<l} Phi_ijkl^2):

* the so(10) generators T_ab = e_a e_b^T - e_b e_a^T acting on Lambda^4 as
  derivations (signed partial permutations, 112 nonzeros each);
* the pair operator K = sum_{a<b} T_ab (x) T_ab, K(W) = sum T W T^T, which is
  C2(210) - C2(R)/2 on the channel R;
* the decomposition of Sym^2(210) by a Weyl-character computation
  (Racah-Speiser reflection into the dominant chamber), confirmed by Lanczos
  on K and by trace identities of the sparse operator;
* the Casimir projectors Pi_R as Lagrange-interpolation polynomials in K;
* the 45x45 pair matrix A(Phi) and I3(Phi) = 8 Tr A(Phi)^3.

Evidence collected (none of it is a proof):

1. multistart minimisation of f = ||Pi_54(PhiPhi)||^2 + ||Pi_4125(PhiPhi)||^2
   on the unit sphere, with every endpoint classified by its A-spectrum and by
   an explicit orbit witness (the complex structure rebuilt from A(Phi));
2. the adversarial profile g(t) = min{f : |Phi| = 1, I3(Phi) = t}, together
   with an exact second-order analysis of f and I3 at F that fixes the
   small-delta law;
3. multistart maximisation of I3, showing that F does not maximise it.

The optimisers use an exact contraction formula for I_54 and I_4125 in the
four O(10)-invariant quartics J0..J3; that identity is re-verified against
the Casimir projectors (values and gradients) on every run, and every
multistart endpoint is polished and re-evaluated with the projectors.

The module is fail-closed.  It never claims the lemma is proved, never closes
G3, and never validates or excludes the whole model.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy import sparse
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "G3_PHI_ORBIT_LEMMA_NUMERICAL_EVIDENCE_V20.json"
OUT_MD = ROOT / "G3_PHI_ORBIT_LEMMA_NUMERICAL_EVIDENCE_V20.md"

STATUS_SUPPORTS = (
    "PHI_ORBIT_LEMMA_NUMERICAL_EVIDENCE_SUPPORTS_SIGNED_TWO_ORBIT_STATEMENT__PROOF_OPEN"
)
STATUS_FAILED = "PHI_ORBIT_LEMMA_NUMERICAL_EVIDENCE_FAILED"
STATUS_COUNTEREXAMPLE = "PHI_ORBIT_LEMMA_NUMERICAL_EVIDENCE_COUNTEREXAMPLE_CANDIDATE_FOUND"

DIM = 10
FOUR = tuple(itertools.combinations(range(DIM), 4))
FOUR_INDEX = {subset: position for position, subset in enumerate(FOUR)}
PAIRS = tuple(itertools.combinations(range(DIM), 2))
PAIR_INDEX = {pair: position for position, pair in enumerate(PAIRS)}
N210 = len(FOUR)
N45 = len(PAIRS)
SYM2_DIMENSION = N210 * (N210 + 1) // 2
ALT2_DIMENSION = N210 * (N210 - 1) // 2
RHO = (4, 3, 2, 1, 0)
HIGHEST_WEIGHTS = {
    "1": (0, 0, 0, 0, 0),
    "54": (2, 0, 0, 0, 0),
    "210": (1, 1, 1, 1, 0),
    "4125": (2, 2, 2, 0, 0),
}

I3_F_EXACT = 8.0 * 60.0 / 10.0**1.5
I3_CAYLEY_EXACT = 8.0 * 168.0 / 14.0**1.5

SEEDS = {
    "projector_sanity": 2102,
    "lanczos": 22155,
    "contraction_fit": 2016,
    "contraction_validation": 288,
    "gradient_check": 35,
    "multistart": 1500210,
    "profile": 4125054,
    "cubic_maximum": 1680014,
}
FULL_CONFIG = {
    "mode": "full",
    "multistart_starts": 150,
    "profile_delta_fractions": (
        0.0025, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5,
        0.6, 0.7, 0.8, 0.9, 1.0, 1.5,
    ),
    "profile_random_starts": 4,
    "profile_slsqp_cross_check": True,
    "cubic_starts": 60,
}
QUICK_CONFIG = {
    "mode": "quick",
    "multistart_starts": 5,
    "profile_delta_fractions": (0.0025, 0.005, 0.01, 0.02, 0.5, 1.0),
    "profile_random_starts": 1,
    "profile_slsqp_cross_check": False,
    "cubic_starts": 8,
}

ZERO_TOL = 1.0e-10
SPECTRAL_TOL = 1.0e-3
WITNESS_TOL = 1.0e-3
PROJECTOR_ZERO_TOL = 1.0e-12
FEASIBILITY_TOL = 1.0e-9
SLOPE_REL_TOL = 0.02
# I3 is quadratic in the distance d to the orbit along the excess directions
# (curvature 3*I3(F) ~ 45.5), so d <= WITNESS_TOL allows |I3 -+ I3(F)| ~ 1e-4.
I3_ENDPOINT_TOL = 1.0e-4

FAST_OPTIONS = {"maxiter": 3000, "maxcor": 30, "ftol": 0.0, "gtol": 0.0, "maxls": 50}
POLISH_OPTIONS = {"maxiter": 150, "maxcor": 30, "ftol": 0.0, "gtol": 0.0, "maxls": 50}
AL_INNER_OPTIONS = {"maxiter": 3000, "maxcor": 30, "ftol": 1.0e-15, "gtol": 1.0e-13, "maxls": 50}
CUBIC_OPTIONS = {"maxiter": 5000, "maxcor": 30, "ftol": 1.0e-16, "gtol": 1.0e-12, "maxls": 50}

CLAIMS = {
    "multistart_starts": 150,
    "multistart_zeros": 150,
    "multistart_plus": 70,
    "multistart_minus": 80,
    "profile_quadratic_coefficient": 1.9e-3,
    "profile_g_at_zero": 0.052,
    "cubic_maximum": 25.66,
}

# I_R = sum_i c_i J_i with J0=|Phi|^4, J1=sum_ab M_ab^2 (M_ab=sum_cde Phi_acde Phi_bcde),
# J2=sum_abcd P_abcd^2 (P_abcd=sum_ef Phi_abef Phi_cdef), J3=sum_abcd P_abcd P_acbd.
CONTRACTION_COEFFICIENTS = {
    "54": (Fraction(-1, 35), Fraction(1, 2016), Fraction(0), Fraction(0)),
    "4125": (Fraction(-1, 14), Fraction(13, 2016), Fraction(-1, 144), Fraction(1, 288)),
}
# Repository slice identities on Phi = a A + b B + c C, as Gram matrices in the
# monomial order (a^2, ab, ac, b^2, bc, c^2): Gram = scale * v v^T.
SLICE_MONOMIALS = ("a2", "a_b", "a_c", "b2", "b_c", "c2")
REPO_SLICE_IDENTITIES = {
    "54": {"vector": (3, 0, 0, -3, 0, 4), "scale": Fraction(1, 35),
           "formula": "(3*a^2-3*b^2+4*c^2)^2/35"},
    "4125": {"vector": (1, 0, 0, -1, 0, -1), "scale": Fraction(80, 21),
             "formula": "80*(a^2-b^2-c^2)^2/21"},
}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _sig(value: float, digits: int = 6) -> float:
    """Round to ``digits`` significant digits (stable JSON output)."""
    value = float(value)
    if value == 0.0 or not math.isfinite(value):
        return 0.0 if value == 0.0 else value
    return float(f"{value:.{digits}g}")


def _bound(value: float) -> float:
    """Power-of-ten upper bound for noise-level diagnostics (stable JSON)."""
    value = abs(float(value))
    if value == 0.0 or not math.isfinite(value):
        return value
    return float(f"1e{math.ceil(math.log10(value))}")


def _value_or_bound(value: float, digits: int = 6, floor: float = 1.0e-8) -> float:
    return _sig(value, digits) if abs(value) > floor else _bound(value)


def _round_abs(value: float, decimals: int = 12) -> float:
    rounded = round(float(value), decimals)
    return 0.0 if rounded == 0.0 else rounded


def _perm_sign(sequence: Any) -> int:
    items = list(sequence)
    sign = 1
    for left in range(len(items)):
        for right in range(left + 1, len(items)):
            if items[left] > items[right]:
                sign = -sign
    return sign


def _unit(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def _normalized(
    function: Callable[[np.ndarray], tuple[float, np.ndarray]],
    vector: np.ndarray,
    degree: int,
) -> tuple[float, np.ndarray]:
    """Value and gradient of x -> h(x/|x|) for h homogeneous of ``degree``."""
    value, gradient = function(vector)
    norm_squared = float(vector @ vector)
    scale = norm_squared ** (0.5 * degree)
    return (
        value / scale,
        gradient / scale - degree * value * vector / (scale * norm_squared),
    )


def _grouped_spectrum(values: np.ndarray, scale: float, tol: float = 1.0e-6) -> list[list[float]]:
    groups: list[list[float]] = []
    for value in sorted(float(v) * scale for v in values):
        if abs(value) <= tol:
            value = 0.0
        if groups and abs(value - groups[-1][0]) <= tol:
            groups[-1][1] += 1
        else:
            groups.append([value, 1])
    return [[_sig(value, 6), int(count)] for value, count in groups]


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


# ---------------------------------------------------------------------------
# so(10) on Lambda^4 R^10 and the pair operator K
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def generator_matrices() -> tuple[sparse.csr_matrix, ...]:
    """T_ab (a<b) on Lambda^4, from T_ab e_b = e_a and T_ab e_a = -e_b on R^10."""
    matrices = []
    for a, b in PAIRS:
        rows: list[int] = []
        columns: list[int] = []
        values: list[float] = []
        for column, subset in enumerate(FOUR):
            if (a in subset) == (b in subset):
                continue
            old, new, sign = (b, a, 1) if b in subset else (a, b, -1)
            image = [new if index == old else index for index in subset]
            rows.append(FOUR_INDEX[tuple(sorted(image))])
            columns.append(column)
            values.append(float(sign * _perm_sign(image)))
        matrices.append(
            sparse.csr_matrix((values, (rows, columns)), shape=(N210, N210))
        )
    return tuple(matrices)


def derivation_matrix(matrix: np.ndarray) -> np.ndarray:
    """A gl(10) matrix acting on Lambda^4 as a derivation (dense 210x210)."""
    result = np.zeros((N210, N210))
    for column, subset in enumerate(FOUR):
        for position, index in enumerate(subset):
            for target in range(DIM):
                coefficient = matrix[target, index]
                if coefficient == 0.0 or (target != index and target in subset):
                    continue
                image = list(subset)
                image[position] = target
                result[FOUR_INDEX[tuple(sorted(image))], column] += (
                    coefficient * _perm_sign(image)
                )
    return result


def _vector_generator(a: int, b: int) -> np.ndarray:
    generator = np.zeros((DIM, DIM))
    generator[a, b] = 1.0
    generator[b, a] = -1.0
    return generator


@lru_cache(maxsize=1)
def pair_operator() -> sparse.csr_matrix:
    """K = sum_g T_g (x) T_g on row-major vec(W): K vec(W) = vec(sum T W T^T)."""
    total = None
    for generator in generator_matrices():
        term = sparse.kron(generator, generator, format="csr")
        total = term if total is None else total + term
    return total.tocsr()


def apply_pair_operator(matrix: np.ndarray) -> np.ndarray:
    return (pair_operator() @ np.ascontiguousarray(matrix).ravel()).reshape(N210, N210)


@lru_cache(maxsize=1)
def generator_certificate() -> dict[str, Any]:
    matrices = generator_matrices()
    vector = [_vector_generator(a, b) for a, b in PAIRS]
    nonzeros = sorted({int(matrix.nnz) for matrix in matrices})
    antisymmetry = max(float(abs(matrix + matrix.T).max()) for matrix in matrices)
    entries = sorted({float(abs(value)) for matrix in matrices for value in matrix.data})
    derivation_defect = max(
        float(np.max(np.abs(derivation_matrix(vector[k]) - matrices[k].toarray())))
        for k in range(N45)
    )
    casimir = sparse.csr_matrix((N210, N210))
    for matrix in matrices:
        casimir = casimir - matrix @ matrix
    casimir_defect = float(abs(casimir - 24.0 * sparse.identity(N210, format="csr")).max())
    commutator_defect = 0.0
    for left in range(N45):
        for right in range(left + 1, N45):
            vector_commutator = vector[left] @ vector[right] - vector[right] @ vector[left]
            commutator = matrices[left] @ matrices[right] - matrices[right] @ matrices[left]
            for k, (a, b) in enumerate(PAIRS):
                if vector_commutator[a, b] != 0.0:
                    commutator = commutator - vector_commutator[a, b] * matrices[k]
            if commutator.nnz:
                commutator_defect = max(commutator_defect, float(abs(commutator).max()))
    operator = pair_operator()
    return {
        "number_of_generators": len(matrices),
        "nonzeros_per_generator": nonzeros,
        "absolute_entries": entries,
        "max_antisymmetry_defect": antisymmetry,
        "max_gl10_derivation_defect": derivation_defect,
        "max_so10_commutation_defect": commutator_defect,
        "casimir_minus_sum_T2_defect_vs_24": casimir_defect,
        "pair_operator_shape": list(operator.shape),
        "pair_operator_nonzeros": int(operator.nnz),
    }


# ---------------------------------------------------------------------------
# Sym^2(210) by characters (weights in the orthonormal e_1..e_5 basis of D5)
# ---------------------------------------------------------------------------
def _add(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(left, right))


@lru_cache(maxsize=1)
def vector_weights() -> tuple[tuple[int, ...], ...]:
    weights = []
    for i in range(5):
        for sign in (1, -1):
            weight = [0] * 5
            weight[i] = sign
            weights.append(tuple(weight))
    return tuple(weights)


@lru_cache(maxsize=1)
def lambda4_weights() -> tuple[tuple[int, ...], ...]:
    weights = vector_weights()
    return tuple(
        tuple(sum(weights[k][j] for k in combo) for j in range(5))
        for combo in itertools.combinations(range(DIM), 4)
    )


def _dominant_conjugate(weight: tuple[int, ...]) -> tuple[tuple[int, ...], int] | None:
    """Reflect ``weight`` into the closed D5 chamber x1>=...>=x4>=|x5|.

    Returns the conjugate and det(w) of the Weyl element (signed permutations
    with an even number of sign changes, so det(w) is the permutation sign),
    or None when the weight is fixed by a reflection.
    """
    absolute = [abs(value) for value in weight]
    if len(set(absolute)) < 5:
        return None
    order = sorted(range(5), key=lambda i: -absolute[i])
    dominant = [absolute[i] for i in order]
    if sum(1 for value in weight if value < 0) % 2 == 1 and dominant[4] != 0:
        dominant[4] = -dominant[4]
    return tuple(dominant), _perm_sign(order)


def decompose_character(character: Counter) -> dict[tuple[int, ...], int]:
    """Irreducible multiplicities of a W-invariant formal character.

    c_lambda = sum_nu m_nu det(w_nu) over weights nu with w_nu(nu+rho) = lambda+rho.
    """
    coefficients: Counter = Counter()
    for weight, multiplicity in character.items():
        result = _dominant_conjugate(_add(weight, RHO))
        if result is None:
            continue
        dominant, sign = result
        coefficients[tuple(d - r for d, r in zip(dominant, RHO))] += sign * multiplicity
    return {weight: count for weight, count in coefficients.items() if count != 0}


def weyl_dimension(weight: tuple[int, ...]) -> int:
    shifted = [w + r for w, r in zip(weight, RHO)]
    numerator = 1
    denominator = 1
    for i in range(5):
        for j in range(i + 1, 5):
            numerator *= (shifted[i] - shifted[j]) * (shifted[i] + shifted[j])
            denominator *= (RHO[i] - RHO[j]) * (RHO[i] + RHO[j])
    if numerator % denominator:
        raise ArithmeticError("non-integral Weyl dimension")
    return numerator // denominator


def casimir_c2(weight: tuple[int, ...]) -> int:
    return sum(w * (w + 2 * r) for w, r in zip(weight, RHO))


def pair_eigenvalue(weight: tuple[int, ...]) -> Fraction:
    """K on channel R: C2(210) - C2(R)/2."""
    return Fraction(casimir_c2(HIGHEST_WEIGHTS["210"])) - Fraction(casimir_c2(weight), 2)


def _irrep_label(weight: tuple[int, ...]) -> str:
    return f"{weyl_dimension(weight)}{'bar' if weight[4] < 0 else ''}"


def _irrep_rows(decomposition: dict[tuple[int, ...], int]) -> list[dict[str, Any]]:
    rows = []
    for weight, multiplicity in sorted(
        decomposition.items(), key=lambda item: (-pair_eigenvalue(item[0]), item[0])
    ):
        rows.append(
            {
                "irrep": _irrep_label(weight),
                "highest_weight_orthonormal": list(weight),
                "dimension": weyl_dimension(weight),
                "multiplicity": multiplicity,
                "C2": casimir_c2(weight),
                "K_eigenvalue": str(pair_eigenvalue(weight)),
            }
        )
    return rows


@lru_cache(maxsize=1)
def representation_certificate() -> dict[str, Any]:
    weights = lambda4_weights()
    symmetric: Counter = Counter()
    antisymmetric: Counter = Counter()
    for i in range(N210):
        symmetric[_add(weights[i], weights[i])] += 1
        for j in range(i + 1, N210):
            total = _add(weights[i], weights[j])
            symmetric[total] += 1
            antisymmetric[total] += 1
    sym2 = decompose_character(symmetric)
    alt2 = decompose_character(antisymmetric)
    vectors = vector_weights()
    vector_square = decompose_character(
        Counter(_add(x, y) for x in vectors for y in vectors)
    )
    lambda4 = decompose_character(Counter(weights))
    eigenvalue_owners: dict[Fraction, list[str]] = {}
    for weight in sym2:
        eigenvalue_owners.setdefault(pair_eigenvalue(weight), []).append(_irrep_label(weight))
    spectrum = sorted(eigenvalue_owners, reverse=True)
    return {
        "sym2": sym2,
        "alt2": alt2,
        "sym2_rows": _irrep_rows(sym2),
        "alt2_rows": _irrep_rows(alt2),
        "sym2_dimension_sum": sum(weyl_dimension(w) * m for w, m in sym2.items()),
        "alt2_dimension_sum": sum(weyl_dimension(w) * m for w, m in alt2.items()),
        "sym2_all_multiplicities_positive": all(m > 0 for m in sym2.values()),
        "alt2_all_multiplicities_positive": all(m > 0 for m in alt2.values()),
        "lambda4_decomposition": {str(list(w)): m for w, m in lambda4.items()},
        "vector_square_decomposition": {
            _irrep_label(w): m for w, m in sorted(vector_square.items())
        },
        "sym2_distinct_K_eigenvalues": [str(value) for value in spectrum],
        "sym2_K_eigenvalue_owners": {
            str(value): sorted(owners) for value, owners in sorted(eigenvalue_owners.items(), reverse=True)
        },
        "K_singlet": str(pair_eigenvalue(HIGHEST_WEIGHTS["1"])),
        "K_54": str(pair_eigenvalue(HIGHEST_WEIGHTS["54"])),
        "K_4125": str(pair_eigenvalue(HIGHEST_WEIGHTS["4125"])),
        "C2_210": casimir_c2(HIGHEST_WEIGHTS["210"]),
        "dimension_54": weyl_dimension(HIGHEST_WEIGHTS["54"]),
        "dimension_4125": weyl_dimension(HIGHEST_WEIGHTS["4125"]),
    }


@lru_cache(maxsize=1)
def sym2_spectrum() -> tuple[int, ...]:
    values = [Fraction(value) for value in representation_certificate()["sym2_distinct_K_eigenvalues"]]
    if any(value.denominator != 1 for value in values):
        raise ArithmeticError("non-integral K eigenvalue on Sym^2(210)")
    return tuple(int(value) for value in values)


def _channel_eigenvalue(channel: str) -> int:
    value = pair_eigenvalue(HIGHEST_WEIGHTS[channel])
    if value.denominator != 1:
        raise ArithmeticError("non-integral channel eigenvalue")
    return int(value)


def _random_symmetric(seed: int) -> np.ndarray:
    matrix = np.random.default_rng(seed).standard_normal((N210, N210))
    matrix = matrix + matrix.T
    return matrix / np.linalg.norm(matrix)


@lru_cache(maxsize=1)
def lanczos_certificate() -> dict[str, Any]:
    """Krylov space of K on a random symmetric input (full reorthogonalisation)."""
    basis = [_random_symmetric(SEEDS["lanczos"])]
    images: list[np.ndarray] = []
    residual = math.inf
    for _ in range(24):
        image = apply_pair_operator(basis[-1])
        images.append(image)
        remainder = image.copy()
        for _ in range(2):
            for vector in basis:
                remainder -= np.sum(vector * remainder) * vector
        residual = float(np.linalg.norm(remainder)) / 24.0
        if residual < 1.0e-9:
            break
        basis.append(remainder / np.linalg.norm(remainder))
    size = len(basis)
    rayleigh = np.array(
        [[np.sum(basis[i] * images[j]) for j in range(size)] for i in range(size)]
    )
    ritz = np.sort(np.linalg.eigvalsh(0.5 * (rayleigh + rayleigh.T)))[::-1]
    predicted = np.asarray(sym2_spectrum(), dtype=float)
    match = size == len(predicted) and float(np.max(np.abs(ritz - predicted))) < 1.0e-8
    return {
        "krylov_dimension": size,
        "terminal_relative_residual": _bound(residual),
        "ritz_values": [_round_abs(value, 9) for value in ritz],
        "character_prediction": [int(value) for value in predicted],
        "max_abs_ritz_minus_prediction": _bound(
            float(np.max(np.abs(ritz - predicted))) if size == len(predicted) else math.inf
        ),
        "matches_character_prediction": bool(match),
    }


@lru_cache(maxsize=1)
def trace_certificate() -> dict[str, Any]:
    """tr(K^k) on Sym^2 and Lambda^2 (k=0,1,2) from the sparse operator vs characters."""
    operator = pair_operator()
    index = np.arange(N210 * N210)
    swap = (index % N210) * N210 + index // N210
    trace_k = float(operator.diagonal().sum())
    trace_k_swap = float(np.asarray(operator[index, swap]).ravel().sum())
    trace_k2 = float(operator.multiply(operator.T).sum())
    trace_k2_swap = float(operator.multiply(operator[:, swap].T).sum())
    measured = {
        "sym2": [SYM2_DIMENSION, 0.5 * (trace_k + trace_k_swap), 0.5 * (trace_k2 + trace_k2_swap)],
        "alt2": [ALT2_DIMENSION, 0.5 * (trace_k - trace_k_swap), 0.5 * (trace_k2 - trace_k2_swap)],
    }
    representation = representation_certificate()
    predicted = {}
    for name in ("sym2", "alt2"):
        predicted[name] = [
            float(
                sum(
                    weyl_dimension(w) * m * pair_eigenvalue(w) ** power
                    for w, m in representation[name].items()
                )
            )
            for power in range(3)
        ]
    defect = max(
        abs(measured[name][k] - predicted[name][k]) for name in measured for k in range(3)
    )
    return {
        "measured_traces_K0_K1_K2": {name: [_sig(v, 12) for v in values] for name, values in measured.items()},
        "character_traces_K0_K1_K2": {name: [_sig(v, 12) for v in values] for name, values in predicted.items()},
        "max_abs_defect": _bound(defect),
        "consistent": bool(defect < 1.0e-6),
    }


# ---------------------------------------------------------------------------
# Casimir projectors (Lagrange interpolation in K over the Sym^2 spectrum)
# ---------------------------------------------------------------------------
def _interpolation_denominator(target: int) -> float:
    return float(np.prod([target - mu for mu in sym2_spectrum() if mu != target]))


def spectral_projector(matrix: np.ndarray, target: int) -> np.ndarray:
    result = matrix
    for mu in sym2_spectrum():
        if mu != target:
            result = apply_pair_operator(result) - mu * result
    result = result / _interpolation_denominator(target)
    return 0.5 * (result + result.T)


def project_54_and_4125(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(Pi_54 W, Pi_4125 W) with the shared factor applied once (7 K products)."""
    k54 = _channel_eigenvalue("54")
    k4125 = _channel_eigenvalue("4125")
    common = matrix
    for mu in sym2_spectrum():
        if mu not in (k54, k4125):
            common = apply_pair_operator(common) - mu * common
    image = apply_pair_operator(common)
    p54 = (image - k4125 * common) / _interpolation_denominator(k54)
    p4125 = (image - k54 * common) / _interpolation_denominator(k4125)
    return 0.5 * (p54 + p54.T), 0.5 * (p4125 + p4125.T)


def reference_projections(phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return project_54_and_4125(np.outer(phi, phi))


def reference_objective(phi: np.ndarray) -> tuple[float, np.ndarray]:
    """f = ||Pi_54(PhiPhi)||^2 + ||Pi_4125(PhiPhi)||^2 and grad f = 4 P Phi."""
    p54, p4125 = reference_projections(phi)
    value = float(np.sum(p54 * p54) + np.sum(p4125 * p4125))
    return value, 4.0 * (p54 + p4125) @ phi


def reference_channel_values(phi: np.ndarray) -> tuple[float, float]:
    p54, p4125 = reference_projections(phi)
    return float(np.sum(p54 * p54)), float(np.sum(p4125 * p4125))


@lru_cache(maxsize=1)
def projector_certificate() -> dict[str, Any]:
    matrix = _random_symmetric(SEEDS["projector_sanity"])
    spectrum = sym2_spectrum()
    parts = {mu: spectral_projector(matrix, mu) for mu in spectrum}
    idempotence = {}
    eigen_residual = {}
    for mu, part in parts.items():
        norm = float(np.linalg.norm(part))
        idempotence[str(mu)] = _bound(float(np.linalg.norm(spectral_projector(part, mu) - part)) / norm)
        eigen_residual[str(mu)] = _bound(
            float(np.linalg.norm(apply_pair_operator(part) - mu * part)) / norm
        )
    completeness = float(np.linalg.norm(sum(parts.values()) - matrix))
    orthogonality = max(
        abs(float(np.sum(parts[m] * parts[n])))
        for m in spectrum for n in spectrum if m < n
    )
    p54, p4125 = project_54_and_4125(matrix)
    pair_helper_defect = max(
        float(np.linalg.norm(p54 - parts[_channel_eigenvalue("54")])),
        float(np.linalg.norm(p4125 - parts[_channel_eigenvalue("4125")])),
    )
    identity = np.eye(N210)
    singlet_defect = float(np.max(np.abs(apply_pair_operator(identity) - 24.0 * identity)))
    rng = np.random.default_rng(SEEDS["projector_sanity"] + 1)
    traceless = rng.standard_normal((DIM, DIM))
    traceless = traceless + traceless.T
    traceless -= np.trace(traceless) / DIM * np.eye(DIM)
    derivation = derivation_matrix(traceless)
    derivation_defect = float(
        np.linalg.norm(apply_pair_operator(derivation) - 14.0 * derivation)
        / np.linalg.norm(derivation)
    )
    derivation_in_54 = float(
        np.linalg.norm(spectral_projector(derivation, _channel_eigenvalue("54")) - derivation)
        / np.linalg.norm(derivation)
    )
    # Direct eigenspace dimensions of the small channels: rank of Pi_mu applied
    # to 64 random symmetric inputs (block application of the sparse K).
    block = np.random.default_rng(SEEDS["projector_sanity"] + 2).standard_normal((64, N210, N210))
    block = (block + block.transpose(0, 2, 1)).reshape(64, N210 * N210).T
    ranks = {}
    for mu in (24, 16, _channel_eigenvalue("54")):
        image = block
        for other in spectrum:
            if other != mu:
                image = pair_operator() @ image - other * image
        singular = np.linalg.svd(image, compute_uv=False)
        ranks[str(mu)] = int(np.sum(singular > 1.0e-9 * singular[0]))
    return {
        "input": "random symmetric 210x210 matrix, unit Frobenius norm",
        "eigenspace_dimension_by_projector_rank_64_inputs": ranks,
        "relative_idempotence_defect": idempotence,
        "relative_eigenspace_residual_K_Pi_minus_mu_Pi": eigen_residual,
        "completeness_defect": _bound(completeness),
        "max_cross_overlap": _bound(orthogonality),
        "shared_factor_helper_defect": _bound(pair_helper_defect),
        "K_identity_minus_24_identity": _bound(singlet_defect),
        "K_on_traceless_derivation_relative_defect_vs_14": _bound(derivation_defect),
        "traceless_derivation_outside_Pi54_relative": _bound(derivation_in_54),
        "max_idempotence_defect": max(idempotence.values()),
        "max_eigenspace_residual": max(eigen_residual.values()),
    }


# ---------------------------------------------------------------------------
# forms, A(Phi) and the cubic invariant
# ---------------------------------------------------------------------------
def four_form(terms: dict[tuple[int, ...], float]) -> np.ndarray:
    vector = np.zeros(N210)
    for indices, value in terms.items():
        vector[FOUR_INDEX[tuple(sorted(indices))]] += value * _perm_sign(indices)
    return vector


@lru_cache(maxsize=1)
def slice_basis() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """A = sum_{i<j<=4} w_i w_j, B = sum_{i<=4} w_i w_5, C = Re(dz1 dz2 dz3 dz4)."""
    a_form = four_form(
        {(2 * i, 2 * i + 1, 2 * j, 2 * j + 1): 1.0 for i in range(4) for j in range(i + 1, 4)}
    )
    b_form = four_form({(2 * i, 2 * i + 1, 8, 9): 1.0 for i in range(4)})
    c_terms = {}
    for choice in itertools.product((0, 1), repeat=4):
        imaginary = sum(choice)
        if imaginary % 2 == 0:
            c_terms[tuple(2 * k + choice[k] for k in range(4))] = float((-1) ** (imaginary // 2))
    c_form = four_form(c_terms)
    return a_form, b_form, c_form


def kahler_square_unit() -> np.ndarray:
    a_form, b_form, _ = slice_basis()
    return (a_form + b_form) / math.sqrt(10.0)


def cayley_unit() -> np.ndarray:
    a_form, _, c_form = slice_basis()
    return (a_form + c_form) / math.sqrt(14.0)


@lru_cache(maxsize=1)
def _pair_matrix_maps() -> tuple[np.ndarray, np.ndarray]:
    flat = np.zeros((N210, 6), dtype=np.int64)
    sign = np.zeros((N210, 6))
    for position, (a, b, c, d) in enumerate(FOUR):
        entries = []
        for left, right, parity in (((a, b), (c, d), 1), ((a, c), (b, d), -1), ((a, d), (b, c), 1)):
            i, j = PAIR_INDEX[left], PAIR_INDEX[right]
            entries.extend(((i * N45 + j, parity), (j * N45 + i, parity)))
        flat[position] = [entry[0] for entry in entries]
        sign[position] = [entry[1] for entry in entries]
    return flat, sign


def pair_matrix(phi: np.ndarray) -> np.ndarray:
    """A(Phi)_[ab],[cd] = Phi_abcd on the pair basis a<b (45x45, symmetric)."""
    flat, sign = _pair_matrix_maps()
    matrix = np.zeros(N45 * N45)
    matrix[flat] = sign * phi[:, None]
    return matrix.reshape(N45, N45)


def cubic_invariant_and_grad(phi: np.ndarray) -> tuple[float, np.ndarray]:
    """I3 = 8 Tr A^3 and its gradient 24 * (A^2 pulled back to 4-forms)."""
    flat, sign = _pair_matrix_maps()
    matrix = pair_matrix(phi)
    square = matrix @ matrix
    return 8.0 * float(np.sum(square * matrix)), 24.0 * np.sum(sign * square.ravel()[flat], axis=1)


def cubic_invariant(phi: np.ndarray) -> float:
    return cubic_invariant_and_grad(phi)[0]


@lru_cache(maxsize=1)
def _full_tensor_maps() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    positions = np.zeros((N210, 24), dtype=np.int64)
    signs = np.zeros((N210, 24))
    for position, subset in enumerate(FOUR):
        for k, permutation in enumerate(itertools.permutations(range(4))):
            a, b, c, d = (subset[p] for p in permutation)
            positions[position, k] = ((a * DIM + b) * DIM + c) * DIM + d
            signs[position, k] = _perm_sign(permutation)
    source = np.full(DIM**4, N210, dtype=np.int64)
    factor = np.zeros(DIM**4)
    source[positions.ravel()] = np.repeat(np.arange(N210), 24)
    factor[positions.ravel()] = signs.ravel()
    return positions, signs, source, factor


def full_tensor(phi: np.ndarray) -> np.ndarray:
    _, _, source, factor = _full_tensor_maps()
    return (factor * np.append(phi, 0.0)[source]).reshape(DIM, DIM, DIM, DIM)


def cubic_invariant_bruteforce(phi: np.ndarray) -> float:
    tensor = full_tensor(phi)
    return float(np.einsum("abcd,cdef,efab->", tensor, tensor, tensor, optimize=True))


def orbit_spectrum(phi: np.ndarray) -> np.ndarray:
    return np.sort(np.linalg.eigvalsh(pair_matrix(phi)))


@lru_cache(maxsize=1)
def reference_spectra() -> dict[str, np.ndarray]:
    return {
        "+F": orbit_spectrum(kahler_square_unit()),
        "-F": orbit_spectrum(-kahler_square_unit()),
        "cayley": orbit_spectrum(cayley_unit()),
    }


# ---------------------------------------------------------------------------
# fast path: exact contraction formula for I_54 and I_4125
# ---------------------------------------------------------------------------
def contraction_invariants(phi: np.ndarray) -> np.ndarray:
    tensor = full_tensor(phi)
    norm_squared = float(phi @ phi)
    rows = tensor.reshape(DIM, DIM**3)
    three = rows @ rows.T
    pairs = tensor.reshape(DIM * DIM, DIM * DIM)
    two = pairs @ pairs.T
    crossed = two.reshape(DIM, DIM, DIM, DIM).transpose(0, 2, 1, 3).reshape(DIM * DIM, DIM * DIM)
    return np.array(
        [norm_squared**2, np.sum(three * three), np.sum(two * two), np.sum(two * crossed)]
    )


def fast_quartic(phi: np.ndarray, coefficients: np.ndarray) -> tuple[float, np.ndarray]:
    """sum_i c_i J_i(Phi) and its gradient (exact polynomial derivatives)."""
    positions, signs, _, _ = _full_tensor_maps()
    tensor = full_tensor(phi)
    norm_squared = float(phi @ phi)
    rows = tensor.reshape(DIM, DIM**3)
    three = rows @ rows.T
    pairs = tensor.reshape(DIM * DIM, DIM * DIM)
    two = pairs @ pairs.T
    crossed = two.reshape(DIM, DIM, DIM, DIM).transpose(0, 2, 1, 3).reshape(DIM * DIM, DIM * DIM)
    values = (
        norm_squared**2,
        float(np.sum(three * three)),
        float(np.sum(two * two)),
        float(np.sum(two * crossed)),
    )
    tensor_gradient = 4.0 * (
        coefficients[1] * (three @ rows).ravel()
        + ((coefficients[2] * two + coefficients[3] * crossed) @ pairs).ravel()
    )
    gradient = np.sum(signs * tensor_gradient[positions], axis=1)
    gradient += 4.0 * coefficients[0] * norm_squared * phi
    return float(np.dot(values, coefficients)), gradient


def _coefficients(channel: str) -> np.ndarray:
    return np.array([float(c) for c in CONTRACTION_COEFFICIENTS[channel]])


def fast_objective(phi: np.ndarray) -> tuple[float, np.ndarray]:
    return fast_quartic(phi, _coefficients("54") + _coefficients("4125"))


@lru_cache(maxsize=1)
def contraction_identity_certificate() -> dict[str, Any]:
    rng = np.random.default_rng(SEEDS["contraction_fit"])
    rows, targets54, targets4125 = [], [], []
    for _ in range(16):
        phi = _unit(rng.standard_normal(N210))
        i54, i4125 = reference_channel_values(phi)
        rows.append(contraction_invariants(phi))
        targets54.append(i54)
        targets4125.append(i4125)
    design = np.array(rows)
    singular_values = np.linalg.svd(design, compute_uv=False)
    fitted = {}
    deviation = 0.0
    for channel, targets in (("54", targets54), ("4125", targets4125)):
        solution = np.linalg.lstsq(design, np.array(targets), rcond=None)[0]
        fitted[channel] = [_round_abs(value, 12) for value in solution]
        deviation = max(deviation, float(np.max(np.abs(solution - _coefficients(channel)))))
    rng = np.random.default_rng(SEEDS["contraction_validation"])
    value_error = 0.0
    gradient_error = 0.0
    for _ in range(8):
        phi = _unit(rng.standard_normal(N210))
        p54, p4125 = reference_projections(phi)
        for channel, projected in (("54", p54), ("4125", p4125)):
            reference = float(np.sum(projected * projected))
            value_error = max(
                value_error,
                abs(fast_quartic(phi, _coefficients(channel))[0] - reference) / reference,
            )
        reference_gradient = 4.0 * (p54 + p4125) @ phi
        gradient_error = max(
            gradient_error,
            float(np.linalg.norm(fast_objective(phi)[1] - reference_gradient)
                  / np.linalg.norm(reference_gradient)),
        )
    special = {}
    for name, phi in (
        ("F", kahler_square_unit()),
        ("minus_F", -kahler_square_unit()),
        ("cayley", cayley_unit()),
    ):
        special[name] = _bound(fast_objective(phi)[0] - reference_objective(phi)[0])
    return {
        "basis": {
            "J0": "|Phi|^4",
            "J1": "sum_ab M_ab^2, M_ab = sum_cde Phi_acde Phi_bcde (all orderings)",
            "J2": "sum_abcd P_abcd^2, P_abcd = sum_ef Phi_abef Phi_cdef",
            "J3": "sum_abcd P_abcd P_acbd",
        },
        "why_four": (
            "Complete contractions of four copies of Phi are 4-regular loopless "
            "multigraphs on four vertices; there are exactly four, so O(10)-invariant "
            "quartics on Lambda^4 R^10 span at most four functions."
        ),
        "identity": {
            channel: {"J0": str(c[0]), "J1": str(c[1]), "J2": str(c[2]), "J3": str(c[3])}
            for channel, c in CONTRACTION_COEFFICIENTS.items()
        },
        "I54_as_traceless_contraction": "I_54 = ||M - tr(M) I/10||_F^2 / 2016 (tr M = 24 |Phi|^2)",
        "fit_points": 16,
        "fit_singular_values": [_sig(value, 6) for value in singular_values],
        "fitted_coefficients": fitted,
        "max_abs_fitted_minus_rational": _bound(deviation),
        "validation_points": 8,
        "max_relative_value_error": _bound(value_error),
        "max_relative_gradient_error_vs_4_P_Phi": _bound(gradient_error),
        "abs_fast_minus_reference_at_special_forms": special,
    }


@lru_cache(maxsize=1)
def gradient_certificate() -> dict[str, Any]:
    rng = np.random.default_rng(SEEDS["gradient_check"])
    phi = _unit(rng.standard_normal(N210))
    step = 1.0e-5
    errors: dict[str, float] = {"reference_f": 0.0, "fast_f_normalized": 0.0, "I3": 0.0}
    point = 1.3 * phi
    functions = {
        "reference_f": reference_objective,
        "fast_f_normalized": lambda x: _normalized(fast_objective, x, 4),
        "I3": cubic_invariant_and_grad,
    }
    for name, function in functions.items():
        _, gradient = function(point)
        for _ in range(3):
            direction = _unit(rng.standard_normal(N210))
            difference = (
                function(point + step * direction)[0] - function(point - step * direction)[0]
            ) / (2.0 * step)
            errors[name] = max(
                errors[name], abs(difference - gradient @ direction) / np.linalg.norm(gradient)
            )
    return {
        "step": step,
        "directions_per_function": 3,
        "max_relative_error": {name: _bound(value) for name, value in errors.items()},
        "passes": bool(max(errors.values()) < 1.0e-7),
    }


# ---------------------------------------------------------------------------
# reference forms and the repository slice identities
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def reference_form_certificate() -> dict[str, Any]:
    f_form = kahler_square_unit()
    cayley = cayley_unit()
    rng = np.random.default_rng(SEEDS["gradient_check"] + 1)
    random_form = _unit(rng.standard_normal(N210))
    forms = {"F": f_form, "minus_F": -f_form, "cayley": cayley}
    out: dict[str, Any] = {}
    for name, phi in forms.items():
        p54, p4125 = reference_projections(phi)
        out[name] = {
            "norm": _sig(float(np.linalg.norm(phi)), 10),
            "I3": _sig(cubic_invariant(phi), 10),
            "Pi54_frobenius_norm": _value_or_bound(float(np.linalg.norm(p54))),
            "Pi4125_frobenius_norm": _value_or_bound(float(np.linalg.norm(p4125))),
        }
    out["F"]["A_spectrum_times_sqrt10"] = _grouped_spectrum(reference_spectra()["+F"], math.sqrt(10.0))
    out["minus_F"]["A_spectrum_times_sqrt10"] = _grouped_spectrum(reference_spectra()["-F"], math.sqrt(10.0))
    out["cayley"]["A_spectrum_times_sqrt14"] = _grouped_spectrum(reference_spectra()["cayley"], math.sqrt(14.0))
    out["cayley"]["I54_exact_expected"] = "1/140"
    out["cayley"]["I54"] = _sig(reference_channel_values(cayley)[0], 10)
    out["I3_F_exact"] = "8*60/10^(3/2) = 48/sqrt(10)"
    out["I3_cayley_exact"] = "8*168/14^(3/2) = 96/sqrt(14)"
    out["I3_F_abs_error"] = _bound(cubic_invariant(f_form) - I3_F_EXACT)
    out["I3_minus_F_abs_error"] = _bound(cubic_invariant(-f_form) + I3_F_EXACT)
    out["I3_cayley_abs_error"] = _bound(cubic_invariant(cayley) - I3_CAYLEY_EXACT)
    out["I3_equals_8_trace_A3_bruteforce_max_abs_error"] = _bound(
        max(
            abs(cubic_invariant(phi) - cubic_invariant_bruteforce(phi))
            for phi in (f_form, cayley, random_form)
        )
    )
    return out


@lru_cache(maxsize=1)
def slice_cross_check() -> dict[str, Any]:
    basis = slice_basis()
    pairs = []
    for left in range(3):
        for right in range(left, 3):
            pair = np.outer(basis[left], basis[right])
            if left != right:
                pair = pair + np.outer(basis[right], basis[left])
            pairs.append(pair)
    projected = [project_54_and_4125(pair) for pair in pairs]
    result: dict[str, Any] = {
        "slice": "Phi = a*A + b*B + c*C with integer-coefficient A, B, C (|A|^2=6, |B|^2=4, |C|^2=8)",
        "monomials": list(SLICE_MONOMIALS),
    }
    for index, channel in enumerate(("54", "4125")):
        gram = np.array(
            [[np.sum(pairs[i] * projected[j][index]) for j in range(6)] for i in range(6)]
        )
        gram = 0.5 * (gram + gram.T)
        identity = REPO_SLICE_IDENTITIES[channel]
        vector = np.asarray(identity["vector"], dtype=float)
        repo = float(identity["scale"]) * np.outer(vector, vector)
        factor = float(np.sum(gram * repo) / np.sum(repo * repo))
        result[channel] = {
            "repo_formula": identity["formula"],
            "fitted_factor_mine_over_repo": _sig(factor, 12),
            "max_abs_gram_residual_factor_one": _bound(float(np.max(np.abs(gram - repo)))),
            "max_abs_gram_residual_fitted_factor": _bound(float(np.max(np.abs(gram - factor * repo)))),
        }
    points = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (0.3, -0.7, 0.45), (1.1, 0.2, -0.6))
    point_error = 0.0
    for a, b, c in points:
        phi = a * basis[0] + b * basis[1] + c * basis[2]
        i54, i4125 = reference_channel_values(phi)
        point_error = max(
            point_error,
            abs(i54 - (3 * a * a - 3 * b * b + 4 * c * c) ** 2 / 35.0),
            abs(i4125 - 80.0 * (a * a - b * b - c * c) ** 2 / 21.0),
        )
    result["point_evaluations"] = len(points)
    result["max_abs_point_error"] = _bound(point_error)
    zeros = {}
    for label, (a, b) in (("A+B", (1.0, 1.0)), ("A-B", (1.0, -1.0))):
        for sign in (1.0, -1.0):
            phi = sign * (a * basis[0] + b * basis[1]) / math.sqrt(10.0)
            distances = _spectral_distances(phi)
            zeros[f"{'+' if sign > 0 else '-'}({label})/sqrt(10)"] = {
                "f_reference": _bound(reference_objective(phi)[0]),
                "orbit": "+F" if distances[0] < SPECTRAL_TOL else ("-F" if distances[1] < SPECTRAL_TOL else "none"),
            }
    result["slice_zero_locus_c0_a2_eq_b2_orbits"] = zeros
    return result


# ---------------------------------------------------------------------------
# second-order analysis at F
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def local_second_order_analysis() -> dict[str, Any]:
    """Hessians of f and I3 at F on the tangent space of the unit sphere.

    Near the +F orbit, g(t) = min{f : I3 = t} obeys g = mu* delta + O(delta^1.5)
    with mu* = sup{mu >= 0 : H_f + mu H_I3^R >= 0 on T_F S^209}.
    """
    f_form = kahler_square_unit()
    flat, sign = _pair_matrix_maps()
    hessian_f = np.zeros((N210, N210))
    hessian_i3 = np.zeros((N210, N210))
    a_f = pair_matrix(f_form)
    for column in range(N210):
        unit = np.zeros(N210)
        unit[column] = 1.0
        p54, p4125 = project_54_and_4125(np.outer(unit, f_form) + np.outer(f_form, unit))
        hessian_f[:, column] = 4.0 * (p54 + p4125) @ f_form
        a_e = pair_matrix(unit)
        product = a_f @ a_e + a_e @ a_f
        hessian_i3[:, column] = 24.0 * np.sum(sign * product.ravel()[flat], axis=1)
    hessian_f = 0.5 * (hessian_f + hessian_f.T)
    hessian_i3 = 0.5 * (hessian_i3 + hessian_i3.T)
    i3_f, gradient_i3 = cubic_invariant_and_grad(f_form)
    radial = float(gradient_i3 @ f_form)
    gradient_tangential = float(np.linalg.norm(gradient_i3 - radial * f_form))
    projector = np.eye(N210) - np.outer(f_form, f_form)
    eigenvalues, eigenvectors = np.linalg.eigh(projector)
    tangent = eigenvectors[:, eigenvalues > 0.5]
    h_f = tangent.T @ hessian_f @ tangent
    h_r = tangent.T @ (hessian_i3 - radial * np.eye(N210)) @ tangent
    w_f, v_f = np.linalg.eigh(h_f)
    w_r = np.linalg.eigvalsh(h_r)
    kernel = v_f[:, np.abs(w_f) < 1.0e-9]
    kernel_i3 = np.linalg.eigvalsh(kernel.T @ h_r @ kernel)
    orbit_tangent = np.column_stack([g @ f_form for g in generator_matrices()])
    orbit_rank = int(np.linalg.matrix_rank(orbit_tangent, tol=1.0e-9))
    orbit_in_kernel = float(np.max(np.abs(hessian_f @ orbit_tangent)))

    def min_eig(mu: float) -> float:
        return float(np.linalg.eigvalsh(h_f + mu * h_r)[0])

    low, high = 0.0, 1.0
    bracket_ok = min_eig(low) > -1.0e-10 and min_eig(high) < -1.0e-6
    for _ in range(50):
        middle = 0.5 * (low + high)
        if min_eig(middle) >= -1.0e-10:
            low = middle
        else:
            high = middle
    mu_star = 0.5 * (low + high)
    closed_form = 7.0 / (270.0 * math.sqrt(10.0))
    positive_f = w_f[np.abs(w_f) >= 1.0e-9]
    return {
        "I3_F": _sig(i3_f, 10),
        "grad_I3_radial_component": _sig(radial, 10),
        "grad_I3_tangential_norm": _bound(gradient_tangential),
        "F_is_critical_point_of_I3_on_sphere": bool(gradient_tangential < 1.0e-10),
        "tangent_dimension": int(tangent.shape[1]),
        "hessian_f_min_eigenvalue": _round_abs(float(w_f[0]), 10),
        "hessian_f_kernel_dimension": int(kernel.shape[1]),
        "hessian_f_smallest_positive_eigenvalue": _sig(float(positive_f.min()), 10),
        "hessian_f_spectrum": _grouped_spectrum(w_f, 1.0, tol=1.0e-7),
        "riemannian_hessian_I3_spectrum": _grouped_spectrum(w_r, 1.0, tol=1.0e-7),
        "riemannian_hessian_I3_on_f_kernel": _grouped_spectrum(kernel_i3, 1.0, tol=1.0e-7),
        "orbit_tangent_rank": orbit_rank,
        "orbit_tangent_in_f_kernel_max_defect": _bound(orbit_in_kernel),
        "excess_directions": int(kernel.shape[1]) - orbit_rank,
        "excess_I3_curvature_expected": _sig(radial, 10),
        "excess_directions_raise_I3": bool(
            np.sum(kernel_i3 > 1.0) == kernel.shape[1] - orbit_rank
            and np.all(np.abs(kernel_i3[kernel_i3 <= 1.0]) < 1.0e-8)
        ),
        "bisection_bracket_valid": bool(bracket_ok),
        "mu_star": _sig(mu_star, 10),
        "mu_star_closed_form_candidate": "7/(270*sqrt(10)) = (28/45)/(24*sqrt(10))",
        "mu_star_closed_form_value": _sig(closed_form, 10),
        "mu_star_relative_difference_to_closed_form": _bound((mu_star - closed_form) / closed_form),
        "small_delta_law": "g(t) = mu_star*delta + O(delta^1.5), delta = I3(F) - t",
        "_mu_star_float": mu_star,
    }


# ---------------------------------------------------------------------------
# endpoint classification
# ---------------------------------------------------------------------------
def _spectral_distances(phi: np.ndarray) -> tuple[float, float]:
    spectrum = orbit_spectrum(_unit(phi))
    spectra = reference_spectra()
    return (
        float(np.max(np.abs(spectrum - spectra["+F"]))),
        float(np.max(np.abs(spectrum - spectra["-F"]))),
    )


def orbit_witness(phi: np.ndarray) -> dict[str, float]:
    """Explicit nearby element of SO(10).(+-F).

    The extreme eigenvector of A(Phi) is rebuilt as an antisymmetric 10x10
    matrix; its orthogonal polar factor J is an orthogonal complex structure
    (J^2 = -1), and s*omega_J^2/|omega_J^2| (s = sign of the extreme
    eigenvalue) lies exactly on SO(10).(sF).
    """
    eigenvalues, eigenvectors = np.linalg.eigh(pair_matrix(phi))
    top = int(np.argmax(np.abs(eigenvalues)))
    sign = 1.0 if eigenvalues[top] > 0 else -1.0
    omega = np.zeros((DIM, DIM))
    for position, (a, b) in enumerate(PAIRS):
        omega[a, b] = eigenvectors[position, top]
        omega[b, a] = -eigenvectors[position, top]
    left, _, right = np.linalg.svd(omega)
    structure = left @ right
    structure = 0.5 * (structure - structure.T)
    square = np.array(
        [
            structure[a, b] * structure[c, d]
            - structure[a, c] * structure[b, d]
            + structure[a, d] * structure[b, c]
            for a, b, c, d in FOUR
        ]
    )
    witness = sign * square / np.linalg.norm(square)
    return {
        "distance": float(np.linalg.norm(_unit(phi) - witness)),
        "sign": sign,
        "complex_structure_defect": float(np.max(np.abs(structure @ structure + np.eye(DIM)))),
    }


def classify_endpoint(phi: np.ndarray) -> dict[str, Any]:
    phi = _unit(phi)
    value, gradient = reference_objective(phi)
    tangential = gradient - (gradient @ phi) * phi
    plus, minus = _spectral_distances(phi)
    witness = orbit_witness(phi)
    i3 = cubic_invariant(phi)
    is_zero = value <= ZERO_TOL
    on_plus = plus <= SPECTRAL_TOL and witness["distance"] <= WITNESS_TOL and witness["sign"] > 0
    on_minus = minus <= SPECTRAL_TOL and witness["distance"] <= WITNESS_TOL and witness["sign"] < 0
    if is_zero and on_plus:
        label = "+F"
    elif is_zero and on_minus:
        label = "-F"
    elif is_zero:
        label = "zero_off_orbit"
    else:
        label = "nonzero_local_minimum"
    return {
        "label": label,
        "f_reference": value,
        "riemannian_gradient_norm": float(np.linalg.norm(tangential)),
        "I3": i3,
        "spectral_distance_plus_F": plus,
        "spectral_distance_minus_F": minus,
        "witness_distance": witness["distance"],
        "witness_complex_structure_defect": witness["complex_structure_defect"],
    }


# ---------------------------------------------------------------------------
# claim 1: multistart
# ---------------------------------------------------------------------------
def run_multistart(n_starts: int, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    records = []
    for start in range(n_starts):
        x0 = _unit(rng.standard_normal(N210))
        fast = minimize(
            lambda x: _normalized(fast_objective, x, 4), x0, jac=True,
            method="L-BFGS-B", options=FAST_OPTIONS,
        )
        stage_one = _unit(fast.x)
        before = reference_objective(stage_one)[0]
        before_distance = min(_spectral_distances(stage_one))
        # Up to three fresh L-BFGS polishes with the Casimir projectors: near the
        # orbit the quartic (5+5bar) directions make the double-precision
        # gradient noisy, which can stop a single pass early.
        current, current_value, passes, polish_iterations = stage_one, before, 0, 0
        while passes < 3 and current_value > 1.0e-20:
            polish = minimize(
                lambda x: _normalized(reference_objective, x, 4), current, jac=True,
                method="L-BFGS-B", options=POLISH_OPTIONS,
            )
            passes += 1
            polish_iterations += int(polish.nit)
            candidate = _unit(polish.x)
            candidate_value = reference_objective(candidate)[0]
            improved = candidate_value < 0.5 * current_value
            if candidate_value < current_value:
                current, current_value = candidate, candidate_value
            if not improved:
                break
        endpoint = classify_endpoint(current)
        endpoint.update(
            {
                "start": start,
                "fast_iterations": int(fast.nit),
                "polish_passes": passes,
                "polish_iterations": polish_iterations,
                "f_reference_before_polish": before,
                "spectral_distance_before_polish": before_distance,
            }
        )
        records.append(endpoint)
    labels = Counter(record["label"] for record in records)
    zeros = [r for r in records if r["label"] in ("+F", "-F", "zero_off_orbit")]
    on_orbit = [r for r in records if r["label"] in ("+F", "-F")]
    anomalies = [
        {
            "start": r["start"],
            "label": r["label"],
            "f_reference": _sig(r["f_reference"], 6),
            "I3": _sig(r["I3"], 8),
            "riemannian_gradient_norm": _sig(r["riemannian_gradient_norm"], 2),
            "spectral_distance_plus_F": _sig(r["spectral_distance_plus_F"], 4),
            "spectral_distance_minus_F": _sig(r["spectral_distance_minus_F"], 4),
            "witness_distance": _sig(r["witness_distance"], 4),
        }
        for r in records
        if r["label"] not in ("+F", "-F")
    ]

    def worst(key: str, pool: list[dict[str, Any]]) -> float:
        return _sig(max((r[key] for r in pool), default=0.0), 2)

    return {
        "n_starts": n_starts,
        "seed": seed,
        "start_distribution": "x0 = standard normal in R^210, normalised",
        "n_reached_zero": len(zeros),
        "n_plus_F": labels.get("+F", 0),
        "n_minus_F": labels.get("-F", 0),
        "n_zero_off_orbit": labels.get("zero_off_orbit", 0),
        "n_nonzero_local_minima": labels.get("nonzero_local_minimum", 0),
        "orbit_sequence": "".join(
            {"+F": "+", "-F": "-", "zero_off_orbit": "X"}.get(r["label"], "?") for r in records
        ),
        "tolerances": {
            "zero_f_reference": ZERO_TOL,
            "sorted_A_spectrum_max_abs": SPECTRAL_TOL,
            "orbit_witness_distance": WITNESS_TOL,
            "abs_I3_minus_signed_I3F": I3_ENDPOINT_TOL,
        },
        "max_f_reference_before_polish": worst("f_reference_before_polish", records),
        "max_spectral_distance_before_polish": worst("spectral_distance_before_polish", on_orbit),
        "max_f_reference_after_polish": worst("f_reference", records),
        "max_spectral_distance_to_assigned_orbit": _sig(
            max(
                (
                    r["spectral_distance_plus_F"] if r["label"] == "+F" else r["spectral_distance_minus_F"]
                    for r in on_orbit
                ),
                default=0.0,
            ),
            2,
        ),
        "min_spectral_distance_to_other_orbit": _sig(
            min(
                (
                    r["spectral_distance_minus_F"] if r["label"] == "+F" else r["spectral_distance_plus_F"]
                    for r in on_orbit
                ),
                default=0.0,
            ),
            6,
        ),
        "max_witness_distance": worst("witness_distance", on_orbit),
        "max_witness_complex_structure_defect": _bound(
            max((r["witness_complex_structure_defect"] for r in on_orbit), default=0.0)
        ),
        "max_abs_I3_minus_signed_I3F": _bound(
            max(
                (
                    abs(r["I3"] - (I3_F_EXACT if r["label"] == "+F" else -I3_F_EXACT))
                    for r in on_orbit
                ),
                default=0.0,
            )
        ),
        "max_fast_iterations": max((r["fast_iterations"] for r in records), default=0),
        "polish_passes_histogram": {
            str(k): v for k, v in sorted(Counter(r["polish_passes"] for r in records).items())
        },
        "precision_note": (
            "f and grad f from the Casimir projectors carry ~1e-14 absolute round-off in "
            "P = Pi(Phi Phi^T); in the quartic 5+5bar directions this limits the reachable "
            "distance to the orbit to ~1e-4..1e-6 in double precision"
        ),
        "anomalies": anomalies,
    }


# ---------------------------------------------------------------------------
# claim 2: adversarial profile g(t) = min{f : |Phi|=1, I3(Phi)=t}
# ---------------------------------------------------------------------------
def _constrained_record(x: np.ndarray, target: float, method: str, start: str) -> dict[str, Any]:
    x = _unit(x)
    value, gradient = fast_objective(x)
    i3, gradient_i3 = cubic_invariant_and_grad(x)
    tangential_f = gradient - (gradient @ x) * x
    tangential_i3 = gradient_i3 - (gradient_i3 @ x) * x
    denominator = float(tangential_i3 @ tangential_i3)
    multiplier = -float(tangential_f @ tangential_i3) / denominator if denominator > 0 else 0.0
    kkt = float(np.linalg.norm(tangential_f + multiplier * tangential_i3))
    return {
        "x": x,
        "value": value,
        "constraint": i3 - target,
        "kkt_relative": kkt / max(float(np.linalg.norm(tangential_f)), 1.0e-300),
        "multiplier": multiplier,
        "method": method,
        "start": start,
    }


def _augmented_lagrangian(target: float, x0: np.ndarray, start: str) -> dict[str, Any]:
    x = _unit(x0)
    multiplier = 0.0
    penalty = 10.0
    previous = math.inf
    for outer in range(1, 41):
        def merit(y: np.ndarray, lam: float = multiplier, rho: float = penalty) -> tuple[float, np.ndarray]:
            value, gradient = _normalized(fast_objective, y, 4)
            cubic, cubic_gradient = _normalized(cubic_invariant_and_grad, y, 3)
            residual = cubic - target
            return (
                value + lam * residual + 0.5 * rho * residual * residual,
                gradient + (lam + rho * residual) * cubic_gradient,
            )

        result = minimize(merit, x, jac=True, method="L-BFGS-B", options=AL_INNER_OPTIONS)
        x = _unit(result.x)
        residual = cubic_invariant(x) - target
        multiplier += penalty * residual
        if abs(residual) <= 1.0e-11 and outer > 1:
            break
        if abs(residual) > 0.25 * abs(previous):
            penalty = min(10.0 * penalty, 1.0e9)
        previous = residual
    return _constrained_record(x, target, "augmented_lagrangian_lbfgs", start)


def _slsqp(target: float, x0: np.ndarray, start: str) -> dict[str, Any]:
    constraints = (
        {"type": "eq", "fun": lambda y: float(y @ y) - 1.0, "jac": lambda y: 2.0 * y},
        {
            "type": "eq",
            "fun": lambda y: cubic_invariant(y) - target,
            "jac": lambda y: cubic_invariant_and_grad(y)[1],
        },
    )
    result = minimize(
        fast_objective, _unit(x0), jac=True, method="SLSQP", constraints=constraints,
        options={"maxiter": 1000, "ftol": 1.0e-16},
    )
    return _constrained_record(result.x, target, "slsqp", start)


def run_profile(fractions: tuple[float, ...], n_random: int, seed: int, slsqp: bool) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    f_form = kahler_square_unit()
    i3_f = cubic_invariant(f_form)
    rows: list[dict[str, Any]] = [
        {
            "delta_over_I3F": 0.0,
            "t": _sig(i3_f, 8),
            "delta": 0.0,
            "g": 0.0,
            "note": "attained at F itself (projector zero)",
        }
    ]
    previous = f_form
    best_values: dict[float, float] = {}
    minimum_off_f = math.inf
    for fraction in fractions:
        target = i3_f * (1.0 - fraction)
        delta = i3_f - target
        continuation = previous + 1.0e-3 * rng.standard_normal(N210)
        runs = [_augmented_lagrangian(target, continuation, "continuation")]
        for k in range(n_random):
            runs.append(_augmented_lagrangian(target, rng.standard_normal(N210), f"random_{k}"))
        if slsqp:
            runs.append(_slsqp(target, continuation, "continuation"))
        feasible = [r for r in runs if abs(r["constraint"]) <= FEASIBILITY_TOL]
        if not feasible:
            rows.append({"delta_over_I3F": fraction, "t": _sig(target, 8), "feasible_runs": 0})
            continue
        best = min(feasible, key=lambda r: r["value"])
        agreeing = sum(
            1 for r in feasible if abs(r["value"] - best["value"]) <= 1.0e-6 * best["value"] + 1.0e-14
        )
        reference_value = reference_objective(best["x"])[0]
        i54, i4125 = reference_channel_values(best["x"])
        plus, minus = _spectral_distances(best["x"])
        best_values[fraction] = best["value"]
        minimum_off_f = min(minimum_off_f, best["value"])
        rows.append(
            {
                "delta_over_I3F": fraction,
                "t": _sig(target, 8),
                "delta": _sig(delta, 8),
                "g": _sig(best["value"], 6),
                "g_reference_projectors": _sig(reference_value, 6),
                "g_over_delta": _sig(best["value"] / delta, 6),
                "g_over_delta_squared": _sig(best["value"] / delta**2, 6),
                "I54_at_minimiser": _sig(i54, 4),
                "I4125_at_minimiser": _sig(i4125, 4),
                "runs": len(runs),
                "feasible_runs": len(feasible),
                "runs_agreeing_with_best": agreeing,
                "worst_feasible_value": _sig(max(r["value"] for r in feasible), 6),
                "best_method": best["method"],
                "best_start": best["start"],
                "best_kkt_relative": _bound(best["kkt_relative"]),
                "best_abs_constraint": _bound(best["constraint"]),
                "minimiser_spectral_distance_to_plus_minus_F": _sig(min(plus, minus), 4),
                "fast_minus_reference_abs": _bound(best["value"] - reference_value),
            }
        )
        previous = best["x"]
    return {
        "rows": rows,
        "best_values": best_values,
        "min_g_off_F": minimum_off_f,
        "i3_f": i3_f,
    }


def analyse_profile(profile: dict[str, Any], mu_star: float) -> dict[str, Any]:
    rows = [r for r in profile["rows"] if r.get("delta", 0.0) > 0.0 and r["delta_over_I3F"] <= 1.0]
    rows.sort(key=lambda r: r["delta"])
    deltas = np.array([r["delta"] for r in rows])
    values = np.array([profile["best_values"][r["delta_over_I3F"]] for r in rows])
    small = slice(0, 4)
    design = np.column_stack([np.ones(4), np.sqrt(deltas[small]), deltas[small]])
    intercept, root_coefficient, linear_coefficient = np.linalg.lstsq(
        design, values[small] / deltas[small], rcond=None
    )[0]
    ratios = values / deltas**2
    monotone = bool(np.all(np.diff(values) > 0.0))
    quadratic_at_least = bool(np.all(np.diff(ratios[:4]) < 0.0) and ratios[:4].min() > 0.0)
    symmetric = None
    if 1.5 in profile["best_values"] and 0.5 in profile["best_values"]:
        a = profile["best_values"][1.5]
        b = profile["best_values"][0.5]
        symmetric = abs(a - b) / b
    g_zero = profile["best_values"].get(1.0)
    drift = float(ratios[:4].max() / ratios[:4].min())
    slope_ok = bool(abs(intercept - mu_star) / mu_star <= SLOPE_REL_TOL)
    if slope_ok and intercept > 0.0 and drift > 1.5:
        law = "linear in delta: g/delta -> mu_star > 0, g/delta^2 not constant"
    elif drift <= 1.2:
        law = "quadratic in delta: g/delta^2 approximately constant"
    else:
        law = "undetermined from the sampled delta"
    return {
        "small_delta_points": [_sig(d, 6) for d in deltas[small]],
        "pure_quadratic_coefficients_g_over_delta2_small_delta": [_sig(r, 6) for r in ratios[:4]],
        "pure_quadratic_coefficient_drift_max_over_min": _sig(drift, 6),
        "fit_form": "g/delta = a + b*sqrt(delta) + c*delta on the four smallest delta",
        "fit_linear_slope_a": _sig(float(intercept), 6),
        "fit_b": _sig(float(root_coefficient), 6),
        "fit_c": _sig(float(linear_coefficient), 6),
        "hessian_slope_mu_star": _sig(mu_star, 6),
        "relative_difference_fit_vs_hessian": _sig(abs(intercept - mu_star) / mu_star, 3),
        "slope_matches_hessian": slope_ok,
        "g_nondecreasing_in_delta": monotone,
        "growth_at_least_quadratic_near_F": quadratic_at_least,
        "growth_law_near_F": law,
        "g_at_I3_zero": _sig(g_zero, 6) if g_zero is not None else None,
        "sign_symmetry_relative_difference_t_vs_minus_t": (
            _bound(symmetric) if symmetric is not None else None
        ),
        "fitted_quadratic_coefficient_on_smallest_delta": _sig(float(ratios[0]), 6),
    }


# ---------------------------------------------------------------------------
# claim 3: the cubic maximum
# ---------------------------------------------------------------------------
def run_cubic_maximum(n_starts: int, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)

    def negative(x: np.ndarray) -> tuple[float, np.ndarray]:
        value, gradient = _normalized(cubic_invariant_and_grad, x, 3)
        return -value, -gradient

    values = []
    best_value = -math.inf
    best_x = None
    for _ in range(n_starts):
        result = minimize(
            negative, rng.standard_normal(N210), jac=True, method="L-BFGS-B", options=CUBIC_OPTIONS
        )
        x = _unit(result.x)
        value = cubic_invariant(x)
        values.append(value)
        if value > best_value:
            best_value, best_x = value, x
    spectrum = orbit_spectrum(best_x)
    cayley_distance = float(np.max(np.abs(spectrum - reference_spectra()["cayley"])))
    local_maxima = Counter(_sig(v, 8) for v in values)
    return {
        "n_starts": n_starts,
        "seed": seed,
        "max_I3": _sig(best_value, 10),
        "I3_F": _sig(I3_F_EXACT, 10),
        "I3_cayley_exact": _sig(I3_CAYLEY_EXACT, 10),
        "abs_max_minus_cayley": _bound(best_value - I3_CAYLEY_EXACT),
        "n_starts_at_max": sum(1 for v in values if abs(v - best_value) <= 1.0e-8),
        "local_maxima_found": [[value, count] for value, count in sorted(local_maxima.items(), reverse=True)],
        "maximiser_A_spectrum_times_sqrt14": _grouped_spectrum(spectrum, math.sqrt(14.0)),
        "maximiser_spectral_distance_to_cayley": _bound(cayley_distance),
        "maximiser_f": _sig(reference_objective(best_x)[0], 8),
        "maximiser_I54_I4125": [_round_abs(v, 12) for v in reference_channel_values(best_x)],
        "_best_value": best_value,
        "_cayley_distance": cayley_distance,
    }


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------
def _verdict(relative_difference: float, tight: float, loose: float) -> str:
    if relative_difference <= tight:
        return "REPRODUCED"
    if relative_difference <= loose:
        return "APPROXIMATELY_REPRODUCED"
    return "NOT_REPRODUCED"


def _claims_table(
    multistart: dict[str, Any],
    profile_analysis: dict[str, Any],
    profile: dict[str, Any],
    cubic: dict[str, Any],
    representation: dict[str, Any],
    slice_check: dict[str, Any],
    forms: dict[str, Any],
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    n = multistart["n_starts"]
    zeros_ok = multistart["n_reached_zero"] == n and multistart["n_zero_off_orbit"] == 0
    drift = profile_analysis["pure_quadratic_coefficient_drift_max_over_min"]
    quadratic_ok = drift <= 1.2 and abs(
        profile_analysis["fitted_quadratic_coefficient_on_smallest_delta"] - CLAIMS["profile_quadratic_coefficient"]
    ) <= 0.2 * CLAIMS["profile_quadratic_coefficient"]
    g_zero = profile_analysis["g_at_I3_zero"]
    rows = [
        {
            "id": "multistart_all_zeros_on_plus_minus_F",
            "claim": "150/150 random starts reach f ~ 0 and every zero lies on SO(10).F or SO(10).(-F)",
            "reproduced": (
                f"{multistart['n_reached_zero']}/{n} starts reach f <= {ZERO_TOL:g} ({config['mode']} run); "
                f"{multistart['n_plus_F'] + multistart['n_minus_F']} on +-F by A-spectrum "
                f"(tol {SPECTRAL_TOL:g}) and orbit witness (tol {WITNESS_TOL:g}); "
                f"{multistart['n_zero_off_orbit']} off-orbit zeros; "
                f"{multistart['n_nonzero_local_minima']} nonzero local minima"
            ),
            "verdict": "REPRODUCED" if zeros_ok and n == CLAIMS["multistart_starts"] else (
                "REPRODUCED_ON_FEWER_STARTS" if zeros_ok else "NOT_REPRODUCED"
            ),
        },
        {
            "id": "multistart_split",
            "claim": "70 on +F, 80 on -F",
            "reproduced": f"{multistart['n_plus_F']} on +F, {multistart['n_minus_F']} on -F (seed {multistart['seed']})",
            "verdict": (
                "REPRODUCED"
                if (multistart["n_plus_F"], multistart["n_minus_F"]) == (CLAIMS["multistart_plus"], CLAIMS["multistart_minus"])
                else "DIFFERENT_SPLIT__SEED_AND_OPTIMIZER_DEPENDENT"
            ),
        },
        {
            "id": "profile_quadratic_growth_near_F",
            "claim": "g(t) ~ 1.9e-3 * delta^2 near F (delta = I3(F) - t)",
            "reproduced": (
                f"growth law near F: {profile_analysis['growth_law_near_F']}; g/delta -> "
                f"{profile_analysis['fit_linear_slope_a']} (fit) vs mu* = {profile_analysis['hessian_slope_mu_star']} "
                f"(exact Hessian pencil at F); g/delta^2 = "
                f"{profile_analysis['pure_quadratic_coefficients_g_over_delta2_small_delta']} "
                f"at delta = {profile_analysis['small_delta_points']}"
            ),
            "verdict": (
                "REPRODUCED"
                if quadratic_ok
                else (
                    "NOT_REPRODUCED__GROWTH_IS_LINEAR_IN_DELTA"
                    if profile_analysis["growth_law_near_F"].startswith("linear")
                    else "NOT_REPRODUCED"
                )
            ),
        },
        {
            "id": "profile_value_at_I3_zero",
            "claim": "g(0) ~ 0.052",
            "reproduced": f"g(0) = {g_zero}",
            "verdict": (
                _verdict(abs(g_zero - CLAIMS["profile_g_at_zero"]) / CLAIMS["profile_g_at_zero"], 0.01, 0.1)
                if g_zero is not None else "NOT_EVALUATED"
            ),
        },
        {
            "id": "profile_positive_no_zero_off_F",
            "claim": "g grows smoothly with no zero off +-F",
            "reproduced": (
                f"min g over delta > 0 grid = {_sig(profile['min_g_off_F'], 6)}; nondecreasing in delta: "
                f"{profile_analysis['g_nondecreasing_in_delta']}"
            ),
            "verdict": (
                "REPRODUCED"
                if profile["min_g_off_F"] > ZERO_TOL and profile_analysis["g_nondecreasing_in_delta"]
                else "NOT_REPRODUCED"
            ),
        },
        {
            "id": "I3_of_F",
            "claim": "I3(F) = 8*60/10^(3/2) ~ 15.18, I3(-F) = -I3(F)",
            "reproduced": f"I3(F) = {forms['F']['I3']}, I3(-F) = {forms['minus_F']['I3']}",
            "verdict": "REPRODUCED" if forms["I3_F_abs_error"] < 1e-10 and forms["I3_minus_F_abs_error"] < 1e-10 else "NOT_REPRODUCED",
        },
        {
            "id": "I3_of_cayley",
            "claim": "unit Cayley form: I3 = 8*168/14^(3/2) ~ 25.66",
            "reproduced": f"I3(Cayley) = {forms['cayley']['I3']}",
            "verdict": "REPRODUCED" if forms["I3_cayley_abs_error"] < 1e-10 else "NOT_REPRODUCED",
        },
        {
            "id": "cubic_maximum",
            "claim": "F does not maximise I3 on the sphere; the maximum 25.66 is attained by the Cayley form",
            "reproduced": (
                f"max over {cubic['n_starts']} starts = {cubic['max_I3']} ({cubic['n_starts_at_max']} starts); "
                f"maximiser spectral distance to Cayley = {cubic['maximiser_spectral_distance_to_cayley']}"
            ),
            "verdict": (
                "REPRODUCED"
                if cubic["_best_value"] > I3_F_EXACT and abs(cubic["_best_value"] - I3_CAYLEY_EXACT) < 1e-8
                else "NOT_REPRODUCED"
            ),
        },
        {
            "id": "cayley_A_spectrum",
            "claim": "3/sqrt14 (x7), -1/sqrt14 (x21), 0 (x17)",
            "reproduced": f"A-spectrum x sqrt14 = {forms['cayley']['A_spectrum_times_sqrt14']}",
            "verdict": (
                "REPRODUCED"
                if forms["cayley"]["A_spectrum_times_sqrt14"] == [[-1.0, 21], [0.0, 17], [3.0, 7]]
                else "NOT_REPRODUCED"
            ),
        },
        {
            "id": "K_eigenvalues",
            "claim": "K = 24 on the singlet, 14 on the 54, 0 on the 4125",
            "reproduced": (
                f"K_1 = {representation['K_singlet']}, K_54 = {representation['K_54']}, "
                f"K_4125 = {representation['K_4125']} (C2(210) = {representation['C2_210']})"
            ),
            "verdict": (
                "REPRODUCED"
                if (representation["K_singlet"], representation["K_54"], representation["K_4125"]) == ("24", "14", "0")
                else "NOT_REPRODUCED"
            ),
        },
        {
            "id": "repo_slice_identities",
            "claim": "I_54 = (3a^2-3b^2+4c^2)^2/35, I_4125 = 80(a^2-b^2-c^2)^2/21 on a*A+b*B+c*C (repo normalization)",
            "reproduced": (
                f"Gram-level agreement, factor mine/repo = {slice_check['54']['fitted_factor_mine_over_repo']} (54), "
                f"{slice_check['4125']['fitted_factor_mine_over_repo']} (4125); max residual "
                f"{max(slice_check['54']['max_abs_gram_residual_factor_one'], slice_check['4125']['max_abs_gram_residual_factor_one'])}"
            ),
            "verdict": (
                "REPRODUCED_EXACTLY_FACTOR_ONE"
                if max(slice_check["54"]["max_abs_gram_residual_factor_one"], slice_check["4125"]["max_abs_gram_residual_factor_one"]) < 1e-9
                else "NOT_REPRODUCED"
            ),
        },
    ]
    return rows


def _method() -> dict[str, str]:
    return {
        "independence": "stdlib + numpy + scipy only; no repository module is imported",
        "representation_theory": (
            "Sym^2(210) and Lambda^2(210) formal characters from the 210 weights of Lambda^4; "
            "irreducible multiplicities by reflecting nu+rho into the D5 chamber with sign det(w) "
            "(Racah-Speiser); Weyl dimension formula; C2 = <lambda, lambda+2rho>. Confirmed by a "
            "fully reorthogonalised Lanczos run of K on a random symmetric input and by tr(K^k), "
            "k=0,1,2, of the sparse operator on Sym^2 and Lambda^2."
        ),
        "projectors": (
            "Pi_R = prod_{mu != K_R}(K - mu)/(K_R - mu) over the distinct K eigenvalues on Sym^2; "
            "Pi_54 and Pi_4125 share all but one factor (7 sparse K products per evaluation)."
        ),
        "objective": (
            "f(Phi) = ||Pi_54(Phi Phi^T)||_F^2 + ||Pi_4125(Phi Phi^T)||_F^2 on the unit sphere; "
            "grad f = 4 P Phi with P = (Pi_54 + Pi_4125)(Phi Phi^T); optimisers minimise f(x/|x|) "
            "with the exact homogeneous-function gradient."
        ),
        "fast_path": (
            "Inside the optimisers f uses the exact identity I_R = sum_i c_i J_i in the four "
            "O(10)-invariant quartic contractions; its coefficients are refitted against the "
            "projectors and its values/gradients re-verified on every run."
        ),
        "multistart": (
            "L-BFGS-B on f(x/|x|) with the fast path from standard-normal starts, then up to three "
            "polish passes (<=150 L-BFGS-B steps each) with the Casimir projectors themselves; the endpoint is "
            "classified by f (projectors), the sorted A-spectrum against A(F) and A(-F), and an "
            "explicit orbit witness s*omega_J^2/|omega_J^2| built from the complex structure J "
            "recovered from the extreme eigenvector of A(Phi)."
        ),
        "profile": (
            "For each t: an augmented Lagrangian (L-BFGS-B inner solves on f(x/|x|) + "
            "lambda*c + rho/2*c^2, c = I3(x/|x|) - t) from a continuation start and random starts"
            ", plus an SLSQP cross-check in the full run; g(t) is the best feasible value "
            "(|c| <= 1e-9), re-evaluated with the projectors."
        ),
        "local_analysis": (
            "Exact Hessian of f at F (210 projector applications) and Riemannian Hessian of I3 on "
            "the sphere; mu* = sup{mu : H_f + mu H_I3 >= 0 on T_F} by bisection gives the sharp "
            "small-delta slope of g."
        ),
        "cubic_maximum": "L-BFGS-B on -I3(x/|x|) from standard-normal starts",
    }


def _normalization() -> dict[str, str]:
    return {
        "basis": (
            "orthonormal component basis of Lambda^4 R^10: Phi = sum_{i<j<k<l} Phi_ijkl e_ijkl, "
            "|Phi|^2 = sum_{i<j<k<l} Phi_ijkl^2"
        ),
        "pair_space": (
            "210 (x) 210 as 210x210 matrices with the Frobenius product (orthonormal product basis); "
            "Phi (x) Phi = Phi Phi^T"
        ),
        "generators": "T_ab = e_a e_b^T - e_b e_a^T on R^10 (a<b), acting on Lambda^4 as derivations",
        "K": "K(W) = sum_{a<b} T_ab W T_ab^T = C2(210) - C2(R)/2 on channel R, C2(210) = 24",
        "channels": "54 = (2,0,0,0,0), 4125 = (2,2,2,0,0) (orthonormal-basis highest weights)",
        "quartics": "I_R(Phi) = ||Pi_R(Phi Phi^T)||_F^2",
        "cubic": (
            "I3(Phi) = sum over all ordered a..f of Phi_abcd Phi_cdef Phi_efab = 8 Tr A(Phi)^3, "
            "A_[ab],[cd] = Phi_abcd (a<b, c<d); the repository's Tr(A^3) is I3/8"
        ),
        "F": "F = (A+B)/sqrt(10) = omega^omega/|omega^omega|, omega = sum_k e_(2k-1)^e_(2k)",
        "cayley": "Phi_Cay = (A+C)/sqrt(14) = (omega_4^2/2 + Re Omega_4)/sqrt(14) on R^8 = C^4 (first 8 coordinates)",
        "delta": "delta = I3(F) - t",
        "repo_slice_normalization": (
            "The repository slice identities use the same orthonormal normalization: "
            "||Pi_R(Phi Phi^T)||^2 equals the repo formulas with factor 1."
        ),
    }


@lru_cache(maxsize=2)
def build_report(quick: bool = False) -> dict[str, Any]:
    config = QUICK_CONFIG if quick else FULL_CONFIG
    generators = generator_certificate()
    representation = representation_certificate()
    lanczos = lanczos_certificate()
    traces = trace_certificate()
    projectors = projector_certificate()
    forms = reference_form_certificate()
    contraction = contraction_identity_certificate()
    gradients = gradient_certificate()
    slice_check = slice_cross_check()
    local = local_second_order_analysis()
    multistart = run_multistart(config["multistart_starts"], SEEDS["multistart"])
    profile = run_profile(
        config["profile_delta_fractions"],
        config["profile_random_starts"],
        SEEDS["profile"],
        config["profile_slsqp_cross_check"],
    )
    profile_analysis = analyse_profile(profile, local["_mu_star_float"])
    cubic = run_cubic_maximum(config["cubic_starts"], SEEDS["cubic_maximum"])

    k54 = _channel_eigenvalue("54")
    k4125 = _channel_eigenvalue("4125")
    owners = representation["sym2_K_eigenvalue_owners"]
    counterexample = multistart["n_zero_off_orbit"] > 0 or profile["min_g_off_F"] <= ZERO_TOL
    flags = {
        "phi_orbit_lemma_proved": False,
        "numerical_evidence_only": True,
        "g3_closed": False,
        "whole_model_validated": False,
        "whole_model_excluded": False,
    }
    checks = {
        "generators_are_antisymmetric_signed_partial_permutations_112_nonzeros": (
            generators["nonzeros_per_generator"] == [112]
            and generators["absolute_entries"] == [1.0]
            and generators["max_antisymmetry_defect"] == 0.0
        ),
        "generators_close_the_so10_commutation_relations": generators["max_so10_commutation_defect"] == 0.0,
        "generators_equal_gl10_derivation_action": generators["max_gl10_derivation_defect"] == 0.0,
        "quadratic_casimir_on_210_equals_24": (
            generators["casimir_minus_sum_T2_defect_vs_24"] == 0.0 and representation["C2_210"] == 24
        ),
        "character_algorithm_sanity_lambda4_irreducible_and_10x10_is_1_45_54": (
            representation["lambda4_decomposition"] == {"[1, 1, 1, 1, 0]": 1}
            and representation["vector_square_decomposition"] == {"1": 1, "45": 1, "54": 1}
        ),
        "sym2_210_multiplicities_times_dimensions_sum_to_22155": (
            representation["sym2_dimension_sum"] == SYM2_DIMENSION == 22155
            and representation["sym2_all_multiplicities_positive"]
        ),
        "alt2_210_multiplicities_times_dimensions_sum_to_21945": (
            representation["alt2_dimension_sum"] == ALT2_DIMENSION == 21945
            and representation["alt2_all_multiplicities_positive"]
        ),
        "K_eigenvalues_singlet_24_54_14_4125_0": (
            (representation["K_singlet"], representation["K_54"], representation["K_4125"]) == ("24", "14", "0")
            and representation["dimension_54"] == 54
            and representation["dimension_4125"] == 4125
        ),
        "K_values_14_and_0_each_owned_by_a_single_sym2_irrep": (
            owners.get(str(k54)) == ["54"] and owners.get(str(k4125)) == ["4125"]
        ),
        "lanczos_confirms_distinct_sym2_K_eigenvalues": lanczos["matches_character_prediction"],
        "trace_identities_confirm_sym2_and_alt2_decompositions": traces["consistent"],
        "spectral_projectors_idempotent_on_random_symmetric_input": projectors["max_idempotence_defect"] < 1.0e-10,
        "spectral_projectors_complete_and_mutually_orthogonal": (
            projectors["completeness_defect"] < 1.0e-10
            and projectors["max_cross_overlap"] < 1.0e-10
            and projectors["shared_factor_helper_defect"] < 1.0e-10
        ),
        "projector_images_are_K_eigenspaces": projectors["max_eigenspace_residual"] < 1.0e-10,
        "eigenspace_dimensions_1_45_54_confirmed_by_projector_rank": (
            projectors["eigenspace_dimension_by_projector_rank_64_inputs"]
            == {"24": 1, "16": 45, str(_channel_eigenvalue("54")): 54}
        ),
        "direct_eigenvectors_identity_24_and_traceless_derivation_14": (
            projectors["K_identity_minus_24_identity"] < 1.0e-10
            and projectors["K_on_traceless_derivation_relative_defect_vs_14"] < 1.0e-10
            and projectors["traceless_derivation_outside_Pi54_relative"] < 1.0e-10
        ),
        "F_and_minus_F_are_projector_zeros_to_1e-12": all(
            forms[name][key] <= PROJECTOR_ZERO_TOL
            for name in ("F", "minus_F")
            for key in ("Pi54_frobenius_norm", "Pi4125_frobenius_norm")
        ),
        "I3_of_plus_minus_F_equals_plus_minus_8x60_over_10_to_3_2": (
            forms["I3_F_abs_error"] < 1.0e-10 and forms["I3_minus_F_abs_error"] < 1.0e-10
        ),
        "I3_equals_8_trace_A_cubed_bruteforce": forms["I3_equals_8_trace_A3_bruteforce_max_abs_error"] < 1.0e-10,
        "cayley_I3_equals_8x168_over_14_to_3_2": forms["I3_cayley_abs_error"] < 1.0e-10,
        "cayley_A_spectrum_3_minus1_0_over_sqrt14_with_7_21_17": (
            forms["cayley"]["A_spectrum_times_sqrt14"] == [[-1.0, 21], [0.0, 17], [3.0, 7]]
        ),
        "F_A_spectrum_4_1_minus1_over_sqrt10_with_1_20_24": (
            forms["F"]["A_spectrum_times_sqrt10"] == [[-1.0, 24], [1.0, 20], [4.0, 1]]
        ),
        "contraction_formula_matches_casimir_projectors": (
            contraction["max_abs_fitted_minus_rational"] < 1.0e-9
            and contraction["max_relative_value_error"] < 1.0e-10
            and contraction["max_relative_gradient_error_vs_4_P_Phi"] < 1.0e-10
        ),
        "analytic_gradients_match_finite_differences": gradients["passes"],
        "slice_I54_gram_equals_repo_formula": slice_check["54"]["max_abs_gram_residual_factor_one"] < 1.0e-9,
        "slice_I4125_gram_equals_repo_formula": slice_check["4125"]["max_abs_gram_residual_factor_one"] < 1.0e-9,
        "slice_normalization_factor_is_exactly_one": all(
            abs(slice_check[c]["fitted_factor_mine_over_repo"] - 1.0) < 1.0e-12 for c in ("54", "4125")
        ) and slice_check["max_abs_point_error"] < 1.0e-9,
        "slice_zero_locus_points_lie_on_plus_minus_F": all(
            entry["f_reference"] <= ZERO_TOL and entry["orbit"] == ("+F" if key.startswith("+") else "-F")
            for key, entry in slice_check["slice_zero_locus_c0_a2_eq_b2_orbits"].items()
        ),
        "F_is_critical_for_I3_and_hessian_kernel_is_orbit_20_plus_excess_10": (
            local["F_is_critical_point_of_I3_on_sphere"]
            and local["hessian_f_min_eigenvalue"] > -1.0e-9
            and local["hessian_f_kernel_dimension"] == 30
            and local["orbit_tangent_rank"] == 20
            and local["orbit_tangent_in_f_kernel_max_defect"] < 1.0e-9
        ),
        "excess_directions_raise_I3_so_F_is_a_saddle_of_I3": local["excess_directions_raise_I3"],
        "multistart_every_start_reached_a_zero": multistart["n_reached_zero"] == multistart["n_starts"],
        "multistart_every_zero_on_plus_or_minus_F_orbit": (
            multistart["n_zero_off_orbit"] == 0
            and multistart["n_plus_F"] + multistart["n_minus_F"] == multistart["n_reached_zero"]
        ),
        "multistart_endpoints_have_I3_equal_plus_minus_I3F": (
            multistart["max_abs_I3_minus_signed_I3F"] <= I3_ENDPOINT_TOL
        ),
        "profile_strictly_positive_off_F": profile["min_g_off_F"] > 1.0e-6,
        "profile_every_point_feasible_and_confirmed_by_two_runs": all(
            row.get("feasible_runs", 0) > 0 and row.get("runs_agreeing_with_best", 0) >= 2
            for row in profile["rows"][1:]
        ),
        "profile_fast_and_reference_objectives_agree_at_minimisers": all(
            row.get("fast_minus_reference_abs", 1.0) < 1.0e-10 for row in profile["rows"][1:]
        ),
        "profile_g_nondecreasing_in_delta": profile_analysis["g_nondecreasing_in_delta"],
        "profile_growth_at_least_quadratic_near_F": profile_analysis["growth_at_least_quadratic_near_F"],
        "profile_small_delta_slope_matches_exact_hessian_pencil": (
            profile_analysis["slope_matches_hessian"] and local["bisection_bracket_valid"]
        ),
        "profile_sign_symmetry_if_sampled": (
            profile_analysis["sign_symmetry_relative_difference_t_vs_minus_t"] is None
            or profile_analysis["sign_symmetry_relative_difference_t_vs_minus_t"] < 1.0e-6
        ),
        "cubic_multistart_maximum_exceeds_I3_F": cubic["_best_value"] > I3_F_EXACT + 1.0,
        "cubic_multistart_maximum_equals_cayley_value": abs(cubic["_best_value"] - I3_CAYLEY_EXACT) < 1.0e-8,
        "cubic_maximiser_A_spectrum_equals_cayley_spectrum": cubic["_cayley_distance"] < 1.0e-6,
        "fail_closed_flags_do_not_overclaim": (
            flags["phi_orbit_lemma_proved"] is False
            and flags["numerical_evidence_only"] is True
            and flags["g3_closed"] is False
            and flags["whole_model_validated"] is False
            and flags["whole_model_excluded"] is False
        ),
    }
    checks = {name: bool(value) for name, value in checks.items()}
    failures = [name for name, passed in checks.items() if not passed]
    if counterexample:
        status = STATUS_COUNTEREXAMPLE
    elif failures:
        status = STATUS_FAILED
    else:
        status = STATUS_SUPPORTS
    claims = _claims_table(multistart, profile_analysis, profile, cubic, representation, slice_check, forms, config)
    public_local = {k: v for k, v in local.items() if not k.startswith("_")}
    public_cubic = {k: v for k, v in cubic.items() if not k.startswith("_")}
    report = {
        "status": status,
        "mode": config["mode"],
        **flags,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "claims_vs_reproduced": claims,
        "method": _method(),
        "normalization": _normalization(),
        "config": {
            key: (list(value) if isinstance(value, tuple) else value) for key, value in config.items()
        },
        "seeds": dict(SEEDS),
        "representation_theory": {
            "sym2_210_decomposition": representation["sym2_rows"],
            "alt2_210_decomposition": representation["alt2_rows"],
            "sym2_dimension_sum": representation["sym2_dimension_sum"],
            "alt2_dimension_sum": representation["alt2_dimension_sum"],
            "sym2_distinct_K_eigenvalues": representation["sym2_distinct_K_eigenvalues"],
            "sym2_K_eigenvalue_owners": owners,
            "K_singlet_54_4125": [representation["K_singlet"], representation["K_54"], representation["K_4125"]],
            "lanczos": lanczos,
            "trace_identities": traces,
            "generators": generators,
            "projector_sanity": projectors,
        },
        "reference_forms": forms,
        "contraction_identity": contraction,
        "gradient_checks": gradients,
        "slice_cross_check": slice_check,
        "local_second_order_analysis_at_F": public_local,
        "multistart": multistart,
        "adversarial_profile": {
            "rows": profile["rows"],
            "min_g_off_F": _sig(profile["min_g_off_F"], 6),
            "analysis": profile_analysis,
        },
        "cubic_maximum": public_cubic,
        "verdict": _verdict_text(status, multistart, profile_analysis, cubic),
    }
    return _jsonable(report)


def _verdict_text(
    status: str, multistart: dict[str, Any], profile_analysis: dict[str, Any], cubic: dict[str, Any]
) -> str:
    if status == STATUS_COUNTEREXAMPLE:
        return (
            "A zero of Pi_54 and Pi_4125 off the +-F orbits (or a profile zero with I3 != +-I3(F)) "
            "was found; see multistart.anomalies and adversarial_profile.rows."
        )
    if status == STATUS_FAILED:
        return "At least one numerical check failed; the evidence is not usable until it is repaired."
    return (
        f"All {multistart['n_starts']} multistart runs end on SO(10).F ({multistart['n_plus_F']}) or "
        f"SO(10).(-F) ({multistart['n_minus_F']}), certified by A-spectrum and an explicit orbit witness; "
        f"the constrained profile g(t) is strictly positive for I3(F) > t >= 0; near F its growth law is "
        f"'{profile_analysis['growth_law_near_F']}' (fitted slope {profile_analysis['fit_linear_slope_a']} vs "
        f"exact {profile_analysis['hessian_slope_mu_star']}; the claimed 1.9e-3*delta^2 law is checked in "
        f"claims_vs_reproduced); g(0) = {profile_analysis['g_at_I3_zero']}. "
        f"I3 is maximised by the Cayley form ({cubic['max_I3']}), not by F. This is numerical evidence for "
        "the signed two-orbit statement only: the lemma is not proved, G3 stays open and the whole model is "
        "neither validated nor excluded."
    )


def _markdown(report: dict[str, Any]) -> str:
    rep = report["representation_theory"]
    multistart = report["multistart"]
    profile = report["adversarial_profile"]
    analysis = profile["analysis"]
    cubic = report["cubic_maximum"]
    local = report["local_second_order_analysis_at_F"]
    lines = [
        "# G3 Phi-orbit lemma: independent numerical evidence -- v20",
        "",
        f"**Status:** `{report['status']}`  ",
        f"**Mode:** `{report['mode']}`; checks: {report['n_checks'] - report['n_failed']}/{report['n_checks']} passed",
        "",
        report["verdict"],
        "",
        "Flags: "
        + ", ".join(
            f"`{key}={report[key]}`"
            for key in (
                "phi_orbit_lemma_proved",
                "numerical_evidence_only",
                "g3_closed",
                "whole_model_validated",
                "whole_model_excluded",
            )
        ),
        "",
        "Independent of the repository projector code (stdlib + numpy + scipy only).",
        "",
        "## Sym^2(210) and the pair Casimir K",
        "",
        "| irrep | highest weight | mult | C2 | K |",
        "|---|---|---|---|---|",
    ]
    for row in rep["sym2_210_decomposition"]:
        lines.append(
            f"| {row['irrep']} | {tuple(row['highest_weight_orthonormal'])} | {row['multiplicity']} | "
            f"{row['C2']} | {row['K_eigenvalue']} |"
        )
    lines += [
        "",
        f"Dimension sum {rep['sym2_dimension_sum']}; distinct K eigenvalues {rep['sym2_distinct_K_eigenvalues']} "
        f"(Lanczos Krylov dimension {rep['lanczos']['krylov_dimension']}, max Ritz defect "
        f"{rep['lanczos']['max_abs_ritz_minus_prediction']}); max projector idempotence defect "
        f"{rep['projector_sanity']['max_idempotence_defect']}.",
        "",
        "## Slice cross-check against the repository identities",
        "",
        f"- I_54: factor mine/repo = {report['slice_cross_check']['54']['fitted_factor_mine_over_repo']}, "
        f"Gram residual {report['slice_cross_check']['54']['max_abs_gram_residual_factor_one']};",
        f"- I_4125: factor mine/repo = {report['slice_cross_check']['4125']['fitted_factor_mine_over_repo']}, "
        f"Gram residual {report['slice_cross_check']['4125']['max_abs_gram_residual_factor_one']}.",
        "",
        "## Multistart",
        "",
        f"- {multistart['n_reached_zero']}/{multistart['n_starts']} starts reach f <= {multistart['tolerances']['zero_f_reference']}; "
        f"+F: {multistart['n_plus_F']}, -F: {multistart['n_minus_F']}, off-orbit zeros: {multistart['n_zero_off_orbit']}, "
        f"nonzero local minima: {multistart['n_nonzero_local_minima']};",
        f"- after the projector polish: max f = {multistart['max_f_reference_after_polish']}, max spectral distance "
        f"{multistart['max_spectral_distance_to_assigned_orbit']} (tol {multistart['tolerances']['sorted_A_spectrum_max_abs']}), "
        f"max witness distance {multistart['max_witness_distance']} (tol {multistart['tolerances']['orbit_witness_distance']}); "
        f"distance to the other orbit >= {multistart['min_spectral_distance_to_other_orbit']}.",
        "",
        "## Adversarial profile g(t) = min{f : |Phi|=1, I3=t}",
        "",
        "| delta/I3(F) | t | g | g/delta | g/delta^2 | runs agreeing |",
        "|---|---|---|---|---|---|",
    ]
    for row in profile["rows"]:
        if row["delta_over_I3F"] == 0.0:
            lines.append(f"| 0 | {row['t']} | 0 | - | - | (F) |")
            continue
        if "g" not in row:
            lines.append(f"| {row['delta_over_I3F']} | {row['t']} | no feasible run | - | - | 0 |")
            continue
        lines.append(
            f"| {row['delta_over_I3F']} | {row['t']} | {row['g']} | {row['g_over_delta']} | "
            f"{row['g_over_delta_squared']} | {row['runs_agreeing_with_best']}/{row['feasible_runs']} |"
        )
    lines += [
        "",
        f"Small-delta law: g/delta -> {analysis['fit_linear_slope_a']} (fit) vs mu* = {analysis['hessian_slope_mu_star']} "
        f"(exact Hessian pencil, closed form {local['mu_star_closed_form_candidate']}); g/delta^2 drifts by a factor "
        f"{analysis['pure_quadratic_coefficient_drift_max_over_min']} over the four smallest delta; growth law: "
        f"{analysis['growth_law_near_F']}. Excess (5+5bar) kernel directions of the f-Hessian raising I3: "
        f"{local['excess_directions_raise_I3']} (curvature +{local['excess_I3_curvature_expected']} on "
        f"{local['excess_directions']} directions), i.e. F is a saddle of I3 on the sphere.",
        "",
        "## Cubic maximum",
        "",
        f"max I3 = {cubic['max_I3']} over {cubic['n_starts']} starts ({cubic['n_starts_at_max']} at the max) vs "
        f"I3(F) = {cubic['I3_F']}; maximiser A-spectrum x sqrt14 = {cubic['maximiser_A_spectrum_times_sqrt14']} "
        "(Cayley form).",
        "",
        "## Claims vs reproduced",
        "",
        "| claim | reproduced | verdict |",
        "|---|---|---|",
    ]
    for row in report["claims_vs_reproduced"]:
        lines.append(f"| {row['claim']} | {row['reproduced']} | `{row['verdict']}` |")
    lines += ["", f"Failures: {report['failures'] if report['failures'] else 'none'}", ""]
    return "\n".join(lines)


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(_markdown(report), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="write the JSON and Markdown reports")
    parser.add_argument("--quick", action="store_true", help="few starts and profile points (smoke run)")
    args = parser.parse_args(argv)
    report = build_report(quick=args.quick)
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
