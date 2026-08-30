#!/usr/bin/env python3
"""Canonical finite-moose action shared by the V50 C2--C4 audits.

This module is the single source of truth for the fixed ``N=4`` positive-
Kahler regulator.  It owns the numerical coefficients, the compressed action
matrices, the representation multiplicities, and the canonical action bytes.
Audits may derive independent certificates from these objects, but they must
not define a second action and call it the same regulator.

The compressed matrices define the full action by exact direct sums and
identity Kronecker lifts.  No claim about a continuum ``N -> infinity`` limit
is part of this specification.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import Any, Mapping

import numpy as np

import susy_v50_full_same_action_collar_audit as collar
import susy_v50_local_constrained_transport_regulator_audit as transport


Array = np.ndarray

N_CELLS = 4
N_CHANNELS = 4
SPINOR_COMPONENTS = 16
SOURCE_COMPONENTS = 465
SOURCE_PHYSICAL_COMPONENTS = 443
SOURCE_GAUGE_ORBIT_COMPONENTS = 22
GAUGE_DIMENSION = 46
UNBROKEN_GAUGE_DIMENSION = 24
BROKEN_GAUGE_DIMENSION = 22

EPSILON = 0.055
SPACING = EPSILON / N_CELLS
TRANSPORT_SCALE = 1.0 / SPACING
GAUGE_COUPLING = 0.73
LINK_VEV = 1.0 / (GAUGE_COUPLING * SPACING)
LINK_KAHLER_SCALE = 1.30
SOURCE_PHYSICAL_MASS = 0.31
SOURCE_GAUGE_ORBIT_MASS = 0.0


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def _complex_matrix_payload(matrix: Array) -> list[list[list[float]]]:
    value = np.asarray(matrix, dtype=np.complex128)
    return [
        [
            [round(float(item.real), 15), round(float(item.imag), 15)]
            for item in row
        ]
        for row in value
    ]


def matrix_sha256(matrix: Array) -> str:
    """Hash exact little-endian complex128 bits, shape and dtype."""

    value = np.ascontiguousarray(np.asarray(matrix, dtype="<c16"))
    digest = hashlib.sha256()
    digest.update(
        canonical_bytes(
            {"dtype": "complex128-little-endian", "shape": list(value.shape)}
        )
    )
    digest.update(b"\x00")
    digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _incidence_matrix() -> Array:
    return np.asarray(transport.incidence_matrix(N_CELLS), dtype=np.complex128)


def _phase_diagonal(size: int, seed: int) -> Array:
    angles = np.asarray(
        [0.29 * math.sin((index + 1) * (seed + 1) * 0.173) for index in range(size)]
    )
    return np.diag(np.exp(1j * angles))


def _complex_basis_transform(
    mass: Array, metric: Array, seed: int
) -> tuple[Array, Array]:
    unitary = _phase_diagonal(mass.shape[0], seed)
    return (
        unitary.T @ mass @ unitary,
        unitary.conjugate().T @ metric @ unitary,
    )


def _source_transport_core(source_mass: float) -> tuple[Array, Array]:
    """One X/P transport chain in the Omega_j=1 background gauge."""

    nodes = N_CELLS + 1
    edges = N_CELLS
    incidence = _incidence_matrix()
    metric = np.diag([1.0 / nodes] * nodes + [1.0] * edges).astype(
        np.complex128
    )
    endpoint_mass = np.zeros((nodes, nodes), dtype=np.complex128)
    endpoint_mass[-1, -1] = complex(source_mass)
    coupling = TRANSPORT_SCALE / math.sqrt(nodes)
    mass = np.block(
        [
            [endpoint_mass, coupling * incidence.T],
            [coupling * incidence, np.zeros((edges, edges), dtype=np.complex128)],
        ]
    )
    return _complex_basis_transform(mass, metric, 73 if source_mass else 79)


def _gauge_vector_core(*, broken: bool) -> tuple[Array, Array]:
    incidence = _incidence_matrix().real
    stiffness = (LINK_VEV**2) * (incidence.T @ incidence)
    if broken:
        stiffness[-1, -1] += LINK_VEV**2
    metric = (1.0 / GAUGE_COUPLING**2) * np.eye(N_CELLS + 1)
    return stiffness.astype(np.complex128), metric.astype(np.complex128)


def _link_goldstone_core() -> tuple[Array, Array]:
    incidence = _incidence_matrix().real
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
    auxiliary_indices = np.arange(
        auxiliary_offset, auxiliary_offset + endpoint["H"].shape[0]
    )
    # These are holomorphic Hessian blocks: transpose, never adjoint.
    mass[np.ix_(q_indices, q_indices)] += endpoint["M"]
    mass[np.ix_(q_indices, auxiliary_indices)] += endpoint["C"].T
    mass[np.ix_(auxiliary_indices, q_indices)] += endpoint["C"]
    mass[np.ix_(auxiliary_indices, auxiliary_indices)] += endpoint["H"]
    metric[np.ix_(q_indices, q_indices)] += endpoint["Z"]
    metric[np.ix_(auxiliary_indices, auxiliary_indices)] += endpoint["W"]


def _collar_endpoint_core() -> tuple[Array, Array, dict[str, Any]]:
    data = collar.deterministic_collar_data(N_CHANNELS)
    if abs(float(data["epsilon"]) - EPSILON) > 1.0e-15:
        raise RuntimeError("frozen collar width drifted")
    callback = collar.deterministic_collar_blocks(data)
    node_width = 2 * N_CHANNELS
    nodes = N_CELLS + 1
    node_dimension = node_width * nodes
    total_dimension = node_dimension + 4
    mass = np.zeros((total_dimension, total_dimension), dtype=np.complex128)
    metric = np.zeros_like(mass)
    weights = transport.trapezoid_weights(N_CELLS)

    block_norms: dict[str, list[float]] = {
        name: [] for name in ("A", "Xi", "C", "R7", "R8", "Z")
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
        derivative = np.block(
            [[zero, r8.T], [np.eye(N_CHANNELS) + r7, zero]]
        )
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
        for name, matrix in (
            ("A", a0),
            ("Xi", xi0),
            ("C", c0),
            ("R7", r7),
            ("R8", r8),
        ):
            block_norms[name].append(float(np.linalg.norm(matrix, 2)))

    host = collar.endpoint_data(N_CHANNELS, 601)
    source = collar.endpoint_data(N_CHANNELS, 611)
    _add_endpoint_sector(mass, metric, 0, node_dimension, host)
    _add_endpoint_sector(mass, metric, N_CELLS, node_dimension + 2, source)
    mass, metric = _complex_basis_transform(mass, metric, 89)
    metadata = {
        "block_spectral_norms": block_norms,
        "host_endpoint": {
            name: _complex_matrix_payload(value) for name, value in host.items()
        },
        "source_endpoint": {
            name: _complex_matrix_payload(value) for name, value in source.items()
        },
        "raw_collar_data": {
            name: (
                _complex_matrix_payload(value)
                if isinstance(value, np.ndarray)
                else value
            )
            for name, value in data.items()
        },
    }
    return mass, metric, metadata


def _build_compressed_action_matrices() -> dict[str, Any]:
    collar_mass, collar_metric, collar_metadata = _collar_endpoint_core()
    source_mass_physical, source_metric_physical = _source_transport_core(
        SOURCE_PHYSICAL_MASS
    )
    source_mass_gauge, source_metric_gauge = _source_transport_core(
        SOURCE_GAUGE_ORBIT_MASS
    )
    gauge_l_unbroken, gauge_z_unbroken = _gauge_vector_core(broken=False)
    gauge_l_broken, gauge_z_broken = _gauge_vector_core(broken=True)
    link_l, link_z = _link_goldstone_core()
    return {
        "collar_M": collar_mass,
        "collar_Z": collar_metric,
        "source_M_physical": source_mass_physical,
        "source_Z_physical": source_metric_physical,
        "source_M_gauge_orbit": source_mass_gauge,
        "source_Z_gauge_orbit": source_metric_gauge,
        "gauge_L_unbroken": gauge_l_unbroken,
        "gauge_Z_unbroken": gauge_z_unbroken,
        "gauge_L_broken": gauge_l_broken,
        "gauge_Z_broken": gauge_z_broken,
        "link_L": link_l,
        "link_Z": link_z,
        "collar_metadata": collar_metadata,
        "sector_multiplicities": {
            "collar": SPINOR_COMPONENTS,
            "source_physical": SOURCE_PHYSICAL_COMPONENTS,
            "source_gauge_orbit": SOURCE_GAUGE_ORBIT_COMPONENTS,
            "gauge_unbroken": UNBROKEN_GAUGE_DIMENSION,
            "gauge_broken": BROKEN_GAUGE_DIMENSION,
            "link": GAUGE_DIMENSION,
        },
    }


def _action_manifest_from_matrices(matrices: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "susy-v50-abstract-finite-moose-quadratic-witness-v2",
        "regulator_choice": (
            "fixed finite-N positive-Kahler abstract quadratic witness; the "
            "degenerate exact-multiplier limit is not used, and identification "
            "with the physical V47/V49 action is deliberately not asserted"
        ),
        "geometry": {
            "N_cells": N_CELLS,
            "epsilon": EPSILON,
            "spacing": SPACING,
            "trapezoid_weights": transport.trapezoid_weights(N_CELLS),
        },
        "field_counts": {
            "spinor_channels": N_CHANNELS,
            "Spin10_spinor_components": SPINOR_COMPONENTS,
            "source_components": SOURCE_COMPONENTS,
            "source_physical_components": SOURCE_PHYSICAL_COMPONENTS,
            "source_gauge_orbit_components": SOURCE_GAUGE_ORBIT_COMPONENTS,
            "gauge_dimension": GAUGE_DIMENSION,
            "unbroken_gauge_dimension": UNBROKEN_GAUGE_DIMENSION,
            "broken_gauge_dimension": BROKEN_GAUGE_DIMENSION,
        },
        "parameters": {
            "transport_scale": TRANSPORT_SCALE,
            "source_physical_mass": SOURCE_PHYSICAL_MASS,
            "source_gauge_orbit_mass": SOURCE_GAUGE_ORBIT_MASS,
            "gauge_coupling": GAUGE_COUPLING,
            "link_vev": LINK_VEV,
            "link_Kahler_scale": LINK_KAHLER_SCALE,
        },
        "local_action": {
            "source_transport": (
                "(Mc/sqrt(N+1)) sum_j P_j[X_j-Omega_j X_(j+1)] with "
                "K_X=I/(N+1), K_P=I"
            ),
            "source_endpoint": (
                "abstract background-gauge Hessian 0.31 I_443 plus 0 I_22; no "
                "equality to or pullback from the V47 465-component Hessian is proved"
            ),
            "source_collar_interaction": (
                "formal node-local channel-block interaction whose frozen H/Hc Hessian "
                "supplies A,Xi,C,R7,R8,Z; the normalized Spin(10) invariant-tensor "
                "lift and proof that these blocks lie in the V49 coefficient image are open"
            ),
            "covariant_difference": (
                "Delta_Omega psi_j=R(Omega_j)psi_(j+1)-psi_j; compressed matrices "
                "use the Omega_j=1 background gauge"
            ),
            "covariant_midpoint_required_for_physical_lift": (
                "psi_bar_Omega,j=[psi_j+R(Omega_j)psi_(j+1)]/2 in the site-j frame; "
                "the executable matrices implement only its Omega_j=1 value"
            ),
            "collar_cell": (
                "psi_bar^T D_j Delta_Omega psi-(1/(2N))psi_bar^T"
                "[[A,C^T],[C,Xi]]psi_bar; D_j=[[0,R8^T],[I+R7,0]]"
            ),
            "collar_Kahler": (
                "positive mass-lumped trapezoid sum of epsilon times the full "
                "mixed H/Hc norm metric"
            ),
            "endpoint": (
                "direct Z/M and positive-metric C/H/W auxiliary sectors retained "
                "as coordinates at nodes 0 and N"
            ),
            "gauge_link": (
                "abstract open path-laplacian transverse vectors, independent positive "
                "link block, and endpoint stiffness; this is not a constructed coupled "
                "endpoint-plus-link R_xi Goldstone Hessian"
            ),
        },
        "gauge_covariance": {
            "site_group": "Spin(10)_j x U(1)_{F,j}",
            "fields": (
                "X_j -> G_j X_j; P_j -> P_j G_j^{-1}; "
                "Omega_j -> G_j Omega_j G_(j+1)^{-1}"
            ),
            "transport_invariant": "P_j[X_j-Omega_j X_(j+1)]",
            "collar_rule": (
                "conditional: a physical lift requires explicit site representations, "
                "normalized invariant tensors and the covariant midpoint"
            ),
            "background_gauge_for_matrices": (
                "Omega_j=1 abstract gauge-fixed matrix witness; not a complete R_xi construction"
            ),
        },
        "anomaly_representations": {
            "transport": (
                "relative to each original source zero profile, the N extra X_j and "
                "N P_j form N copies of R plus R-bar"
            ),
            "Spin10_link_tangent": "adjoint 45, a real representation",
            "U1_link_tangent": "Stueckelberg shift multiplet with neutral fermion",
            "endpoint_auxiliaries": (
                "four positive-Kahler auxiliary multiplets per spinor lift are counted, "
                "but their Spin(10)xU(1)_F representations and anomaly pairing are not specified"
            ),
            "scope": (
                "transport/link additions alone are anomaly-safe; the complete physical G1 "
                "statement is not re-certified because endpoint-auxiliary representations "
                "and a nonlinear Wess-Zumino/global-anomaly completion are absent"
            ),
        },
        "quadratic_domain": {
            "chiral": "all site X/P, collar H/Hc, and four endpoint auxiliaries",
            "vector": "all transverse site vectors plus R_xi link coordinates",
            "unitary_gauge_quotient": (
                "formal dimension subtraction of 22 source-orbit profiles and 4x46 link "
                "Goldstones; no 465x22 orbit map or Z-orthogonal projector is supplied"
            ),
        },
        "physical_identification_status": {
            "status": "OPEN_NOT_A_V47_V49_SAME_ACTION_CERTIFICATE",
            "missing_maps": [
                "explicit V47 465x465 Hessian pullback in a representation-respecting basis",
                "rank-22 orbit map Q, Z-orthogonal projector and Ward identity M Q=0",
                "coupled five-Goldstone R_xi block from [B; e_N^T] for each broken generator",
                "normalized Spin(10) invariant-tensor lift of every A/Xi/C/R7/R8/Z block",
                "endpoint-auxiliary representations, charges and anomaly-safe pairing",
            ],
        },
        "sector_multiplicities": copy.deepcopy(matrices["sector_multiplicities"]),
        "matrix_sha256": {
            name: matrix_sha256(value)
            for name, value in matrices.items()
            if isinstance(value, np.ndarray)
        },
        "coefficient_generators": {
            "collar": "deterministic_collar_data(4), epsilon=0.055",
            "endpoint_seeds": [601, 611],
            "complex_phase_seeds": {
                "collar": 89,
                "source_physical": 73,
                "source_gauge_orbit": 79,
            },
        },
    }


_FROZEN_MATRICES = _build_compressed_action_matrices()
ACTION_SPEC = _action_manifest_from_matrices(_FROZEN_MATRICES)
_ACTION_BYTES = canonical_bytes(ACTION_SPEC)
SHARED_ACTION_SHA256 = hashlib.sha256(_ACTION_BYTES).hexdigest()


def canonical_action_bytes() -> bytes:
    return bytes(_ACTION_BYTES)


def action_manifest() -> dict[str, Any]:
    return copy.deepcopy(ACTION_SPEC)


def action_fingerprint() -> str:
    return SHARED_ACTION_SHA256


def compressed_action_matrices() -> dict[str, Any]:
    return copy.deepcopy(_FROZEN_MATRICES)


def assert_matrix_fingerprint(matrices: Mapping[str, Any]) -> None:
    observed = {
        name: matrix_sha256(value)
        for name, value in matrices.items()
        if isinstance(value, np.ndarray)
    }
    if observed != ACTION_SPEC["matrix_sha256"]:
        raise RuntimeError("compressed matrices do not match canonical ACTION_SPEC")


__all__ = [
    "ACTION_SPEC",
    "SHARED_ACTION_SHA256",
    "N_CELLS",
    "N_CHANNELS",
    "SPINOR_COMPONENTS",
    "SOURCE_COMPONENTS",
    "SOURCE_PHYSICAL_COMPONENTS",
    "SOURCE_GAUGE_ORBIT_COMPONENTS",
    "GAUGE_DIMENSION",
    "UNBROKEN_GAUGE_DIMENSION",
    "BROKEN_GAUGE_DIMENSION",
    "EPSILON",
    "SPACING",
    "TRANSPORT_SCALE",
    "GAUGE_COUPLING",
    "LINK_VEV",
    "LINK_KAHLER_SCALE",
    "SOURCE_PHYSICAL_MASS",
    "SOURCE_GAUGE_ORBIT_MASS",
    "canonical_action_bytes",
    "action_manifest",
    "action_fingerprint",
    "compressed_action_matrices",
    "matrix_sha256",
    "assert_matrix_fingerprint",
]
