#!/usr/bin/env python3
"""Exact census and universal map for the rank-one SU(4) augmented SOS.

Let ``W = R*t (+) Phi210`` and let ``Z = Sym^2(W)`` be the homogeneous
degree-two monomial representation used by a quartic Gram/SOS ansatz.  This
module certifies, with exact integer and rational arithmetic, the SU(4)
character census of ``Z`` and the universal multiplication map

    mu : Sym^2(Sym^2(W)) -> Sym^4(W).

The live ``Phi210`` weight character is read from the certified rank-one
intertwiner chain.  Gelfand--Tsetlin characters and exact highest-weight
subtraction give 35 complex isotypic types and 824 irreducible copies in
``Z``.  Conjugation groups them into 9 real-symmetric and 13
complex-Hermitian isotypic blocks.  Their 22 Schur cones contain 19,594 real
Gram parameters.  The grading by Phi-degree is
``[1, 4, 90, 1414, 18085]``.

The invariant quartic target dimensions are computed independently from
``Sym^k(Phi210)``, using the Weyl alternating formula, and are
``[1, 4, 45, 478, 6057]``.  A natural rational GL(W)-equivariant section of
``mu`` is the average of the three pairings of four vectors.  Therefore the
restriction of ``mu`` to every invariant Phi-degree sector is surjective;
its exact abstract ranks and nullities follow without floating point.

This is deliberately *not* the Schur-coordinate coefficient matrix.  The 35
full isotypic carrier maps spanning all 824 irreducible copies of
``Sym^2(W)`` have not yet been constructed, nor have invariant cubic and
quartic target bases.  Thus the 6,585-row by 19,594-column coordinate map, the
PSD feasibility problem, an arbitrary-Phi lower bound, and G3 all remain
open.  In particular, the full 1,414-variable ``t*Phi <-> Phi^2`` cross
sector is counted and an abstract interface reserves its 478 cubic equations
with zero right-hand side.  The physical G3 gap target vector has not been
constructed, so this reservation is not a certification of its cubic
coefficients.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import copy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from scipy import sparse

import exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20 as aligned
import exact_gauged_u1x_g3_rank1_su4_phi210_intertwiners_v20 as intertwiners
import exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20 as quadratics


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json"
OUT_MD = ROOT / "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
STATUS = "EXACT_RANK1_SU4_AUGMENTED_SOS_CENSUS_AND_UNIVERSAL_MAP_CERTIFIED"
OVERALL_STATE = "SU4_AUGMENTED_SOS_CENSUS_CLOSED__SCHUR_EMBEDDINGS_SDP_AND_G3_OPEN"

PHI_DIMENSION = 210
AUGMENTED_LINEAR_DIMENSION = 211
HOMOGENEOUS_QUADRATIC_DIMENSION = 22_366
SCHUR_REAL_PARAMETER_COUNT = 19_594
INVARIANT_QUARTIC_EQUATION_COUNT = 6_585
EXPECTED_DOMAIN_GRADE_COUNTS = (1, 4, 90, 1_414, 18_085)
EXPECTED_TARGET_GRADE_COUNTS = (1, 4, 45, 478, 6_057)
EXPECTED_KERNEL_GRADE_COUNTS = (0, 0, 45, 936, 12_028)
EXPECTED_CUBIC_CROSS_PARAMETER_COUNT = 1_414
EXPECTED_CUBIC_ZERO_RHS_ROW_COUNT = 478
EXPECTED_COMPLEX_ISOTYPIC_TYPE_COUNT = 35
EXPECTED_IRREDUCIBLE_COPY_GRADE_COUNTS = (1, 25, 798)
EXPECTED_IRREDUCIBLE_COPY_COUNT = 824

EXPECTED_ALIGNED_MODULE = "exact_gauged_u1x_g3_rank1_su4_aligned_carriers_v20.py"
EXPECTED_QUADRATIC_MODULE = (
    "exact_gauged_u1x_g3_rank1_su4_phi210_quadratic_basis_v20.py"
)
# These source hashes bind the exact APIs used to create this certificate.
# They are intentionally fail-closed and must be updated only after a fresh
# exact audit if either frozen companion is deliberately changed.
EXPECTED_ALIGNED_SOURCE_SHA256 = (
    "5671857444bda7d53db45393e28a3b9ac0784d0f2a63aa1e541eb5e356d23ccc"
)
EXPECTED_QUADRATIC_SOURCE_SHA256 = (
    "4eec63ba40b888de736c84f607019ba0f21915028b423578502893744bab1060"
)
EXPECTED_ALIGNED_REPORT_SHA256 = (
    "d2da0572dc33a1f3f88b5ac5df3343201650ca660498f34ff59806a607015c67"
)
EXPECTED_ALIGNMENT_CERTIFICATE_SHA256 = (
    "f74b7845b57472f62773c398fa927b551b5d9d09f86bd7defb92a6ed71adbe15"
)
EXPECTED_QUADRATIC_REPORT_SHA256 = (
    "497a8c1db29e7d88f30bd1cc68902cc7981da4a3fefd5586bd15bad323d1e259"
)
EXPECTED_QUADRATIC_BASIS_SHA256 = (
    "27c0649758c87aa2cbe39ae04596f4bd6df511ba3ca4004013bdcf936599b694"
)

EXPECTED_ALIGNED_STATUS = (
    "EXACT_RANK1_SU4_ALIGNED_CARRIER_INFRASTRUCTURE_CERTIFIED"
)
EXPECTED_ALIGNED_OVERALL_STATE = (
    "SU4_ALIGNED_CARRIERS_CLOSED__INVARIANT_BASIS_SDP_AND_G3_OPEN"
)
EXPECTED_QUADRATIC_STATUS = (
    "EXACT_RANK1_SU4_PHI210_QUADRATIC_BASIS_CERTIFIED"
)
EXPECTED_QUADRATIC_OVERALL_STATE = (
    "SU4_INVARIANT_QUADRATIC_BASIS_CLOSED__AUGMENTED_SDP_AND_G3_OPEN"
)

DynkinWeight = tuple[int, int, int]
QuadraticMonomial = tuple[int, int]
QuarticMonomial = tuple[int, int, int, int]

# Exact complexified branching of the live real Phi210 representation.
EXPECTED_PHI_BRANCHING: dict[DynkinWeight, int] = {
    (0, 0, 0): 4,
    (1, 0, 0): 4,
    (0, 0, 1): 4,
    (0, 1, 0): 4,
    (1, 0, 1): 2,
    (2, 0, 0): 1,
    (0, 0, 2): 1,
    (1, 1, 0): 2,
    (0, 1, 1): 2,
    (0, 2, 0): 1,
}

# Exact decomposition of Z = 1 (+) Phi (+) Sym^2(Phi).  This independent
# expected table makes character/census drift fail closed.
EXPECTED_AUGMENTED_MULTIPLICITIES: dict[DynkinWeight, int] = {
    (0, 0, 0): 50,
    (0, 0, 1): 64,
    (0, 0, 2): 40,
    (0, 0, 3): 8,
    (0, 0, 4): 1,
    (0, 1, 0): 66,
    (0, 1, 1): 64,
    (0, 1, 2): 19,
    (0, 1, 3): 2,
    (0, 2, 0): 43,
    (0, 2, 1): 20,
    (0, 2, 2): 4,
    (0, 3, 0): 6,
    (0, 3, 1): 2,
    (0, 4, 0): 1,
    (1, 0, 0): 64,
    (1, 0, 1): 71,
    (1, 0, 2): 30,
    (1, 0, 3): 3,
    (1, 1, 0): 64,
    (1, 1, 1): 42,
    (1, 1, 2): 8,
    (1, 2, 0): 20,
    (1, 2, 1): 6,
    (1, 3, 0): 2,
    (2, 0, 0): 40,
    (2, 0, 1): 30,
    (2, 0, 2): 9,
    (2, 1, 0): 19,
    (2, 1, 1): 8,
    (2, 2, 0): 4,
    (3, 0, 0): 8,
    (3, 0, 1): 3,
    (3, 1, 0): 2,
    (4, 0, 0): 1,
}

CARTAN_MATRIX: tuple[DynkinWeight, ...] = (
    (2, -1, 0),
    (-1, 2, -1),
    (0, -1, 2),
)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Counter):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def _file_sha256(path: Path) -> str:
    # Git may materialize text sources with CRLF on Windows.  Provenance is
    # bound to the repository's canonical LF byte stream on every platform.
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(
        _jsonable(value), ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _character_sha256(character: Mapping[DynkinWeight, int]) -> str:
    rows = tuple(
        (weight, int(multiplicity))
        for weight, multiplicity in sorted(character.items())
        if multiplicity
    )
    return _canonical_json_sha256(rows)


def _sparse_sequence_sha256(matrices: Iterable[sparse.spmatrix]) -> str:
    digest = hashlib.sha256()
    for matrix in matrices:
        value = matrix.tocsr(copy=True)
        value.sum_duplicates()
        value.sort_indices()
        value.eliminate_zeros()
        digest.update(np.asarray(value.shape, dtype="<i8").tobytes())
        digest.update(np.asarray(value.indptr, dtype="<i8").tobytes())
        digest.update(np.asarray(value.indices, dtype="<i8").tobytes())
        digest.update(np.asarray(value.data, dtype="<i8").tobytes())
    return digest.hexdigest()


def _validate_dynkin(weight: Sequence[int]) -> DynkinWeight:
    if len(weight) != 3:
        raise ValueError("an SU(4) Dynkin weight must have length three")
    if any(isinstance(entry, bool) or not isinstance(entry, (int, np.integer)) for entry in weight):
        raise TypeError("Dynkin coordinates must be exact integers")
    return tuple(int(entry) for entry in weight)  # type: ignore[return-value]


@lru_cache(maxsize=None)
def _gl4_irrep_character_cached(highest_weight: DynkinWeight) -> Counter[DynkinWeight]:
    """Return an exact A3 character by Gelfand--Tsetlin enumeration."""
    a, b, c = _validate_dynkin(highest_weight)
    if min(a, b, c) < 0:
        raise ValueError("highest-weight Dynkin coordinates must be nonnegative")
    top = (a + b + c, b + c, c, 0)
    character: Counter[DynkinWeight] = Counter()
    for x0 in range(top[1], top[0] + 1):
        for x1 in range(top[2], top[1] + 1):
            for x2 in range(top[3], top[2] + 1):
                row3 = (x0, x1, x2)
                for y0 in range(row3[1], row3[0] + 1):
                    for y1 in range(row3[2], row3[1] + 1):
                        row2 = (y0, y1)
                        for z0 in range(row2[1], row2[0] + 1):
                            counts = (
                                z0,
                                sum(row2) - z0,
                                sum(row3) - sum(row2),
                                sum(top) - sum(row3),
                            )
                            weight = (
                                counts[0] - counts[1],
                                counts[1] - counts[2],
                                counts[2] - counts[3],
                            )
                            character[weight] += 1
    return character


def gl4_irrep_character(highest_weight: Sequence[int]) -> dict[DynkinWeight, int]:
    """Return a mutation-isolated exact character for an SU(4) irrep."""
    return dict(_gl4_irrep_character_cached(_validate_dynkin(highest_weight)))


def _weyl_dimension(highest_weight: DynkinWeight) -> int:
    a, b, c = highest_weight
    partition = (a + b + c, b + c, c, 0)
    dimension = Fraction(1)
    for left in range(4):
        for right in range(left + 1, 4):
            dimension *= Fraction(
                partition[left] - partition[right] + right - left,
                right - left,
            )
    if dimension.denominator != 1:
        raise ArithmeticError("Weyl dimension ceased to be integral")
    return dimension.numerator


def frobenius_schur_indicator(highest_weight: Sequence[int]) -> int:
    """Return the exact SU(4) Frobenius--Schur indicator ``+1, 0, -1``.

    An SU(4) irrep ``(a,b,c)`` is self-conjugate exactly when ``a == c``.
    For a self-conjugate irrep, Kostant's formula evaluates the indicator at
    ``exp(2*pi*i*rho^vee) = -I``.  Its central character is
    ``(-1)^(a+2b+3c)``.  Non-self-conjugate irreps have indicator zero.
    """
    a, b, c = _validate_dynkin(highest_weight)
    if min(a, b, c) < 0:
        raise ValueError("highest-weight Dynkin coordinates must be nonnegative")
    if a != c:
        return 0
    box_count = a + 2 * b + 3 * c
    return 1 if box_count % 2 == 0 else -1


@lru_cache(maxsize=1)
def _phi_weight_character_cached() -> Counter[DynkinWeight]:
    weights = intertwiners.exterior_state_weights()
    if len(weights) != PHI_DIMENSION:
        raise ArithmeticError("live Phi210 weight census drifted")
    return Counter(_validate_dynkin(weight) for weight in weights)


def phi_weight_character() -> dict[DynkinWeight, int]:
    return dict(_phi_weight_character_cached())


@lru_cache(maxsize=1)
def _symmetric_power_characters_cached() -> tuple[Counter[DynkinWeight], ...]:
    """Return Sym^k(Phi), 0<=k<=4, by an exact weight generating function."""
    characters = [Counter({(0, 0, 0): 1})] + [Counter() for _ in range(4)]
    for weight, multiplicity in _phi_weight_character_cached().items():
        updated = [Counter() for _ in range(5)]
        for degree in range(5):
            for old_weight, old_multiplicity in characters[degree].items():
                for added_degree in range(5 - degree):
                    new_weight = tuple(
                        old_weight[axis] + added_degree * weight[axis]
                        for axis in range(3)
                    )
                    coefficient = math.comb(
                        multiplicity + added_degree - 1, added_degree
                    )
                    updated[degree + added_degree][new_weight] += (
                        old_multiplicity * coefficient
                    )
        characters = updated
    return tuple(characters)


def symmetric_power_character(degree: int) -> dict[DynkinWeight, int]:
    if isinstance(degree, bool) or not isinstance(degree, int):
        raise TypeError("symmetric-power degree must be an integer")
    if not 0 <= degree <= 4:
        raise ValueError("this certificate constructs degrees zero through four")
    return dict(_symmetric_power_characters_cached()[degree])


@lru_cache(maxsize=1)
def _augmented_character_cached() -> Counter[DynkinWeight]:
    character = _symmetric_power_characters_cached()[2].copy()
    character.update(_phi_weight_character_cached())
    character[(0, 0, 0)] += 1
    return character


def augmented_homogeneous_character() -> dict[DynkinWeight, int]:
    """Return the exact character of Sym^2(R*t (+) Phi210)."""
    return dict(_augmented_character_cached())


def _highest_weight_score(weight: DynkinWeight) -> int:
    # Twice pairing with the sum of fundamental coweights.  Subtracting any
    # simple root lowers this score by exactly two.
    return 3 * weight[0] + 4 * weight[1] + 3 * weight[2]


def _decompose_character(
    character: Mapping[DynkinWeight, int],
) -> tuple[dict[DynkinWeight, int], bool]:
    residual: Counter[DynkinWeight] = Counter(
        {
            _validate_dynkin(weight): int(multiplicity)
            for weight, multiplicity in character.items()
            if multiplicity
        }
    )
    if any(multiplicity < 0 for multiplicity in residual.values()):
        raise ValueError("a character cannot contain negative weight multiplicities")
    decomposition: Counter[DynkinWeight] = Counter()
    while residual:
        maximum_score = max(_highest_weight_score(weight) for weight in residual)
        dominant = [
            weight
            for weight in residual
            if min(weight) >= 0 and _highest_weight_score(weight) == maximum_score
        ]
        if not dominant:
            return dict(decomposition), False
        highest = max(dominant)
        multiplicity = residual[highest]
        decomposition[highest] += multiplicity
        for weight, irrep_multiplicity in _gl4_irrep_character_cached(highest).items():
            residual[weight] -= multiplicity * irrep_multiplicity
            if residual[weight] < 0:
                return dict(decomposition), False
            if residual[weight] == 0:
                del residual[weight]
    return dict(decomposition), True


def exact_character_decompositions() -> dict[str, dict[DynkinWeight, int]]:
    """Return exact irreducible multiplicities used by the block census."""
    phi, phi_zero = _decompose_character(_phi_weight_character_cached())
    sym2, sym2_zero = _decompose_character(_symmetric_power_characters_cached()[2])
    augmented, augmented_zero = _decompose_character(_augmented_character_cached())
    if not (phi_zero and sym2_zero and augmented_zero):
        raise ArithmeticError("exact highest-weight subtraction left a residual")
    return {
        "Phi210": phi,
        "Sym2_Phi210": sym2,
        "augmented_degree2": augmented,
    }


def _simple_reflection(weight: DynkinWeight, simple_root: int) -> DynkinWeight:
    return tuple(
        weight[axis] - weight[simple_root] * CARTAN_MATRIX[simple_root][axis]
        for axis in range(3)
    )  # type: ignore[return-value]


@lru_cache(maxsize=1)
def _weyl_rho_orbit_with_sign() -> tuple[tuple[DynkinWeight, int], ...]:
    rho: DynkinWeight = (1, 1, 1)
    signs: dict[DynkinWeight, int] = {rho: 1}
    queue: deque[DynkinWeight] = deque((rho,))
    while queue:
        weight = queue.popleft()
        for simple_root in range(3):
            reflected = _simple_reflection(weight, simple_root)
            sign = -signs[weight]
            if reflected in signs:
                if signs[reflected] != sign:
                    raise ArithmeticError("inconsistent Weyl parity")
                continue
            signs[reflected] = sign
            queue.append(reflected)
    if len(signs) != 24:
        raise ArithmeticError("A3 Weyl group census drifted")
    return tuple(sorted(signs.items()))


def _trivial_multiplicity(character: Mapping[DynkinWeight, int]) -> int:
    """Exact Weyl alternating extraction of the trivial character."""
    rho = (1, 1, 1)
    value = sum(
        sign
        * int(
            character.get(
                tuple(rho[axis] - image[axis] for axis in range(3)), 0
            )
        )
        for image, sign in _weyl_rho_orbit_with_sign()
    )
    if value < 0:
        raise ArithmeticError("trivial multiplicity became negative")
    return value


def target_invariant_grade_counts() -> tuple[int, ...]:
    """Return dim Sym^k(Phi210)^SU4 for 0<=k<=4 exactly."""
    return tuple(
        _trivial_multiplicity(character)
        for character in _symmetric_power_characters_cached()
    )


def _grade_parameter_counts(kind: str, multiplicities: Sequence[int]) -> tuple[int, ...]:
    if len(multiplicities) != 3:
        raise ValueError("expected homogeneous grades zero, one, and two")
    output = [0] * 5
    for left, left_multiplicity in enumerate(multiplicities):
        for right in range(left, 3):
            right_multiplicity = multiplicities[right]
            if left == right:
                if kind == "real_symmetric":
                    contribution = left_multiplicity * (left_multiplicity + 1) // 2
                elif kind == "complex_Hermitian":
                    contribution = left_multiplicity**2
                else:
                    raise ValueError("unknown real Schur block kind")
            else:
                contribution = left_multiplicity * right_multiplicity
                if kind == "complex_Hermitian":
                    contribution *= 2
            output[left + right] += contribution
    return tuple(output)


@lru_cache(maxsize=1)
def _isotypic_blocks_cached() -> tuple[dict[str, Any], ...]:
    decompositions = exact_character_decompositions()
    phi = decompositions["Phi210"]
    sym2 = decompositions["Sym2_Phi210"]
    augmented = decompositions["augmented_degree2"]
    rows: list[dict[str, Any]] = []
    for highest in sorted(augmented):
        conjugate = (highest[2], highest[1], highest[0])
        if highest[0] > highest[2]:
            continue
        self_conjugate = highest == conjugate
        if not self_conjugate and augmented.get(conjugate) != augmented[highest]:
            raise ArithmeticError("complex conjugate multiplicities drifted")
        indicator = frobenius_schur_indicator(highest)
        if self_conjugate and indicator != 1:
            raise ArithmeticError("a self-conjugate SU(4) constituent ceased to be real type")
        if not self_conjugate and indicator != 0:
            raise ArithmeticError("a complex SU(4) constituent acquired a nonzero indicator")
        multiplicities = (
            1 if highest == (0, 0, 0) else 0,
            phi.get(highest, 0),
            sym2.get(highest, 0),
        )
        if sum(multiplicities) != augmented[highest]:
            raise ArithmeticError("graded isotypic multiplicities do not add")
        kind = "real_symmetric" if self_conjugate else "complex_Hermitian"
        parameter_grades = _grade_parameter_counts(kind, multiplicities)
        irrep_dimension = _weyl_dimension(highest)
        rows.append(
            {
                "representative_dynkin": highest,
                "conjugate_dynkin": conjugate,
                "self_conjugate": self_conjugate,
                "young_diagram_box_count": (
                    highest[0] + 2 * highest[1] + 3 * highest[2]
                ),
                "Frobenius_Schur_indicator": indicator,
                "Frobenius_Schur_type": (
                    "real" if indicator == 1 else "complex"
                ),
                "real_block_kind": kind,
                "PSD_cone": (
                    f"S_+^{augmented[highest]}(R)"
                    if self_conjugate
                    else f"Herm_+^{augmented[highest]}(C)"
                ),
                "irrep_complex_dimension": irrep_dimension,
                "graded_multiplicities_t2_tPhi_Phi2": multiplicities,
                "multiplicity_matrix_order": augmented[highest],
                "real_Schur_parameter_count": sum(parameter_grades),
                "real_parameter_grade_counts": parameter_grades,
                "cubic_tPhi_to_Phi2_cross_real_parameter_count": parameter_grades[3],
                "represented_real_dimension": (
                    augmented[highest] * irrep_dimension
                    if self_conjugate
                    else 2 * augmented[highest] * irrep_dimension
                ),
                "coordinate_convention": (
                    "real symmetric multiplicity matrix; diagonal-grade blocks "
                    "are symmetric and cross-grade rectangles are real"
                    if self_conjugate
                    else "complex Hermitian multiplicity matrix; diagonal-grade "
                    "blocks are Hermitian and each cross-grade complex rectangle "
                    "contributes twice its complex entry count in real variables"
                ),
                "Frobenius_Schur_type_argument": (
                    "For a self-conjugate SU(4) highest weight (a,b,a), "
                    "the Young-diagram box count is 4a+2b and is even. "
                    "Kostant's indicator is the action of exp(2*pi*i*rho^vee)="
                    "-I, hence the computed indicator is +1: every "
                    "self-conjugate isotypic type here is "
                    "real, not quaternionic."
                    if self_conjugate
                    else "The paired highest weights (a,b,c) and (c,b,a) form "
                    "one real isotypic component of complex type; its self-"
                    "adjoint commutant is a complex Hermitian multiplicity block."
                ),
            }
        )
    return tuple(rows)


def exact_augmented_isotypic_blocks() -> tuple[dict[str, Any], ...]:
    return copy.deepcopy(_isotypic_blocks_cached())


def schur_parameter_grade_counts() -> tuple[int, ...]:
    return tuple(
        sum(row["real_parameter_grade_counts"][grade] for row in _isotypic_blocks_cached())
        for grade in range(5)
    )


def _validate_linear_index(index: int) -> int:
    if isinstance(index, bool) or not isinstance(index, (int, np.integer)):
        raise TypeError("monomial indices must be exact integers")
    value = int(index)
    if not 0 <= value < AUGMENTED_LINEAR_DIMENSION:
        raise ValueError("monomial index lies outside R*t (+) Phi210")
    return value


def _canonical_quadratic_monomial(indices: Sequence[int]) -> QuadraticMonomial:
    if len(indices) != 2:
        raise ValueError("a quadratic monomial requires two indices")
    return tuple(sorted(_validate_linear_index(index) for index in indices))  # type: ignore[return-value]


def _canonical_quartic_monomial(indices: Sequence[int]) -> QuarticMonomial:
    if len(indices) != 4:
        raise ValueError("a quartic monomial requires four indices")
    return tuple(sorted(_validate_linear_index(index) for index in indices))  # type: ignore[return-value]


def raw_gram_entry_image(
    left: Sequence[int], right: Sequence[int]
) -> tuple[QuarticMonomial, int]:
    """Return the polynomial image of one symmetric Gram-matrix entry.

    The returned scale is one on a diagonal entry and two off diagonal,
    matching ``z.T @ Q @ z`` for symmetric ``Q``.
    """
    left_pair = _canonical_quadratic_monomial(left)
    right_pair = _canonical_quadratic_monomial(right)
    quartic = _canonical_quartic_monomial(left_pair + right_pair)
    return quartic, 1 if left_pair == right_pair else 2


def polarized_section_tensor_terms(
    quartic: Sequence[int],
) -> tuple[tuple[QuadraticMonomial, QuadraticMonomial, Fraction], ...]:
    """Exact GL(W)-equivariant section in symmetric-tensor coordinates.

    The section is one third of the sum over the three pair partitions of
    four slots.  Equal terms are combined exactly.
    """
    indices = _canonical_quartic_monomial(quartic)
    pairings = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
    coefficients: Counter[tuple[QuadraticMonomial, QuadraticMonomial]] = Counter()
    for left_slots, right_slots in pairings:
        left = _canonical_quadratic_monomial(tuple(indices[slot] for slot in left_slots))
        right = _canonical_quadratic_monomial(tuple(indices[slot] for slot in right_slots))
        if right < left:
            left, right = right, left
        coefficients[(left, right)] += 1
    return tuple(
        (left, right, Fraction(count, 3))
        for (left, right), count in sorted(coefficients.items())
    )


def polarized_section_gram_entries(
    quartic: Sequence[int],
) -> tuple[tuple[QuadraticMonomial, QuadraticMonomial, Fraction], ...]:
    """Return the same section in symmetric Gram-matrix entry convention."""
    return tuple(
        (left, right, coefficient / (1 if left == right else 2))
        for left, right, coefficient in polarized_section_tensor_terms(quartic)
    )


def _section_identity_exact(quartic: Sequence[int]) -> bool:
    target = _canonical_quartic_monomial(quartic)
    tensor_total = Fraction(0)
    for left, right, coefficient in polarized_section_tensor_terms(target):
        image, _ = raw_gram_entry_image(left, right)
        if image != target:
            return False
        tensor_total += coefficient
    gram_total = Fraction(0)
    for left, right, coefficient in polarized_section_gram_entries(target):
        image, scale = raw_gram_entry_image(left, right)
        if image != target:
            return False
        gram_total += scale * coefficient
    return tensor_total == gram_total == 1


def _universal_map_certificate() -> dict[str, Any]:
    raw_source_grades = [0] * 5
    quadratic_grades = (1, PHI_DIMENSION, PHI_DIMENSION * (PHI_DIMENSION + 1) // 2)
    for left, left_dimension in enumerate(quadratic_grades):
        for right in range(left, 3):
            right_dimension = quadratic_grades[right]
            raw_source_grades[left + right] += (
                left_dimension * (left_dimension + 1) // 2
                if left == right
                else left_dimension * right_dimension
            )
    raw_target_grades = tuple(
        math.comb(PHI_DIMENSION + degree - 1, degree) for degree in range(5)
    )
    representatives = (
        (0, 0, 0, 0),
        (0, 0, 0, 1),
        (0, 0, 1, 1),
        (0, 0, 1, 2),
        (0, 1, 1, 1),
        (0, 1, 1, 2),
        (0, 1, 2, 3),
        (1, 1, 1, 1),
        (1, 1, 1, 2),
        (1, 1, 2, 2),
        (1, 1, 2, 3),
        (1, 2, 3, 4),
    )
    representative_checks = tuple(_section_identity_exact(row) for row in representatives)
    return {
        "linear_space": "W=R*t (+) Phi210",
        "linear_dimension": AUGMENTED_LINEAR_DIMENSION,
        "quadratic_monomial_space": "Z=Sym^2(W)",
        "quadratic_monomial_dimension": HOMOGENEOUS_QUADRATIC_DIMENSION,
        "raw_symmetric_Gram_dimension": sum(raw_source_grades),
        "raw_quartic_polynomial_dimension": sum(raw_target_grades),
        "raw_domain_grade_dimensions": tuple(raw_source_grades),
        "raw_target_grade_dimensions": raw_target_grades,
        "raw_grade_ranks_exact": raw_target_grades,
        "raw_grade_kernel_dimensions": tuple(
            raw_source_grades[grade] - raw_target_grades[grade]
            for grade in range(5)
        ),
        "multiplication_formula": (
            "(u*v) odot (x*y) maps to u*v*x*y; a symmetric Gram "
            "entry contributes once on the diagonal and twice off diagonal"
        ),
        "section_formula": (
            "iota(u*v*x*y)=((u*v)odot(x*y)+(u*x)odot(v*y)+"
            "(u*y)odot(v*x))/3"
        ),
        "section_is_GL211_equivariant_by_naturality_exact": True,
        "multiplication_after_section_is_identity_exact": all(representative_checks),
        "equality_and_grade_pattern_representative_count": len(representatives),
        "all_representative_identities_exact": all(representative_checks),
        "section_preserves_Phi_degree_exact": True,
        "invariant_restriction_surjective_exact": True,
        "invariant_surjectivity_argument": (
            "The displayed section is GL(W)-equivariant over Q, hence SU(4)-"
            "equivariant. It preserves Phi degree and mu o iota is the "
            "identity, so every invariant target sector has an invariant "
            "preimage over Q."
        ),
        "proof_grade": all(representative_checks),
    }


def _representation_census() -> dict[str, Any]:
    decompositions = exact_character_decompositions()
    blocks = _isotypic_blocks_cached()
    self_blocks = sum(row["self_conjugate"] for row in blocks)
    complex_blocks = len(blocks) - self_blocks
    represented_dimension = sum(row["represented_real_dimension"] for row in blocks)
    parameter_grades = schur_parameter_grade_counts()
    copy_grade_counts = (
        1,
        sum(decompositions["Phi210"].values()),
        sum(decompositions["Sym2_Phi210"].values()),
    )
    copy_count = sum(copy_grade_counts)
    frobenius_schur_types_exact = all(
        row["Frobenius_Schur_indicator"] == (1 if row["self_conjugate"] else 0)
        and row["Frobenius_Schur_type"]
        == ("real" if row["self_conjugate"] else "complex")
        and (
            not row["self_conjugate"]
            or row["young_diagram_box_count"] % 2 == 0
        )
        for row in blocks
    )
    rows = tuple(
        {
            "dynkin": highest,
            "multiplicity_Phi": decompositions["Phi210"].get(highest, 0),
            "multiplicity_Sym2Phi": decompositions["Sym2_Phi210"].get(highest, 0),
            "multiplicity_augmented": multiplicity,
            "complex_dimension": _weyl_dimension(highest),
        }
        for highest, multiplicity in sorted(
            decompositions["augmented_degree2"].items()
        )
    )
    all_character_dimensions_exact = all(
        sum(_gl4_irrep_character_cached(highest).values())
        == _weyl_dimension(highest)
        for highest in decompositions["augmented_degree2"]
    )
    return {
        "Phi210_weight_character_dimension": sum(_phi_weight_character_cached().values()),
        "Phi210_weight_count": len(_phi_weight_character_cached()),
        "Phi210_character_sha256": _character_sha256(_phi_weight_character_cached()),
        "Phi210_branching": decompositions["Phi210"],
        "Phi210_branching_expected_exact": decompositions["Phi210"] == EXPECTED_PHI_BRANCHING,
        "Sym2Phi_dimension": sum(_symmetric_power_characters_cached()[2].values()),
        "Sym2Phi_character_sha256": _character_sha256(
            _symmetric_power_characters_cached()[2]
        ),
        "augmented_homogeneous_dimension": sum(_augmented_character_cached().values()),
        "augmented_character_sha256": _character_sha256(_augmented_character_cached()),
        "complex_isotypic_type_count": len(
            decompositions["augmented_degree2"]
        ),
        "complex_irreducible_copy_grade_counts_t2_tPhi_Phi2": copy_grade_counts,
        "complex_irreducible_copy_count": copy_count,
        "complex_irrep_rows": rows,
        "expected_augmented_multiplicities_exact": (
            decompositions["augmented_degree2"]
            == EXPECTED_AUGMENTED_MULTIPLICITIES
        ),
        "all_Gelfand_Tsetlin_character_dimensions_match_Weyl_exact": (
            all_character_dimensions_exact
        ),
        "real_isotypic_block_count": len(blocks),
        "real_symmetric_block_count": self_blocks,
        "complex_Hermitian_block_count": complex_blocks,
        "Frobenius_Schur_classification_computed_exact": (
            frobenius_schur_types_exact
        ),
        "real_isotypic_blocks": blocks,
        "represented_real_dimension": represented_dimension,
        "Schur_real_parameter_grade_counts": parameter_grades,
        "Schur_real_parameter_count": sum(parameter_grades),
        "proof_grade": bool(
            decompositions["Phi210"] == EXPECTED_PHI_BRANCHING
            and decompositions["augmented_degree2"]
            == EXPECTED_AUGMENTED_MULTIPLICITIES
            and all_character_dimensions_exact
            and len(decompositions["augmented_degree2"])
            == EXPECTED_COMPLEX_ISOTYPIC_TYPE_COUNT
            and copy_grade_counts == EXPECTED_IRREDUCIBLE_COPY_GRADE_COUNTS
            and copy_count == EXPECTED_IRREDUCIBLE_COPY_COUNT
            and len(blocks) == 22
            and self_blocks == 9
            and complex_blocks == 13
            and frobenius_schur_types_exact
            and represented_dimension == HOMOGENEOUS_QUADRATIC_DIMENSION
            and parameter_grades == EXPECTED_DOMAIN_GRADE_COUNTS
            and sum(parameter_grades) == SCHUR_REAL_PARAMETER_COUNT
        ),
    }


def _target_census() -> dict[str, Any]:
    characters = _symmetric_power_characters_cached()
    dimensions = tuple(sum(character.values()) for character in characters)
    expected_dimensions = tuple(
        math.comb(PHI_DIMENSION + degree - 1, degree) for degree in range(5)
    )
    invariant_counts = target_invariant_grade_counts()
    return {
        "target_sector": "t^(4-k) Sym^k(Phi210), k=0,...,4",
        "symmetric_power_dimensions": dimensions,
        "expected_symmetric_power_dimensions": expected_dimensions,
        "symmetric_power_character_sha256": tuple(
            _character_sha256(character) for character in characters
        ),
        "Weyl_group_order": len(_weyl_rho_orbit_with_sign()),
        "trivial_multiplicity_extraction": (
            "sum_{w in W(A3)} sign(w) mult[rho-w(rho)]"
        ),
        "invariant_equation_grade_counts": invariant_counts,
        "invariant_equation_count": sum(invariant_counts),
        "proof_grade": bool(
            dimensions == expected_dimensions
            and invariant_counts == EXPECTED_TARGET_GRADE_COUNTS
            and sum(invariant_counts) == INVARIANT_QUARTIC_EQUATION_COUNT
        ),
    }


def _coefficient_map_census(
    representation: Mapping[str, Any],
    target: Mapping[str, Any],
    universal: Mapping[str, Any],
) -> dict[str, Any]:
    domain = tuple(representation["Schur_real_parameter_grade_counts"])
    rows = tuple(target["invariant_equation_grade_counts"])
    ranks = rows if universal.get("invariant_restriction_surjective_exact") else ()
    kernels = tuple(domain[index] - rows[index] for index in range(5))
    cubic_block_rows = tuple(
        {
            "representative_dynkin": block["representative_dynkin"],
            "real_block_kind": block["real_block_kind"],
            "tPhi_multiplicity": block["graded_multiplicities_t2_tPhi_Phi2"][1],
            "Phi2_multiplicity": block["graded_multiplicities_t2_tPhi_Phi2"][2],
            "real_cross_parameter_count": block[
                "cubic_tPhi_to_Phi2_cross_real_parameter_count"
            ],
        }
        for block in representation["real_isotypic_blocks"]
        if block["cubic_tPhi_to_Phi2_cross_real_parameter_count"]
    )
    return {
        "map": (
            "mu^SU4: Sym^2(Sym^2(R*t (+) Phi210))^SU4 -> "
            "Sym^4(R*t (+) Phi210)^SU4"
        ),
        "domain_real_parameter_grade_counts": domain,
        "target_invariant_row_grade_counts": rows,
        "abstract_grade_ranks_exact": ranks,
        "abstract_grade_kernel_dimensions_exact": kernels,
        "abstract_total_rank_exact": sum(ranks),
        "abstract_total_kernel_dimension_exact": sum(kernels),
        "cubic_cross_sector": {
            "source": "all t*Phi <-> Phi^2 isotypic cross subblocks",
            "nonzero_block_row_count": len(cubic_block_rows),
            "block_rows": cubic_block_rows,
            "real_Schur_variable_count": domain[3],
            "invariant_target_row_count": rows[3],
            "abstract_interface_RHS": "zero",
            "abstract_zero_RHS_row_count_reserved": rows[3],
            "abstract_zero_RHS_interface_contract_reserved": True,
            "zero_RHS_is_interface_contract_not_a_physical_vector_certificate": True,
            "physical_G3_gap_target_vector_constructed": False,
            "physical_G3_gap_cubic_zero_RHS_certified": False,
            "all_1414_cross_variables_present_in_census_exact": (
                sum(row["real_cross_parameter_count"] for row in cubic_block_rows)
                == EXPECTED_CUBIC_CROSS_PARAMETER_COUNT
            ),
            "all_478_cubic_target_rows_reserved_exact": (
                rows[3] == EXPECTED_CUBIC_ZERO_RHS_ROW_COUNT
            ),
        },
        "surjectivity_is_abstract_not_a_coordinate_matrix": True,
        "Schur_coordinate_matrix_shape_when_constructed": (
            INVARIANT_QUARTIC_EQUATION_COUNT,
            SCHUR_REAL_PARAMETER_COUNT,
        ),
        "Schur_coordinate_matrix_constructed": False,
        "missing_coordinate_data": (
            "35 exact isotypic carrier maps spanning all 824 irreducible copies "
            "of Sym^2(R*t (+) Phi210), plus ordered invariant cubic and quartic "
            "coordinates and the physical G3 gap target vector"
        ),
        "proof_grade": bool(
            domain == EXPECTED_DOMAIN_GRADE_COUNTS
            and rows == EXPECTED_TARGET_GRADE_COUNTS
            and ranks == EXPECTED_TARGET_GRADE_COUNTS
            and kernels == EXPECTED_KERNEL_GRADE_COUNTS
            and sum(domain) == SCHUR_REAL_PARAMETER_COUNT
            and sum(rows) == INVARIANT_QUARTIC_EQUATION_COUNT
            and sum(kernels)
            == SCHUR_REAL_PARAMETER_COUNT - INVARIANT_QUARTIC_EQUATION_COUNT
            and sum(row["real_cross_parameter_count"] for row in cubic_block_rows)
            == EXPECTED_CUBIC_CROSS_PARAMETER_COUNT
            and rows[3] == EXPECTED_CUBIC_ZERO_RHS_ROW_COUNT
        ),
    }


def _provenance_certificate(
    *,
    aligned_source_sha256: str,
    aligned_report: Mapping[str, Any],
    alignment_certificate: Mapping[str, Any],
    quadratic_source_sha256: str,
    quadratic_report: Mapping[str, Any],
    quadratic_basis_matrices: Sequence[sparse.spmatrix],
) -> dict[str, Any]:
    aligned_report_hash = _canonical_json_sha256(aligned_report)
    alignment_hash = _canonical_json_sha256(alignment_certificate)
    quadratic_report_hash = _canonical_json_sha256(quadratic_report)
    quadratic_basis_hash = _sparse_sequence_sha256(quadratic_basis_matrices)
    aligned_scope = aligned_report.get("scope", {})
    quadratic_scope = quadratic_report.get("scope", {})
    exact = bool(
        Path(aligned.__file__).name == EXPECTED_ALIGNED_MODULE
        and Path(quadratics.__file__).name == EXPECTED_QUADRATIC_MODULE
        and aligned_source_sha256 == EXPECTED_ALIGNED_SOURCE_SHA256
        and quadratic_source_sha256 == EXPECTED_QUADRATIC_SOURCE_SHA256
        and aligned_report_hash == EXPECTED_ALIGNED_REPORT_SHA256
        and alignment_hash == EXPECTED_ALIGNMENT_CERTIFICATE_SHA256
        and quadratic_report_hash == EXPECTED_QUADRATIC_REPORT_SHA256
        and aligned_report.get("status") == EXPECTED_ALIGNED_STATUS
        and aligned_report.get("overall_state") == EXPECTED_ALIGNED_OVERALL_STATE
        and aligned_report.get("model_contract_id") == MODEL_CONTRACT_ID
        and aligned_report.get("n_failed") == 0
        and aligned_scope.get("aligned_complexified_Phi210_carriers_constructed")
        is True
        and aligned_scope.get("physical_real_structure_and_Gaussian_embeddings_constructed")
        is True
        and alignment_certificate.get("proof_grade") is True
        and alignment_certificate.get("carrier_count") == 25
        and alignment_certificate.get("concatenated_aligned_basis_shape")
        == (PHI_DIMENSION, PHI_DIMENSION)
        and quadratic_report.get("status") == EXPECTED_QUADRATIC_STATUS
        and quadratic_report.get("overall_state")
        == EXPECTED_QUADRATIC_OVERALL_STATE
        and quadratic_report.get("model_contract_id") == MODEL_CONTRACT_ID
        and quadratic_report.get("n_failed") == 0
        and quadratic_scope.get("SU4_invariant_quadratic_form_basis_complete")
        is True
        and quadratic_scope.get("SU4_invariant_quadratic_form_dimension_45_exact")
        is True
        and len(quadratic_basis_matrices) == 45
        and all(matrix.shape == (PHI_DIMENSION, PHI_DIMENSION) for matrix in quadratic_basis_matrices)
        and all(np.issubdtype(matrix.dtype, np.integer) for matrix in quadratic_basis_matrices)
        and quadratic_basis_hash == EXPECTED_QUADRATIC_BASIS_SHA256
        and quadratic_report.get("quadratic_basis", {}).get("basis_sha256")
        == EXPECTED_QUADRATIC_BASIS_SHA256
    )
    return {
        "model_contract_id": MODEL_CONTRACT_ID,
        "aligned_module": EXPECTED_ALIGNED_MODULE,
        "aligned_source_sha256": aligned_source_sha256,
        "expected_aligned_source_sha256": EXPECTED_ALIGNED_SOURCE_SHA256,
        "aligned_report_sha256": aligned_report_hash,
        "expected_aligned_report_sha256": EXPECTED_ALIGNED_REPORT_SHA256,
        "alignment_certificate_sha256": alignment_hash,
        "expected_alignment_certificate_sha256": EXPECTED_ALIGNMENT_CERTIFICATE_SHA256,
        "quadratic_module": EXPECTED_QUADRATIC_MODULE,
        "quadratic_source_sha256": quadratic_source_sha256,
        "expected_quadratic_source_sha256": EXPECTED_QUADRATIC_SOURCE_SHA256,
        "quadratic_report_sha256": quadratic_report_hash,
        "expected_quadratic_report_sha256": EXPECTED_QUADRATIC_REPORT_SHA256,
        "quadratic_basis_sha256": quadratic_basis_hash,
        "expected_quadratic_basis_sha256": EXPECTED_QUADRATIC_BASIS_SHA256,
        "quadratic_basis_matrix_count": len(quadratic_basis_matrices),
        "all_required_frozen_API_provenance_exact": exact,
        "proof_grade": exact,
    }


def _build_report_from_evidence(
    *,
    provenance: Mapping[str, Any],
    representation: Mapping[str, Any],
    target: Mapping[str, Any],
    universal: Mapping[str, Any],
    coefficient_map: Mapping[str, Any],
) -> dict[str, Any]:
    canonical_representation = _representation_census()
    canonical_target = _target_census()
    canonical_universal = _universal_map_certificate()
    canonical_coefficient_map = _coefficient_map_census(
        canonical_representation, canonical_target, canonical_universal
    )
    cubic = coefficient_map.get("cubic_cross_sector", {})
    checks = {
        "frozen_aligned_carrier_and_quadratic_basis_APIs_exact": bool(
            provenance.get("proof_grade")
            and provenance.get("all_required_frozen_API_provenance_exact")
            and provenance.get("model_contract_id") == MODEL_CONTRACT_ID
            and provenance.get("aligned_module") == EXPECTED_ALIGNED_MODULE
            and provenance.get("aligned_source_sha256")
            == EXPECTED_ALIGNED_SOURCE_SHA256
            and provenance.get("aligned_report_sha256")
            == EXPECTED_ALIGNED_REPORT_SHA256
            and provenance.get("alignment_certificate_sha256")
            == EXPECTED_ALIGNMENT_CERTIFICATE_SHA256
            and provenance.get("quadratic_module") == EXPECTED_QUADRATIC_MODULE
            and provenance.get("quadratic_source_sha256")
            == EXPECTED_QUADRATIC_SOURCE_SHA256
            and provenance.get("quadratic_report_sha256")
            == EXPECTED_QUADRATIC_REPORT_SHA256
            and provenance.get("quadratic_basis_sha256")
            == EXPECTED_QUADRATIC_BASIS_SHA256
            and provenance.get("quadratic_basis_matrix_count") == 45
        ),
        "live_Phi210_character_and_exact_branching_certified": bool(
            representation.get("proof_grade")
            and _canonical_json_sha256(representation)
            == _canonical_json_sha256(canonical_representation)
            and representation.get("Phi210_weight_character_dimension")
            == PHI_DIMENSION
            and representation.get("Phi210_branching_expected_exact") is True
        ),
        "augmented_dimension_35_isotypic_types_and_824_copies_exact": bool(
            representation.get("augmented_homogeneous_dimension")
            == HOMOGENEOUS_QUADRATIC_DIMENSION
            and representation.get("complex_isotypic_type_count")
            == EXPECTED_COMPLEX_ISOTYPIC_TYPE_COUNT
            and tuple(
                representation.get(
                    "complex_irreducible_copy_grade_counts_t2_tPhi_Phi2", ()
                )
            )
            == EXPECTED_IRREDUCIBLE_COPY_GRADE_COUNTS
            and representation.get("complex_irreducible_copy_count")
            == EXPECTED_IRREDUCIBLE_COPY_COUNT
            and representation.get("expected_augmented_multiplicities_exact")
            is True
        ),
        "nine_real_and_thirteen_complex_isotypic_blocks_exact": bool(
            representation.get("real_isotypic_block_count") == 22
            and representation.get("real_symmetric_block_count") == 9
            and representation.get("complex_Hermitian_block_count") == 13
            and representation.get("represented_real_dimension")
            == HOMOGENEOUS_QUADRATIC_DIMENSION
        ),
        "real_symmetric_and_complex_Hermitian_conventions_complete": bool(
            len(representation.get("real_isotypic_blocks", ())) == 22
            and all(
                block.get("real_block_kind")
                in {"real_symmetric", "complex_Hermitian"}
                and block.get("real_Schur_parameter_count")
                == sum(block.get("real_parameter_grade_counts", ()))
                for block in representation.get("real_isotypic_blocks", ())
            )
        ),
        "Frobenius_Schur_indicators_computed_and_real_types_exact": bool(
            representation.get("Frobenius_Schur_classification_computed_exact")
            is True
            and all(
                block.get("Frobenius_Schur_indicator")
                == (1 if block.get("self_conjugate") else 0)
                and block.get("Frobenius_Schur_type")
                == ("real" if block.get("self_conjugate") else "complex")
                and (
                    not block.get("self_conjugate")
                    or block.get("young_diagram_box_count", 1) % 2 == 0
                )
                for block in representation.get("real_isotypic_blocks", ())
            )
        ),
        "Schur_parameter_19594_grade_census_exact": bool(
            tuple(representation.get("Schur_real_parameter_grade_counts", ()))
            == EXPECTED_DOMAIN_GRADE_COUNTS
            and representation.get("Schur_real_parameter_count")
            == SCHUR_REAL_PARAMETER_COUNT
        ),
        "invariant_target_6585_grade_census_exact": bool(
            target.get("proof_grade")
            and _canonical_json_sha256(target)
            == _canonical_json_sha256(canonical_target)
            and tuple(target.get("invariant_equation_grade_counts", ()))
            == EXPECTED_TARGET_GRADE_COUNTS
            and target.get("invariant_equation_count")
            == INVARIANT_QUARTIC_EQUATION_COUNT
        ),
        "universal_GL211_equivariant_section_exact": bool(
            universal.get("proof_grade")
            and _canonical_json_sha256(universal)
            == _canonical_json_sha256(canonical_universal)
            and universal.get("section_is_GL211_equivariant_by_naturality_exact")
            is True
            and universal.get("multiplication_after_section_is_identity_exact")
            is True
            and universal.get("invariant_restriction_surjective_exact") is True
        ),
        "abstract_invariant_map_ranks_and_kernels_exact": bool(
            coefficient_map.get("proof_grade")
            and _canonical_json_sha256(coefficient_map)
            == _canonical_json_sha256(canonical_coefficient_map)
            and tuple(coefficient_map.get("abstract_grade_ranks_exact", ()))
            == EXPECTED_TARGET_GRADE_COUNTS
            and tuple(
                coefficient_map.get("abstract_grade_kernel_dimensions_exact", ())
            )
            == EXPECTED_KERNEL_GRADE_COUNTS
        ),
        "cubic_abstract_zero_interface_reserved_without_physical_claim": bool(
            cubic.get("real_Schur_variable_count")
            == EXPECTED_CUBIC_CROSS_PARAMETER_COUNT
            and cubic.get("invariant_target_row_count")
            == EXPECTED_CUBIC_ZERO_RHS_ROW_COUNT
            and cubic.get("abstract_interface_RHS") == "zero"
            and cubic.get("abstract_zero_RHS_row_count_reserved")
            == EXPECTED_CUBIC_ZERO_RHS_ROW_COUNT
            and cubic.get("abstract_zero_RHS_interface_contract_reserved") is True
            and cubic.get(
                "zero_RHS_is_interface_contract_not_a_physical_vector_certificate"
            )
            is True
            and cubic.get("physical_G3_gap_target_vector_constructed") is False
            and cubic.get("physical_G3_gap_cubic_zero_RHS_certified") is False
            and cubic.get("all_1414_cross_variables_present_in_census_exact")
            is True
            and cubic.get("all_478_cubic_target_rows_reserved_exact") is True
        ),
        "coordinate_map_absence_declared_fail_closed": bool(
            coefficient_map.get("surjectivity_is_abstract_not_a_coordinate_matrix")
            is True
            and coefficient_map.get("Schur_coordinate_matrix_constructed")
            is False
            and tuple(
                coefficient_map.get("Schur_coordinate_matrix_shape_when_constructed", ())
            )
            == (INVARIANT_QUARTIC_EQUATION_COUNT, SCHUR_REAL_PARAMETER_COUNT)
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    ready = not failures
    return {
        "status": STATUS if ready else "RANK1_SU4_AUGMENTED_SOS_CENSUS_EXECUTION_FAILED",
        "overall_state": OVERALL_STATE if ready else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "source_provenance": copy.deepcopy(provenance),
        "augmented_representation": copy.deepcopy(representation),
        "invariant_quartic_target": copy.deepcopy(target),
        "universal_multiplication_and_section": copy.deepcopy(universal),
        "abstract_coefficient_map_census": copy.deepcopy(coefficient_map),
        "public_exact_APIs": {
            "Phi_character": "phi_weight_character()",
            "symmetric_power_character": "symmetric_power_character(k), 0<=k<=4",
            "augmented_character": "augmented_homogeneous_character()",
            "character_decompositions": "exact_character_decompositions()",
            "Frobenius_Schur_indicator": "frobenius_schur_indicator(highest_weight)",
            "real_isotypic_blocks": "exact_augmented_isotypic_blocks()",
            "Schur_grade_counts": "schur_parameter_grade_counts()",
            "target_grade_counts": "target_invariant_grade_counts()",
            "raw_Gram_entry_map": "raw_gram_entry_image(left_pair,right_pair)",
            "polarized_tensor_section": "polarized_section_tensor_terms(quartic)",
            "polarized_Gram_section": "polarized_section_gram_entries(quartic)",
        },
        "scope": {
            "H_fixed_to_h_minus": ready,
            "Sigma_fixed_to_q_over_4": ready,
            "rank1_endpoint_SU4_stabilizer_used": ready,
            "augmented_homogeneous_representation_census_constructed": ready,
            "all_22_real_Hermitian_Schur_block_sizes_certified": ready,
            "universal_GL211_multiplication_and_rational_section_constructed": ready,
            "abstract_invariant_grade_ranks_certified": ready,
            "quadratic_target_invariant_basis_dimension_45_bound_live": ready,
            "all_35_isotypic_type_maps_spanning_824_irreducible_copies_constructed": False,
            "ordered_invariant_cubic_basis_constructed": False,
            "ordered_invariant_quartic_basis_constructed": False,
            "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed": False,
            "physical_G3_gap_target_vector_constructed": False,
            "physical_G3_gap_cubic_zero_RHS_certified": False,
            "augmented_Schur_SOS_SDP_constructed": False,
            "augmented_Schur_SOS_SDP_feasibility_certified": False,
            "augmented_Schur_SOS_SDP_infeasibility_certified": False,
            "arbitrary_real_Phi_lower_bound_proved": False,
            "arbitrary_rank1_Phi_proved": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "blocking_gap": (
            "Construct all 35 exact aligned isotypic carrier maps spanning the "
            "824 irreducible copies of Sym^2(R*t (+) Phi210), together with "
            "ordered 478-dimensional cubic and 6057-dimensional quartic "
            "invariant target coordinates and the physical G3 gap target vector. "
            "Only then can the 6585 by 19594 Schur coefficient matrix and PSD "
            "feasibility problem be assembled."
        ),
        "next_exact_target": (
            "Build the 35 graded isotypic carrier maps, spanning all 824 copies, "
            "and their real/complex multiplicity-coordinate maps, beginning with "
            "the complete 1414-"
            "variable t*Phi-to-Phi^2 cubic cross sector and its 478 exact zero-"
            "RHS interface rows; construction of the physical target remains a "
            "separate required certificate."
        ),
        "verdict": (
            "The full augmented SU(4) representation, real/Hermitian Schur-cone "
            "sizes, invariant target dimensions, and abstract grade-resolved "
            "multiplication ranks are exact. The universal rational polarization "
            "section includes every homogenizing grade. This is census/map "
            "infrastructure only: no Schur-coordinate matrix, physical G3 gap "
            "target vector, or PSD feasibility certificate exists yet, so no "
            "arbitrary-Phi bound or G3 conclusion is claimed."
            if ready
            else "The augmented SU(4) census/map audit failed closed; no SOS or G3 conclusion is certified."
        ),
    }


@lru_cache(maxsize=1)
def _build_report_cached() -> dict[str, Any]:
    aligned_path = Path(aligned.__file__).resolve()
    quadratic_path = Path(quadratics.__file__).resolve()
    aligned_report = aligned.build_report()
    alignment_certificate = aligned.exact_aligned_carrier_certificate()
    quadratic_report = quadratics.build_report()
    quadratic_matrices = quadratics.exact_invariant_quadratic_basis()
    provenance = _provenance_certificate(
        aligned_source_sha256=_file_sha256(aligned_path),
        aligned_report=aligned_report,
        alignment_certificate=alignment_certificate,
        quadratic_source_sha256=_file_sha256(quadratic_path),
        quadratic_report=quadratic_report,
        quadratic_basis_matrices=quadratic_matrices,
    )
    representation = _representation_census()
    target = _target_census()
    universal = _universal_map_certificate()
    coefficient_map = _coefficient_map_census(representation, target, universal)
    return _build_report_from_evidence(
        provenance=provenance,
        representation=representation,
        target=target,
        universal=universal,
        coefficient_map=coefficient_map,
    )


def build_report() -> dict[str, Any]:
    return copy.deepcopy(_build_report_cached())


def render_markdown(report: Mapping[str, Any]) -> str:
    representation = report["augmented_representation"]
    target = report["invariant_quartic_target"]
    coefficient_map = report["abstract_coefficient_map_census"]
    cubic = coefficient_map["cubic_cross_sector"]
    block_lines = [
        "| Dynkin representative | FS indicator | Kind | order | grades `(t2,tPhi,Phi2)` | real vars | cubic cross |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for block in representation["real_isotypic_blocks"]:
        block_lines.append(
            "| `{}` | {} | {} | {} | `{}` | {} | {} |".format(
                tuple(block["representative_dynkin"]),
                block["Frobenius_Schur_indicator"],
                block["real_block_kind"],
                block["multiplicity_matrix_order"],
                tuple(block["graded_multiplicities_t2_tPhi_Phi2"]),
                block["real_Schur_parameter_count"],
                block["cubic_tPhi_to_Phi2_cross_real_parameter_count"],
            )
        )
    return "\n".join(
        [
            "# Exact rank-one SU(4) augmented SOS census and universal map -- v20",
            "",
            f"**Status:** `{report['status']}`",
            "",
            report["verdict"],
            "",
            "## Exact dimensions",
            "",
            f"- `dim Sym^2(R*t (+) Phi210) = {representation['augmented_homogeneous_dimension']}`;",
            f"- complex isotypic types: `{representation['complex_isotypic_type_count']}`;",
            f"- irreducible copies by `(t2,tPhi,Phi2)`: "
            f"`{tuple(representation['complex_irreducible_copy_grade_counts_t2_tPhi_Phi2'])}` "
            f"(total `{representation['complex_irreducible_copy_count']}`);",
            f"- real isotypic blocks: `{representation['real_isotypic_block_count']}` = "
            f"`{representation['real_symmetric_block_count']}` real-symmetric + "
            f"`{representation['complex_Hermitian_block_count']}` complex-Hermitian;",
            f"- Schur real parameters by Phi degree: `{tuple(representation['Schur_real_parameter_grade_counts'])}` "
            f"(total `{representation['Schur_real_parameter_count']}`);",
            f"- invariant target rows by Phi degree: `{tuple(target['invariant_equation_grade_counts'])}` "
            f"(total `{target['invariant_equation_count']}`);",
            f"- exact abstract map kernel by Phi degree: `{tuple(coefficient_map['abstract_grade_kernel_dimensions_exact'])}`.",
            "",
            "## Cubic homogenizing cross sector",
            "",
            f"All `{cubic['real_Schur_variable_count']:,}` real variables in the "
            "`t*Phi <-> Phi^2` cross subblocks are included.  The invariant cubic "
            f"target has `{cubic['invariant_target_row_count']:,}` rows; an abstract "
            "interface reserves all of them with exact zero right-hand side. This "
            "is not a physical-vector certificate: the physical G3 gap target "
            "vector has not been constructed and its cubic zero RHS has not been "
            "certified.",
            "",
            "## Real/Hermitian Schur blocks",
            "",
            *block_lines,
            "",
            "## Exact universal map",
            "",
            report["universal_multiplication_and_section"]["section_formula"],
            "",
            report["universal_multiplication_and_section"]["invariant_surjectivity_argument"],
            "",
            "## Deliberate open scope",
            "",
            report["blocking_gap"],
            "",
            "Consequently the 6,585 by 19,594 Schur-coordinate matrix, PSD "
            "feasibility, arbitrary-Phi bound, and G3 remain open.",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=OUT_JSON)
    parser.add_argument("--markdown", type=Path, default=OUT_MD)
    arguments = parser.parse_args(argv)
    report = build_report()
    arguments.json.write_text(
        json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    arguments.markdown.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps({
        "status": report["status"],
        "n_checks": report["n_checks"],
        "n_failed": report["n_failed"],
        "Schur_real_parameter_count": report["augmented_representation"]["Schur_real_parameter_count"],
        "invariant_equation_count": report["invariant_quartic_target"]["invariant_equation_count"],
        "G3_closed": report["scope"]["G3_closed"],
    }, sort_keys=True))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
