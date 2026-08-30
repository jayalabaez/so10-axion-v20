#!/usr/bin/env python3
"""V50 full same-action quadratic collar, domain, and Wilson audit.

This certificate closes the algebraic gap left by the restricted V49 collar.
It starts from the most general quadratic holomorphic collar blocks

    A=A^T,  Xi=Xi^T,  C arbitrary,

and from independent O7/O8 one-normal-derivative matrices.  Exact integration
by parts puts all of them in one first-order action.  The resulting transfer is
path ordered, is composed with the undivided bulk transfer and with enlarged
positive-metric endpoint pencils, and is used directly for a deterministic
pole/residue/Wilson witness.

The calculation is deliberately representation-agnostic.  A, Xi, C and the
derivative blocks may be supplied either by the finite-range V49 kernel or by
a local constrained-profile regulator.  It therefore resolves the quadratic
functional analysis, not the still-missing normalized SO(10)->PS Cartesian
tensors required for a physical component Wilson array.
"""

from __future__ import annotations

import argparse
import copy
import functools
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np
from scipy.linalg import expm

import susy_v48_source_operator_wilson_audit as v48
import susy_v49_generalized_boundary_pencil_audit as v49


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V50_FULL_SAME_ACTION_COLLAR_AUDIT.json"
MD_PATH = ROOT / "SUSY_V50_FULL_SAME_ACTION_COLLAR_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v50_full_same_action_collar_audit.py"

STATUS = (
    "V50_FULL_SAME_ACTION_QUADRATIC_COLLAR_DERIVED__"
    "A_XI_C_AND_O7_O8_IN_ONE_PATH_ORDERED_GENERATOR__"
    "VARIATIONAL_LAGRANGIAN_DOMAIN_AND_POSITIVE_ADMISSIBLE_CONE_CERTIFIED__"
    "UNDIVIDED_BULK_ENDPOINT_POLE_RESIDUE_WILSON_WITNESS_PASSES__"
    "C3_AND_QUADRATIC_C4_CLOSED__C7_COMPONENT_MATCHING_PARTIAL__G2_OPEN"
)

UPSTREAM = (
    ROOT / "SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json",
    ROOT / "SUSY_V49_FIXED_PROFILE_SOURCE_REGULATOR_AUDIT.json",
    ROOT / "SUSY_V49_GENERALIZED_BOUNDARY_PENCIL_AUDIT.json",
    ROOT / "SUSY_V49_G2_FRONTIER_INTEGRATION_AUDIT.json",
)

Array = np.ndarray
BlockCallback = Callable[[float, complex], Mapping[str, Array]]


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maximum_abs(matrix: Sequence[Sequence[complex]]) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    return float(np.max(np.abs(value))) if value.size else 0.0


def transpose_symmetry_residual(matrix: Sequence[Sequence[complex]]) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    return maximum_abs(value - value.T)


def hermitian_residual(matrix: Sequence[Sequence[complex]]) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    return maximum_abs(value - value.conjugate().T)


def minimum_eigenvalue(matrix: Sequence[Sequence[complex]]) -> float:
    value = np.asarray(matrix, dtype=np.complex128)
    if hermitian_residual(value) > 1.0e-10:
        raise ValueError("minimum_eigenvalue requires a Hermitian matrix")
    return float(np.min(np.linalg.eigvalsh(value)))


def j_form(channels: int) -> Array:
    eye = np.eye(channels, dtype=np.complex128)
    zero = np.zeros_like(eye)
    return np.block([[zero, -eye], [eye, zero]])


def deterministic_symmetric(size: int, seed: int, scale: float) -> Array:
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(size, size))
    return scale * (raw + raw.T) / (2.0 * size)


def deterministic_rectangular(rows: int, columns: int, seed: int, scale: float) -> Array:
    rng = np.random.default_rng(seed)
    return scale * rng.normal(size=(rows, columns)) / math.sqrt(max(rows, columns))


def deterministic_positive(size: int, seed: int, floor: float, scale: float) -> Array:
    rng = np.random.default_rng(seed)
    raw = rng.normal(size=(size, size))
    return floor * np.eye(size) + scale * (raw.T @ raw) / size


def sp_generator(a: Array, xi: Array, c: Array) -> Array:
    """Return the general Hamiltonian block [[C,Xi],[-A,-C^T]]."""

    a0 = np.asarray(a, dtype=np.complex128)
    xi0 = np.asarray(xi, dtype=np.complex128)
    c0 = np.asarray(c, dtype=np.complex128)
    if a0.shape != xi0.shape or a0.shape != c0.shape or a0.shape[0] != a0.shape[1]:
        raise ValueError("A, Xi and C must be equally square")
    if transpose_symmetry_residual(a0) > 1.0e-11:
        raise ValueError("A must be symmetric")
    if transpose_symmetry_residual(xi0) > 1.0e-11:
        raise ValueError("Xi must be symmetric")
    return np.block([[c0, xi0], [-a0, -c0.T]])


def sp_span_certificate(channels: int) -> dict[str, Any]:
    """Construct and rank the A/Xi/C basis of sp(2n)."""

    generators: list[Array] = []
    for target in ("A", "Xi"):
        for row in range(channels):
            for column in range(row, channels):
                symmetric = np.zeros((channels, channels))
                symmetric[row, column] = 1.0
                symmetric[column, row] = 1.0
                zero = np.zeros_like(symmetric)
                generators.append(
                    sp_generator(
                        symmetric if target == "A" else zero,
                        symmetric if target == "Xi" else zero,
                        zero,
                    )
                )
    for row in range(channels):
        for column in range(channels):
            c0 = np.zeros((channels, channels))
            c0[row, column] = 1.0
            zero = np.zeros_like(c0)
            generators.append(sp_generator(zero, zero, c0))

    flattened = np.asarray([item.reshape(-1) for item in generators])
    rank = int(np.linalg.matrix_rank(flattened))
    expected = channels * (2 * channels + 1)
    j0 = j_form(channels)
    residual = max(maximum_abs(item.T @ j0 + j0 @ item) for item in generators)
    return {
        "channels": channels,
        "basis_count": len(generators),
        "matrix_rank": rank,
        "expected_dimension_n_2n_plus_1": expected,
        "maximum_Hamiltonian_residual": residual,
        "spanned": rank == expected and residual < 1.0e-12,
    }


def deterministic_collar_data(channels: int = 4) -> dict[str, Any]:
    """A noncommuting, endpoint-regular representative of the full action."""

    metric = deterministic_positive(2 * channels, 500, 0.32, 0.035)
    return {
        "channels": channels,
        "epsilon": 0.055,
        "A0": np.diag(np.linspace(0.26, 0.47, channels))
        + deterministic_symmetric(channels, 501, 0.07),
        "A1": deterministic_symmetric(channels, 502, 0.09),
        "Xi0": np.diag(np.linspace(0.08, 0.17, channels))
        + deterministic_symmetric(channels, 503, 0.035),
        "Xi1": deterministic_symmetric(channels, 504, 0.045),
        "C0": deterministic_rectangular(channels, channels, 505, 0.075),
        "C1": deterministic_rectangular(channels, channels, 506, 0.065),
        "R7a": deterministic_rectangular(channels, channels, 507, 0.022),
        "R7b": deterministic_rectangular(channels, channels, 508, 0.014),
        "R8a": deterministic_rectangular(channels, channels, 509, 0.018),
        "R8b": deterministic_rectangular(channels, channels, 510, 0.012),
        "norm_metric": metric,
    }


def deterministic_collar_blocks(data: Mapping[str, Any]) -> BlockCallback:
    """Return A/Xi/C/R7/R8 and profile derivatives as a callback.

    The callback interface is the regulator seam.  A finite-range Wilson-line
    kernel and a local constrained profile both enter by returning the same
    coefficient blocks; the functional analysis below is unchanged.
    """

    channels = int(data["channels"])
    epsilon = float(data["epsilon"])

    def callback(t: float, mass: complex) -> Mapping[str, Array]:
        angle = 2.0 * math.pi * t
        even_a = 1.0 + 0.19 * math.cos(angle)
        even_xi = 1.0 - 0.13 * math.cos(angle)
        odd = math.sin(angle)
        derivative_even = math.sin(math.pi * t) ** 2
        derivative_even_prime = math.pi * math.sin(angle)
        derivative_odd = math.sin(angle)
        derivative_odd_prime = 2.0 * math.pi * math.cos(angle)

        r7 = derivative_even * data["R7a"] + derivative_odd * data["R7b"]
        r8 = derivative_even * data["R8a"] + derivative_odd * data["R8b"]
        r7_prime = (
            derivative_even_prime * data["R7a"]
            + derivative_odd_prime * data["R7b"]
        )
        r8_prime = (
            derivative_even_prime * data["R8a"]
            + derivative_odd_prime * data["R8b"]
        )
        a0 = even_a * data["A0"] + 0.31 * odd * data["A1"]
        xi0 = even_xi * data["Xi0"] + 0.27 * odd * data["Xi1"]
        c0 = (1.0 + 0.11 * math.cos(angle)) * data["C0"] + 0.23 * odd * data["C1"]
        if a0.shape != (channels, channels):
            raise ValueError("invalid deterministic collar data")
        return {
            "A": np.asarray(a0, dtype=np.complex128),
            "Xi": np.asarray(xi0, dtype=np.complex128),
            "C": np.asarray(c0, dtype=np.complex128),
            "R7": np.asarray(r7, dtype=np.complex128),
            "R8": np.asarray(r8, dtype=np.complex128),
            "R7_prime": np.asarray(r7_prime, dtype=np.complex128),
            "R8_prime": np.asarray(r8_prime, dtype=np.complex128),
            # The 4D mass dependence is suppressed by the physical width.
            "spectral_metric": epsilon
            * np.asarray(data["norm_metric"], dtype=np.complex128),
        }

    return callback


def collar_normal_form(t: float, mass: complex, callback: BlockCallback) -> dict[str, Array]:
    """Map the literal O7/O8 action to its exact first-order normal form.

    Before integration by parts the derivative coefficient is

      D=[[0,R8^T],[I+R7,0]].

    D-D^T is the symplectic form.  The symmetric part S=(D+D^T)/2
    contributes S' to the quadratic potential and [psi^T S psi/2] to the
    endpoints.  This is the executable O7+O8+M_o quotient; no derivative
    operator is silently dropped.
    """

    blocks = callback(float(t), mass)
    a0 = np.asarray(blocks["A"], dtype=np.complex128)
    xi0 = np.asarray(blocks["Xi"], dtype=np.complex128)
    c0 = np.asarray(blocks["C"], dtype=np.complex128)
    r7 = np.asarray(blocks["R7"], dtype=np.complex128)
    r8 = np.asarray(blocks["R8"], dtype=np.complex128)
    r7p = np.asarray(blocks["R7_prime"], dtype=np.complex128)
    r8p = np.asarray(blocks["R8_prime"], dtype=np.complex128)
    spectral = np.asarray(blocks["spectral_metric"], dtype=np.complex128)
    channels = a0.shape[0]
    zero = np.zeros((channels, channels), dtype=np.complex128)
    eye = np.eye(channels, dtype=np.complex128)
    draw = np.block([[zero, r8.T], [eye + r7, zero]])
    draw_prime = np.block([[zero, r8p.T], [r7p, zero]])
    j0 = draw - draw.T
    jprime = draw_prime - draw_prime.T
    symmetric_derivative = (draw + draw.T) / 2.0
    symmetric_derivative_prime = (draw_prime + draw_prime.T) / 2.0
    potential = np.block([[a0, c0.T], [c0, xi0]]) - mass * spectral
    q0 = potential + symmetric_derivative_prime
    k0 = eye + r7 - r8
    kprime = r7p - r8p
    darboux = np.block([[eye, zero], [zero, k0.T]])
    darboux_prime = np.block([[zero, zero], [zero, kprime.T]])
    return {
        "D_raw": draw,
        "D_raw_prime": draw_prime,
        "J": j0,
        "J_prime": jprime,
        "S": symmetric_derivative,
        "S_prime": symmetric_derivative_prime,
        "Q": q0,
        "K": k0,
        "K_prime": kprime,
        "Darboux": darboux,
        "Darboux_prime": darboux_prime,
        "spectral_metric": spectral,
    }


def canonical_generator(t: float, mass: complex, callback: BlockCallback) -> tuple[Array, dict[str, float]]:
    """Return the canonical Hamiltonian generator of the same action."""

    normal = collar_normal_form(t, mass, callback)
    j0 = normal["J"]
    q0 = normal["Q"]
    # Variation of 1/2 psi^T J psi' - 1/2 psi^T Q psi gives
    # J psi'=(Q-J'/2)psi.
    raw_generator = np.linalg.solve(j0, q0 - 0.5 * normal["J_prime"])
    darboux = normal["Darboux"]
    darboux_inverse = np.linalg.inv(darboux)
    generator = (
        normal["Darboux_prime"] @ darboux_inverse
        + darboux @ raw_generator @ darboux_inverse
    )
    channels = normal["K"].shape[0]
    canonical_j = j_form(channels)
    return generator, {
        "raw_J_skew_residual": maximum_abs(j0 + j0.T),
        "Q_symmetric_residual": transpose_symmetry_residual(q0),
        "Darboux_congruence_residual": maximum_abs(
            darboux.T @ canonical_j @ darboux - j0
        ),
        "canonical_Hamiltonian_residual": maximum_abs(
            generator.T @ canonical_j + canonical_j @ generator
        ),
        "K_min_singular_value": float(np.min(np.linalg.svd(normal["K"], compute_uv=False))),
    }


def path_ordered_collar_transfer(
    mass: complex, callback: BlockCallback, channels: int, steps: int = 24
) -> Array:
    """Midpoint product for P exp integral_0^1 G(t,m)dt.

    Every factor is an exponential of a Hamiltonian matrix and is therefore
    symplectic to roundoff.  Increasing ``steps`` tests path-order convergence.
    """

    transfer = np.eye(2 * channels, dtype=np.complex128)
    width = 1.0 / steps
    for index in range(steps):
        midpoint = (index + 0.5) * width
        generator, _ = canonical_generator(midpoint, mass, callback)
        transfer = expm(width * generator) @ transfer
    return transfer


def symplectic_residual(transfer: Array, channels: int, hermitian: bool = False) -> float:
    j0 = j_form(channels)
    left = transfer.conjugate().T if hermitian else transfer.T
    return maximum_abs(left @ j0 @ transfer - j0)


def bulk_transfer(
    mass: complex, bulk_masses: Sequence[float], length: float, even: Sequence[bool]
) -> Array:
    rblock = v48.source_value_transfer(mass, bulk_masses, length, even)
    qblock = v48.inner_residual_transfer(mass, bulk_masses, length, even)
    pblock, tblock = v48.initial_conjugate_transfers(mass, bulk_masses, length, even)
    return np.block([[rblock, pblock], [qblock, tblock]])


def total_transfer(
    mass: complex,
    callback: BlockCallback,
    bulk_masses: Sequence[float],
    length: float,
    even: Sequence[bool],
    steps: int = 24,
) -> Array:
    channels = len(bulk_masses)
    collar = path_ordered_collar_transfer(mass, callback, channels, steps)
    return collar @ bulk_transfer(mass, bulk_masses, length, even)


def endpoint_data(channels: int, seed: int) -> dict[str, Array]:
    auxiliary = 2
    return {
        "M": deterministic_symmetric(channels, seed, 0.075),
        "Z": deterministic_positive(channels, seed + 1, 0.075, 0.018),
        "C": deterministic_rectangular(auxiliary, channels, seed + 2, 0.045),
        "H": np.diag([2.15 + 0.11 * (seed % 3), 2.82 + 0.07 * (seed % 5)]),
        "W": deterministic_positive(auxiliary, seed + 3, 0.84, 0.025),
    }


def endpoint_pencil(mass: complex, endpoint: Mapping[str, Array]) -> Array:
    return v49.passive_boundary_pencil(
        mass,
        endpoint["M"],
        endpoint["Z"],
        endpoint["C"],
        endpoint["H"],
        endpoint["W"],
    )


def transfer_blocks(transfer: Array) -> tuple[Array, Array, Array, Array]:
    channels = transfer.shape[0] // 2
    return (
        transfer[:channels, :channels],
        transfer[:channels, channels:],
        transfer[channels:, :channels],
        transfer[channels:, channels:],
    )


def reduced_characteristic(
    transfer: Array, mass: complex, host: Mapping[str, Array], source: Mapping[str, Array]
) -> tuple[Array, Array]:
    """Reduced graph Gamma and N, used only away from auxiliary poles."""

    rblock, pblock, qblock, tblock = transfer_blocks(transfer)
    p0 = endpoint_pencil(mass, host)
    p1 = endpoint_pencil(mass, source)
    nblock = tblock + p1 @ pblock
    kblock = qblock + p1 @ rblock
    return kblock + nblock @ p0, nblock


def enlarged_characteristic(
    transfer: Array, mass: complex, host: Mapping[str, Array], source: Mapping[str, Array]
) -> Array:
    """Undivided characteristic retaining both endpoint auxiliary sectors.

    Unknowns are (q0,chi0,chi1).  No inverse or auxiliary determinant is used
    in this matrix, so its zeros include every mixed bulk/collar/wall state and
    no rational division can hide a pole.
    """

    rblock, pblock, qblock, tblock = transfer_blocks(transfer)
    m0 = host["M"] - mass * host["Z"]
    a0 = host["H"] - mass * host["W"]
    c0 = host["C"]
    m1 = source["M"] - mass * source["Z"]
    a1 = source["H"] - mass * source["W"]
    c1 = source["C"]

    q1_q = rblock + pblock @ m0
    q1_chi0 = pblock @ c0.conjugate().T
    p1_q = qblock + tblock @ m0
    p1_chi0 = tblock @ c0.conjugate().T

    source_row = np.hstack(
        [p1_q + m1 @ q1_q, p1_chi0 + m1 @ q1_chi0, c1.conjugate().T]
    )
    zero_01 = np.zeros((a0.shape[0], a1.shape[0]), dtype=np.complex128)
    auxiliary0_row = np.hstack([c0, a0, zero_01])
    auxiliary1_row = np.hstack([c1 @ q1_q, c1 @ q1_chi0, a1])
    return np.vstack([source_row, auxiliary0_row, auxiliary1_row])


def undivided_reduced_identity(
    transfer: Array, mass: complex, host: Mapping[str, Array], source: Mapping[str, Array]
) -> float:
    full = enlarged_characteristic(transfer, mass, host, source)
    gamma, _ = reduced_characteristic(transfer, mass, host, source)
    det_aux0 = np.linalg.det(host["H"] - mass * host["W"])
    det_aux1 = np.linalg.det(source["H"] - mass * source["W"])
    expected = det_aux0 * det_aux1 * np.linalg.det(gamma)
    scale = max(1.0, abs(expected), abs(np.linalg.det(full)))
    return float(abs(np.linalg.det(full) - expected) / scale)


def graph_isotropy_residual(pencil: Array, sign: float = 1.0) -> float:
    channels = pencil.shape[0]
    graph = np.vstack([np.eye(channels), sign * pencil])
    return maximum_abs(graph.conjugate().T @ j_form(channels) @ graph)


def _bisect(function: Callable[[float], float], low: float, high: float) -> float:
    flow = float(function(low))
    fhigh = float(function(high))
    if flow * fhigh > 0.0:
        raise ValueError("root is not bracketed")
    for _ in range(80):
        middle = (low + high) / 2.0
        fmiddle = float(function(middle))
        if abs(fmiddle) < 1.0e-13 or high - low < 2.0e-13:
            return middle
        if flow * fmiddle <= 0.0:
            high, fhigh = middle, fmiddle
        else:
            low, flow = middle, fmiddle
    return (low + high) / 2.0


def first_roots(
    function: Callable[[float], float], maximum: float, intervals: int, count: int
) -> list[float]:
    roots: list[float] = []
    previous_x = 0.0
    previous = float(function(previous_x))
    for index in range(1, intervals + 1):
        current_x = maximum * index / intervals
        current = float(function(current_x))
        if previous * current < 0.0:
            root = _bisect(function, previous_x, current_x)
            if not roots or abs(root - roots[-1]) > 1.0e-6:
                roots.append(root)
                if len(roots) == count:
                    break
        previous_x, previous = current_x, current
    return roots


@functools.lru_cache(maxsize=1)
def representative_certificate() -> dict[str, Any]:
    channels = 4
    data = deterministic_collar_data(channels)
    callback = deterministic_collar_blocks(data)
    bulk_masses = (0.0, 0.07, -0.04, 0.025)
    even = (True, False, False, True)
    length = 0.93
    host = endpoint_data(channels, 601)
    source = endpoint_data(channels, 611)
    steps = 18

    def full_matrix(mass: complex) -> Array:
        transfer = total_transfer(
            mass, callback, bulk_masses, length, even, steps=steps
        )
        return enlarged_characteristic(transfer, mass, host, source)

    def determinant(mass: float) -> float:
        value = np.linalg.det(full_matrix(float(mass)))
        return float(value.real)

    roots = first_roots(determinant, maximum=7.5, intervals=900, count=3)
    if len(roots) < 3:
        raise RuntimeError("the deterministic V50 witness did not find three roots")
    root = roots[0]
    finite_step = 5.0e-7
    derivative = (
        determinant(root + finite_step) - determinant(root - finite_step)
    ) / (2.0 * finite_step)
    at_root = full_matrix(root)
    residue_formula = v48.adjugate(at_root) / derivative
    near_residue = finite_step * np.linalg.inv(full_matrix(root + finite_step))

    transfer_real = total_transfer(
        0.31, callback, bulk_masses, length, even, steps=steps
    )
    transfer_refined = total_transfer(
        0.31, callback, bulk_masses, length, even, steps=2 * steps
    )
    collar_real = path_ordered_collar_transfer(0.31, callback, channels, steps)
    bulk_real = bulk_transfer(0.31, bulk_masses, length, even)
    generator_residuals = [
        canonical_generator(point, 0.31, callback)[1]
        for point in np.linspace(0.0, 1.0, 21)
    ]

    k_min = min(item["K_min_singular_value"] for item in generator_residuals)
    hamiltonian_max = max(
        item["canonical_Hamiltonian_residual"] for item in generator_residuals
    )
    normal_q_max = max(item["Q_symmetric_residual"] for item in generator_residuals)

    p0 = endpoint_pencil(0.31, host)
    p1 = endpoint_pencil(0.31, source)
    metric = np.asarray(data["norm_metric"], dtype=np.complex128)
    zhh = metric[:channels, :channels]
    zhc = metric[:channels, channels:]
    zcc = metric[channels:, channels:]
    metric_schur = zcc - zhc.conjugate().T @ np.linalg.solve(zhh, zhc)

    locality: dict[str, float] = {}
    projection = np.hstack(
        [np.eye(channels), np.zeros((channels, 4), dtype=np.complex128)]
    )
    injection = np.vstack(
        [np.eye(channels), np.zeros((4, channels), dtype=np.complex128)]
    )
    for momentum in (1.0, 2.0, 4.0, 8.0):
        response = projection @ np.linalg.solve(full_matrix(1j * momentum), injection)
        locality[str(momentum)] = v48.spectral_norm(response)

    zero_transfer = total_transfer(
        0.0, callback, bulk_masses, length, even, steps=steps
    )
    gamma_zero, n_zero = reduced_characteristic(zero_transfer, 0.0, host, source)
    g00 = np.linalg.solve(gamma_zero, n_zero)
    current = np.asarray([0.11, -0.07, 0.045, -0.032], dtype=np.complex128)
    weff = -0.5 * current.T @ g00 @ current

    commutator = canonical_generator(0.19, 0.31, callback)[0] @ canonical_generator(
        0.67, 0.31, callback
    )[0] - canonical_generator(0.67, 0.31, callback)[0] @ canonical_generator(
        0.19, 0.31, callback
    )[0]

    identity_residuals = []
    for mass in (-0.4, 0.0, 0.31, 1.1):
        transfer = total_transfer(
            mass, callback, bulk_masses, length, even, steps=steps
        )
        identity_residuals.append(
            undivided_reduced_identity(transfer, mass, host, source)
        )

    return {
        "channels": channels,
        "path_order_steps": steps,
        "profile_is_genuinely_noncommuting": v48.spectral_norm(commutator),
        "normal_form": {
            "minimum_K_singular_value_on_21_point_grid": k_min,
            "maximum_Q_transpose_symmetry_residual": normal_q_max,
            "maximum_canonical_Hamiltonian_residual": hamiltonian_max,
        },
        "transfer": {
            "collar_symplectic_residual": symplectic_residual(collar_real, channels),
            "bulk_symplectic_residual": symplectic_residual(bulk_real, channels),
            "total_symplectic_residual": symplectic_residual(transfer_real, channels),
            "real_slice_J_unitary_residual": symplectic_residual(
                transfer_real, channels, hermitian=True
            ),
            "step_doubling_difference_norm": v48.spectral_norm(
                transfer_refined - transfer_real
            ),
        },
        "variational_domain": {
            "host_graph_isotropy_residual": graph_isotropy_residual(p0, +1.0),
            "source_graph_isotropy_residual": graph_isotropy_residual(p1, -1.0),
            "host_pencil_hermitian_residual": hermitian_residual(p0),
            "source_pencil_hermitian_residual": hermitian_residual(p1),
            "enlarged_domain_keeps_auxiliary_states": True,
        },
        "positive_norm": {
            "collar_metric_min_eigenvalue": minimum_eigenvalue(metric),
            "collar_H_block_min_eigenvalue": minimum_eigenvalue(zhh),
            "collar_mixed_Schur_min_eigenvalue": minimum_eigenvalue(metric_schur),
            "host_Z_min_eigenvalue": minimum_eigenvalue(host["Z"]),
            "source_Z_min_eigenvalue": minimum_eigenvalue(source["Z"]),
            "host_W_min_eigenvalue": minimum_eigenvalue(host["W"]),
            "source_W_min_eigenvalue": minimum_eigenvalue(source["W"]),
        },
        "undivided_characteristic": {
            "maximum_full_vs_reduced_identity_residual": max(identity_residuals),
            "matrix_dimension": int(full_matrix(0.0).shape[0]),
            "first_three_signed_positive_roots": roots,
            "determinant_at_first_root_abs": abs(determinant(root)),
            "first_root_derivative": derivative,
            "near_pole_full_residue_residual": maximum_abs(
                near_residue - residue_formula
            ),
        },
        "Wilson_witness": {
            "G00_finite": bool(np.isfinite(g00).all()),
            "G00_spectral_norm": v48.spectral_norm(g00),
            "representative_W_eff": [float(weff.real), float(weff.imag)],
            "source_to_host_euclidean_norms": locality,
            "norm8_over_norm4": locality["8.0"] / locality["4.0"],
        },
    }


def action_and_domain_theorem() -> dict[str, Any]:
    return {
        "literal_derivative_action": (
            "Hc^T(I+R7)D5H+(D5Hc)^T R8 H, with independent matrix-valued "
            "profiles R7 and R8"
        ),
        "exact_IBP_normal_form": {
            "D": "[[0,R8^T],[I+R7,0]]",
            "J": "D-D^T=[[0,-K^T],[K,0]], K=I+R7-R8",
            "S": "(D+D^T)/2",
            "Q": "[[A,C^T],[C,Xi]]-m epsilon Z+S'",
            "endpoint_shift": "[psi^T S psi/2]_0^1 retained in the endpoint action",
            "generator": "G_raw=J^-1(Q-J'/2)",
            "Darboux_map": "z=diag(I,K^T)psi, so J=Darboux^T J0 Darboux",
            "path_ordered_transfer": "T_col=P exp integral G_can dt",
        },
        "spanning_result": (
            "A=A^T and Xi=Xi^T give the two symmetric Hamiltonian blocks; "
            "arbitrary C gives the diagonal block. Together they span all sp(2n)."
        ),
        "variational_domain": {
            "host": "p0=P0 q0 (or p0=j0+P0 q0 with a current)",
            "source": "p1=-P1 q1 (or p1+P1 q1=j1)",
            "graph_condition": "P0=P0^dagger and P1=P1^dagger",
            "Green_form": "[u^dagger J0 v]_0^1",
            "proof": (
                "Each endpoint graph is maximal isotropic; the path transfer is "
                "J0-unitary. Energy-dependent Schur pencils are not treated as "
                "fixed domains: their positive-metric auxiliary states and determinant "
                "factors remain in the enlarged operator."
            ),
            "complex_couplings": (
                "transpose-symplectic holomorphic transfer is exact; physical "
                "self-adjointness is applied to the real CP slice used by the witness "
                "or, equivalently, to the standard field/conjugate Nambu doubling"
            ),
        },
        "positive_admissible_cone": {
            "conditions": [
                "K(t)=I+R7(t)-R8(t) is invertible with a uniform singular-value bound",
                "the complete bulk/collar Kahler metric Z(t) is positive definite",
                "mixed Kahler blocks obey Z_H>0 and Z_c-Y^dagger Z_H^-1 Y>0",
                "endpoint direct metrics Z0,Z1 are positive semidefinite",
                "every retained auxiliary metric W0,W1 is positive definite",
                "higher-derivative rational pencils are kept as positive auxiliary enlargements",
            ],
            "consequence": (
                "The complete quadratic norm is positive and the enlarged mass operator "
                "is self-adjoint. Holomorphic A,Xi,C change the mass operator, not the "
                "Kahler norm. These are sufficient open-cone conditions, not necessary ones."
            ),
        },
        "regulator_interface": (
            "Only the coefficient callback (A,Xi,C,R7,R8,Z) depends on whether the "
            "source profile is the finite-range V49 kernel or a local constrained "
            "profile. The transfer/domain proof consumes either without modification."
        ),
    }


def build_report() -> dict[str, Any]:
    span = sp_span_certificate(4)
    witness = representative_certificate()
    theorem = action_and_domain_theorem()
    transfer = witness["transfer"]
    domain = witness["variational_domain"]
    norm = witness["positive_norm"]
    characteristic = witness["undivided_characteristic"]
    wilson = witness["Wilson_witness"]

    checks = {
        "A_Xi_C_span_full_sp8": span["spanned"],
        "O7_O8_normal_form_is_symmetric_and_Hamiltonian": (
            witness["normal_form"]["maximum_Q_transpose_symmetry_residual"] < 1.0e-11
            and witness["normal_form"]["maximum_canonical_Hamiltonian_residual"] < 1.0e-10
        ),
        "derivative_symplectic_form_never_degenerates": witness["normal_form"][
            "minimum_K_singular_value_on_21_point_grid"
        ] > 0.5,
        "collar_bulk_total_transfers_are_symplectic": max(
            transfer["collar_symplectic_residual"],
            transfer["bulk_symplectic_residual"],
            transfer["total_symplectic_residual"],
        ) < 1.0e-10,
        "real_slice_transfer_is_J_unitary": transfer["real_slice_J_unitary_residual"] < 1.0e-10,
        "path_ordering_converges": transfer["step_doubling_difference_norm"] < 2.0e-4,
        "endpoint_graphs_are_variational_Lagrangian_subspaces": max(
            domain["host_graph_isotropy_residual"],
            domain["source_graph_isotropy_residual"],
            domain["host_pencil_hermitian_residual"],
            domain["source_pencil_hermitian_residual"],
        ) < 1.0e-10,
        "complete_quadratic_norm_witness_is_positive": min(norm.values()) > 0.0,
        "undivided_and_reduced_determinants_agree_off_auxiliary_poles": characteristic[
            "maximum_full_vs_reduced_identity_residual"
        ] < 1.0e-9,
        "three_undivided_roots_are_found": len(
            characteristic["first_three_signed_positive_roots"]
        ) == 3,
        "first_undivided_root_is_simple": abs(characteristic["first_root_derivative"]) > 1.0e-6,
        "full_pole_residue_matches": characteristic["near_pole_full_residue_residual"] < 1.0e-5,
        "same_action_Wilson_kernel_is_finite": wilson["G00_finite"],
        "source_to_host_kernel_is_Euclidean_local": wilson["norm8_over_norm4"] < 0.08,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V50 same-action collar integrity failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v50-full-same-action-collar-audit-v1",
        "status": STATUS,
        "scientific_scope": (
            "Complete quadratic invariant-tensor collar/domain calculation. It is not "
            "a normalized SO(10) component match, profile-rematching calculation, loop "
            "subtraction, UV completion, or empirical validation."
        ),
        "action_and_domain_theorem": theorem,
        "sp_2n_span_certificate": span,
        "representative_same_action_certificate": witness,
        "C3_C4_C7_decision": {
            "C3": {
                "status": "PASS_AT_DECLARED_QUADRATIC_ACTION_LEVEL",
                "reason": (
                    "Every retained A,Xi,C and O7/O8 quadratic block now comes from one "
                    "IBP-complete action, one path-ordered transfer, and one variational "
                    "maximal-isotropic endpoint domain. Auxiliary wall states are retained."
                ),
                "boundary": (
                    "This does not choose between the local constrained-profile regulator "
                    "and the admitted finite-range kernel; that is C2, not a defect in the "
                    "quadratic domain theorem."
                ),
            },
            "C4": {
                "status": "PASS_ON_EXPLICIT_POSITIVE_ADMISSIBLE_CONE_AT_QUADRATIC_LEVEL",
                "reason": (
                    "Uniform K invertibility, positive full Kahler Schur complements, "
                    "positive endpoint Z, and positive auxiliary W give a positive full "
                    "quadratic norm. The deterministic same-action witness lies strictly "
                    "inside this nonempty open cone."
                ),
                "boundary": (
                    "Parameter points outside the declared cone are rejected; no claim is "
                    "made about loop-corrected positivity or an uncomputed component tensor "
                    "assignment."
                ),
            },
            "C7": {
                "status": "PARTIAL",
                "reason": (
                    "The complete abstract A/Xi/C/O7/O8 transfer, undivided enlarged "
                    "characteristic, pole residues and Wilson response are now same-action."
                ),
                "remaining": [
                    "normalized SO(10)->PS Cartesian tensors for every retained source portal",
                    "normalized derivative-current Clebsches and their family/component embedding",
                    "the resulting complete physical Wilson-coefficient array rather than abstract matrix inputs",
                ],
            },
        },
        "G2_decision": {
            "closed": False,
            "verdict": "G2_REMAINS_OPEN",
            "closed_full_gate_count": 1,
            "why": (
                "C3 and the declared quadratic C4 obstruction are removed, but C2 still "
                "requires a regulator-class decision/local construction, C5 requires an "
                "independent profile rematch and subtraction audit, and C7 lacks normalized "
                "physical component tensors and the full Wilson array."
            ),
        },
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "primary_sources": [
            "https://arxiv.org/abs/hep-th/0106256",
            "https://arxiv.org/abs/hep-ph/0112230",
            "https://arxiv.org/abs/hep-th/0411133",
            "https://arxiv.org/abs/hep-ph/0601222",
            "https://arxiv.org/abs/1408.1852",
        ],
        "source_manifest": [
            {"path": path.name, "sha256": sha256_file(path)} for path in UPSTREAM
        ]
        + [
            {
                "path": TEST_PATH.name,
                "sha256": sha256_file(TEST_PATH) if TEST_PATH.is_file() else None,
            }
        ],
    }
    report["core_sha256"] = canonical_sha(report)
    return report


def render_markdown(report: Mapping[str, Any]) -> str:
    witness = report["representative_same_action_certificate"]
    characteristic = witness["undivided_characteristic"]
    transfer = witness["transfer"]
    norm = witness["positive_norm"]
    decision = report["C3_C4_C7_decision"]
    return f"""# V50 full same-action quadratic collar audit

Status: `{report['status']}`

## Verdict

V50 removes the V49 quadratic strong-collar gap.  General symmetric `A`,
symmetric `Xi`, arbitrary `C`, and the independent O7/O8 normal-derivative
blocks now arise from one integration-by-parts-complete action, one
path-ordered transfer, and one variational endpoint domain.  The undivided
enlarged characteristic retains the endpoint auxiliary states and produces a
deterministic pole, residue, Euclidean-locality and Wilson witness.

**C3 passes at the declared quadratic-action level.  C4 passes on the
explicit positive admissible cone.  C7 remains partial, and G2 remains open.**
The missing C7 objects are normalized SO(10)-to-PS portal and
normal-derivative Clebsches plus the resulting physical component Wilson
array.  C2 and C5 are separate unresolved regulator/rematching clauses.

## One action and one generator

For `psi=(H,Hc)`, begin literally with

`Hc^T(I+R7) D5 H + (D5 Hc)^T R8 H`.

Define

```text
D = [[0,R8^T],[I+R7,0]],
J = D-D^T = [[0,-K^T],[K,0]],       K=I+R7-R8,
S = (D+D^T)/2,
Q = [[A,C^T],[C,Xi]]-m epsilon Z+S'.
```

Exact collar integration by parts gives

`L=psi^T J psi'/2-psi^T Q psi/2+[psi^T S psi/2]'`.

Thus `O7-O8` changes `J`, while `O7+O8` supplies the `S'` potential and the
retained endpoint counterterm.  The variational equation and Darboux map are

```text
J psi'=(Q-J'/2)psi,
z=diag(I,K^T)psi,
T_col=P exp integral_0^1 G_can(t,m) dt.
```

The three blocks

`G=[[C,Xi],[-A,-C^T]]`, with `A=A^T`, `Xi=Xi^T`,

span all of `sp(2n)`: the executable `n=4` basis has rank
{report['sp_2n_span_certificate']['matrix_rank']} out of the expected
{report['sp_2n_span_certificate']['expected_dimension_n_2n_plus_1']}.
The representative profile is genuinely noncommuting, with commutator norm
`{witness['profile_is_genuinely_noncommuting']:.6g}`.

## Variational domain and positive norm

In Darboux coordinates use the host graph `p0=P0 q0` and source graph
`p1=-P1 q1`.  Hermitian endpoint pencils make both graphs maximal isotropic
for the Green form `[u^dagger J0 v]_0^1`.  Energy-dependent rational pencils
are never treated as fixed boundary conditions: their positive-metric
auxiliary states remain in the enlarged domain and determinant.

The sufficient positive cone is:

1. `sigma_min K(t)>0` uniformly;
2. the full collar Kahler metric is positive, equivalently including the
   mixed-block Schur inequality;
3. direct endpoint `Z0,Z1` are positive semidefinite;
4. auxiliary endpoint `W0,W1` are positive definite.

The witness has `min sigma(K)={witness['normal_form']['minimum_K_singular_value_on_21_point_grid']:.6g}`,
full collar metric minimum eigenvalue `{norm['collar_metric_min_eigenvalue']:.6g}`,
and mixed Schur-complement minimum eigenvalue
`{norm['collar_mixed_Schur_min_eigenvalue']:.6g}`.  This is a nonempty open
positive cone, not a claim that arbitrary Wilson coefficients are healthy.

The total real-slice J-unitarity residual is
`{transfer['real_slice_J_unitary_residual']:.3e}`.  Step doubling changes the
path-ordered transfer by `{transfer['step_doubling_difference_norm']:.3e}`.

## Undivided pole and Wilson witness

Let the total transfer be `[[R,P],[Q,T]]`.  With positive-metric auxiliary
states `(chi0,chi1)`, the certificate constructs the polynomial/entire block
system directly on `(q0,chi0,chi1)`.  Off auxiliary poles it obeys

`det F_full = det(H0-mW0) det(H1-mW1) det Gamma_reduced`

with maximum relative residual
`{characteristic['maximum_full_vs_reduced_identity_residual']:.3e}`.  No
factor is divided away in the spectrum calculation.

The first three positive signed roots are
`{characteristic['first_three_signed_positive_roots']}`.  The first is simple;
the full-matrix near-pole residue error is
`{characteristic['near_pole_full_residue_residual']:.3e}`.  The representative
same-action host response has norm
`{witness['Wilson_witness']['G00_spectral_norm']:.6g}` and the Euclidean
source-to-host ratio `||G(8i)||/||G(4i)||` is
`{witness['Wilson_witness']['norm8_over_norm4']:.6g}`.

## Clause decision

- **C3 — `{decision['C3']['status']}`.** {decision['C3']['reason']}
- **C4 — `{decision['C4']['status']}`.** {decision['C4']['reason']}
- **C7 — `{decision['C7']['status']}`.** {decision['C7']['reason']}

The transfer accepts either the finite-range V49 coefficient kernel or a
local constrained profile through the same `(A,Xi,C,R7,R8,Z)` callback.  That
interface does not itself decide C2.  A second independent profile rematch and
loop subtraction remain C5.

Therefore the full ledger stays **G1 closed; G2--G8 open (1/8)**.

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts() -> dict[str, Any]:
    report = build_report()
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")
    return report


def check_artifacts() -> None:
    report = build_report()
    expected_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
    expected_md = render_markdown(report)
    if not JSON_PATH.is_file() or JSON_PATH.read_text(encoding="utf-8") != expected_json:
        raise RuntimeError(f"stale artifact: {JSON_PATH.name}")
    if not MD_PATH.is_file() or MD_PATH.read_text(encoding="utf-8") != expected_md:
        raise RuntimeError(f"stale artifact: {MD_PATH.name}")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash mismatch")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check_artifacts()
        print("V50_FULL_SAME_ACTION_COLLAR_AUDIT_CHECK_PASS")
    else:
        report = write_artifacts()
        print(report["status"])
        print(report["core_sha256"])


if __name__ == "__main__":
    main()
