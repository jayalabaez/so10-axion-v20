#!/usr/bin/env python3
"""Exact normalized SO(10) Yukawa Clebsch tensors for the v20 model.

The construction is entirely representation theoretic.  It uses the explicit
ten-dimensional Euclidean Clifford algebra already audited in
``spin10_referee_audit.py`` and the canonical kinetic-orthonormal ``-i`` Hodge
basis of the physical ``Delta126bar`` five-form used by the scalar backend.

Conventions
-----------
The signed model representation ``16`` is assigned to Clifford chirality -1
and ``16bar`` to chirality +1.  This is not an arbitrary relabeling: with this
choice, and only this choice, ``C Gamma_[5]`` contracts nontrivially and
covariantly with the source-bound ``-i``-Hodge ``Delta126bar`` basis.

The representation Clebsches are normalized in the ordered-pair
Hilbert--Schmidt metric,

    Tr(C_A^dagger C_B) = delta_AB.

Thus ``16 x 16 x 10`` is ``(C Gamma_a)|_- / 4``.  For a canonical physical
five-form state ``E_r``, ``16 x 16 x 126bar`` is

    sum_I (E_r)_I (C Gamma_I)|_- / 8.

The numerator has sixteen entries of magnitude two and Gram matrix ``64 I``.
The factor eight therefore includes the canonical ``1/(2 5!)`` scalar kinetic
normalization; it must not be replaced by the factor four appropriate to one
unpaired five-index component.  In the C-dual basis for a ``16bar``, the
singlet tensor is exactly ``I_16 / 4``.

This closes normalized SO(10) *representation* CGCs for every Yukawa symbol in
``models/SO10Z17AxionV20.m`` and supplies sparse embeddings into its canonical
304-Weyl inventory.  Flavor tensors remain symbolic.  The mapping between
these normalized tensors and SARAH's implicit ``Dot``/identical-field
normalization, numerical Yukawa boundary data, beta functions and thresholds
remain open.  Consequently neither the full Yukawa sector nor G7 is closed.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import direct_phi_h_sigmabar_tensor_v20 as five_forms
import spin10_referee_audit as clifford


HERE = Path(__file__).resolve().parent
MODEL = HERE / "models" / "SO10Z17AxionV20.m"
CLIFFORD_SOURCE = HERE / "spin10_referee_audit.py"
FIVE_FORM_SOURCE = HERE / "direct_phi_h_sigmabar_tensor_v20.py"
BRANCHING_SOURCE = HERE / "exact_126bar_triplet_clebsch_v20.py"
OUT_JSON = HERE / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.json"
OUT_MD = HERE / "EXACT_NORMALIZED_SO10_YUKAWA_CGCS_V20.md"

STATUS = (
    "EXACT_NORMALIZED_SO10_REPRESENTATION_YUKAWA_CGCS_CLOSED__"
    "FLAVOR_RGE_AND_FULL_G7_OPEN"
)
CONTRACT_ID = "exact_normalized_so10_yukawa_cgcs_v20"

DEPENDENCIES: dict[str, tuple[Path, str, str]] = {
    "authoritative_model": (
        MODEL,
        "66a2ce2c3491d0b3079ec93a16ab79d3e8a7e4e35cb54aadf21100b9fdd90cc1",
        "raw",
    ),
    "audited_clifford_backend": (
        CLIFFORD_SOURCE,
        "daf80f5ab2b4480e5e03b025bd685dd1ffdce91a4cb0435774dd52ad702b72c9",
        "portable_text",
    ),
    "canonical_scalar_five_form_backend": (
        FIVE_FORM_SOURCE,
        "3a87470a06362a2a4c05eac6b71fe9cd4cd6c9b8a41732786184cbfeae89fac4",
        "portable_text",
    ),
    "standard_embedding_and_hodge_audit": (
        BRANCHING_SOURCE,
        "c5954c21561f44ea183af17b4cd1205007c0b30021f4cca0a9fc4f96852c103a",
        "portable_text",
    ),
}

EXPECTED_INTERACTIONS = (
    "Y10",
    "Y126",
    "yP",
    "yQ",
    "yR",
    "ys",
    "lambdaP",
    "lambdaR",
    "lambdaQB",
    "lambdaQR",
)

EXPECTED_MODEL_16_PS_CARTAN_WEIGHTS = [
    ("-1", "-1/2", "0", 1),
    ("-1", "1/2", "0", 1),
    ("-1/3", "0", "-1/2", 3),
    ("-1/3", "0", "1/2", 3),
    ("1", "0", "-1/2", 1),
    ("1", "0", "1/2", 1),
    ("1/3", "-1/2", "0", 3),
    ("1/3", "1/2", "0", 3),
]
EXPECTED_MODEL_16BAR_PS_CARTAN_WEIGHTS = [
    ("-1", "0", "-1/2", 1),
    ("-1", "0", "1/2", 1),
    ("-1/3", "-1/2", "0", 3),
    ("-1/3", "1/2", "0", 3),
    ("1", "-1/2", "0", 1),
    ("1", "1/2", "0", 1),
    ("1/3", "0", "-1/2", 3),
    ("1/3", "0", "1/2", 3),
]


def _digest(path: Path, mode: str = "raw") -> str:
    data = path.read_bytes()
    if mode == "portable_text":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    elif mode != "raw":
        raise ValueError(f"unknown digest mode: {mode}")
    return hashlib.sha256(data).hexdigest()


def source_guard() -> dict[str, dict[str, str]]:
    observed: dict[str, dict[str, str]] = {}
    for name, (path, expected, mode) in DEPENDENCIES.items():
        digest = _digest(path, mode)
        if digest != expected:
            raise ArithmeticError(f"Yukawa-CGC dependency drifted: {name}")
        observed[name] = {
            "path": str(path.relative_to(HERE)),
            "sha256": digest,
            "mode": mode,
        }
    return observed


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _gaussian_integer(matrix: np.ndarray) -> np.ndarray:
    """Round an exact Pauli product and reject any non-Gaussian residue."""
    value = np.asarray(matrix, dtype=complex)
    real = np.rint(value.real).astype(np.int64)
    imag = np.rint(value.imag).astype(np.int64)
    exact = real + 1j * imag
    if not np.array_equal(value, exact):
        raise ArithmeticError("Clifford result is not an exact Gaussian integer")
    return exact


def _array_sha256(array: np.ndarray) -> str:
    value = np.asarray(array)
    packed = np.stack(
        (np.rint(value.real).astype("<i2"), np.rint(value.imag).astype("<i2")),
        axis=-1,
    )
    return hashlib.sha256(packed.tobytes(order="C")).hexdigest()


@dataclass(frozen=True)
class ExactCGC:
    channel: str
    numerator: np.ndarray
    denominator: int
    scalar_labels: tuple[str, ...]

    @property
    def n_scalars(self) -> int:
        return int(self.numerator.shape[0])

    @property
    def nonzero_count(self) -> int:
        return int(np.count_nonzero(self.numerator))

    def gram_numerator(self) -> np.ndarray:
        return np.einsum(
            "aij,bij->ab", self.numerator.conjugate(), self.numerator
        )

    def normalized_gram_is_identity(self) -> bool:
        expected = (self.denominator**2) * np.eye(self.n_scalars)
        return bool(np.array_equal(self.gram_numerator(), expected))

    def sparse_entries(self) -> tuple[tuple[int, int, int, int, int, int], ...]:
        entries: list[tuple[int, int, int, int, int, int]] = []
        for scalar, left, right in np.argwhere(self.numerator != 0):
            value = self.numerator[scalar, left, right]
            entries.append(
                (
                    int(scalar),
                    int(left),
                    int(right),
                    int(round(value.real)),
                    int(round(value.imag)),
                    self.denominator,
                )
            )
        return tuple(entries)


def _clifford_data() -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    return clifford.clifford_generators_so10()


def chiral_indices(sign: int) -> np.ndarray:
    if sign not in (-1, +1):
        raise ValueError("chirality sign must be -1 or +1")
    _, chirality, _ = _clifford_data()
    return np.flatnonzero(sign * np.real(np.diag(chirality)) > 0.5)


@lru_cache(maxsize=2)
def vector_numerators(chirality_sign: int = -1) -> np.ndarray:
    """Ten Gaussian-integer ``C Gamma_a`` matrices; normalized by 4."""
    matrices = clifford.chiral_vector_bilinears(chirality_sign)
    return np.asarray([_gaussian_integer(matrix) for matrix in matrices])


@lru_cache(maxsize=2)
def five_form_matrices(chirality_sign: int = -1) -> tuple[np.ndarray, ...]:
    """The 252 ordered-index ``C Gamma_[abcde]`` matrices."""
    gammas, _, charge_conjugation = _clifford_data()
    selected = chiral_indices(chirality_sign)
    output: list[np.ndarray] = []
    for indices in itertools.combinations(range(10), 5):
        product = np.eye(32, dtype=complex)
        for index in indices:
            product = product @ gammas[index]
        output.append(
            _gaussian_integer(
                (charge_conjugation @ product)[np.ix_(selected, selected)]
            )
        )
    return tuple(output)


def five_index_labels() -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.combinations(range(10), 5))


@lru_cache(maxsize=1)
def canonical_126_basis() -> tuple[five_forms.Form, ...]:
    """Source-bound kinetic-orthonormal physical ``-i`` Hodge basis."""
    return tuple(five_forms.anti_self_dual_five_form_basis())


@lru_cache(maxsize=2)
def physical_126_numerators(chirality_sign: int = -1) -> np.ndarray:
    labels = five_index_labels()
    raw = dict(zip(labels, five_form_matrices(chirality_sign), strict=True))
    output: list[np.ndarray] = []
    for state in canonical_126_basis():
        matrix = sum(
            (coefficient * raw[indices] for indices, coefficient in state.items()),
            np.zeros((16, 16), dtype=complex),
        )
        output.append(_gaussian_integer(matrix))
    return np.asarray(output)


def physical_126_shortcut_numerators() -> np.ndarray:
    """Independent complement-pair replay: each physical numerator is 2 T_I."""
    raw = dict(zip(five_index_labels(), five_form_matrices(-1), strict=True))
    return np.asarray(
        [2 * raw[min(state)] for state in canonical_126_basis()], dtype=complex
    )


def spinor_standard_model_weight_multiset(chirality_sign: int) -> list[tuple[str, str, str, int]]:
    """Exact ``(B-L,T3L,T3R)`` multiplicities in the standard embedding.

    Charges are returned as strings so the source-bound chirality assignment
    can be audited without floating diagonalization.  In this Clifford basis
    the five commuting plane operators are already diagonal Gaussian-integer
    matrices.  ``-i S_ab`` has half-integral eigenvalues.
    """
    twice_spin = twice_spin_generators(chirality_sign)

    def twice_hermitian(a: int, b: int) -> np.ndarray:
        return _gaussian_integer(-1j * twice_spin[(a, b)])

    plane2 = [
        twice_hermitian(0, 1),
        twice_hermitian(2, 3),
        twice_hermitian(4, 5),
        twice_hermitian(6, 7),
        twice_hermitian(8, 9),
    ]
    # Store 6(B-L), 2T3L and 2T3R as integers.
    six_bl = -2 * (plane2[0] + plane2[1] + plane2[2])
    two_t3l = _gaussian_integer((plane2[3] - plane2[4]) / 2)
    two_t3r = _gaussian_integer((plane2[3] + plane2[4]) / 2)
    if any(np.count_nonzero(matrix - np.diag(np.diag(matrix))) for matrix in (six_bl, two_t3l, two_t3r)):
        raise ArithmeticError("standard spinor Cartans are not diagonal")

    def rational_label(numerator: int, denominator: int) -> str:
        from fractions import Fraction

        return str(Fraction(numerator, denominator))

    counts: dict[tuple[str, str], int] = {}
    for index in range(16):
        bl6 = int(round(six_bl[index, index].real))
        l2 = int(round(two_t3l[index, index].real))
        r2 = int(round(two_t3r[index, index].real))
        key = (
            rational_label(bl6, 6),
            rational_label(l2, 2),
            rational_label(r2, 2),
        )
        counts[key] = counts.get(key, 0) + 1
    return [(bl, t3l, t3r, multiplicity) for (bl, t3l, t3r), multiplicity in sorted(counts.items())]


@lru_cache(maxsize=1)
def singlet_clifford_numerator() -> np.ndarray:
    """Invariant 16 x 16bar pairing in the two raw Clifford bases."""
    _, _, charge_conjugation = _clifford_data()
    minus = chiral_indices(-1)
    plus = chiral_indices(+1)
    return _gaussian_integer(charge_conjugation[np.ix_(minus, plus)])


def cgc_10() -> ExactCGC:
    return ExactCGC(
        channel="16x16x10",
        numerator=vector_numerators(-1),
        denominator=4,
        scalar_labels=tuple(f"e{index}" for index in range(10)),
    )


def cgc_126bar() -> ExactCGC:
    labels = tuple(
        "+".join("".join(str(index) for index in term) for term in state)
        for state in canonical_126_basis()
    )
    return ExactCGC(
        channel="16x16x126bar",
        numerator=physical_126_numerators(-1),
        denominator=8,
        scalar_labels=labels,
    )


def cgc_singlet_dual_basis() -> ExactCGC:
    return ExactCGC(
        channel="16x16barx1",
        numerator=np.eye(16, dtype=complex)[None, :, :],
        denominator=4,
        scalar_labels=("1",),
    )


def twice_spin_generators(chirality_sign: int) -> dict[tuple[int, int], np.ndarray]:
    """Return ``2 S_ab = Gamma_a Gamma_b`` on one chiral subspace."""
    gammas, _, _ = _clifford_data()
    selected = chiral_indices(chirality_sign)
    return {
        (a, b): _gaussian_integer(
            (gammas[a] @ gammas[b])[np.ix_(selected, selected)]
        )
        for a, b in itertools.combinations(range(10), 2)
    }


def vector_generator(a: int, b: int) -> np.ndarray:
    matrix = np.zeros((10, 10), dtype=complex)
    matrix[a, b] = 1
    matrix[b, a] = -1
    return matrix


@lru_cache(maxsize=45)
def physical_126_generator(a: int, b: int) -> np.ndarray:
    """Exact coordinate generator on the canonical ``-i`` Hodge basis."""
    basis = canonical_126_basis()
    first_to_row = {min(state): row for row, state in enumerate(basis)}
    matrix = np.zeros((126, 126), dtype=complex)
    for column, state in enumerate(basis):
        transformed = five_forms.generator_action(state, a, b)
        for indices, coefficient in transformed.items():
            if indices in first_to_row:
                matrix[first_to_row[indices], column] = coefficient
    matrix = _gaussian_integer(matrix)
    # Verify that first-component coordinates reconstruct every complement.
    for column, state in enumerate(basis):
        reconstructed = five_forms.add_forms(
            *[
                five_forms.scale_form(basis[row], matrix[row, column])
                for row in np.flatnonzero(matrix[:, column])
            ]
        )
        transformed = five_forms.generator_action(state, a, b)
        keys = set(reconstructed).union(transformed)
        if any(reconstructed.get(key, 0) != transformed.get(key, 0) for key in keys):
            raise ArithmeticError("five-form coordinate reconstruction failed")
    return matrix


def covariance_residuals() -> dict[str, int]:
    """Exact all-45-generator covariance residuals, with no tolerance."""
    spin_minus = twice_spin_generators(-1)
    spin_plus = twice_spin_generators(+1)
    vector = vector_numerators(-1)
    sigma = physical_126_numerators(-1)
    duality = singlet_clifford_numerator()
    maxima = {"10": 0, "126bar": 0, "singlet": 0}
    for pair in itertools.combinations(range(10), 2):
        k_minus = spin_minus[pair]
        k_plus = spin_plus[pair]

        r10 = vector_generator(*pair)
        left10 = np.einsum("ij,ajk->aik", k_minus.T, vector)
        left10 += np.einsum("aij,jk->aik", vector, k_minus)
        left10 += 2 * np.einsum("bij,ba->aij", vector, r10)
        maxima["10"] = max(maxima["10"], int(np.max(np.abs(left10))))

        r126 = physical_126_generator(*pair)
        left126 = np.einsum("ij,ajk->aik", k_minus.T, sigma)
        left126 += np.einsum("aij,jk->aik", sigma, k_minus)
        left126 += 2 * np.einsum("bij,ba->aij", sigma, r126)
        maxima["126bar"] = max(
            maxima["126bar"], int(np.max(np.abs(left126)))
        )

        singlet = k_minus.T @ duality + duality @ k_plus
        maxima["singlet"] = max(
            maxima["singlet"], int(np.max(np.abs(singlet)))
        )
    return maxima


@dataclass(frozen=True)
class FermionBlock:
    name: str
    generations: int
    signed_so10_rep: int
    x: int
    z17: int
    start: int
    stop: int

    @property
    def representation(self) -> str:
        return "16" if self.signed_so10_rep == 16 else "16bar"

    @property
    def chirality(self) -> int:
        return -1 if self.signed_so10_rep == 16 else +1

    def copy_start(self, generation: int) -> int:
        if not 0 <= generation < self.generations:
            raise IndexError("generation outside fermion block")
        return self.start + 16 * generation


def canonical_304_inventory() -> tuple[FermionBlock, ...]:
    pattern = re.compile(
        r"FermionFields\[\[\d+\]\]\s*=\s*\{\s*(\w+)\s*,\s*(\d+)\s*,"
        r"\s*\w+\s*,\s*(-?16)\s*,\s*(-?\d+)\s*,\s*([^}]+?)\s*\};"
    )
    rows = pattern.findall(MODEL.read_text(encoding="utf-8"))
    if len(rows) != 9:
        raise ArithmeticError(f"expected nine fermion blocks, found {len(rows)}")
    output: list[FermionBlock] = []
    offset = 0
    for name, generations, signed_rep, x, z17_expression in rows:
        z17_text = z17_expression.strip()
        if re.fullmatch(r"-?\d+", z17_text):
            z17 = int(z17_text) % 17
        else:
            phase = re.fullmatch(
                r"Exp\[\s*2\s*\*\s*Pi\s*\*\s*I\s*\*\s*(-?\d+)\s*/\s*17\s*\]",
                z17_text,
            )
            if phase is None:
                raise ArithmeticError(
                    f"unsupported exact Z17 charge expression for {name}: {z17_text}"
                )
            z17 = int(phase.group(1)) % 17
        count = int(generations)
        stop = offset + 16 * count
        output.append(
            FermionBlock(
                name=name,
                generations=count,
                signed_so10_rep=int(signed_rep),
                x=int(x),
                z17=z17,
                start=offset,
                stop=stop,
            )
        )
        offset = stop
    if offset != 304:
        raise ArithmeticError(f"expected 304 Weyl components, found {offset}")
    return tuple(output)


INTERACTION_SPECS: dict[str, dict[str, Any]] = {
    "Y10": {"left": "F", "right": "F", "channel": "10", "family": "symmetric_3x3"},
    "Y126": {"left": "F", "right": "F", "channel": "126bar", "family": "symmetric_3x3"},
    "yP": {"left": "P", "right": "Pbar", "channel": "singlet", "family": "scalar"},
    "yQ": {"left": "Q", "right": "Qbar", "channel": "singlet", "family": "scalar"},
    "yR": {"left": "R", "right": "Rbar", "channel": "singlet", "family": "scalar"},
    "ys": {"left": "SpecS", "right": "SpecB", "channel": "singlet", "family": "general_5x5"},
    "lambdaP": {"left": "P", "right": "F", "channel": "10", "family": "row_1x3"},
    "lambdaR": {"left": "R", "right": "F", "channel": "10", "family": "row_1x3"},
    "lambdaQB": {"left": "Qbar", "right": "F", "channel": "singlet", "family": "row_1x3"},
    "lambdaQR": {"left": "Q", "right": "Rbar", "channel": "singlet", "family": "scalar"},
}

MODEL_TERMS = {
    "Y10": "Y10F.F.H10",
    "Y126": "Y126F.F.Delta126bar",
    "yP": "yPconj[Phi17].P.Pbar",
    "yQ": "yQconj[Phi17].Q.Qbar",
    "yR": "yRPhi17.R.Rbar",
    "ys": "ysS.SpecS.SpecB",
    "lambdaP": "lambdaPP.F.H10",
    "lambdaR": "lambdaRR.F.H10",
    "lambdaQB": "lambdaQBconj[S].Qbar.F",
    "lambdaQR": "lambdaQRS.Q.Rbar",
}


def verify_declared_interactions() -> None:
    compact = re.sub(r"\s+", "", MODEL.read_text(encoding="utf-8"))
    missing = [name for name, term in MODEL_TERMS.items() if term not in compact]
    if missing:
        raise ArithmeticError(f"authoritative Yukawa declarations missing: {missing}")
    if tuple(INTERACTION_SPECS) != EXPECTED_INTERACTIONS:
        raise ArithmeticError("declared interaction order drifted")


def cgc_for_channel(channel: str) -> ExactCGC:
    if channel == "10":
        return cgc_10()
    if channel == "126bar":
        return cgc_126bar()
    if channel == "singlet":
        return cgc_singlet_dual_basis()
    raise KeyError(channel)


def embedded_sparse_support(
    symbol: str,
) -> tuple[tuple[int, int, int, int, int, int], ...]:
    """Embed one generic symbolic-flavor vertex into indices 0..303.

    Entries are ``(scalar_component, global_left, global_right,
    real_numerator, imag_numerator, denominator)``.  Every allowed flavor
    pair is included; coefficients of the symbolic flavor tensor are not.
    """
    spec = INTERACTION_SPECS[symbol]
    blocks = {row.name: row for row in canonical_304_inventory()}
    left = blocks[spec["left"]]
    right = blocks[spec["right"]]
    tensor = cgc_for_channel(spec["channel"])
    output: list[tuple[int, int, int, int, int, int]] = []
    for left_generation in range(left.generations):
        for right_generation in range(right.generations):
            left_offset = left.copy_start(left_generation)
            right_offset = right.copy_start(right_generation)
            for scalar, i, j, real, imag, denominator in tensor.sparse_entries():
                output.append(
                    (
                        scalar,
                        left_offset + i,
                        right_offset + j,
                        real,
                        imag,
                        denominator,
                    )
                )
    return tuple(output)


def exact_checks() -> dict[str, bool]:
    source_guard()
    verify_declared_interactions()
    ten = cgc_10()
    sigma = cgc_126bar()
    singlet = cgc_singlet_dual_basis()
    ten_sigma_overlap = np.einsum(
        "aij,rij->ar", ten.numerator.conjugate(), sigma.numerator
    )

    # Multiply the normalized completeness projector by 64 to stay integral.
    projector64 = 4 * np.einsum(
        "aij,akl->ijkl", ten.numerator, ten.numerator.conjugate()
    )
    projector64 += np.einsum(
        "rij,rkl->ijkl", sigma.numerator, sigma.numerator.conjugate()
    )
    expected64 = np.zeros((16, 16, 16, 16), dtype=complex)
    for i, j, k, ell in itertools.product(range(16), repeat=4):
        expected64[i, j, k, ell] = 32 * (
            (i == k and j == ell) + (i == ell and j == k)
        )

    duality = singlet_clifford_numerator()
    covariance = covariance_residuals()
    inventory = canonical_304_inventory()
    supports = {name: embedded_sparse_support(name) for name in EXPECTED_INTERACTIONS}
    checks = {
        "authoritative_sources_match_frozen_hashes": bool(source_guard()),
        "all_ten_declared_yukawa_symbols_found": True,
        "canonical_inventory_has_19_weyl_multiplets": sum(row.generations for row in inventory) == 19,
        "canonical_inventory_has_304_weyl_components": inventory[-1].stop == 304,
        "minus_chirality_has_standard_model_16_weights": spinor_standard_model_weight_multiset(-1) == EXPECTED_MODEL_16_PS_CARTAN_WEIGHTS,
        "plus_chirality_is_conjugate_16bar": spinor_standard_model_weight_multiset(+1) == EXPECTED_MODEL_16BAR_PS_CARTAN_WEIGHTS,
        "vector_has_ten_symmetric_matrices": ten.n_scalars == 10 and all(np.array_equal(x, x.T) for x in ten.numerator),
        "vector_normalized_gram_is_identity": ten.normalized_gram_is_identity(),
        "physical_126bar_has_126_symmetric_matrices": sigma.n_scalars == 126 and all(np.array_equal(x, x.T) for x in sigma.numerator),
        "physical_126bar_normalized_gram_is_identity": sigma.normalized_gram_is_identity(),
        "physical_126bar_complement_shortcut_agrees": np.array_equal(sigma.numerator, physical_126_shortcut_numerators()),
        "opposite_spinor_chirality_annihilates_physical_126bar": not np.any(physical_126_numerators(+1)),
        "ten_and_126bar_are_exactly_orthogonal": not np.any(ten_sigma_overlap),
        "ten_plus_126bar_complete_symmetric_square": np.array_equal(projector64, expected64),
        "singlet_duality_map_is_unitary": np.array_equal(duality @ duality.conjugate().T, np.eye(16)),
        "singlet_dual_basis_normalized_gram_is_identity": singlet.normalized_gram_is_identity(),
        "all_45_vector_covariance_residuals_zero": covariance["10"] == 0,
        "all_45_126bar_covariance_residuals_zero": covariance["126bar"] == 0,
        "all_45_singlet_covariance_residuals_zero": covariance["singlet"] == 0,
        "vector_sparse_count_is_160": ten.nonzero_count == 160,
        "physical_126bar_sparse_count_is_2016": sigma.nonzero_count == 2016,
        "singlet_sparse_count_is_16": singlet.nonzero_count == 16,
        "all_embedded_support_indices_lie_in_304_inventory": all(
            0 <= row[1] < 304 and 0 <= row[2] < 304
            for rows in supports.values()
            for row in rows
        ),
        "all_declared_representation_cgcs_closed": all(
            cgc_for_channel(INTERACTION_SPECS[name]["channel"]).normalized_gram_is_identity()
            for name in EXPECTED_INTERACTIONS
        ),
        "flavor_boundary_values_closed": False,
        "sarah_symbol_normalization_closed": False,
        "full_yukawa_rge_closed": False,
        "full_physical_G7_closed": False,
    }
    return checks


def _tensor_summary(tensor: ExactCGC) -> dict[str, Any]:
    magnitudes = sorted(
        {
            f"{int(round(abs(value)))} / {tensor.denominator}"
            for value in tensor.numerator.flat
            if value != 0
        }
    )
    return {
        "channel": tensor.channel,
        "shape": list(tensor.numerator.shape),
        "numerator_sha256_i16_real_imag_C_order": _array_sha256(tensor.numerator),
        "denominator": tensor.denominator,
        "nonzero_count": tensor.nonzero_count,
        "nonzero_magnitudes": magnitudes,
        "numerator_gram_diagonal": tensor.denominator**2,
        "normalized_gram": "identity",
        "scalar_basis_labels": list(tensor.scalar_labels),
    }


def build_report() -> dict[str, Any]:
    dependencies = source_guard()
    verify_declared_interactions()
    checks = exact_checks()
    deliberately_open = {
        "flavor_boundary_values_closed",
        "sarah_symbol_normalization_closed",
        "full_yukawa_rge_closed",
        "full_physical_G7_closed",
    }
    positive_failures = [
        key for key, value in checks.items() if not value and key not in deliberately_open
    ]
    if positive_failures:
        raise ArithmeticError(f"exact Yukawa-CGC checks failed: {positive_failures}")

    inventory = canonical_304_inventory()
    tensors = {
        "10": _tensor_summary(cgc_10()),
        "126bar": _tensor_summary(cgc_126bar()),
        "singlet_dual_basis": _tensor_summary(cgc_singlet_dual_basis()),
    }
    closure = []
    for symbol in EXPECTED_INTERACTIONS:
        spec = INTERACTION_SPECS[symbol]
        support = embedded_sparse_support(symbol)
        closure.append(
            {
                "symbol": symbol,
                "left": spec["left"],
                "right": spec["right"],
                "channel": spec["channel"],
                "family_tensor": spec["family"],
                "representation_CGC_closed": True,
                "flavor_tensor_preserved_symbolically": True,
                "generic_flavor_sparse_support_count": len(support),
                "global_left_range": [min(row[1] for row in support), max(row[1] for row in support)],
                "global_right_range": [min(row[2] for row in support), max(row[2] for row in support)],
            }
        )

    core = {
        "contract_id": CONTRACT_ID,
        "status": STATUS,
        "dependencies": dependencies,
        "conventions": {
            "model_16_clifford_chirality": -1,
            "model_16bar_clifford_chirality": +1,
            "physical_Delta126bar_hodge_eigenvalue": "-i",
            "Delta126bar_kinetic_term": "Sigma*Sigma/(2*5!)",
            "cgc_inner_product": "Tr(C_A^dagger C_B)=delta_AB",
            "five_index_antisymmetrization": "strictly increasing indices; Gamma_[I]=ordered product because distinct gammas anticommute",
            "lagrangian_identical_Weyl_convention": "-1/2 Y_AB psi_A psi_B C_r phi_r + h.c. within this artifact",
            "sarah_Dot_conversion": "open; no numerical conversion factor inferred",
        },
        "canonical_304_weyl_inventory": [
            {
                "name": row.name,
                "generations": row.generations,
                "SO10": row.representation,
                "X": row.x,
                "Z17": row.z17,
                "clifford_chirality": row.chirality,
                "global_component_half_open_range": [row.start, row.stop],
                "generation_offsets": [row.copy_start(index) for index in range(row.generations)],
            }
            for row in inventory
        ],
        "weyl_multiplet_count": sum(row.generations for row in inventory),
        "weyl_component_count": inventory[-1].stop,
        "normalized_tensors": tensors,
        "chirality_obstruction": {
            "wrong_plus_chirality_contraction_rank": int(np.linalg.matrix_rank(physical_126_numerators(+1).reshape(126, 256))),
            "correct_minus_chirality_contraction_rank": 126,
            "wrong_plus_chirality_is_identically_zero": True,
            "normalization_is_fixed_not_guessed": True,
            "model_16_standard_PS_Cartan_weights": [
                list(row) for row in spinor_standard_model_weight_multiset(-1)
            ],
            "model_16bar_conjugate_Cartan_weights": [
                list(row) for row in spinor_standard_model_weight_multiset(+1)
            ],
        },
        "covariance": {
            "generators_tested_per_channel": 45,
            "exact_integer_residual_maxima": covariance_residuals(),
            "floating_tolerance_used": False,
        },
        "symmetric_square_theorem": {
            "dim_Sym2_16": 136,
            "10_plus_126": 136,
            "orthonormal_complete_projector_verified_exactly": True,
        },
        "declared_yukawa_closure": closure,
        "total_generic_flavor_sparse_support_count": sum(row["generic_flavor_sparse_support_count"] for row in closure),
        "checks": checks,
        "scope": {
            "normalized_representation_CGCs_for_all_declared_Yukawas": True,
            "canonical_304_Weyl_sparse_embedding": True,
            "flavor_tensor_values_or_textures": False,
            "sarah_implicit_contraction_normalization": False,
            "one_or_two_loop_Yukawa_betas": False,
            "threshold_matching_and_running": False,
            "full_yukawa_sector": False,
            "mathematical_G7": False,
            "release_G7": False,
        },
        "blockers": [
            "Fix the conversion between this explicit -1/2 identical-Weyl convention and SARAH's implicit Dot contractions.",
            "Supply or fit the symbolic flavor tensors and their boundary conditions.",
            "Compile independently replayed one- and two-loop Yukawa, scalar and dimensionful beta functions.",
            "Derive physical component masses, mixing matrices and finite threshold matching before claiming G7.",
        ],
    }
    return {"core_sha256": _canonical_sha256(core), **core}


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Exact normalized SO(10) Yukawa CGCs — v20",
        "",
        f"Status: `{report['status']}`",
        "",
        f"Core SHA-256: `{report['core_sha256']}`",
        "",
        "## Closed representation theorem",
        "",
        "The exact Clifford construction gives `16 x 16 x 10 = (C Gamma_a)|_- / 4`. "
        "Projection onto the canonical kinetic-normalized physical `-i` Hodge basis gives "
        "`16 x 16 x 126bar = sum_I E[r,I](C Gamma_I)|_- / 8`.  Their Gram matrices "
        "are identities, both families are symmetric, mutually orthogonal, SO(10)-covariant "
        "under all 45 generators, and together form the complete 136-dimensional symmetric square.",
        "",
        "The opposite Clifford chirality contracts identically to zero with this physical "
        "`126bar`; this exact obstruction fixes the chirality assignment and prevents a guessed CGC.",
        "",
        "## Canonical inventory and declared symbols",
        "",
        f"The source-bound inventory contains {report['weyl_multiplet_count']} Weyl multiplets and "
        f"{report['weyl_component_count']} Weyl components.  Normalized representation CGCs are "
        "closed for:",
        "",
    ]
    for row in report["declared_yukawa_closure"]:
        lines.append(
            f"- `{row['symbol']}`: {row['left']} x {row['right']} through "
            f"`{row['channel']}`; flavor tensor `{row['family_tensor']}` remains symbolic."
        )
    lines.extend(
        [
            "",
            "## Fail-closed boundary",
            "",
            "This artifact does not infer SARAH's implicit identical-field normalization, choose "
            "flavor boundary values, compute Yukawa/scalar/dimensionful beta functions, or provide "
            "physical component thresholds.  Full Yukawa closure and mathematical/release G7 remain false.",
            "",
            "## Exact checks",
            "",
        ]
    )
    for name, value in report["checks"].items():
        lines.append(f"- `{name}`: `{str(value).lower()}`")
    return "\n".join(lines) + "\n"


def write_outputs() -> dict[str, Any]:
    report = build_report()
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    OUT_MD.write_text(render_markdown(report), encoding="utf-8", newline="\n")
    return report


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown reports")
    args = parser.parse_args(list(argv) if argv is not None else None)
    report = write_outputs() if args.write else build_report()
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
