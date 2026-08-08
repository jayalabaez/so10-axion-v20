#!/usr/bin/env python3
"""Fail-closed G3 local-stability audit for the gauged-U(1)_X theory.

The exact-X-neutral scalar contract contains 44 invariant directions and 51
real parameters on the canonical 486-real-coordinate chart.  G2 now proves
three structural zero-gradient columns, an exact nonzero 13x13 stationarity
minor, and the full factorization ``A=L A[pivots,:]``.  Thus the stationarity
rank/nullity are exactly 13/38.

An exact rational coupling vector provides the decisive regression test:

    c[O07] = 10, c[O48/J0] = 1, c[O48/J2] = -1/4,

with every other coupling zero.  It obeys ``A c = 0`` exactly, the normalization
and 4*pi box, and has exact positive trace ``tr(P24 H(c)) = 288``.  The previous
normalized-SVD constraint basis rejects this vector at roughly 1.4e-2.  Thus
the previously recorded finite-cut search, common-kernel calculation, Hessian
pencil, block SDP margin, and negative trace LP all used a false stationary
family and are invalidated.  They are retained only as quarantined historical
records and have no scientific use for G3.

The corrected numerical constraint representation uses 11 normalized compiler
pivot rows and exact unit constraints for re/im(O31); it never normalizes
columns or backscales singular vectors.  A separate Gaussian-integer tangent
certificate proves gauge-orbit rank 37, leaving a 449-dimensional gauge
quotient that includes the physical axion.  Removing the independent global-PQ
orbit gives the 448-dimensional massive/transverse space used by the Hessian
test.  SVD is retained only to construct an orthonormal projection basis; it is
not the dimension certificate.

An exact polynomial witness also rules out promoting the tiny H[6].x radial
curvature to an exact flat direction: with ``t=sqrt(2)h``, coefficients
``c[O06]=-t^2`` and ``c[O36_B01]=10`` have zero gradient but curvature
``2t^2=4h^2>0``.  A corrected opt-in common-kernel diagnostic uses the raw
orthonormal 448-space quotient and reports numerical rank/nullity 448/0.  The
former apparent 135-dimensional flat subspace is reproduced only after an
ill-conditioned reference-derived field congruence and is invalidated as a
conditioning artifact.

A new sparse stationary candidate changes the stability frontier.  It contains
27 nonzero real parameters, has maximum absolute coefficient ``73/8 < 4*pi``,
and uses the exactly bounded Pati--Salam 210 potential with
``J0=-21/200``.  It therefore proves that the historical ``J0=+1`` SDP slice
was not without loss of generality.  Exact source-bound sum-of-squares
identities prove boundedness below and stationarity.  Direct Gaussian-integer,
Fraction, and Q(sqrt(2)) assembly proves positivity on all 448 transverse
directions, leaving exactly the 38 symmetry tangents.  The selected orbit is
therefore a proof-grade strict local minimum.  A source-bound global-gap test
also constructs a symmetry-inequivalent 126bar field configuration with
exactly lower energy.  It disproves global minimality of the selected orbit and
rejects this constructive candidate for G3 without excluding the full model.
``--recompute-heavy`` retains the corrected numerical common-kernel diagnostic
but does not start a solver.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import time
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.optimize import linprog

import exact_gauged_u1x_physical_quotient_v20 as exact_quotient_source
import exact_gauged_u1x_stationarity_rank_certificate_v20 as exact_rank_source
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import gauged_u1x_g3_corrected_common_kernel_v20 as corrected_kernel_source
import gauged_u1x_g3_sos_candidate_v20 as sos_candidate_source
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "GAUGED_U1X_G3_STABILITY_V20.json"
OUT_MD = ROOT / "GAUGED_U1X_G3_STABILITY_V20.md"
UPSTREAM_G2_JSON = ROOT / "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EXPECTED_DIRECTION_COUNT = 44
EXPECTED_PARAMETER_COUNT = 51
EXPECTED_STATIONARITY_RANK = 13
EXPECTED_STATIONARITY_NULLITY = 38
EXPECTED_SO10_RANK = 36
EXPECTED_SO10_U1X_RANK = 37
EXPECTED_FULL_SYMMETRY_RANK = 38
EXPECTED_GAUGE_QUOTIENT_DIMENSION = 449
EXPECTED_MASSIVE_TRANSVERSE_QUOTIENT_DIMENSION = 448
# Backward-compatible name for callers that historically used "physical
# quotient" for the further quotient by global PQ.  New output distinguishes
# the 449-dimensional gauge quotient from the 448-dimensional transverse one.
EXPECTED_PHYSICAL_QUOTIENT_DIMENSION = EXPECTED_MASSIVE_TRANSVERSE_QUOTIENT_DIMENSION
REQUIRED_UPSTREAM_G2_FLAGS = (
    "G2_gauged_u1x_derivatives_certified",
    "exact_three_structural_zero_gradient_certificates",
    "stationarity_rank_lower_bound_13_exactly_certified",
    "stationarity_rank_upper_bound_13_exactly_certified",
    "stationarity_rank_13_exactly_certified",
    "stationarity_nullity_38_exactly_certified",
    "compiler_gradients_bound_to_exact_nonzero_13x13_minor",
    "exact_informed_13_row_constraint_representation_ready",
    "exact_stationary_witness_regression_passes",
)
COUPLING_BOUND = float(4.0 * np.pi)
RANK_RTOL = 1.0e-10
COMMON_KERNEL_RANK_RTOL = 1.0e-8
MARGIN_SCALE = 1.0e-10
NORMALIZATION_PARAMETER_ID = "lambda::O48_B01_Phi_self_quartics"
REFERENCE_ANCHOR_PARAMETER_IDS = (
    "lambda::O20_B01_singlet_polynomial",
    "lambda::O23_B01_singlet_polynomial",
    "lambda::O27_B04_126bar_self_projectors",
    "lambda::O36_B02_H_self_quartics",
    NORMALIZATION_PARAMETER_ID,
)

PQ_CHARGES = {
    "Phi210": 0.0,
    "H10": -2.0,
    "Sigma126bar": -2.0,
    "S": 4.0,
    "Phi17": 0.0,
}

LEGACY_STATIONARY_FAMILY_INVALIDATION_REASON = (
    "The normalized-SVD stationarity constraint rows reject the exact rational "
    "witness c[O07]=10, c[O48/J0]=1, c[O48/J2]=-1/4 even though the dense "
    "gradient A c is exactly zero. The maximum false constraint residual is "
    "approximately 0.0140183, caused by normalizing hierarchy-suppressed "
    "gradient columns before deriving the row space."
)
LEGACY_FALSE_CONSTRAINT_RESIDUAL = 0.0140183
LEGACY_AFFECTED_RESULTS = (
    "normalized-SVD 38-dimensional stationary nullspace",
    "stationary Hessian pencil",
    "normalized common-kernel diagnostic",
    "finite Rayleigh-cut search",
    "eight-block stationary SDP margin",
    "negative P24 trace LP",
)

# Quarantined historical numbers from the invalid stationary family. They are
# retained only for provenance and are wrapped with status=INVALIDATED by
# recorded_numerical_evidence(); none is evidence about the true SDP optimum.
RECORDED_FINITE_CUT_EVIDENCE = {
    "evidence_kind": "recorded_exploratory_finite_Rayleigh_cut_relaxation",
    "recomputed_in_this_invocation": False,
    "iterations": 187,
    "coupling_bound": COUPLING_BOUND,
    "normalization_parameter_id": NORMALIZATION_PARAMETER_ID,
    "best_primal_lower_bound": -6.612036100266937e-11,
    "finite_cut_relaxation_bound_noncertified": 9.215652220851327e-12,
    "open_bracket_width": 7.53360132235207e-11,
    "best_exact_adapter_tadpole_max_abs_residual": 4.999450374628439e-12,
    "best_max_abs_coupling": 12.56637061784604,
    "bracket_straddles_zero": True,
    "strict_local_minimum_certified": False,
    "PSD_feasibility_certified": False,
    "PSD_infeasibility_certified": False,
    "proof_grade": False,
    "limitations": [
        "the finite Rayleigh-cut master is only a numerically solved finite relaxation",
        "the bracket straddles zero",
        "no interval-verified primal Cholesky or dual Farkas certificate exists",
        "several optimal-search couplings saturate the 4*pi box",
    ],
}

RECORDED_NORMALIZED_COMMON_KERNEL = {
    "evidence_kind": "normalized_stationary_pencil_common_kernel_diagnostic",
    "recomputed_in_this_invocation": False,
    "stationary_pencil_generators": 38,
    "nonzero_Hessian_generators": 37,
    "exactly_zero_Hessian_generators": 1,
    "nonzero_generator_frobenius_norm_min": 2.694924952975825e-29,
    "nonzero_generator_frobenius_norm_max": 5.3479816428029645,
    "normalized_Gram_min_eigenvalue": 0.002295651428711279,
    "normalized_Gram_max_eigenvalue": 7.863139284793251,
    "normalized_Gram_rank": 448,
    "tested_relative_rank_tolerances": [1.0e-8, 1.0e-10, 1.0e-12, 1.0e-14, 1.0e-16],
    "common_kernel_dimension": 0,
    "structural_common_flat_subspace_found": False,
    "proof_grade": False,
    "note": (
        "An unnormalized Gram falsely suggested 50 flat modes because generator "
        "norms span about 29 orders.  Frobenius-normalizing every nonzero "
        "generator makes the joint field-space Gram full rank."
    ),
}

# Quarantined data-only record of the invalid stationary block experiment.
# Only the unbroken algebra and Casimir block dimensions survive structurally;
# its solver margin and trace LP are explicitly invalidated below.
RECORDED_SYMMETRY_BLOCK_EVIDENCE = {
    "evidence_kind": "recorded_exploratory_unbroken_gauge_Casimir_reduction",
    "recomputed_in_this_invocation": False,
    "unbroken_gauge_algebra": {
        "physical_dimension": 9,
        "identification": "su(3)_c plus u(1)_em",
        "pre_EW_SO10_orbit_rank": 33,
        "EW_rank_increment": 3,
        "physical_SO10_orbit_rank": 36,
    },
    "construction": {
        "pencil": "unscaled Q.T H Q stationary pencil",
        "warning": (
            "A diagonal congruence-scaled pencil must not be tested against "
            "the original skew generators without transforming their action."
        ),
        "maximum_relative_stationary_generator_commutator_residual": (
            1.872893316277335e-13
        ),
        "maximum_off_block_Frobenius_residual": 2.5338422092716617e-13,
    },
    "Casimir_blocks": [
        {"eigenvalue": "0", "electric_center_square": "0", "dimension": 20},
        {"eigenvalue": "1", "electric_center_square": "1", "dimension": 20},
        {"eigenvalue": "8/3", "electric_center_square": "0", "dimension": 84},
        {"eigenvalue": "11/3", "electric_center_square": "1", "dimension": 84},
        {"eigenvalue": "6", "electric_center_square": "0", "dimension": 56},
        {"eigenvalue": "20/3", "electric_center_square": "0", "dimension": 48},
        {"eigenvalue": "7", "electric_center_square": "1", "dimension": 64},
        {"eigenvalue": "23/3", "electric_center_square": "1", "dimension": 72},
    ],
    "block_dimension_sum": 448,
    "block_solver": {
        "interface": "CVXPY",
        "solver": "CLARABEL",
        "status": "optimal_inaccurate",
        "common_block_scaled_margin": -1.9421038424279142,
        "largest_cone_dimension": 84,
        "bottleneck_Casimir_eigenvalue": "20/3",
        "bottleneck_electric_center_square": "0",
        "bottleneck_dimension": 48,
        "primal_certificate": False,
        "dual_certificate": False,
    },
    "candidate_trace_obstruction": {
        "source_block_dimension": 48,
        "float_derived_dual_projector_rank": 24,
        "projector_field_trace": {
            "Phi210": 23.999999999995595,
            "H10": 1.8811928954298647e-30,
            "Sigma126bar": 4.404196838635561e-12,
            "S": 4.375340653383405e-32,
            "Phi17": 2.2117185613872187e-32,
        },
        "scaled_projector_idempotence_residual": 2.7531246310028102e-16,
        "distance_from_inaccurate_solver_dual": 2.8109003656689e-4,
        "LP_constraints": [
            "A c = 0 on the exact-zero-corrected normalized-SVD rank-13 family",
            "c[lambda::O48_B01_Phi_self_quartics] = 1",
            "-4*pi <= c_i <= 4*pi",
        ],
        "LP_solver": "HiGHS dual simplex",
        "LP_status": "optimal_numerical",
        "candidate_maximum_trace_functional": -1.9420691384829096,
        "interpretation_if_certified": (
            "A negative upper bound for a PSD-projector trace would exclude "
            "PSD Hessians in the normalized bounded-coupling feasible set."
        ),
        "exact_or_interval_projector_available": False,
        "rational_or_interval_LP_dual_available": False,
    },
    "proof_grade": False,
    "PSD_feasibility_certified": False,
    "PSD_infeasibility_certified": False,
    "limitations": [
        "the Casimir eigenspaces and rank-24 projector were derived in float64",
        "Clarabel returned optimal_inaccurate rather than a certificate",
        "the trace LP has no rational or outward-rounded interval dual",
        "a negative numerical margin must not be interpreted as a no-go theorem",
    ],
}

RECORDED_SOLVER_ATTEMPTS = {
    "certificate_available": False,
    "attempts": [
        {
            "solver_path": "CVXPY symbolic dense PSD expression",
            "outcome": "resource_failure_before_solver",
            "requested_allocation_bytes": 15578731928,
            "primal_certificate": False,
            "dual_certificate": False,
        },
        {
            "solver_path": "CVXPY compact 200704x38 affine PSD operator",
            "outcome": "resource_failure_during_canonicalization",
            "requested_allocation_bytes": 15388028928,
            "primal_certificate": False,
            "dual_certificate": False,
        },
        {
            "solver_path": "direct Clarabel PSDTriangle(448), 39 variables",
            "outcome": "resource_failure_before_iterations",
            "requested_allocation_bytes": 36929722984,
            "primal_certificate": False,
            "dual_certificate": False,
        },
        {
            "solver_path": "direct SCS generalized-margin PSDTriangle(448)",
            "outcome": "terminated_at_approximately_15_minute_cap",
            "working_set_bytes_approx": 1298000000,
            "primal_certificate": False,
            "dual_certificate": False,
        },
        {
            "solver_path": (
                "CVXPY Clarabel on eight unbroken-gauge Casimir blocks "
                "of dimensions 20,20,84,84,56,48,64,72"
            ),
            "outcome": "optimal_inaccurate_negative_margin_candidate",
            "largest_cone_dimension": 84,
            "primal_certificate": False,
            "dual_certificate": False,
        },
    ],
    "interpretation": (
        "Solver resource failures are not evidence for either feasibility or "
        "infeasibility of the SDP."
    ),
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return _jsonable(value.tolist())
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    return value


def _copy_jsonable(value: Any) -> Any:
    """Return a mutation-independent JSON-compatible copy."""
    return json.loads(json.dumps(_jsonable(value)))


def _orthonormal_image(
    matrix: np.ndarray,
    *,
    relative_tolerance: float = RANK_RTOL,
    column_relative_tolerance: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    value = np.asarray(matrix, dtype=float)
    norms = np.linalg.norm(value, axis=0)
    floor = column_relative_tolerance * float(np.max(norms, initial=0.0))
    active = norms > floor
    if not np.any(active):
        return np.zeros((value.shape[0], 0)), np.asarray([], dtype=float)
    normalized = value[:, active] / norms[active]
    u, singular, _vh = np.linalg.svd(normalized, full_matrices=False)
    rank = int(np.sum(singular > relative_tolerance * singular[0]))
    return u[:, :rank], singular


@lru_cache(maxsize=1)
def _stage_resolved_so10_basis_cached() -> dict[str, Any]:
    physical = g2_audit.physical_hierarchy_state()
    pre = dataclasses.replace(physical, h=np.zeros_like(physical.h))
    pre_orbit = chart.gauge_orbit_matrix(pre)
    physical_orbit = chart.gauge_orbit_matrix(physical)
    pre_basis, pre_singular = _orthonormal_image(pre_orbit)
    pre_rank = pre_basis.shape[1]

    _u, raw_singular, vh = np.linalg.svd(pre_orbit, full_matrices=True)
    raw_rank = int(np.sum(raw_singular > RANK_RTOL * raw_singular[0]))
    if raw_rank != pre_rank:
        raise ArithmeticError(
            f"pre-EW SO10 rank mismatch: raw={raw_rank}, normalized={pre_rank}"
        )
    unbroken_generators = vh[pre_rank:, :].T
    increment = (physical_orbit - pre_orbit) @ unbroken_generators
    increment -= pre_basis @ (pre_basis.T @ increment)
    increment_basis, increment_singular = _orthonormal_image(
        increment, column_relative_tolerance=RANK_RTOL
    )
    basis, combined_singular = _orthonormal_image(
        np.column_stack((pre_basis, increment_basis))
    )
    basis.setflags(write=False)
    return {
        "basis": basis,
        "pre_rank": pre_rank,
        "increment_rank": int(increment_basis.shape[1]),
        "total_rank": int(basis.shape[1]),
        "pre_singular_values": pre_singular,
        "increment_singular_values": increment_singular,
        "combined_singular_values": combined_singular,
        "orthonormality_residual": float(
            np.max(np.abs(basis.T @ basis - np.eye(basis.shape[1])), initial=0.0)
        ),
    }


def stage_resolved_so10_basis() -> dict[str, Any]:
    report = dict(_stage_resolved_so10_basis_cached())
    report["basis"] = np.asarray(report["basis"]).copy()
    return report


def _phase_tangent(state: potential.FieldState, charges: dict[str, float]) -> np.ndarray:
    tangent = np.zeros(chart.TOTAL_DIM, dtype=float)

    def block(values: Iterable[complex], charge: float) -> np.ndarray:
        z = np.asarray(tuple(values), dtype=complex).reshape(-1)
        varied = 1j * float(charge) * z
        output = np.empty(2 * len(z), dtype=float)
        output[0::2] = chart.SQRT2 * varied.real
        output[1::2] = chart.SQRT2 * varied.imag
        return output

    tangent[chart.H_SLICE] = block(state.h, charges["H10"])
    tangent[chart.SIGMA_SLICE] = block(
        chart.sigma_coordinates(state.sigma), charges["Sigma126bar"]
    )
    tangent[chart.S_SLICE] = block((state.s,), charges["S"])
    tangent[chart.X_SLICE] = block((state.x,), charges["Phi17"])
    return tangent


@lru_cache(maxsize=1)
def _exact_quotient_summary_cached() -> dict[str, Any]:
    """Return proof metadata without embedding the full 486x47 integer matrix."""

    report = exact_quotient_source.build_report()
    certificate = report["exact_certificate"]
    so10 = certificate["SO10"]
    gauge = certificate["gauged_symmetry"]
    full = certificate["full_removed_symmetry"]
    phase = certificate["U1X_PQ_independence"]
    binding = report["live_compiler_binding"]
    return {
        "source_module": "exact_gauged_u1x_physical_quotient_v20",
        "status": report["status"],
        "certified": bool(report["certified"]),
        "arithmetic_domain": certificate["arithmetic_domain"],
        "exact_row_scaling_identity": certificate[
            "exact_row_scaling_identity"
        ],
        "nonzero_scale_assumptions": list(
            certificate["nonzero_scale_assumptions"]
        ),
        "SO10": {
            "rank": so10["rank"],
            "stabilizer_dimension": so10["stabilizer_dimension"],
            "minor": so10["minor"],
            "null_vector_count": len(so10["right_nullspace"]),
            "null_vector_rank": so10["null_vector_rank"],
        },
        "gauged_SO10_U1X": {
            "rank": gauge["rank"],
            "right_nullity": gauge["right_nullity"],
            "minor": gauge["minor"],
            "null_vector_count": len(gauge["right_nullspace"]),
            "null_vector_rank": gauge["null_vector_rank"],
            "gauge_quotient_dimension_including_axion": gauge[
                "gauge_quotient_dimension_including_axion"
            ],
        },
        "U1X_PQ_independence": phase,
        "full_SO10_U1X_global_PQ": {
            "rank": full["rank"],
            "right_nullity": full["right_nullity"],
            "minor": full["minor"],
            "null_vector_count": len(full["right_nullspace"]),
            "null_vector_rank": full["null_vector_rank"],
            "all_null_residuals_exactly_zero": full[
                "all_null_residuals_exactly_zero"
            ],
        },
        "gauge_quotient_dimension_including_axion": report[
            "gauge_quotient_dimension_including_axion"
        ],
        "massive_transverse_quotient_dimension": report[
            "massive_transverse_quotient_dimension"
        ],
        "live_compiler_binding": binding,
    }


@lru_cache(maxsize=1)
def _physical_quotient_cached() -> dict[str, Any]:
    state = g2_audit.physical_hierarchy_state()
    exact = _exact_quotient_summary_cached()
    so10 = _stage_resolved_so10_basis_cached()
    so10_basis = np.asarray(so10["basis"])
    u1x = g2_audit.u1x_tangent(state)
    so10_u1x_basis, so10_u1x_singular = _orthonormal_image(
        np.column_stack((so10_basis, u1x))
    )
    pq = _phase_tangent(state, PQ_CHARGES)
    pq_after_gauge = pq - so10_u1x_basis @ (so10_u1x_basis.T @ pq)
    pq_after_gauge_norm = float(np.linalg.norm(pq_after_gauge))
    if pq_after_gauge_norm <= 0.0:
        raise ArithmeticError("global PQ tangent is not independent of the gauge orbit")
    symmetry_basis, symmetry_singular = _orthonormal_image(
        np.column_stack((so10_u1x_basis, pq_after_gauge))
    )
    _u, _s, vh = np.linalg.svd(symmetry_basis.T, full_matrices=True)
    quotient = vh[symmetry_basis.shape[1] :, :].T
    symmetry_basis.setflags(write=False)
    quotient.setflags(write=False)
    return {
        "exact_certificate": exact,
        "so10": so10,
        "numerical_so10_u1x_rank": int(so10_u1x_basis.shape[1]),
        "so10_u1x_singular_values": so10_u1x_singular,
        "pq_raw_norm": float(np.linalg.norm(pq)),
        "pq_after_gauge_norm": pq_after_gauge_norm,
        "numerical_pq_independent": pq_after_gauge_norm > 0.0,
        "numerical_full_symmetry_rank": int(symmetry_basis.shape[1]),
        "symmetry_singular_values": symmetry_singular,
        "numerical_massive_transverse_basis_dimension": int(quotient.shape[1]),
        "symmetry_basis": symmetry_basis,
        "quotient": quotient,
        "symmetry_quotient_overlap": float(
            np.max(np.abs(symmetry_basis.T @ quotient), initial=0.0)
        ),
        "quotient_orthonormality_residual": float(
            np.max(
                np.abs(quotient.T @ quotient - np.eye(quotient.shape[1])),
                initial=0.0,
            )
        ),
    }


def physical_quotient_audit(*, include_basis: bool = False) -> dict[str, Any]:
    raw = _physical_quotient_cached()
    exact = raw["exact_certificate"]
    report = {
        "interpretation": (
            "The gauged SO(10)+U(1)_X quotient has dimension 449 and includes "
            "the physical axion. The 448-dimensional Hessian space is the "
            "further massive/transverse quotient by the independent global-PQ "
            "orbit; PQ is not gauge-eaten."
        ),
        "dimension_certification": "exact Gaussian-integer tangent certificate",
        "exact_certificate": exact,
        "SO10_pre_EW_rank": raw["so10"]["pre_rank"],
        "SO10_EW_increment_rank": raw["so10"]["increment_rank"],
        "SO10_physical_rank": exact["SO10"]["rank"],
        "SO10_physical_rank_numerical_diagnostic": raw["so10"]["total_rank"],
        "SO10_plus_U1X_rank": exact["gauged_SO10_U1X"]["rank"],
        "SO10_plus_U1X_rank_numerical_diagnostic": raw[
            "numerical_so10_u1x_rank"
        ],
        "gauge_quotient_dimension_including_axion": exact[
            "gauge_quotient_dimension_including_axion"
        ],
        "global_PQ_raw_norm": raw["pq_raw_norm"],
        "global_PQ_after_gauge_norm": raw["pq_after_gauge_norm"],
        "global_PQ_independent": (
            exact["U1X_PQ_independence"]["determinant"] != 0
        ),
        "global_PQ_independent_numerical_diagnostic": raw[
            "numerical_pq_independent"
        ],
        "SO10_plus_U1X_plus_PQ_rank": exact[
            "full_SO10_U1X_global_PQ"
        ]["rank"],
        "SO10_plus_U1X_plus_PQ_rank_numerical_diagnostic": raw[
            "numerical_full_symmetry_rank"
        ],
        "massive_transverse_quotient_dimension": exact[
            "massive_transverse_quotient_dimension"
        ],
        "numerical_massive_transverse_basis_dimension": raw[
            "numerical_massive_transverse_basis_dimension"
        ],
        "physical_quotient_dimension": exact[
            "massive_transverse_quotient_dimension"
        ],
        "physical_quotient_dimension_legacy_alias": (
            "massive_transverse_quotient_dimension; not the gauge quotient"
        ),
        "symmetry_quotient_overlap": raw["symmetry_quotient_overlap"],
        "quotient_orthonormality_residual": raw[
            "quotient_orthonormality_residual"
        ],
    }
    if include_basis:
        report["symmetry_basis"] = np.asarray(raw["symmetry_basis"]).copy()
        report["quotient"] = np.asarray(raw["quotient"]).copy()
    return report


def load_upstream_g2_report() -> dict[str, Any]:
    if not UPSTREAM_G2_JSON.exists():
        raise FileNotFoundError(
            f"required gauged-U1X G2 artifact is absent: {UPSTREAM_G2_JSON}"
        )
    report = json.loads(UPSTREAM_G2_JSON.read_text(encoding="utf-8"))
    flags = report.get("flags", {})
    missing = [name for name in REQUIRED_UPSTREAM_G2_FLAGS if name not in flags]
    false = [name for name in REQUIRED_UPSTREAM_G2_FLAGS if flags.get(name) is not True]
    if missing or false:
        raise RuntimeError(
            "stale or failed upstream G2 artifact; regenerate it with "
            "gauged_u1x_g2_derivative_audit_v20.py --write before G3. "
            f"missing_required_flags={missing}, nontrue_required_flags={false}"
        )
    return report


def recorded_numerical_evidence() -> dict[str, Any]:
    """Return historical solver records with invalidity made machine-readable."""
    phi_certificate = (
        g2_audit.exact_phi_projector_and_stationary_witness_certificate()
    )
    witness = phi_certificate["stationary_witness"]
    invalidation = {
        "status": "INVALIDATED",
        "invalidated": True,
        "scientific_use_for_G3": False,
        "reason": LEGACY_STATIONARY_FAMILY_INVALIDATION_REASON,
        "maximum_false_constraint_residual_for_exact_witness": (
            LEGACY_FALSE_CONSTRAINT_RESIDUAL
        ),
        "affected_results": list(LEGACY_AFFECTED_RESULTS),
        "exact_counterexample": {
            "coefficients": witness["coefficients"],
            "all_unlisted_coefficients": witness["all_unlisted_coefficients"],
            "dense_stationarity_gradient_exactly_zero": witness[
                "gradient_exactly_zero"
            ],
            "normalization_value": witness["normalization_value"],
            "strictly_inside_4pi_box": witness["strictly_inside_4pi_box"],
            "exact_P24_trace": witness["P24_trace"],
        },
    }

    finite = _copy_jsonable(RECORDED_FINITE_CUT_EVIDENCE)
    finite.update(invalidation)
    common = _copy_jsonable(RECORDED_NORMALIZED_COMMON_KERNEL)
    common.update(invalidation)
    solvers = _copy_jsonable(RECORDED_SOLVER_ATTEMPTS)
    solvers.update(invalidation)
    solvers["certificate_available"] = False

    historical_block = _copy_jsonable(RECORDED_SYMMETRY_BLOCK_EVIDENCE)
    invalid_block_solver = historical_block["block_solver"]
    invalid_block_solver.update(invalidation)
    invalid_trace = historical_block["candidate_trace_obstruction"]
    invalid_trace.update(invalidation)
    invalid_trace["contradicted_by_exact_stationary_witness_trace_288"] = True
    block = {
        "status": "STRUCTURAL_ONLY__STATIONARY_SOLVES_INVALIDATED",
        "recomputed_in_this_invocation": False,
        "unbroken_gauge_algebra": historical_block["unbroken_gauge_algebra"],
        "Casimir_blocks": historical_block["Casimir_blocks"],
        "block_dimension_sum": historical_block["block_dimension_sum"],
        "exact_P24_certificate": phi_certificate["P24"],
        "invalidated_stationary_family_results": {
            "construction_diagnostics": historical_block["construction"],
            "block_solver": invalid_block_solver,
            "candidate_trace_obstruction": invalid_trace,
        },
        "structural_scope": (
            "unbroken algebra, quotient block dimensions, and exact P24 only"
        ),
        "stationary_family_dependent_results_invalidated": True,
        "PSD_feasibility_certified": False,
        "PSD_infeasibility_certified": False,
        "proof_grade": False,
    }
    return {
        "legacy_stationary_family_invalidation": invalidation,
        "finite_cut_search": finite,
        "normalized_common_kernel": common,
        "symmetry_block_reduction": block,
        "solver_attempts": solvers,
    }


def _exact_parameter_rows() -> tuple[
    potential.FieldState, tuple[derivatives.ParameterDerivative, ...]
]:
    selection = g2_audit.contract_selection()
    selected_ids = tuple(selection["direction_ids"])
    selected_set = set(selected_ids)
    state = g2_audit.physical_hierarchy_state()
    all_directions = potential.evaluate_directions(state)
    by_id = {row.direction_id: row for row in all_directions}
    missing = selected_set.difference(by_id)
    if missing:
        raise KeyError(f"gauged directions missing from compiler: {sorted(missing)}")
    selected = tuple(by_id[direction_id] for direction_id in selected_ids)
    owners = g2_audit._adapter_modules_by_family()
    q = chart.pack(state)
    direction_rows = tuple(
        owners[row.base_family].direction_derivative(q, row) for row in selected
    )
    parameter_rows = derivatives.parameter_derivatives(direction_rows)
    observed = tuple(row.parameter_id for row in parameter_rows)
    if observed != tuple(selection["parameter_ids"]):
        raise AssertionError("gauged parameter order differs from scalar contract")
    return state, parameter_rows


def _stationarity_family(
    parameter_rows: tuple[derivatives.ParameterDerivative, ...]
) -> dict[str, Any]:
    """Return the corrected exact-informed numerical constraint family.

    The legacy column-normalize/SVD/backscale construction is intentionally not
    present here.  Heavy stability solving remains separately fail-closed.
    """
    family = exact_rank_source.exact_informed_stationarity_constraints(
        parameter_rows
    )
    if not family["certified"]:
        raise ArithmeticError(
            "exact-informed stationarity constraints failed: "
            + ", ".join(family["failures"])
        )
    return family


def _equilibrate_congruence(matrix: np.ndarray, *, iterations: int = 12) -> dict[str, Any]:
    balanced = np.asarray(matrix, dtype=float).copy()
    scale = np.ones(balanced.shape[0], dtype=float)
    for _ in range(iterations):
        row_scale = np.max(np.abs(balanced), axis=1, initial=0.0)
        active = row_scale > 0.0
        if not np.any(active):
            break
        floor = max(float(np.max(row_scale)) * 1.0e-300, 1.0e-300)
        factor = np.ones_like(row_scale)
        factor[active] = 1.0 / np.sqrt(np.maximum(row_scale[active], floor))
        factor = np.clip(factor, 1.0e-8, 1.0e8)
        balanced = factor[:, None] * balanced * factor[None, :]
        scale *= factor
    return {
        "matrix": 0.5 * (balanced + balanced.T),
        "diagonal_scale": scale,
        "scale_min": float(np.min(scale)),
        "scale_max": float(np.max(scale)),
        "scale_condition_ratio": float(np.max(scale) / np.min(scale)),
    }


def _physical_stationary_pencil(
    parameter_rows: tuple[derivatives.ParameterDerivative, ...],
    family: dict[str, Any],
) -> dict[str, Any]:
    raise RuntimeError(
        "invalidated reference-derived field congruence: use "
        "gauged_u1x_g3_corrected_common_kernel_v20 with the raw orthonormal "
        "massive/transverse quotient"
    )
    # The unreachable body is retained only to document the conditioning bug
    # that manufactured an apparent 135-dimensional common kernel.
    parameter_ids = tuple(family["parameter_ids"])
    by_id = {parameter_id: index for index, parameter_id in enumerate(parameter_ids)}
    rows = np.asarray(family["constraint_rows"], dtype=float)
    anchors = [by_id[item] for item in REFERENCE_ANCHOR_PARAMETER_IDS]
    constraints = np.vstack((rows, np.eye(len(parameter_ids))[anchors]))
    target = np.concatenate((np.zeros(rows.shape[0]), np.ones(len(anchors))))
    reference_c = np.linalg.lstsq(constraints, target, rcond=1.0e-12)[0]

    hessian_basis = np.stack(
        [np.asarray(row.hessian, dtype=float) for row in parameter_rows]
    )
    hessian_basis = 0.5 * (hessian_basis + hessian_basis.transpose(0, 2, 1))
    quotient = np.asarray(
        physical_quotient_audit(include_basis=True)["quotient"], dtype=float
    )
    reference_hessian = np.tensordot(reference_c, hessian_basis, axes=(0, 0))
    projected_reference = quotient.T @ reference_hessian @ quotient
    equilibrium = _equilibrate_congruence(projected_reference)
    congruence = quotient * np.asarray(equilibrium["diagonal_scale"])[None, :]
    projected_parameter_basis = np.einsum(
        "ia,pij,jb->pab", congruence, hessian_basis, congruence, optimize="optimal"
    )
    projected_parameter_basis = 0.5 * (
        projected_parameter_basis + projected_parameter_basis.transpose(0, 2, 1)
    )
    stationary_generators = np.einsum(
        "pk,pab->kab",
        np.asarray(family["null_basis"]),
        projected_parameter_basis,
        optimize=True,
    )
    stationary_generators = 0.5 * (
        stationary_generators + stationary_generators.transpose(0, 2, 1)
    )
    reference_y = np.asarray(family["null_basis"]).T @ reference_c
    return {
        "parameter_ids": parameter_ids,
        "reference_coefficients": reference_c,
        "reference_free_coordinates": reference_y,
        "stationary_generators": stationary_generators,
        "equilibration": {
            key: value
            for key, value in equilibrium.items()
            if key not in {"matrix", "diagonal_scale"}
        },
    }


def _normalized_common_kernel(stationary_generators: np.ndarray) -> dict[str, Any]:
    matrices = np.asarray(stationary_generators, dtype=float)
    norms = np.linalg.norm(matrices.reshape(matrices.shape[0], -1), axis=1)
    active = norms > 0.0
    normalized = matrices[active] / norms[active, None, None]
    gram = np.zeros(matrices.shape[1:], dtype=float)
    for matrix in normalized:
        gram += matrix @ matrix
    eigenvalues = np.linalg.eigvalsh(0.5 * (gram + gram.T))
    threshold = COMMON_KERNEL_RANK_RTOL * float(eigenvalues[-1])
    rank = int(np.sum(eigenvalues > threshold))
    return {
        "evidence_kind": "heavy_recomputed_normalized_stationary_pencil_common_kernel",
        "recomputed_in_this_invocation": True,
        "stationary_pencil_generators": int(len(matrices)),
        "nonzero_Hessian_generators": int(np.sum(active)),
        "exactly_zero_Hessian_generators": int(np.sum(~active)),
        "nonzero_generator_frobenius_norm_min": float(np.min(norms[active])),
        "nonzero_generator_frobenius_norm_max": float(np.max(norms[active])),
        "normalized_Gram_min_eigenvalue": float(eigenvalues[0]),
        "normalized_Gram_max_eigenvalue": float(eigenvalues[-1]),
        "normalized_Gram_rank": rank,
        "relative_rank_tolerance": COMMON_KERNEL_RANK_RTOL,
        "common_kernel_dimension": int(len(eigenvalues) - rank),
        "structural_common_flat_subspace_found": rank < len(eigenvalues),
        "proof_grade": False,
    }


def _rayleigh_cut(vector: np.ndarray, matrices: np.ndarray) -> np.ndarray:
    return np.einsum("i,kij,j->k", vector, matrices, vector, optimize=True)


def _finite_cut_search(
    stationary_generators: np.ndarray,
    family: dict[str, Any],
    reference_y: np.ndarray,
    *,
    max_iterations: int,
) -> dict[str, Any]:
    matrices = np.asarray(stationary_generators, dtype=float)
    null_basis = np.asarray(family["null_basis"], dtype=float)
    parameter_ids = tuple(family["parameter_ids"])
    normalization_index = parameter_ids.index(NORMALIZATION_PARAMETER_ID)
    normalization_row = null_basis[normalization_index]
    reference_matrix = np.tensordot(reference_y, matrices, axes=(0, 0))
    initial_eigenvalues, initial_vectors = np.linalg.eigh(reference_matrix)
    cuts = [
        _rayleigh_cut(vector, matrices)
        for vector in initial_vectors[:, : min(80, len(initial_vectors))].T
    ]
    best_lower = float(initial_eigenvalues[0])
    best_y = np.asarray(reference_y, dtype=float).copy()
    best_eigenvalues = initial_eigenvalues.copy()
    last_upper = float("inf")
    history: list[dict[str, Any]] = []

    for iteration in range(int(max_iterations)):
        objective = np.zeros(null_basis.shape[1] + 1, dtype=float)
        objective[-1] = -1.0
        rows = [
            np.column_stack((null_basis, np.zeros(len(parameter_ids)))),
            np.column_stack((-null_basis, np.zeros(len(parameter_ids)))),
        ]
        rhs = [
            np.full(len(parameter_ids), COUPLING_BOUND),
            np.full(len(parameter_ids), COUPLING_BOUND),
        ]
        for cut in cuts:
            scale = max(float(np.max(np.abs(cut), initial=0.0)), MARGIN_SCALE)
            rows.append((np.concatenate((-cut, [MARGIN_SCALE])) / scale)[None, :])
            rhs.append(np.asarray([0.0]))
        equality = np.concatenate((normalization_row, [0.0]))
        equality_scale = max(float(np.max(np.abs(equality))), 1.0e-300)
        result = linprog(
            objective,
            A_ub=np.vstack(rows),
            b_ub=np.concatenate(rhs),
            A_eq=(equality / equality_scale)[None, :],
            b_eq=np.asarray([1.0 / equality_scale]),
            bounds=[(None, None)] * len(objective),
            method="highs-ipm",
            options={
                "dual_feasibility_tolerance": 1.0e-9,
                "primal_feasibility_tolerance": 1.0e-9,
                "ipm_optimality_tolerance": 1.0e-10,
            },
        )
        if not result.success:
            return {
                "evidence_kind": "heavy_recomputed_finite_cut_search",
                "recomputed_in_this_invocation": True,
                "termination": "LP_master_failure",
                "LP_status": int(result.status),
                "LP_message": str(result.message),
                "iterations": iteration,
                "proof_grade": False,
                "strict_local_minimum_certified": False,
                "PSD_feasibility_certified": False,
                "PSD_infeasibility_certified": False,
            }
        y = np.asarray(result.x[:-1], dtype=float)
        upper = float(MARGIN_SCALE * result.x[-1])
        candidate = np.tensordot(y, matrices, axes=(0, 0))
        eigenvalues, eigenvectors = np.linalg.eigh(0.5 * (candidate + candidate.T))
        lower = float(eigenvalues[0])
        if lower > best_lower:
            best_lower = lower
            best_y = y.copy()
            best_eigenvalues = eigenvalues.copy()
        last_upper = upper
        history.append(
            {
                "iteration": iteration,
                "cut_count": len(cuts),
                "finite_cut_relaxation_value": upper,
                "candidate_lower": lower,
                "best_lower": best_lower,
            }
        )
        for vector in eigenvectors[:, : min(24, len(eigenvectors))].T:
            cuts.append(_rayleigh_cut(vector, matrices))

    coefficients = null_basis @ best_y
    gap = float(last_upper - best_lower)
    return {
        "evidence_kind": "heavy_recomputed_finite_cut_search",
        "recomputed_in_this_invocation": True,
        "termination": "iteration_limit",
        "iterations": len(history),
        "cut_count": len(cuts),
        "coupling_bound": COUPLING_BOUND,
        "normalization_parameter_id": NORMALIZATION_PARAMETER_ID,
        "best_primal_lower_bound": best_lower,
        "finite_cut_relaxation_bound_noncertified": last_upper,
        "open_bracket_width": gap,
        "best_max_abs_coupling": float(np.max(np.abs(coefficients))),
        "best_negative_modes_at_1e-10": int(np.sum(best_eigenvalues < -1.0e-10)),
        "bracket_straddles_zero": best_lower < 0.0 < last_upper,
        "strict_local_minimum_certified": False,
        "PSD_feasibility_certified": False,
        "PSD_infeasibility_certified": False,
        "proof_grade": False,
        "history": history,
    }


def run_heavy_recomputation(*, max_iterations: int = 80) -> dict[str, Any]:
    diagnostic = corrected_kernel_source.corrected_common_kernel_diagnostic()
    passed = diagnostic["n_failed"] == 0
    return {
        "executed": True,
        "status": (
            "CORRECTED_COMMON_KERNEL_RECOMPUTED__SDP_SOLVER_BLOCKED"
            if passed
            else "CORRECTED_COMMON_KERNEL_RECOMPUTATION_FAILED"
        ),
        "requested": True,
        "requested_max_iterations": int(max_iterations),
        "dense_Hessians_assembled": True,
        "solver_started": False,
        "proof_grade": False,
        "corrected_common_kernel_diagnostic": diagnostic,
        "strict_local_minimum_certified": False,
        "PSD_feasibility_certified": False,
        "PSD_infeasibility_certified": False,
        "reason": (
            "The corrected 51-Hessian common-kernel diagnostic is permitted, "
            "but its float64 full-rank result is not a stability certificate. "
            "The finite-cut and SDP solvers remain quarantined."
        ),
        "unblock_condition": (
            "construct and audit a hierarchy-aware proof-grade primal/dual "
            "SDP pipeline on the exact 448-dimensional transverse space"
        ),
    }


def _dimension_six_boundary() -> dict[str, Any]:
    return {
        "operator": "126bar_H^2 10_H^2 S^2 / M_GUT^2 in the 54 channel",
        "included_in_renormalizable_44_direction_51_parameter_pencil": False,
        "exact_selected_vacuum_facts": {
            "P54_DeltaR_DeltaR": 0.0,
            "selected_vacuum_potential_amplitude": 0.0,
            "selected_H10_H10_mass_block": 0.0,
            "selected_phase_curvature": 0.0,
            "phase_vector_is_parallel_to_lambda4": True,
        },
        "interpretation": (
            "This historical dimension-six locking proposal does not provide a "
            "known rescue of the selected vacuum.  Its full component Hessian "
            "has not been integrated here, so the statement is not a theorem "
            "about every possible higher-dimensional completion."
        ),
    }


def _legacy_build_report_forensic_only(
    *, recompute_heavy: bool = False, max_iterations: int = 80
) -> dict[str, Any]:
    """Disabled report path that depended on the invalid SVD nullspace."""
    raise RuntimeError(LEGACY_STATIONARY_FAMILY_INVALIDATION_REASON)


def build_report(
    *, recompute_heavy: bool = False, max_iterations: int = 80
) -> dict[str, Any]:
    """Build the corrected light G3 report without constructing a false nullspace."""
    upstream = load_upstream_g2_report()
    counts = upstream.get("counts", {})
    upstream_flags = upstream.get("flags", {})
    upstream_stationarity = upstream.get("stationary_Hessian_bridge", {}).get(
        "promoted_stationarity_matrix", {}
    )
    sigma_certificate = g2_audit.exact_delta_r_projector_zero_certificate()
    phi_certificate = (
        g2_audit.exact_phi_projector_and_stationary_witness_certificate()
    )
    rank_lower_certificate = (
        g2_audit.exact_stationarity_rank_lower_bound_certificate()
    )
    rank_certificate = exact_rank_source.build_report()
    witness = phi_certificate["stationary_witness"]
    h6_witness = corrected_kernel_source.exact_h6_radial_curvature_certificate()
    common_kernel_regression = (
        corrected_kernel_source.recorded_common_kernel_regression()
    )
    constructive_candidate = sos_candidate_source.build_report()
    candidate_flags = constructive_candidate.get("flags", {})
    candidate_coefficients = constructive_candidate.get("coefficient_vector", {})
    symmetry = physical_quotient_audit()
    quotient_certificate = symmetry["exact_certificate"]
    numerical = recorded_numerical_evidence()
    heavy = (
        run_heavy_recomputation(max_iterations=max_iterations)
        if recompute_heavy
        else {
            "executed": False,
            "status": "NOT_REQUESTED",
            "requested": False,
            "dense_Hessians_assembled": False,
            "solver_started": False,
        }
    )

    numerical_rank = upstream_stationarity.get("rank")
    numerical_nullity = upstream_stationarity.get("nullity")
    invalidation = numerical["legacy_stationary_family_invalidation"]
    block = numerical["symmetry_block_reduction"]
    exact_three_zeros = bool(
        sigma_certificate["certified"]
        and phi_certificate["certified"]
        and phi_certificate["O44_B03_210_gradient_zero"]["certified"]
    )
    exact_rank_certified = bool(
        rank_certificate["certified"]
        and upstream_flags.get("stationarity_rank_13_exactly_certified")
        and upstream_flags.get("stationarity_nullity_38_exactly_certified")
        and upstream_flags.get(
            "compiler_gradients_bound_to_exact_nonzero_13x13_minor"
        )
    )
    stable_constraints_ready = bool(
        upstream_flags.get(
            "exact_informed_13_row_constraint_representation_ready"
        )
    )
    checks = {
        "upstream_model_contract_is_gauged_u1x": (
            upstream.get("model_contract_id") == MODEL_CONTRACT_ID
        ),
        "upstream_G2_dense_derivative_gate_passed": bool(
            upstream_flags.get("G2_gauged_u1x_derivatives_certified")
        ),
        "upstream_G2_artifact_binds_all_three_exact_zero_certificates": bool(
            upstream_flags.get(
                "exact_three_structural_zero_gradient_certificates"
            )
        ),
        "upstream_G2_artifact_binds_exact_rank13_lower_bound": bool(
            upstream_flags.get(
                "stationarity_rank_lower_bound_13_exactly_certified"
            )
        ),
        "upstream_G2_artifact_binds_exact_rank13_upper_bound": bool(
            upstream_flags.get(
                "stationarity_rank_upper_bound_13_exactly_certified"
            )
        ),
        "upstream_G2_artifact_binds_compiler_minor": bool(
            upstream_flags.get(
                "compiler_gradients_bound_to_exact_nonzero_13x13_minor"
            )
        ),
        "upstream_G2_artifact_binds_stable_13_row_constraints": (
            stable_constraints_ready
        ),
        "upstream_G2_artifact_binds_exact_stationary_witness": bool(
            upstream_flags.get("exact_stationary_witness_regression_passes")
        ),
        "gauged_direction_count_is_44": (
            counts.get("invariant_directions") == EXPECTED_DIRECTION_COUNT
        ),
        "gauged_parameter_count_is_51": (
            counts.get("real_parameters") == EXPECTED_PARAMETER_COUNT
        ),
        "real_field_dimension_is_486": counts.get("real_field_dimension")
        == chart.TOTAL_DIM,
        "all_three_structural_zero_gradients_are_exactly_certified": (
            exact_three_zeros
        ),
        "exact_nonzero_13x13_minor_proves_rank_at_least_13": (
            rank_lower_certificate["determinant_nonzero"]
            and rank_lower_certificate["certified_rank_lower_bound"] == 13
        ),
        "matching_exact_rank_upper_bound_proves_rank_13": (
            rank_lower_certificate["exact_rank_upper_bound_certified"] is True
            and rank_lower_certificate["exact_rank_13_certified"] is True
            and exact_rank_certified
        ),
        "normalized_SVD_rank13_nullity38_matches_the_exact_result": (
            numerical_rank == EXPECTED_STATIONARITY_RANK
            and numerical_nullity == EXPECTED_STATIONARITY_NULLITY
        ),
        "exact_stationary_counterexample_has_zero_gradient": witness[
            "gradient_exactly_zero"
        ],
        "exact_stationary_counterexample_satisfies_normalization_and_box": (
            witness["normalization_value"] == "1"
            and witness["strictly_inside_4pi_box"]
        ),
        "exact_P24_is_rank24_symmetric_idempotent": (
            phi_certificate["P24"]["rank"] == 24
            and phi_certificate["P24"]["trace"] == 24
            and phi_certificate["P24"]["idempotence_exact"]
        ),
        "exact_stationary_counterexample_P24_trace_is_positive_288": (
            witness["P24_trace"] == 288
        ),
        "exact_H6_radial_nonflat_stationary_witness_is_certified": (
            h6_witness["certified"]
            and h6_witness["radial_coordinate_name"] == "H[6].x"
            and not any(h6_witness["exact_symmetry_tangent_row"])
        ),
        "legacy_stationary_family_results_are_explicitly_invalidated": (
            invalidation["status"] == "INVALIDATED"
            and invalidation["invalidated"]
            and invalidation["scientific_use_for_G3"] is False
            and all(
                numerical[key]["status"] == "INVALIDATED"
                for key in (
                    "finite_cut_search",
                    "normalized_common_kernel",
                    "solver_attempts",
                )
            )
        ),
        "negative_trace_LP_is_invalidated_by_exact_positive_trace_witness": (
            block["invalidated_stationary_family_results"]
            ["candidate_trace_obstruction"]
            ["contradicted_by_exact_stationary_witness_trace_288"]
        ),
        "exact_quotient_certificate_is_bound_to_live_compiler": (
            quotient_certificate["certified"]
            and quotient_certificate["live_compiler_binding"][
                "compiler_binding_passes"
            ]
        ),
        "exact_SO10_orbit_rank_is_36": (
            quotient_certificate["SO10"]["rank"] == EXPECTED_SO10_RANK
            and quotient_certificate["SO10"]["minor"][
                "determinant_nonzero"
            ]
            and quotient_certificate["SO10"]["null_vector_rank"] == 9
        ),
        "exact_SO10_plus_U1X_gauge_rank_is_37": (
            quotient_certificate["gauged_SO10_U1X"]["rank"]
            == EXPECTED_SO10_U1X_RANK
            and quotient_certificate["gauged_SO10_U1X"]["minor"][
                "determinant_nonzero"
            ]
            and quotient_certificate["gauged_SO10_U1X"][
                "null_vector_rank"
            ]
            == 9
        ),
        "gauge_quotient_dimension_including_axion_is_449": (
            symmetry["gauge_quotient_dimension_including_axion"]
            == EXPECTED_GAUGE_QUOTIENT_DIMENSION
        ),
        "global_PQ_is_exactly_independent_of_gauge_orbit": (
            quotient_certificate["U1X_PQ_independence"]["determinant"]
            == -68
        ),
        "exact_full_removed_symmetry_rank_is_38": (
            quotient_certificate["full_SO10_U1X_global_PQ"]["rank"]
            == EXPECTED_FULL_SYMMETRY_RANK
            and quotient_certificate["full_SO10_U1X_global_PQ"]["minor"][
                "determinant_nonzero"
            ]
            and quotient_certificate["full_SO10_U1X_global_PQ"][
                "all_null_residuals_exactly_zero"
            ]
            and quotient_certificate["full_SO10_U1X_global_PQ"][
                "null_vector_rank"
            ]
            == 9
        ),
        "massive_transverse_quotient_dimension_is_448": (
            symmetry["massive_transverse_quotient_dimension"]
            == EXPECTED_MASSIVE_TRANSVERSE_QUOTIENT_DIMENSION
        ),
        "numerical_projection_basis_matches_exact_transverse_dimension": (
            symmetry["SO10_physical_rank_numerical_diagnostic"]
            == EXPECTED_SO10_RANK
            and symmetry["SO10_plus_U1X_rank_numerical_diagnostic"]
            == EXPECTED_SO10_U1X_RANK
            and symmetry[
                "SO10_plus_U1X_plus_PQ_rank_numerical_diagnostic"
            ]
            == EXPECTED_FULL_SYMMETRY_RANK
            and symmetry["numerical_massive_transverse_basis_dimension"]
            == EXPECTED_MASSIVE_TRANSVERSE_QUOTIENT_DIMENSION
            and symmetry["symmetry_quotient_overlap"] < 1.0e-12
            and symmetry["quotient_orthonormality_residual"] < 1.0e-12
        ),
        "physical_quotient_dimension_is_448": (
            symmetry["physical_quotient_dimension"]
            == EXPECTED_MASSIVE_TRANSVERSE_QUOTIENT_DIMENSION
        ),
        "symmetry_block_dimensions_sum_to_448": (
            block["block_dimension_sum"]
            == EXPECTED_PHYSICAL_QUOTIENT_DIMENSION
        ),
        "legacy_reference_equilibrated_135_flat_claim_is_invalidated": (
            common_kernel_regression["invalidated_reference_equilibration"][
                "invalidated"
            ]
            and common_kernel_regression[
                "invalidated_reference_equilibration"
            ]["scientific_use_for_G3"]
            is False
            and common_kernel_regression[
                "invalidated_reference_equilibration"
            ]["apparent_common_Gram_nullity_at_1e_minus_8"]
            == 135
        ),
        "corrected_common_Gram_is_numerically_rank448_nullity0": (
            common_kernel_regression["corrected_raw_orthonormal_quotient"][
                "field_congruence"
            ]
            == "identity"
            and common_kernel_regression[
                "corrected_raw_orthonormal_quotient"
            ]["common_Gram_rank"]
            == EXPECTED_MASSIVE_TRANSVERSE_QUOTIENT_DIMENSION
            and common_kernel_regression[
                "corrected_raw_orthonormal_quotient"
            ]["common_Gram_nullity"]
            == 0
        ),
        "constructive_sparse_candidate_audit_passes": (
            constructive_candidate.get("model_contract_id") == MODEL_CONTRACT_ID
            and constructive_candidate.get("n_failed") == 0
            and candidate_flags.get(
                "exact_sparse_51_parameter_candidate_constructed"
            )
            and candidate_coefficients.get("nonzero_count") == 27
            and candidate_coefficients.get("maximum_absolute_coefficient")
            < COUPLING_BOUND
        ),
        "historical_positive_J0_anchor_is_not_WLOG": (
            candidate_flags.get(
                "positive_J0_normalization_is_without_loss_of_generality"
            )
            is False
            and candidate_coefficients.get("symbolic_nonzero", {}).get(
                NORMALIZATION_PARAMETER_ID
            )
            == "-21/200"
        ),
        "constructive_A_square_recoupling_is_exactly_source_bound": (
            candidate_flags.get("A_square_recoupling_exactly_source_bound")
            is True
        ),
        "constructive_candidate_exact_local_minimum_is_source_bound": (
            candidate_flags.get(
                "P_plus_Delta_Qsqrt2_component_LDL_conditional"
            )
            is False
            and candidate_flags.get("full_448_kernel_count_conditional")
            is False
            and candidate_flags.get(
                "P_plus_Delta_source_binding_exactly_certified"
            )
            is True
            and candidate_flags.get("full_448_kernel_count_exact") is True
            and candidate_flags.get(
                "complete_potential_BFB_exactly_certified"
            )
            is True
            and candidate_flags.get(
                "selected_vacuum_stationarity_exactly_compiler_certified"
            )
            is True
            and candidate_flags.get("full_448_PSD_feasibility_certified")
            is True
            and candidate_flags.get("strict_local_minimum_certified") is True
            and candidate_flags.get("selected_vacuum_global_minimum_certified")
            is False
            and candidate_flags.get("selected_vacuum_global_minimum_disproved")
            is True
            and candidate_flags.get("selected_vacuum_unique_modulo_symmetry")
            is False
            and candidate_flags.get("G3_closed") is False
        ),
        "constructive_candidate_exact_global_counterexample_is_source_bound": (
            candidate_flags.get("exact_lower_energy_field_witness_certified")
            is True
            and candidate_flags.get("selected_vacuum_global_minimum_disproved")
            is True
            and candidate_flags.get("constructive_candidate_rejected_for_G3")
            is True
        ),
        "heavy_option_recomputes_only_diagnostic_and_blocks_solver": (
            not recompute_heavy
            or (
                heavy["status"]
                == "CORRECTED_COMMON_KERNEL_RECOMPUTED__SDP_SOLVER_BLOCKED"
                and heavy["executed"] is True
                and heavy["dense_Hessians_assembled"] is True
                and heavy["solver_started"] is False
                and heavy["proof_grade"] is False
                and heavy["corrected_common_kernel_diagnostic"][
                    "corrected_common_kernel"
                ]["rank"]
                == EXPECTED_MASSIVE_TRANSVERSE_QUOTIENT_DIMENSION
                and heavy["corrected_common_kernel_diagnostic"][
                    "corrected_common_kernel"
                ]["nullity"]
                == 0
            )
        ),
        "strict_local_minimum_is_claimed_only_for_selected_orbit": (
            candidate_flags.get("strict_local_minimum_certified") is True
            and candidate_flags.get("selected_vacuum_global_minimum_certified")
            is False
            and candidate_flags.get("selected_vacuum_global_minimum_disproved")
            is True
        ),
        "fixed_vacuum_no_go_not_claimed": True,
        "complete_potential_BFB_is_exactly_certified": (
            candidate_flags.get("complete_potential_BFB_exactly_certified")
            is True
        ),
        "selected_global_minimum_exactly_disproved": (
            candidate_flags.get("selected_vacuum_global_minimum_disproved")
            is True
        ),
        "model_wide_exclusion_not_claimed": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    massive_transverse_quotient_certified = all(
        checks[name]
        for name in (
            "exact_quotient_certificate_is_bound_to_live_compiler",
            "exact_SO10_orbit_rank_is_36",
            "exact_SO10_plus_U1X_gauge_rank_is_37",
            "gauge_quotient_dimension_including_axion_is_449",
            "global_PQ_is_exactly_independent_of_gauge_orbit",
            "exact_full_removed_symmetry_rank_is_38",
            "massive_transverse_quotient_dimension_is_448",
        )
    )
    numerical_transverse_projection_constructed = checks[
        "numerical_projection_basis_matches_exact_transverse_dimension"
    ]
    status = (
        "G3_SELECTED_VACUUM_REJECTED_BY_EXACT_GLOBAL_COUNTEREXAMPLE"
        if not failures
        else "G3_GAUGED_U1X_AUDIT_EXECUTION_FAILED"
    )
    return _jsonable(
        {
            "model_contract_id": MODEL_CONTRACT_ID,
            "status": status,
            "overall_state": "OPEN" if not failures else "EXECUTION_FAIL",
            "authoritative_for_manuscript_G3_formulation": not failures,
            "n_checks": len(checks),
            "n_failed": len(failures),
            "failures": failures,
            "execution_failures": failures,
            "checks": checks,
            "coverage": {
                "invariant_directions": counts.get("invariant_directions"),
                "real_parameters": counts.get("real_parameters"),
                "real_field_dimension": counts.get("real_field_dimension"),
                "stationarity_rank": numerical_rank,
                "stationarity_nullity": numerical_nullity,
                "exact_stationarity_rank": rank_certificate["rank"],
                "exact_stationarity_nullity": rank_certificate["nullity"],
                "exact_stationarity_rank_lower_bound": rank_lower_certificate[
                    "certified_rank_lower_bound"
                ],
                "gauge_quotient_dimension_including_axion": symmetry[
                    "gauge_quotient_dimension_including_axion"
                ],
                "massive_transverse_quotient_dimension": symmetry[
                    "massive_transverse_quotient_dimension"
                ],
                "physical_quotient_dimension": symmetry[
                    "physical_quotient_dimension"
                ],
            },
            "stationarity_contract": {
                "analytic_zero_gradient_parameter_ids": list(
                    g2_audit.ANALYTIC_ZERO_GRADIENT_PARAMETER_IDS
                ),
                "exact_three_zero_gradient_certificates": exact_three_zeros,
                "exact_Delta_R_projector_zero_certificate": sigma_certificate,
                "exact_mixed_Phi_Sigma_210_zero_certificate": phi_certificate[
                    "O44_B03_210_gradient_zero"
                ],
                "rank": numerical_rank,
                "nullity": numerical_nullity,
                "rank_interpretation": (
                    "exact rank 13/nullity 38; normalized float64 SVD 13/38 "
                    "is a consistency diagnostic only"
                ),
                "exact_rank_lower_bound": rank_lower_certificate[
                    "certified_rank_lower_bound"
                ],
                "exact_rank_lower_bound_certificate": rank_lower_certificate,
                "exact_rank_13_nullity_38_certificate": rank_certificate,
                "exact_rank_upper_bound_certified": exact_rank_certified,
                "stationarity_rank_13_exactly_certified": exact_rank_certified,
                "stationarity_nullity_38_exactly_certified": exact_rank_certified,
                "exact_stationarity_nullspace_certified": False,
                "exact_stationarity_rank_certificate_open": False,
                "exact_projector_zero_corrected_normalized_SVD_rank_13": (
                    numerical_rank == 13 and numerical_nullity == 38
                ),
                "exact_informed_constraint_representation": {
                    "status": "CERTIFIED_BY_UPSTREAM_G2_COMPILER_AUDIT",
                    "upstream_certified": stable_constraints_ready,
                    "compiler_pivot_rows": list(
                        exact_rank_source.STABLE_COMPILER_PIVOT_ROWS
                    ),
                    "compiler_pivot_coordinates": [
                        chart.coordinate_names()[row]
                        for row in exact_rank_source.STABLE_COMPILER_PIVOT_ROWS
                    ],
                    "exact_unit_parameter_ids": list(
                        exact_rank_source.STABLE_EXACT_UNIT_PARAMETER_IDS
                    ),
                    "constructor": (
                        "exact_gauged_u1x_stationarity_rank_certificate_v20."
                        "exact_informed_stationarity_constraints"
                    ),
                    "legacy_column_normalize_backscale_used": False,
                    "numerical_null_basis_proof_grade": False,
                },
                "exact_stationary_witness": witness,
                "exact_H6_radial_nonflat_witness": h6_witness,
                "legacy_normalized_SVD_family": invalidation,
                "reason": (
                    "Three columns vanish by exact projector identities. A "
                    "nonzero exact 13x13 compiler-bound minor and the exact "
                    "factorization A=L A[pivots,:] prove rank/nullity 13/38. "
                    "The old SVD nullspace remains unusable; the replacement "
                    "uses 11 normalized compiler rows plus exact re/im(O31) "
                    "unit equations and accepts the exact witness."
                ),
            },
            "symmetry_quotient": symmetry,
            "corrected_common_kernel_reaudit": {
                "status": "NUMERICAL_CONDITIONING_REGRESSION_ONLY",
                "exact_H6_radial_nonflat_witness": h6_witness,
                "recorded_numerical_regression": common_kernel_regression,
                "recomputed_in_this_invocation": bool(recompute_heavy),
                "recomputed_diagnostic": (
                    heavy.get("corrected_common_kernel_diagnostic")
                    if recompute_heavy
                    else None
                ),
                "proof_grade": False,
                "strict_local_minimum_certified": False,
                "PSD_feasibility_certified": False,
                "fixed_vacuum_no_go_certified": False,
            },
            "constructive_candidate_reaudit": constructive_candidate,
            "SDP_formulation": {
                "status": "EXACT_LOCAL_MINIMUM_FOUND__GLOBAL_COUNTEREXAMPLE_REJECTS_CANDIDATE",
                "kind": "conceptual_linear_matrix_pencil_semidefinite_program",
                "stationary_parameterization_available": stable_constraints_ready,
                "stationary_parameterization_is_exact_informed_numerical": True,
                "exact_nullspace_basis_available": False,
                "solver_started": False,
                "historical_positive_J0_anchor_WLOG": False,
                "historical_positive_J0_anchor_counterexample": {
                    "parameter_id": NORMALIZATION_PARAMETER_ID,
                    "constructive_candidate_exact_value": "-21/200",
                },
                "equations_after_unblock": [
                    "A c = 0 exactly",
                    "-4*pi <= c_i <= 4*pi",
                    (
                        "use a sign-complete nonzero normalization or audit the "
                        "positive-J0, negative-J0, and J0=0 branches separately"
                    ),
                    "Q^T (sum_i c_i H_i) Q - t I_448 >= 0",
                ],
                "strict_local_minimum_criterion": "certified optimum t > 0",
                "fixed_vacuum_PSD_no_go_criterion": "certified optimum t < 0",
                "unblock_condition": (
                    "replace the rejected candidate or promote the lower-energy "
                    "field configuration after independently proving its full "
                    "stationarity, then prove an exact global energy-gap "
                    "bound and classify its equality orbit"
                ),
            },
            "numerical_evidence": numerical,
            "heavy_recomputation": heavy,
            "dimension_six_boundary": _dimension_six_boundary(),
            "flags": {
                "G1_gauged_u1x_contract_required": True,
                "G2_gauged_u1x_derivatives_required": True,
                "G3_numerical_rank13_stationarity_family_constructed": (
                    stable_constraints_ready
                ),
                "G3_exact_informed_13_row_constraints_ready": (
                    stable_constraints_ready
                ),
                "legacy_stationary_family_numerics_invalidated": True,
                "exact_three_structural_zero_gradient_certificates": (
                    exact_three_zeros
                ),
                "stationarity_rank_lower_bound_13_exactly_certified": True,
                "stationarity_rank_upper_bound_13_only_numerical": False,
                "stationarity_rank_upper_bound_13_exactly_certified": (
                    exact_rank_certified
                ),
                "stationarity_rank_13_exactly_certified": exact_rank_certified,
                "stationarity_nullity_38_exactly_certified": exact_rank_certified,
                "G3_stationary_nullspace_certified": False,
                "exact_P24_structural_certificate": True,
                "exact_stationary_witness_trace_288": True,
                "exact_H6_radial_nonflat_stationary_witness_certified": (
                    checks[
                        "exact_H6_radial_nonflat_stationary_witness_is_certified"
                    ]
                ),
                "legacy_reference_equilibrated_common_kernel_135_invalidated": (
                    checks[
                        "legacy_reference_equilibrated_135_flat_claim_is_invalidated"
                    ]
                ),
                "corrected_common_kernel_rank448_nullity0_numerical_only": (
                    checks[
                        "corrected_common_Gram_is_numerically_rank448_nullity0"
                    ]
                ),
                "corrected_common_kernel_proof_grade": False,
                "corrected_common_kernel_recomputed_this_invocation": bool(
                    recompute_heavy
                ),
                "constructive_sparse_27_parameter_candidate_found": (
                    checks["constructive_sparse_candidate_audit_passes"]
                ),
                "constructive_candidate_max_abs_coefficient_73_over_8": (
                    candidate_coefficients.get("maximum_absolute_coefficient")
                    == 73 / 8
                ),
                "historical_positive_J0_normalization_invalidated": (
                    checks["historical_positive_J0_anchor_is_not_WLOG"]
                ),
                "constructive_candidate_conditional_rank448_evidence": False,
                "constructive_candidate_exact_rank448_certificate": checks[
                    "constructive_candidate_exact_local_minimum_is_source_bound"
                ],
                "constructive_A_square_recoupling_exactly_source_bound": (
                    checks[
                        "constructive_A_square_recoupling_is_exactly_source_bound"
                    ]
                ),
                "constructive_candidate_direct_exact_source_binding": bool(
                    candidate_flags.get(
                        "P_plus_Delta_source_binding_exactly_certified", False
                    )
                ),
                "exact_SO10_orbit_rank_36_certified": (
                    checks["exact_SO10_orbit_rank_is_36"]
                    and checks[
                        "exact_quotient_certificate_is_bound_to_live_compiler"
                    ]
                ),
                "exact_gauge_orbit_rank_37_certified": (
                    checks["exact_SO10_plus_U1X_gauge_rank_is_37"]
                    and checks[
                        "exact_quotient_certificate_is_bound_to_live_compiler"
                    ]
                ),
                "gauge_quotient_dimension_449_including_axion_certified": (
                    checks["gauge_quotient_dimension_including_axion_is_449"]
                    and checks[
                        "exact_quotient_certificate_is_bound_to_live_compiler"
                    ]
                ),
                "exact_full_symmetry_orbit_rank_38_certified": (
                    checks["exact_full_removed_symmetry_rank_is_38"]
                    and checks[
                        "exact_quotient_certificate_is_bound_to_live_compiler"
                    ]
                ),
                "massive_transverse_quotient_dimension_448_certified": (
                    massive_transverse_quotient_certified
                ),
                "G3_massive_transverse_projection_basis_constructed": (
                    numerical_transverse_projection_constructed
                ),
                "G3_corrected_physical_quotient_constructed": (
                    numerical_transverse_projection_constructed
                ),
                "physical_quotient_dimension_448_certified": (
                    massive_transverse_quotient_certified
                ),
                (
                    "physical_quotient_dimension_448_is_legacy_name_for_"
                    "massive_transverse"
                ): True,
                "G3_fixed_vacuum_strict_minimum_certified": checks[
                    "constructive_candidate_exact_local_minimum_is_source_bound"
                ],
                "G3_fixed_vacuum_PSD_feasible_certified": checks[
                    "constructive_candidate_exact_local_minimum_is_source_bound"
                ],
                "G3_fixed_vacuum_no_go_certified": False,
                "G3_selected_vacuum_global_no_go_certified": checks[
                    "constructive_candidate_exact_global_counterexample_is_source_bound"
                ],
                "exact_lower_energy_field_witness_certified": checks[
                    "constructive_candidate_exact_global_counterexample_is_source_bound"
                ],
                "constructive_candidate_rejected_for_G3": checks[
                    "constructive_candidate_exact_global_counterexample_is_source_bound"
                ],
                "complete_potential_BFB": checks[
                    "complete_potential_BFB_is_exactly_certified"
                ],
                "global_competing_extrema_exhausted": False,
                "G3_closed": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
                "empirical_discovery": False,
            },
            "next_exact_target": (
                "Audit the lower-energy field witness (or a replacement "
                "candidate) through its exact quotient Hessian, then prove a "
                "global energy-gap certificate and classify the equality orbit."
            ),
            "verdict": (
                "The prior G3 stationary-family numerics are invalid: their "
                "normalized-SVD constraints reject an exact stationary "
                "witness whose exact P24 Hessian trace is +288. Consequently "
                "the finite-cut, common-kernel, block-SDP, and negative-trace "
                "LP results cannot support either a minimum or a no-go. The "
                "exact factorization and compiler-bound minor now close the "
                "stationarity rank/nullity at 13/38. A well-conditioned corrected "
                "constraint representation is available, while its numerical "
                "null basis is not itself proof-grade. Exact integer tangents "
                "certify gauge rank 37 and a 449-dimensional gauge quotient "
                "including the axion; removing independent global PQ gives the "
                "448-dimensional massive/transverse Hessian space. The exact "
                "rank-24 P24 projector also survives. An exact stationary "
                "H[6].x witness has curvature 4h^2>0, so its tiny hierarchy "
                "scale is not an exact flat. On the raw orthonormal transverse "
                "quotient, the corrected common Gram is numerically rank/nullity "
                "448/0; the apparent 135-flat result comes only from an "
                "ill-conditioned reference congruence and is invalidated. "
                "Neither historical numerical fact is used as a PSD "
                "certificate. A new sparse "
                "27-parameter candidate, with maximum coefficient 73/8 and "
                "exact J0=-21/200, invalidates the old assumption that J0=+1 "
                "was a WLOG stability normalization. Exact source-bound SOS "
                "identities certify the complete potential BFB and the "
                "selected vacuum stationary. Direct Gaussian-integer/Fraction "
                "assembly and exact Q(sqrt(2)) arithmetic give P+Delta_R "
                "rank/nullity 429/33; an explicit exact quotient Jacobian "
                "leaves precisely the 38 symmetry tangents and proves all 448 "
                "transverse Hessian directions positive. Thus the selected "
                "orbit is a strict local minimum. The final exact global-gap "
                "test constructs a symmetry-inequivalent 126bar field "
                "orientation whose energy is lower by 25*r^4/19008. Thus the "
                "selected orbit is not global and this candidate is rejected "
                "for G3. The lower orbit still needs a quotient-Hessian and "
                "globality audit, so the whole model is neither validated nor "
                "excluded."
            ),
        }
    )


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    block = report["numerical_evidence"]["symmetry_block_reduction"]
    symmetry = report["symmetry_quotient"]
    witness = report["stationarity_contract"]["exact_stationary_witness"]
    h6 = report["stationarity_contract"]["exact_H6_radial_nonflat_witness"]
    common = report["corrected_common_kernel_reaudit"][
        "recorded_numerical_regression"
    ]["corrected_raw_orthonormal_quotient"]
    candidate = report["constructive_candidate_reaudit"]
    candidate_coefficients = candidate["coefficient_vector"]
    OUT_MD.write_text(
        "# Gauged-U(1)_X G3 stability audit — v20\n\n"
        f"**Status:** `{report['status']}`\n\n"
        f"**State:** `{report['overall_state']}`\n\n"
        "- scalar directions / real parameters: "
        f"`{report['coverage']['invariant_directions']}/"
        f"{report['coverage']['real_parameters']}`;\n"
        "- stationarity rank / nullity: "
        f"`{report['coverage']['stationarity_rank']}/"
        f"{report['coverage']['stationarity_nullity']}`;\n"
        f"- SO(10)+U(1)_X+PQ removed rank: "
        f"`{symmetry['SO10_plus_U1X_plus_PQ_rank']}`;\n"
        f"- SO(10)+U(1)_X gauge quotient (axion included): "
        f"`{symmetry['gauge_quotient_dimension_including_axion']}`;\n"
        f"- massive/transverse quotient after global PQ: "
        f"`{symmetry['massive_transverse_quotient_dimension']}`;\n"
        f"- exact stationarity-rank lower bound: "
        f"`{report['coverage']['exact_stationarity_rank_lower_bound']}`;\n"
        f"- exact stationary-witness P24 trace: "
        f"`{witness['P24_trace']}`;\n"
        f"- exact H[6].x stationary curvature: `4 h^2 > 0`;\n"
        f"- corrected numerical common-Gram rank / nullity: "
        f"`{common['common_Gram_rank']}/{common['common_Gram_nullity']}`;\n"
        "- constructive candidate nonzero parameters: "
        f"`{candidate_coefficients['nonzero_count']}/51`;\n"
        "- constructive candidate max |coefficient|: "
        f"`{candidate_coefficients['maximum_absolute_coefficient']}`;\n"
        "- constructive candidate exact 210 J0: `-21/200`.\n\n"
        "G2 proves three exact structural zero-gradient columns and an exact "
        "nonzero 13x13 compiler-bound minor. Together with the exact full-row "
        "factorization, this proves stationarity rank/nullity 13/38. The "
        "corrected numerical family uses 11 normalized compiler rows and exact "
        "unit equations for re/im(O31), without column normalization or "
        "singular-vector backscaling. Exact Gaussian-integer tangents, bound "
        "directly to the live compiler, certify gauge rank 37 and full "
        "SO(10)+U(1)_X+global-PQ rank 38. The gauge quotient is 449-dimensional "
        "and contains the axion; the Hessian projection further removes global "
        "PQ and is the 448-dimensional massive/transverse space. "
        f"The unbroken-gauge Casimir reduction gives eight blocks summing to "
        f"`{block['block_dimension_sum']}` dimensions, and P24 is now an exact "
        "rank-24 projector. However, the old normalized-SVD stationary family "
        "rejects the exact witness (10,1,-1/4), whose dense gradient vanishes "
        "exactly and whose P24 trace is +288. The finite-cut, common-kernel, "
        "block-SDP, and negative-trace LP results are therefore invalidated. "
        f"Independently, the exact H[6].x witness has curvature "
        f"`{h6['exact_second_derivative']}`, so its hierarchy-suppressed "
        "float magnitude is not an exact flat. Recomputing the stationary "
        "pencil on the raw orthonormal 448-space quotient gives numerical "
        "common-Gram rank/nullity 448/0. The apparent 135-flat result is "
        "created only by a reference-derived congruence with condition ratio "
        "above 10^8 and is invalidated. The heavy finite-cut and SDP solvers "
        "remain quarantined pending a hierarchy-aware proof-grade pipeline. "
        "A sparse 27-parameter candidate supplies exact source-bound SOS "
        "identities for the complete potential and direct exact P+Delta_R "
        "rank/nullity 429/33. "
        "Because its exact J0 is -21/200, the historical J0=+1 slice is not "
        "WLOG. The complete potential is exactly BFB and stationary at the "
        "selected vacuum. The source-bound full-Hessian certificate leaves "
        "only 38 symmetry zero modes and proves positivity on all 448 "
        "transverse directions, so the selected orbit is a strict local "
        "minimum. An exact symmetry-inequivalent field configuration has energy "
        "lower by `25*r^4/19008`, so the selected vacuum is not global and the "
        "candidate is rejected for G3. The lower orbit still requires its own "
        "full-stationarity, Hessian, and global-gap classification; G3 is not "
        "closed.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--recompute-heavy",
        action="store_true",
        help=(
            "recompute the corrected numerical common-kernel diagnostic; the "
            "finite-cut and SDP solvers remain fail-closed"
        ),
    )
    parser.add_argument("--max-iterations", type=int, default=80)
    args = parser.parse_args(argv)
    report = build_report(
        recompute_heavy=args.recompute_heavy,
        max_iterations=args.max_iterations,
    )
    if args.write:
        write_report(report)
    print(json.dumps(report, indent=2))
    return 0 if report["overall_state"] != "EXECUTION_FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
