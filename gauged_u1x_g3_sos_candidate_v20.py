#!/usr/bin/env python3
"""Constructive bounded stationary candidate for the exact-X scalar theory.

This module records a sparse member of the authoritative 44-direction,
51-real-parameter potential.  Its construction combines

* the exact globally bounded Pati--Salam 210 potential;
* positive 126bar self-projector weights;
* two candidate positive Phi--Sigma contraction squares;
* elementary H/S/Phi17 norm and alignment squares.

The candidate is useful because it lies outside the historical ``J0=+1``
slice: its exact 210 coefficient is ``J0=-21/200``.  Therefore that old
normalization was not without loss of generality for a stability search.

The integer recoupling

    ||A_Phi Sigma||^2 =
        40 I_1 + 72 I_45 + 28 I_210
        - 8 I_770 - 12 I_5940 + 12 I_8910

is now bound by an exact Gaussian-integer/Fraction six-witness certificate.
An independent exact end-to-end expansion also certifies boundedness of the
complete sparse potential and exact stationarity of the selected vacuum. A
separate direct Gaussian-integer/Fraction construction certifies positivity of
all 448 transverse Hessian directions, so the selected symmetry orbit is a
strict local minimum.  A final exact global-gap test now supplies a different
126bar field configuration at lower energy.  The selected orbit is therefore
not the global minimum and this candidate cannot close G3. ``--recompute-heavy``
binds the coefficient vector to the live 486-real compiler and records
independent float64 diagnostics.
"""
from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import exact_210_pati_salam_global_vacuum_v20 as phi_source
import exact_gauged_u1x_g3_a_square_recoupling_v20 as a_square_source
import exact_gauged_u1x_g3_global_counterexample_v20 as global_counterexample_source
import exact_gauged_u1x_g3_pd_rank_certificate_v20 as pd_rank_source
import exact_gauged_u1x_g3_sos_bfb_stationarity_v20 as exact_sos_source
import exact_gauged_u1x_physical_quotient_v20 as quotient_source
import gauged_u1x_g2_derivative_audit_v20 as g2_audit
import live_g2_arbitrary_component_potential_values_v20 as potential
import live_g2_canonical_486_field_chart_v20 as chart
import live_g2_exact_quadratic_family_derivatives_v20 as derivatives

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json"
OUT_MD = ROOT / "GAUGED_U1X_G3_SOS_CANDIDATE_V20.md"

MODEL_CONTRACT_ID = "gauged_u1x_phi17_v20"
EXPECTED_PARAMETER_COUNT = 51
EXPECTED_FIELD_DIMENSION = 486
EXPECTED_REMOVED_SYMMETRY_RANK = 38
EXPECTED_PHYSICAL_DIMENSION = 448
SIGMA_SCALE = Fraction(1, 8)

PHI_J_COEFFICIENTS = {
    "lambda::O48_B01_Phi_self_quartics": Fraction(-21, 200),
    "lambda::O48_B02_Phi_self_quartics": Fraction(2467, 28800),
    "lambda::O48_B03_Phi_self_quartics": Fraction(-77, 3200),
    "lambda::O48_B04_Phi_self_quartics": Fraction(119, 115200),
}

# Basis order: 1,45,210,770,5940,8910.
A_SQUARED_RECOUPLING = (40, 72, 28, -8, -12, 12)
C_SQUARED_RECOUPLING = (1, 1, 1, 1, 1, 1)
TOTAL_MIXED_RECOUPLING = tuple(
    left + right
    for left, right in zip(
        A_SQUARED_RECOUPLING, C_SQUARED_RECOUPLING, strict=True
    )
)

RECORDED_NUMERICAL_EVIDENCE = {
    "evidence_kind": "scratch_float64_candidate_diagnostic",
    "recomputed_in_this_invocation": False,
    "proof_grade": False,
    "candidate_max_abs_coupling": 9.125,
    "compiler_gradient_max_abs_residual": 1.7763541510632597e-15,
    "P_plus_Delta_gauge_rank": 33,
    "P_plus_Delta_quotient_dimension": 429,
    "P_plus_Delta_unscaled_minimum_eigenvalue_before_sigma_scale": (
        3.372615386965929e-10
    ),
    "full_massive_transverse_dimension": 448,
    "full_raw_minimum_eigenvalue": -4.6550653645152325e-15,
    "full_raw_maximum_eigenvalue": 12.70866463982956,
    "full_raw_eigenvalues_below_minus_1e_minus_12": 0,
    "strict_local_minimum_certified": False,
    "PSD_feasibility_certified": False,
    "interpretation": (
        "These are secondary float64 diagnostics. Direct exact tensor assembly "
        "and Q(sqrt(2)) LDL now own the transverse-Hessian certification."
    ),
}


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    return value


def hierarchy_scales() -> dict[str, float]:
    state = g2_audit.physical_hierarchy_state()
    h = float(np.real(state.h[6]))
    r = float(np.real(state.s))
    x = float(np.real(state.x))
    if not (h > 0.0 and r > 0.0 and x > 0.0):
        raise ArithmeticError("the selected hierarchy scales must be positive")
    sigma_norm = float(
        potential.direct.sigma_kinetic_inner(state.sigma, state.sigma).real
    )
    if not math.isclose(sigma_norm, r * r, rel_tol=1.0e-12, abs_tol=0.0):
        raise ArithmeticError("the selected Sigma and S hierarchy scales drifted")
    return {"h": h, "r": r, "x": x, "alpha": h * h / r}


def symbolic_nonzero_coefficients() -> dict[str, str]:
    """Return the sparse coefficient vector as exact formulas in h,r,x."""
    output = {
        "lambda::O07_B01_Phi_norm": "-2",
        **{parameter_id: str(value) for parameter_id, value in PHI_J_COEFFICIENTS.items()},
        "lambda::O05_B01_126bar_norm": "(1/8)*(4-(25/12)*r^2)",
        "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": "-1/2",
        "lambda::O27_B01_126bar_self_projectors": "1/4",
        "lambda::O27_B02_126bar_self_projectors": "1/4",
        "lambda::O27_B03_126bar_self_projectors": "17/128",
        "lambda::O27_B04_126bar_self_projectors": "1/8",
        "lambda::O44_B01_Phi2_Sigma_projectors": "41/8",
        "lambda::O44_B02_Phi2_Sigma_projectors": "73/8",
        "lambda::O44_B03_Phi2_Sigma_projectors": "29/8",
        "lambda::O44_B04_Phi2_Sigma_projectors": "-7/8",
        "lambda::O44_B05_Phi2_Sigma_projectors": "-11/8",
        "lambda::O44_B06_Phi2_Sigma_projectors": "13/8",
        "lambda::O06_B01_Hdag_H_norm": "-2*h^2",
        "re::O12_B01_Hdag_Hdag_pair": "-h^2/r",
        "lambda::O04_B01_singlet_polynomial": "h^4/r^2-2*r^2",
        "lambda::O23_B01_singlet_polynomial": "1",
        "lambda::O36_B01_H_self_quartics": "2",
        "lambda::O36_B02_H_self_quartics": "2",
        "lambda::O46_B01_Phi2_HdagH_channels": "3/5",
        "lambda::O46_B03_Phi2_HdagH_channels": "-1",
        "lambda::O03_B01_singlet_polynomial": "-x^2/16",
        "lambda::O20_B01_singlet_polynomial": "1/32",
    }
    return output


def evaluated_nonzero_coefficients(
    scales: dict[str, float] | None = None,
) -> dict[str, float]:
    values = hierarchy_scales() if scales is None else dict(scales)
    h = float(values["h"])
    r = float(values["r"])
    x = float(values["x"])
    t = float(SIGMA_SCALE)
    output = {
        "lambda::O07_B01_Phi_norm": -2.0,
        **{
            parameter_id: float(value)
            for parameter_id, value in PHI_J_COEFFICIENTS.items()
        },
        "lambda::O05_B01_126bar_norm": t * (4.0 - (25.0 / 12.0) * r * r),
        "lambda::O14_B01_Phi_Sigma_Sigmadag_cubic": -4.0 * t,
        "lambda::O27_B01_126bar_self_projectors": 2.0 * t,
        "lambda::O27_B02_126bar_self_projectors": 2.0 * t,
        "lambda::O27_B03_126bar_self_projectors": (17.0 / 16.0) * t,
        "lambda::O27_B04_126bar_self_projectors": t,
        **{
            f"lambda::O44_B0{index + 1}_Phi2_Sigma_projectors": t * value
            for index, value in enumerate(TOTAL_MIXED_RECOUPLING)
        },
        "lambda::O06_B01_Hdag_H_norm": -2.0 * h * h,
        "re::O12_B01_Hdag_Hdag_pair": -(h * h / r),
        "lambda::O04_B01_singlet_polynomial": h**4 / r**2 - 2.0 * r**2,
        "lambda::O23_B01_singlet_polynomial": 1.0,
        "lambda::O36_B01_H_self_quartics": 2.0,
        "lambda::O36_B02_H_self_quartics": 2.0,
        "lambda::O46_B01_Phi2_HdagH_channels": 3.0 / 5.0,
        "lambda::O46_B03_Phi2_HdagH_channels": -1.0,
        "lambda::O03_B01_singlet_polynomial": -(x * x) / 16.0,
        "lambda::O20_B01_singlet_polynomial": 1.0 / 32.0,
    }
    return output


def full_coefficient_vector(
    scales: dict[str, float] | None = None,
) -> dict[str, float]:
    selection = g2_audit.contract_selection()
    parameter_ids = tuple(str(value) for value in selection["parameter_ids"])
    output = dict.fromkeys(parameter_ids, 0.0)
    nonzero = evaluated_nonzero_coefficients(scales)
    missing = sorted(set(nonzero).difference(output))
    if missing:
        raise KeyError(f"candidate parameters are outside the exact-X contract: {missing}")
    output.update(nonzero)
    return output


def decomposition(scales: dict[str, float]) -> dict[str, Any]:
    h = float(scales["h"])
    r = float(scales["r"])
    x = float(scales["x"])
    conditional_lower_bound = (
        -1.0
        - h**4
        - r**4
        - x**4 / 32.0
        - float(SIGMA_SCALE) * (625.0 / 576.0) * r**4
    )
    return {
        "Phi210": {
            "identity": "V_Phi=-2 I2+Q; Q=J0+I45+I210+I5940>=I2^2",
            "exact_J_coefficients": PHI_J_COEFFICIENTS,
            "global_lower_bound": "V_Phi>=-1",
            "source_exact_certificate": "exact_210_pati_salam_global_vacuum_v20.py",
        },
        "Sigma126bar": {
            "overall_scale": str(SIGMA_SCALE),
            "self_projector_weights_54_1050bar_2772bar_4125": [
                "2",
                "2",
                "17/16",
                "1",
            ],
            "self_projector_completeness": (
                "I54+I1050bar+I2772bar+I4125=N_Sigma^2"
            ),
            "C_square_recoupling_1_45_210_770_5940_8910": C_SQUARED_RECOUPLING,
            "A_square_recoupling_1_45_210_770_5940_8910": A_SQUARED_RECOUPLING,
            "A_shift_square": (
                "||(A_Phi-2)Sigma||^2="
                "||A_Phi Sigma||^2-4 O14+4 N_Sigma"
            ),
            "radial_mass_term": "-(25/12) r^2 N_Sigma",
            "selected_Delta_projector_fractions": {
                "54": "0",
                "1050bar": "0",
                "2772bar": "2/3",
                "4125": "1/3",
            },
            "selected_radial_stationarity_identity": (
                "2*(17/16)*(2/3)+2*1*(1/3)-25/12=0"
            ),
            "full_252_coordinate_stationarity_certificate": (
                "exact_gauged_u1x_g3_sos_bfb_stationarity_v20.py"
            ),
            "conditional_lower_bound": "V_Sigma>=-(625/576) r^4 before the 1/8 scale",
            "exact_symbolic_A_square_recoupling_certificate_available": True,
            "exact_A_square_recoupling_certificate": (
                "exact_gauged_u1x_g3_a_square_recoupling_v20.py"
            ),
        },
        "H10_S_Phi17": {
            "sum_of_nonnegative_terms": [
                "(Hdag H-h^2)^2",
                "(Hdag H)^2-|H.H|^2",
                "|H.H-(h^2/r)S*|^2",
                "(|S|^2-r^2)^2",
                "(1/32)(|Phi17|^2-x^2)^2",
                "Hdag (||Phi||^2 I-C(Phi)) H",
            ],
            "colour_projector_identity_at_P": (
                "||P||^2 I-C(P)=diag(1_6,0_4)"
            ),
            "Phi17_phase_note": (
                "its phase is the U(1)_X-minus-PQ symmetry direction, not an extra physical mode"
            ),
        },
        "conditional_global_lower_bound": conditional_lower_bound,
        "proof_scope": (
            "The complete 27-nonzero/51-parameter polynomial identity, global "
            "lower bound, and selected-vacuum gradient are exactly source-bound. "
            "Global uniqueness and direct exact physical-Hessian positivity are "
            "separate open claims."
        ),
    }


def _compiler_rows() -> tuple[
    potential.FieldState, tuple[derivatives.ParameterDerivative, ...]
]:
    selection = g2_audit.contract_selection()
    selected_ids = set(selection["direction_ids"])
    needed_ids = {
        parameter_id.split("::", 1)[1]
        for parameter_id in symbolic_nonzero_coefficients()
    }
    state = g2_audit.physical_hierarchy_state()
    all_directions = potential.evaluate_directions(state)
    by_id = {row.direction_id: row for row in all_directions}
    missing = sorted(needed_ids.difference(by_id))
    if missing:
        raise KeyError(f"candidate directions are missing from the compiler: {missing}")
    owners = g2_audit._adapter_modules_by_family()
    q = chart.pack(state)
    direction_rows = tuple(
        owners[by_id[direction_id].base_family].direction_derivative(
            q, by_id[direction_id]
        )
        for direction_id in sorted(needed_ids)
        if direction_id in selected_ids
    )
    return state, derivatives.parameter_derivatives(direction_rows)


def _orthonormal_quotient(state: potential.FieldState) -> dict[str, Any]:
    certificate = quotient_source.exact_quotient_certificate()
    if not certificate["certified"]:
        raise RuntimeError("the exact symmetry quotient is not certified")
    integer = np.asarray(
        quotient_source.exact_integer_tangent_matrix(), dtype=float
    )
    scales = np.empty(chart.TOTAL_DIM, dtype=float)
    h = float(np.real(state.h[6]))
    r = float(np.real(state.s))
    x = float(np.real(state.x))
    scales[chart.PHI_SLICE] = 1.0
    scales[chart.H_SLICE] = chart.SQRT2 * h
    scales[chart.SIGMA_SLICE] = r / 2.0
    scales[chart.S_SLICE] = chart.SQRT2 * r
    scales[chart.X_SLICE] = chart.SQRT2 * x
    columns = tuple(
        int(value)
        for value in certificate["full_removed_symmetry"]["minor"][
            "column_indices"
        ]
    )
    live = scales[:, None] * integer[:, columns]
    norms = np.linalg.norm(live, axis=0)
    complete, _ = np.linalg.qr(live / norms[None, :], mode="complete")
    return {
        "symmetry": complete[:, :EXPECTED_REMOVED_SYMMETRY_RANK],
        "quotient": complete[:, EXPECTED_REMOVED_SYMMETRY_RANK:],
        "exact_certificate": certificate,
    }


def run_heavy_recomputation() -> dict[str, Any]:
    state, parameter_rows = _compiler_rows()
    scales = hierarchy_scales()
    coefficients = full_coefficient_vector(scales)
    by_id = {row.parameter_id: row for row in parameter_rows}
    missing = sorted(
        parameter_id
        for parameter_id, coefficient in coefficients.items()
        if coefficient != 0.0 and parameter_id not in by_id
    )
    if missing:
        raise KeyError(f"nonzero candidate rows are missing: {missing}")

    gradient = np.zeros(chart.TOTAL_DIM, dtype=float)
    hessian = np.zeros((chart.TOTAL_DIM, chart.TOTAL_DIM), dtype=float)
    value = 0.0
    for parameter_id, coefficient in coefficients.items():
        if coefficient == 0.0:
            continue
        row = by_id[parameter_id]
        value += coefficient * float(np.real(row.value))
        gradient += coefficient * np.asarray(row.gradient).real
        hessian += coefficient * np.asarray(row.hessian).real
    hessian = 0.5 * (hessian + hessian.T)

    quotient_data = _orthonormal_quotient(state)
    symmetry = np.asarray(quotient_data["symmetry"], dtype=float)
    quotient = np.asarray(quotient_data["quotient"], dtype=float)
    projected = quotient.T @ hessian @ quotient
    projected = 0.5 * (projected + projected.T)
    eigenvalues = np.linalg.eigvalsh(projected)

    pd_indices = np.concatenate(
        (
            np.arange(chart.PHI_SLICE.start, chart.PHI_SLICE.stop),
            np.arange(chart.SIGMA_SLICE.start, chart.SIGMA_SLICE.stop),
        )
    )
    pd_hessian = hessian[np.ix_(pd_indices, pd_indices)]
    pd_orbit = chart.gauge_orbit_matrix(state)[pd_indices]
    u, singular_values, _ = np.linalg.svd(pd_orbit, full_matrices=True)
    pd_rank = int(
        np.sum(singular_values > 1.0e-10 * singular_values[0])
    )
    pd_quotient = u[:, pd_rank:]
    pd_matrix = pd_quotient.T @ pd_hessian @ pd_quotient
    pd_eigenvalues = np.linalg.eigvalsh(0.5 * (pd_matrix + pd_matrix.T))

    selected_values = {
        parameter_id: float(np.real(row.value))
        for parameter_id, row in by_id.items()
    }
    a_squared_value = sum(
        coefficient
        * selected_values[
            f"lambda::O44_B0{index + 1}_Phi2_Sigma_projectors"
        ]
        for index, coefficient in enumerate(A_SQUARED_RECOUPLING)
    )
    c_squared_value = sum(
        selected_values[
            f"lambda::O44_B0{index + 1}_Phi2_Sigma_projectors"
        ]
        for index in range(6)
    )
    a_shift_value = (
        a_squared_value
        - 4.0
        * selected_values["lambda::O14_B01_Phi_Sigma_Sigmadag_cubic"]
        + 4.0 * selected_values["lambda::O05_B01_126bar_norm"]
    )
    return {
        "evidence_kind": "live_compiler_float64_candidate_recomputation",
        "recomputed_in_this_invocation": True,
        "proof_grade": False,
        "dense_Hessians_assembled": True,
        "parameter_rows_assembled": len(parameter_rows),
        "nonzero_parameter_count": sum(value != 0.0 for value in coefficients.values()),
        "potential_value": value,
        "compiler_gradient_max_abs_residual": float(
            np.max(np.abs(gradient), initial=0.0)
        ),
        "compiler_gradient_norm": float(np.linalg.norm(gradient)),
        "stationary_Hessian_symmetry_max_abs_residual": float(
            np.max(np.abs(hessian @ symmetry), initial=0.0)
        ),
        "P_plus_Delta": {
            "gauge_rank": pd_rank,
            "quotient_dimension": int(pd_quotient.shape[1]),
            "minimum_eigenvalue": float(pd_eigenvalues[0]),
            "negative_eigenvalues_below_minus_1e_minus_12": int(
                np.sum(pd_eigenvalues < -1.0e-12)
            ),
            "zero_eigenvalues_at_1e_minus_12": int(
                np.sum(np.abs(pd_eigenvalues) <= 1.0e-12)
            ),
        },
        "full_massive_transverse": {
            "dimension": int(projected.shape[0]),
            "minimum_raw_eigenvalue": float(eigenvalues[0]),
            "maximum_raw_eigenvalue": float(eigenvalues[-1]),
            "negative_eigenvalues_below_zero": int(np.sum(eigenvalues < 0.0)),
            "negative_eigenvalues_below_minus_1e_minus_12": int(
                np.sum(eigenvalues < -1.0e-12)
            ),
            "strict_local_minimum_certified": False,
            "PSD_feasibility_certified": False,
        },
        "candidate_square_values_at_selected_vacuum": {
            "C_square": c_squared_value,
            "A_squared": a_squared_value,
            "A_shift_square": a_shift_value,
        },
        "limitations": [
            "float64 cannot resolve the electroweak hierarchy across the raw 448-space spectrum",
            "this numerical diagnostic is secondary to the separate direct exact rank certificate",
            "an independent exact lower-energy field witness rejects this candidate globally",
        ],
    }


def build_report(*, recompute_heavy: bool = False) -> dict[str, Any]:
    scales = hierarchy_scales()
    symbolic = symbolic_nonzero_coefficients()
    coefficients = full_coefficient_vector(scales)
    exact_quotient = quotient_source.exact_quotient_certificate()
    a_square = a_square_source.build_report()
    exact_sos = exact_sos_source.build_report()
    pd_rank = pd_rank_source.build_report()
    global_counterexample = global_counterexample_source.build_report()
    pd_ranks = pd_rank["direct_exact_ranks"]
    extension = pd_rank["exact_full_kernel_argument"]
    max_coupling = max(abs(value) for value in coefficients.values())
    nonzero_count = sum(value != 0.0 for value in coefficients.values())
    checks = {
        "exact_X_parameter_vector_has_length_51": len(coefficients)
        == EXPECTED_PARAMETER_COUNT,
        "candidate_has_27_nonzero_real_parameters": nonzero_count == 27,
        "every_symbolic_nonzero_parameter_is_in_exact_X_contract": set(symbolic)
        <= set(coefficients),
        "candidate_is_strictly_inside_4pi_box": max_coupling < 4.0 * math.pi,
        "candidate_J0_is_negative_21_over_200": PHI_J_COEFFICIENTS[
            "lambda::O48_B01_Phi_self_quartics"
        ]
        == Fraction(-21, 200),
        "historical_positive_J0_anchor_excludes_candidate": coefficients[
            "lambda::O48_B01_Phi_self_quartics"
        ]
        != 1.0,
        "exact_A_square_recoupling_is_source_bound": (
            a_square["n_failed"] == 0
            and a_square["flags"]["A_square_recoupling_exactly_source_bound"]
            and tuple(
                int(value)
                for value in a_square["certificate"]["unique_weights"]
            )
            == A_SQUARED_RECOUPLING
        ),
        "complete_SOS_BFB_stationarity_certificate_passes": (
            exact_sos["n_failed"] == 0
            and exact_sos["flags"][
                "complete_27_parameter_SOS_identity_exactly_source_bound"
            ]
            and exact_sos["flags"]["complete_potential_BFB_exactly_certified"]
            and exact_sos["flags"][
                "selected_vacuum_stationarity_exactly_certified"
            ]
        ),
        "exact_symmetry_rank_is_38": exact_quotient["full_removed_symmetry"][
            "rank"
        ]
        == EXPECTED_REMOVED_SYMMETRY_RANK,
        "exact_massive_transverse_dimension_is_448": exact_quotient[
            "physical_quotient_dimension"
        ]
        == EXPECTED_PHYSICAL_DIMENSION,
        "direct_exact_PD_rank_certificate_is_internally_consistent": pd_rank[
            "n_failed"
        ]
        == 0,
        "direct_exact_PD_Qsqrt2_LDL_has_rank_429_nullity_33": (
            pd_ranks["H_Phi_plus_K"]
            == {"rank": 429, "nullity": 33, "PSD": True}
        ),
        "direct_exact_full_kernel_count_has_rank_448": (
            extension["exact_full_Hessian_rank"]
            == EXPECTED_PHYSICAL_DIMENSION
            and extension["remaining_kernel_dimension"]
            == EXPECTED_REMOVED_SYMMETRY_RANK
        ),
        "direct_exact_Hessian_source_binding_passes": (
            pd_rank["flags"]["direct_exact_source_binding"]
            and pd_rank["flags"]["proof_grade_P_plus_Delta_PSD"]
            and pd_rank["flags"]["proof_grade_full_rank_448"]
            and pd_rank["flags"][
                "strict_transverse_Hessian_positive_certified"
            ]
        ),
        "exact_global_counterexample_rejects_selected_vacuum": (
            global_counterexample["n_failed"] == 0
            and global_counterexample["flags"][
                "selected_vacuum_global_minimum_disproved"
            ]
            and global_counterexample["flags"][
                "lower_energy_field_witness_exactly_certified"
            ]
        ),
        "G3_remains_fail_closed_after_candidate_rejection": True,
    }
    failures = [name for name, passed in checks.items() if not passed]
    heavy = (
        run_heavy_recomputation()
        if recompute_heavy
        else dict(RECORDED_NUMERICAL_EVIDENCE)
    )
    return {
        "status": (
            "EXACT_BFB_STATIONARY_STRICT_LOCAL_MINIMUM__GLOBAL_COUNTEREXAMPLE"
            if not failures
            else "G3_SOS_CANDIDATE_INTEGRITY_FAILED"
        ),
        "overall_state": "OPEN" if not failures else "EXECUTION_FAIL",
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_checks": len(checks),
        "n_failed": len(failures),
        "failures": failures,
        "checks": checks,
        "hierarchy_scales": scales,
        "coefficient_vector": {
            "basis": "authoritative exact-X 51-real-parameter order",
            "symbolic_nonzero": symbolic,
            "evaluated_all_51": coefficients,
            "nonzero_count": nonzero_count,
            "maximum_absolute_coefficient": max_coupling,
        },
        "boundedness_decomposition": decomposition(scales),
        "symmetry_quotient": {
            "SO10_broken_rank": exact_quotient["SO10"]["rank"],
            "SO10_plus_U1X_rank": exact_quotient["gauged_symmetry"]["rank"],
            "SO10_plus_U1X_plus_global_PQ_rank": exact_quotient[
                "full_removed_symmetry"
            ]["rank"],
            "massive_transverse_dimension": exact_quotient[
                "physical_quotient_dimension"
            ],
            "removed_tangents": [
                "36 broken SO(10) orbit directions",
                "1 gauged U(1)_X direction",
                "1 independent global-PQ direction",
            ],
        },
        "exact_rank_certificate": pd_rank,
        # Compatibility alias for consumers of the exploratory artifact.
        "conditional_exact_rank_certificate": pd_rank,
        "exact_A_square_recoupling_certificate": a_square,
        "exact_SOS_BFB_stationarity_certificate": exact_sos,
        "exact_global_counterexample_certificate": global_counterexample,
        "numerical_diagnostic": heavy,
        "flags": {
            "exact_sparse_51_parameter_candidate_constructed": not failures,
            "candidate_inside_4pi_box": max_coupling < 4.0 * math.pi,
            "positive_J0_normalization_is_without_loss_of_generality": False,
            "manifest_BFB_decomposition_candidate_constructed": not failures,
            "A_square_recoupling_exactly_source_bound": bool(
                not a_square["failures"]
                and a_square["flags"]["A_square_recoupling_exactly_source_bound"]
            ),
            "complete_potential_BFB_exactly_certified": bool(
                not exact_sos["failures"]
                and exact_sos["flags"][
                    "complete_potential_BFB_exactly_certified"
                ]
            ),
            "selected_vacuum_stationarity_exactly_compiler_certified": bool(
                not exact_sos["failures"]
                and exact_sos["flags"][
                    "selected_vacuum_stationarity_exactly_certified"
                ]
            ),
            "selected_vacuum_global_minimum_certified": False,
            "selected_vacuum_global_minimum_disproved": bool(
                not global_counterexample["failures"]
                and global_counterexample["flags"][
                    "selected_vacuum_global_minimum_disproved"
                ]
            ),
            "selected_vacuum_unique_modulo_symmetry": False,
            "exact_lower_energy_field_witness_certified": bool(
                not global_counterexample["failures"]
                and global_counterexample["flags"][
                    "lower_energy_field_witness_exactly_certified"
                ]
            ),
            "constructive_candidate_rejected_for_G3": bool(
                not global_counterexample["failures"]
                and global_counterexample["flags"][
                    "selected_vacuum_global_minimum_disproved"
                ]
            ),
            "selected_vacuum_stationarity_numerically_recomputed": bool(
                recompute_heavy
                and heavy["compiler_gradient_max_abs_residual"] < 1.0e-12
            ),
            "P_plus_Delta_local_positivity_numerical_only": False,
            # Compatibility fields retained with their old semantics.
            "P_plus_Delta_Qsqrt2_component_LDL_conditional": False,
            "full_448_kernel_count_conditional": False,
            "P_plus_Delta_source_binding_exactly_certified": bool(
                not pd_rank["failures"]
                and pd_rank["flags"]["direct_exact_source_binding"]
            ),
            "full_448_kernel_count_exact": bool(
                not pd_rank["failures"]
                and extension["exact_full_Hessian_rank"] == 448
                and extension["remaining_kernel_dimension"] == 38
            ),
            "full_448_PSD_feasibility_certified": bool(
                not exact_sos["failures"]
                and not pd_rank["failures"]
                and exact_sos["flags"][
                    "selected_vacuum_stationarity_exactly_certified"
                ]
                and pd_rank["flags"][
                    "strict_transverse_Hessian_positive_certified"
                ]
            ),
            "strict_local_minimum_certified": bool(
                not exact_sos["failures"]
                and not pd_rank["failures"]
                and exact_sos["flags"][
                    "selected_vacuum_stationarity_exactly_certified"
                ]
                and pd_rank["flags"][
                    "strict_transverse_Hessian_positive_certified"
                ]
            ),
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
        "verdict": (
            "A perturbative sparse candidate with a manifest sum-of-squares "
            "structure has been found outside the old J0=+1 search slice. Its "
            "complete potential is exactly bounded below and the selected "
            "vacuum is exactly stationary. Direct Gaussian-integer/Fraction "
            "assembly and exact Q(sqrt(2)) LDL certify a rank-429/nullity-33 "
            "P+Delta core; the exact H/S/Phi17 constraint Jacobian leaves only "
            "the 38 symmetry tangents, so all 448 transverse Hessian directions "
            "are positive and the selected orbit is a strict local minimum. "
            "The final exact global-gap test constructs a symmetry-inequivalent "
            "126bar field configuration with energy lower by "
            "25*r^4/19008. The selected orbit is therefore not global, this "
            "candidate is rejected for G3, and the broader model is not thereby "
            "excluded."
        ),
    }


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(_jsonable(report), indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(
        "# Gauged U(1)_X G3 constructive SOS candidate\n\n"
        f"**Status:** `{report['status']}`\n\n"
        + report["verdict"]
        + "\n\n"
        f"- nonzero parameters: `{report['coefficient_vector']['nonzero_count']}` of `51`;\n"
        f"- maximum absolute coefficient: `{report['coefficient_vector']['maximum_absolute_coefficient']}`;\n"
        "- exact 210 `J0`: `-21/200`;\n"
        "- removed symmetry rank: `38`;\n"
        "- massive/transverse dimension: `448`;\n"
        f"- complete-potential BFB certified: `{report['flags']['complete_potential_BFB_exactly_certified']}`;\n"
        f"- exact selected stationarity: `{report['flags']['selected_vacuum_stationarity_exactly_compiler_certified']}`;\n"
        f"- strict local minimum certified: `{report['flags']['strict_local_minimum_certified']}`;\n"
        "- selected global minimum disproved: "
        f"`{report['flags']['selected_vacuum_global_minimum_disproved']}`;\n"
        "- exact lower-energy field witness: "
        f"`{report['flags']['exact_lower_energy_field_witness_certified']}`;\n"
        "- G3 closed: `False`.\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--recompute-heavy", action="store_true")
    args = parser.parse_args(argv)
    report = build_report(recompute_heavy=args.recompute_heavy)
    if args.write:
        write_report(report)
    print(json.dumps(_jsonable(report), indent=2))
    return 0 if report["n_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
