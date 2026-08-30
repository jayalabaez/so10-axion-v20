#!/usr/bin/env python3
"""V49 generalized boundary pencil and restricted-action Wilson-kernel audit.

The objective is not to hide omitted wall terms behind a constant B.  Every
quadratic retained wall term is represented by a Hermitian matrix pencil (or
by a positive-metric auxiliary boundary state whose Schur complement is that
pencil).  The exact finite V48 collar is retained, and the PS and source
pencils are composed with it before any determinant or Wilson kernel is taken.

The executable also constructs the full 64-coordinate PS spinor trace map in
an explicit SU(4) x SU(2)L x SU(2)R epsilon convention.  SO(10) source tensors
beyond the singlet-VEV projectors remain finite invariant-tensor inputs; that
limitation is reported rather than treated as component-resolved matching.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

import susy_v47_four_spinor_mixed_kk_audit as v47
import susy_v48_source_operator_wilson_audit as v48


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V49_GENERALIZED_BOUNDARY_PENCIL_AUDIT.json"
MD_PATH = ROOT / "SUSY_V49_GENERALIZED_BOUNDARY_PENCIL_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v49_generalized_boundary_pencil_audit.py"

STATUS = (
    "V49_GENERALIZED_POSITIVE_BOUNDARY_PENCIL_AND_RESTRICTED_ACTION_KERNEL_DERIVED__"
    "FULL_64_TRACE_PS_CLEBSCH_CURRENT_MAP_EXECUTABLE__"
    "POLE_RESIDUE_LOCALITY_AND_DECOUPLING_IDENTITIES_PASS__"
    "STRONG_COLLAR_HC_GENERATOR_AND_SOURCE_QUARTIC_SO10_TENSORS_REMAIN_ABSTRACT__"
    "G2_FAIL_CLOSED"
)

UPSTREAM = (
    ROOT / "SUSY_V48_G2_FRONTIER_INTEGRATION_AUDIT.json",
    ROOT / "SUSY_V48_G2_ADVERSARIAL_CLOSURE_AUDIT.json",
    ROOT / "SUSY_V48_SOURCE_OPERATOR_WILSON_AUDIT.json",
    ROOT / "SUSY_V48_RESOLVED_SOURCE_WALL_AUDIT.json",
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = dict(value)
    payload.pop("core_sha256", None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def hermitian_residual(matrix: Sequence[Sequence[complex]]) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    return float(np.max(np.abs(value - value.conjugate().T)))


def minimum_eigenvalue(matrix: Sequence[Sequence[complex]]) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    if hermitian_residual(value) > 1.0e-10:
        raise ValueError("minimum_eigenvalue requires a Hermitian matrix")
    return float(np.min(np.linalg.eigvalsh(value)))


def positive_definite(matrix: Sequence[Sequence[complex]], tolerance: float = 1.0e-10) -> bool:
    return minimum_eigenvalue(matrix) > tolerance


def positive_semidefinite(matrix: Sequence[Sequence[complex]], tolerance: float = 1.0e-10) -> bool:
    return minimum_eigenvalue(matrix) >= -tolerance


def passive_boundary_pencil(
    mass: complex,
    mass_matrix: Sequence[Sequence[complex]],
    kinetic: Sequence[Sequence[complex]],
    coupling: Sequence[Sequence[complex]] | None = None,
    auxiliary_hamiltonian: Sequence[Sequence[complex]] | None = None,
    auxiliary_metric: Sequence[Sequence[complex]] | None = None,
) -> np.ndarray:
    """P(m)=M-mZ-C^dagger(H-mW)^-1 C.

    This is the Schur complement of a finite Hermitian generalized eigenvalue
    problem.  Z>=0 and W>0 are sufficient for a positive enlarged norm.
    """

    m0 = np.asarray(mass_matrix, dtype=np.complex128)
    z0 = np.asarray(kinetic, dtype=np.complex128)
    if m0.shape != z0.shape or m0.shape[0] != m0.shape[1]:
        raise ValueError("boundary mass and kinetic matrices must be equally square")
    if hermitian_residual(m0) > 1.0e-10 or hermitian_residual(z0) > 1.0e-10:
        raise ValueError("boundary M and Z must be Hermitian")
    result = m0 - mass * z0
    if coupling is None:
        if auxiliary_hamiltonian is not None or auxiliary_metric is not None:
            raise ValueError("auxiliary blocks require a coupling")
        return result
    c0 = np.asarray(coupling, dtype=np.complex128)
    h0 = np.asarray(auxiliary_hamiltonian, dtype=np.complex128)
    w0 = np.asarray(auxiliary_metric, dtype=np.complex128)
    if h0.shape != w0.shape or h0.shape[0] != h0.shape[1]:
        raise ValueError("auxiliary H and W must be equally square")
    if c0.shape != (h0.shape[0], m0.shape[0]):
        raise ValueError("auxiliary coupling has incompatible shape")
    if hermitian_residual(h0) > 1.0e-10 or not positive_definite(w0):
        raise ValueError("auxiliary H must be Hermitian and W positive")
    resolvent = np.linalg.inv(h0 - mass * w0)
    return result - c0.conjugate().T @ resolvent @ c0


def passive_derivative_metric(
    mass: float,
    kinetic: Sequence[Sequence[complex]],
    coupling: Sequence[Sequence[complex]],
    auxiliary_hamiltonian: Sequence[Sequence[complex]],
    auxiliary_metric: Sequence[Sequence[complex]],
) -> np.ndarray:
    """Return -dP/dm=Z+C^dag R W R C on a real pole-free interval."""

    z0 = np.asarray(kinetic, dtype=np.complex128)
    c0 = np.asarray(coupling, dtype=np.complex128)
    h0 = np.asarray(auxiliary_hamiltonian, dtype=np.complex128)
    w0 = np.asarray(auxiliary_metric, dtype=np.complex128)
    resolvent = np.linalg.inv(h0 - mass * w0)
    return z0 + c0.conjugate().T @ resolvent @ w0 @ resolvent @ c0


def relation_to_graph_pencil(
    a_relation: Sequence[Sequence[complex]], b_relation: Sequence[Sequence[complex]]
) -> np.ndarray:
    """Convert A_rel b+B_rel a=0 into b+P a=0 when A_rel is invertible."""

    arel = np.asarray(a_relation, dtype=np.complex128)
    brel = np.asarray(b_relation, dtype=np.complex128)
    if arel.shape != brel.shape or arel.shape[0] != arel.shape[1]:
        raise ValueError("relation blocks must be equally square")
    pencil = np.linalg.solve(arel, brel)
    if hermitian_residual(pencil) > 1.0e-9:
        raise ValueError("normal-derivative relation is not a self-adjoint graph")
    return pencil


def generalized_host_pair(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    collar_mass: Sequence[Sequence[complex]],
    even: Sequence[bool],
    epsilon: float,
    source_pencil: Sequence[Sequence[complex]],
) -> tuple[np.ndarray, np.ndarray]:
    """Compose bulk, finite collar, and an outer source pencil.

    The collar gives fout=D fL+U gL and gout=C fL+D gL.  Imposing
    gout+P_L fout=0 produces Cf=C+P_L D and Cg=D+P_L U, hence
    K=Cf R+Cg Q and N=Cf P+Cg T.
    """

    dblock, ublock, cblock = v48.collar_transfer_blocks(mass, collar_mass, epsilon)
    rblock = v48.source_value_transfer(mass, bulk_masses, length, even)
    qblock = v48.inner_residual_transfer(mass, bulk_masses, length, even)
    pblock, tblock = v48.initial_conjugate_transfers(mass, bulk_masses, length, even)
    source = np.asarray(source_pencil, dtype=np.complex128)
    cf = cblock + source @ dblock
    cg = dblock + source @ ublock
    return cf @ rblock + cg @ qblock, cf @ pblock + cg @ tblock


def generalized_wilson_kernel(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    collar_mass: Sequence[Sequence[complex]],
    even: Sequence[bool],
    epsilon: float,
    source_pencil: Sequence[Sequence[complex]],
    host_pencil: Sequence[Sequence[complex]],
) -> tuple[np.ndarray, np.ndarray]:
    kblock, nblock = generalized_host_pair(
        mass, bulk_masses, length, collar_mass, even, epsilon, source_pencil
    )
    gamma = kblock + nblock @ np.asarray(host_pencil, dtype=np.complex128)
    return gamma, np.linalg.solve(gamma, nblock)


def ps_higgs_clebsch(higgs: Sequence[Sequence[complex]]) -> np.ndarray:
    """8x8 PS map in a fixed epsilon_L epsilon_R convention.

    Left order is (r_up,r_down,g_up,g_down,b_up,b_down,nu,e).
    Right order is (uCr,dCr,uCg,dCg,uCb,dCb,nuC,eC).  This is a
    presentation permutation of V47's internal right ordering.
    """

    h = np.asarray(higgs, dtype=np.complex128)
    if h.shape != (2, 2):
        raise ValueError("the bidoublet must be 2x2")
    epsilon2 = np.asarray([[0.0, 1.0], [-1.0, 0.0]], dtype=np.complex128)
    contracted = epsilon2 @ h @ epsilon2.T
    result = np.zeros((8, 8), dtype=np.complex128)
    for su4 in range(4):
        result[2 * su4 : 2 * su4 + 2, 2 * su4 : 2 * su4 + 2] = contracted
    return result


def v47_to_ps_right_permutation() -> np.ndarray:
    """Map V47 right order (uC^3,dC^3,eC,nuC) to paired PS order."""

    # ps paired order takes V47 indices [8,11,9,12,10,13,15,14].
    relative = (0, 3, 1, 4, 2, 5, 7, 6)
    result = np.zeros((8, 8), dtype=np.complex128)
    for ps_index, v47_index in enumerate(relative):
        result[ps_index, v47_index] = 1.0
    return result


def full_64_ps_vertex(
    higgs: Sequence[Sequence[complex]], coefficients: Sequence[complex]
) -> np.ndarray:
    """All four PS H/Hc bilinears on the 64 boundary trace coordinates.

    Coordinate order is V47 internal component major, then (A,B,C,D).  The
    four coefficients multiply A_L-C_R, B_L-D_R, Cc_L-Ac_R, Dc_L-Bc_R.
    """

    if len(coefficients) != 4:
        raise ValueError("four PS bilinear coefficients are required")
    paired = ps_higgs_clebsch(higgs)
    permutation = v47_to_ps_right_permutation()
    # Columns returned in the V47 right ordering.
    clebsch = paired @ permutation
    result = np.zeros((64, 64), dtype=np.complex128)
    channel_pairs = ((0, 2), (1, 3), (2, 0), (3, 1))
    for (left_channel, right_channel), coefficient in zip(channel_pairs, coefficients):
        for left in range(8):
            for right_relative in range(8):
                value = complex(coefficient) * clebsch[left, right_relative]
                if value == 0:
                    continue
                right_internal = 8 + right_relative
                first = 4 * left + left_channel
                second = 4 * right_internal + right_channel
                result[first, second] += value
                result[second, first] += value.conjugate()
    return result


def full_64_bulk_blocks(
    mass: complex,
    bulk_masses: Sequence[float],
    length: float,
    theta_left: float,
    theta_right: float,
    sigma_16: float,
    sigma_bar16: float,
    epsilon: float,
    source_pencil_4: Sequence[Sequence[complex]],
) -> tuple[np.ndarray, np.ndarray]:
    k_blocks: list[np.ndarray] = []
    n_blocks: list[np.ndarray] = []
    for component in range(16):
        singlet = component == 15
        boundary = np.asarray(
            v47.theta_sigma_boundary_matrix(
                theta_left,
                theta_right,
                sigma_16 if singlet else 0.0,
                sigma_bar16 if singlet else 0.0,
                su5_singlet=singlet,
            ),
            dtype=np.complex128,
        )
        even = v47.E_LEFT if component < 8 else v47.E_RIGHT
        kblock, nblock = generalized_host_pair(
            mass,
            bulk_masses,
            length,
            boundary,
            even,
            epsilon,
            source_pencil_4,
        )
        k_blocks.append(kblock)
        n_blocks.append(nblock)
    return v48.block_diagonal(*k_blocks), v48.block_diagonal(*n_blocks)


def full_64_current(
    higgs: Sequence[Sequence[complex]],
    q_families: Sequence[Sequence[complex]],
    qc_families: Sequence[Sequence[complex]],
    y_i4: Sequence[complex],
    y_4j: Sequence[complex],
) -> np.ndarray:
    """Physical six one-bulk PS currents in the V47 64-coordinate order."""

    q = np.asarray(q_families, dtype=np.complex128)
    qc = np.asarray(qc_families, dtype=np.complex128)
    if q.shape != (3, 8) or qc.shape != (3, 8):
        raise ValueError("Q and Qc family component arrays must be 3x8")
    left_source = np.tensordot(np.asarray(y_i4), q, axes=(0, 0))
    right_source_ps = np.tensordot(np.asarray(y_4j), qc, axes=(0, 0))
    clebsch = ps_higgs_clebsch(higgs) @ v47_to_ps_right_permutation()
    # J_A(left)=H*sum Y4j Qc_j; J_C(right)=H^T*sum Yi4 Qi.
    j_left = clebsch @ right_source_ps
    j_right_v47 = clebsch.T @ left_source
    result = np.zeros(64, dtype=np.complex128)
    for left in range(8):
        result[4 * left + 0] = j_left[left]
    for right_relative in range(8):
        result[4 * (8 + right_relative) + 2] = j_right_v47[right_relative]
    return result


def deterministic_hermitian(size: int, seed: int, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size))
    return scale * (raw + raw.conjugate().T) / (2.0 * size)


def deterministic_positive(size: int, seed: int, floor: float, scale: float) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(size, size)) + 1j * rng.normal(size=(size, size))
    return floor * np.eye(size) + scale * (raw.conjugate().T @ raw) / size


def _bisect(function: Any, low: float, high: float) -> float:
    f_low = float(function(low))
    f_high = float(function(high))
    if f_low * f_high > 0:
        raise ValueError("root not bracketed")
    for _ in range(100):
        middle = (low + high) / 2.0
        value = float(function(middle))
        if abs(value) < 1.0e-12 or high - low < 1.0e-11:
            return middle
        if f_low * value <= 0:
            high = middle
            f_high = value
        else:
            low = middle
            f_low = value
    return (low + high) / 2.0


def first_roots(function: Any, maximum: float, steps: int, count: int) -> list[float]:
    roots: list[float] = []
    previous_x = 0.0
    previous = float(function(previous_x))
    for step in range(1, steps + 1):
        current_x = maximum * step / steps
        current = float(function(current_x))
        if previous * current < 0:
            root = _bisect(function, previous_x, current_x)
            if not roots or abs(root - roots[-1]) > 1.0e-6:
                roots.append(root)
                if len(roots) == count:
                    break
        previous_x, previous = current_x, current
    return roots


def representative_certificate() -> dict[str, Any]:
    masses = (0.0, 0.0, 0.0, 0.0)
    length = 1.0
    epsilon = 0.05
    boundary = np.asarray(
        v47.theta_sigma_boundary_matrix(0.4, 0.6, 0.2, -1.0 / 6.0, su5_singlet=True),
        dtype=np.complex128,
    )
    m_host = deterministic_hermitian(4, 101, 0.08)
    z_host = deterministic_positive(4, 102, 0.12, 0.015)
    c_host = np.asarray([[0.03, 0.01j, 0.0, 0.0], [0.0, 0.02, -0.01j, 0.0]], dtype=np.complex128)
    h_host = np.asarray([[2.1, 0.04], [0.04, 2.7]], dtype=np.complex128)
    w_host = np.asarray([[1.1, 0.0], [0.0, 0.9]], dtype=np.complex128)
    m_source = deterministic_hermitian(4, 103, 0.06)
    z_source = deterministic_positive(4, 104, 0.10, 0.012)
    c_source = np.asarray([[0.02, 0.0, 0.01, 0.0], [0.0, -0.015j, 0.0, 0.025]], dtype=np.complex128)
    h_source = np.asarray([[2.4, -0.03], [-0.03, 3.0]], dtype=np.complex128)
    w_source = np.asarray([[1.0, 0.0], [0.0, 1.2]], dtype=np.complex128)

    def pencils(mass: complex) -> tuple[np.ndarray, np.ndarray]:
        return (
            passive_boundary_pencil(mass, m_host, z_host, c_host, h_host, w_host),
            passive_boundary_pencil(mass, m_source, z_source, c_source, h_source, w_source),
        )

    def gamma(mass: complex) -> np.ndarray:
        host, source = pencils(mass)
        return generalized_wilson_kernel(
            mass, masses, length, boundary, v47.E_RIGHT, epsilon, source, host
        )[0]

    determinant = lambda trial: float(np.linalg.det(gamma(trial)).real)
    roots = first_roots(determinant, 10.0, 20000, 3)
    first = roots[0]
    step = 1.0e-6
    derivative = (determinant(first + step) - determinant(first - step)) / (2.0 * step)
    residue_formula = v48.adjugate(gamma(first)) / derivative
    near = step * np.linalg.inv(gamma(first + step))

    euclidean: dict[str, float] = {}
    euclidean_host: dict[str, float] = {}
    for p in (1.0, 2.0, 4.0, 8.0):
        host, source = pencils(1j * p)
        matrix, kernel = generalized_wilson_kernel(
            1j * p, masses, length, boundary, v47.E_RIGHT, epsilon, source, host
        )
        # Gamma^-1 is the one-crossing response to an outer/source current and
        # must be exponentially local. G00=Gamma^-1 N contains the ordinary
        # local PS reflection/contact response and need not decay exponentially.
        euclidean[str(p)] = v48.spectral_norm(np.linalg.inv(matrix))
        euclidean_host[str(p)] = v48.spectral_norm(kernel)

    derivative_host = passive_derivative_metric(
        0.3, z_host, c_host, h_host, w_host
    )
    derivative_source = passive_derivative_metric(
        0.3, z_source, c_source, h_source, w_source
    )

    # Profile/counterterm rematching: exact collar versus its O(m) kernel.
    test_mass = 0.17
    exact_b = v48.collar_kernel_matrix(test_mass, boundary, epsilon)
    linear_b = boundary - test_mass * epsilon * (
        np.eye(4) + boundary @ boundary / 3.0
    )
    collar_remainder = v48.spectral_norm(exact_b - linear_b)

    auxiliary_decoupling: dict[str, float] = {}
    base_source = m_source - 0.3 * z_source
    for scale in (1.0, 2.0, 4.0, 8.0, 16.0):
        full = passive_boundary_pencil(
            0.3, m_source, z_source, c_source, scale * h_source, w_source
        )
        auxiliary_decoupling[str(scale)] = v48.spectral_norm(full - base_source)

    return {
        "metric_checks": {
            "host_Z_min_eigenvalue": minimum_eigenvalue(z_host),
            "source_Z_min_eigenvalue": minimum_eigenvalue(z_source),
            "host_W_min_eigenvalue": minimum_eigenvalue(w_host),
            "source_W_min_eigenvalue": minimum_eigenvalue(w_source),
            "minus_dP_host_min_eigenvalue_at_m03": minimum_eigenvalue(derivative_host),
            "minus_dP_source_min_eigenvalue_at_m03": minimum_eigenvalue(derivative_source),
        },
        "self_adjoint_checks": {
            "host_pencil_hermitian_at_real_m": hermitian_residual(pencils(0.3)[0]),
            "source_pencil_hermitian_at_real_m": hermitian_residual(pencils(0.3)[1]),
            "collar_J_unitary_at_zero": v48.symplectic_residual(boundary),
        },
        "roots_and_residue": {
            "first_three_positive_roots": roots,
            "det_at_first_abs": abs(determinant(first)),
            "first_derivative": derivative,
            "near_pole_residue_residual": float(np.max(np.abs(near - residue_formula))),
        },
        "euclidean_locality": {
            "source_to_host_Gamma_inverse_norms": euclidean,
            "host_to_host_G00_norms": euclidean_host,
            "norm8_over_norm4": euclidean["8.0"] / euclidean["4.0"],
            "scaled_at_4": euclidean["4.0"] * math.exp(4.0 * (length + epsilon)),
            "scaled_at_8": euclidean["8.0"] * math.exp(8.0 * (length + epsilon)),
        },
        "collar_linear_remainder": {
            "mass": test_mass,
            "epsilon": epsilon,
            "exact_minus_linear_norm": collar_remainder,
            "normalized_by_m2_epsilon2": collar_remainder / (test_mass**2 * epsilon**2),
        },
        "auxiliary_decoupling": {
            "Schur_correction_norms": auxiliary_decoupling,
            "norm16_over_norm8": auxiliary_decoupling["16.0"] / auxiliary_decoupling["8.0"],
            "monotone": all(
                later < earlier
                for earlier, later in zip(
                    auxiliary_decoupling.values(), list(auxiliary_decoupling.values())[1:]
                )
            ),
        },
    }


def full_component_certificate() -> dict[str, Any]:
    masses = (0.0, 0.0, 0.0, 0.0)
    higgs = np.asarray([[0.07, -0.02], [0.03, 0.05]], dtype=np.complex128)
    coefficients = (0.31, -0.23, 0.19, -0.17)
    vertex = full_64_ps_vertex(higgs, coefficients)
    source_pencil = np.zeros((4, 4), dtype=np.complex128)
    kblock, nblock = full_64_bulk_blocks(
        0.0, masses, 1.0, 0.4, 0.6, 0.2, -1.0 / 6.0, 0.05, source_pencil
    )
    z64 = deterministic_positive(64, 201, 0.015, 0.001)
    host = vertex  # At m=0; Z64 is tested independently and enters for m!=0.
    gamma = kblock + nblock @ host
    g00 = np.linalg.solve(gamma, nblock)

    q = np.asarray(
        [[0.01 * (1 + family + component) for component in range(8)] for family in range(3)],
        dtype=np.complex128,
    )
    qc = np.asarray(
        [[-0.008 * (1 + 2 * family + component) for component in range(8)] for family in range(3)],
        dtype=np.complex128,
    )
    current = full_64_current(higgs, q, qc, (0.11, -0.07, 0.05), (0.09, 0.04, -0.06))
    weff = -0.5 * current.T @ g00 @ current

    clebsch = ps_higgs_clebsch(higgs)
    expected_clebsch_norm = 4.0 * float(np.sum(np.abs(higgs) ** 2))
    nonzero_upper = int(np.count_nonzero(np.triu(np.abs(vertex) > 1.0e-14, 1)))

    # Universal deterministic admissible-tensor test: add three Hermitian
    # counterterm/normal-derivative draws and require a finite same-action kernel.
    random_trials: list[dict[str, Any]] = []
    for seed in (301, 302, 303):
        mass_block = deterministic_hermitian(64, seed, 0.002)
        kinetic_block = deterministic_positive(64, seed + 10, 0.01, 0.0005)
        trial_mass = 0.12
        host_pencil = vertex + mass_block - trial_mass * kinetic_block
        # Rebuild bulk at the same nonzero mass.
        k_trial, n_trial = full_64_bulk_blocks(
            trial_mass,
            masses,
            1.0,
            0.4,
            0.6,
            0.2,
            -1.0 / 6.0,
            0.05,
            source_pencil,
        )
        trial_gamma = k_trial + n_trial @ host_pencil
        trial_kernel = np.linalg.solve(trial_gamma, n_trial)
        random_trials.append(
            {
                "seed": seed,
                "kinetic_min_eigenvalue": minimum_eigenvalue(kinetic_block),
                "host_hermitian_residual": hermitian_residual(host_pencil),
                "kernel_finite": bool(np.isfinite(trial_kernel).all()),
                "kernel_norm": v48.spectral_norm(trial_kernel),
            }
        )

    return {
        "coordinate_count": 64,
        "component_order": list(v47.INTERNAL_COMPONENTS),
        "channel_order": list(v47.CHANNELS),
        "PS_right_presentation_permutation": [0, 3, 1, 4, 2, 5, 7, 6],
        "clebsch_frobenius_norm_squared": float(np.sum(np.abs(clebsch) ** 2)),
        "clebsch_expected_norm_squared": expected_clebsch_norm,
        "vertex_hermitian_residual": hermitian_residual(vertex),
        "independent_nonzero_vertex_entries": nonzero_upper,
        "expected_nonzero_entries": 4 * int(np.count_nonzero(np.abs(clebsch) > 1.0e-14)),
        "positive_host_metric_min_eigenvalue": minimum_eigenvalue(z64),
        "full_kernel_finite": bool(np.isfinite(g00).all()),
        "current_nonzero_entries": int(np.count_nonzero(np.abs(current) > 1.0e-14)),
        "expected_current_nonzero_entries": 16,
        "representative_full_W_eff": [float(weff.real), float(weff.imag)],
        "deterministic_admissible_tensor_trials": random_trials,
    }


def retained_v49_action_contract() -> dict[str, Any]:
    return {
        "order": "tree level through O(Lambda^-1), with O(E^2/Lambda^2) plus loops as remainder",
        "bulk": "V47 four hypermultiplets and gauge multiplet on the interval",
        "PS_superpotential": {
            "terms": [
                "9 Q_i H Qc_j",
                "3 Q_i H HRA",
                "3 HLF H Qc_j",
                "HLF H HRA",
                "HLA H HRF",
                "HRAc_L H HLFc_R",
                "HRFc_L H HLAc_R",
                "mu_H epsilon_L epsilon_R H H",
            ],
            "coefficient_count": "19 spinor cubics plus mu_H",
        },
        "PS_quadratic_and_derivative": [
            "positive 4x4 Z_L and Z_R including Q-HLF and Qc-HRA mixing",
            "independent positive metrics for HLA,HRF and four complementary even Hc traces",
            "O7/O8 covariant normal-derivative graph coefficients",
            "Q_i nabla5(HLFc) and Qc_i nabla5(HRAc) current coefficients",
            "constant PS gauge kinetic, U1F FI and broken-sector Zhat^2 coefficients",
        ],
        "source": [
            "all V48 renormalizable source terms and four H-H portals",
            "all twelve degree-four two-H portal contractions",
            "four conjugate Hc-Hc portals in the finite collar",
            "source-dependent H-Hc and mixed Kahler matrices represented in the source pencil",
            "constant/source-dependent Spin10 and U1F gauge kinetic terms and source FI coefficient",
        ],
        "pure_source_quartics": {
            "definition": "B4_source=Hom_(Spin10 x U1F)(1, Sym^4 R_source), with one coefficient per independent invariant tensor",
            "examples": [
                "S^4",
                "S^2 ThetaPlus ThetaMinus",
                "(ThetaPlus ThetaMinus)^2",
                "S^2 Phi^2",
                "S Phi^3",
                "S Phi Sigma barSigma",
                "all independent Phi^4, Phi^2 Sigma barSigma and (Sigma barSigma)^2 contractions",
            ],
            "status": "complete abstract invariant-space parameterization; multiplicities and normalized SO10 tensors not enumerated",
        },
        "matrix_absorption": {
            "host": "P0(m)=M0-mZ0-C0^dag(H0-mW0)^-1 C0",
            "source": "PL(m)=ML-mZL-CL^dag(HL-mWL)^-1 CL",
            "normal_derivative": "A_rel b+B_rel a=0 is admitted when A_rel invertible and A_rel^-1 B_rel Hermitian",
            "restricted_action_kernel": "Gamma_HH=K(P_L)+N(P_L)P0; G00=Gamma_HH^-1 N for the encoded zero-Hc-counterterm collar",
            "light_Schur_complement": "Gamma_eff=Gamma_LL-Gamma_LH Gamma_HH^-1 Gamma_HL",
            "strong_collar_limit": "generic Hc-Hc and odd-profile H-Hc coefficients enter the path-ordered collar generator at O(1), so they cannot be represented only as an appended endpoint pencil",
        },
    }


def build_report() -> dict[str, Any]:
    representative = representative_certificate()
    components = full_component_certificate()
    action = retained_v49_action_contract()

    checks = {
        "positive_direct_and_auxiliary_metrics": all(
            value > 0.0 for value in representative["metric_checks"].values()
        ),
        "real_mass_pencils_are_hermitian": max(
            representative["self_adjoint_checks"]["host_pencil_hermitian_at_real_m"],
            representative["self_adjoint_checks"]["source_pencil_hermitian_at_real_m"],
        ) < 1.0e-12,
        "collar_is_J_unitary": representative["self_adjoint_checks"]["collar_J_unitary_at_zero"] < 1.0e-12,
        "three_generalized_roots_found": len(representative["roots_and_residue"]["first_three_positive_roots"]) == 3,
        "first_generalized_root_is_simple": abs(representative["roots_and_residue"]["first_derivative"]) > 1.0e-4,
        "generalized_residue_matches": representative["roots_and_residue"]["near_pole_residue_residual"] < 5.0e-6,
        "generalized_kernel_is_euclidean_local": representative["euclidean_locality"]["norm8_over_norm4"] < 0.04,
        "collar_remainder_is_quadratic": representative["collar_linear_remainder"]["normalized_by_m2_epsilon2"] < 2.0,
        "positive_auxiliary_states_decouple": representative["auxiliary_decoupling"]["monotone"]
        and representative["auxiliary_decoupling"]["norm16_over_norm8"] < 0.6,
        "full_64_vertex_is_hermitian": components["vertex_hermitian_residual"] < 1.0e-12,
        "full_64_clebsch_completeness_norm": abs(
            components["clebsch_frobenius_norm_squared"] - components["clebsch_expected_norm_squared"]
        ) < 1.0e-12,
        "all_four_full_component_vertices_present": components["independent_nonzero_vertex_entries"] == components["expected_nonzero_entries"],
        "full_component_current_has_expected_support": components["current_nonzero_entries"] == components["expected_current_nonzero_entries"],
        "full_64_kernel_is_finite": components["full_kernel_finite"],
        "random_admissible_tensor_trials_pass": all(
            row["kinetic_min_eigenvalue"] > 0.0
            and row["host_hermitian_residual"] < 1.0e-12
            and row["kernel_finite"]
            for row in components["deterministic_admissible_tensor_trials"]
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V49 generalized-pencil integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v49-generalized-boundary-pencil-audit-v1",
        "status": STATUS,
        "retained_action_contract": action,
        "positivity_and_self_adjointness_theorem": {
            "sufficient_conditions": [
                "bulk and finite collar have positive canonical metric and J-unitary real-m transfer",
                "direct boundary kinetic matrices Z0,ZL are positive semidefinite",
                "every retained auxiliary boundary metric W0,WL is positive definite and its Hamiltonian is Hermitian",
                "M0,ML and every real-m graph pencil are Hermitian",
                "normal-derivative relations have full rank and define a Hermitian graph A_rel^-1 B_rel in the retained chart",
                "all poles of eliminated auxiliary resolvents are retained in the enlarged determinant",
            ],
            "positive_derivative_identity": "-dP/dm=Z+C^dag(H-mW)^-1 W(H-mW)^-1 C >=0 between auxiliary poles",
            "consequence": "the enlarged generalized eigenproblem is self-adjoint in its positive bulk+boundary metric; signed masses are real and unbroken-SUSY scalar mass squares are nonnegative",
            "not_necessary": "these are sufficient conditions, not a classification of every self-adjoint boundary relation",
        },
        "generalized_kernel": {
            "outer_source_pencil": "g_out+P_L(m) f_out=0",
            "collar_composition": "Cf=C+P_L D, Cg=D+P_L U",
            "bulk_composition": "K=Cf R+Cg Q, N=Cf P+Cg T",
            "host_relation": "b=J0+P0(m)a",
            "heavy_pencil": "Gamma_HH=K+N P0",
            "host_response": "G00=Gamma_HH^-1 N",
            "full_light_action": "Gamma_eff=Gamma_LL-Gamma_LH Gamma_HH^-1 Gamma_HL",
            "pole_rule": "use the undivided enlarged determinant, including collar D and auxiliary det(H-mW) factors; a divided rational pencil may hide physical wall states",
        },
        "representative_generalized_certificate": representative,
        "full_64_PS_component_certificate": components,
        "C1_to_C7_assessment": {
            "C1": "FAIL: mu_H, Hc portals and derivative coordinates are named and pure-source quartics are parameterized abstractly, but independent multiplicities/tensors and the complete strong-collar action are not enumerated",
            "C2": "CONDITIONAL: the square H/Hc transfer is explicit at a restricted point, but its source coupling is a finite-range Wilson-line bilocal rather than a point-local microscopic 5D regulator",
            "C3": "PARTIAL: the passive endpoint pencils give a positive-metric self-adjoint enlargement, but the allowed O(1) Hc-Hc and odd-profile terms have not been varied into one complete collar generator",
            "C4": "PARTIAL: direct and auxiliary endpoint metrics and -dP/dm are positive in executable witnesses, but positivity of the complete strong-collar action with all allowed Hc blocks is unproved",
            "C5": "PARTIAL: all counterterm types fit named pencil coordinates at mu=Lambda, but a second-profile rematching and loop subtraction calculation are absent",
            "C6": "PARTIAL: the fixed-order policy is explicit, but zero Hc-Hc and odd-profile finite parts define a matching point rather than symmetry-protected omissions and must be rematched",
            "C7": "PARTIAL: the 64 PS trace/Higgs/current map is executable for the restricted collar and universal admissible tensors are tested, but the O(1) Hc collar blocks, normalized SO10 tensors and derivative-current Clebsches remain absent",
        },
        "G2_decision": {
            "closed": False,
            "closed_gate_count": 1,
            "verdict": "G2_REMAINS_OPEN",
            "precise_remaining_objects": [
                "enumerate multiplicities and normalized projectors for B4_source=Hom_G(1,Sym4 R_source)",
                "supply normalized SO10-to-PS component tensors for all degree-four source portals and H/Hc derivative currents",
                "derive the named O7/O8 and brane-bulk derivative graph blocks by varying one explicit superspace action",
                "insert every allowed Hc-Hc and odd-profile H-Hc block into the path-ordered strong-collar generator and recompute its transfer",
                "perform one independent collar-profile rematch, including local counterterms, and show agreement through O(Lambda^-1)",
                "publish the complete same-action Wilson coefficient array rather than universal placeholder tensor inputs",
            ],
            "why_formal_absorption_is_not_closure": "A matrix pencil proves that encoded endpoint blocks propagate consistently; it neither supplies normalized physical invariant tensors nor replaces O(1) interactions that live inside the strong collar generator.",
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "primary_sources": [
            "https://arxiv.org/abs/hep-th/0106256",
            "https://arxiv.org/abs/hep-ph/0112230",
            "https://arxiv.org/abs/hep-th/0411133",
            "https://arxiv.org/abs/hep-ph/0601222",
            "https://arxiv.org/abs/hep-th/0109116",
            "https://arxiv.org/abs/1408.1852",
        ],
        "source_manifest": [
            {"path": path.name, "sha256": sha256_file(path)} for path in UPSTREAM
        ]
        + [{"path": TEST_PATH.name, "sha256": sha256_file(TEST_PATH) if TEST_PATH.is_file() else None}],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    cert = report["representative_generalized_certificate"]
    comp = report["full_64_PS_component_certificate"]
    clauses = report["C1_to_C7_assessment"]
    clause_rows = "\n".join(f"| {key} | {value} |" for key, value in clauses.items())
    remaining = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(report["G2_decision"]["precise_remaining_objects"], 1)
    )
    return f"""# V49 generalized restricted-action boundary pencil audit

Status: `{report['status']}`

## Verdict

V49 supplies a generalized boundary pencil capable of carrying every named
endpoint Kähler, derivative, counterterm and portal block through the
restricted finite-collar calculation.  It also replaces the V48
eight-coordinate witness by an executable 64-coordinate PS trace map with all
four H/Hc Higgs vertices and the six one-bulk family currents.

This is a substantial C3/C4/C7 advance, but **G2 remains open**.  The full
SO(10) quartic invariant multiplicities and normalized component tensors, the
normal-derivative superspace variation, the generic strong-collar Hc
generator, and a second-profile counterterm rematch are still absent.  A
universal matrix slot is neither a normalized physical Clebsch coefficient
nor a replacement for an interaction inside the collar.

## Restricted-action pencil

At each wall retain a passive Hermitian pencil

`P(m)=M-m Z-C^dagger(H-m W)^-1 C`,

with `Z>=0`, `W>0`, and Hermitian `M,H`.  It obeys

`-dP/dm=Z+C^dagger(H-mW)^-1 W(H-mW)^-1 C>=0`

between auxiliary poles.  The auxiliary states are part of the enlarged
positive Hilbert space; their determinant factors are never divided away.
Normal-derivative relations `A_rel b+B_rel a=0` enter this graph chart when
`A_rel` is invertible and `A_rel^-1 B_rel` is Hermitian.

For the V48 collar,

`Cf=C+P_L D`, `Cg=D+P_L U`,

`K=Cf R+Cg Q`, `N=Cf P+Cg T`.

With the PS relation `b=J0+P0 a`, the exact restricted-action heavy and Wilson
kernels are

`Gamma_HH=K+N P0`, `G00=Gamma_HH^-1 N`,

and the complete light Schur complement is

`Gamma_eff=Gamma_LL-Gamma_LH Gamma_HH^-1 Gamma_HL`.

The executable positive witness finds signed roots
`{cert['roots_and_residue']['first_three_positive_roots']}`.  Its first-pole
residue error is `{cert['roots_and_residue']['near_pole_residue_residual']:.3e}`;
the Euclidean norm ratio between `p=8` and `p=4` is
`{cert['euclidean_locality']['norm8_over_norm4']:.6g}`.  Scaling the positive
auxiliary Hamiltonian from eight to sixteen reduces its Schur correction by a
factor `{cert['auxiliary_decoupling']['norm16_over_norm8']:.6g}`.

## Full PS component map

The boundary vector has {comp['coordinate_count']} coordinates: sixteen V47
internal components times `(HLF,HLA,HRA,HRF)`.  In a declared epsilon-tensor
convention the bidoublet map is four repeated 2x2 blocks.  The four vertices
are `A_L-C_R`, `B_L-D_R`, `HRAc_L-HLFc_R`, and
`HRFc_L-HLAc_R`.

The executable map has {comp['independent_nonzero_vertex_entries']} independent
nonzero entries, exactly its expected count.  Its Clebsch norm completeness
identity and Hermiticity pass.  The physical family current has
{comp['current_nonzero_entries']} nonzero component entries, and three
deterministic positive-metric 64x64 counterterm trials give finite kernels.

The action contract now explicitly admits `mu_H H H`, O7/O8 graph
coefficients, `Q nabla5(HLFc)`, `Qc nabla5(HRAc)`, four conjugate Hc source
portals, mixed source Kähler blocks, both FI coordinates, all boundary gauge
terms, and the abstract full pure-source quartic invariant space.  Vacuum
selection from those quartics remains G3; their presence in the action is G2.
However, the executable transfer sets the Hc-Hc and odd-profile mixed finite
parts to zero.  In the strong `Lambda/epsilon` collar they are generically
`O(1)` and must be inserted into the path-ordered generator, so the contract
and executable kernel are not yet the same complete action.

## Clause decision

| Clause | V49 result |
|---|---|
{clause_rows}

## Exact remaining G2 work

{remaining}

The formal pencil is therefore not used to overrule the missing physical
tensors or strong-collar blocks.  G1 remains the only closed gate, so the
total is **1/8**.

Primary references: [Marti--Pomarol](https://arxiv.org/abs/hep-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230),
[von Gersdorff et al.](https://arxiv.org/abs/hep-th/0411133),
[del Aguila--Perez-Victoria--Santiago](https://arxiv.org/abs/hep-ph/0601222),
[Nath--Syed](https://arxiv.org/abs/hep-th/0109116), and
[Barcelo--Mitra--Moreau](https://arxiv.org/abs/1408.1852).

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError("V49 generalized-pencil JSON missing or stale; run --write")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError("V49 generalized-pencil Markdown missing or stale; run --write")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        print(write_artifacts()["status"])
    if args.check:
        check_artifacts()
        print("V49_GENERALIZED_BOUNDARY_PENCIL_AUDIT_CHECK_PASS")
    if not args.write and not args.check:
        print(json.dumps(build_report(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
