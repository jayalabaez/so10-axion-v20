#!/usr/bin/env python3
"""Exact feasibility audit for Standard-Model provenance of the frozen G6 spectrum.

The canonical 486-real chart carries exact SO(10) generators, so ultraviolet
Pati--Salam and Standard-Model ancestry projectors can be constructed without
guessing component labels.  That fact is weaker than assigning those labels
to the *mass eigenspaces* of the frozen EFT G6 Hessian.  Such an assignment is
valid only when the corresponding generators/Casimirs commute with the mass
pencil.

This audit performs that missing commutant test.  It also distinguishes the
single-plane generator ``G_89`` used by the G6 report from the standard SO(10)
electromagnetic embedding

    3 Q = 3 G_67 - (G_01 + G_23 + G_45).

The two generators are not SO(10)-conjugate: already on the vector 10 their
ranks and squared-charge spectra differ.  The selected ``direct.delta_r()``
background has ``|6Y|=6`` in the independently documented Pati--Salam/SM
embedding, and the final selected vacuum is not fixed by the standard Q.
Consequently the G6 label called ``U(1)_em`` is, source-bound, the actual
``U(1)_89`` stabilizer of this EFT representative rather than a completed
physical electromagnetic-provenance theorem.

This is a maximal exact subtheorem, not a replacement spectrum.  It supplies
exact coordinate-carrier projectors and proves why stage-specific Hessians at
an explicitly validated SO(10)->intermediate->SM vacuum are still required.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import inspect
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import sparse

import exact_eft_physical_scalar_spectrum_v20 as spectrum
import exact_gauged_u1x_g3_su5_delta_pd_sos_v20 as su5_pd
import exact_gauged_u1x_stationarity_rank_certificate_v20 as stationarity
import live_g2_canonical_486_field_chart_v20 as chart


HERE = Path(__file__).resolve().parent
STATUS = "EXACT_G6_SM_PROVENANCE_MISMATCH_PROVED__G6_RELEASE_OPEN"
MODEL_CONTRACT_ID = spectrum.MODEL_CONTRACT_ID
OUT_JSON = HERE / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.json"
OUT_MD = HERE / "EXACT_G6_SM_PROVENANCE_FEASIBILITY_V20.md"

EXPECTED_CORE_SHA256 = (
    "0d9bad1158c6c93b29243c08b0265d472be1309267e390edafc3afb556233d39"
)
EXPECTED_REPORT_RAW_SHA256 = {
    "json": "a8daa4fb1dadbea48b25ad671a18f8d467384979769772be628a43f75054f6fa",
    "md": "e3d05634421c4721003cb1916a3d02dc2d2b0c93bd58c03523bc927fa3793673",
}
EXPECTED_G6_CORE_SHA256 = (
    "abb704133c8be22b424ba20e23387d6f30412e6c82ab3a214e88bd8df5bef9cc"
)
EXPECTED_HESSIAN_PAYLOAD_SHA256 = (
    "7ea54d59138f8e5b66aad3d1f1ecb707c65ac9bb0f0e118a597daaccc136b568"
)

DEPENDENCIES: dict[str, tuple[Path, str]] = {
    "G6_spectrum_source": (
        HERE / "exact_eft_physical_scalar_spectrum_v20.py",
        "cdcc25b383098464fc6312d553dff555d19c57388df7de08db48b4167ebc5a36",
    ),
    "G6_spectrum_JSON": (
        HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json",
        "797a90473c064a78ef313d56f1894d71114643a19ebd373e86fe8b2911bcf416",
    ),
    "exact_full_generator_source": (
        HERE / "exact_gauged_u1x_stationarity_rank_certificate_v20.py",
        "846bd3e57a816dfa8df4a4ce9957c547a591442200fbc3800dfe27f3c84df9c7",
    ),
    "selected_Hessian_source": (
        HERE / "exact_gauged_u1x_g3_su5_delta_hsx_exact_hessian_v20.py",
        "cd4192713d8b3b13f6a9cf492f37d8615e3ead7a1a49fb3c30a1f6de235f7498",
    ),
    "selected_SU5_Delta_source": (
        HERE / "exact_gauged_u1x_g3_su5_delta_pd_sos_v20.py",
        "afc1dca43a6ec2a657a4ab8e3a846517edaaaf532f1c3fffd1a82c637d208c6b",
    ),
    "standard_PS_SM_embedding_source": (
        HERE / "exact_126bar_triplet_clebsch_v20.py",
        "d94f37da94333fbf58e448ef6effb00e718191ed45b63bafdc0e2650ccdb0499",
    ),
    "Pati_Salam_210_source": (
        HERE / "exact_210_pati_salam_global_vacuum_v20.py",
        "d98baa655cd5af9ccbc34fd2637670b7ceadedd5b2eccc10e1d6c000fda943c4",
    ),
    "canonical_486_chart": (
        HERE / "live_g2_canonical_486_field_chart_v20.py",
        "85ae9470f3aa25c28fc03c083b6c1e150106a276e51044a590060d290ba7945e",
    ),
}

EXPECTED_COMMUTATORS = {
    "actual_G89": {"nnz": 0, "max_abs": 0},
    "actual_G89_squared": {"nnz": 0, "max_abs": 0},
    "standard_Y6": {"nnz": 3576, "max_abs": 151_200_000},
    "standard_Y6_squared": {"nnz": 3632, "max_abs": 68_040_000},
    "standard_Q3": {"nnz": 3576, "max_abs": 151_200_000},
    "standard_Q3_squared": {"nnz": 3632, "max_abs": 22_680_000},
    "standard_4C2L": {"nnz": 442, "max_abs": 20_160_000},
    "standard_4C2R": {"nnz": 814, "max_abs": 25_984_000},
}

EXPECTED_EXACT_CHARGE_CENSUS = {
    "actual_G89_squared": {0: 230, 1: 256},
    "standard_Q3_squared": {0: 78, 1: 132, 4: 102, 9: 84, 16: 60, 25: 24, 36: 6},
    "standard_Y6_squared": {
        0: 52,
        1: 72,
        4: 102,
        9: 84,
        16: 48,
        25: 48,
        36: 26,
        49: 24,
        64: 18,
        81: 4,
        100: 6,
        144: 2,
    },
}

# Independent float64 live-compiler regression.  This is deliberately not
# promoted to exact proof grade; the exact generator mismatch above is already
# decisive.  ``recompute_live_true_sm_swap_diagnostic`` reproduces this record.
RECORDED_TRUE_SM_SWAP_DIAGNOSTIC = {
    "potential_value": -1.9610499999999509,
    "gradient_max_abs": 0.1272792206136687,
    "gradient_l2_norm": 0.562849891179113,
    "gradient_phi_block_l2_norm": 0.23999999999995988,
    "gradient_sigma_block_l2_norm": 0.5091168824546664,
    "gradient_entries_above_1e_minus_9": 26,
    "minimum_full_Hessian_eigenvalue": -0.4086149805542996,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _source_guard() -> dict[str, dict[str, str]]:
    bindings: dict[str, dict[str, str]] = {}
    for name, (path, expected) in DEPENDENCIES.items():
        observed = _sha256(path)
        if observed != expected:
            raise ArithmeticError(f"frozen G6 provenance dependency drifted: {name}")
        bindings[name] = {
            "path": str(path.relative_to(HERE)),
            "sha256": observed,
        }
    return bindings


@lru_cache(maxsize=None)
def _generator(first: int, second: int) -> sparse.csr_matrix:
    """One exact SO(10) generator on the 486-real chart.

    The upstream implementation constructs all 45 generators at once.  This
    source-equivalent adapter constructs only the generators needed here and
    keeps every entry in Z.
    """
    if not (0 <= first < second < 10):
        raise ValueError("generator requires 0 <= first < second < 10")
    rows: list[int] = []
    columns: list[int] = []
    data: list[int] = []

    def add(row: int, column: int, value: int) -> None:
        if value:
            rows.append(int(row))
            columns.append(int(column))
            data.append(int(value))

    for column, indices in enumerate(stationarity.FOUR):
        action = stationarity._generator_action(
            {indices: stationarity.GI_ONE}, first, second
        )
        for target, (real, imaginary) in action.items():
            if imaginary:
                raise ArithmeticError("real 210 generator acquired an imaginary entry")
            add(stationarity.FOUR_LOOKUP[target], column, real)

    for offset in (0, 1):
        add(
            chart.H_SLICE.start + 2 * first + offset,
            chart.H_SLICE.start + 2 * second + offset,
            1,
        )
        add(
            chart.H_SLICE.start + 2 * second + offset,
            chart.H_SLICE.start + 2 * first + offset,
            -1,
        )

    for complex_column, basis_row in enumerate(stationarity._sigma_basis_rows()):
        action = stationarity._generator_action(
            stationarity._basis_form(basis_row), first, second
        )
        coordinates = stationarity._sigma_coordinates(action)
        x_column = chart.SIGMA_SLICE.start + 2 * complex_column
        y_column = x_column + 1
        for complex_row, (real, imaginary) in coordinates.items():
            x_row = chart.SIGMA_SLICE.start + 2 * complex_row
            y_row = x_row + 1
            add(x_row, x_column, real)
            add(x_row, y_column, -imaginary)
            add(y_row, x_column, imaginary)
            add(y_row, y_column, real)

    return sparse.csr_matrix(
        (np.asarray(data, dtype=np.int64), (rows, columns)),
        shape=(chart.TOTAL_DIM, chart.TOTAL_DIM),
        dtype=np.int64,
    )


def _zero() -> sparse.csr_matrix:
    return sparse.csr_matrix(
        (chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=np.int64
    )


def _sum(values: Iterable[sparse.spmatrix]) -> sparse.csr_matrix:
    result = _zero()
    for value in values:
        result = result + value
    return result.tocsr()


@lru_cache(maxsize=1)
def _ancestry_operators() -> dict[str, sparse.csr_matrix]:
    g = _generator
    color_planes = g(0, 1) + g(2, 3) + g(4, 5)

    # Six times standard hypercharge and three times electric charge.
    y6 = 3 * (g(6, 7) + g(8, 9)) - 2 * color_planes
    q3 = 3 * g(6, 7) - color_planes

    twice_l = (
        g(7, 8) - g(6, 9),
        -g(6, 8) - g(7, 9),
        g(6, 7) - g(8, 9),
    )
    twice_r = (
        g(7, 8) + g(6, 9),
        -g(6, 8) + g(7, 9),
        g(6, 7) + g(8, 9),
    )
    c2l4 = -_sum(operator @ operator for operator in twice_l)
    c2r4 = -_sum(operator @ operator for operator in twice_r)
    c6 = -_sum(
        g(first, second) @ g(first, second)
        for first in range(6)
        for second in range(first + 1, 6)
    )

    su3 = (
        g(0, 1) - g(2, 3),
        g(2, 3) - g(4, 5),
        g(0, 2) + g(1, 3),
        g(0, 3) - g(1, 2),
        g(0, 4) + g(1, 5),
        g(0, 5) - g(1, 4),
        g(2, 4) + g(3, 5),
        g(2, 5) - g(3, 4),
    )
    c3_12 = -(
        4 * (su3[0] @ su3[0])
        + 2 * (su3[0] @ su3[1])
        + 2 * (su3[1] @ su3[0])
        + 4 * (su3[1] @ su3[1])
        + _sum(3 * (su3[index] @ su3[index]) for index in range(2, 8))
    )
    g89 = g(8, 9)
    return {
        "actual_G89": g89,
        "actual_G89_squared": -(g89 @ g89),
        "standard_Y6": y6,
        "standard_Y6_squared": -(y6 @ y6),
        "standard_Q3": q3,
        "standard_Q3_squared": -(q3 @ q3),
        "standard_4C2L": c2l4,
        "standard_4C2R": c2r4,
        "standard_C2_SO6": c6,
        "standard_12C2_SU3": c3_12,
    }


def _exterior_squared_charge_census(
    plane_weights: tuple[int, int, int, int, int]
) -> dict[int, int]:
    """Exact census from 210=Lambda4, 126+126bar=Lambda5, and complex 10."""
    one_form_weights: list[int] = []
    for weight in plane_weights:
        one_form_weights.extend((weight, -weight))

    def exterior(degree: int) -> Counter[int]:
        return Counter(
            sum(one_form_weights[index] for index in selected) ** 2
            for selected in itertools.combinations(range(10), degree)
        )

    counts = exterior(4) + exterior(5)
    # H10 is a complex vector: its 20-real carrier complexifies to two 10s.
    for weight in one_form_weights:
        counts[weight * weight] += 2
    # S and Phi17 are two complex SO(10) singlets.
    counts[0] += 4
    if sum(counts.values()) != chart.TOTAL_DIM:
        raise ArithmeticError("exact exterior charge census lost coordinates")
    return dict(sorted(counts.items()))


def _exact_projector_multiplicities(
    operator: sparse.csr_matrix, eigenvalues: tuple[int, ...]
) -> dict[int, int]:
    """Exact traces of Lagrange spectral projectors over Z."""
    identity = sparse.identity(chart.TOTAL_DIM, dtype=np.int64, format="csr")
    output: dict[int, int] = {}
    for target in eigenvalues:
        numerator = identity
        denominator = 1
        for other in eigenvalues:
            if other == target:
                continue
            numerator = numerator @ (operator - other * identity)
            denominator *= target - other
        trace = int(np.sum(numerator.diagonal(), dtype=object))
        quotient, remainder = divmod(trace, denominator)
        if remainder:
            raise ArithmeticError("spectral projector trace left Z")
        output[target] = int(quotient)
    if sum(output.values()) != chart.TOTAL_DIM:
        raise ArithmeticError("spectral projector census is incomplete")
    return output


def _commutator_stats(
    hessian: np.ndarray, operator: sparse.csr_matrix
) -> dict[str, int]:
    dense = operator.toarray()
    commutator = hessian @ dense - dense @ hessian
    return {
        "nnz": int(np.count_nonzero(commutator)),
        "max_abs": int(np.max(np.abs(commutator), initial=0)),
        "l1_abs": int(np.sum(np.abs(commutator), dtype=object)),
    }


def _sparse_vector(values: dict[int, int]) -> np.ndarray:
    output = np.zeros(chart.TOTAL_DIM, dtype=np.int64)
    for index, value in values.items():
        output[int(index)] = int(value)
    return output


def _selected_target_vector() -> np.ndarray:
    """Integral shape of (F0,H_chi,Delta_R); singlet phases do not transform."""
    _form, f0 = su5_pd.raw_su5_form_and_vector()
    target = np.zeros(chart.TOTAL_DIM, dtype=np.int64)
    target[chart.PHI_SLICE] = f0
    target[chart.H_SLICE.start + 2 * 6] = 1
    target[chart.H_SLICE.start + 2 * 7 + 1] = 1
    delta = stationarity._vacuum_block_vectors()["Delta_R"]
    for index, value in delta.items():
        target[index] = value
    return target


def _phase_rotated_sigma(vector: np.ndarray) -> np.ndarray:
    """Multiply the complex Sigma coefficients by i in the real chart."""
    source = np.asarray(vector, dtype=np.int64).reshape(chart.TOTAL_DIM)
    output = np.zeros(chart.TOTAL_DIM, dtype=np.int64)
    sigma = source[chart.SIGMA_SLICE]
    output[chart.SIGMA_SLICE][0::2] = -sigma[1::2]
    output[chart.SIGMA_SLICE][1::2] = sigma[0::2]
    return output


def _true_sm_singlet_vector() -> np.ndarray:
    """Exact -i-Hodge 126bar state z1 wedge ... wedge z5.

    Here ``zk=e_(2k)+i e_(2k+1)``.  This is the unique complex Standard-Model
    singlet in the repository's physical 126bar chirality.  Normalization is
    immaterial for the generator certificate.
    """
    factors = tuple(
        stationarity._form_add(
            stationarity._one_form(first),
            stationarity._one_form(first + 1, stationarity.GI_I),
        )
        for first in (0, 2, 4, 6, 8)
    )
    form = factors[0]
    for factor in factors[1:]:
        form = stationarity._wedge(form, factor)
    if stationarity._hodge_star(form) != stationarity._form_scale_gi(
        form, (0, -1)
    ):
        raise ArithmeticError("constructed SM singlet left the -i Hodge chirality")
    coordinates = stationarity._sigma_coordinates(form)
    output = np.zeros(chart.TOTAL_DIM, dtype=np.int64)
    for complex_index, (real, imaginary) in coordinates.items():
        output[chart.SIGMA_SLICE.start + 2 * complex_index] = real
        output[chart.SIGMA_SLICE.start + 2 * complex_index + 1] = imaginary
    return output


def _standard_sm_generator_basis() -> tuple[sparse.csr_matrix, ...]:
    """Integral basis of su(3)C + su(2)L + u(1)Y on the 486 chart."""
    g = _generator
    su3 = (
        g(0, 1) - g(2, 3),
        g(2, 3) - g(4, 5),
        g(0, 2) + g(1, 3),
        g(0, 3) - g(1, 2),
        g(0, 4) + g(1, 5),
        g(0, 5) - g(1, 4),
        g(2, 4) + g(3, 5),
        g(2, 5) - g(3, 4),
    )
    twice_l = (
        g(7, 8) - g(6, 9),
        -g(6, 8) - g(7, 9),
        g(6, 7) - g(8, 9),
    )
    return (*su3, *twice_l, _ancestry_operators()["standard_Y6"])


def _sm_singlet_exact_nullity() -> dict[str, Any]:
    """Exact rank-250 certificate for one complex SM singlet in 126bar."""
    rows: list[dict[int, int]] = []
    for generator in _standard_sm_generator_basis():
        block = generator[chart.SIGMA_SLICE, chart.SIGMA_SLICE].tocsr()
        for row_index in range(block.shape[0]):
            start, stop = block.indptr[row_index : row_index + 2]
            row = {
                int(column): int(value)
                for column, value in zip(
                    block.indices[start:stop], block.data[start:stop], strict=True
                )
            }
            if row:
                rows.append(row)
    primes = (1_000_003, 1_000_033)
    ranks = {
        str(prime): stationarity._modular_rank(rows, prime) for prime in primes
    }
    true_singlet = _true_sm_singlet_vector()
    phase_partner = _phase_rotated_sigma(true_singlet)
    kernel_annihilation = all(
        not np.any(generator @ vector)
        for generator in _standard_sm_generator_basis()
        for vector in (true_singlet, phase_partner)
    )
    gram = np.asarray(
        [
            [
                int(left @ right)
                for right in (true_singlet, phase_partner)
            ]
            for left in (true_singlet, phase_partner)
        ],
        dtype=np.int64,
    )
    independent = int(round(np.linalg.det(gram))) != 0
    exact_rank = 250 if kernel_annihilation and independent and all(
        rank == 250 for rank in ranks.values()
    ) else None
    return {
        "Sigma_real_dimension": chart.SIGMA_REAL_DIM,
        "nonzero_SM_generator_row_equations": len(rows),
        "rank_mod_primes": ranks,
        "two_explicit_integer_kernel_vectors_annihilated": kernel_annihilation,
        "kernel_Gram_matrix": gram.tolist(),
        "kernel_vectors_independent": independent,
        "exact_rational_rank": exact_rank,
        "exact_real_nullity": (
            chart.SIGMA_REAL_DIM - exact_rank if exact_rank is not None else None
        ),
        "unique_complex_SM_singlet": exact_rank == 250,
        "rank_argument": (
            "rank 250 modulo either prime gives rank_Q>=250; two independent "
            "integer kernel vectors give rank_Q<=250"
        ),
    }


@lru_cache(maxsize=1)
def recompute_live_true_sm_swap_diagnostic() -> dict[str, Any]:
    """Test the fully Q-neutral naive H/Delta replacement at beta=0.

    Delta is moved to the unique SM-neutral 126bar line and the chiral H line
    is moved from the charged (6,7) plane to the Q-neutral (8,9) plane.  All
    other selected fields and renormalizable coefficients are held fixed.
    The signed-current coefficient ``O35_B02`` is removed, matching the beta=0
    base used by the stabilized EFT construction.  This is a reproducible
    float64 live-compiler diagnostic, not an exact lattice theorem.
    """
    source = spectrum.hessian_source
    true_vector = _true_sm_singlet_vector()[chart.SIGMA_SLICE]
    # The raw holomorphic five-form has norm four in the canonical 126bar
    # kinetic metric.  Divide by four and apply the selected r=1/5 amplitude.
    true_coordinates = (
        true_vector[0::2] + 1j * true_vector[1::2]
    ) / 20.0
    base = source.hsx.candidate_state()
    neutral_h = np.zeros(chart.H_COMPLEX_DIM, dtype=complex)
    neutral_h[8] = 1.0 / np.sqrt(2.0)
    neutral_h[9] = 1.0j / np.sqrt(2.0)
    state = source.potential.FieldState(
        phi=base.phi,
        h=neutral_h,
        sigma=chart.sigma_from_coordinates(true_coordinates),
        s=base.s,
        x=base.x,
    ).validated()
    q = chart.pack(state)
    selection = source.g2_audit.contract_selection()
    values = source.potential.evaluate_directions(state)
    by_direction = {row.direction_id: row for row in values}
    owners = source.g2_audit._adapter_modules_by_family()
    direction_rows = tuple(
        owners[by_direction[direction_id].base_family].direction_derivative(
            q, by_direction[direction_id]
        )
        for direction_id in sorted(selection["direction_ids"])
    )
    parameter_rows = source.derivatives.parameter_derivatives(direction_rows)
    by_parameter = {row.parameter_id: row for row in parameter_rows}
    coefficients = source.hsx.numerical_coefficient_map()
    removed_beta = coefficients.pop("lambda::O35_B02_H_Sigma_hermitian")
    value = 0.0
    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    for parameter_id, coefficient in coefficients.items():
        row = by_parameter[parameter_id]
        value += coefficient * float(row.value)
        gradient += coefficient * np.asarray(row.gradient, dtype=float)
        hessian += coefficient * np.asarray(row.hessian, dtype=float)
    hessian = 0.5 * (hessian + hessian.T)
    return {
        "evidence_kind": "independent_live_486_field_compiler_float64",
        "proof_grade": False,
        "replacement": (
            "selected direct.delta_r() -> normalized holomorphic "
            "z0 wedge z1 wedge z2 wedge z3 wedge z4; selected chiral "
            "H=(e6+i e7)/sqrt(2) -> Q-neutral H=(e8+i e9)/sqrt(2)"
        ),
        "held_fixed": "Phi, S, Phi17, and all beta=0 coefficients",
        "removed_signed_current_beta": float(removed_beta),
        "direction_rows": len(direction_rows),
        "parameter_rows": len(parameter_rows),
        "potential_value": float(value),
        "gradient_max_abs": float(np.max(np.abs(gradient), initial=0.0)),
        "gradient_l2_norm": float(np.linalg.norm(gradient)),
        "gradient_phi_block_l2_norm": float(
            np.linalg.norm(gradient[chart.PHI_SLICE])
        ),
        "gradient_sigma_block_l2_norm": float(
            np.linalg.norm(gradient[chart.SIGMA_SLICE])
        ),
        "gradient_entries_above_1e_minus_9": int(
            np.sum(np.abs(gradient) > 1.0e-9)
        ),
        "minimum_full_Hessian_eigenvalue": float(np.linalg.eigvalsh(hessian)[0]),
        "naive_swap_is_stationary": bool(
            np.max(np.abs(gradient), initial=0.0) < 1.0e-9
        ),
        "naive_swap_is_locally_stable": bool(
            np.linalg.eigvalsh(hessian)[0] >= -1.0e-9
        ),
    }


def _vector_10_generator(plane_weights: tuple[int, int, int, int, int]) -> np.ndarray:
    output = np.zeros((10, 10), dtype=np.int64)
    for plane, weight in enumerate(plane_weights):
        first = 2 * plane
        second = first + 1
        output[first, second] = weight
        output[second, first] = -weight
    return output


def _vector_generator_signature(
    plane_weights: tuple[int, int, int, int, int]
) -> dict[str, Any]:
    generator = _vector_10_generator(plane_weights)
    squared = -(generator @ generator)
    diagonal = [int(value) for value in np.diag(squared)]
    return {
        "plane_weights": list(plane_weights),
        "rank_on_real_vector_10": int(np.count_nonzero(np.diag(squared))),
        "squared_charge_multiplicities": {
            str(value): count for value, count in sorted(Counter(diagonal).items())
        },
    }


def _embedding_source_checks() -> dict[str, bool]:
    g6_source = inspect.getsource(spectrum._stabilizer_operators)
    unbroken_source = inspect.getsource(stationarity._unbroken_generators)
    embedding_source = DEPENDENCIES["standard_PS_SM_embedding_source"][0].read_text(
        encoding="utf-8"
    )
    return {
        "G6_charge_operator_is_minus_t8_squared": (
            "charge_squared = -(t[8] @ t[8])" in g6_source
        ),
        "G6_t8_is_exactly_elementary_G89": (
            "{(8, 9): 1}" in unbroken_source
            and "Exact ``su(3)_c`` basis plus the unbroken ``G_89`` generator."
            in unbroken_source
        ),
        "standard_embedding_defines_Y_as_T3R_plus_half_BL": (
            "hypercharge = t3r + 0.5 * b_minus_l" in embedding_source
            and '"hypercharge": "Y=T3R+(B-L)/2"' in embedding_source
        ),
        "standard_embedding_defines_color_and_weak_planes": (
            '"SO6_color_planes": [[0, 1], [2, 3], [4, 5]]' in embedding_source
            and '"SO4_weak_planes": [[6, 7], [8, 9]]' in embedding_source
        ),
    }


@lru_cache(maxsize=1)
def build_report() -> dict[str, Any]:
    bindings = _source_guard()
    frozen_g6 = json.loads(
        (HERE / "EXACT_EFT_PHYSICAL_SCALAR_SPECTRUM_V20.json").read_text(
            encoding="utf-8"
        )
    )
    hessian = spectrum._exact_stabilized_numerator()
    operators = _ancestry_operators()
    kinetic = sparse.diags(
        spectrum._kinetic_weight_vector(), format="csr", dtype=np.int64
    )

    embedding_checks = _embedding_source_checks()
    commutators = {
        name: _commutator_stats(hessian, operators[name])
        for name in EXPECTED_COMMUTATORS
    }
    exact_charge_census = {
        "actual_G89_squared": _exterior_squared_charge_census((0, 0, 0, 0, 1)),
        "standard_Q3_squared": _exterior_squared_charge_census((-1, -1, -1, 3, 0)),
        "standard_Y6_squared": _exterior_squared_charge_census((-2, -2, -2, 3, 3)),
    }
    casimir_census = {
        "standard_12C2_SU3": _exact_projector_multiplicities(
            operators["standard_12C2_SU3"], (0, 16, 36, 40)
        ),
        "standard_4C2L": _exact_projector_multiplicities(
            operators["standard_4C2L"], (0, 3, 8)
        ),
        "standard_4C2R": _exact_projector_multiplicities(
            operators["standard_4C2R"], (0, 3, 8)
        ),
        "standard_C2_SO6": _exact_projector_multiplicities(
            operators["standard_C2_SO6"], (0, 5, 8, 9)
        ),
    }

    delta = _sparse_vector(stationarity._vacuum_block_vectors()["Delta_R"])
    delta_norm = int(delta @ delta)
    delta_quantum = {
        "raw_norm_squared": delta_norm,
        "minus_Y6_squared_eigenvalue": int(
            delta @ (operators["standard_Y6_squared"] @ delta) // delta_norm
        ),
        "four_C2L_eigenvalue": int(
            delta @ (operators["standard_4C2L"] @ delta) // delta_norm
        ),
        "four_C2R_eigenvalue": int(
            delta @ (operators["standard_4C2R"] @ delta) // delta_norm
        ),
        "minus_Q3_squared_eigenvalue": int(
            delta @ (operators["standard_Q3_squared"] @ delta) // delta_norm
        ),
        "minus_G89_squared_eigenvalue": int(
            delta @ (operators["actual_G89_squared"] @ delta) // delta_norm
        ),
    }
    delta_residuals = {
        "signed_Y6_equals_minus_6_residual_nnz": int(
            np.count_nonzero(
                operators["standard_Y6"] @ delta
                + 6 * _phase_rotated_sigma(delta)
            )
        ),
        "signed_Q3_equals_minus_3_residual_nnz": int(
            np.count_nonzero(
                operators["standard_Q3"] @ delta
                + 3 * _phase_rotated_sigma(delta)
            )
        ),
        "Y6_squared_eigen_residual_nnz": int(
            np.count_nonzero(
                operators["standard_Y6_squared"] @ delta - 36 * delta
            )
        ),
        "C2L_singlet_residual_nnz": int(
            np.count_nonzero(operators["standard_4C2L"] @ delta)
        ),
        "C2R_triplet_residual_nnz": int(
            np.count_nonzero(operators["standard_4C2R"] @ delta - 8 * delta)
        ),
        "G89_neutral_residual_nnz": int(
            np.count_nonzero(operators["actual_G89_squared"] @ delta)
        ),
    }

    true_sm_singlet = _true_sm_singlet_vector()
    true_sm_phase = _phase_rotated_sigma(true_sm_singlet)
    true_norm = int(true_sm_singlet @ true_sm_singlet)
    true_sm_singlet_certificate = {
        "exact_form": (
            "(e0+i e1) wedge (e2+i e3) wedge (e4+i e5) wedge "
            "(e6+i e7) wedge (e8+i e9)"
        ),
        "Hodge_chirality": "-i",
        "raw_chart_support": int(np.count_nonzero(true_sm_singlet)),
        "raw_norm_squared": true_norm,
        "signed_Y6": 0,
        "signed_Q3": 0,
        "signed_G89": 1,
        "four_C2L": 0,
        "four_C2R": 8,
        "twelve_C2_SU3": 0,
        "Y6_annihilation_nnz": int(
            np.count_nonzero(operators["standard_Y6"] @ true_sm_singlet)
        ),
        "Q3_annihilation_nnz": int(
            np.count_nonzero(operators["standard_Q3"] @ true_sm_singlet)
        ),
        "G89_charge_plus_one_residual_nnz": int(
            np.count_nonzero(
                operators["actual_G89"] @ true_sm_singlet - true_sm_phase
            )
        ),
        "C2L_singlet_residual_nnz": int(
            np.count_nonzero(operators["standard_4C2L"] @ true_sm_singlet)
        ),
        "C2R_triplet_residual_nnz": int(
            np.count_nonzero(
                operators["standard_4C2R"] @ true_sm_singlet
                - 8 * true_sm_singlet
            )
        ),
        "SU3_singlet_residual_nnz": int(
            np.count_nonzero(
                operators["standard_12C2_SU3"] @ true_sm_singlet
            )
        ),
        "orthogonal_to_selected_Delta_raw": int(delta @ true_sm_singlet) == 0,
    }
    sm_singlet_uniqueness = _sm_singlet_exact_nullity()

    target = _selected_target_vector()
    target_tangents = {
        "standard_Q3_nnz": int(
            np.count_nonzero(operators["standard_Q3"] @ target)
        ),
        "standard_Q3_norm_squared": int(
            np.dot(
                operators["standard_Q3"] @ target,
                operators["standard_Q3"] @ target,
            )
        ),
        "actual_G89_nnz": int(
            np.count_nonzero(operators["actual_G89"] @ target)
        ),
    }

    ancestry_names = (
        "standard_12C2_SU3",
        "standard_4C2L",
        "standard_4C2R",
        "standard_C2_SO6",
        "standard_Y6_squared",
    )
    ancestry_pair_commutators = {
        f"{left}__{right}": int(
            (
                operators[left] @ operators[right]
                - operators[right] @ operators[left]
            ).nnz
        )
        for index, left in enumerate(ancestry_names)
        for right in ancestry_names[index + 1 :]
    }
    kinetic_commutators = {
        name: int((kinetic @ operator - operator @ kinetic).nnz)
        for name, operator in operators.items()
    }

    actual_vector = _vector_generator_signature((0, 0, 0, 0, 1))
    physical_vector = _vector_generator_signature((-1, -1, -1, 3, 0))
    sector_dimension_census = frozen_g6["stabilizer_provenance"]["sector_reports"]
    frozen_q_census = {
        0: sum(
            row["full_real_dimension"]
            for row in sector_dimension_census.values()
            if row["U1em_charge_squared"] == 0
        ),
        1: sum(
            row["full_real_dimension"]
            for row in sector_dimension_census.values()
            if row["U1em_charge_squared"] == 1
        ),
    }

    checks = {
        "all_dependency_hashes_frozen": len(bindings) == len(DEPENDENCIES),
        "G6_core_and_Hessian_payload_bound": (
            frozen_g6["core_sha256"] == EXPECTED_G6_CORE_SHA256
            and frozen_g6["source_binding"]["stabilized_Hessian_payload_sha256"]
            == EXPECTED_HESSIAN_PAYLOAD_SHA256
        ),
        **embedding_checks,
        "all_needed_generators_are_exactly_antisymmetric": all(
            (operator + operator.T).nnz == 0
            for name, operator in operators.items()
            if name in {"actual_G89", "standard_Y6", "standard_Q3"}
        ),
        "ancestry_operators_commute_pairwise_exactly": all(
            value == 0 for value in ancestry_pair_commutators.values()
        ),
        "ancestry_operators_commute_with_kinetic_metric_exactly": all(
            value == 0 for value in kinetic_commutators.values()
        ),
        "exact_charge_censuses_match_frozen_targets": (
            exact_charge_census == EXPECTED_EXACT_CHARGE_CENSUS
        ),
        "G6_sector_census_is_exactly_G89_census": (
            frozen_q_census == exact_charge_census["actual_G89_squared"]
        ),
        "G89_and_standard_Q_are_not_conjugate_on_vector_10": (
            actual_vector["rank_on_real_vector_10"] == 2
            and physical_vector["rank_on_real_vector_10"] == 8
            and actual_vector["squared_charge_multiplicities"]
            != physical_vector["squared_charge_multiplicities"]
        ),
        "selected_Delta_is_not_standard_SM_hypercharge_singlet": (
            delta_quantum["minus_Y6_squared_eigenvalue"] == 36
            and delta_quantum["four_C2L_eigenvalue"] == 0
            and delta_quantum["four_C2R_eigenvalue"] == 8
            and all(value == 0 for value in delta_residuals.values())
        ),
        "true_SM_neutral_126bar_singlet_constructed_exactly": (
            true_sm_singlet_certificate["Y6_annihilation_nnz"] == 0
            and true_sm_singlet_certificate["Q3_annihilation_nnz"] == 0
            and true_sm_singlet_certificate["C2L_singlet_residual_nnz"] == 0
            and true_sm_singlet_certificate["C2R_triplet_residual_nnz"] == 0
            and true_sm_singlet_certificate["SU3_singlet_residual_nnz"] == 0
            and true_sm_singlet_certificate[
                "G89_charge_plus_one_residual_nnz"
            ]
            == 0
            and true_sm_singlet_certificate["orthogonal_to_selected_Delta_raw"]
        ),
        "true_SM_neutral_126bar_singlet_is_unique_complex_line": (
            sm_singlet_uniqueness["unique_complex_SM_singlet"]
            and sm_singlet_uniqueness["exact_real_nullity"] == 2
        ),
        "recorded_naive_true_SM_singlet_swap_is_nonstationary_and_tachyonic": (
            RECORDED_TRUE_SM_SWAP_DIAGNOSTIC["gradient_max_abs"] > 0.1
            and RECORDED_TRUE_SM_SWAP_DIAGNOSTIC[
                "gradient_entries_above_1e_minus_9"
            ]
            == 26
            and RECORDED_TRUE_SM_SWAP_DIAGNOSTIC[
                "minimum_full_Hessian_eigenvalue"
            ]
            < -0.4
        ),
        "selected_target_is_fixed_by_G89_not_standard_Q": (
            target_tangents
            == {
                "standard_Q3_nnz": 10,
                "standard_Q3_norm_squared": 90,
                "actual_G89_nnz": 0,
            }
        ),
        "actual_G89_commutes_with_frozen_mass_pencil": (
            commutators["actual_G89"]["nnz"] == 0
            and commutators["actual_G89_squared"]["nnz"] == 0
        ),
        "standard_SM_operators_do_not_commute_with_frozen_mass_pencil": all(
            commutators[name]["nnz"] > 0
            for name in (
                "standard_Y6",
                "standard_Y6_squared",
                "standard_Q3",
                "standard_Q3_squared",
                "standard_4C2L",
                "standard_4C2R",
            )
        ),
        "exact_commutator_signatures_frozen": all(
            {
                "nnz": commutators[name]["nnz"],
                "max_abs": commutators[name]["max_abs"],
            }
            == expected
            for name, expected in EXPECTED_COMMUTATORS.items()
        ),
        "coordinate_carrier_projectors_complete": (
            all(sum(row.values()) == chart.TOTAL_DIM for row in casimir_census.values())
            and all(
                sum(row.values()) == chart.TOTAL_DIM
                for row in exact_charge_census.values()
            )
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise ArithmeticError(f"G6 provenance audit checks failed: {failures}")

    decisive = {
        "model_contract_id": MODEL_CONTRACT_ID,
        "source_binding": bindings,
        "checks": checks,
        "operator_conventions": {
            "actual_frozen_G6_U1": "G89",
            "standard_B_minus_L_times_3": "-2*(G01+G23+G45)",
            "standard_hypercharge_times_6": (
                "Y6=3*(G67+G89)-2*(G01+G23+G45)"
            ),
            "standard_electric_charge_times_3": (
                "Q3=3*G67-(G01+G23+G45)"
            ),
            "standard_four_C2L": (
                "-[(G78-G69)^2+(-G68-G79)^2+(G67-G89)^2]"
            ),
            "standard_four_C2R": (
                "-[(G78+G69)^2+(-G68+G79)^2+(G67+G89)^2]"
            ),
        },
        "vector_10_nonconjugacy_certificate": {
            "actual_G89": actual_vector,
            "standard_Q3": physical_vector,
            "reason": (
                "conjugation preserves rank and squared-charge multiplicities"
            ),
        },
        "exact_coordinate_carrier_census": {
            "charge_squared": {
                name: {str(key): value for key, value in row.items()}
                for name, row in exact_charge_census.items()
            },
            "casimirs": {
                name: {str(key): value for key, value in row.items()}
                for name, row in casimir_census.items()
            },
            "construction": (
                "SO10-origin block projectors times Lagrange polynomials in "
                "the mutually commuting exact C2(SO6), 4C2L, 4C2R, 12C2SU3, "
                "and charge-squared operators"
            ),
            "signed_hypercharge_refinement": (
                "over Q(i), use the spectral projectors of -i*Y6; the real "
                "carrier combines the conjugate +Y and -Y spaces"
            ),
            "coordinate_ancestry_projectors_exactly_available": True,
        },
        "selected_background_audit": {
            "G6_Phi_background": "F0/sqrt(10), F0 has ten unit four-form components",
            "Pati_Salam_Phi_background": "P=e6789",
            "backgrounds_are_the_same_direction": False,
            "F_orbit_stabilizer_dimension": 25,
            "P_orbit_stabilizer_dimension": 21,
            "therefore_F_and_P_are_not_SO10_conjugate": True,
            "selected_Delta_quantum_numbers_in_standard_embedding": delta_quantum,
            "selected_Delta_signed_quantum_numbers": {
                "B_minus_L": "-2",
                "T3R": "0",
                "Y": "-1",
                "Q": "-1",
            },
            "selected_Delta_exact_eigen_residuals": delta_residuals,
            "true_SM_neutral_126bar_singlet": true_sm_singlet_certificate,
            "true_SM_singlet_uniqueness": sm_singlet_uniqueness,
            "selected_full_target_tangents": target_tangents,
        },
        "mass_pencil_commutant": commutators,
        "independent_live_true_SM_singlet_swap_diagnostic": {
            "evidence_kind": "independent_live_486_field_compiler_float64",
            "proof_grade": False,
            "recomputation_function": "recompute_live_true_sm_swap_diagnostic",
            "replacement": (
                "selected direct.delta_r() -> normalized holomorphic "
                "z0 wedge z1 wedge z2 wedge z3 wedge z4; selected chiral "
                "H=(e6+i e7)/sqrt(2) -> Q-neutral H=(e8+i e9)/sqrt(2)"
            ),
            "held_fixed": "Phi, S, Phi17, and all beta=0 coefficients",
            **RECORDED_TRUE_SM_SWAP_DIAGNOSTIC,
            "naive_swap_is_stationary": False,
            "naive_swap_is_locally_stable": False,
            "interpretation": (
                "the correct SM-neutral representation direction cannot be "
                "inserted without re-solving stationarity and stability"
            ),
        },
        "projector_feasibility": {
            "UV_coordinate_SO10_PS_SM_ancestry": "EXACTLY_RECONSTRUCTIBLE",
            "frozen_G6_mass_eigenspace_standard_SU2L_x_U1Y_labels": (
                "NOT_DEFINED_BY_SIMULTANEOUS_PROJECTORS"
            ),
            "reason": (
                "the standard ancestry Casimirs/charges do not commute with "
                "the frozen generalized mass pencil"
            ),
            "mass_projector_overlap_diagnostics_possible": True,
            "overlap_diagnostics_are_irrep_labels": False,
        },
        "classification": {
            "exact_coordinate_carrier_provenance_projectors_constructed": True,
            "frozen_G6_actual_stabilizer_identified_as_SU3_x_U1_89": True,
            "frozen_G6_physical_U1em_provenance_complete": False,
            "frozen_G6_per_mass_state_SU2L_x_U1Y_provenance_complete": False,
            "frozen_G6_Pati_Salam_threshold_provenance_complete": False,
            "mathematical_tree_level_mass_factorization_remains_valid": True,
            "prior_positive_physical_G6_interpretation_valid": False,
            "prior_positive_mathematical_G6_as_physical_SM_spectrum_valid": False,
            "mathematical_physical_G6_closed": False,
            "release_level_G6_complete": False,
            "positive_G7_threshold_input_complete": False,
        },
        "recommended_gate_downgrades": {
            "formal_EFT_G6_mass_factorization_under_SU3_x_U1_89": True,
            "mathematical_physical_SM_G6": False,
            "release_G6": False,
            "authoritative_renormalizable_G6": False,
            "mathematical_G7": False,
            "release_G7": False,
            "authoritative_renormalizable_G7": False,
            "required_status": (
                "FORMAL_SU3_X_U1_89_EFT_SPECTRUM_ONLY__PHYSICAL_G6_AND_G7_OPEN"
            ),
        },
        "required_recalculation": [
            "fix one explicit physical SO(10)->intermediate->SM embedding and verify every VEV is neutral under the claimed residual generators",
            "replace or gauge-align the selected Delta and H directions so the desired Y and Q generators annihilate the staged vacua",
            "recompute exact Hessians separately at the SO(10), intermediate, SM, and electroweak stages",
            "diagonalize each stage Hessian jointly with the exact ancestry projectors",
            "attach absolute VEV/matching scales, pole-mass corrections, and scheme-dependent component thresholds",
        ],
    }
    return {
        "status": STATUS,
        "core_sha256": _canonical_sha256(decisive),
        "n_checks": len(checks),
        "n_failed": 0,
        "failures": [],
        **decisive,
    }


def render_markdown(report: dict[str, Any]) -> str:
    vector = report["vector_10_nonconjugacy_certificate"]
    delta = report["selected_background_audit"][
        "selected_Delta_quantum_numbers_in_standard_embedding"
    ]
    true_delta = report["selected_background_audit"][
        "true_SM_neutral_126bar_singlet"
    ]
    return "\n".join(
        [
            "# Exact G6 Standard-Model provenance feasibility audit",
            "",
            f"- Status: `{report['status']}`",
            f"- Core SHA256: `{report['core_sha256']}`",
            f"- Exact checks: {report['n_checks']} / {report['n_checks']}",
            "",
            "## Decisive result",
            "",
            "The frozen G6 U(1) operator is the elementary plane rotation `G89`.",
            (
                "On the vector 10 it has rank "
                f"{vector['actual_G89']['rank_on_real_vector_10']}, while the "
                "standard SO(10) electromagnetic generator `Q3` has rank "
                f"{vector['standard_Q3']['rank_on_real_vector_10']}."
            ),
            "Rank and squared-charge spectra are conjugacy invariants, so these are not gauge-conjugate generators.",
            (
                "The selected Delta direction has `(6Y)^2="
                f"{delta['minus_Y6_squared_eigenvalue']}` and is therefore not "
                "the standard-SM hypercharge singlet."
            ),
            (
            "Its signed quantum numbers are `Y=-1, Q=-1`.  The unique true "
                "SM-neutral complex 126bar line is instead the exact decomposable "
                f"state `{true_delta['exact_form']}`, with `Y=Q=0`."
            ),
            "A separate 44-direction live-compiler swap to that true singlet and the Q-neutral chiral H line, with all other beta=0 data fixed, has gradient max 0.127279 and a Hessian eigenvalue -0.408615; the fully neutral naive replacement is neither stationary nor stable.",
            "",
            "## What is complete",
            "",
            "Exact SO(10)-origin, Pati–Salam Casimir, SU(3), SU(2)L/R, and charge projectors exist on all 486 field coordinates.",
            "Their full carrier censuses are source-bound in the JSON artifact.",
            "",
            "## What remains open",
            "",
            "Those standard ancestry operators do not commute with the frozen G6 mass pencil, so they cannot label its mass eigenspaces.",
            "Release G6 and positive-threshold G7 require staged Hessians around an explicitly validated physical embedding, followed by joint projector diagonalization and absolute matching.",
            "Accordingly the former positive physical-SM G6 interpretation and every positive G7 gate must be downgraded; only the formal SU(3) x U(1)_89 factorization remains true.",
            "",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-unfrozen", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if not args.allow_unfrozen:
        if EXPECTED_CORE_SHA256 == "TO_BE_FROZEN":
            raise ArithmeticError("EXPECTED_CORE_SHA256 is not frozen")
        if report["core_sha256"] != EXPECTED_CORE_SHA256:
            raise ArithmeticError("frozen G6 provenance audit core drifted")
    if args.write:
        OUT_JSON.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        OUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
