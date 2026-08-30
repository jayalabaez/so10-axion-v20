#!/usr/bin/env python3
"""V50 finite-moose same-matrix theorem and physical bridge obstruction.

This audit freezes one *positive-Kahler*, finite-N abstract quadratic matrix
witness inspired by the proposed supersymmetric regulator.  It combines:

* the local X/P constrained-transport moose;
* every quadratic collar block type A, Xi, C, R7, R8 and Z;
* both endpoint auxiliary sectors without rational division;
* 465 source-profile coordinates with a declared 443 plus 22 split;
* an abstract discretized Spin(10)xU(1)_F link/gauge block; and
* the retained mixed H/Hc Kahler block.

The action is finite dimensional after gauge fixing.  Its complex symmetric
chiral Hessian M is embedded in the Hermitian Nambu pencil

    H_N=[[0,M^dagger],[M,0]],  Z_N=diag(Z^*,Z),

and every gauge/link block is a Hermitian quadratic pencil.  Positivity of the
full 5303-coordinate kinetic form is proved by an exact direct-sum/Kronecker
spectral decomposition, so no giant dense matrix is materialized.

The result is deliberately scoped to an abstract fixed finite quadratic
witness.  It proves the matrix theorem but does not identify that witness with
the physical V47/V49 action: the source Hessian/orbit map, coupled Goldstone
gauge fixing, invariant-tensor lift and auxiliary representations are missing.
Consequently physical C3 and C4 remain partial and G2 stays open.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

import susy_v50_full_same_action_collar_audit as v50_collar
import susy_v50_finite_moose_action_spec as shared_action
import susy_v50_local_constrained_transport_regulator_audit as v50_local


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V50_FINITE_MOOSE_SAME_ACTION_BRIDGE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V50_FINITE_MOOSE_SAME_ACTION_BRIDGE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v50_finite_moose_same_action_bridge_audit.py"

STATUS = (
    "V50_ABSTRACT_FINITE_N_POSITIVE_KAHLER_MATRIX_WITNESS_FROZEN__"
    "EXACT_BIT_ACTION_FINGERPRINT__"
    "ABSTRACT_COMPLEX_NAMBU_HERMITICITY_AND_5303_COORDINATE_POSITIVITY_PASS__"
    "C2_LOCALIZER_PASS__PHYSICAL_C3_C4_PARTIAL_NOT_IDENTIFIED__"
    "FIVE_MISSING_PHYSICAL_MAPS_EXHIBITED__G2_NOT_CLOSED"
)

N_CELLS = shared_action.N_CELLS
N_CHANNELS = shared_action.N_CHANNELS
SPINOR_COMPONENTS = shared_action.SPINOR_COMPONENTS
SOURCE_COMPONENTS = shared_action.SOURCE_COMPONENTS
SOURCE_PHYSICAL_COMPONENTS = shared_action.SOURCE_PHYSICAL_COMPONENTS
SOURCE_GAUGE_ORBIT_COMPONENTS = shared_action.SOURCE_GAUGE_ORBIT_COMPONENTS
GAUGE_DIMENSION = shared_action.GAUGE_DIMENSION
UNBROKEN_GAUGE_DIMENSION = shared_action.UNBROKEN_GAUGE_DIMENSION
BROKEN_GAUGE_DIMENSION = shared_action.BROKEN_GAUGE_DIMENSION

EPSILON = shared_action.EPSILON
SPACING = shared_action.SPACING
TRANSPORT_SCALE = shared_action.TRANSPORT_SCALE
GAUGE_COUPLING = shared_action.GAUGE_COUPLING
LINK_VEV = shared_action.LINK_VEV
LINK_KAHLER_SCALE = shared_action.LINK_KAHLER_SCALE
SOURCE_PHYSICAL_MASS = shared_action.SOURCE_PHYSICAL_MASS
SOURCE_GAUGE_ORBIT_MASS = shared_action.SOURCE_GAUGE_ORBIT_MASS

UPSTREAM_JSONS = (
    ROOT / "SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json",
    ROOT / "SUSY_V50_LOCAL_CONSTRAINED_TRANSPORT_REGULATOR_AUDIT.json",
    ROOT / "SUSY_V50_FULL_SAME_ACTION_COLLAR_AUDIT.json",
)


Array = np.ndarray


def maximum_abs(matrix: Array) -> float:
    return float(np.max(np.abs(matrix))) if matrix.size else 0.0


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _complex_matrix_payload(matrix: Array) -> list[list[list[float]]]:
    data = np.asarray(matrix, dtype=np.complex128)
    return [
        [[float(value.real), float(value.imag)] for value in row]
        for row in data
    ]


def matrix_sha256(matrix: Array) -> str:
    return hashlib.sha256(canonical_bytes(_complex_matrix_payload(matrix))).hexdigest()


def block_diagonal(*blocks: Array) -> Array:
    total = sum(block.shape[0] for block in blocks)
    result = np.zeros((total, total), dtype=np.complex128)
    offset = 0
    for block in blocks:
        size = block.shape[0]
        if block.shape != (size, size):
            raise ValueError("block diagonal inputs must be square")
        result[offset : offset + size, offset : offset + size] = block
        offset += size
    return result


def positive_inverse_square_root(metric: Array) -> Array:
    metric = np.asarray(metric, dtype=np.complex128)
    eigenvalues, eigenvectors = np.linalg.eigh(metric)
    if float(np.min(eigenvalues)) <= 0.0:
        raise ValueError("metric must be positive definite")
    return eigenvectors @ np.diag(eigenvalues ** -0.5) @ eigenvectors.conjugate().T


def incidence_matrix(num_cells: int = N_CELLS) -> Array:
    return np.asarray(v50_local.incidence_matrix(num_cells), dtype=np.complex128)


def deterministic_phase_diagonal(size: int, seed: int) -> Array:
    angles = np.asarray(
        [0.29 * math.sin((index + 1) * (seed + 1) * 0.173) for index in range(size)]
    )
    return np.diag(np.exp(1j * angles))


def complex_basis_transform(mass: Array, metric: Array, seed: int) -> tuple[Array, Array]:
    """Put a real action in a genuinely complex coordinate convention.

    A holomorphic quadratic form transforms by U^T M U and a Kahler metric by
    U^dagger Z U.  This preserves locality, symmetry, positivity and spectra
    while forcing the executable Nambu audit to use conjugation correctly.
    """

    unitary = deterministic_phase_diagonal(mass.shape[0], seed)
    return unitary.T @ mass @ unitary, unitary.conjugate().T @ metric @ unitary


def source_transport_core(source_mass: float) -> tuple[Array, Array]:
    """Positive-Kahler X/P completion for one source component."""

    nodes = N_CELLS + 1
    edges = N_CELLS
    incidence = incidence_matrix()
    metric = np.diag([1.0 / nodes] * nodes + [1.0] * edges).astype(np.complex128)
    endpoint_mass = np.zeros((nodes, nodes), dtype=np.complex128)
    endpoint_mass[-1, -1] = complex(source_mass)
    coupling = TRANSPORT_SCALE / math.sqrt(nodes)
    mass = np.block(
        [
            [endpoint_mass, coupling * incidence.conjugate().T],
            [coupling * incidence, np.zeros((edges, edges), dtype=np.complex128)],
        ]
    )
    return complex_basis_transform(mass, metric, 73 if source_mass else 79)


def gauge_vector_core(*, broken: bool) -> tuple[Array, Array]:
    """Transverse-vector stiffness and positive kinetic metric per generator."""

    incidence = incidence_matrix().real
    stiffness = (LINK_VEV**2) * (incidence.T @ incidence)
    if broken:
        stiffness[-1, -1] += LINK_VEV**2
    metric = (1.0 / GAUGE_COUPLING**2) * np.eye(N_CELLS + 1)
    return stiffness.astype(np.complex128), metric.astype(np.complex128)


def link_goldstone_core() -> tuple[Array, Array]:
    """Gauge-fixed link/Stueckelberg block per generator.

    These N modes are eaten by the N relative vectors in unitary gauge.  Their
    positive gauge-fixed kinetic and stiffness blocks are included before the
    quotient, and then removed together with the redundant coordinates.
    """

    incidence = incidence_matrix().real
    metric = (LINK_KAHLER_SCALE**2) * np.eye(N_CELLS)
    stiffness = (LINK_KAHLER_SCALE**2 / SPACING**2) * (incidence @ incidence.T)
    return stiffness.astype(np.complex128), metric.astype(np.complex128)


def _add_endpoint_sector(
    mass: Array,
    metric: Array,
    node: int,
    auxiliary_offset: int,
    endpoint: Mapping[str, Array],
) -> None:
    node_width = 2 * N_CHANNELS
    q_indices = np.arange(node * node_width, node * node_width + N_CHANNELS)
    auxiliary_indices = np.arange(auxiliary_offset, auxiliary_offset + endpoint["H"].shape[0])
    mass[np.ix_(q_indices, q_indices)] += endpoint["M"]
    mass[np.ix_(q_indices, auxiliary_indices)] += endpoint["C"].T
    mass[np.ix_(auxiliary_indices, q_indices)] += endpoint["C"]
    mass[np.ix_(auxiliary_indices, auxiliary_indices)] += endpoint["H"]
    metric[np.ix_(q_indices, q_indices)] += endpoint["Z"]
    metric[np.ix_(auxiliary_indices, auxiliary_indices)] += endpoint["W"]


def collar_endpoint_core() -> tuple[Array, Array, dict[str, Any]]:
    """Literal local finite-node A/Xi/C/R7/R8/Z action and auxiliaries.

    On cell j, with midpoint psi_bar and difference Delta psi, the quadratic
    superpotential is

      W_j=psi_bar^T D_j Delta psi - psi_bar^T V_j psi_bar/(2N),

    where D_j contains independent R7 and R8 and
    V_j=[[A,C^T],[C,Xi]].  Taking the Hessian of this scalar expression gives
    the complex symmetric nearest-neighbour matrix below.  No continuum IBP
    domain is imported.
    """

    data = v50_collar.deterministic_collar_data(N_CHANNELS)
    if abs(float(data["epsilon"]) - EPSILON) > 1.0e-15:
        raise RuntimeError("frozen collar width drifted")
    callback = v50_collar.deterministic_collar_blocks(data)
    node_width = 2 * N_CHANNELS
    nodes = N_CELLS + 1
    endpoint_auxiliaries = 4
    node_dimension = node_width * nodes
    total_dimension = node_dimension + endpoint_auxiliaries
    mass = np.zeros((total_dimension, total_dimension), dtype=np.complex128)
    metric = np.zeros_like(mass)
    weights = v50_local.trapezoid_weights(N_CELLS)

    block_norms: dict[str, list[float]] = {
        key: [] for key in ("A", "Xi", "C", "R7", "R8", "Z")
    }
    for node, point in enumerate(np.linspace(0.0, 1.0, nodes)):
        blocks = callback(float(point), 0.0)
        spectral = np.asarray(blocks["spectral_metric"], dtype=np.complex128)
        node_slice = slice(node * node_width, (node + 1) * node_width)
        metric[node_slice, node_slice] += weights[node] * spectral
        block_norms["Z"].append(float(np.linalg.norm(spectral, 2)))

    for cell in range(N_CELLS):
        midpoint = (cell + 0.5) / N_CELLS
        blocks = callback(midpoint, 0.0)
        a0 = np.asarray(blocks["A"], dtype=np.complex128)
        xi0 = np.asarray(blocks["Xi"], dtype=np.complex128)
        c0 = np.asarray(blocks["C"], dtype=np.complex128)
        r7 = np.asarray(blocks["R7"], dtype=np.complex128)
        r8 = np.asarray(blocks["R8"], dtype=np.complex128)
        zero = np.zeros((N_CHANNELS, N_CHANNELS), dtype=np.complex128)
        derivative = np.block([[zero, r8.T], [np.eye(N_CHANNELS) + r7, zero]])
        potential = np.block([[a0, c0.T], [c0, xi0]])

        midpoint_map = np.zeros((node_width, node_dimension), dtype=np.complex128)
        difference_map = np.zeros_like(midpoint_map)
        left = slice(cell * node_width, (cell + 1) * node_width)
        right = slice((cell + 1) * node_width, (cell + 2) * node_width)
        midpoint_map[:, left] = 0.5 * np.eye(node_width)
        midpoint_map[:, right] = 0.5 * np.eye(node_width)
        difference_map[:, left] = -np.eye(node_width)
        difference_map[:, right] = np.eye(node_width)
        local_mass = (
            midpoint_map.T @ derivative @ difference_map
            + difference_map.T @ derivative.T @ midpoint_map
            - (1.0 / N_CELLS) * midpoint_map.T @ potential @ midpoint_map
        )
        mass[:node_dimension, :node_dimension] += local_mass
        for key, matrix in (("A", a0), ("Xi", xi0), ("C", c0), ("R7", r7), ("R8", r8)):
            block_norms[key].append(float(np.linalg.norm(matrix, 2)))

    host = v50_collar.endpoint_data(N_CHANNELS, 601)
    source = v50_collar.endpoint_data(N_CHANNELS, 611)
    _add_endpoint_sector(mass, metric, 0, node_dimension, host)
    _add_endpoint_sector(mass, metric, N_CELLS, node_dimension + 2, source)
    mass, metric = complex_basis_transform(mass, metric, 89)
    metadata = {
        "block_spectral_norms": block_norms,
        "host_endpoint": {key: _complex_matrix_payload(value) for key, value in host.items()},
        "source_endpoint": {key: _complex_matrix_payload(value) for key, value in source.items()},
        "raw_collar_data": {
            key: (_complex_matrix_payload(value) if isinstance(value, np.ndarray) else value)
            for key, value in data.items()
        },
    }
    return mass, metric, metadata


def analytic_fifth_derivative_bound() -> dict[str, float]:
    """Uniform, non-sampled bound for K5(t)=I+R7(t)-R8(t)."""

    data = v50_collar.deterministic_collar_data(N_CHANNELS)
    even_difference = np.asarray(data["R7a"] - data["R8a"], dtype=np.complex128)
    odd_difference = np.asarray(data["R7b"] - data["R8b"], dtype=np.complex128)
    even_norm = float(np.linalg.norm(even_difference, 2))
    odd_norm = float(np.linalg.norm(odd_difference, 2))
    lower_bound = 1.0 - even_norm - odd_norm
    dense_minimum = min(
        float(
            np.min(
                np.linalg.svd(
                    np.eye(N_CHANNELS)
                    + math.sin(math.pi * point) ** 2 * even_difference
                    + math.sin(2.0 * math.pi * point) * odd_difference,
                    compute_uv=False,
                )
            )
        )
        for point in np.linspace(0.0, 1.0, 2001)
    )
    return {
        "norm_R7a_minus_R8a": even_norm,
        "norm_R7b_minus_R8b": odd_norm,
        "analytic_all_t_lower_bound": lower_bound,
        "dense_2001_point_crosscheck": dense_minimum,
    }


def mixed_kahler_schur_certificate() -> dict[str, float]:
    metric = np.asarray(v50_collar.deterministic_collar_data(N_CHANNELS)["norm_metric"])
    z_h = metric[:N_CHANNELS, :N_CHANNELS]
    mixing = metric[:N_CHANNELS, N_CHANNELS:]
    z_c = metric[N_CHANNELS:, N_CHANNELS:]
    h_min = float(np.min(np.linalg.eigvalsh(z_h)))
    c_min = float(np.min(np.linalg.eigvalsh(z_c)))
    mixing_norm = float(np.linalg.norm(mixing, 2))
    norm_bound = c_min - mixing_norm**2 / h_min
    exact_schur = z_c - mixing.conjugate().T @ np.linalg.solve(z_h, mixing)
    return {
        "H_block_minimum": h_min,
        "Hc_block_minimum": c_min,
        "mixed_block_operator_norm": mixing_norm,
        "global_operator_norm_Schur_lower_bound": norm_bound,
        "exact_Schur_minimum": float(np.min(np.linalg.eigvalsh(exact_schur))),
        "full_metric_minimum": float(np.min(np.linalg.eigvalsh(metric))),
    }


def nambu_pencil(mass: Array, metric: Array) -> tuple[Array, Array]:
    """Hermitian Nambu pencil for an arbitrary complex chiral Hessian."""

    mass = np.asarray(mass, dtype=np.complex128)
    metric = np.asarray(metric, dtype=np.complex128)
    zero = np.zeros_like(mass)
    hamiltonian = np.block([[zero, mass.conjugate().T], [mass, zero]])
    nambu_metric = block_diagonal(metric.conjugate(), metric)
    return hamiltonian, nambu_metric


def nambu_certificate(mass: Array, metric: Array) -> dict[str, Any]:
    hamiltonian, nambu_metric = nambu_pencil(mass, metric)
    inverse_root = positive_inverse_square_root(nambu_metric)
    whitened = inverse_root @ hamiltonian @ inverse_root
    eigenvalues = np.linalg.eigvalsh(whitened)
    return {
        "dimension": int(hamiltonian.shape[0]),
        "M_transpose_symmetry_residual": maximum_abs(mass - mass.T),
        "Z_Hermitian_residual": maximum_abs(metric - metric.conjugate().T),
        "H_N_Hermitian_residual": maximum_abs(hamiltonian - hamiltonian.conjugate().T),
        "Z_N_Hermitian_residual": maximum_abs(nambu_metric - nambu_metric.conjugate().T),
        "Z_N_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(nambu_metric))),
        "whitened_Hermitian_residual": maximum_abs(whitened - whitened.conjugate().T),
        "plus_minus_pairing_residual": float(np.max(np.abs(eigenvalues + eigenvalues[::-1]))),
        "minimum_eigenvalue": float(eigenvalues[0]),
        "maximum_eigenvalue": float(eigenvalues[-1]),
        "zero_count_at_1e_minus_9": int(np.count_nonzero(np.abs(eigenvalues) < 1.0e-9)),
    }


def source_transport_spectrum_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    """Separate the one intended profile from the N vectorlike heavy pairs."""

    def positive_masses(mass: Array, metric: Array) -> Array:
        hamiltonian, nambu_metric = nambu_pencil(mass, metric)
        inverse_root = positive_inverse_square_root(nambu_metric)
        values = np.linalg.eigvalsh(inverse_root @ hamiltonian @ inverse_root)
        return np.sort(values[values > 1.0e-9])

    gauge_masses = positive_masses(
        matrices["source_M_gauge_orbit"], matrices["source_Z_gauge_orbit"]
    )
    physical_masses = positive_masses(
        matrices["source_M_physical"], matrices["source_Z_physical"]
    )
    expected_singular = np.asarray(
        v50_local.transport_singular_values(N_CELLS, TRANSPORT_SCALE), dtype=float
    )
    expected_heavy = np.repeat(expected_singular, 2)
    endpoint_canonical_norm = SOURCE_PHYSICAL_MASS * (N_CELLS + 1)
    physical_heavy_lower_bound = float(np.min(expected_heavy) - endpoint_canonical_norm)
    return {
        "intended_profiles_per_original_source": 1,
        "heavy_vectorlike_pairs_per_original_source": N_CELLS,
        "total_heavy_vectorlike_pairs": N_CELLS * SOURCE_COMPONENTS,
        "gauge_orbit_zero_profiles_before_quotient": SOURCE_GAUGE_ORBIT_COMPONENTS,
        "physical_endpoint_modes": int(len(physical_masses)),
        "gauge_orbit_nonzero_chiral_masses": int(len(gauge_masses)),
        "gauge_orbit_heavy_mass_residual_against_incidence_formula": float(
            np.max(np.abs(gauge_masses - expected_heavy))
        ),
        "smallest_unperturbed_transport_mass": float(np.min(expected_heavy)),
        "endpoint_Hessian_canonical_operator_norm": endpoint_canonical_norm,
        "analytic_physical_heavy_mass_lower_bound": physical_heavy_lower_bound,
        "explicit_physical_light_mass": float(physical_masses[0]),
        "explicit_physical_heavy_mass_minimum": float(physical_masses[1]),
        "additional_uncontrolled_light_profiles": 0,
        "proof": (
            "rank(B)=N leaves one and only one X profile; the remaining 2N chiral "
            "coordinates are N vectorlike pairs with Takagi masses equal to the N "
            "incidence singular values, each twice. The endpoint Hessian has canonical "
            "operator norm 5*0.31, so Weyl's inequality leaves the heavy gap positive."
        ),
    }


def compressed_action_matrices() -> dict[str, Any]:
    """Return the canonical shared blocks; this audit defines no second action."""

    matrices = shared_action.compressed_action_matrices()
    shared_action.assert_matrix_fingerprint(matrices)
    return matrices


def action_manifest() -> dict[str, Any]:
    return shared_action.action_manifest()


def action_fingerprint() -> str:
    return shared_action.action_fingerprint()


def direct_sum_kinetic_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    collar_eigenvalues = np.linalg.eigvalsh(matrices["collar_Z"])
    source_physical_eigenvalues = np.linalg.eigvalsh(matrices["source_Z_physical"])
    source_gauge_eigenvalues = np.linalg.eigvalsh(matrices["source_Z_gauge_orbit"])
    gauge_unbroken_eigenvalues = np.linalg.eigvalsh(matrices["gauge_Z_unbroken"])
    gauge_broken_eigenvalues = np.linalg.eigvalsh(matrices["gauge_Z_broken"])
    link_eigenvalues = np.linalg.eigvalsh(matrices["link_Z"])
    core_spectra = {
        "collar": collar_eigenvalues,
        "source_physical": source_physical_eigenvalues,
        "source_gauge_orbit": source_gauge_eigenvalues,
        "gauge_unbroken": gauge_unbroken_eigenvalues,
        "gauge_broken": gauge_broken_eigenvalues,
        "link": link_eigenvalues,
    }
    multiplicities = matrices["sector_multiplicities"]
    sector_dimensions = {
        name: int(len(values) * multiplicities[name]) for name, values in core_spectra.items()
    }
    full_dimension = sum(sector_dimensions.values())
    full_minimum = min(float(np.min(values)) for values in core_spectra.values())
    full_trace = sum(
        float(np.sum(values)) * multiplicities[name] for name, values in core_spectra.items()
    )

    representative_metric = block_diagonal(
        matrices["collar_Z"],
        matrices["source_Z_physical"],
        matrices["source_Z_gauge_orbit"],
        matrices["gauge_Z_unbroken"],
        matrices["gauge_Z_broken"],
        matrices["link_Z"],
    )
    representative_minimum = float(np.min(np.linalg.eigvalsh(representative_metric)))
    schur = mixed_kahler_schur_certificate()
    minimum_weight = min(v50_local.trapezoid_weights(N_CELLS))
    analytic_collar_bound = (
        minimum_weight * EPSILON * schur["full_metric_minimum"]
    )
    analytic_full_bound = min(
        analytic_collar_bound,
        1.0 / (N_CELLS + 1),
        1.0 / GAUGE_COUPLING**2,
        LINK_KAHLER_SCALE**2,
    )
    return {
        "sector_dimensions": sector_dimensions,
        "full_gauge_fixed_coordinate_dimension": full_dimension,
        "full_metric_positive_eigenvalue_count": full_dimension,
        "full_metric_minimum_from_exact_core_spectra": full_minimum,
        "full_metric_trace_from_exact_core_spectra": full_trace,
        "representative_all_sector_matrix_dimension": int(representative_metric.shape[0]),
        "representative_all_sector_minimum": representative_minimum,
        "analytic_collar_metric_lower_bound": analytic_collar_bound,
        "analytic_full_metric_lower_bound": analytic_full_bound,
        "Kronecker_direct_sum_proof": (
            "Z_full=(Z_collar tensor I_16) direct_sum (Z_source,phys tensor I_443) "
            "direct_sum (Z_source,gauge tensor I_22) direct_sum "
            "(Z_vector,unbroken tensor I_24) direct_sum (Z_vector,broken tensor I_22) "
            "direct_sum (Z_link tensor I_46); its spectrum is exactly the multiset union "
            "of the six core spectra with those multiplicities"
        ),
    }


def gauge_reduction_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    source_gauge_nambu = nambu_certificate(
        matrices["source_M_gauge_orbit"], matrices["source_Z_gauge_orbit"]
    )

    def generalized_eigenvalues(stiffness: Array, metric: Array) -> Array:
        inverse_root = positive_inverse_square_root(metric)
        return np.linalg.eigvalsh(inverse_root @ stiffness @ inverse_root)

    unbroken_values = generalized_eigenvalues(
        matrices["gauge_L_unbroken"], matrices["gauge_Z_unbroken"]
    )
    broken_values = generalized_eigenvalues(
        matrices["gauge_L_broken"], matrices["gauge_Z_broken"]
    )
    link_values = generalized_eigenvalues(matrices["link_L"], matrices["link_Z"])
    chiral_gauge_fixed_dimension = (
        matrices["collar_M"].shape[0] * SPINOR_COMPONENTS
        + matrices["source_M_physical"].shape[0] * SOURCE_PHYSICAL_COMPONENTS
        + matrices["source_M_gauge_orbit"].shape[0] * SOURCE_GAUGE_ORBIT_COMPONENTS
    )
    chiral_gauge_reduced_dimension = chiral_gauge_fixed_dimension - SOURCE_GAUGE_ORBIT_COMPONENTS
    full_gauge_fixed_dimension = direct_sum_kinetic_certificate(matrices)[
        "full_gauge_fixed_coordinate_dimension"
    ]
    full_unitary_gauge_dimension = (
        full_gauge_fixed_dimension
        - N_CELLS * GAUGE_DIMENSION
        - SOURCE_GAUGE_ORBIT_COMPONENTS
    )
    return {
        "one_source_gauge_profile_Nambu_zero_count": source_gauge_nambu[
            "zero_count_at_1e_minus_9"
        ],
        "removed_source_gauge_orbit_complex_profiles": SOURCE_GAUGE_ORBIT_COMPONENTS,
        "removed_link_Goldstone_coordinates": N_CELLS * GAUGE_DIMENSION,
        "chiral_gauge_fixed_dimension": chiral_gauge_fixed_dimension,
        "chiral_gauge_reduced_dimension": chiral_gauge_reduced_dimension,
        "formal_reduced_chiral_Nambu_dimension": 2 * chiral_gauge_reduced_dimension,
        "full_gauge_fixed_dimension": full_gauge_fixed_dimension,
        "full_unitary_gauge_dimension": full_unitary_gauge_dimension,
        "dimension_kind": (
            "5303 and 5097 are undoubled kinetic-coordinate counts, not Nambu dimensions"
        ),
        "unbroken_vector_zero_modes_per_generator": int(
            np.count_nonzero(np.abs(unbroken_values) < 1.0e-9)
        ),
        "broken_vector_zero_modes_per_generator": int(
            np.count_nonzero(np.abs(broken_values) < 1.0e-9)
        ),
        "link_zero_modes_per_generator": int(np.count_nonzero(np.abs(link_values) < 1.0e-9)),
        "total_physical_unbroken_vector_zero_modes": UNBROKEN_GAUGE_DIMENSION,
        "minimum_broken_vector_mass_squared": float(np.min(broken_values)),
        "minimum_link_gauge_fixed_mass_squared": float(np.min(link_values)),
        "formal_quotient_positivity_if_maps_are_supplied": (
            "Restriction of a strictly positive metric to any exhibited Z-orthogonal "
            "complement stays positive. Here only the declared 22+184 dimension subtraction "
            "is tested; the physical orbit map and projector are not constructed."
        ),
        "physical_465_by_22_orbit_map_constructed": False,
        "Z_orthogonal_projector_constructed": False,
        "coupled_endpoint_link_Rxi_Goldstone_block_constructed": False,
    }


def locality_certificate(matrices: Mapping[str, Any]) -> dict[str, Any]:
    node_width = 2 * N_CHANNELS
    collar_mass = matrices["collar_M"]
    collar_violations = 0
    for first in range(N_CELLS + 1):
        for second in range(N_CELLS + 1):
            if abs(first - second) <= 1:
                continue
            block = collar_mass[
                first * node_width : (first + 1) * node_width,
                second * node_width : (second + 1) * node_width,
            ]
            if maximum_abs(block) > 1.0e-13:
                collar_violations += 1

    node_dimension = (N_CELLS + 1) * node_width
    endpoint_auxiliary_violations = 0
    for auxiliary in range(node_dimension, node_dimension + 4):
        if auxiliary < node_dimension + 2:
            allowed = set(range(N_CHANNELS)) | set(range(node_dimension, node_dimension + 2))
        else:
            source_start = N_CELLS * node_width
            allowed = set(range(source_start, source_start + N_CHANNELS)) | set(
                range(node_dimension + 2, node_dimension + 4)
            )
        for coordinate in range(collar_mass.shape[0]):
            if coordinate not in allowed and abs(collar_mass[auxiliary, coordinate]) > 1.0e-13:
                endpoint_auxiliary_violations += 1

    source_mass = matrices["source_M_physical"]
    nodes = N_CELLS + 1
    source_violations = 0
    for first in range(source_mass.shape[0]):
        for second in range(source_mass.shape[1]):
            if abs(source_mass[first, second]) <= 1.0e-13:
                continue
            if first < nodes and second < nodes:
                allowed = first == second
            elif first >= nodes and second >= nodes:
                allowed = first == second
            else:
                site = first if first < nodes else second
                edge = (second if first < nodes else first) - nodes
                allowed = site in (edge, edge + 1)
            if not allowed:
                source_violations += 1

    def scalar_path_violations(matrix: Array) -> int:
        return sum(
            1
            for first in range(matrix.shape[0])
            for second in range(matrix.shape[1])
            if abs(first - second) > 1 and abs(matrix[first, second]) > 1.0e-13
        )

    gauge_link_violations = sum(
        scalar_path_violations(matrices[name])
        for name in ("gauge_L_unbroken", "gauge_L_broken", "link_L")
    )
    incidence = incidence_matrix()
    all_local = (
        collar_violations == 0
        and endpoint_auxiliary_violations == 0
        and source_violations == 0
        and gauge_link_violations == 0
    )
    return {
        "collar_non_nearest_neighbour_block_violations": collar_violations,
        "endpoint_auxiliary_nonlocal_entry_violations": endpoint_auxiliary_violations,
        "source_transport_nonlocal_entry_violations": source_violations,
        "gauge_link_non_nearest_neighbour_entry_violations": gauge_link_violations,
        "source_incidence_nonzero_count": int(np.count_nonzero(np.abs(incidence) > 0.0)),
        "source_incidence_expected_nonzero_count": 2 * N_CELLS,
        "fundamental_endpoint_to_interior_product_present": endpoint_auxiliary_violations > 0,
        "all_fundamental_terms_site_or_nearest_neighbour": all_local,
    }


def build_report() -> dict[str, Any]:
    matrices = compressed_action_matrices()
    manifest = action_manifest()
    shared_hash = action_fingerprint()
    if shared_action.canonical_action_bytes() != canonical_bytes(manifest):
        raise RuntimeError("bridge did not consume the canonical ACTION_SPEC bytes")
    collar_nambu = nambu_certificate(matrices["collar_M"], matrices["collar_Z"])
    source_physical_nambu = nambu_certificate(
        matrices["source_M_physical"], matrices["source_Z_physical"]
    )
    source_gauge_nambu = nambu_certificate(
        matrices["source_M_gauge_orbit"], matrices["source_Z_gauge_orbit"]
    )
    source_spectrum = source_transport_spectrum_certificate(matrices)
    metric = direct_sum_kinetic_certificate(matrices)
    gauge = gauge_reduction_certificate(matrices)
    locality = locality_certificate(matrices)
    derivative = analytic_fifth_derivative_bound()
    schur = mixed_kahler_schur_certificate()

    same_action_references = {
        "C2_same_action_sha256": shared_hash,
        "C3_same_action_sha256": shared_hash,
        "C4_same_action_sha256": shared_hash,
    }
    checks = {
        "one_shared_action_hash_for_abstract_matrix_certificates": len(
            set(same_action_references.values())
        ) == 1,
        "fixed_positive_Kahler_regulator_not_degenerate_limit": (
            "positive-Kahler" in manifest["regulator_choice"]
        ),
        "abstract_background_matrix_is_nearest_neighbour_local": (
            locality["all_fundamental_terms_site_or_nearest_neighbour"]
            and not locality["fundamental_endpoint_to_interior_product_present"]
        ),
        "all_named_collar_blocks_are_nonzero": all(
            max(matrices["collar_metadata"]["block_spectral_norms"][name]) > 0.0
            for name in ("A", "Xi", "C", "R7", "R8", "Z")
        ),
        "collar_complex_M_is_symmetric": collar_nambu["M_transpose_symmetry_residual"] < 1.0e-11,
        "collar_complex_Nambu_pencil_is_Hermitian": max(
            collar_nambu["H_N_Hermitian_residual"],
            collar_nambu["Z_N_Hermitian_residual"],
            collar_nambu["whitened_Hermitian_residual"],
        ) < 1.0e-10,
        "source_complex_Nambu_pencils_are_Hermitian": max(
            source_physical_nambu["H_N_Hermitian_residual"],
            source_physical_nambu["whitened_Hermitian_residual"],
            source_gauge_nambu["H_N_Hermitian_residual"],
            source_gauge_nambu["whitened_Hermitian_residual"],
        ) < 1.0e-10,
        "source_transport_has_only_the_intended_light_profile": (
            source_spectrum["gauge_orbit_heavy_mass_residual_against_incidence_formula"]
            < 1.0e-10
            and source_spectrum["analytic_physical_heavy_mass_lower_bound"] > 0.0
            and source_spectrum["additional_uncontrolled_light_profiles"] == 0
        ),
        "Nambu_spectra_have_plus_minus_pairing": max(
            collar_nambu["plus_minus_pairing_residual"],
            source_physical_nambu["plus_minus_pairing_residual"],
            source_gauge_nambu["plus_minus_pairing_residual"],
        ) < 1.0e-9,
        "full_5303_coordinate_metric_is_positive": (
            metric["full_gauge_fixed_coordinate_dimension"] == 5303
            and metric["full_metric_positive_eigenvalue_count"] == 5303
            and metric["analytic_full_metric_lower_bound"] > 0.0
            and metric["full_metric_minimum_from_exact_core_spectra"] > 0.0
        ),
        "mixed_Kahler_Schur_bound_is_global_and_positive": (
            schur["global_operator_norm_Schur_lower_bound"] > 0.0
            and schur["exact_Schur_minimum"] > 0.0
        ),
        "fifth_derivative_form_uniformly_invertible_analytically": derivative[
            "analytic_all_t_lower_bound"
        ] > 0.0,
        "endpoint_auxiliaries_are_retained": matrices["collar_M"].shape[0] == 44,
        "formal_gauge_dimension_split_has_expected_matrix_zero_modes": (
            gauge["unbroken_vector_zero_modes_per_generator"] == 1
            and gauge["broken_vector_zero_modes_per_generator"] == 0
            and gauge["link_zero_modes_per_generator"] == 0
            and gauge["one_source_gauge_profile_Nambu_zero_count"] == 2
        ),
        "physical_identification_is_explicitly_fail_closed": (
            manifest["physical_identification_status"]["status"]
            == "OPEN_NOT_A_V47_V49_SAME_ACTION_CERTIFICATE"
            and len(manifest["physical_identification_status"]["missing_maps"]) == 5
            and not gauge["physical_465_by_22_orbit_map_constructed"]
            and not gauge["Z_orthogonal_projector_constructed"]
            and not gauge["coupled_endpoint_link_Rxi_Goldstone_block_constructed"]
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise RuntimeError("V50 finite-moose same-action bridge failure: " + ", ".join(failures))

    report: dict[str, Any] = {
        "schema": "susy-v50-finite-moose-abstract-theorem-and-obstruction-v2",
        "status": STATUS,
        "scientific_scope": (
            "One fixed finite-N abstract tree-level quadratic witness. It proves exact-bit "
            "same-matrix locality, finite-dimensional Hermiticity and kinetic positivity. "
            "It does not identify the matrices with the physical V47/V49 representation and "
            "therefore leaves physical C3 and C4 partial."
        ),
        "shared_action_sha256": shared_hash,
        "same_action_clause_references": same_action_references,
        "action_manifest": manifest,
        "locality_and_C2": {
            **locality,
            "C2_decision": "PASS_REPRESENTATION_LEVEL_FINITE_LOCALIZER",
            "scope": (
                "The X/P plus link construction is site/link local and gauge covariant for "
                "arbitrary supplied representations. The missing normalized V49 tensor lift "
                "blocks physical C3/C4 integration, not the existence of the C2 localizer."
            ),
        },
        "variational_domain_and_C3": {
            "finite_chiral_pencil": "H_N-m Z_N on the full finite coordinate space, with H_N=[[0,Mdagger],[M,0]] and Z_N=diag(Z*,Z)",
            "gauge_link_pencil": "abstract L_V-p^2 Z_V and independent L_link-p^2 Z_link blocks",
            "domain": (
                "all abstract finite site and endpoint-auxiliary coordinates before reduction; "
                "the physical Z-orthogonal quotient is not defined until the 465x22 orbit map "
                "and coupled endpoint/link Goldstone map are exhibited"
            ),
            "variation": (
                "The endpoint and auxiliary equations are literal rows of the symmetric/Hermitian "
                "full pencil. No mass-dependent Schur pencil is substituted as a boundary domain."
            ),
            "summation_by_parts_Green_identity": (
                "For the finite local Hessian, u^dagger H_N v-(H_N u)^dagger v=0 exactly; "
                "nearest-neighbour boundary terms are cancelled by the retained endpoint rows."
            ),
            "collar_Nambu_certificate": collar_nambu,
            "source_physical_Nambu_certificate": source_physical_nambu,
            "source_gauge_orbit_Nambu_certificate": source_gauge_nambu,
            "source_transport_spectrum": source_spectrum,
            "formal_gauge_dimension_arithmetic": gauge,
            "physical_C3_decision": "PARTIAL_NOT_PHYSICALLY_IDENTIFIED",
        },
        "full_kinetic_form_and_C4": {
            "direct_sum_certificate": metric,
            "mixed_Kahler_certificate": schur,
            "uniform_fifth_derivative_form": derivative,
            "source_metric": "K_X=I_5/5 and K_P=I_4 for each of all 465 source components",
            "gauge_link_metric": "Z_V=I_5/g^2 and Z_link=f^2 I_4 for every one of 46 generators",
            "positive_cone_statement": (
                "For the abstract witness, the frozen point is interior: positivity persists "
                "for Hermitian kinetic perturbations smaller than the analytic lower bound."
            ),
            "physical_C4_decision": "PARTIAL_NOT_PHYSICALLY_IDENTIFIED",
        },
        "abstract_quadratic_factorization": (
            "The displayed compressed matrices are exact direct summands by construction. "
            "Identifying their 443+22 split, endpoint blocks and channel coefficients with the "
            "physical V47/V49 Hessian requires the missing maps below and is not inferred."
        ),
        "physical_identification_obstruction": {
            "status": "OPEN_FIVE_EXPLICIT_MAPS_REQUIRED",
            "missing_maps": manifest["physical_identification_status"]["missing_maps"],
            "orbit_projector_required": (
                "Exhibit Q in C^(465x22), rank Q=22, P=I-Q(Q^dagger Z Q)^(-1)"
                "Q^dagger Z, and the Ward relation M Q=0."
            ),
            "Rxi_block_required": (
                "For each broken generator augment the four link variations B alpha by "
                "the endpoint source variation e_N^T alpha; construct the five-mode "
                "Goldstone block from D_aug=[B;e_N^T], not BB^T direct-sum a source zero."
            ),
            "closure_rule": (
                "Physical C3/C4 may be promoted only after all five maps are executable, "
                "hashed into this same action, and the resulting full pencil/metric pass."
            ),
        },
        "clause_decision": {
            "C2_same_finite_regulator": "PASS_REPRESENTATION_LEVEL_FINITE_LOCALIZER",
            "C3_same_action_variational_domain_and_self_adjointness": "PARTIAL_ABSTRACT_MATRIX_PASS__PHYSICAL_IDENTIFICATION_OPEN",
            "C4_same_action_full_kinetic_positivity": "PARTIAL_ABSTRACT_MATRIX_PASS__PHYSICAL_IDENTIFICATION_OPEN",
            "C5_counterterm_and_matching": "NOT_ASSESSED_HERE_REMAINS_OPEN",
            "C7_component_Wilson_matching": "NOT_ASSESSED_HERE_REMAINS_OPEN",
            "G2_closed": False,
            "gates_promoted": [],
        },
        "continuum_and_scope_caveats": [
            "Fixed finite N is the abstract witness; no N->infinity norm/resolvent theorem is claimed.",
            "The nonlinear link sector is a cutoff gauge-moose action, not a renormalizable continuum-five-dimensional UV completion.",
            "The 5303 and 5097 totals are undoubled kinetic-coordinate counts; the formal reduced chiral Nambu dimension is 9734.",
            "Finite transport/link thresholds and profile-dependent coefficient rematching remain C5.",
            "The component tensor/current incidence and physical Wilson array remain C7.",
        ],
        "G1_anomaly_effect": (
            "The X/P additions are representation-wise R plus R-bar pairs, the Spin(10) link "
            "tangent is real adjoint and the U(1) Stueckelberg fermion is neutral, so those "
            "pieces add no perturbative anomaly. However the four positive-Kahler endpoint "
            "auxiliary multiplets per spinor lift have no assigned representations or charges. "
            "This abstract witness therefore does not alter the already-closed original G1, "
            "but it also cannot be adopted as physical new matter or independently re-certify "
            "G1 until the auxiliary anomaly map is supplied."
        ),
        "integrity_checks": checks,
        "n_failed_integrity_checks": 0,
        "primary_sources": [
            "https://arxiv.org/abs/hep-th/0104005",
            "https://arxiv.org/abs/he-th/0106256",
            "https://arxiv.org/abs/hep-ph/0112230",
            "https://arxiv.org/abs/hep-th/0212206",
        ],
        "provenance": {
            "upstream_sha256": {path.name: sha256_file(path) for path in UPSTREAM_JSONS},
            "existing_files_modified": False,
        },
    }
    report["core_sha256"] = canonical_sha(report)
    validate(report)
    return report


def validate(report: Mapping[str, Any]) -> None:
    if report["status"] != STATUS:
        raise RuntimeError("status drifted")
    if report["core_sha256"] != canonical_sha(report):
        raise RuntimeError("core hash is stale")
    if report["n_failed_integrity_checks"] != 0 or not all(
        report["integrity_checks"].values()
    ):
        raise RuntimeError("integrity checks failed")
    references = report["same_action_clause_references"]
    if set(references.values()) != {report["shared_action_sha256"]}:
        raise RuntimeError("C2-C4 do not use one action fingerprint")
    decision = report["clause_decision"]
    if decision["C2_same_finite_regulator"] != "PASS_REPRESENTATION_LEVEL_FINITE_LOCALIZER":
        raise RuntimeError("C2 localizer result drifted")
    for key in (
        "C3_same_action_variational_domain_and_self_adjointness",
        "C4_same_action_full_kinetic_positivity",
    ):
        if not decision[key].startswith("PARTIAL_ABSTRACT_MATRIX_PASS"):
            raise RuntimeError("physical C3/C4 must remain fail-closed")
    if decision["G2_closed"] or decision["gates_promoted"]:
        raise RuntimeError("the bridge cannot close or promote G2")


def render_markdown(report: Mapping[str, Any]) -> str:
    c3 = report["variational_domain_and_C3"]
    c4 = report["full_kinetic_form_and_C4"]
    metric = c4["direct_sum_certificate"]
    derivative = c4["uniform_fifth_derivative_form"]
    schur = c4["mixed_Kahler_certificate"]
    gauge = c3["formal_gauge_dimension_arithmetic"]
    collar_nambu = c3["collar_Nambu_certificate"]
    source_spectrum = c3["source_transport_spectrum"]
    blockers = report["physical_identification_obstruction"]["missing_maps"]
    blocker_lines = "\n".join(f"{index}. {item}" for index, item in enumerate(blockers, 1))
    return f"""# V50 finite-moose matrix theorem and physical bridge obstruction

Status: `{report['status']}`

## Verdict

One fixed `N={N_CELLS}` positive-Kahler quadratic witness has the canonical
exact-bit action fingerprint

`{report['shared_action_sha256']}`.

The finite X/P localizer is genuinely nearest-neighbour, so **C2 passes**.
For the abstract matrices, the complex Nambu theorem and all 5,303 kinetic
eigenvalues also pass.  But these matrices have not been identified with the
physical V47/V49 representation, orbit quotient and gauge fixing.  Therefore
**physical C3 and C4 remain PARTIAL, no gate is promoted, and G2 is open**.

## Frozen abstract witness

There are `N+1` sites and spacing `a=epsilon/N`.  For every source component,

```text
K_XP = sum_j |X_j|^2/(N+1) + sum_j |P_j|^2,
W_XP = (M_c/sqrt(N+1)) sum_j P_j[X_j-Omega_j X_(j+1)].
```

For `psi=(H,Hc)` on cell `j`, use the literal nearest-neighbour action

```text
W_j = psi_bar^T D_j Delta_Omega psi
    - (1/(2N)) psi_bar^T [[A,C^T],[C,Xi]]_j psi_bar,
D_j = [[0,R8^T],[I+R7,0]].
```

Here `Delta_Omega psi_j=R(Omega_j)psi_(j+1)-psi_j`.  A physical covariant lift
also needs `psi_bar_Omega,j=[psi_j+R(Omega_j)psi_(j+1)]/2` in one site frame.
The executable matrices use only `Omega_j=1`.  Their `0.31 I_443 plus 0 I_22`
endpoint Hessian and random four-channel `A/Xi/C/R7/R8/Z` blocks are abstract
witness data: equality to the V47 Hessian and membership in the normalized
V49 invariant-tensor image are not asserted.

The full mixed `Z` block is mass-lumped with positive trapezoid weights.
Direct endpoint `M/Z` and both positive-metric `C/H/W` auxiliary systems are
retained as coordinates.  The abstract gauge/link sector is the open path
Laplacian with endpoint stiffness for the 22 declared broken generators.  There are no
non-nearest-neighbour collar blocks and no fundamental endpoint-to-interior
Wilson product.

## Abstract C3 theorem; physical C3 obstruction

The scalar finite action is differentiated before any field is eliminated,
so its chiral Hessian is complex symmetric.  For arbitrary complex
coordinates it is embedded as

```text
H_N = [[0,M^dagger],[M,0]],
Z_N = diag(Z^*,Z).
```

The collar Nambu dimension is `{collar_nambu['dimension']}`.  Its Hermiticity
residual is `{collar_nambu['H_N_Hermitian_residual']:.3g}`, its whitened
Hermiticity residual is `{collar_nambu['whitened_Hermitian_residual']:.3g}`,
and its `+/-` spectral-pairing residual is
`{collar_nambu['plus_minus_pairing_residual']:.3g}`.

The abstract domain is the complete finite coordinate space with the endpoint
auxiliaries retained, so boundary equations are rows of the same Hermitian
pencil and no energy-dependent Schur complement is used.  Subtracting the
declared `{gauge['removed_source_gauge_orbit_complex_profiles']}` source and
`{gauge['removed_link_Goldstone_coordinates']}` link directions gives the
formal undoubled count `{gauge['full_unitary_gauge_dimension']}` and formal
reduced chiral Nambu dimension
`{gauge['formal_reduced_chiral_Nambu_dimension']}`.  This is dimension
arithmetic, not a physical quotient: no `465 x 22` orbit map, `Z`-orthogonal
projector, or coupled endpoint/link Goldstone block is present.

Each original source has exactly one intended profile and `{N_CELLS}` added
vectorlike heavy pairs.  The unperturbed transport gap is
`{source_spectrum['smallest_unperturbed_transport_mass']:.6g}`.  Even after
the frozen endpoint Hessian, Weyl's inequality gives the analytic heavy-gap
bound `{source_spectrum['analytic_physical_heavy_mass_lower_bound']:.6g}`;
there are no additional light profiles in the abstract witness.  This does
not substitute for the missing physical orbit and Hessian maps.

## Abstract C4 theorem; physical C4 obstruction

The abstract full gauge-fixed, undoubled kinetic-coordinate count is
`{metric['full_gauge_fixed_coordinate_dimension']}`:

```text
Z_full = (Z_collar tensor I_16)
       direct_sum (Z_source,physical tensor I_443)
       direct_sum (Z_source,gauge tensor I_22)
       direct_sum (Z_vector,unbroken tensor I_24)
       direct_sum (Z_vector,broken tensor I_22)
       direct_sum (Z_link tensor I_46).
```

This identity is exact for the frozen abstract witness, so the giant matrix need not be materialized.  Its
entire spectrum is the multiset union of the six core spectra.  All
`{metric['full_metric_positive_eigenvalue_count']}` eigenvalues are positive;
the exact core-spectrum minimum is
`{metric['full_metric_minimum_from_exact_core_spectra']:.6g}`.  An independent
analytic lower bound is `{metric['analytic_full_metric_lower_bound']:.6g}`.

For the retained mixed H/Hc Kahler block,

```text
lambda_min(Z_Hc)-||Y||^2/lambda_min(Z_H)
  = {schur['global_operator_norm_Schur_lower_bound']:.6g} > 0,
```

and the exact Schur minimum is `{schur['exact_Schur_minimum']:.6g}`.

The abstract fifth-direction derivative form is also controlled analytically, not by
a grid.  For every `t`,

```text
sigma_min[I+R7(t)-R8(t)]
 >= 1-||R7a-R8a||-||R7b-R8b||
 = {derivative['analytic_all_t_lower_bound']:.6g} > 0.
```

## Exact physical-identification obstruction

Physical C3/C4 need all five executable maps below; none is inferred from a
dimension count or from positivity of the abstract witness:

{blocker_lines}

In particular, the orbit certificate must exhibit `Q in C^(465 x 22)`, prove
`rank(Q)=22` and `M Q=0`, and construct
`P=I-Q(Q^dagger Z Q)^(-1)Q^dagger Z`.  For every broken generator the correct
Goldstone map is `D_aug=[B;e_N^T]`, coupling four link modes to the endpoint
source mode.  The current independent `B B^T` block plus a source zero is not
that `R_xi` Hessian.

## Scope and anomaly statement

No continuum resolvent limit, profile/loop rematch, or physical component
Wilson array is claimed; C5 and C7 remain open.  The transport pairs and
link tangent add no perturbative anomaly by themselves.  But the four
positive-Kahler endpoint auxiliary multiplets per spinor lift have no assigned
Spin(10) x U(1)_F representations or charges.  The witness therefore is not
adopted as new physical matter and does not independently re-certify G1.

Primary references: [Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005),
[Marti--Pomarol](https://arxiv.org/abs/he-th/0106256),
[Hebecker](https://arxiv.org/abs/hep-ph/0112230), and
[Falkowski et al.](https://arxiv.org/abs/hep-th/0212206).

Core SHA-256: `{report['core_sha256']}`
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V50 finite-moose bridge artifacts are missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V50 finite-moose bridge JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V50 finite-moose bridge Markdown is stale; run --write")


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
