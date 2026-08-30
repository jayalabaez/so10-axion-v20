#!/usr/bin/env python3
"""V51 representation-faithful finite SUSY mediator/moose candidate.

This file tests a possible *new microscopic route* for the open SUSY G2
problem.  It is a finite four-dimensional N=1 product-group quiver, not a
continuum fifth dimension and not the abstract four-channel identity witness
of V50.  The construction uses the repository's convention-locked Spin(10)
Clifford matrices to build a vector/spinor link whose local F-flat tangent
space is exactly the 45-dimensional complexified Spin(10) orbit.

What is executable here:

* a 567 by 612 Gaussian-integer Jacobian for the covariant link constraints;
* an exact finite-field rank certificate and all 45 explicit null tangents;
* the PS endpoint Clifford projector (rank 8 in each spinor chirality);
* rectangular nearest-neighbour hopping with 32 and only 32 chiral profiles;
* ordinary perturbative endpoint/site anomaly ledgers; and
* the exact tree-level elimination identity for vectorlike channel mediators.

What is not claimed: a global classification of the nonlinear link variety,
a lifting mechanism for the 12 residual combined-endpoint A5-like chirals,
a full interacting physical pencil, a one-loop matching calculation, or the
final component Wilson array.
Consequently this is an algebraically explicit candidate architecture, not a
controlled UV completion and not a G2 closure.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
from scipy.linalg import expm

import exact_normalized_so10_yukawa_cgcs_v20 as yukawa


ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "SUSY_V51_REPRESENTATION_FAITHFUL_MEDIATOR_MOOSE_AUDIT.json"
MD_PATH = ROOT / "SUSY_V51_REPRESENTATION_FAITHFUL_MEDIATOR_MOOSE_AUDIT.md"
TEST_PATH = ROOT / "test_susy_v51_representation_faithful_mediator_moose_audit.py"

STATUS = (
    "V51_FINITE_4D_N1_CLIFFORD_LOCKED_PS_TO_SPIN10_MOOSE_CANDIDATE__"
    "EXACT_LOCAL_LINK_NULLITY45_AND_NO_UNEATEN_LINEARIZED_LINK_MODULUS__"
    "PS_PROJECTED_RECTANGULAR_HOPPING_HAS_EXACTLY32_CHIRAL_PROFILES__"
    "ORDINARY_LOCAL_POLYNOMIAL_ANOMALY_LEDGERS_CANCEL__"
    "ONE_LOOP_SPIN10_LANDAU_WINDOW_BELOW1P70_IS_SERIOUS_BLOCKER__"
    "SOURCE_HESSIAN_WARD_EXACT__12_A5_LIKE_CHIRALS_REMAIN__"
    "ONE_LOOP_MATCHING_AND_WILSON_ARRAY_OPEN__"
    "CANDIDATE_NOT_G2_CLOSURE"
)

N_CELLS = 4
SPINOR_DIMENSION = 16
VECTOR_DIMENSION = 10
LINK_VARIABLE_DIMENSION = 10 * 10 + 2 * 16 * 16
LINK_CONSTRAINT_DIMENSION = 55 + 2 * 256
LINK_GOLDSTONE_DIMENSION = 45

UPSTREAM_PATHS = (
    ROOT / "SUSY_V45_RECONCILED_BULK_SPINOR_AUDIT.json",
    ROOT / "SUSY_V46_SOURCE_HIGGS_RANK_AUDIT.json",
    ROOT / "SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json",
    ROOT / "SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.json",
    ROOT / "SUSY_V50_FINITE_MOOSE_SAME_ACTION_BRIDGE_AUDIT.json",
    ROOT / "SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.json",
    ROOT / "SUSY_V51_CARTESIAN_SOURCE_HESSIAN_AUDIT.json",
    ROOT / "SUSY_V51_CARTESIAN_MEDIATOR_C5_C7_FEASIBILITY_AUDIT.json",
    ROOT / "exact_normalized_so10_yukawa_cgcs_v20.py",
)

SPINOR_SPECIES = (
    {
        "name": "HLF",
        "Spin10_rep": "16",
        "chirality": -1,
        "qF": 1,
        "host_eta": 1,
        "host_PS_rep": "(4,2,1)",
        "host_rep_key": "L4",
    },
    {
        "name": "HLA",
        "Spin10_rep": "bar16",
        "chirality": 1,
        "qF": -4,
        "host_eta": 1,
        "host_PS_rep": "(bar4,2,1)",
        "host_rep_key": "Lbar4",
    },
    {
        "name": "HRA",
        "Spin10_rep": "16",
        "chirality": -1,
        "qF": -1,
        "host_eta": -1,
        "host_PS_rep": "(bar4,1,2)",
        "host_rep_key": "Rbar4",
    },
    {
        "name": "HRF",
        "Spin10_rep": "bar16",
        "chirality": 1,
        "qF": 4,
        "host_eta": -1,
        "host_PS_rep": "(4,1,2)",
        "host_rep_key": "R4",
    },
)

PS_REPS = {
    "L4": {"dimension": 8, "indices_2T": (2, 4, 0), "SU4_cubic": 2},
    "Lbar4": {"dimension": 8, "indices_2T": (2, 4, 0), "SU4_cubic": -2},
    "Rbar4": {"dimension": 8, "indices_2T": (2, 0, 4), "SU4_cubic": -2},
    "R4": {"dimension": 8, "indices_2T": (2, 0, 4), "SU4_cubic": 2},
    "H": {"dimension": 4, "indices_2T": (0, 2, 2), "SU4_cubic": 0},
}

PS_ANOMALY_KEYS = (
    "U1F_SU4_squared_doubled",
    "U1F_SU2L_squared_doubled",
    "U1F_SU2R_squared_doubled",
    "gravity_squared_U1F",
    "U1F_cubed",
    "SU4_cubed",
)


Array = np.ndarray


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha(value: Mapping[str, Any]) -> str:
    payload = copy.deepcopy(dict(value))
    payload.pop("core_sha256", None)
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def matrix_sha256(matrix: Array) -> str:
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


def maximum_abs(matrix: Array) -> float:
    return float(np.max(np.abs(matrix))) if matrix.size else 0.0


def _clifford_blocks() -> tuple[Array, Array, Array, dict[tuple[int, int], Array], dict[tuple[int, int], Array]]:
    gamma, _, charge_conjugation = yukawa._clifford_data()
    minus = yukawa.chiral_indices(-1)
    plus = yukawa.chiral_indices(1)
    gamma_minus_plus = np.asarray(
        [item[np.ix_(minus, plus)] for item in gamma], dtype=np.complex128
    )
    pairing = np.asarray(
        charge_conjugation[np.ix_(minus, plus)], dtype=np.complex128
    )
    return (
        np.asarray(gamma, dtype=np.complex128),
        gamma_minus_plus,
        pairing,
        yukawa.twice_spin_generators(-1),
        yukawa.twice_spin_generators(1),
    )


def link_constraint_jacobians() -> dict[str, Array]:
    """Linearize the three covariant link equations at L=U_-=U_+=1.

    Variables are ordered as ``ell(10x10), u_-(16x16), u_+(16x16)``.
    The equations are

      Sym(L^T L-I)=0,
      U_-^T B U_+-B=0,
      E=sum_a F_a Gamma_a^dagger=0,
      F_a=U_- Gamma_a-sum_b L_ab Gamma_b U_+.

    ``E`` is a product-group covariant bifundamental equation: the right
    vector and negative-spinor indices in ``F_a Gamma_a^dagger`` contract
    with invariant right-site Clifford tensors.  Every multiplier term is
    linear, quadratic or cubic in chiral superfields.
    """

    _, gamma, pairing, _, _ = _clifford_blocks()
    n_variables = LINK_VARIABLE_DIMENSION
    minus_offset = 100
    plus_offset = 100 + 256

    full_clifford = np.zeros((10, 16, 16, n_variables), dtype=np.complex128)
    for a in range(10):
        for row in range(16):
            for column in range(16):
                for middle in range(16):
                    full_clifford[a, row, column, minus_offset + row * 16 + middle] += gamma[
                        a, middle, column
                    ]
                    full_clifford[a, row, column, plus_offset + middle * 16 + column] -= gamma[
                        a, row, middle
                    ]
                for b in range(10):
                    full_clifford[a, row, column, a * 10 + b] -= gamma[
                        b, row, column
                    ]

    orthogonality_rows: list[Array] = []
    for a in range(10):
        for b in range(a, 10):
            row = np.zeros(n_variables, dtype=np.complex128)
            row[a * 10 + b] += 1.0
            row[b * 10 + a] += 1.0
            orthogonality_rows.append(row)
    orthogonality = np.asarray(orthogonality_rows, dtype=np.complex128)

    invariant_pairing = np.zeros((16, 16, n_variables), dtype=np.complex128)
    for row in range(16):
        for column in range(16):
            for middle in range(16):
                invariant_pairing[
                    row, column, minus_offset + middle * 16 + row
                ] += pairing[middle, column]
                invariant_pairing[
                    row, column, plus_offset + middle * 16 + column
                ] += pairing[row, middle]

    # F_a Gamma_a^dagger is an S-_L x S-_R^* bifundamental.  This is the
    # covariant 256-equation contraction that removes precisely the second
    # 1+45+210 normal block without introducing redundant multipliers.
    contracted_clifford = np.zeros((16, 16, n_variables), dtype=np.complex128)
    for a in range(10):
        contracted_clifford += np.einsum(
            "imv,km->ikv", full_clifford[a], gamma[a].conjugate()
        )

    minimal = np.vstack(
        (
            orthogonality,
            invariant_pairing.reshape(256, n_variables),
            contracted_clifford.reshape(256, n_variables),
        )
    )
    without_pairing = np.vstack(
        (orthogonality, full_clifford.reshape(2560, n_variables))
    )
    return {
        "minimal": minimal,
        "orthogonality": orthogonality,
        "invariant_pairing": invariant_pairing.reshape(256, n_variables),
        "contracted_clifford": contracted_clifford.reshape(256, n_variables),
        "full_clifford": full_clifford.reshape(2560, n_variables),
        "without_pairing": without_pairing,
    }


def gaussian_integer_mod_rank(
    matrix: Array, prime: int = 13, image_of_i: int = 5
) -> tuple[int, list[int], float]:
    """Exact rank lower bound via Z[i] -> F_p, i |-> image_of_i."""

    if (image_of_i * image_of_i + 1) % prime != 0:
        raise ValueError("image_of_i must square to -1 modulo prime")
    value = np.asarray(matrix, dtype=np.complex128)
    real = np.rint(value.real).astype(np.int64)
    imaginary = np.rint(value.imag).astype(np.int64)
    integer_residual = max(
        maximum_abs(value.real - real), maximum_abs(value.imag - imaginary)
    )
    if integer_residual > 1.0e-12:
        raise ValueError("Jacobian is not Gaussian-integer valued")
    finite = (real + image_of_i * imaginary) % prime
    rank = 0
    pivot_columns: list[int] = []
    for column in range(finite.shape[1]):
        candidates = np.flatnonzero(finite[rank:, column])
        if not len(candidates):
            continue
        pivot = rank + int(candidates[0])
        finite[[rank, pivot]] = finite[[pivot, rank]]
        inverse = pow(int(finite[rank, column]), -1, prime)
        finite[rank] = (finite[rank] * inverse) % prime
        nonzero = np.flatnonzero(finite[:, column])
        nonzero = nonzero[nonzero != rank]
        finite[nonzero] = (
            finite[nonzero]
            - finite[nonzero, column, None] * finite[rank]
        ) % prime
        pivot_columns.append(column)
        rank += 1
        if rank == finite.shape[0]:
            break
    return rank, pivot_columns, integer_residual


def explicit_spin_tangents() -> Array:
    """The 45 infinitesimal simultaneous Spin(10) link rotations."""

    _, _, _, spin_minus, spin_plus = _clifford_blocks()
    columns: list[Array] = []
    for a in range(10):
        for b in range(a + 1, 10):
            ell = np.zeros((10, 10), dtype=np.complex128)
            ell[a, b] = 1.0
            ell[b, a] = -1.0
            u_minus = -0.5 * np.asarray(spin_minus[(a, b)], dtype=np.complex128)
            u_plus = -0.5 * np.asarray(spin_plus[(a, b)], dtype=np.complex128)
            columns.append(
                np.concatenate((ell.reshape(-1), u_minus.reshape(-1), u_plus.reshape(-1)))
            )
    return np.column_stack(columns)


def nonlinear_spin_orbit_residuals() -> dict[str, Any]:
    """Check finite relative Spin rotations solve all nonlinear link equations."""

    _, gamma, pairing, spin_minus, spin_plus = _clifford_blocks()
    trials = ((0, 1, 0.37), (2, 7, -0.22), (4, 9, 0.19))
    rows: list[dict[str, Any]] = []
    for a, b, angle in trials:
        vector_generator = np.zeros((10, 10), dtype=np.complex128)
        vector_generator[a, b] = 1.0
        vector_generator[b, a] = -1.0
        link_vector = expm(angle * vector_generator)
        link_minus = expm(-0.5 * angle * spin_minus[(a, b)])
        link_plus = expm(-0.5 * angle * spin_plus[(a, b)])
        full = np.asarray(
            [
                link_minus @ gamma[index]
                - sum(
                    link_vector[index, target] * gamma[target] @ link_plus
                    for target in range(10)
                )
                for index in range(10)
            ]
        )
        contracted = sum(
            full[index] @ gamma[index].conjugate().T for index in range(10)
        )
        rows.append(
            {
                "generator": [a, b],
                "angle": angle,
                "orthogonality_residual": maximum_abs(
                    link_vector.T @ link_vector - np.eye(10)
                ),
                "pairing_residual": maximum_abs(
                    link_minus.T @ pairing @ link_plus - pairing
                ),
                "full_Clifford_residual": maximum_abs(full),
                "contracted_Clifford_residual": maximum_abs(contracted),
            }
        )
    return {
        "trials": rows,
        "worst_residual": max(
            max(
                row["orthogonality_residual"],
                row["pairing_residual"],
                row["full_Clifford_residual"],
                row["contracted_Clifford_residual"],
            )
            for row in rows
        ),
        "scope": (
            "finite relative group-orbit covariance checks; not a global solution-variety classification"
        ),
    }


def link_rigidity_certificate() -> dict[str, Any]:
    jacobians = link_constraint_jacobians()
    jacobian = jacobians["minimal"]
    rank, pivots, integer_residual = gaussian_integer_mod_rank(jacobian)
    rank_without_pairing, _, _ = gaussian_integer_mod_rank(
        jacobians["without_pairing"]
    )
    tangents = explicit_spin_tangents()
    twice_tangents = 2.0 * tangents
    tangent_rank, _, tangent_integer_residual = gaussian_integer_mod_rank(
        twice_tangents.T
    )
    tangent_residual = maximum_abs(jacobian @ tangents)
    nonlinear_orbit = nonlinear_spin_orbit_residuals()

    return {
        "vacuum": "L=I_10, U_-=I_16, U_+=I_16, all constraint multipliers=0",
        "link_fields": {
            "L": "(10_left,10_right), qF=0",
            "U_minus": "(16_left,bar16_right), qF=0",
            "U_plus": "(bar16_left,16_right), qF=0",
        },
        "holomorphic_constraints": {
            "orthogonality_55": "Sym[L^T L-v^2 I_10]=0 in 1+54",
            "invariant_pairing_256": "U_-^T B_left U_+-B_right=0 in 1+45+210",
            "contracted_Clifford_256": (
                "E=sum_a (U_- Gamma_a-sum_b L_ab Gamma_b U_+) "
                "Gamma_a^dagger=0, a product-group bifundamental whose diagonal "
                "content is 1+45+210"
            ),
            "multiplier_superpotential": (
                "W_link=Y54:Sym(L^T L-v^2 I)+YB:(U_-^T B U_+-B)+YE:E; "
                "every monomial has degree at most three"
            ),
        },
        "multiplier_representation_table": [
            {
                "field": "Y_O",
                "representation": "(1_left,1+54_right)",
                "pairs_with": "Sym(L^T L-v^2 I)",
                "complex_components": 55,
            },
            {
                "field": "Y_B",
                "representation": "(1_left,1+45+210_right)",
                "pairs_with": "U_-^T B_left U_+-B_right",
                "complex_components": 256,
            },
            {
                "field": "Y_E",
                "representation": "(bar16_left,16_right)",
                "pairs_with": "E in (16_left,bar16_right)",
                "complex_components": 256,
                "diagonal_restriction": "1+45+210",
            },
        ],
        "representation_covariance": (
            "Each multiplier is in the contragredient representation of its "
            "constraint. On the PS host edge the left Spin(10) factors are restricted "
            "to SU(4)xSU(2)LxSU(2)R. The contractions are therefore gauge invariant "
            "before any diagonal-site identification is made."
        ),
        "variable_dimension": int(jacobian.shape[1]),
        "constraint_dimension": int(jacobian.shape[0]),
        "constraint_block_dimensions": [55, 256, 256],
        "diagonal_multiplier_content": "3 x 1 + 1 x 54 + 2 x 45 + 2 x 210 = 567",
        "jacobian_sha256": matrix_sha256(jacobian),
        "Gaussian_integer_entry_residual": integer_residual,
        "finite_field": {"prime": 13, "image_of_i": 5, "i_squared": 12},
        "modular_rank": rank,
        "certified_minor_shape": [rank, rank],
        "certified_minor_nonzero_mod_prime": (
            rank == jacobian.shape[0] and len(pivots) == jacobian.shape[0]
        ),
        "pivot_column_count": len(pivots),
        "pivot_columns": pivots,
        "pivot_columns_sha256": hashlib.sha256(canonical_bytes(pivots)).hexdigest(),
        "explicit_tangent_count": int(tangents.shape[1]),
        "explicit_tangent_rank": tangent_rank,
        "twice_tangent_Gaussian_integer_residual": tangent_integer_residual,
        "all_tangent_constraint_residual": tangent_residual,
        "finite_group_orbit_certificate": nonlinear_orbit,
        "complex_rank_upper_bound_from_45_kernel_vectors": (
            LINK_VARIABLE_DIMENSION - tangent_rank
        ),
        "complex_rank_exact": rank,
        "complex_nullity_exact": LINK_VARIABLE_DIMENSION - rank,
        "without_invariant_pairing_full_Clifford_rank": rank_without_pairing,
        "without_invariant_pairing_nullity": (
            LINK_VARIABLE_DIMENSION - rank_without_pairing
        ),
        "extra_modulus_without_pairing": (
            LINK_VARIABLE_DIMENSION - rank_without_pairing - LINK_GOLDSTONE_DIMENSION
        ),
        "local_SUSY_Higgs_conclusion": (
            "with canonical positive Kahler metrics and nonzero multiplier couplings, "
            "567 normal link chirals pair with 567 multipliers; the remaining 45 "
            "complex directions are precisely the broken relative Spin(10) orbit and "
            "are eaten.  This is a tangent-space theorem at the identity vacuum."
        ),
        "global_scope": (
            "No claim is made that the nonlinear constraint variety has no remote or "
            "singular branches; only the identity component is locally rigid."
        ),
    }


def ps_parity_certificate() -> dict[str, Any]:
    gamma, _, _, spin_minus, spin_plus = _clifford_blocks()
    full_parity = gamma[6] @ gamma[7] @ gamma[8] @ gamma[9]
    data: dict[str, Any] = {}
    for chirality, generators in ((-1, spin_minus), (1, spin_plus)):
        indices = yukawa.chiral_indices(chirality)
        parity = full_parity[np.ix_(indices, indices)]
        plus_projector = 0.5 * (np.eye(16) + parity)
        minus_projector = 0.5 * (np.eye(16) - parity)
        centralizer_residuals = [
            maximum_abs(parity @ generator - generator @ parity)
            for generator in generators.values()
        ]
        data[str(chirality)] = {
            "parity_sha256": matrix_sha256(parity),
            "Hermitian_residual": maximum_abs(parity - parity.conjugate().T),
            "involution_residual": maximum_abs(parity @ parity - np.eye(16)),
            "trace": float(np.trace(parity).real),
            "plus_projector_rank": int(np.linalg.matrix_rank(plus_projector)),
            "minus_projector_rank": int(np.linalg.matrix_rank(minus_projector)),
            "commuting_Spin10_generator_count": sum(
                residual < 1.0e-12 for residual in centralizer_residuals
            ),
            "noncommuting_Spin10_generator_count": sum(
                residual >= 1.0e-12 for residual in centralizer_residuals
            ),
        }
    return {
        "Cartesian_definition": "P_PS=Gamma_6 Gamma_7 Gamma_8 Gamma_9",
        "unbroken_centralizer": "Spin(6)xSpin(4) ~= SU(4)xSU(2)LxSU(2)R",
        "chirality_blocks": data,
        "species_selection": [
            {
                "field": field["name"],
                "chirality": field["chirality"],
                "selected_eigenvalue": field["host_eta"],
                "selected_rank": 8,
                "declared_PS_zero_mode": field["host_PS_rep"],
            }
            for field in SPINOR_SPECIES
        ],
        "phase_scope": (
            "The rank/eigenprojector is explicit in the locked Cartesian basis.  A "
            "common-phase Cartesian-to-PS component intertwiner is still required "
            "before declaring entrywise PS Wilson coefficients."
        ),
    }


def hopping_matrices(num_cells: int = N_CELLS) -> tuple[Array, Array]:
    desired = np.zeros((num_cells, num_cells + 1), dtype=np.float64)
    for edge in range(num_cells):
        desired[edge, edge] = 1.0
        desired[edge, edge + 1] = -1.0
    unwanted = np.zeros((num_cells, num_cells), dtype=np.float64)
    unwanted[0, 0] = -1.0
    for edge in range(1, num_cells):
        unwanted[edge, edge - 1] = 1.0
        unwanted[edge, edge] = -1.0
    return desired, unwanted


def hopping_certificate() -> dict[str, Any]:
    desired, unwanted = hopping_matrices()
    desired_singular = np.linalg.svd(desired, compute_uv=False)
    unwanted_singular = np.linalg.svd(unwanted, compute_uv=False)
    desired_formula = sorted(
        2.0 * math.sin(k * math.pi / (2 * (N_CELLS + 1)))
        for k in range(1, N_CELLS + 1)
    )
    unwanted_formula = sorted(
        2.0 * math.sin((2 * k - 1) * math.pi / (4 * N_CELLS + 2))
        for k in range(1, N_CELLS + 1)
    )
    return {
        "fundamental_superpotential": (
            "W_hop=sum_(alpha,j) P_(alpha,j)^T [M_alpha X_(alpha,j)-"
            "lambda_alpha U_(chirality(alpha),j) X_(alpha,j+1)]"
        ),
        "link_vacuum_condition": "lambda_alpha <U_chi,j>=M_alpha I_16",
        "theory_space_locality": (
            "P_j X_j is site-local and P_j U_j X_(j+1) is a nearest-neighbour "
            "cubic; no fundamental endpoint-to-interior product occurs"
        ),
        "host_projection": (
            "X_0 contains only Pi_eta components; P_0 is a full PS-decomposed "
            "dual. Desired components have a 4x5 incidence matrix, while unwanted "
            "components have an anchored 4x4 matrix."
        ),
        "desired_matrix_shape": list(desired.shape),
        "desired_rank": int(np.linalg.matrix_rank(desired)),
        "desired_nullity": int(desired.shape[1] - np.linalg.matrix_rank(desired)),
        "desired_singular_values": [float(x) for x in sorted(desired_singular)],
        "desired_formula_residual": maximum_abs(
            np.asarray(sorted(desired_singular)) - np.asarray(desired_formula)
        ),
        "unwanted_matrix_shape": list(unwanted.shape),
        "unwanted_rank": int(np.linalg.matrix_rank(unwanted)),
        "unwanted_nullity": int(unwanted.shape[1] - np.linalg.matrix_rank(unwanted)),
        "unwanted_determinant": float(np.linalg.det(unwanted)),
        "unwanted_singular_values": [float(x) for x in sorted(unwanted_singular)],
        "unwanted_formula_residual": maximum_abs(
            np.asarray(sorted(unwanted_singular)) - np.asarray(unwanted_formula)
        ),
        "full_spinor_species": len(SPINOR_SPECIES),
        "selected_components_per_species": 8,
        "unwanted_components_per_species": 8,
        "total_X_coordinates": 4 * (8 * 5 + 8 * 4),
        "total_P_coordinates": 4 * 16 * 4,
        "total_transport_rank": 4 * (8 * 4 + 8 * 4),
        "total_chiral_profile_count": 4 * 8,
        "additional_uncontrolled_transport_zero_modes": 0,
        "smallest_heavy_mass_in_units_of_min_M": float(
            min(np.min(desired_singular), np.min(unwanted_singular))
        ),
        "single_U1F_redesign": (
            "U(1)F is one four-dimensional gauge factor shared by all sites, not a "
            "deconstructed U(1)F tower.  This keeps every charged hopping term cubic "
            "with neutral Spin(10) links, but is new physics relative to V50."
        ),
    }


def source_orbit_binding() -> dict[str, Any]:
    """Bind to, and independently hash-check, the V51 exact source orbit."""

    path = ROOT / "SUSY_V51_PHYSICAL_SOURCE_ORBIT_AUDIT.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    observed_core = source["core_sha256"]
    payload = copy.deepcopy(source)
    payload.pop("core_sha256")
    recomputed_core = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    orbit = source["orbit_and_projector_certificate"]
    gram = orbit["selected_Gram"]
    published_q = orbit["selected_broken_map_Q"]
    u1f_column = published_q["column_labels"].index("U1F")
    u1f_sparse_entries = [
        entry for entry in published_q["sparse_entries"]
        if entry["column"] == u1f_column
    ]
    diagonal = [int(value) for value in gram["diagonal"]]
    return {
        "path": path.name,
        "file_sha256": sha256_file(path),
        "declared_core_sha256": observed_core,
        "recomputed_core_sha256": recomputed_core,
        "canonical_core_valid": observed_core == recomputed_core,
        "status": source["status"],
        "Q_shape": orbit["selected_broken_map_Q"]["shape"],
        "Q_sha256": orbit["selected_broken_map_Q"]["canonical_matrix_sha256"],
        "Q_exact_rank": gram["exact_rank"],
        "Gram_diagonal": diagonal,
        "Gram_off_diagonal_exact_zero": gram["off_diagonal_exact_zero"],
        "Gram_positive_definite": gram["positive_definite"],
        "published_U1F_column_sparse_entries": u1f_sparse_entries,
        "published_U1F_Theta_charges": [3, -3],
        "published_U1F_column_matches_Theta_charges": u1f_sparse_entries
        == [
            {"column": u1f_column, "row": 463, "value_re_im": ["0", "3"]},
            {"column": u1f_column, "row": 464, "value_re_im": ["0", "-3"]},
        ],
        "projector_shape": orbit["physical_projector_Z"]["shape"],
        "projector_rank": orbit["physical_projector_Z"]["rank"],
        "projector_sha256": orbit["physical_projector_Z"][
            "canonical_projector_sha256"
        ],
        "physical_source_components": orbit["counting"][
            "physical_complex_components"
        ],
        "Hessian_scope": source["hessian_availability"],
    }


def source_hessian_binding() -> dict[str, Any]:
    """Bind to the exact V51 Cartesian source Hessian and Ward certificate."""

    path = ROOT / "SUSY_V51_CARTESIAN_SOURCE_HESSIAN_AUDIT.json"
    source = json.loads(path.read_text(encoding="utf-8"))
    observed_core = source["core_sha256"]
    payload = copy.deepcopy(source)
    payload.pop("core_sha256")
    recomputed_core = hashlib.sha256(canonical_bytes(payload)).hexdigest()
    hessian = source["hessian_certificate"]
    rank = hessian["exact_rank_proof"]
    ward = hessian["Ward_identity"]
    pullback = hessian["physical_pullback"]
    stationarity = source["stationarity_certificate"]
    return {
        "path": path.name,
        "file_sha256": sha256_file(path),
        "declared_core_sha256": observed_core,
        "recomputed_core_sha256": recomputed_core,
        "canonical_core_valid": observed_core == recomputed_core,
        "status": source["status"],
        "all_465_F_terms_exact_zero": stationarity[
            "all_465_F_terms_exact_zero"
        ],
        "H_shape": hessian["published_H"]["shape"],
        "H_sha256": hessian["published_H"]["canonical_H_sha256"],
        "H_complex_symmetric": hessian["exact_structure"][
            "complex_symmetric_H_transpose_equals_H"
        ],
        "H_exact_rank": rank["exact_rank_H"],
        "H_exact_nullity": rank["exact_nullity_H"],
        "kernel_equals_gauge_orbit": rank["kernel_equals_gauge_orbit"],
        "HQ_exact_zero_all_46_columns": ward["HQ_exact_zero_all_46_columns"],
        "physical_pullback_shape": pullback["shape"],
        "physical_pullback_rank_mod_13": pullback["rank_mod_13"],
        "physical_pullback_determinant_mod_13": pullback[
            "determinant_mod_13"
        ],
        "physical_pullback_nondegenerate": pullback[
            "nondegenerate_over_characteristic_zero"
        ],
        "tuning_scope": stationarity["matching_scale_tuning"],
    }


def source_side_rxi_certificate() -> dict[str, Any]:
    """Exact finite-dimensional source/link Goldstone singular pairing.

    This is the full source-side Spin(10) chain before the host PS vector
    projection is imposed.  The latter mixes the PS/SU(5) generator classes
    and remains a separate, explicitly listed obligation.
    """

    source = source_orbit_binding()
    hessian = source_hessian_binding()
    gram = source["Gram_diagonal"]
    if gram != [2] + [7] * 20 + [18]:
        raise RuntimeError("source-orbit Gram diagonal drifted")
    incidence, _ = hopping_matrices()
    endpoint = np.zeros((1, N_CELLS + 1), dtype=np.float64)
    endpoint[0, -1] = 1.0

    unbroken_vector = incidence.T @ incidence
    unbroken_goldstone = incidence @ incidence.T
    vector_nonzero = np.linalg.eigvalsh(unbroken_vector)[1:]
    goldstone_nonzero = np.linalg.eigvalsh(unbroken_goldstone)

    broken_rows: list[dict[str, Any]] = []
    worst_pairing = 0.0
    smallest_positive = math.inf
    for index, norm_squared in enumerate(gram[:-1]):
        augmented = np.vstack((incidence, math.sqrt(norm_squared) * endpoint))
        vector = augmented.T @ augmented
        goldstone = augmented @ augmented.T
        vector_spectrum = np.linalg.eigvalsh(vector)
        goldstone_spectrum = np.linalg.eigvalsh(goldstone)
        pairing = maximum_abs(vector_spectrum - goldstone_spectrum)
        worst_pairing = max(worst_pairing, pairing)
        smallest_positive = min(smallest_positive, float(np.min(vector_spectrum)))
        broken_rows.append(
            {
                "source_column": index,
                "source_orbit_norm_squared": norm_squared,
                "D_shape": list(augmented.shape),
                "D_rank": int(np.linalg.matrix_rank(augmented)),
                "det_D_abs": float(abs(np.linalg.det(augmented))),
                "vector_Goldstone_spectral_pairing_residual": pairing,
                "minimum_mass_squared_at_unit_link_scale": float(
                    np.min(vector_spectrum)
                ),
            }
        )

    u1_norm = gram[-1]
    primitive_theta_charges = [3, -3]
    primitive_theta_norm = sum(charge * charge for charge in primitive_theta_charges)
    if (
        not source["published_U1F_column_matches_Theta_charges"]
        or primitive_theta_norm != u1_norm
    ):
        raise RuntimeError("candidate/source U(1)F normalization mismatch")
    # Resolve the two endpoint stabilizers.  PS cap SU(5) is the 12-generator
    # SM algebra.  A generator absent at the host has only the four Spin(10)
    # site-vector coordinates 1,...,N, so the anchored matrix is used.
    anchored = hopping_matrices()[1]
    anchored_endpoint = np.zeros((1, N_CELLS), dtype=np.float64)
    anchored_endpoint[0, -1] = 1.0
    neither_rows: list[dict[str, Any]] = []
    for norm_squared in (2, 7):
        neither = np.vstack(
            (anchored, math.sqrt(norm_squared) * anchored_endpoint)
        )
        vector_spectrum = np.linalg.eigvalsh(neither.T @ neither)
        goldstone_spectrum = np.linalg.eigvalsh(neither @ neither.T)
        neither_rows.append(
            {
                "source_orbit_norm_squared": norm_squared,
                "D_shape": list(neither.shape),
                "D_rank": int(np.linalg.matrix_rank(neither)),
                "vector_zero_modes": int(
                    np.count_nonzero(np.abs(vector_spectrum) < 1.0e-12)
                ),
                "Goldstone_zero_modes": int(
                    np.count_nonzero(np.abs(goldstone_spectrum) < 1.0e-12)
                ),
                "nonzero_spectral_pairing_residual": maximum_abs(
                    vector_spectrum - goldstone_spectrum[1:]
                ),
            }
        )
    combined_endpoint = {
        "generator_partition": {
            "PS_intersection_SU5__SM": 12,
            "PS_only": 9,
            "SU5_only": 12,
            "neither": 12,
            "sum": 45,
        },
        "both_SM": {
            "D_shape": list(incidence.shape),
            "D_rank": int(np.linalg.matrix_rank(incidence)),
            "massless_vectors_per_generator": 1,
            "uneaten_chirals_per_generator": 0,
        },
        "PS_only": {
            "D_shape": [N_CELLS + 1, N_CELLS + 1],
            "D_rank": N_CELLS + 1,
            "massless_vectors_per_generator": 0,
            "uneaten_chirals_per_generator": 0,
        },
        "SU5_only": {
            "D_shape": list(anchored.shape),
            "D_rank": int(np.linalg.matrix_rank(anchored)),
            "massless_vectors_per_generator": 0,
            "uneaten_chirals_per_generator": 0,
        },
        "neither": {
            "representative_norm_cases": neither_rows,
            "D_shape": [N_CELLS + 1, N_CELLS],
            "D_rank": N_CELLS,
            "massless_vectors_per_generator": 0,
            "uneaten_chirals_per_generator": 1,
        },
        "total_massless_SM_vectors": 12,
        "total_uneaten_A5_like_chirals": 12,
        "verdict": (
            "BLOCKER: the 12 generators in neither endpoint stabilizer have five "
            "Goldstone coordinates but only four vector coordinates. One orthogonal "
            "A5-like chiral remains per generator until an explicit host/source "
            "interaction or additional vector multiplet lifts it."
        ),
    }
    return {
        "source_orbit_input": source,
        "source_hessian_input": hessian,
        "definition": (
            "For each source-broken Spin generator, D_a=[B; sqrt(g_a)e_N^T], "
            "M_vector=D_a^dagger D_a and M_Goldstone=xi D_a D_a^dagger. "
            "For each SU(5) generator, D=B and the vector block retains one zero."
        ),
        "gauge_parameter": "xi>0; reported spectra set xi=1",
        "unbroken_Spin_generators": 24,
        "unbroken_incidence_rank": int(np.linalg.matrix_rank(incidence)),
        "unbroken_vector_zero_modes_per_generator": int(
            np.count_nonzero(np.abs(np.linalg.eigvalsh(unbroken_vector)) < 1.0e-12)
        ),
        "unbroken_nonzero_spectral_pairing_residual": maximum_abs(
            vector_nonzero - goldstone_nonzero
        ),
        "source_broken_Spin_generators": len(broken_rows),
        "source_broken_rows": broken_rows,
        "all_source_broken_D_full_rank": all(
            row["D_rank"] == N_CELLS + 1 for row in broken_rows
        ),
        "worst_broken_vector_Goldstone_pairing_residual": worst_pairing,
        "minimum_broken_mass_squared_at_unit_link_scale": smallest_positive,
        "shared_U1F": {
            "primitive_Theta_charges": primitive_theta_charges,
            "source_orbit_norm_squared": u1_norm,
            "candidate_charge_norm_squared": primitive_theta_norm,
            "candidate_source_normalization_matches": primitive_theta_norm == u1_norm,
            "link_modes": 0,
            "vector_dimension": 1,
            "Goldstone_dimension": 1,
            "vector_mass_squared_at_unit_gauge_coupling": u1_norm,
            "Goldstone_mass_squared_at_xi_1": u1_norm,
        },
        "combined_host_PS_source_SU5": combined_endpoint,
        "proved_scope": (
            "The previously missing independent-link-plus-source-zero block is replaced "
            "by one augmented D_a and has exactly paired nonzero spectra."
        ),
        "remaining_host_scope": (
            "The generator-by-generator endpoint intersection is now counted exactly "
            "and exposes 12 uneaten A5-like chirals. Their lifting interaction and the "
            "resulting full interacting Hessian are not constructed."
        ),
    }


def perturbativity_certificate(gauge_coupling: float = 0.73) -> dict[str, Any]:
    """One-loop N=1 Spin(10) index stress test above the link threshold."""

    indices = {
        "T_10": 1,
        "T_16": 2,
        "T_45": 8,
        "T_54": 12,
        "T_126": 35,
        "T_210": 56,
        "C2_adjoint_Spin10": 8,
    }
    # At either end of one edge, spectator dimensions multiply the index:
    # L: 10*T(10), U-/U+: 16*T(16) each, and the contracted-equation
    # multiplier YE is another conjugate spinor bifundamental.
    common_edge = 10 * indices["T_10"] + 3 * 16 * indices["T_16"]
    right_site_multipliers = (
        indices["T_54"]
        + indices["T_45"]
        + indices["T_210"]
    )
    left_edge_index = common_edge
    right_edge_index = common_edge + right_site_multipliers
    transport_XP_index = 8 * indices["T_16"]
    source_X_index = 4 * indices["T_16"]
    source_Higgs_index = (
        indices["T_210"] + 2 * indices["T_126"]
    )
    interior_sum = right_edge_index + left_edge_index + transport_XP_index
    source_sum = right_edge_index + source_X_index + source_Higgs_index
    three_c2 = 3 * indices["C2_adjoint_Spin10"]
    interior_b = three_c2 - interior_sum
    source_b = three_c2 - source_sum

    def pole_ratio(beta: int) -> float:
        return math.exp(8.0 * math.pi**2 / (abs(beta) * gauge_coupling**2))

    interior_ratio = pole_ratio(interior_b)
    source_ratio = pole_ratio(source_b)
    return {
        "convention": "b=3 C2(G)-sum_chiral T(R), T(10)=1",
        "gauge_coupling_at_link_scale": gauge_coupling,
        "Spin10_indices": indices,
        "per_edge_index_at_left_site": left_edge_index,
        "per_edge_index_at_right_site": right_edge_index,
        "edge_breakdown": {
            "L_10x10": 10,
            "U_minus_16xbar16": 32,
            "U_plus_bar16x16": 32,
            "YE_conjugate_spinor_bifundamental": 32,
            "right_Y54": 12,
            "right_YB_45_plus_210": 64,
        },
        "interior_site": {
            "sum_T": interior_sum,
            "three_C2": three_c2,
            "b_one_loop": interior_b,
            "Landau_pole_over_link_scale": interior_ratio,
        },
        "source_site": {
            "sum_T": source_sum,
            "three_C2": three_c2,
            "b_one_loop": source_b,
            "Landau_pole_over_link_scale": source_ratio,
            "source_Higgs_T": source_Higgs_index,
        },
        "formula": "Lambda_pole/mu_link=exp[8 pi^2/(|b| g^2)] for b<0",
        "optimism_warning": (
            "These are upper bounds on the window: resolved endpoint channel mediators "
            "and any further completion fields add positive Dynkin index and lower the pole."
        ),
        "controlled_perturbative_window": False,
        "serious_blocker": (
            "The pole occurs below 1.70 times the link threshold.  The algebraic quiver "
            "is therefore not a controlled perturbative UV completion at g=0.73."
        ),
        "nondynamical_multiplier_limit": (
            "Treating the 567 multipliers as nondynamical constraints would remove their "
            "running contribution, but contradicts the candidate's canonical positive-Kahler "
            "field contract and returns to an exact-multiplier/non-microscopic regulator."
        ),
        "remaining_possible_interpretation": (
            "Only a strongly coupled/composite UV completion or a much leaner algebraic "
            "link realization could rescue this route; neither is constructed here."
        ),
    }


def ps_anomaly(rep_key: str, qf: int, multiplicity: int = 1) -> dict[str, int]:
    rep = PS_REPS[rep_key]
    i4, i2l, i2r = rep["indices_2T"]
    return {
        "U1F_SU4_squared_doubled": multiplicity * qf * i4,
        "U1F_SU2L_squared_doubled": multiplicity * qf * i2l,
        "U1F_SU2R_squared_doubled": multiplicity * qf * i2r,
        "gravity_squared_U1F": multiplicity * qf * rep["dimension"],
        "U1F_cubed": multiplicity * qf**3 * rep["dimension"],
        "SU4_cubed": multiplicity * rep["SU4_cubic"],
    }


def add_ledgers(rows: Iterable[Mapping[str, int]]) -> dict[str, int]:
    rows = list(rows)
    return {key: sum(row[key] for row in rows) for key in PS_ANOMALY_KEYS}


def full_spinor_ps_anomaly(rep: str, qf: int) -> dict[str, int]:
    components = ("L4", "Rbar4") if rep == "16" else ("Lbar4", "R4")
    return add_ledgers(ps_anomaly(component, qf) for component in components)


def anomaly_certificate() -> dict[str, Any]:
    selected_rows = [
        {
            "field": field["name"] + "_selected",
            "rep": field["host_rep_key"],
            "qF": field["qF"],
            "ledger": ps_anomaly(field["host_rep_key"], field["qF"]),
        }
        for field in SPINOR_SPECIES
    ]
    visible_specs = (
        ("3xQ", "L4", 1, 3),
        ("3xQc", "Rbar4", -1, 3),
        ("H", "H", 0, 1),
    )
    visible_rows = [
        {
            "field": name,
            "rep": rep,
            "qF": qf,
            "multiplicity": multiplicity,
            "ledger": ps_anomaly(rep, qf, multiplicity),
        }
        for name, rep, qf, multiplicity in visible_specs
    ]
    p0_rows = [
        {
            "field": "P0_" + field["name"],
            "rep": "bar16" if field["Spin10_rep"] == "16" else "16",
            "qF": -field["qF"],
            "ledger": full_spinor_ps_anomaly(
                "bar16" if field["Spin10_rep"] == "16" else "16",
                -field["qF"],
            ),
        }
        for field in SPINOR_SPECIES
    ]
    selected_totals = add_ledgers(row["ledger"] for row in selected_rows)
    visible_totals = add_ledgers(row["ledger"] for row in visible_rows)
    p0_totals = add_ledgers(row["ledger"] for row in p0_rows)
    host_totals = add_ledgers((selected_totals, visible_totals, p0_totals))

    source_spin10_rows = [
        {
            "field": field["name"] + "_N",
            "rep": field["Spin10_rep"],
            "qF": field["qF"],
            "U1F_Spin10_squared_doubled": 4 * field["qF"],
            "gravity_squared_U1F": 16 * field["qF"],
            "U1F_cubed": 16 * field["qF"] ** 3,
            "Spin10_cubed": 0,
        }
        for field in SPINOR_SPECIES
    ]
    source_totals = {
        key: sum(row[key] for row in source_spin10_rows)
        for key in (
            "U1F_Spin10_squared_doubled",
            "gravity_squared_U1F",
            "U1F_cubed",
            "Spin10_cubed",
        )
    }

    return {
        "host_selected_rows": selected_rows,
        "host_visible_rows": visible_rows,
        "host_full_P0_rows": p0_rows,
        "host_selected_totals": selected_totals,
        "host_visible_totals": visible_totals,
        "host_full_P0_totals": p0_totals,
        "host_complete_totals": host_totals,
        "interior_sites": (
            "For j=1,...,N-1 every X_(alpha,j) has P_(alpha,j) in the "
            "conjugate Spin(10) representation and opposite qF; each pair cancels "
            "all displayed mixed, gravitational and cubic U(1)F anomalies."
        ),
        "source_spin10_rows": source_spin10_rows,
        "source_spin10_totals": source_totals,
        "source_Higgs_additions": (
            "Phi=210_0, Sigma=126_0, barSigma=bar126_0, neutral singlets, and "
            "ThetaPlus/ThetaMinus=1_(+/-3); 210 is real, 126+bar126 is "
            "vectorlike, and the charged singlets cancel pairwise"
        ),
        "link_and_multiplier_sector": (
            "qF=0 throughout. U_- and U_+ are product-group conjugates; L and "
            "the diagonal 1,45,54,210 multiplier sectors are real. Spin(10) has "
            "no perturbative cubic gauge invariant. Their complete PS restrictions "
            "contain conjugate SU(4) pairs."
        ),
        "channel_mediators": (
            "For every channel A_R B_barR, use Y_barR,-q plus Z_R,+q. The "
            "mediator pair is vectorlike under Spin(10)xU(1)F before it is integrated out."
        ),
        "global_scope": (
            "This certifies ordinary perturbative polynomial anomalies only; a "
            "global/bordism and threshold Wess-Zumino audit remains open."
        ),
    }


def mediator_elimination_certificate() -> dict[str, Any]:
    mass = np.asarray(
        [[2.1 + 0.2j, -0.3 + 0.1j], [0.4 - 0.2j, 1.7 - 0.1j]],
        dtype=np.complex128,
    )
    source_a = np.asarray([0.7 + 0.3j, -0.2 + 0.5j], dtype=np.complex128)
    source_b = np.asarray([-0.4 + 0.6j, 0.9 - 0.2j], dtype=np.complex128)
    z_solution = -np.linalg.solve(mass, source_a)
    y_solution = -np.linalg.solve(mass.T, source_b)
    f_y = mass @ z_solution + source_a
    f_z = mass.T @ y_solution + source_b
    full_w = (
        y_solution.T @ mass @ z_solution
        + y_solution.T @ source_a
        + source_b.T @ z_solution
    )
    effective_w = -source_b.T @ np.linalg.solve(mass, source_a)
    inverse_mass = np.linalg.inv(mass)
    return {
        "universal_channel_superpotential": (
            "W=Y_barR^T M Z_R + Y_barR^T A_R + B_barR^T Z_R, "
            "with deg(A),deg(B)<=2"
        ),
        "exact_tree_result": "W_eff=-B^T M^-1 A",
        "mass_matrix_sha256": matrix_sha256(mass),
        "mass_determinant_abs": float(abs(np.linalg.det(mass))),
        "F_Y_residual": maximum_abs(f_y),
        "F_Z_residual": maximum_abs(f_z),
        "effective_superpotential_residual": float(abs(full_w - effective_w)),
        "inverse_mass_finite": bool(np.all(np.isfinite(inverse_mass))),
        "renormalizability": (
            "Y A and B Z have degree at most three, Y M Z has degree two; "
            "therefore every neutral holomorphic invariant of degree at most four "
            "that is supplied with an explicit bilinear channel tensor has a finite "
            "renormalizable mediator realization"
        ),
        "decoupling": (
            "M -> infinity removes W_eff as 1/M and leaves no extra light field "
            "when det(M) is nonzero"
        ),
        "anomaly_pair_example": {
            "representation": "R plus barR",
            "charges": [7, -7],
            "gravity_U1_sum_per_rep_dimension": 0,
            "U1_cubed_sum_per_rep_dimension": 7**3 + (-7) ** 3,
            "mixed_Spin10_squared_U1_sum_per_index": 7 + (-7),
        },
    }


def operator_coverage() -> dict[str, Any]:
    retained = json.loads(
        (ROOT / "SUSY_V49_RETAINED_BOUNDARY_ACTION_COMPLETENESS.json").read_text(
            encoding="utf-8"
        )
    )
    c7 = json.loads(
        (ROOT / "SUSY_V50_C7_CONJUGATE_INCIDENCE_AUDIT.json").read_text(
            encoding="utf-8"
        )
    )
    v51_path = ROOT / "SUSY_V51_CARTESIAN_MEDIATOR_C5_C7_FEASIBILITY_AUDIT.json"
    v51 = json.loads(v51_path.read_text(encoding="utf-8"))
    v51_payload = copy.deepcopy(v51)
    v51_core = v51_payload.pop("core_sha256")
    v51_recomputed_core = hashlib.sha256(canonical_bytes(v51_payload)).hexdigest()
    inventory = v51["incidence_inventory"]
    return {
        "V51_feasibility_input": {
            "path": v51_path.name,
            "file_sha256": sha256_file(v51_path),
            "declared_core_sha256": v51_core,
            "recomputed_core_sha256": v51_recomputed_core,
            "canonical_core_valid": v51_core == v51_recomputed_core,
            "status": v51["status"],
        },
        "tree_holomorphic": {
            "pure_source_quartic_directions": retained[
                "exact_pure_source_quartic_basis"
            ]["direction_count"],
            "source_collar_schema_rows": c7["counts"]["total_rows"],
            "low_degree_rows_resolved": inventory[
                "degree_two_or_three_rows_resolved_here"
            ],
            "low_degree_nonempty": inventory["low_degree_resolution_counts"][
                "RESOLVED_NONEMPTY_CARTESIAN"
            ],
            "low_degree_empty": inventory["low_degree_resolution_counts"][
                "RESOLVED_EMPTY"
            ],
            "degree_four_rows_pending": inventory[
                "degree_four_rows_pending_factorization"
            ],
            "PS_primitives_resolved": inventory[
                "ps_total_primitive_declarations"
            ],
            "algebraic_capability": (
                "Every nonempty neutral degree<=4 invariant can be generated "
                "channel-by-channel after a normalized bilinear intertwiner and copy "
                "label are supplied. This includes cubic and quartic endpoint portals."
            ),
            "all_rows_instantiated_now": False,
            "reason": (
                "All 48 degree-two/three rows and all 34 PS primitives are resolved, "
                "but 120 degree-four factor spaces and the final Wilson array remain "
                "absent; a formal mediator for an unnamed factor is not a physical coupling."
            ),
        },
        "Kahler": {
            "tree_chiral_mediator_subset": (
                "Integrating canonical heavy chirals produces positive-semidefinite "
                "factorized A^dagger (M^dagger M)^-1 A corrections."
            ),
            "full_V49_Hermitian_basis": "NOT GENERATED OR MATCHED",
            "missing": (
                "indefinite/general mixed Kahler directions, their bare counterterms, "
                "and a positivity proof after all contributions"
            ),
        },
        "gauge_kinetic_and_FI": {
            "one_source_gauge_functions": "require explicit charged-mediator loop thresholds",
            "FI": "independent renormalized D-term datum",
            "status": "NOT COMPUTED",
        },
        "normal_derivative_and_distributed_currents": (
            "Nearest-neighbour differences provide a microscopic derivative surrogate, "
            "but the V49 source-functional jets and distributed collar currents have not "
            "been matched to finite-site couplings."
        ),
    }


def source_endpoint_contract() -> dict[str, Any]:
    return {
        "gauge_groups": {
            "site_0": "SU(4)xSU(2)LxSU(2)R",
            "sites_1_through_N": "Spin(10)",
            "U1F": (
                "one shared four-dimensional gauge factor; it is deliberately not "
                "replicated along the quiver"
            ),
        },
        "source_fields_at_N": [
            "Phi=210_0",
            "Sigma=126_0",
            "barSigma=bar126_0",
            "ThetaPlus=1_(+3)",
            "ThetaMinus=1_(-3)",
            "STheta=1_0",
        ],
        "renormalizable_source_superpotential": [
            "m Phi^2 + lambda Phi^3 + M Sigma barSigma + eta Phi Sigma barSigma",
            "kappa STheta(ThetaPlus ThetaMinus-vF^2)",
            "lambdaL ThetaPlus HLF_N HLA_N",
            "lambdaR ThetaMinus HRA_N HRF_N",
            "lambdaSigmaBar barSigma HLF_N HRA_N",
            "lambdaSigma Sigma HLA_N HRF_N",
        ],
        "displayed_U1F_charge_sums": {
            "ThetaPlus_HLF_HLA": 3 + 1 - 4,
            "ThetaMinus_HRA_HRF": -3 - 1 + 4,
            "barSigma_HLF_HRA": 1 - 1,
            "Sigma_HLA_HRF": -4 + 4,
        },
        "U1F_normalization": (
            "primitive V51 charge lattice: (HLF,HLA,HRA,HRF)=(1,-4,-1,4), "
            "visible (Q,Qc)=(1,-1), and (ThetaPlus,ThetaMinus)=(3,-3). "
            "This is the V45 integer pattern divided uniformly by three and exactly "
            "matches the bound source-orbit convention Q_U1=(+3,-3), whose unit-VEV "
            "Gram norm is 3^2+(-3)^2=18."
        ),
        "Higgs_route": (
            "Use the already certified renormalizable 210+126+bar126 source branch; "
            "the exact V51 orbit/projector and tuned-witness 465x465 Hessian/Ward "
            "certificate are bound separately and are not replaced by aggregate rank claims."
        ),
        "missing_physical_maps": [
            "an explicit local interaction that lifts the 12 neither-PS-nor-SU5 A5-like chirals",
            "the complete interacting link/source Hessian and positive physical metric",
        ],
    }


def kill_tests(report_parts: Mapping[str, Any]) -> dict[str, Any]:
    link = report_parts["link"]
    hop = report_parts["hopping"]
    rxi = report_parts["rxi"]
    perturbativity = report_parts["perturbativity"]
    mediator = report_parts["mediator"]
    coverage = report_parts["coverage"]
    return {
        "abstract_four_channel_identity_not_reused": True,
        "remove_invariant_pairing_exposes_one_Cstar_modulus": (
            link["extra_modulus_without_pairing"] == 1
        ),
        "all_45_and_only_45_link_tangents_survive_locally": (
            link["complex_nullity_exact"] == 45
            and link["explicit_tangent_rank"] == 45
            and link["all_tangent_constraint_residual"] < 1.0e-12
        ),
        "unwanted_PS_components_have_no_transport_zero_mode": (
            hop["unwanted_nullity"] == 0
        ),
        "desired_PS_components_have_one_profile_each": (
            hop["desired_nullity"] == 1
            and hop["total_chiral_profile_count"] == 32
        ),
        "nearest_neighbour_only": "nearest-neighbour" in hop["theory_space_locality"],
        "singular_mediator_mass_rejected": mediator["mass_determinant_abs"] > 0.0,
        "formal_unnamed_Haar_channel_not_promoted": not coverage["tree_holomorphic"][
            "all_rows_instantiated_now"
        ],
        "general_Kahler_not_claimed_from_chiral_tree_exchange": (
            coverage["Kahler"]["full_V49_Hermitian_basis"]
            == "NOT GENERATED OR MATCHED"
        ),
        "combined_endpoint_residual_chirals_are_not_hidden": (
            rxi["combined_host_PS_source_SU5"][
                "total_uneaten_A5_like_chirals"
            ]
            == 12
        ),
        "short_Landau_window_is_not_hidden": (
            not perturbativity["controlled_perturbative_window"]
            and perturbativity["source_site"]["Landau_pole_over_link_scale"]
            < 1.70
        ),
    }


def build_report() -> dict[str, Any]:
    link = link_rigidity_certificate()
    parity = ps_parity_certificate()
    hopping = hopping_certificate()
    rxi = source_side_rxi_certificate()
    perturbativity = perturbativity_certificate()
    anomaly = anomaly_certificate()
    mediator = mediator_elimination_certificate()
    coverage = operator_coverage()
    source = source_endpoint_contract()
    parts = {
        "link": link,
        "parity": parity,
        "hopping": hopping,
        "rxi": rxi,
        "perturbativity": perturbativity,
        "anomaly": anomaly,
        "mediator": mediator,
        "coverage": coverage,
        "source": source,
    }
    kills = kill_tests(parts)

    checks = {
        "link_Jacobian_has_declared_shape": (
            link["constraint_dimension"] == LINK_CONSTRAINT_DIMENSION
            and link["variable_dimension"] == LINK_VARIABLE_DIMENSION
        ),
        "exact_modular_rank_is_567": link["modular_rank"] == 567,
        "rank_upper_and_lower_bounds_meet": (
            link["complex_rank_upper_bound_from_45_kernel_vectors"]
            == link["modular_rank"]
            == 567
        ),
        "link_nullity_is_exactly_45": link["complex_nullity_exact"] == 45,
        "finite_Spin_orbit_solves_nonlinear_link_constraints": (
            link["finite_group_orbit_certificate"]["worst_residual"] < 1.0e-12
        ),
        "pairing_removes_radial_modulus": link["extra_modulus_without_pairing"] == 1,
        "PS_projectors_are_8_plus_8": all(
            block["plus_projector_rank"] == block["minus_projector_rank"] == 8
            for block in parity["chirality_blocks"].values()
        ),
        "PS_centralizer_has_dimension_21": all(
            block["commuting_Spin10_generator_count"] == 21
            for block in parity["chirality_blocks"].values()
        ),
        "transport_has_32_and_only_32_profiles": (
            hopping["total_chiral_profile_count"] == 32
            and hopping["additional_uncontrolled_transport_zero_modes"] == 0
        ),
        "source_orbit_artifact_is_canonically_bound": (
            rxi["source_orbit_input"]["canonical_core_valid"]
            and rxi["source_orbit_input"]["Q_shape"] == [465, 22]
            and rxi["source_orbit_input"]["Q_exact_rank"] == 22
            and rxi["source_orbit_input"]["projector_rank"] == 443
            and rxi["source_orbit_input"][
                "published_U1F_column_matches_Theta_charges"
            ]
        ),
        "source_Hessian_Ward_and_physical_pullback_are_exactly_bound": (
            rxi["source_hessian_input"]["canonical_core_valid"]
            and rxi["source_hessian_input"]["H_shape"] == [465, 465]
            and rxi["source_hessian_input"]["H_exact_rank"] == 443
            and rxi["source_hessian_input"]["H_exact_nullity"] == 22
            and rxi["source_hessian_input"]["HQ_exact_zero_all_46_columns"]
            and rxi["source_hessian_input"]["physical_pullback_nondegenerate"]
        ),
        "source_side_Rxi_blocks_are_full_rank_and_spectrally_paired": (
            rxi["all_source_broken_D_full_rank"]
            and rxi["worst_broken_vector_Goldstone_pairing_residual"] < 1.0e-12
            and rxi["unbroken_nonzero_spectral_pairing_residual"] < 1.0e-12
            and rxi["unbroken_vector_zero_modes_per_generator"] == 1
            and rxi["shared_U1F"]["candidate_source_normalization_matches"]
        ),
        "combined_endpoint_count_exposes_12_residual_chirals": (
            rxi["combined_host_PS_source_SU5"][
                "total_uneaten_A5_like_chirals"
            ]
            == 12
            and all(
                row["D_rank"] == N_CELLS
                and row["Goldstone_zero_modes"] == 1
                and row["nonzero_spectral_pairing_residual"] < 1.0e-12
                for row in rxi["combined_host_PS_source_SU5"]["neither"][
                    "representative_norm_cases"
                ]
            )
        ),
        "perturbativity_blocker_is_not_suppressed": (
            not perturbativity["controlled_perturbative_window"]
            and perturbativity["interior_site"]["b_one_loop"] == -280
            and perturbativity["source_site"]["b_one_loop"] == -292
            and perturbativity["source_site"]["Landau_pole_over_link_scale"] < 1.70
        ),
        "V51_C5_C7_feasibility_input_is_canonically_bound": coverage[
            "V51_feasibility_input"
        ]["canonical_core_valid"],
        "host_ordinary_anomalies_cancel": all(
            value == 0 for value in anomaly["host_complete_totals"].values()
        ),
        "source_ordinary_anomalies_cancel": all(
            value == 0 for value in anomaly["source_spin10_totals"].values()
        ),
        "mediator_tree_identity": (
            mediator["F_Y_residual"] < 1.0e-12
            and mediator["F_Z_residual"] < 1.0e-12
            and mediator["effective_superpotential_residual"] < 1.0e-12
        ),
        "all_kill_tests_pass": all(kills.values()),
        "fail_closed_G2": True,
    }

    report = {
        "schema": "susy-spin10-v51-representation-faithful-mediator-moose-v1",
        "status": STATUS,
        "candidate_name": "Clifford-locked PS-to-Spin(10) mediator moose",
        "candidate_contract": {
            "spacetime": "finite four-dimensional N=1 supersymmetric quiver",
            "sites": N_CELLS + 1,
            "edges": N_CELLS,
            "why_new": (
                "The Spin(10) representation matrices, PS endpoint projector, link "
                "constraint variety, and channel mediators are physical coordinates. "
                "No four-channel tensor identity or continuum smeared boundary is used."
            ),
            "fundamental_locality": (
                "site terms plus nearest-neighbour cubic link terms only; Wilson products "
                "appear only after finite heavy-field elimination"
            ),
            "Kahler": "canonical positive metrics for all elementary chirals, with positive gauge kinetic terms",
        },
        "field_content": {
            "spinor_species": list(SPINOR_SPECIES),
            "per_edge_link": link["link_fields"],
            "per_edge_constraint_multipliers": link[
                "multiplier_representation_table"
            ],
            "per_edge_diagonal_multiplier_content": link[
                "diagonal_multiplier_content"
            ],
            "transport": (
                "X_(alpha,j) at every allowed PS/Spin(10) site and P_(alpha,j) "
                "in the conjugate representation/opposite qF on every edge"
            ),
            "source_endpoint": source["source_fields_at_N"],
            "channel_mediators": (
                "one vectorlike R+barR pair per resolved invariant/copy channel, "
                "with opposite U1F charges"
            ),
        },
        "Clifford_locked_link": link,
        "PS_endpoint_projector": parity,
        "rectangular_spinor_transport": hopping,
        "source_side_coupled_Rxi": rxi,
        "perturbativity_stress_test": perturbativity,
        "ordinary_anomaly_certificate": anomaly,
        "vectorlike_channel_mediator_theorem": mediator,
        "operator_class_coverage": coverage,
        "source_endpoint_contract": source,
        "kill_tests": kills,
        "gate_effect": {
            "C2": (
                "CANDIDATE_LOCALITY_PASS_ONLY__NOT_FROZEN_G2_SAME_ACTION_C2"
            ),
            "C3": (
                "PARTIAL: exact link/transport tangent domain, 465x22 orbit/projector, "
                "465x465 Hessian/Ward identity and source-side augmented R_xi block "
                "exist; 12 combined-endpoint A5-like chirals remain unlifted"
            ),
            "C4": (
                "PARTIAL: canonical elementary Kahler metrics, local link rigidity and "
                "source Hessian/vector-Goldstone pairing pass; the 12 residual chirals "
                "and full interacting physical quotient metric/pencil remain unresolved"
            ),
            "C5": (
                "PARTIAL: tree holomorphic mediator identity passes; full one-loop 1PI "
                "mixing, finite thresholds and scale cancellation are uncomputed"
            ),
            "C6": (
                "UNASSESSED_FOR_NEW_ACTION__V50_SELECTOR_POLICY_REMAINS_PASS_ONLY_IN_V50_LEDGER; "
                "perturbativity is a separate candidate-UV-viability test"
            ),
            "C7": (
                "PARTIAL: 48 low-degree rows and all 34 PS primitives are explicit; "
                "120 degree-four factor spaces and the final Wilson array remain absent"
            ),
            "candidate_UV_viability": (
                "FAIL_CONTROLLED_PERTURBATIVITY_AT_G_0P73_AND_12_UNEATEN_A5_LIKE_CHIRALS"
            ),
            "G2_closed": False,
            "gates_promoted": [],
        },
        "sharp_next_obligations": [
            "replace the 567-multiplier link by a substantially leaner perturbative realization or construct a genuine strong/composite UV completion",
            "construct a local gauge-covariant interaction that lifts the 12 neither-PS-nor-SU5 A5-like chirals and re-audit the full Hessian",
            "differentiate the complete V51 superpotential/Kahler action and certify the full physical pencil",
            "resolve the remaining 120 degree-four factor spaces and instantiate one mediator pair per nonempty channel",
            "compute one-loop mediator/link thresholds, the complete operator-mixing matrix and mu cancellation",
            "publish the normalized Cartesian-to-PS Wilson array and compare its observables with the V50 target",
            "test global nonlinear link branches, global anomalies, perturbativity and Landau-pole bounds",
        ],
        "integrity_checks": checks,
        "n_failed_integrity_checks": sum(not value for value in checks.values()),
        "primary_sources": [
            "https://arxiv.org/abs/hep-th/0104005",
            "https://arxiv.org/abs/hep-th/0212206",
            "https://arxiv.org/abs/hep-ph/0306242",
            "https://arxiv.org/abs/hep-ph/0501025",
        ],
        "provenance": {
            "upstream_sha256": {
                path.name: sha256_file(path) for path in UPSTREAM_PATHS
            },
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
    gate = report["gate_effect"]
    if gate["G2_closed"] or gate["gates_promoted"]:
        raise RuntimeError("candidate architecture cannot promote or close G2")
    if not gate["C3"].startswith("PARTIAL") or not gate["C4"].startswith(
        "PARTIAL"
    ):
        raise RuntimeError("physical C3/C4 must remain fail-closed")
    if not gate["C2"].startswith("CANDIDATE_LOCALITY_PASS_ONLY"):
        raise RuntimeError("new-action locality cannot promote frozen same-action C2")
    if not gate["C6"].startswith("UNASSESSED_FOR_NEW_ACTION"):
        raise RuntimeError("V50 selector policy cannot be inherited by a new action")
    if not gate["candidate_UV_viability"].startswith("FAIL"):
        raise RuntimeError("candidate UV blockers must remain fail-closed")


def render_markdown(report: Mapping[str, Any]) -> str:
    link = report["Clifford_locked_link"]
    hop = report["rectangular_spinor_transport"]
    rxi = report["source_side_coupled_Rxi"]
    running = report["perturbativity_stress_test"]
    parity = report["PS_endpoint_projector"]
    mediator = report["vectorlike_channel_mediator_theorem"]
    coverage = report["operator_class_coverage"]
    obligations = "\n".join(
        f"{index}. {item}"
        for index, item in enumerate(report["sharp_next_obligations"], 1)
    )
    species = "\n".join(
        f"- `{item['name']}`: `{item['Spin10_rep']}_{item['qF']:+d}`, "
        f"host `eta={item['host_eta']:+d}` -> `{item['host_PS_rep']}`"
        for item in SPINOR_SPECIES
    )
    return f"""# V51 representation-faithful mediator/moose candidate

Status: `{report['status']}`  
Core SHA-256: `{report['core_sha256']}`

## Verdict

There is a concrete algebraic new-physics route worth retaining for study: a finite 4D N=1
`PS -- Spin(10)^4` quiver with one shared gauged `U(1)F`, Clifford-locked
vector/spinor links, PS-projected rectangular hopping, and vectorlike
channel mediators.  It removes two fatal abstractions of V50: the link is a
physical representation-level field system and the four spinor species are
not replaced by a `4 x 4` identity.

The executable result is substantial but **does not close G2**.  It proves
local link rigidity, the exact chiral-profile count, perturbative anomaly
cancellation and a tree-level mediator theorem, and it binds the exact
source orbit/projector into a coupled source-side `R_xi` block.  The physical
source Hessian/Ward identity is now also exact at the tuned witness.  The
combined endpoint count instead exposes 12 uneaten A5-like chirals; their
lifting interaction, one-loop matching and final component Wilson array
remain absent.

There is also a decisive negative result: with all constraint multipliers as
canonical dynamical chirals, the one-loop Spin(10) Landau pole is less than
1.70 link scales away.  The present field realization is therefore **not a
controlled perturbative UV completion** at `g=0.73`.

## Explicit fields and endpoint selection

{species}

At site zero, the Cartesian operator
`P_PS=Gamma_6 Gamma_7 Gamma_8 Gamma_9` is Hermitian, squares to one, and has
rank-eight `+` and `-` projectors in both spinor chiralities.  Exactly
`{parity['chirality_blocks']['-1']['commuting_Spin10_generator_count']}` of
the 45 Spin(10) generators commute with it, giving the PS centralizer.  This
is an actual 16-component Clifford projector, not a parity label.  The V51
C5/C7 audit now resolves all 34 PS primitives directly in this Cartesian
basis; 120 degree-four factor spaces and the final Wilson array remain open.

## Clifford-locked link theorem

On every edge use

```text
L       in (10_left,10_right),
U_minus in (16_left,bar16_right),
U_plus  in (bar16_left,16_right),
```

all neutral under the shared `U(1)F`.  The renormalizable multiplier action
imposes

```text
Sym(L^T L-v^2 I)=0,
U_minus^T B U_plus-B=0,
sum_a [U_minus Gamma_a-sum_b L_ab Gamma_b U_plus] Gamma_a^dagger=0.
```

The three equation blocks have dimensions `55+256+256=567`; their diagonal
multiplier content is `3(1)+54+2(45)+2(210)`.  Every superpotential monomial
has degree at most three.  Before diagonal breaking, the multipliers are
`Y_O in (1,1+54)`, `Y_B in (1,1+45+210)`, and
`Y_E in (bar16,16)`, contragredient respectively to the three displayed
constraint sectors.  Thus their covariance is under the full product group,
not merely under the diagonal Spin(10) left at the vacuum.

The exact identity-vacuum Jacobian is `{link['constraint_dimension']} x
{link['variable_dimension']}` with hash `{link['jacobian_sha256']}`.  Its
entries are Gaussian integers.  Reduction through
`Z[i] -> F_13, i -> 5` has rank `{link['modular_rank']}`; hence a 567-minor is
nonzero modulo 13 and therefore over the complex numbers.  Independently, all 45 explicit
Spin(10) tangent vectors are linearly independent and have constraint
residual `{link['all_tangent_constraint_residual']:.3g}`, so rank is at most
`612-45=567`.  The rank is therefore exactly 567 and the nullity exactly 45.

With positive elementary Kahler metrics, the 567 normal link modes pair with
the 567 multipliers.  The remaining 45 directions are the relative
Spin(10) orbit eaten by the massive vector multiplets.  Omitting the
invariant-pairing equation leaves rank
`{link['without_invariant_pairing_full_Clifford_rank']}` and one extra
complex scaling modulus.  This is a local tangent theorem at the identity;
global uniqueness of the nonlinear constraint variety is not claimed.  Three
finite relative Spin rotations solve all nonlinear constraint equations to
worst residual
`{link['finite_group_orbit_certificate']['worst_residual']:.3g}`.

## Perturbativity kill test

In the convention `T(10)=1`, one edge contributes Dynkin index
`{running['per_edge_index_at_left_site']}` at its left site and
`{running['per_edge_index_at_right_site']}` at its right site.  An interior
site sees two edges plus four `X/P` pairs:

```text
sum T(R) = {running['interior_site']['sum_T']},
b = 3 C2(Spin10)-sum T(R) = {running['interior_site']['b_one_loop']},
Lambda_pole/mu_link = {running['interior_site']['Landau_pole_over_link_scale']:.8g}.
```

At the source, the `210+126+bar126` fields make the result still worse:
`sum T={running['source_site']['sum_T']}`, `b={running['source_site']['b_one_loop']}`,
and `Lambda_pole/mu_link={running['source_site']['Landau_pole_over_link_scale']:.8g}`.
These are optimistic upper bounds because the unresolved channel mediators
would add positive index.  Making the 567 multipliers nondynamical would
reduce the running but contradict canonical positive Kahler and revert to an
exact-multiplier regulator.  A leaner link or a genuine strongly coupled
completion is required.

## Rectangular hopping and locality

For each species,

```text
W_hop=sum_j P_j^T(M X_j-lambda U_chi,j X_(j+1)).
```

All terms are site-local or nearest-neighbour and cubic at most.  At the link
vacuum, every selected PS component has a `4 x 5` incidence matrix of rank
four and one constant profile.  Every rejected component has an anchored
`4 x 4` matrix with determinant `{hop['unwanted_determinant']:.0f}` and no
zero mode.  Across four species this gives **exactly
{hop['total_chiral_profile_count']} chiral profile components**, with no
extra transport zero.  The smallest heavy singular value is
`{hop['smallest_heavy_mass_in_units_of_min_M']:.8g} min(M_alpha)`.

Finite Wilson products arise only after the intermediate site fields are
integrated out.  They are not fundamental bilocal operators.  The price is
explicit: `U(1)F` is one shared 4D gauge factor and has no deconstructed KK
tower.  That is a falsifiable change of microscopic physics, not an
equivalence silently asserted with V50.

## Exact source orbit and source-side R_xi pairing

This candidate is bound to
`{rxi['source_orbit_input']['path']}` at core
`{rxi['source_orbit_input']['declared_core_sha256']}`.  That upstream now
provides the exact `465 x 22` source orbit, Gram diagonal
`(2,7 x 20,18)`, and rank-443 orthogonal projector.
It is also bound to `{rxi['source_hessian_input']['path']}` at core
`{rxi['source_hessian_input']['declared_core_sha256']}`.  The latter proves
all 465 F terms vanish, `rank(H)=443`, `nullity(H)=22`, `H Q=0` for all 46
Spin(10)+U(1) columns, and a nondegenerate `443 x 443` physical pullback.

For each of the 21 source-broken Spin(10) generators the quiver uses one
augmented map

```text
D_a = [B ; sqrt(g_a) e_N^T],
M_vector = D_a^dagger D_a,
M_Goldstone = xi D_a D_a^dagger.
```

Every `D_a` has rank five.  At `xi=1` the worst vector/Goldstone spectral
pairing residual is
`{rxi['worst_broken_vector_Goldstone_pairing_residual']:.3g}` and the
smallest broken mass squared at unit link scale is
`{rxi['minimum_broken_mass_squared_at_unit_link_scale']:.8g}`.  For the 24
source-unbroken SU(5) directions, `D=B`: the vector block has exactly one
zero and its four nonzero eigenvalues equal the link-Goldstone spectrum.
The shared `U(1)F` has no link tower; its endpoint vector and Goldstone masses
both use the exact norm 18.  V51 uses the primitive charge convention
`(HLF,HLA,HRA,HRF)=(1,-4,-1,4)`, `(Q,Qc)=(1,-1)`, and
`(ThetaPlus,ThetaMinus)=(3,-3)`.  Thus the published source-orbit column has
entries `(+3i,-3i)` and norm `3^2+(-3)^2=18`; no charge rescaling is hidden
inside this `R_xi` comparison.

This repairs V50's independent `B B^T` plus source-zero error on the source
side.  Intersecting the two endpoint stabilizers gives the exact generator
partition `12 SM + 9 PS-only + 12 SU5-only + 12 neither`.  The first three
classes have the expected vector/Goldstone rank.  In the `neither` class,
however, `D` is `5 x 4`: it has rank four and leaves one uneaten Goldstone
combination per generator.  The candidate therefore contains
**{rxi['combined_host_PS_source_SU5']['total_uneaten_A5_like_chirals']} residual
A5-like chirals** until a new local lifting interaction is constructed.

## Anomalies and source endpoint

The complete host PS ledger (selected spinors, three visible families,
Higgs, and full edge multipliers) vanishes entry by entry for
`U1F-SU4^2`, `U1F-SU2L^2`, `U1F-SU2R^2`, gravitational-`U1F`, `U1F^3`, and
`SU4^3`.  Interior `X/P` fields are vectorlike.  At the source, the four full
spinors sum to zero for `U1F-Spin10^2`, gravity-`U1F` and `U1F^3`;
`210_0` is real, `126_0+bar126_0` is vectorlike, and
`ThetaPlus_(+3)+ThetaMinus_(-3)` cancels.  Every channel mediator is also an
`R+barR` pair with opposite charge.

This is an ordinary perturbative anomaly certificate.  Global/bordism
anomalies and threshold Wess-Zumino terms remain to be audited.

The source superpotential explicitly retains the standard
`210+126+bar126` Higgs terms, both Theta masses, and the unavoidable
`barSigma HLF HRA` and `Sigma HLA HRF` portals.  The exact Hessian witness is
an allowed tuned matching point; its `m1=M1=0` choice is not selector-protected
or claimed radiatively stable.

## What vectorlike mediators solve

For every resolved bilinear channel `A_R B_barR`, introduce a vectorlike pair
and

```text
W=Y_barR^T M Z_R+Y_barR^T A_R+B_barR^T Z_R.
```

The executable complex benchmark satisfies both heavy F equations and
`W_eff=-B^T M^-1 A` to residual
`{mediator['effective_superpotential_residual']:.3g}`.  Thus every nonempty
holomorphic invariant of degree at most four has a finite renormalizable UV
realization once its normalized intermediate tensor and copy label are
known.

This does not instantiate unnamed channels.  V49 has
`{coverage['tree_holomorphic']['pure_source_quartic_directions']}` exact
pure-source quartic directions.  V51 has resolved
`{coverage['tree_holomorphic']['low_degree_rows_resolved']}` low-degree rows
(`{coverage['tree_holomorphic']['low_degree_nonempty']}` nonempty and
`{coverage['tree_holomorphic']['low_degree_empty']}` empty) and all
`{coverage['tree_holomorphic']['PS_primitives_resolved']}` PS primitives;
`{coverage['tree_holomorphic']['degree_four_rows_pending']}` degree-four
factor spaces still lack physical mediator tensors.  General Kahler
coefficients are not produced by the tree theorem, and the gauge-kinetic,
FI, one-loop mixing and finite-threshold calculations are open.

## Gate effect and next obligations

The candidate-locality audit passes for this finite microscopic contract,
but that is **not** a promotion of frozen same-action `C2`.  `C3`, `C4`,
`C5`, and `C7` remain partial.  `C6` is unassessed for the new V51 action;
the selector/naturalness policy remains passed only in the V50 ledger.  The
Landau pole is reported separately as a failure of this candidate's UV
viability.  No gate is promoted and G2 remains open.

{obligations}

Primary references: [Arkani-Hamed--Cohen--Georgi](https://arxiv.org/abs/hep-th/0104005),
[Falkowski et al.](https://arxiv.org/abs/hep-th/0212206),
[Aulakh et al.](https://arxiv.org/abs/hep-ph/0306242), and
[Aulakh--Girdhar](https://arxiv.org/abs/hep-ph/0501025).
"""


def write_artifacts(report: Mapping[str, Any]) -> None:
    JSON_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(render_markdown(report), encoding="utf-8")


def check_artifacts(report: Mapping[str, Any]) -> None:
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        raise RuntimeError("V51 mediator/moose artifacts are missing; run --write")
    if json.loads(JSON_PATH.read_text(encoding="utf-8")) != report:
        raise RuntimeError("V51 mediator/moose JSON is stale; run --write")
    if MD_PATH.read_text(encoding="utf-8") != render_markdown(report):
        raise RuntimeError("V51 mediator/moose Markdown is stale; run --write")


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
