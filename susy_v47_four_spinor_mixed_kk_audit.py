#!/usr/bin/env python3
"""V47 four-spinor transfer-matrix and exact zero-mode audit.

This enlarges the factorized V46 problem to HLF, HLA, HRA and HRF and to
the two source operators selected by the SU(5)-singlet 126 VEVs:

    barSigma HLF HRA,      Sigma HLA HRF.

The exact calculation is stated in terms of a finite renormalized boundary
extension matrix B.  It does not identify a bare endpoint delta coefficient
with B without a declared thin-brane prescription.
"""

from __future__ import annotations

import argparse
import cmath
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import susy_v46_spinor_kk_determinant_audit as v46


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V47_FOUR_SPINOR_MIXED_KK_AUDIT.json"
MD_PATH = ROOT / "SUSY_V47_FOUR_SPINOR_MIXED_KK_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v47_four_spinor_mixed_kk_audit.py"

STATUS = (
    "V47_FOUR_SPINOR_TRANSFER_CHARACTERISTIC_DERIVED__"
    "ZERO_NULLITY_CONTROLLED_ONLY_BY_SOURCE_EVEN_EVEN_BLOCK__"
    "THETA_PLUS_AND_MINUS_REMOVE_ALL_ZERO_MODES_WHILE_SIGMA_CROSS_BLOCKS_ONLY_SHIFT_TOWERS__"
    "HERMITIAN_EXTENSION_HAS_NO_TACHYONS__"
    "REGULATOR_THRESHOLDS_AND_GLOBAL_GATES_OPEN"
)

CHANNELS = ("HLF=16_+1", "HLA=bar16_-4", "HRA=16_-1", "HRF=bar16_+4")

PRIMITIVE_U1F = {
    "HLF": 1,
    "HLA": -4,
    "HRA": -1,
    "HRF": 4,
    "ThetaPlus": 3,
    "ThetaMinus": -3,
    "Sigma": 0,
    "barSigma": 0,
}

# A component ordering compatible with the PS split 8+8.  The final entry is
# the SU(5) singlet 1_-5 (or its conjugate in a bar16).  Sigma's singlet VEV
# acts only on this final entry.
INTERNAL_COMPONENTS = (
    "Q_r_up",
    "Q_r_down",
    "Q_g_up",
    "Q_g_down",
    "Q_b_up",
    "Q_b_down",
    "L_neutral",
    "L_charged",
    "uC_r",
    "uC_g",
    "uC_b",
    "dC_r",
    "dC_g",
    "dC_b",
    "eC",
    "nuC_SU5_singlet",
)
P_LEFT = tuple(1 if index < 8 else 0 for index in range(16))
P_RIGHT = tuple(1 - value for value in P_LEFT)
P_SU5_SINGLET = tuple(1 if index == 15 else 0 for index in range(16))

E_LEFT = (True, True, False, False)
E_RIGHT = (False, False, True, True)

UPSTREAM_INPUTS = (
    ROOT / "SUSY_V45_NEW_PHYSICS_MASTER_AUDIT.json",
    ROOT / "SUSY_V46_MICROSCOPIC_KILL_TEST_AUDIT.json",
    ROOT / "SUSY_V47_SOURCE_COMPLETION_ROUTE_AUDIT.json",
)

PRIMARY_SOURCES = (
    {
        "url": "https://arxiv.org/abs/hep-th/0106256",
        "use": "5D N=1 hypermultiplet first-order superfield operator",
    },
    {
        "url": "https://arxiv.org/abs/hep-ph/0112230",
        "use": "orbifold superspace and brane-localized operators",
    },
    {
        "url": "https://arxiv.org/abs/hep-ph/0508153",
        "use": "explicit SU(5) decomposition of 16x16xbar126 and conjugate SO(10) couplings",
    },
    {
        "url": "https://arxiv.org/abs/hep-ph/0603086",
        "use": "5D SO(10) interval, Pati--Salam parities and boundary-shifted KK towers",
    },
    {
        "url": "https://arxiv.org/abs/1408.1852",
        "use": "thin-brane and infinite-KK limits need an explicit regularization prescription",
    },
)


Matrix = list[list[complex]]


def zero_matrix(size: int) -> Matrix:
    return [[0.0j for _ in range(size)] for _ in range(size)]


def determinant(matrix: Sequence[Sequence[complex]], tolerance: float = 1.0e-14) -> complex:
    """Complex determinant by pivoted elimination."""

    size = len(matrix)
    if any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a square matrix")
    work = [[complex(value) for value in row] for row in matrix]
    result = 1.0 + 0.0j
    sign = 1
    for column in range(size):
        pivot = max(range(column, size), key=lambda row: abs(work[row][column]))
        if abs(work[pivot][column]) <= tolerance:
            return 0.0j
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            for inner in range(column + 1, size):
                work[row][inner] -= factor * work[column][inner]
    return sign * result


def matrix_rank(matrix: Sequence[Sequence[complex]], tolerance: float = 1.0e-11) -> int:
    if not matrix:
        return 0
    rows = len(matrix)
    columns = len(matrix[0])
    work = [[complex(value) for value in row] for row in matrix]
    scale = max(1.0, max(abs(value) for row in work for value in row))
    threshold = tolerance * scale
    rank = 0
    for column in range(columns):
        pivot = max(range(rank, rows), key=lambda row: abs(work[row][column]), default=rank)
        if rank >= rows or abs(work[pivot][column]) <= threshold:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        for row in range(rows):
            if row == rank:
                continue
            factor = work[row][column] / pivot_value
            for inner in range(column, columns):
                work[row][inner] -= factor * work[rank][inner]
        rank += 1
        if rank == rows:
            break
    return rank


def conjugate_transpose(matrix: Sequence[Sequence[complex]]) -> Matrix:
    return [
        [complex(matrix[column][row]).conjugate() for column in range(len(matrix))]
        for row in range(len(matrix[0]))
    ]


def is_hermitian(matrix: Sequence[Sequence[complex]], tolerance: float = 1.0e-12) -> bool:
    adjoint = conjugate_transpose(matrix)
    return all(
        abs(complex(matrix[row][column]) - adjoint[row][column]) <= tolerance
        for row in range(len(matrix))
        for column in range(len(matrix))
    )


def nambu_lift(holomorphic_mass: Sequence[Sequence[complex]]) -> Matrix:
    """Hermitian lift [[0,mu^dagger],[mu,0]] of a complex mass matrix."""

    size = len(holomorphic_mass)
    if any(len(row) != size for row in holomorphic_mass):
        raise ValueError("holomorphic mass must be square")
    result = zero_matrix(2 * size)
    adjoint = conjugate_transpose(holomorphic_mass)
    for row in range(size):
        for column in range(size):
            result[row][size + column] = adjoint[row][column]
            result[size + row][column] = complex(holomorphic_mass[row][column])
    return result


def holomorphic_zero_nullity(
    holomorphic_mass: Sequence[Sequence[complex]], even: Sequence[bool]
) -> int:
    """Complex-chiral nullity of the even-even holomorphic mass block."""

    indices = [index for index, value in enumerate(even) if value]
    block = [
        [complex(holomorphic_mass[row][column]) for column in indices] for row in indices
    ]
    return len(indices) - matrix_rank(block)


def theta_sigma_boundary_matrix(
    theta_left: complex,
    theta_right: complex,
    sigma_16: complex = 0.0,
    sigma_bar16: complex = 0.0,
    *,
    su5_singlet: bool,
) -> Matrix:
    """Hermitian extension matrix in channel order HLF,HLA,HRA,HRF.

    ``sigma_16`` is induced by <barSigma> HLF HRA and ``sigma_bar16``
    by <Sigma> HLA HRF.  They are projected away unless the internal
    component is the SU(5) singlet.
    """

    matrix = zero_matrix(4)

    def edge(first: int, second: int, value: complex) -> None:
        matrix[first][second] = complex(value)
        matrix[second][first] = complex(value).conjugate()

    edge(0, 1, theta_left)
    edge(2, 3, theta_right)
    if su5_singlet:
        edge(0, 2, sigma_16)
        edge(1, 3, sigma_bar16)
    return matrix


def even_even_block(boundary: Sequence[Sequence[complex]], even: Sequence[bool]) -> Matrix:
    indices = [index for index, value in enumerate(even) if value]
    return [[complex(boundary[row][column]) for column in indices] for row in indices]


def zero_mode_nullity(boundary: Sequence[Sequence[complex]], even: Sequence[bool]) -> int:
    """Exact complex chiral zero-mode nullity for finite kink masses."""

    block = even_even_block(boundary, even)
    return len(block) - matrix_rank(block)


def _real_z_from_mass(mass: complex) -> float:
    value = complex(mass) * complex(mass)
    if abs(value.imag) > 1.0e-12 * max(1.0, abs(value.real)):
        raise ValueError("this executable evaluates the real and imaginary mass axes only")
    return float(value.real)


def transfer_blocks(
    mass: complex, bulk_masses: Sequence[float], length: float
) -> tuple[list[float], list[float], list[float]]:
    z = _real_z_from_mass(mass)
    s_values = [v46.s_function(z, item, length) for item in bulk_masses]
    f_values = [v46.f_function(z, item, length) for item in bulk_masses]
    g_values = [v46.g_function(z, item, length) for item in bulk_masses]
    return s_values, f_values, g_values


def characteristic_matrix(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    boundary: Sequence[Sequence[complex]],
    even: Sequence[bool],
) -> Matrix:
    """K(m)=(-m S+B F)E+(G+m B S)O."""

    size = len(bulk_masses)
    if len(boundary) != size or len(even) != size:
        raise ValueError("channel dimensions do not agree")
    s_values, f_values, g_values = transfer_blocks(mass, bulk_masses, length)
    result = zero_matrix(size)
    for column in range(size):
        for row in range(size):
            if even[column]:
                result[row][column] = boundary[row][column] * f_values[column]
                if row == column:
                    result[row][column] -= mass * s_values[column]
            else:
                if row == column:
                    result[row][column] = g_values[column]
                result[row][column] += mass * boundary[row][column] * s_values[column]
    return result


def signed_characteristic(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    boundary: Sequence[Sequence[complex]],
    even: Sequence[bool],
) -> complex:
    return determinant(characteristic_matrix(mass, bulk_masses, length, boundary, even))


def mass_squared_characteristic(
    z: float,
    bulk_masses: Sequence[float],
    length: float,
    boundary: Sequence[Sequence[complex]],
    even: Sequence[bool],
) -> complex:
    """Entire squared-spectrum characteristic C(sqrt(z)) C(-sqrt(z))."""

    mass = math.sqrt(z) if z >= 0.0 else 1j * math.sqrt(-z)
    return signed_characteristic(mass, bulk_masses, length, boundary, even) * signed_characteristic(
        -mass, bulk_masses, length, boundary, even
    )


def zero_factorization(
    bulk_masses: Sequence[float],
    length: float,
    boundary: Sequence[Sequence[complex]],
    even: Sequence[bool],
) -> dict[str, complex]:
    """Return det K(0) and its block-triangular factorization."""

    odd_indices = [index for index, value in enumerate(even) if not value]
    even_indices = [index for index, value in enumerate(even) if value]
    g_odd = math.prod(math.exp(bulk_masses[index] * length) for index in odd_indices)
    f_even = math.prod(math.exp(-bulk_masses[index] * length) for index in even_indices)
    block_det = determinant(even_even_block(boundary, even))
    direct = signed_characteristic(0.0, bulk_masses, length, boundary, even)
    return {
        "direct": direct,
        "factorized": g_odd * block_det * f_even,
        "det_G_odd_0": complex(g_odd),
        "det_B_even_even": block_det,
        "det_F_even_0": complex(f_even),
    }


def full_zero_count(theta_left: complex, theta_right: complex) -> dict[str, int]:
    boundary = theta_sigma_boundary_matrix(
        theta_left, theta_right, 2.3, -1.7, su5_singlet=True
    )
    left_nullity = zero_mode_nullity(boundary, E_LEFT)
    right_nullity = zero_mode_nullity(boundary, E_RIGHT)
    return {
        "left_component_nullity": left_nullity,
        "right_non_singlet_component_nullity": right_nullity,
        "right_SU5_singlet_component_nullity": right_nullity,
        "total_chiral_component_zero_modes": 8 * left_nullity + 7 * right_nullity + right_nullity,
    }


def _bisect(function: Callable[[float], float], low: float, high: float) -> float:
    f_low = function(low)
    f_high = function(high)
    if f_low == 0.0:
        return low
    if f_high == 0.0:
        return high
    if f_low * f_high > 0.0:
        raise ValueError("interval does not bracket a root")
    for _ in range(100):
        mid = (low + high) / 2.0
        value = function(mid)
        if value == 0.0 or high - low < 1.0e-13 * max(1.0, abs(mid)):
            return mid
        if f_low * value < 0.0:
            high = mid
        else:
            low = mid
            f_low = value
    return (low + high) / 2.0


def first_absolute_signed_root(
    function: Callable[[float], complex], maximum_mass: float, steps: int = 100000
) -> float:
    roots: list[float] = []
    for direction in (1.0, -1.0):
        previous_x = 0.0
        previous = float(function(0.0).real)
        for step in range(1, steps + 1):
            x = maximum_mass * step / steps
            value_complex = function(direction * x)
            if abs(value_complex.imag) > 1.0e-9 * max(1.0, abs(value_complex.real)):
                raise ValueError("root scan requires a real characteristic")
            value = float(value_complex.real)
            if value == 0.0:
                roots.append(x)
                break
            if previous * value < 0.0:
                root = _bisect(lambda trial: float(function(direction * trial).real), previous_x, x)
                roots.append(root)
                break
            previous_x = x
            previous = value
    if not roots:
        raise RuntimeError("no signed root found")
    return min(roots)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    payload.pop("core_sha256", None)
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _clean_number(value: complex | float, digits: int = 14) -> float | list[float]:
    item = complex(value)
    if abs(item.imag) <= 1.0e-12 * max(1.0, abs(item.real)):
        return round(item.real, digits)
    return [round(item.real, digits), round(item.imag, digits)]


def build_report() -> dict[str, Any]:
    masses = (0.35, -0.2, 0.55, -0.1)
    length = 1.0
    theta_left = 0.4
    theta_right = 0.6
    sigma_16 = 12.0
    sigma_bar16 = 9.0

    boundary_plain = theta_sigma_boundary_matrix(
        theta_left, theta_right, 0.0, 0.0, su5_singlet=False
    )
    boundary_singlet = theta_sigma_boundary_matrix(
        theta_left, theta_right, sigma_16, sigma_bar16, su5_singlet=True
    )
    left_zero = zero_factorization(masses, length, boundary_plain, E_LEFT)
    right_zero = zero_factorization(masses, length, boundary_singlet, E_RIGHT)

    flat_masses = (0.0, 0.0, 0.0, 0.0)
    weak_sigma = theta_sigma_boundary_matrix(
        theta_left, theta_right, 0.0, 0.0, su5_singlet=True
    )
    strong_sigma = theta_sigma_boundary_matrix(
        theta_left, theta_right, sigma_16, sigma_bar16, su5_singlet=True
    )
    weak_root = first_absolute_signed_root(
        lambda trial: signed_characteristic(trial, flat_masses, 1.0, weak_sigma, E_RIGHT),
        2.0,
    )
    strong_root = first_absolute_signed_root(
        lambda trial: signed_characteristic(trial, flat_masses, 1.0, strong_sigma, E_RIGHT),
        2.0,
    )

    tuned_sigma = theta_sigma_boundary_matrix(
        theta_left,
        theta_right,
        0.8,
        theta_left * theta_right / 0.8,
        su5_singlet=True,
    )
    complex_mu = [[0.0j, 0.7 + 0.2j], [0.7 + 0.2j, 0.0j]]
    complex_nambu = nambu_lift(complex_mu)

    counts_both = full_zero_count(theta_left, theta_right)
    counts_no_left = full_zero_count(0.0, theta_right)
    counts_no_right = full_zero_count(theta_left, 0.0)
    counts_neither = full_zero_count(0.0, 0.0)

    report: dict[str, Any] = {
        "schema": "susy-v47-four-spinor-mixed-kk-audit-v1",
        "status": STATUS,
        "field_and_component_contract": {
            "channel_order": list(CHANNELS),
            "primitive_U1F_charges": dict(PRIMITIVE_U1F),
            "U1F_operator_charge_sums": {
                "ThetaPlus_HLF_HLA": PRIMITIVE_U1F["ThetaPlus"]
                + PRIMITIVE_U1F["HLF"]
                + PRIMITIVE_U1F["HLA"],
                "ThetaMinus_HRA_HRF": PRIMITIVE_U1F["ThetaMinus"]
                + PRIMITIVE_U1F["HRA"]
                + PRIMITIVE_U1F["HRF"],
                "barSigma_HLF_HRA": PRIMITIVE_U1F["barSigma"]
                + PRIMITIVE_U1F["HLF"]
                + PRIMITIVE_U1F["HRA"],
                "Sigma_HLA_HRF": PRIMITIVE_U1F["Sigma"]
                + PRIMITIVE_U1F["HLA"]
                + PRIMITIVE_U1F["HRF"],
            },
            "internal_component_order": list(INTERNAL_COMPONENTS),
            "P_PS_left": list(P_LEFT),
            "P_PS_right": list(P_RIGHT),
            "P_SU5_singlet": list(P_SU5_SINGLET),
            "projector_relations": {
                "P_left_plus_P_right_is_identity": all(
                    left + right == 1 for left, right in zip(P_LEFT, P_RIGHT)
                ),
                "P_singlet_is_subprojector_of_P_right": all(
                    singlet <= right for singlet, right in zip(P_SU5_SINGLET, P_RIGHT)
                ),
                "rank_P_left": sum(P_LEFT),
                "rank_P_right": sum(P_RIGHT),
                "rank_P_SU5_singlet": sum(P_SU5_SINGLET),
            },
            "parity_by_component": {
                "PS_left_8": {"E_at_y0": [1, 1, 0, 0], "multiplicity": 8},
                "PS_right_non_singlet_7": {"E_at_y0": [0, 0, 1, 1], "multiplicity": 7},
                "PS_right_SU5_singlet_1": {"E_at_y0": [0, 0, 1, 1], "multiplicity": 1},
            },
            "Sigma_projector_statement": "the SU5-singlet barSigma/Sigma VEV couples only nuC_SU5_singlet and its conjugate; it is zero on the other 15 spinor components",
            "SU5_decomposition": "16=10_(chi=-1)+bar5_(chi=+3)+1_(chi=-5); these are U1_chi labels, not U1F charges; the chi=-5 singlet is the right-handed-neutrino component inside the PS-right half",
        },
        "renormalized_source_boundary_matrix": {
            "basis": "(HLF,HLA,HRA,HRF)",
            "B_component": [
                ["0", "t_L", "s_16 P_1", "0"],
                ["t_L*", "0", "0", "s_bar16 P_bar1"],
                ["s_16* P_1", "0", "0", "t_R"],
                ["0", "s_bar16* P_bar1", "t_R*", "0"],
            ],
            "parameters": {
                "t_L": "B_R(lambda_L <ThetaPlus>)",
                "t_R": "B_R(lambda_R <ThetaMinus>)",
                "s_16": "B_R(lambda_barSigma <barSigma>_SU5-singlet)",
                "s_bar16": "B_R(lambda_Sigma <Sigma>_SU5-singlet)",
            },
            "real_singlet_boundary_determinant": "det B_1=(t_L t_R-s_16 s_bar16)^2",
            "complex_singlet_boundary_determinant": "det B_1=|t_L t_R* - s_16 s_bar16*|^2 in the Hermitian extension convention",
            "warning": "rank(B) is not the zero-mode criterion when y0 parities are mixed",
        },
        "general_transfer_theorem": {
            "bulk_state": "Psi=(f,g)^T",
            "bulk_equations": [
                "(partial_y+M)f=m g",
                "(-partial_y+M)g=m f",
            ],
            "one_channel_transfer": "T_i(m)=[[F_i,m S_i],[-m S_i,G_i]]",
            "initial_parity_data": "f(0)=E a and g(0)=O a, with O=1-E",
            "source_condition": "g(L)+B f(L)=0",
            "characteristic_matrix": "K(m)=(-m S+B F)E+(G+m B S)O",
            "signed_characteristic": "C(m)=det K(m)",
            "mass_squared_characteristic": "D(z)=C(sqrt(z)) C(-sqrt(z)), entire in z",
            "full_four_spinor_characteristic": "C_full(m)=C_left(m)^8 C_right_non_singlet(m)^7 C_right_singlet(m)",
            "no_division_warning": "K is valid at m=0 and k_i=0; do not divide by m, S_i, F_i or G_i",
        },
        "exact_zero_mode_theorem": {
            "zero_matrix": "K(0)=B F(0)E+G(0)O",
            "block_factorization": "det K(0)=det G_O(0) det(B_EE) det F_E(0)",
            "criterion": "ker K(0) is isomorphic to ker(B_EE), where B_EE=E B E restricted to im(E)",
            "nullity": "n_zero_chiral=n_even-rank(B_EE)",
            "odd_solution": "a_O=-G_O(0)^-1 O B E F_E(0) a_E",
            "meaning": "even-odd and odd-odd source blocks change the zero-mode wavefunction but cannot lift it",
            "finite_localization": "F_E(0) and G_O(0) are diagonal exponentials and never singular for finite real M_i,L",
            "complex_superpotential": "for arbitrary complex symmetric mu, use the Hermitian Nambu lift B_N=[[0,mu^dagger],[mu,0]]; the complex chiral criterion reduces to ker(mu_EE)",
        },
        "V46_Theta_Sigma_zero_count": {
            "B_EE_left_components": "[[0,t_L],[t_L*,0]] on HLF,HLA",
            "B_EE_right_components": "[[0,t_R],[t_R*,0]] on HRA,HRF",
            "Sigma_location": "only E-O entries HLF-HRA and HLA-HRF in the one SU5-singlet component",
            "both_Theta_nonzero": counts_both,
            "t_L_zero": counts_no_left,
            "t_R_zero": counts_no_right,
            "both_Theta_zero": counts_neither,
            "conclusion": "t_L and t_R nonzero give zero exact KK zero modes for arbitrary finite Sigma entries; Sigma cannot replace either Theta block",
            "boundary_rank_counterexamples": [
                "det B_1 can vanish at t_L t_R=s_16 s_bar16 while B_EE remains full rank and there is no zero mode",
                "with t_R=0 and nonzero s_16,s_bar16, B_1 can be full rank while B_EE is zero and two right-component chiral zero modes remain",
            ],
        },
        "self_adjointness_and_stability": {
            "boundary_form": "[-f_psi^dagger g_phi+g_psi^dagger f_phi]_0^L",
            "PS_parity_is_isotropic": True,
            "source_condition_is_self_adjoint_iff": "B=B^dagger (or the equivalent Hermitian Nambu lift for complex holomorphic masses)",
            "consequence": "the first-order KK operator has real signed eigenvalues; unbroken 4D N=1 multiplets have m_scalar^2=m_fermion^2>=0",
            "tachyonic_or_complex_roots": 0,
            "outside_certificate": [
                "non-Hermitian matching used without Nambu completion",
                "negative-norm boundary kinetic terms",
                "SUSY-breaking scalar-only boundary masses",
                "energy-dependent boundary kernels with unaccounted boundary states",
            ],
        },
        "regulated_spectral_determinant": {
            "nonzero_case": "P_B(z)=C(sqrt(z))C(-sqrt(z))/C(0)^2=product_a(1-z/m_a^2)",
            "zero_removed_case": "if C(m)=c_q m^q+..., divide C(sqrt(z))C(-sqrt(z)) by (-1)^q c_q^2 z^q",
            "boundary_row_normalization": "use (I+B^2)^(-1/2)[g+Bf]=0 for Hermitian B; the squared characteristic receives det(I+B^2)^(-1)",
            "same_domain_invariance": "P_B is unchanged by nonsingular rescaling of boundary equations",
            "cross_domain_warning": "absolute and cross-B determinant constants require a brane regulator and boundary counterterm scheme",
        },
        "strong_coupling_caveats": {
            "uniform_invertible_B_limit": "as ||B||->infinity the source condition approaches f(L)=0; parity spectral flow produces n_odd asymptotic zero modes",
            "finite_B": "no new exact zero occurs while B_EE stays full rank, but eigenvalues can be parametrically small",
            "direction_dependence": "if only selected singular values of B grow, count spectral flow in those image/kernel subspaces; rank alone is insufficient",
            "localization": "finite kink masses can independently make source overlaps and physical poles exponentially small",
            "threshold_warning": "full thresholds must use all roots of C_full, not projected rank or det B",
        },
        "numerical_certificate": {
            "parameters": {
                "L": length,
                "M_HLF_HLA_HRA_HRF": list(masses),
                "t_L": theta_left,
                "t_R": theta_right,
                "s_16": sigma_16,
                "s_bar16": sigma_bar16,
            },
            "boundary_is_hermitian": is_hermitian(boundary_singlet),
            "complex_Nambu_certificate": {
                "mu_is_symmetric": complex_mu[0][1] == complex_mu[1][0],
                "B_N_is_hermitian": is_hermitian(complex_nambu),
                "complex_chiral_zero_nullity": holomorphic_zero_nullity(
                    complex_mu, (True, True)
                ),
                "doubled_B_N_rank": matrix_rank(complex_nambu),
            },
            "left_zero_factorization": {key: _clean_number(value) for key, value in left_zero.items()},
            "right_singlet_zero_factorization": {key: _clean_number(value) for key, value in right_zero.items()},
            "zero_counts": counts_both,
            "boundary_rank_tuned_example": {
                "det_B": _clean_number(determinant(tuned_sigma)),
                "right_zero_nullity": zero_mode_nullity(tuned_sigma, E_RIGHT),
                "parameters": {
                    "t_L": theta_left,
                    "t_R": theta_right,
                    "s_16": 0.8,
                    "s_bar16": theta_left * theta_right / 0.8,
                },
            },
            "flat_singlet_lightest_absolute_signed_mass": {
                "Sigma_zero": round(weak_root, 14),
                "Sigma_large": round(strong_root, 14),
                "large_over_zero": round(strong_root / weak_root, 14),
            },
        },
        "decision": {
            "idealized_four_spinor_zero_mode_problem": "closed for finite Hermitian B with t_L,t_R nonzero",
            "S2_closed": False,
            "gates_promoted": [],
            "complete_theory": False,
            "remaining_obligations": [
                "derive the full matrix-valued map from bare Theta/Sigma delta coefficients to B in one resolved source-wall regulator",
                "include induced boundary kinetic, derivative and any wrong-chirality terms in the transfer problem",
                "choose numerical M_i,L and source couplings and compute the complete shifted threshold spectrum",
                "recompute 5D unification, perturbativity and cross-wall Wilson coefficients from C_full",
                "finish eta/global anomaly, discrete selector, flavor, neutrino, Higgs and SUSY-breaking audits",
            ],
        },
        "primary_sources": [dict(item) for item in PRIMARY_SOURCES],
        "provenance": {
            "generator": Path(__file__).name,
            "tests": TEST_PATH.name,
            "upstream_sha256": {
                path.name: sha256_file(path) if path.exists() else None for path in UPSTREAM_INPUTS
            },
            "charge_blind_numeric_dependency": {
                v46.__file__: sha256_file(Path(v46.__file__)),
                "use": "only S(z), F(z), and G(z) profile functions are imported; no V46 charge labels are imported",
            },
            "normalization_audit": {
                "authoritative_convention": "primitive displayed local-particle U1F normalization",
                "relation_to_legacy_x3_labels": "q_primitive=q_legacy/3",
                "legacy_x3_channel_labels_retained_in_V47": False,
                "U1chi_labels_kept_distinct_from_U1F": True,
            },
            "V45_or_V46_files_modified": False,
        },
    }
    report = json.loads(json.dumps(report, ensure_ascii=True))
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if canonical_sha(report) != report["core_sha256"]:
        raise RuntimeError("core hash is stale")
    projectors = report["field_and_component_contract"]["projector_relations"]
    charge_contract = report["field_and_component_contract"]
    if charge_contract["primitive_U1F_charges"] != PRIMITIVE_U1F:
        raise RuntimeError("primitive U1F field charges drifted")
    if any(charge_contract["U1F_operator_charge_sums"].values()):
        raise RuntimeError("a retained source operator is not U1F neutral")
    if projectors["rank_P_left"] != 8 or projectors["rank_P_right"] != 8:
        raise RuntimeError("PS component split drifted")
    if projectors["rank_P_SU5_singlet"] != 1 or not projectors["P_singlet_is_subprojector_of_P_right"]:
        raise RuntimeError("Sigma singlet projector drifted")
    counts = report["V46_Theta_Sigma_zero_count"]
    if counts["both_Theta_nonzero"]["total_chiral_component_zero_modes"] != 0:
        raise RuntimeError("both Theta blocks should remove all zero modes")
    if counts["t_L_zero"]["total_chiral_component_zero_modes"] != 16:
        raise RuntimeError("missing t_L should leave 16 chiral component zero modes")
    if counts["t_R_zero"]["total_chiral_component_zero_modes"] != 16:
        raise RuntimeError("missing t_R should leave 16 chiral component zero modes")
    if counts["both_Theta_zero"]["total_chiral_component_zero_modes"] != 32:
        raise RuntimeError("missing both Theta blocks should leave 32 zero modes")
    numerical = report["numerical_certificate"]
    if not numerical["boundary_is_hermitian"]:
        raise RuntimeError("certificate boundary matrix is not Hermitian")
    if not numerical["complex_Nambu_certificate"]["B_N_is_hermitian"]:
        raise RuntimeError("complex Nambu lift is not Hermitian")
    if numerical["complex_Nambu_certificate"]["complex_chiral_zero_nullity"] != 0:
        raise RuntimeError("full-rank complex holomorphic mass gained a zero")
    for key in ("left_zero_factorization", "right_singlet_zero_factorization"):
        if abs(numerical[key]["direct"] - numerical[key]["factorized"]) > 1.0e-11:
            raise RuntimeError("zero determinant factorization failed")
    if numerical["boundary_rank_tuned_example"]["det_B"] != 0.0:
        raise RuntimeError("boundary-rank counterexample is not tuned")
    if numerical["boundary_rank_tuned_example"]["right_zero_nullity"] != 0:
        raise RuntimeError("singular full B incorrectly created a zero")
    if report["decision"]["S2_closed"] or report["decision"]["gates_promoted"]:
        raise RuntimeError("this transfer subaudit cannot close S2 or promote gates")


def render_markdown(data: Mapping[str, Any]) -> str:
    numerical = data["numerical_certificate"]
    counts = data["V46_Theta_Sigma_zero_count"]
    roots = numerical["flat_singlet_lightest_absolute_signed_mass"]
    return f"""# V47 four-spinor mixed KK audit

Status: `{data['status']}`

## Verdict

The exact four-hypermultiplet boundary problem can be solved without truncating
the KK tower.  For every finite, self-adjoint renormalized source matrix `B`,
the massless spectrum depends **only** on the block `B_EE=E B E` connecting
fields even at the PS wall.  Even--odd and odd--odd source masses can alter the
wavefunctions and every nonzero KK pole, but they cannot lift an exact chiral
zero mode.

Applied to V46/V47, the two Theta masses make `B_EE` full rank in all 16
Spin(10) component directions.  The allowed `barSigma HLF HRA` and
`Sigma HLA HRF` entries act only on the SU(5)-singlet component and are
even--odd there.  Consequently they create no additional zero and remove no
zero that would remain if a Theta block vanished.  With both Theta parameters
finite and nonzero, the enlarged idealized system has **zero exact KK zero
modes**.  This does not close S2 because the bare-brane matching and numerical
threshold spectrum remain open.

## Exact component projectors

The faithful primitive `U(1)F` charges are

`HLF,HLA,HRA,HRF,ThetaPlus,ThetaMinus = +1,-4,-1,+4,+3,-3`.

All four retained source operators are neutral in this normalization.  The
older labels `(+3,-12,-3,+12; +/-9)` are only a common-factor-three convention
and are not used in this V47 contract.

Use the internal spinor ordering

`(Q[6], L[2] | uC[3], dC[3], eC | nuC)`.

Then

`P_L=diag(1^8,0^8)`, `P_R=diag(0^8,1^8)`, and
`P_1=diag(0^15,1)`.

Separately, under `SU(5) x U(1)chi`, the SO(10) spinor decomposition is
`16=10_(chi=-1)+bar5_(chi=+3)+1_(chi=-5)`.  These subscripts are `U(1)chi`,
not `U(1)F`.  The final `nuC` entry is the `chi=-5` singlet and lies in the
PS-right half, so `P_1 P_R=P_1` and `rank(P_1)=1`.  The SU(5)-singlet 126 or
bar126 VEV therefore projects

- `barSigma HLF HRA` onto the `HLF_nuC--HRA_nuC` entry, and
- `Sigma HLA HRF` onto its conjugate `HLA_nuC--HRF_nuC` entry.

It vanishes on the other fifteen internal components.  This is stronger than
saying the direct selected-zero-mode projection vanishes: it specifies the
complete component operator that must enter the KK determinant.

## Renormalized boundary matrix

In channel order `(HLF,HLA,HRA,HRF)`, the Hermitian extension matrix is

```text
B = [[0,    tL,       s16 P1,       0],
     [tL*,  0,        0,       sbar16 P1],
     [s16*, 0,        0,            tR],
     [0,    sbar16*,  tR*,           0]] .
```

The four entries are renormalized boundary-extension parameters, not bare
delta coefficients.  In the real singlet component

`det B=(tL tR-s16 sbar16)^2`.

This determinant is **not** the zero-mode test when the PS-wall parities are
mixed.

## General transfer-matrix characteristic

Let `E` project H fields even at `y=0`, `O=1-E`, and let the real diagonal odd
bulk masses on `0<y<L` be `M_i`.  Define

`S_i=sin(k_iL)/k_i`, `F_i=cos(k_iL)-M_iS_i`,
`G_i=cos(k_iL)+M_iS_i`, with `k_i^2=m^2-M_i^2`.

The exact one-channel transfer matrix is

```text
[f_i(L)]   [ F_i    m S_i ] [f_i(0)]
[g_i(L)] = [-m S_i  G_i  ] [g_i(0)].
```

The parity data can be written `f(0)=E a`, `g(0)=O a`.  Imposing
`g(L)+B f(L)=0` gives the finite characteristic matrix

`K(m)=(-mS+BF)E+(G+mBS)O`,

and the exact signed eigenvalue equation is

`C(m)=det K(m)=0`.

Because mixed even--odd masses need not make `C` even, the complete
mass-squared characteristic is

`D(z)=C(sqrt(z)) C(-sqrt(z))`.

It is entire in `z`.  The complete four-spinor result is

`C_full=C_L^8 C_R,non-singlet^7 C_R,singlet`.

This accounts for all 64 bulk-H chiral component channels.  No division by
`m`, `S`, `F`, or `G` is made, so the formula remains valid at zero and at
bulk thresholds.

## Exact zero theorem

At `m=0`,

`K(0)=B F(0)E+G(0)O`.

Ordering odd rows/columns before even ones makes this block triangular:

`det K(0)=det G_O(0) det(B_EE) det F_E(0)`.

Both profile determinants are products of finite exponentials and cannot
vanish.  Therefore

`n_zero,chiral = n_even-rank(B_EE)`.

For a vector in `ker(B_EE)`, the odd-channel admixture is fixed by

`a_O=-G_O(0)^(-1) OBE F_E(0) a_E`.

This explicitly proves that the even--odd block changes the zero-mode profile
but cannot change its existence.  For a general complex symmetric holomorphic
mass `mu`, the same statement follows after the Hermitian Nambu lift
`B_N=[[0,mu^dagger],[mu,0]]`, and reduces to `ker(mu_EE)` in complex chiral
counting.

## V46 Theta+Sigma count

For the eight PS-left components, `E=diag(1,1,0,0)` and

`B_EE=[[0,tL],[tL*,0]]`.

For all eight PS-right components, including the single SU(5) singlet,
`E=diag(0,0,1,1)` and

`B_EE=[[0,tR],[tR*,0]]`.

The Sigma entries are outside both displayed even--even blocks.  The exact
chiral-component counts are:

- both Theta blocks nonzero: `{counts['both_Theta_nonzero']['total_chiral_component_zero_modes']}`;
- `tL=0`: `{counts['t_L_zero']['total_chiral_component_zero_modes']}`;
- `tR=0`: `{counts['t_R_zero']['total_chiral_component_zero_modes']}`;
- both zero: `{counts['both_Theta_zero']['total_chiral_component_zero_modes']}`.

Two useful counterexamples prevent a false rank argument:

1. `det B` can vanish at `tL tR=s16 sbar16` while `B_EE` is full rank and
   there is no zero mode.
2. With `tR=0` and nonzero Sigma entries, the full singlet `B` can be
   invertible while `B_EE=0` and two right-component chiral zero modes remain.

## Self-adjointness and tachyons

The first-order boundary form is

`[-f_psi^dagger g_phi+g_psi^dagger f_phi]_0^L`.

The parity condition at `y=0` is isotropic.  At the source, `g=-Bf` cancels
the form exactly when `B=B^dagger`; arbitrary complex superpotential masses
must be handled by the Hermitian Nambu lift.  The resulting first-order KK
operator has real signed eigenvalues.  Unbroken 4D N=1 supersymmetry then gives
nonnegative scalar masses squared.  Thus the declared problem has no
tachyonic or complex roots.

This proof does not cover non-Hermitian matching, negative boundary kinetic
norms, scalar-only SUSY-breaking masses, or an energy-dependent boundary kernel
whose additional boundary states have been integrated out incorrectly.

## Regulated determinant and strong-coupling warning

When `C(0)!=0`, the same-domain spectral determinant is

`P_B(z)=C(sqrt(z))C(-sqrt(z))/C(0)^2=product_a(1-z/m_a^2)`.

If `C(m)=c_q m^q+...`, remove the zeros by dividing the numerator by
`(-1)^q c_q^2 z^q`.  Unit-normalized Hermitian boundary rows are
`(I+B^2)^(-1/2)(g+Bf)=0`.  Same-domain products are independent of boundary-row
rescaling, while absolute and cross-`B` constants still require a brane
regulator and local counterterm scheme.

No exact zero appears at finite `B` while `B_EE` is full rank, but large
boundary singular values can create parametrically light states.  At the flat
certificate point, increasing the two Sigma entries from zero to
`({numerical['parameters']['s_16']},{numerical['parameters']['s_bar16']})`
changes the lightest singlet absolute signed mass from
`{roots['Sigma_zero']}` to `{roots['Sigma_large']}`.  If an invertible `B` is
scaled to infinity, the source condition tends to `f(L)=0` and `n_odd`
parity-flow zero modes appear at the limiting self-adjoint endpoint.

Projected rank, `det B`, and the phrase “large boundary mass” therefore do not
determine thresholds.  The actual 5D threshold calculation must use every root
of `C_full`.

## Fail-closed decision

The idealized four-spinor zero-mode question is closed: finite Hermitian `B`
with `tL,tR!=0` has no exact zero.  S2 and every G gate remain open.  Required
next steps are:

1. derive the matrix map from the four bare Theta/Sigma brane coefficients to
   `B` in one resolved source-wall regulator;
2. include induced kinetic, derivative and wrong-chirality terms;
3. fix `M_i,L` and source couplings and calculate the complete shifted
   thresholds, perturbativity and cross-wall Wilson coefficients;
4. finish the eta/global-anomaly, selector, flavor, neutrino, Higgs and
   SUSY-breaking audits.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230),
[Syed](https://arxiv.org/abs/hep-ph/0508153),
[Alciati et al.](https://arxiv.org/abs/hep-ph/0603086), and
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `{data['core_sha256']}`
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.exists() or not MD_PATH.exists():
        raise RuntimeError("V47 artifacts are missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V47 JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V47 Markdown is stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    args = parser.parse_args()
    report = build_report()
    if args.write:
        write_artifacts(report)
    if args.check:
        check_artifacts(report)
    if args.print_json or (not args.write and not args.check):
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
