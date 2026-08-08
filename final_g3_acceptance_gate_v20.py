#!/usr/bin/env python3
"""Fail-closed final acceptance test for the gauged-U(1)_X G3 vacuum gate.

The test deliberately separates a promising numerical local minimum from a
proof of G3.  PASS requires one source-bound statement on the full 486-real
field chart::

    V_beta(q) - V_beta(q0) >= 0  for every q,

with equality exactly on the SO(10) x U(1)_X x PQ orbit of q0, together with
an exact full Hessian rank/nullity 448/38 certificate.  Repository model
execution and G1/G2 promotion are independent release prerequisites.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import g1_g8_gate_ledger_v20 as ledger

ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.json"
OUT_MD = ROOT / "FINAL_G3_ACCEPTANCE_GATE_V20.md"

HSX_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json"
EQUALITY_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json"
LOCAL_COMPONENT_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json"
)
SU3_SLICE_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json"
GAP_JSON = ROOT / "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json"
EXACT_HESSIAN_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
)
ALTERNATIVE_SOS_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json"
)
FIXED_F_OFFKERNEL_JSON = (
    ROOT / "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json"
)
MAX_NEGATIVE_ZERO_RESIDUAL_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json"
)
MAX_NEGATIVE_FULL_RESIDUAL_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json"
)
MAX_NEGATIVE_RANK1_SU3_SLICE_JSON = (
    ROOT
    / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json"
)

MODEL_CONTRACT_ID = ledger.AUTHORITATIVE_CONTRACT_ID
FINAL_THEOREM = (
    "For every 486-real field q, V_beta(q)-V_beta(q0)>=0; equality holds "
    "exactly on the SO(10)xU(1)_XxPQ orbit of q0."
)


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _dig(value: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def build_report(
    *,
    ledger_report: dict[str, Any] | None = None,
    hsx_report: dict[str, Any] | None = None,
    equality_report: dict[str, Any] | None = None,
    local_component_report: dict[str, Any] | None = None,
    su3_slice_report: dict[str, Any] | None = None,
    gap_report: dict[str, Any] | None = None,
    exact_hessian_report: dict[str, Any] | None = None,
    alternative_sos_report: dict[str, Any] | None = None,
    fixed_f_offkernel_report: dict[str, Any] | None = None,
    max_negative_zero_residual_report: dict[str, Any] | None = None,
    max_negative_full_residual_report: dict[str, Any] | None = None,
    max_negative_rank1_su3_slice_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ledger_report = ledger.build_report() if ledger_report is None else ledger_report
    hsx_report = _load(HSX_JSON) if hsx_report is None else hsx_report
    equality_report = (
        _load(EQUALITY_JSON) if equality_report is None else equality_report
    )
    local_component_report = (
        _load(LOCAL_COMPONENT_JSON)
        if local_component_report is None
        else local_component_report
    )
    su3_slice_report = (
        _load(SU3_SLICE_JSON) if su3_slice_report is None else su3_slice_report
    )
    gap_report = _load(GAP_JSON) if gap_report is None else gap_report
    exact_hessian_report = (
        _load(EXACT_HESSIAN_JSON)
        if exact_hessian_report is None
        else exact_hessian_report
    )
    alternative_sos_report = (
        _load(ALTERNATIVE_SOS_JSON)
        if alternative_sos_report is None
        else alternative_sos_report
    )
    fixed_f_offkernel_report = (
        _load(FIXED_F_OFFKERNEL_JSON)
        if fixed_f_offkernel_report is None
        else fixed_f_offkernel_report
    )
    max_negative_zero_residual_report = (
        _load(MAX_NEGATIVE_ZERO_RESIDUAL_JSON)
        if max_negative_zero_residual_report is None
        else max_negative_zero_residual_report
    )
    max_negative_full_residual_report = (
        _load(MAX_NEGATIVE_FULL_RESIDUAL_JSON)
        if max_negative_full_residual_report is None
        else max_negative_full_residual_report
    )
    max_negative_rank1_su3_slice_report = (
        _load(MAX_NEGATIVE_RANK1_SU3_SLICE_JSON)
        if max_negative_rank1_su3_slice_report is None
        else max_negative_rank1_su3_slice_report
    )

    frontier = ledger_report.get("gauged_u1x_g3_constructive_frontier", {})
    gates = ledger_report.get("gates", {})
    hsx_flags = hsx_report.get("flag", {})
    hsx_orbit = _dig(hsx_report, "chiral_H_candidate", "exact_orbit", default={})
    hsx_bfb = hsx_report.get("BFB_certificate", {})
    hsx_hessian = hsx_report.get("live_full_gradient_and_quotient_Hessian", {})
    equality_scope = equality_report.get("scope", {})
    equality_lemma = equality_report.get("remaining_global_lemma", {})
    local_scope = local_component_report.get("scope", {})
    local_checks = local_component_report.get("checks", {})
    su3_scope = su3_slice_report.get("scope", {})
    su3_checks = su3_slice_report.get("checks", {})
    gap_flags = gap_report.get("flags", {})
    gap_acceptance = gap_report.get("final_acceptance_test", {})
    exact_hessian_flags = exact_hessian_report.get("flags", {})
    alternative_flags = alternative_sos_report.get("flags", {})
    fixed_f_scope = fixed_f_offkernel_report.get("scope", {})
    fixed_f_checks = fixed_f_offkernel_report.get("checks", {})
    max_negative_scope = max_negative_zero_residual_report.get("scope", {})
    max_negative_checks = max_negative_zero_residual_report.get("checks", {})
    max_negative_full_scope = max_negative_full_residual_report.get("scope", {})
    max_negative_full_checks = max_negative_full_residual_report.get("checks", {})
    rank1_su3_scope = max_negative_rank1_su3_slice_report.get("scope", {})
    rank1_su3_checks = max_negative_rank1_su3_slice_report.get("checks", {})

    artifact_integrity = {
        "ledger_executes": ledger_report.get("n_failed") == 0,
        "HSX_audit_executes": hsx_report.get("n_failed") == 0,
        "equality_audit_executes": equality_report.get("n_failed") == 0,
        "Phi_local_component_audit_executes": (
            local_component_report.get("n_failed") == 0
            and local_component_report.get("status")
            == "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN"
            and local_component_report.get("overall_state")
            == "LOCAL_COMPONENT_THEOREM_CLOSED"
            and all(
                local_checks.get(name) is True
                for name in (
                    "linearized_4125_rank_is_exactly_179",
                    "kernel_is_orbit_plus_radial_plus_C5",
                    "unit_normal_slice_has_only_C5_kernel",
                    "SU4_fixed_space_is_exactly_four_dimensional",
                    "phase_fixed_SU4_slice_is_exactly_classified",
                    "local_signed_orbit_components_closed",
                )
            )
        ),
        "Phi_SU3_fixed_slice_audit_executes": (
            su3_slice_report.get("n_failed") == 0
            and su3_slice_report.get("status")
            == "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN"
            and su3_slice_report.get("overall_state") == "SU3_FIXED_SLICE_CLOSED"
            and all(
                su3_checks.get(name) is True
                for name in (
                    "global_I45_hodge_square_identity_is_exact",
                    "global_I54_isotropic_contraction_identity_is_exact",
                    "displayed_space_is_complete_SU3_fixed_space",
                    "restricted_projector_rowspace_reduced_exactly",
                    "eight_nondiagonal_directions_have_real_SOS_obstruction",
                    "both_branch_parameterizations_satisfy_all_45_relations_mod_sphere",
                    "complete_SU3_fixed_slice_is_signed_Kahler_orbit",
                )
            )
        ),
        "global_gap_audit_executes": gap_report.get("n_failed") == 0,
        "fixed_F_full_offkernel_audit_executes": bool(
            fixed_f_offkernel_report.get("n_failed") == 0
            and fixed_f_offkernel_report.get("status")
            == "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED"
            and fixed_f_offkernel_report.get("overall_state")
            == "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
            and fixed_f_offkernel_report.get("model_contract_id")
            == MODEL_CONTRACT_ID
            and fixed_f_scope.get("Phi_fixed_to_F") is True
            and fixed_f_scope.get("H_arbitrary") is True
            and fixed_f_scope.get("Sigma_arbitrary") is True
            and fixed_f_scope.get(
                "global_gap_nonnegative_on_full_fixed_F_stratum"
            )
            is True
            and fixed_f_scope.get("equality_is_selected_SU5_flag_orbit")
            is True
            and fixed_f_scope.get("arbitrary_Phi_proved") is False
            and fixed_f_scope.get("G3_closed") is False
            and fixed_f_checks.get("cross_block_bound_exact") is True
            and fixed_f_checks.get("full_fixed_F_equality_orbit_exact") is True
        ),
        "max_negative_all_zero_residual_audit_executes_fail_closed": bool(
            max_negative_zero_residual_report.get("n_failed") == 0
            and max_negative_zero_residual_report.get("status")
            == "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED"
            and max_negative_zero_residual_report.get("overall_state")
            == "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
            and max_negative_zero_residual_report.get("model_contract_id")
            == MODEL_CONTRACT_ID
            and max_negative_scope.get(
                "strongest_all_zero_max_negative_route_excluded"
            )
            is True
            and max_negative_scope.get(
                "strongest_pure_Delta_mixed_zero_max_negative_route_excluded"
            )
            is True
            and max_negative_scope.get(
                "normalized_affine_stratum_requires_u_gt_0_v_gt_0"
            )
            is True
            and max_negative_scope.get(
                "u_zero_and_v_zero_boundaries_closed_separately"
            )
            is True
            and max_negative_scope.get("nonzero_residual_cancellations_excluded")
            is False
            and max_negative_scope.get("arbitrary_Phi_global_gap_proved") is False
            and max_negative_scope.get("G3_closed") is False
            and max_negative_checks.get("exact_rank_168_nullity_42") is True
            and max_negative_checks.get("kernel_splits_35_plus_7_exactly") is True
            and max_negative_checks.get(
                "live_HSX_and_PD_coefficients_bound_exactly"
            )
            is True
            and max_negative_checks.get(
                "N_and_C00_C11_contraction_identities_computed_exactly"
            )
            is True
            and max_negative_checks.get(
                "Phi_radial_plus_I54_lower_bound_1_over_141"
            )
            is True
            and max_negative_checks.get("worst_radial_current_minimum_exact")
            is True
            and max_negative_checks.get("strict_positive_stratum_margin_exact")
            is True
            and max_negative_checks.get(
                "u_zero_and_v_zero_radial_boundaries_closed_exactly"
            )
            is True
            and _dig(
                max_negative_zero_residual_report,
                "exact_stratum_gap",
                "strict_margin",
            )
            == "7859/140295000"
        ),
        "max_negative_full_residual_pure_Delta_audit_executes_fail_closed": bool(
            max_negative_full_residual_report.get("n_failed") == 0
            and max_negative_full_residual_report.get("status")
            == "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED"
            and max_negative_full_residual_report.get("overall_state")
            == "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
            and max_negative_full_residual_report.get("model_contract_id")
            == MODEL_CONTRACT_ID
            and max_negative_full_scope.get("Sigma_on_pure_Delta_orbit") is True
            and max_negative_full_scope.get(
                "H_current_saturates_I45_equals_minus_NH_NSigma"
            )
            is True
            and max_negative_full_scope.get("Phi_arbitrary_real_210") is True
            and max_negative_full_scope.get(
                "nonzero_Phi_Sigma_residuals_covered"
            )
            is True
            and max_negative_full_scope.get(
                "nonzero_chiral_Phi_H_residual_covered"
            )
            is True
            and max_negative_full_scope.get("u_v_all_nonnegative") is True
            and max_negative_full_scope.get("restricted_gap_global_minimum")
            == "1/5000"
            and max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
            is False
            and max_negative_full_scope.get("G3_closed") is False
            and all(
                max_negative_full_checks.get(name) is True
                for name in (
                    "live_restricted_residual_normalizations_exact",
                    "single_4125_covariant_Cauchy_bound_exact",
                    "anchor_quadratic_has_exact_positive_spectral_floor",
                    "anchor_lower_bound_strictly_exceeds_1_over_50",
                    "piecewise_u_v_completion_covers_nonnegative_quadrant",
                    "exact_1_over_5000_saturation_exhibited",
                    "arbitrary_real_Phi_covered",
                    "mixed_and_chiral_residuals_not_assumed_zero",
                    "arbitrary_Sigma_orientation_not_overclaimed",
                    "G3_not_overclaimed",
                )
            )
        ),
        "max_negative_rank1_SU3_four_dimensional_slice_audit_executes_fail_closed": bool(
            max_negative_rank1_su3_slice_report.get("n_failed") == 0
            and max_negative_rank1_su3_slice_report.get("failed_checks") == []
            and max_negative_rank1_su3_slice_report.get("status")
            == "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED"
            and max_negative_rank1_su3_slice_report.get("overall_state")
            == "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN"
            and max_negative_rank1_su3_slice_report.get("model_contract_id")
            == MODEL_CONTRACT_ID
            and rank1_su3_scope.get("H_fixed_to_h_minus") is True
            and rank1_su3_scope.get(
                "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor"
            )
            is True
            and rank1_su3_scope.get(
                "Phi_restricted_to_four_real_SU3_fixed_variables"
            )
            is True
            and rank1_su3_scope.get("Phi_slice_real_dimension") == 4
            and rank1_su3_scope.get("full_SU3_fixed_space_real_dimension") == 16
            and rank1_su3_scope.get("full_SU3_fixed_space_proved") is False
            and rank1_su3_scope.get("u_v_arbitrary_nonnegative") is True
            and rank1_su3_scope.get("arbitrary_real_Phi") is False
            and rank1_su3_scope.get("arbitrary_max_negative_Sigma") is False
            and rank1_su3_scope.get("G3_closed") is False
            and rank1_su3_scope.get("whole_model_excluded") is False
            and all(
                rank1_su3_checks.get(name) is True
                for name in (
                    "rank1_live_residual_source_exact",
                    "explicit_endpoint_current_and_self_projectors_exactly",
                    "slice_basis_Gram_exact",
                    "rank1_common_affine_kernel_rank160_nullity50_exact",
                    "angular_projector_Gram_symmetric_exact",
                    "angular_projector_int64_overflow_preflight_exact",
                    "anchor_polynomial_reconstructed_exactly",
                    "rational_SOS_polynomial_identity_exact",
                    "rational_SOS_Gram_positive_definite_exact",
                    "anchor_at_least_3_over_200_exact",
                    "radial_patch_global_minimum_1_over_5000_exact",
                    "attaining_slice_witness_evaluated_from_live_arrays_exact",
                )
            )
            and rank1_su3_checks.get("arbitrary_rank1_Phi_proved") is False
            and rank1_su3_checks.get("arbitrary_Sigma35_proved") is False
            and rank1_su3_checks.get("G3_closed") is False
            and _dig(
                max_negative_rank1_su3_slice_report,
                "SOS",
                "strict_anchor_lower_bound",
            )
            == "3/200"
            and _dig(
                max_negative_rank1_su3_slice_report,
                "radial_patch",
                "restricted_global_minimum",
            )
            == "1/5000"
        ),
        "alternative_global_SOS_audit_executes_fail_closed": bool(
            alternative_sos_report.get("n_failed") == 0
            and alternative_sos_report.get("status")
            == "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT"
            and alternative_sos_report.get("overall_state")
            == "G3_GLOBAL_ALTERNATIVE_OPEN"
            and alternative_flags.get(
                "all_vanishing_45_current_Gram_completion_excluded"
            )
            is True
            and alternative_flags.get(
                "all_vanishing_affine_SOS_completion_excluded"
            )
            is True
            and alternative_flags.get(
                "all_vanishing_unique_chiral_quartic_completion_excluded"
            )
            is True
            and alternative_flags.get(
                "nonvanishing_residual_gradient_cancellation_excluded"
            )
            is False
            and alternative_flags.get("different_vacuum_orbit_excluded") is False
            and alternative_flags.get("globally_certifiable_alternative_found")
            is False
            and alternative_flags.get("G3_closed") is False
            and alternative_flags.get("whole_model_excluded") is False
        ),
        "all_current_artifacts_use_authoritative_contract": all(
            report.get("model_contract_id", MODEL_CONTRACT_ID) == MODEL_CONTRACT_ID
            for report in (
                hsx_report,
                gap_report,
                fixed_f_offkernel_report,
                max_negative_zero_residual_report,
                max_negative_full_residual_report,
                max_negative_rank1_su3_slice_report,
            )
        ),
        "numerical_Hessian_not_promoted_to_proof": (
            hsx_hessian.get("proof_grade") is False
        ),
        "upstream_G3_not_overclaimed": (
            hsx_flags.get("G3_closed") is False
            and equality_scope.get("G3_closed") is False
            and local_scope.get("G3_closed") is False
            and su3_scope.get("G3_closed") is False
            and gap_flags.get("G3_closed") is False
            and fixed_f_scope.get("G3_closed") is False
            and max_negative_scope.get("G3_closed") is False
            and max_negative_full_scope.get("G3_closed") is False
            and rank1_su3_scope.get("G3_closed") is False
        ),
    }

    science_criteria = {
        "G1_G2_exact_scoped_calculations_complete": bool(
            str(_dig(
                ledger_report,
                "gauged_u1x_scalar_subtheorems",
                "G1",
                "scoped_status",
                default="",
            )).startswith("COMPLETE")
            and str(_dig(
                ledger_report,
                "gauged_u1x_scalar_subtheorems",
                "G2",
                "scoped_status",
                default="",
            )).startswith("COMPLETE")
        ),
        "full_candidate_exactly_stationary": bool(
            hsx_flags.get("chiral_H_exact_stationary_candidate_constructed")
            and _dig(
                hsx_report,
                "chiral_H_candidate",
                "Phi_H_alignment",
                "source_binding_exact",
                default=False,
            )
        ),
        "full_homogeneous_quartic_BFB_exact": bool(
            hsx_bfb.get("homogeneous_quartic_BFB_certified")
            and hsx_bfb.get("source_binding_exact")
        ),
        "target_SM_and_full_symmetry_orbits_exact": bool(
            hsx_orbit.get("SO10_rank") == 36
            and hsx_orbit.get("SO10_plus_U1X_rank") == 37
            and hsx_orbit.get("SO10_plus_U1X_plus_PQ_rank") == 38
            and hsx_orbit.get("physical_quotient_dimension") == 448
            and hsx_orbit.get("source_binding_exact") is True
        ),
        "couplings_perturbative": bool(
            _dig(hsx_report, "coefficient_map", "nonzero_count") == 28
            and float(
                _dig(
                    hsx_report,
                    "coefficient_map",
                    "maximum_absolute_coefficient",
                    default=float("inf"),
                )
            )
            < float(_dig(hsx_report, "coefficient_map", "four_pi", default=0.0))
        ),
        "full_Hessian_rank_448_nullity_38_exact": bool(
            exact_hessian_report.get("n_failed") == 0
            and exact_hessian_report.get("status")
            == "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED"
            and exact_hessian_report.get("overall_state")
            == "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM"
            and exact_hessian_report.get("model_contract_id") == MODEL_CONTRACT_ID
            and exact_hessian_flags.get("source_binding_exact") is True
            and exact_hessian_flags.get("proof_grade") is True
            and exact_hessian_flags.get("exact_rank_448") is True
            and exact_hessian_flags.get("exact_nullity_38") is True
        ),
        "full_448_quotient_strictly_positive_exact": bool(
            exact_hessian_flags.get("exact_PSD") is True
            and exact_hessian_flags.get("strict_quotient_positive") is True
            and exact_hessian_flags.get("kernel_equals_38_symmetry_tangents")
            is True
        ),
        "full_fixed_F_offkernel_gap_and_equality_exact": bool(
            fixed_f_scope.get("global_gap_nonnegative_on_full_fixed_F_stratum")
            is True
            and fixed_f_scope.get("equality_is_selected_SU5_flag_orbit") is True
            and fixed_f_scope.get("arbitrary_Phi_proved") is False
            and fixed_f_checks.get("mixed_offkernel_gap_at_least_6_over_5_exact")
            is True
            and fixed_f_checks.get("pure_hplus_current_error_bound_exact") is True
            and fixed_f_checks.get("cross_block_bound_exact") is True
            and fixed_f_checks.get("rational_inside_outside_patch_positive")
            is True
            and fixed_f_checks.get("full_fixed_F_equality_orbit_exact") is True
        ),
        "max_negative_all_zero_residual_route_excluded_exactly": bool(
            max_negative_scope.get(
                "strongest_all_zero_max_negative_route_excluded"
            )
            is True
            and max_negative_scope.get(
                "strongest_pure_Delta_mixed_zero_max_negative_route_excluded"
            )
            is True
            and max_negative_scope.get("nonzero_residual_cancellations_excluded")
            is False
            and max_negative_scope.get("arbitrary_Phi_global_gap_proved") is False
            and max_negative_checks.get("exact_rank_168_nullity_42") is True
            and max_negative_checks.get("kernel_splits_35_plus_7_exactly") is True
            and max_negative_checks.get(
                "live_HSX_and_PD_coefficients_bound_exactly"
            )
            is True
            and max_negative_checks.get(
                "N_and_C00_C11_contraction_identities_computed_exactly"
            )
            is True
            and max_negative_checks.get("strict_positive_stratum_margin_exact")
            is True
            and max_negative_checks.get(
                "u_zero_and_v_zero_radial_boundaries_closed_exactly"
            )
            is True
        ),
        "max_negative_pure_Delta_full_residual_gap_excluded_exactly": bool(
            max_negative_full_scope.get("Sigma_on_pure_Delta_orbit") is True
            and max_negative_full_scope.get("Phi_arbitrary_real_210") is True
            and max_negative_full_scope.get(
                "nonzero_Phi_Sigma_residuals_covered"
            )
            is True
            and max_negative_full_scope.get(
                "nonzero_chiral_Phi_H_residual_covered"
            )
            is True
            and max_negative_full_scope.get("u_v_all_nonnegative") is True
            and max_negative_full_scope.get("restricted_gap_global_minimum")
            == "1/5000"
            and max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
            is False
            and max_negative_full_scope.get("G3_closed") is False
            and max_negative_full_checks.get(
                "anchor_lower_bound_strictly_exceeds_1_over_50"
            )
            is True
            and max_negative_full_checks.get(
                "piecewise_u_v_completion_covers_nonnegative_quadrant"
            )
            is True
            and max_negative_full_checks.get(
                "exact_1_over_5000_saturation_exhibited"
            )
            is True
        ),
        "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3": bool(
            rank1_su3_scope.get("H_fixed_to_h_minus") is True
            and rank1_su3_scope.get(
                "Phi_restricted_to_four_real_SU3_fixed_variables"
            )
            is True
            and rank1_su3_scope.get("Phi_slice_real_dimension") == 4
            and rank1_su3_scope.get("full_SU3_fixed_space_real_dimension") == 16
            and rank1_su3_scope.get("full_SU3_fixed_space_proved") is False
            and rank1_su3_scope.get("u_v_arbitrary_nonnegative") is True
            and rank1_su3_scope.get("arbitrary_real_Phi") is False
            and rank1_su3_scope.get("arbitrary_max_negative_Sigma") is False
            and rank1_su3_scope.get("G3_closed") is False
            and rank1_su3_checks.get("arbitrary_rank1_Phi_proved") is False
            and rank1_su3_checks.get("arbitrary_Sigma35_proved") is False
            and rank1_su3_checks.get("G3_closed") is False
            and rank1_su3_checks.get(
                "radial_patch_global_minimum_1_over_5000_exact"
            )
            is True
            and _dig(
                max_negative_rank1_su3_slice_report,
                "radial_patch",
                "restricted_global_minimum",
            )
            == "1/5000"
        ),
        "signed_Phi_orbits_locally_isolated_exactly": bool(
            local_scope.get("plus_F_local_component_classified") is True
            and local_scope.get("minus_F_local_component_classified") is True
            and local_scope.get("signed_orbit_locally_isolated") is True
            and local_scope.get("disconnected_distant_components_excluded")
            is False
            and local_scope.get("corrected_signed_global_orbit_theorem_proved")
            is False
        ),
        "complete_SU3_fixed_Phi_slice_classified_exactly": bool(
            su3_scope.get(
                "complete_16_real_dimensional_SU3_fixed_space_classified"
            )
            is True
            and su3_scope.get(
                "nondiagonal_Omega3_wedge_R4_directions_included"
            )
            is True
            and su3_scope.get(
                "all_nonzero_slice_solutions_are_signed_Kahler_squares"
            )
            is True
            and su3_scope.get("all_arbitrary_real_four_forms_classified")
            is False
            and su3_scope.get("corrected_signed_global_orbit_theorem_proved")
            is False
        ),
        "all_PD_equality_orbits_classified_exactly": bool(
            equality_scope.get("all_arbitrary_Phi_global_equalities_classified")
            is True
            and equality_scope.get("global_equality_orbit_classification_complete")
            is True
            and equality_lemma.get("proved") is True
            and equality_lemma.get("source_bound_certificate_available") is True
        ),
        "beta_global_gap_and_unique_equality_exact": bool(
            gap_flags.get("beta_1_over_20_global_minimum_certified") is True
            and gap_flags.get("global_equality_orbits_classified") is True
            and gap_acceptance.get("currently_passes") is True
            and gap_acceptance.get("required_statement") == FINAL_THEOREM
        ),
    }
    mathematical_g3_closed = bool(
        all(artifact_integrity.values()) and all(science_criteria.values())
    )

    release_criteria = {
        "authoritative_external_model_contract_executed": bool(
            ledger_report.get("contract_consistent")
        ),
        "G1_promoted_closed": _dig(gates, "G1", "status") == ledger.STATUS_CLOSED,
        "G2_promoted_closed": _dig(gates, "G2", "status") == ledger.STATUS_CLOSED,
    }
    release_g3_verified = bool(
        mathematical_g3_closed and all(release_criteria.values())
    )

    exact_lower_witness = gap_flags.get("lower_witness_found") is True
    whole_model_excluded = bool(
        hsx_flags.get("whole_model_excluded") is True
        or gap_flags.get("whole_model_excluded") is True
    )
    if not all(artifact_integrity.values()):
        overall_state = "EXECUTION_FAIL"
    elif whole_model_excluded:
        overall_state = "THEORY_FAIL"
    elif release_g3_verified:
        overall_state = "PASS"
    elif exact_lower_witness:
        overall_state = "CANDIDATE_FAIL"
    else:
        overall_state = "OPEN"

    blockers = [name for name, passed in science_criteria.items() if not passed]
    blockers.extend(name for name, passed in release_criteria.items() if not passed)
    missing_artifacts = [
        path.name
        for path, report in (
            (HSX_JSON, hsx_report),
            (EQUALITY_JSON, equality_report),
            (LOCAL_COMPONENT_JSON, local_component_report),
            (SU3_SLICE_JSON, su3_slice_report),
            (GAP_JSON, gap_report),
            (EXACT_HESSIAN_JSON, exact_hessian_report),
            (ALTERNATIVE_SOS_JSON, alternative_sos_report),
            (FIXED_F_OFFKERNEL_JSON, fixed_f_offkernel_report),
            (MAX_NEGATIVE_ZERO_RESIDUAL_JSON, max_negative_zero_residual_report),
            (MAX_NEGATIVE_FULL_RESIDUAL_JSON, max_negative_full_residual_report),
            (
                MAX_NEGATIVE_RANK1_SU3_SLICE_JSON,
                max_negative_rank1_su3_slice_report,
            ),
        )
        if not report
    ]

    return {
        "status": "FINAL_G3_ACCEPTANCE_TEST_EXECUTED",
        "overall_state": overall_state,
        "model_contract_id": MODEL_CONTRACT_ID,
        "n_integrity_checks": len(artifact_integrity),
        "n_failed": sum(not value for value in artifact_integrity.values()),
        "failures": [name for name, value in artifact_integrity.items() if not value],
        "missing_artifacts": missing_artifacts,
        "artifact_integrity": artifact_integrity,
        "decisive_theorem": FINAL_THEOREM,
        "science_criteria": science_criteria,
        "release_criteria": release_criteria,
        "blockers": blockers,
        "diagnostic_only": {
            "live_full_gradient_max_abs_residual": hsx_hessian.get(
                "full_gradient_max_abs_residual"
            ),
            "live_minimum_transverse_eigenvalue": hsx_hessian.get(
                "minimum_transverse_eigenvalue"
            ),
            "live_transverse_dimension": hsx_hessian.get("transverse_dimension"),
            "Phi_local_component_state": local_component_report.get(
                "overall_state"
            ),
            "distant_Phi_components_excluded": local_scope.get(
                "disconnected_distant_components_excluded"
            ),
            "complete_SU3_fixed_Phi_slice_classified": su3_scope.get(
                "complete_16_real_dimensional_SU3_fixed_space_classified"
            ),
            "SU3_slice_generic_components_excluded": su3_scope.get(
                "disconnected_distant_components_excluded"
            ),
            "fixed_F_full_offkernel_state": fixed_f_offkernel_report.get(
                "overall_state"
            ),
            "fixed_F_global_gap_closed": fixed_f_scope.get(
                "global_gap_nonnegative_on_full_fixed_F_stratum"
            ),
            "arbitrary_Phi_global_gap_closed": fixed_f_scope.get(
                "arbitrary_Phi_proved"
            ),
            "max_negative_all_zero_residual_route_excluded": (
                max_negative_scope.get(
                    "strongest_all_zero_max_negative_route_excluded"
                )
            ),
            "max_negative_all_zero_residual_strict_margin": _dig(
                max_negative_zero_residual_report,
                "exact_stratum_gap",
                "strict_margin",
            ),
            "arbitrary_Phi_nonzero_residual_cancellations_excluded": (
                max_negative_scope.get("nonzero_residual_cancellations_excluded")
            ),
            "max_negative_pure_Delta_full_residual_gap_closed": (
                max_negative_full_scope.get("Phi_arbitrary_real_210") is True
                and max_negative_full_scope.get(
                    "nonzero_Phi_Sigma_residuals_covered"
                )
                is True
                and max_negative_full_scope.get(
                    "nonzero_chiral_Phi_H_residual_covered"
                )
                is True
            ),
            "max_negative_pure_Delta_full_residual_minimum": (
                max_negative_full_scope.get("restricted_gap_global_minimum")
            ),
            "rank1_SU3_Phi_slice_real_dimension": rank1_su3_scope.get(
                "Phi_slice_real_dimension"
            ),
            "rank1_SU3_ambient_real_dimension": rank1_su3_scope.get(
                "full_SU3_fixed_space_real_dimension"
            ),
            "rank1_SU3_slice_minimum": _dig(
                max_negative_rank1_su3_slice_report,
                "radial_patch",
                "restricted_global_minimum",
            ),
            "arbitrary_rank1_Phi_open": not bool(
                rank1_su3_checks.get("arbitrary_rank1_Phi_proved")
            ),
            "arbitrary_non_pure_Delta_Sigma_orientations_open": not bool(
                max_negative_full_scope.get("arbitrary_Sigma_orientation_proved")
            ),
            "all_vanishing_global_SOS_replacements_excluded": bool(
                alternative_flags.get(
                    "all_vanishing_45_current_Gram_completion_excluded"
                )
                and alternative_flags.get(
                    "all_vanishing_affine_SOS_completion_excluded"
                )
                and alternative_flags.get(
                    "all_vanishing_unique_chiral_quartic_completion_excluded"
                )
            ),
            "nonvanishing_residual_global_SOS_replacements_excluded": (
                alternative_flags.get(
                    "nonvanishing_residual_gradient_cancellation_excluded"
                )
            ),
        },
        "classification": {
            "mathematical_G3_closed": mathematical_g3_closed,
            "release_G3_verified": release_g3_verified,
            "candidate_exactly_rejected": exact_lower_witness,
            "whole_model_excluded": whole_model_excluded,
            "theory_still_viable": not whole_model_excluded,
            "G3_closed": release_g3_verified,
        },
        "upstream_frontier_integrity": frontier.get("integrity_pass"),
        "remaining_open_problem": (
            "uniform coercivity for arbitrary non-pure-Delta Sigma orientations"
        ),
        "verdict": (
            "G3 is verified." if release_g3_verified else
            "G3 remains open. The chiral-H candidate now has an exact full "
            "Hessian theorem (rank/nullity 448/38, positive on the quotient) "
            "and an exact global gap/equality theorem on the complete Phi=F "
            "stratum for arbitrary H and Sigma. The complete maximally-negative "
            "pure-Delta sector is now also excluded for arbitrary real Phi and "
            "all nonzero residuals, with sharp gap 1/5000; no exact lower witness "
            "is known. At fixed H=h_- and one explicit rank-one Sigma endpoint, "
            "an exact certificate "
            "also proves the 1/5000 gap on only a four-real-dimensional Phi "
            "sub-slice of the 16-dimensional SU(3)-fixed space. PASS still "
            "requires a uniform coercive beta gap for "
            "arbitrary non-pure-Delta Sigma orientations, plus the external authoritative "
            "model execution."
        ),
    }


def write_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Final G3 acceptance gate — v20",
        "",
        f"**State:** `{report['overall_state']}`",
        "",
        report["verdict"],
        "",
        "## Decisive theorem",
        "",
        report["decisive_theorem"],
        "",
        "## Science criteria",
        "",
    ]
    lines.extend(
        f"- `{name}`: `{value}`"
        for name, value in report["science_criteria"].items()
    )
    lines.extend(["", "## Release criteria", ""])
    lines.extend(
        f"- `{name}`: `{value}`"
        for name, value in report["release_criteria"].items()
    )
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- `{item}`" for item in report["blockers"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    report = build_report()
    if args.write:
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        OUT_MD.write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["overall_state"] == "EXECUTION_FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
