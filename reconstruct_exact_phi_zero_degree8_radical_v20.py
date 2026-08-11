#!/usr/bin/env python3
"""Finite-field scout for D^2 in the degree-eight Phi projector ideal."""
from __future__ import annotations

import importlib.util
import itertools
import sys
import time
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE
sys.path.insert(0, str(REPO))

import exact_210_self_invariant_basis_v20 as invariants
import exact_gauged_u1x_g3_su5_phi_su3_slice_v20 as covariants
import exact_phisigma_casimir_projectors_v20 as projectors


P = int(sys.argv[1]) if len(sys.argv) > 1 else 10_007
N_SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 50
MODE = sys.argv[3] if len(sys.argv) > 3 else ""
SOLVE = MODE in {"solve", "reconstruct"}
CHANNELS = tuple(projectors.SPECTRAL_EIGENVALUES)
TRIPLES = (
    tuple(itertools.combinations_with_replacement(range(8), 3))
    if MODE == "reconstruct"
    else tuple(itertools.product(range(8), repeat=3))
)
PAIRS = tuple(itertools.combinations_with_replacement(range(8), 2))
ORDERED_PAIRS = PAIRS if MODE == "reconstruct" else tuple(itertools.product(range(8), repeat=2))
WORD_COUNT = 2 * len(TRIPLES)
TWO_INDICES = tuple(itertools.combinations(range(10), 2))
TRACE_AG_WORDS = ("AAAAAAAA", "AAAAAAG", "AAAAGG", "AAAGAG", "AAGAAG", "AAGGG", "AGAGG", "GGGG")
BILINEAR_AG_WORDS = ("AAAA", "AAG", "AGA", "GG")
DEG6_LABELS = tuple(
    (residual, left, right)
    for residual in (2, 5)
    for left in range(8)
    for right in range(left, 8)
)
DEG6_PIVOTS = (2, 8, 15, 17, 21, 22, 41, 49, 57, 58, 59, 60, 62, 63, 64)


def fmod(value):
    return value.numerator % P * pow(value.denominator % P, -1, P) % P


COEFFICIENTS = {
    name: tuple(fmod(x) for x in projectors.projector_polynomial(eigenvalue))
    for name, eigenvalue in projectors.SPECTRAL_EIGENVALUES.items()
}


def rank_mod(matrix: np.ndarray) -> int:
    work = np.asarray(matrix, dtype=np.int64).copy() % P
    row = 0
    for column in range(work.shape[1]):
        nz = np.flatnonzero(work[row:, column])
        if not nz.size:
            continue
        pivot = row + int(nz[0])
        work[[row, pivot]] = work[[pivot, row]]
        work[row] = work[row] * pow(int(work[row, column]), -1, P) % P
        for target in range(work.shape[0]):
            if target != row and work[target, column]:
                work[target] = (
                    work[target] - work[target, column] * work[row]
                ) % P
        row += 1
        if row == work.shape[0]:
            break
    return row


def solve_mod(matrix: np.ndarray, rhs: np.ndarray) -> tuple[np.ndarray, list[int]]:
    work = np.column_stack([matrix, rhs]).astype(np.int64) % P
    row = 0
    pivots: list[int] = []
    for column in range(matrix.shape[1]):
        nz = np.flatnonzero(work[row:, column])
        if not nz.size:
            continue
        pivot = row + int(nz[0])
        work[[row, pivot]] = work[[pivot, row]]
        work[row] = work[row] * pow(int(work[row, column]), -1, P) % P
        for target in range(work.shape[0]):
            if target != row and work[target, column]:
                work[target] = (
                    work[target] - work[target, column] * work[row]
                ) % P
        pivots.append(column)
        row += 1
        if row == work.shape[0]:
            break
    if np.any(work[row:, -1]):
        raise ArithmeticError("inconsistent system")
    solution = np.zeros(matrix.shape[1], dtype=np.int64)
    for pivot_row, column in enumerate(pivots):
        solution[column] = work[pivot_row, -1]
    return solution, pivots


def hodge_square(vector: np.ndarray) -> np.ndarray:
    output = np.zeros(45, dtype=np.int64)
    for left, right, target, coefficient in covariants._disjoint_four_form_pairs():
        output[target] = (
            output[target] + coefficient * vector[left] * vector[right]
        ) % P
    return output


def four_form_operator(vector: np.ndarray) -> np.ndarray:
    matrix = np.zeros((45, 45), dtype=np.int64)
    for row, left in enumerate(TWO_INDICES):
        for column, right in enumerate(TWO_INDICES):
            if set(left).intersection(right):
                continue
            sequence = left + right
            indices = tuple(sorted(sequence))
            inversions = sum(
                sequence[i] > sequence[j]
                for i in range(4)
                for j in range(i + 1, 4)
            )
            matrix[row, column] = (
                (-1 if inversions & 1 else 1)
                * vector[projectors.FOUR_INDEX[indices]]
            ) % P
    return matrix


def matrix_word(word: str, matrices: dict[str, np.ndarray]) -> np.ndarray:
    output = np.eye(45, dtype=np.int64)
    for letter in word:
        output = output @ matrices[letter] % P
    return output


def channels(vector: np.ndarray) -> list[np.ndarray]:
    pair = np.outer(vector, vector) % P
    powers = [pair]
    for _ in range(7):
        powers.append(invariants.integer_pair_casimir(powers[-1]) % P)
    output = []
    for name in CHANNELS:
        q = np.zeros_like(pair)
        for coefficient, power in zip(COEFFICIENTS[name], powers, strict=True):
            q = (q + coefficient * power) % P
        output.append(q)
    return output


def evaluate(vector: np.ndarray) -> tuple[list[int], int]:
    qs = channels(vector)
    pair_products = {
        (left, right): qs[left] @ qs[right] % P for left, right in ORDERED_PAIRS
    }
    features: list[int] = []
    for residual_index in (2, 5):  # 54 and 4125
        left_products = [qs[residual_index] @ q % P for q in qs]
        for left, middle, right in TRIPLES:
            product = pair_products[(middle, right)]
            features.append(
                int(np.sum(left_products[left] * product.T, dtype=np.int64) % P)
            )

    # Products of the residual channel norm with every spectral channel norm.
    norms = [int(np.sum(q * q, dtype=np.int64) % P) for q in qs]
    for residual_index in (2, 5):
        features.extend(norms[residual_index] * value % P for value in norms)

    norm = int(vector @ vector % P)
    wedge = hodge_square(vector)
    defect = (9 * pow(5, -1, P) * norm**2 - int(wedge @ wedge % P)) % P
    if MODE == "reconstruct":
        return features, defect**2 % P

    # N times the frozen 18-element sextic basis.
    sextic_values: list[int] = []
    for feature_index in DEG6_PIVOTS:
        residual, left, right = DEG6_LABELS[feature_index]
        product = qs[residual] @ qs[left] % P
        sextic_values.append(
            int(np.sum(product * qs[right].T, dtype=np.int64) % P)
        )
    features.extend(norm * value % P for value in sextic_values)
    features.append(norm**2 * defect % P)

    orbit = np.column_stack(
        [generator @ vector for generator in invariants.integer_generators()]
    ) % P
    gram = orbit.T @ orbit % P
    shifted = (5 * gram - 6 * norm * np.eye(45, dtype=np.int64)) % P
    scalar = (
        int(np.trace((gram @ shifted % P) @ shifted % P))
        * pow(25, -1, P)
        % P
    )
    features.extend((norm * scalar % P, norm**4 % P))

    # All products of spectral quartic norms (a spanning Sym^2 of the
    # four-dimensional quartic invariant space).
    features.extend(norms[left] * norms[right] % P for left, right in PAIRS)

    # Further exact SO(10) contractions not generated by pair-channel trace
    # partitions: words in A_Phi (degree one), G (degree two), and B (degree
    # two).  These scout the missing primitive degree-eight directions.
    four_operator = four_form_operator(vector)
    matrices = {"A": four_operator, "G": gram}
    features.extend(
        int(np.trace(matrix_word(word, matrices)) % P) for word in TRACE_AG_WORDS
    )
    features.extend(
        int(wedge @ matrix_word(word, matrices) @ wedge % P)
        for word in BILINEAR_AG_WORDS
    )
    cubic = int(np.trace(four_operator @ four_operator % P @ four_operator) % P)
    degree_five = (
        int(np.trace(matrix_word("AAAAA", matrices)) % P),
        int(np.trace(matrix_word("AAAG", matrices)) % P),
        int(np.trace(matrix_word("AGG", matrices)) % P),
        int(wedge @ four_operator @ wedge % P),
    )
    features.extend(cubic * value % P for value in degree_five)
    return features, defect**2 % P


def main() -> None:
    rng = np.random.default_rng(20_260_810)
    rows = []
    targets = []
    start = time.time()
    for sample in range(N_SAMPLES):
        vector = rng.integers(-3, 4, size=210, dtype=np.int64) % P
        features, target = evaluate(vector)
        rows.append(features)
        targets.append(target)
        if (sample + 1) % 5 == 0:
            matrix = np.asarray(rows, dtype=np.int64)
            rank = rank_mod(matrix)
            target_rank = rank_mod(np.column_stack([matrix, targets]))
            print(
                sample + 1,
                len(features),
                rank,
                target_rank,
                f"{time.time()-start:.1f}s",
                flush=True,
            )
    matrix = np.asarray(rows, dtype=np.int64)
    print(
        "trace_only",
        rank_mod(matrix[:, :WORD_COUNT]),
        rank_mod(np.column_stack([matrix[:, :WORD_COUNT], targets])),
    )
    if MODE == "reconstruct":
        solution, pivots = solve_mod(matrix[:, :WORD_COUNT], np.asarray(targets))
        print("pivots", pivots)
        print(
            "solution",
            [(index, int(solution[index])) for index in pivots],
        )
        return
    print(
        "product_only",
        rank_mod(matrix[:, WORD_COUNT:]),
        rank_mod(np.column_stack([matrix[:, WORD_COUNT:], targets])),
    )
    print(
        "ideal_plus_Nsextic_quartic_products",
        rank_mod(matrix),
        rank_mod(np.column_stack([matrix, targets])),
    )
    prefix = WORD_COUNT
    for label, width in (
        ("residual_norm_products", 16),
        ("N_times_sextic", 15),
        ("N2D", 1),
        ("NS_N4", 2),
        ("quartic_products", len(PAIRS)),
        ("trace_AG", len(TRACE_AG_WORDS)),
        ("B_AG_B", len(BILINEAR_AG_WORDS)),
        ("I3_degree5", 4),
    ):
        prefix += width
        print("prefix", label, prefix, rank_mod(matrix[:, :prefix]))
    trace = matrix[:, :WORD_COUNT]
    n2d_column = matrix[:, WORD_COUNT + 16 + 15]
    ns_column = matrix[:, WORD_COUNT + 16 + 15 + 1]
    n4_column = matrix[:, WORD_COUNT + 16 + 15 + 2]
    for label, columns in (
        ("trace_N2D", [n2d_column]),
        ("trace_NS", [ns_column]),
        ("trace_N4", [n4_column]),
        ("trace_N2D_NS", [n2d_column, ns_column]),
        ("trace_N2D_N4", [n2d_column, n4_column]),
        ("trace_NS_N4", [ns_column, n4_column]),
    ):
        print(label, rank_mod(np.column_stack([trace, *columns])))
    eigenvalues = np.asarray(
        [int(value) % P for value in projectors.SPECTRAL_EIGENVALUES.values()],
        dtype=np.int64,
    )
    for maximum_power in range(1, 6):
        powers = np.asarray(
            [pow(int(value), degree, P) for degree in range(maximum_power + 1) for value in eigenvalues],
            dtype=np.int64,
        ).reshape(maximum_power + 1, 8)
        aggregated_columns = []
        for residual_block in range(2):
            block = matrix[:, residual_block * 512 : (residual_block + 1) * 512]
            block = block.reshape(len(matrix), 8, 8, 8)
            for first in range(maximum_power + 1):
                for second in range(maximum_power + 1):
                    for third in range(maximum_power + 1):
                        weights = np.einsum(
                            "a,b,c->abc",
                            powers[first],
                            powers[second],
                            powers[third],
                        ) % P
                        aggregated_columns.append(
                            np.sum(block * weights[None, :, :, :], axis=(1, 2, 3), dtype=np.int64) % P
                        )
        aggregated = np.column_stack(aggregated_columns)
        print(
            "power_words",
            maximum_power,
            aggregated.shape[1],
            rank_mod(aggregated),
            rank_mod(np.column_stack([aggregated, targets])),
        )
    if SOLVE:
        solution, pivots = solve_mod(matrix[:, :WORD_COUNT], np.asarray(targets))
        print("pivots", pivots)
        print(
            "solution",
            [(index, int(solution[index])) for index in pivots],
        )


if __name__ == "__main__":
    main()
