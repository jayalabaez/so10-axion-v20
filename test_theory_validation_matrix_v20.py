#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import theory_validation_matrix_v20 as matrix


def test_overall_state_never_promotes_open_or_conditional_gates_to_pass():
    assert matrix._overall_state(True, [{"state": "PASS"}]) == "PASS"
    assert matrix._overall_state(True, [{"state": "CONDITIONAL"}]) == "CONDITIONAL"
    assert matrix._overall_state(True, [{"state": "OPEN"}]) == "OPEN"
    assert matrix._overall_state(True, [{"state": "BLOCKED"}]) == "BLOCKED"
    assert matrix._overall_state(False, [{"state": "PASS"}]) == "FAIL"


def write_json(root: Path, name: str, value: dict) -> None:
    root.joinpath(name).write_text(json.dumps(value), encoding="utf-8")


def minimal_tree(
    root: Path,
    *,
    engine_pass: bool = True,
    unit_pass: bool = True,
    sphere_probability: bool = False,
    vacuum_minimized: bool = False,
    exact_stationarity_rank: bool = True,
    full_rg: bool = False,
    contract_consistent: bool = True,
) -> None:
    write_json(
        root,
        "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json",
        {
            "n_failed": 0,
            "contract_consistent": contract_consistent,
            "contract_conflicts": []
            if contract_consistent
            else ["executable_scaffold_omits_manuscript_U1X_gauge_factor"],
            "scientific_blockers": []
            if contract_consistent
            else ["AUTHORITATIVE_GAUGED_U1X_CONTRACT_MISMATCH"],
            "executable_scaffold_contract": {
                "model_syntax_class": (
                    "sarah_native"
                    if contract_consistent
                    else "legacy_pseudo_sarah_metadata"
                ),
                "tool_native_sarah_syntax": contract_consistent,
                "statically_executable_model_contract": contract_consistent,
                "lagrangian": {
                    "registered_in_GaugeES_LagrangianInput": contract_consistent
                },
            },
            "external_model_validation": {
                "schema": matrix.exact_x_gate.EXTERNAL_VALIDATION_SCHEMA
                if contract_consistent
                else None,
                "valid": contract_consistent,
                "checks": {
                    name: contract_consistent
                    for name in (
                        "tool_native_model_format_matches_path",
                        "external_process_command_matches_tool",
                        "input_manifest_schema_is_supported",
                        "input_manifest_sha256_matches_entries",
                        "primary_model_is_bound_in_input_manifest",
                        "validation_driver_is_bound_to_command",
                        "captured_process_log_is_hash_bound",
                        "captured_process_log_has_all_required_pass_markers",
                    )
                },
            },
        },
    )
    write_json(
        root,
        "GAUGED_U1X_SCALAR_CONTRACT_V20.json",
        {
            "n_failed": 0,
            "implementation_matches_manuscript": contract_consistent,
        },
    )
    write_json(
        root,
        "G1_G8_GATE_LEDGER_V20.json",
        {
            "gates": {
                "G1": {"status": "CLOSED" if contract_consistent else "BLOCKED"},
                "G2": {"status": "CLOSED" if contract_consistent else "BLOCKED"},
            }
        },
    )
    write_json(
        root,
        "GAUGED_U1X_G2_DERIVATIVE_AUDIT_V20.json",
        {
            "model_contract_id": "gauged_u1x_phi17_v20",
            "n_failed": 0,
            "counts": {
                "invariant_directions": 44,
                "real_parameters": 51,
                "real_field_dimension": 486,
            },
            "stationary_Hessian_bridge": {
                "promoted_stationarity_matrix": {"rank": 13, "nullity": 38}
            },
            "flags": {
                "G2_gauged_u1x_derivatives_certified": True,
                "exact_Delta_R_projector_zero_certificate": True,
                "exact_projector_zero_corrected_normalized_SVD_rank_13": True,
                "stationarity_rank_13_exactly_certified": exact_stationarity_rank,
                "stationarity_nullity_38_exactly_certified": (
                    exact_stationarity_rank
                ),
                "stationarity_rank_upper_bound_13_exactly_certified": (
                    exact_stationarity_rank
                ),
            },
        },
    )
    for name in (
        "G3_FULL_STATIONARITY_FEASIBILITY_V20.json",
        "G3_FULL_HESSIAN_CLASSIFICATION_V20.json",
        "G3_STATIONARY_STABILITY_SEARCH_V20.json",
    ):
        write_json(
            root,
            name,
            {
                "model_contract_id": "historical_option_c_no_x_v20",
                "authoritative_for_manuscript": False,
                "model_wide_no_go_certified": False,
            },
        )
    write_json(
        root,
        "GAUGED_U1X_G3_STABILITY_V20.json",
        {
            "model_contract_id": "gauged_u1x_phi17_v20",
            "authoritative_for_manuscript_G3_formulation": True,
            "n_failed": 0,
            "coverage": {
                "invariant_directions": 44,
                "real_parameters": 51,
                "real_field_dimension": 486,
                "gauge_quotient_dimension_including_axion": 449,
                "massive_transverse_quotient_dimension": 448,
                "physical_quotient_dimension": 448,
            },
            "flags": {
                "gauge_quotient_dimension_449_including_axion_certified": True,
                "massive_transverse_quotient_dimension_448_certified": True,
                "physical_quotient_dimension_448_certified": True,
                "exact_projector_zero_corrected_normalized_SVD_rank_13": True,
                "stationarity_rank_13_exactly_certified": exact_stationarity_rank,
                "stationarity_nullity_38_exactly_certified": (
                    exact_stationarity_rank
                ),
                "constructive_candidate_exact_rank448_certificate": True,
                "constructive_candidate_direct_exact_source_binding": True,
                "G3_fixed_vacuum_strict_minimum_certified": True,
                "G3_fixed_vacuum_PSD_feasible_certified": True,
                "G3_selected_vacuum_global_no_go_certified": True,
                "exact_lower_energy_field_witness_certified": True,
                "constructive_candidate_rejected_for_G3": True,
                "complete_potential_BFB": True,
                "global_competing_extrema_exhausted": vacuum_minimized,
                "G3_closed": False,
                "model_wide_no_go_certified": False,
                "whole_model_excluded": False,
                "proof_grade_model_wide_no_go": False,
            },
        },
    )
    write_json(
        root,
        "GAUGED_U1X_G3_CORRECTED_COMMON_KERNEL_V20.json",
        {
            "model_contract_id": "gauged_u1x_phi17_v20",
            "overall_state": "OPEN",
            "n_failed": 0,
            "flags": {
                "legacy_common_kernel_dimension_135_invalidated": True,
                "exact_H6_radial_flat_direction_refuted": True,
            },
            "corrected_common_kernel_diagnostic": {
                "corrected_common_kernel": {"rank": 448, "nullity": 0},
                "proof_grade": False,
                "certified_PSD_feasibility": False,
                "certified_no_go": False,
            },
        },
    )
    a_square = {
        "status": "EXACT_A_SQUARE_RECOUPLING_CERTIFIED",
        "overall_state": "CLOSED_SUBPROBLEM",
        "n_failed": 0,
        "certificate": {
            "source_binding_exact": True,
            "proof_grade": True,
            "unique_weights": ["40", "72", "28", "-8", "-12", "12"],
        },
        "flags": {
            "A_square_recoupling_exactly_source_bound": True,
            "complete_potential_BFB_exactly_certified": False,
            "full_Hessian_exactly_source_bound": False,
            "strict_local_minimum_certified": False,
            "G3_closed": False,
        },
    }
    sos_bfb = {
        "status": (
            "EXACT_COMPLETE_POTENTIAL_BFB_AND_SELECTED_STATIONARITY_CERTIFIED"
        ),
        "overall_state": "CLOSED_SUBPROBLEM",
        "model_contract_id": "gauged_u1x_phi17_v20",
        "n_failed": 0,
        "flags": {
            "complete_27_parameter_SOS_identity_exactly_source_bound": True,
            "complete_potential_BFB_exactly_certified": True,
            "selected_vacuum_stationarity_exactly_certified": True,
            "selected_vacuum_global_minimum_certified": False,
            "selected_vacuum_unique_modulo_symmetry": False,
            "full_Hessian_exactly_source_bound": False,
            "strict_local_minimum_certified": False,
            "G3_closed": False,
        },
    }
    pd_rank = {
        "status": (
            "DIRECT_EXACT_TRANSVERSE_HESSIAN_PASS__"
            "SOS_AND_GLOBAL_EXTREMA_EXTERNAL"
        ),
        "overall_state": "OPEN",
        "n_failed": 0,
        "direct_P_plus_Delta_certificate": {
            "source_binding_exact": True,
            "proof_grade": True,
        },
        "direct_exact_ranks": {
            "H_Phi_plus_K": {"rank": 429, "nullity": 33, "PSD": True}
        },
        "exact_full_kernel_argument": {
            "exact_full_Hessian_rank": 448,
            "remaining_kernel_dimension": 38,
            "source_binding_exact": True,
            "proof_grade": True,
        },
        "flags": {
            "conditional_exact_LDL_on_reconstructed_matrix": False,
            "direct_exact_source_binding": True,
            "proof_grade_P_plus_Delta_PSD": True,
            "proof_grade_full_rank_448": True,
            "strict_transverse_Hessian_positive_certified": True,
            "strict_local_minimum_certified_here": False,
            "global_minimum_certified": False,
            "global_uniqueness_certified": False,
            "G3_closed": False,
            "whole_model_validated": False,
            "whole_model_excluded": False,
        },
    }
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_A_SQUARE_RECOUPLING_V20.json",
        a_square,
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json",
        pd_rank,
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SOS_BFB_STATIONARITY_V20.json",
        sos_bfb,
    )
    write_json(
        root,
        "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json",
        {
            "status": (
                "EXACT_BFB_STATIONARY_STRICT_LOCAL_MINIMUM__"
                "GLOBAL_COUNTEREXAMPLE"
            ),
            "overall_state": "OPEN",
            "model_contract_id": "gauged_u1x_phi17_v20",
            "n_failed": 0,
            "coefficient_vector": {
                "nonzero_count": 27,
                "maximum_absolute_coefficient": 9.125,
                "symbolic_nonzero": {
                    "lambda::O48_B01_Phi_self_quartics": "-21/200"
                },
            },
            "symmetry_quotient": {
                "SO10_plus_U1X_plus_global_PQ_rank": 38,
                "massive_transverse_dimension": 448,
            },
            "exact_rank_certificate": pd_rank,
            "exact_A_square_recoupling_certificate": a_square,
            "exact_SOS_BFB_stationarity_certificate": sos_bfb,
            "flags": {
                "exact_sparse_51_parameter_candidate_constructed": True,
                "candidate_inside_4pi_box": True,
                "positive_J0_normalization_is_without_loss_of_generality": False,
                "manifest_BFB_decomposition_candidate_constructed": True,
                "A_square_recoupling_exactly_source_bound": True,
                "complete_potential_BFB_exactly_certified": True,
                "selected_vacuum_stationarity_exactly_compiler_certified": True,
                "selected_vacuum_global_minimum_certified": False,
                "selected_vacuum_global_minimum_disproved": True,
                "selected_vacuum_unique_modulo_symmetry": False,
                "exact_lower_energy_field_witness_certified": True,
                "constructive_candidate_rejected_for_G3": True,
                "P_plus_Delta_Qsqrt2_component_LDL_conditional": False,
                "P_plus_Delta_source_binding_exactly_certified": True,
                "full_448_kernel_count_conditional": False,
                "full_448_kernel_count_exact": True,
                "full_448_PSD_feasibility_certified": True,
                "strict_local_minimum_certified": True,
                "G3_closed": False,
                "whole_model_validated": False,
                "whole_model_excluded": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_KERNEL_QUARTIC_BOUND_V20.json",
        {
            "n_failed": 0,
            "flags": {
                "fixed_P_strict_local_global_no_go_exact": True,
                "fixed_P_branch_closed_negative": True,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_REPLACEMENT_STATIONARY_ORBIT_V20.json",
        {
            "n_failed": 0,
            "flags": {
                "replacement_full_stationarity_exact": True,
                "replacement_symmetry_orbit_rank_exact": True,
                "replacement_target_gauge_symmetry_correct": False,
                "replacement_strict_local_minimum_proof_grade": False,
                "replacement_global_minimum_established": False,
                "G3_closed": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_DELTA_PD_SOS_V20.json",
        {
            "status": "EXACT_SU5_DELTA_PD_GLOBAL_SOS_CANDIDATE_CERTIFIED",
            "n_failed": 0,
            "scope": {
                "Phi_Sigma_global_minimum_exact": True,
                "Phi_Sigma_stationarity_exact": True,
                "SO10_to_SM_stabilizer_dimension_exact": True,
                "Phi_Sigma_Hessian_rank_429_nullity_33_exact": True,
                "Phi_Sigma_quotient_strictly_positive_exact": True,
                "Phi_Sigma_equality_set_locally_one_orbit": True,
                "full_486_field_stationarity": False,
                "global_orbit_uniqueness": False,
                "G3_closed": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXTENSION_V20.json",
        {
            "status": (
                "EXACT_REAL_H_NO_GO__CHIRAL_H_STRICT_LOCAL_CANDIDATE__"
                "GLOBAL_GAP_OPEN"
            ),
            "n_failed": 0,
            "flag": {
                "real_H_e6_extension_exactly_excluded": True,
                "chiral_H_exact_stationary_candidate_constructed": True,
                "full_486_gradient_zero_live": True,
                "full_quartic_BFB_certified": True,
                "full_global_minimum_certified": False,
                "G3_closed": False,
            },
            "chiral_H_candidate": {
                "exact_orbit": {
                    "SO10_rank": 36,
                    "SO10_plus_U1X_rank": 37,
                    "SO10_plus_U1X_plus_PQ_rank": 38,
                    "physical_quotient_dimension": 448,
                }
            },
            "BFB_certificate": {
                "homogeneous_quartic_BFB_certified": True,
                "finite_field_global_gap_certified": False,
            },
            "live_full_gradient_and_quotient_Hessian": {
                "proof_grade": False,
                "transverse_dimension": 448,
                "negative_transverse_eigenvalues_below_minus_1e_minus_9": 0,
                "zero_transverse_eigenvalues_at_1e_minus_9": 0,
            },
            "global_status": {"global_equality_orbits_classified": False},
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json",
        {
            "status": "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED",
            "overall_state": "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM",
            "model_contract_id": "gauged_u1x_phi17_v20",
            "n_failed": 0,
            "flags": {
                "exact_rank_448": True,
                "exact_nullity_38": True,
                "exact_PSD": True,
                "strict_quotient": True,
                "strict_quotient_positive": True,
                "kernel_equals_38_symmetry_tangents": True,
                "proof_grade": True,
                "source_binding": True,
                "source_binding_exact": True,
            },
            "G3_closed": False,
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_EQUALITY_ORBIT_V20.json",
        {
            "status": (
                "EXACT_CONDITIONAL_EQUALITY_CLASSIFICATION__"
                "SIGNED_GLOBAL_PHI_ORBIT_LEMMA_OPEN"
            ),
            "overall_state": "OPEN_GLOBAL_LEMMA",
            "n_failed": 0,
            "scope": {
                "fixed_F_Sigma_global_equality_classified": True,
                "fixed_Delta_diagonal_Phi_global_equality_classified": True,
                "fixed_Delta_two_tau_plus_representatives_equivalent": True,
                "literal_single_Phi_orbit_statement_refuted": True,
                "minus_F_mixed_branch_excluded_exact": True,
                "corrected_signed_Phi_orbit_theorem_open": True,
                "complete_SU3_fixed_Phi_slice_classified_exactly": True,
                "global_equality_orbit_classification_complete": False,
                "G3_closed": False,
            },
            "remaining_global_lemma": {
                "proved": False,
                "literal_single_orbit_version_refuted": True,
                "corrected_signed_two_orbit_version": True,
                "complete_SU3_fixed_slice_classified_exactly": True,
                "SU3_fixed_slice_real_dimension": 16,
                "source_bound_certificate_available": False,
                "source_bound_partial_certificate_available": True,
                "numerical_search_is_not_a_substitute": True,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json",
        {
            "status": (
                "LITERAL_SINGLE_ORBIT_LEMMA_REFUTED__"
                "SIGNED_GLOBAL_LEMMA_OPEN"
            ),
            "overall_state": "SHARP_COUNTEREXAMPLE_AND_REDUCTION",
            "n_failed": 0,
            "checks": {
                "literal_single_orbit_lemma_is_refuted": True,
                "corrected_signed_global_lemma_not_overclaimed": True,
            },
            "corrected_global_lemma": {"proved": False},
            "scope": {
                "literal_plus_orbit_only_statement_refuted": True,
                "complete_SU4_invariant_slice_classified": True,
                "all_arbitrary_real_four_forms_classified": False,
                "corrected_signed_two_orbit_theorem_proved": False,
                "PD_global_equality_orbit_classification_complete": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_PHI_LOCAL_COMPONENT_V20.json",
        {
            "status": "EXACT_LOCAL_COMPONENT_THEOREM_CLOSED__DISTANT_COMPONENTS_OPEN",
            "overall_state": "LOCAL_COMPONENT_THEOREM_CLOSED",
            "n_failed": 0,
            "scope": {
                "plus_F_local_component_classified": True,
                "minus_F_local_component_classified": True,
                "signed_orbit_locally_isolated": True,
                "explicit_neighborhood_radius_available": False,
                "disconnected_distant_components_excluded": False,
                "corrected_signed_global_orbit_theorem_proved": False,
                "PD_global_equality_orbit_classification_complete": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_PHI_SU3_SLICE_V20.json",
        {
            "status": "EXACT_COMPLETE_SU3_FIXED_SLICE_CLASSIFIED__GENERIC_GLOBAL_OPEN",
            "overall_state": "SU3_FIXED_SLICE_CLOSED",
            "n_failed": 0,
            "checks": {
                "displayed_space_is_complete_SU3_fixed_space": True,
                "restricted_projector_rowspace_reduced_exactly": True,
                "eight_nondiagonal_directions_have_real_SOS_obstruction": True,
                "complete_SU3_fixed_slice_is_signed_Kahler_orbit": True,
            },
            "scope": {
                "complete_16_real_dimensional_SU3_fixed_space_classified": True,
                "all_nonzero_slice_solutions_are_signed_Kahler_squares": True,
                "all_arbitrary_real_four_forms_classified": False,
                "disconnected_distant_components_excluded": False,
                "corrected_signed_global_orbit_theorem_proved": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_CHIRAL_GLOBAL_GAP_REDUCTION_V20.json",
        {
            "status": "GLOBAL_GAP_REDUCED_TO_PD_EQUALITY_CLASSIFICATION",
            "overall_state": "FINAL_G3_TEST_OPEN",
            "n_failed": 0,
            "flags": {
                "lower_witness_found": False,
                "conditional_small_positive_beta_route_exists": True,
                "beta_1_over_20_global_minimum_certified": False,
                "global_equality_orbits_classified": False,
                "G3_closed": False,
            },
            "final_acceptance_test": {"currently_passes": False},
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_FIXED_F_OFFKERNEL_BOUND_V20.json",
        {
            "status": "EXACT_FIXED_F_FULL_OFFKERNEL_BETA_GAP_CERTIFIED",
            "overall_state": "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM",
            "n_failed": 0,
            "checks": {
                "mixed_offkernel_gap_at_least_6_over_5_exact": True,
                "pure_hplus_current_error_bound_exact": True,
                "kernel_chirality_cross_zero_exact": True,
                "cross_block_bound_exact": True,
                "rational_inside_outside_patch_positive": True,
                "full_fixed_F_equality_orbit_exact": True,
            },
            "scope": {
                "Phi_fixed_to_F": True,
                "H_arbitrary": True,
                "Sigma_arbitrary": True,
                "beta_equals_1_over_20": True,
                "global_gap_nonnegative_on_full_fixed_F_stratum": True,
                "equality_is_selected_SU5_flag_orbit": True,
                "arbitrary_Phi_proved": False,
                "G3_closed": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_ZERO_RESIDUAL_BOUND_V20.json",
        {
            "status": "EXACT_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_ROUTE_EXCLUDED",
            "overall_state": (
                "CLOSED_PURE_DELTA_MAX_NEGATIVE_MIXED_ZERO_STRATUM__ARBITRARY_PHI_OPEN"
            ),
            "model_contract_id": "gauged_u1x_phi17_v20",
            "n_failed": 0,
            "checks": {
                "exact_rank_168_nullity_42": True,
                "kernel_splits_35_plus_7_exactly": True,
                "live_HSX_and_PD_coefficients_bound_exactly": True,
                "N_and_C00_C11_contraction_identities_computed_exactly": True,
                "Phi_radial_plus_I54_lower_bound_1_over_141": True,
                "worst_radial_current_minimum_exact": True,
                "strict_positive_stratum_margin_exact": True,
                "u_zero_and_v_zero_radial_boundaries_closed_exactly": True,
            },
            "exact_stratum_gap": {"strict_margin": "7859/140295000"},
            "scope": {
                "strongest_all_zero_max_negative_route_excluded": True,
                "strongest_pure_Delta_mixed_zero_max_negative_route_excluded": True,
                "normalized_affine_stratum_requires_u_gt_0_v_gt_0": True,
                "u_zero_and_v_zero_boundaries_closed_separately": True,
                "nonzero_residual_cancellations_excluded": False,
                "arbitrary_Phi_global_gap_proved": False,
                "G3_closed": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_FULL_RESIDUAL_BOUND_V20.json",
        {
            "status": "EXACT_MAX_NEGATIVE_FULL_RESIDUAL_PURE_DELTA_BOUND_CERTIFIED",
            "overall_state": (
                "CLOSED_MAX_NEGATIVE_PURE_DELTA_ARBITRARY_PHI_SUBPROBLEM"
            ),
            "model_contract_id": "gauged_u1x_phi17_v20",
            "n_failed": 0,
            "checks": {
                "live_restricted_residual_normalizations_exact": True,
                "single_4125_covariant_Cauchy_bound_exact": True,
                "anchor_quadratic_has_exact_positive_spectral_floor": True,
                "anchor_lower_bound_strictly_exceeds_1_over_50": True,
                "piecewise_u_v_completion_covers_nonnegative_quadrant": True,
                "exact_1_over_5000_saturation_exhibited": True,
                "arbitrary_real_Phi_covered": True,
                "mixed_and_chiral_residuals_not_assumed_zero": True,
                "arbitrary_Sigma_orientation_not_overclaimed": True,
                "G3_not_overclaimed": True,
            },
            "scope": {
                "Sigma_on_pure_Delta_orbit": True,
                "H_current_saturates_I45_equals_minus_NH_NSigma": True,
                "Phi_arbitrary_real_210": True,
                "nonzero_Phi_Sigma_residuals_covered": True,
                "nonzero_chiral_Phi_H_residual_covered": True,
                "u_v_all_nonnegative": True,
                "restricted_gap_global_minimum": "1/5000",
                "strictly_above_selected_vacuum_gap_zero": True,
                "arbitrary_Sigma_orientation_proved": False,
                "G3_closed": False,
            },
        },
    )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json",
        {
            "status": "EXACT_RANK1_SU3_DANGEROUS_SLICE_BOUND_CERTIFIED",
            "overall_state": "CLOSED_RANK1_SU3_SLICE__ARBITRARY_RANK1_PHI_OPEN",
            "model_contract_id": matrix.MODEL_CONTRACT_ID,
            "n_failed": 0,
            "failed_checks": [],
            "checks": {
                "rank1_live_residual_source_exact": True,
                "explicit_endpoint_current_and_self_projectors_exactly": True,
                "slice_basis_Gram_exact": True,
                "rank1_common_affine_kernel_rank160_nullity50_exact": True,
                "angular_projector_Gram_symmetric_exact": True,
                "angular_projector_int64_overflow_preflight_exact": True,
                "anchor_polynomial_reconstructed_exactly": True,
                "rational_SOS_polynomial_identity_exact": True,
                "rational_SOS_Gram_positive_definite_exact": True,
                "anchor_at_least_3_over_200_exact": True,
                "radial_patch_global_minimum_1_over_5000_exact": True,
                "attaining_slice_witness_evaluated_from_live_arrays_exact": True,
                "arbitrary_rank1_Phi_proved": False,
                "arbitrary_Sigma35_proved": False,
                "G3_closed": False,
            },
            "scope": {
                "H_fixed_to_h_minus": True,
                "Sigma_fixed_to_normalized_explicit_decomposable_pure_spinor": True,
                "Phi_restricted_to_four_real_SU3_fixed_variables": True,
                "Phi_slice_real_dimension": 4,
                "full_SU3_fixed_space_real_dimension": 16,
                "full_SU3_fixed_space_proved": False,
                "u_v_arbitrary_nonnegative": True,
                "arbitrary_real_Phi": False,
                "arbitrary_max_negative_Sigma": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
            "SOS": {"strict_anchor_lower_bound": "3/200"},
            "radial_patch": {"restricted_global_minimum": "1/5000"},
        },
    )
    for filename in (
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
    ):
        write_json(
            root,
            filename,
            json.loads((matrix.ROOT / filename).read_text(encoding="utf-8")),
        )
    write_json(
        root,
        "EXACT_GAUGED_U1X_G3_ALTERNATIVE_GLOBAL_SOS_AUDIT_V20.json",
        {
            "status": "ALTERNATIVE_GLOBAL_SOS_AUDIT_COMPLETE__NO_CERTIFIED_REPLACEMENT",
            "overall_state": "G3_GLOBAL_ALTERNATIVE_OPEN",
            "n_failed": 0,
            "flags": {
                "globally_certifiable_alternative_found": False,
                "all_vanishing_45_current_Gram_completion_excluded": True,
                "all_vanishing_affine_SOS_completion_excluded": True,
                "all_vanishing_unique_chiral_quartic_completion_excluded": True,
                "nonvanishing_residual_gradient_cancellation_excluded": False,
                "different_vacuum_orbit_excluded": False,
                "G3_closed": False,
                "whole_model_excluded": False,
            },
        },
    )
    write_json(
        root,
        "FINAL_G3_ACCEPTANCE_GATE_V20.json",
        {
            "status": "FINAL_G3_ACCEPTANCE_TEST_EXECUTED",
            "overall_state": "OPEN",
            "n_failed": 0,
            "classification": {
                "mathematical_G3_closed": False,
                "release_G3_verified": False,
                "whole_model_excluded": False,
                "theory_still_viable": True,
                "G3_closed": False,
            },
        },
    )
    write_json(
        root,
        "so10_axion_v20_verdict.json",
        {
            "status": "PASS" if engine_pass else "FAIL",
            "n_checks_total": 42,
            "n_checks_failed": 0 if engine_pass else 1,
        },
    )
    write_json(
        root,
        "V20_ERROR_AUDIT.json",
        {
            "status": "PASS",
            "n_checks_failed": 0,
            "soft_falsifications_of_manuscript_overclaims": [
                "manuscript portal list is incomplete"
            ],
        },
    )
    write_json(
        root,
        "FALSIFICATION_VERDICT.json",
        {
            "status": "PASS",
            "n_hard_failed": 0,
            "n_soft_overclaim_missed": 0,
        },
    )
    write_json(
        root,
        "EXTENSIVE_CONFIRM_FALSIFY_VERDICT.json",
        {
            "status": "PASS",
            "n_extensive_checks": 53,
            "n_failed": 0,
        },
    )
    write_json(
        root,
        "GLOBAL_FLAVOUR_FIT_V20_VERDICT.json",
        {
            "best_point": {
                "chi2": 4.9,
                "viable_chi2_lt_30": True,
                "rg_threshold_status": {
                    "common_scale_RG_inputs_applied": False,
                    "two_loop_thresholds_coupled": False,
                },
            }
        },
    )
    write_json(
        root,
        "UV_VACUUM_ALIGNMENT_V20_VERDICT.json",
        {
            "status": "CONDITIONAL_ALIGNMENT_AXIOM",
            "flag": {
                "vacuum_alignment_principle_stated": True,
                "exact_W_zero_vacuum_selected": True,
                "scalar_quartic_landscape_fully_minimized": vacuum_minimized,
                "unconditional_unique_Cf": False,
            },
        },
    )
    write_json(
        root,
        "YUKAWA_RGE_2LOOP_V20_VERDICT.json",
        {
            "status": "DIAGNOSTIC_CHAIN",
            "flag": {
                "piecewise_yukawa_chain_integrated": True,
                "clebsch_threshold_matching_implemented": True,
                "two_loop_so10_complete": full_rg,
                "published_210_tensor_contractions": full_rg,
                "piecewise_component_threshold_matching_complete": full_rg,
            },
        },
    )
    write_json(
        root,
        "PORTAL_FULL_COMPLEX_ORIENTATION_SPHERE_V20_VERDICT.json",
        {
            "scan": {
                "aggregate_counts": {
                    "n_total_points": 100,
                    "n_NA62_excluded": 90,
                    "n_NA62_surviving": 10,
                    "geometric_fraction_is_uv_probability": sphere_probability,
                }
            }
        },
    )
    write_json(
        root,
        "PORTAL_YUKAWA_POSTERIOR_V20_VERDICT.json",
        {"flag": {"full_portal_yukawa_posterior_derived": False}},
    )
    write_json(root, "NEXT_PHYSICS_ANALYSIS_VERDICT.json", {"status": "PASS"})
    write_json(
        root,
        "HALOSCOPE_37GHZ_LIMIT_COMPARE_V20_VERDICT.json",
        {
            "flag": {
                "real_37GHz_detection": False,
                "benchmark_excluded": False,
            }
        },
    )
    write_json(
        root,
        "CURRENT_UNIT_TEST_ATTESTATION.json",
        {
            "passed": unit_pass,
            "tests_discovered": 1,
            "commit_sha": "test",
        },
    )


class TheoryValidationMatrixTests(unittest.TestCase):
    def test_rank1_slice_rejects_wrong_fixed_H_orientation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / (
                "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_"
                "RANK1_SU3_SLICE_V20.json"
            )
            forged = json.loads(artifact.read_text(encoding="utf-8"))
            forged["scope"]["H_fixed_to_h_minus"] = False
            write_json(root, artifact.name, forged)
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
                ]
            )

    def test_rank1_su4_infrastructure_is_exact_but_does_not_close_g3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=True)
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            evidence = vacuum["evidence"]
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_stabilizer_infrastructure_exact"]
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_joint_stabilizer_dimension"], 15
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_Phi210_intertwiner_infrastructure_exact"
                ]
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_Phi210_carrier_count"], 25
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_Sym2_invariant_dimension"], 45
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_aligned_carriers_exact"]
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_aligned_direct_sum_rank"], 210
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_physical_real_maps_exact"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_Phi210_quadratic_basis_exact"]
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_quadratic_constraint_shape"],
                [5952, 551],
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_quadratic_constraint_rank"], 506
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_quadratic_constraint_nullity"], 45
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_quadratic_basis_count"], 45
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_quadratic_basis_rank"], 45
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_quadratic_live_invariance_exact"]
            )
            self.assertTrue(evidence["gauged_G3_rank1_SU4_Schur_SOS_SDP_open"])
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_arbitrary_Phi_bound_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_SOS_census_exact"]
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_homogeneous_dimension"
                ],
                22_366,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_isotypic_type_count"],
                35,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_irreducible_copy_count"
                ],
                824,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_Schur_parameter_count"],
                19_594,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_invariant_row_count"],
                6_585,
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_coordinate_Schur_map_open"
                ]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_physical_target_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_SDP_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_arbitrary_Phi_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_G3_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_cubic_map_exact"]
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_cubic_carrier_copy_count"
                ],
                540,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_cubic_real_variable_count"
                ],
                1_414,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_cubic_map_shape"],
                [478, 1_414],
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_cubic_map_rank"], 478
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_cubic_map_kernel_dimension"
                ],
                936,
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_cubic_zero_placeholder_nonphysical"
                ]
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_cubic_other_maps_open"
                ]
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_cubic_physical_target_open"
                ]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_cubic_SDP_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_cubic_G3_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_quartic_map_exact"]
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_quartic_carrier_family_count"
                ],
                35,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_quartic_irreducible_copy_count"
                ],
                798,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_quartic_map_shape"],
                [6_057, 18_085],
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_quartic_map_rank"],
                6_057,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_quartic_map_kernel_dimension"
                ],
                12_028,
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_quartic_physical_target_open"
                ]
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_quartic_standard_PSD_congruences_open"
                ]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_quartic_SDP_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_quartic_G3_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_PSD_target_exact"]
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_standard_PSD_route_count"],
                22,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_standard_PSD_parameter_count"
                ],
                19_594,
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_real_type_PSD_congruences_exact"
                ]
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_complex_Hermitian_coordinates_exact"
                ]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_physical_target_exact"]
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_physical_target_row_count"],
                6_585,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_physical_target_common_denominator"
                ],
                1_728_000,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_physical_target_nonzero_count"
                ],
                845,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_augmented_physical_target_sha256"],
                "e2d9eec1b01b3eeefc4a54d404db93171aa6600ea9ef646a215ab0b5401f7630",
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_augmented_standard_coordinate_map_open"
                ]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_PSD_SDP_open"]
            )
            self.assertTrue(
                evidence["gauged_G3_rank1_SU4_augmented_PSD_G3_open"]
            )
            self.assertIn("478x1414 integer map", vacuum["summary"])
            self.assertIn("kernel dimension 936", vacuum["summary"])
            self.assertIn(
                "reserved zero placeholder is nonphysical", vacuum["summary"]
            )
            self.assertIn(
                "exact-rank-6057, 6057x18085 integer map", vacuum["summary"]
            )
            self.assertIn("kernel dimension 12028", vacuum["summary"])
            self.assertIn("22 standard PSD-coordinate routes", vacuum["summary"])
            self.assertIn("physical 6585-row target", vacuum["summary"])
            self.assertIn(
                "coefficient map in standard PSD coordinates", vacuum["summary"]
            )
            self.assertNotIn("infrastructure only", vacuum["summary"])

    def test_rank1_su4_infrastructure_mutations_fail_closed(self):
        mutations = (
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_STABILIZER_V20.json",
                lambda value: value["scope"].__setitem__("G3_closed", True),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
                lambda value: value["scope"].__setitem__(
                    "Schur_SOS_SDP_constructed", True
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_ALIGNED_CARRIERS_V20.json",
                lambda value: value["alignment"].__setitem__(
                    "concatenated_aligned_basis_rank_mod_prime", 209
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
                lambda value: value["constraint_system"].__setitem__(
                    "exact_rational_rank", 505
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json",
                lambda value: value["scope"].__setitem__(
                    "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
                    True,
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CENSUS_V20.json",
                lambda value: value["scope"].__setitem__("G3_closed", True),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
                lambda value: value["cubic_coordinate_map"].__setitem__(
                    "exact_rank", 477
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
                lambda value: value["cubic_coordinate_map"].__setitem__(
                    "abstract_zero_placeholder_is_not_a_physical_G3_target",
                    False,
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
                lambda value: value["scope"].__setitem__(
                    "physical_G3_gap_target_vector_constructed", True
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_V20.json",
                lambda value: value["scope"].__setitem__("G3_closed", True),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
                lambda value: value["coefficient_map_certificate"].__setitem__(
                    "rank_over_Q_exact", 6_056
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
                lambda value: value["scope"].__setitem__(
                    "semidefinite_feasibility_solved", True
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_V20.json",
                lambda value: value["scope"].__setitem__("G3_closed", True),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
                lambda value: value["standard_PSD_coordinate_routes"].__setitem__(
                    "standard_total_parameter_count", 19_593
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_V20.json",
                lambda value: value["scope"].__setitem__("G3_closed", True),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_QUADRATIC_BASIS_V20.json",
                lambda value: value["scope"].__setitem__(
                    "augmented_homogeneous_Schur_SOS_SDP_constructed", True
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
                lambda value: value["companion_stabilizer_provenance"].__setitem__(
                    "all_required_provenance_exact", False
                ),
            ),
            (
                "EXACT_GAUGED_U1X_G3_RANK1_SU4_PHI210_INTERTWINERS_V20.json",
                lambda value: value["intertwiner"].__setitem__(
                    "intertwining_count", 14
                ),
            ),
        )
        for filename, mutate in mutations:
            with self.subTest(filename=filename, mutation=mutate.__code__.co_firstlineno):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    minimal_tree(root, contract_consistent=True)
                    path = root / filename
                    forged = json.loads(path.read_text(encoding="utf-8"))
                    mutate(forged)
                    write_json(root, filename, forged)
                    report = matrix.build_report(root)
                    vacuum = next(
                        gate
                        for gate in report["gates"]
                        if gate["name"]
                        == "full_scalar_potential_vacuum_and_spectrum"
                    )
                    self.assertFalse(
                        vacuum["evidence"][
                            "gauged_G3_frontier_honestly_fail_closed"
                        ]
                    )
                    if filename.endswith("AUGMENTED_SOS_PSD_TARGET_V20.json"):
                        self.assertTrue(
                            vacuum["evidence"][
                                "gauged_G3_rank1_SU4_augmented_quartic_map_exact"
                            ]
                        )
                    else:
                        self.assertFalse(
                            vacuum["evidence"][
                                "gauged_G3_rank1_SU4_augmented_quartic_map_exact"
                            ]
                        )
                    self.assertFalse(
                        vacuum["evidence"][
                            "gauged_G3_rank1_SU4_augmented_PSD_target_exact"
                        ]
                    )

    def test_conditional_candidate_is_not_full_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["classification"],
                "INTERNALLY_CONSISTENT_CONDITIONAL_CANDIDATE",
            )
            self.assertFalse(report["full_theory_validated"])
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(states["proton_decay"], "OPEN")
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"],
                "OPEN",
            )
            self.assertEqual(states["UV_portal_selection_and_FCNC"], "CONDITIONAL")

    def test_core_failure_rejects_current_realization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, engine_pass=False)
            report = matrix.build_report(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["decision"], "REJECT")
            self.assertIn(
                "mathematical_and_software_core",
                report["failed_gates"],
            )

    def test_geometric_fraction_cannot_be_promoted_to_uv_probability(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, sphere_probability=True)
            report = matrix.build_report(root)
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(
                report["classification"],
                "VALIDATION_MATRIX_FAIL__OVERCLAIM",
            )
            self.assertTrue(
                any("UV probability" in item for item in report["overclaim_errors"])
            )

    def test_partial_rge_and_axiom_vacuum_stay_conditional(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, vacuum_minimized=False, full_rg=False)
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"],
                "OPEN",
            )
            self.assertEqual(
                states["two_loop_RGE_unification_and_thresholds"],
                "CONDITIONAL",
            )

    def test_current_repository_can_never_claim_discovery_from_internal_tests(self):
        report = matrix.build_report(matrix.ROOT)
        self.assertFalse(report["empirical_discovery"])
        self.assertFalse(report["full_theory_validated"])
        self.assertIn(
            report["classification"],
            {
                "MODEL_CONTRACT_INCONSISTENT__AUTHORITATIVE_GATES_REOPENED",
                "INTERNALLY_CONSISTENT_CONDITIONAL_CANDIDATE",
                "INSUFFICIENT_CURRENT_REPRODUCIBILITY",
            },
        )

    def test_contract_mismatch_blocks_without_falsely_rejecting_theory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=False)
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["overall_state"], "BLOCKED")
            self.assertEqual(report["decision"], "WITHHOLD_APPROVAL")
            self.assertEqual(states["authoritative_model_contract"], "BLOCKED")
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"], "BLOCKED"
            )
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertTrue(
                vacuum["evidence"]["gauged_G2_scoped_calculation_complete"]
            )
            self.assertEqual(
                vacuum["evidence"]["gauged_G2_direction_parameter_field_counts"],
                [44, 51, 486],
            )
            self.assertEqual(
                vacuum["evidence"]["gauged_G2_promoted_stationarity_rank_nullity"],
                [13, 38],
            )
            self.assertTrue(vacuum["evidence"][
                "gauged_G2_exact_projector_zero_corrected_normalized_SVD_rank_13"
            ])
            self.assertTrue(vacuum["evidence"][
                "gauged_G2_stationarity_rank_13_exactly_certified"
            ])
            self.assertTrue(vacuum["evidence"][
                "gauged_G2_stationarity_nullity_38_exactly_certified"
            ])
            self.assertTrue(vacuum["evidence"][
                "gauged_G2_stationarity_rank_upper_bound_13_exactly_certified"
            ])
            self.assertTrue(
                vacuum["evidence"]["gauged_G3_contract_and_coverage_bound"]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_corrected_common_kernel_honestly_bound"
                ]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_corrected_common_kernel_rank_nullity_numerical"
                ],
                [448, 0],
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_corrected_common_kernel_proof_grade"
                ]
            )
            self.assertTrue(
                vacuum["evidence"]["gauged_G3_SOS_candidate_honestly_scoped"]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_A_square_recoupling_exactly_source_bound"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SOS_BFB_stationarity_exactly_source_bound"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_PD_rank_direct_exact_and_fail_closed"
                ]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_constructive_candidate_nonzero_of_51"
                ],
                [27, 51],
            )
            self.assertEqual(
                vacuum["evidence"]["gauged_G3_exact_PD_rank_nullity"],
                [429, 33],
            )
            self.assertEqual(
                vacuum["evidence"]["gauged_G3_exact_full_Hessian_rank"],
                448,
            )
            self.assertTrue(
                vacuum["evidence"]["gauged_G3_direct_PD_source_binding"]
            )
            self.assertTrue(
                vacuum["evidence"]["gauged_G3_frontier_honestly_fail_closed"]
            )
            self.assertTrue(
                vacuum["evidence"]["gauged_G3_fixed_P_branch_exactly_excluded"]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_lower_replacement_rejected_for_wrong_symmetry"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_PD_exact_global_frontier"
                ]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_PD_exact_Hessian_rank_nullity"
                ],
                [429, 33],
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_PD_full_486_extension_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_PD_global_orbit_uniqueness_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"]["gauged_G3_SU5_Delta_HSX_honest_frontier"]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_exact_symmetry_ranks"
                ],
                [36, 37, 38],
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_full_quartic_BFB_exact"
                ]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_transverse_dimension"
                ],
                448,
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_full_Hessian_proof_grade"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_exact_Hessian_audit_fail_closed"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_exact_Hessian_certified"
                ]
            )
            self.assertTrue(
                vacuum["evidence"]["gauged_G3_SU5_equality_honestly_reduced"]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Phi_orbit_literal_refuted_signed_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_signed_Phi_local_components_exactly_closed"
                ]
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_distant_Phi_components_excluded"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Phi_SU3_fixed_slice_exactly_closed"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_global_Phi_orbit_lemma_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_chiral_global_gap_honestly_reduced"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_fixed_F_full_gap_exactly_closed"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_arbitrary_Phi_offstratum_gap_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_zero_residual_artifact_present"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_full_residual_artifact_present"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_rank1_SU3_slice_artifact_present"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_all_zero_residual_route_excluded"
                ]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_all_zero_residual_strict_margin"
                ],
                "7859/140295000",
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_pure_Delta_full_residual_gap_closed"
                ]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_pure_Delta_full_residual_minimum"
                ],
                "1/5000",
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
                ]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_rank1_SU3_slice_dimension"
                ],
                4,
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_rank1_SU3_ambient_dimension"
                ],
                16,
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_rank1_SU3_slice_minimum"
                ],
                "1/5000",
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_arbitrary_rank1_Phi_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_arbitrary_Sigma_orientation_open"
                ]
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_arbitrary_Phi_nonzero_residual_cancellations_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_arbitrary_Phi_uniform_coercivity_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_arbitrary_non_pure_Delta_Sigma_coercivity_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_alternative_global_SOS_honestly_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_all_vanishing_global_SOS_routes_excluded"
                ]
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_beta_1_over_20_global_certified"
                ]
            )
            self.assertFalse(
                vacuum["evidence"]["gauged_G3_final_acceptance_test_passes"]
            )
            self.assertTrue(
                vacuum["evidence"]["final_G3_acceptance_gate_honestly_open"]
            )
            self.assertEqual(
                vacuum["evidence"][
                    "gauged_G3_direction_parameter_field_quotient_counts"
                ],
                [44, 51, 486, 449, 448],
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_gauge_quotient_dimension_449_certified"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_massive_transverse_dimension_448_certified"
                ]
            )
            self.assertTrue(vacuum["evidence"][
                "gauged_G3_legacy_physical_quotient_448_alias_present"
            ])
            self.assertTrue(vacuum["evidence"][
                "gauged_G3_stationarity_rank_13_exactly_certified"
            ])
            self.assertEqual(report["failed_gates"], [])

    def test_unbound_external_boolean_cannot_pass_model_contract_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=True)
            path = root / "EXACT_X_SYMMETRY_CONSISTENCY_GATE_V20.json"
            audit = json.loads(path.read_text(encoding="utf-8"))
            audit["external_model_validation"] = {
                "schema": "legacy-unbound-attestation",
                "valid": True,
                "checks": {},
            }
            path.write_text(json.dumps(audit), encoding="utf-8")
            report = matrix.build_report(root)
            contract_gate = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "authoritative_model_contract"
            )
            self.assertEqual(contract_gate["state"], "BLOCKED")
            self.assertFalse(
                contract_gate["evidence"][
                    "tool_native_bound_external_evidence"
                ]
            )
            self.assertFalse(report["full_theory_validated"])

    def test_hypothetical_consistent_stable_gauged_vacuum_can_pass_vacuum_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=True,
            )
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(states["authoritative_model_contract"], "PASS")
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"], "PASS"
            )

    def test_numerical_rank_diagnostic_cannot_promote_vacuum_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=False,
            )
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"], "OPEN"
            )

    def test_stale_g3_contract_cannot_promote_vacuum_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=True,
            )
            path = root / "GAUGED_U1X_G3_STABILITY_V20.json"
            stale = json.loads(path.read_text(encoding="utf-8"))
            stale["model_contract_id"] = "historical_option_c_no_x_v20"
            path.write_text(json.dumps(stale), encoding="utf-8")
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertEqual(vacuum["state"], "OPEN")
            self.assertFalse(
                vacuum["evidence"]["gauged_G3_contract_and_coverage_bound"]
            )

    def test_incomplete_g3_coverage_cannot_promote_vacuum_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=True,
            )
            path = root / "GAUGED_U1X_G3_STABILITY_V20.json"
            incomplete = json.loads(path.read_text(encoding="utf-8"))
            incomplete["coverage"]["massive_transverse_quotient_dimension"] = 449
            path.write_text(json.dumps(incomplete), encoding="utf-8")
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertEqual(vacuum["state"], "OPEN")
            self.assertFalse(
                vacuum["evidence"]["gauged_G3_contract_and_coverage_bound"]
            )

    def test_uncertified_no_go_flags_cannot_reject_theory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=True,
            )
            path = root / "GAUGED_U1X_G3_STABILITY_V20.json"
            candidate = json.loads(path.read_text(encoding="utf-8"))
            flags = candidate["flags"]
            flags["G3_fixed_vacuum_strict_minimum_certified"] = False
            flags["complete_potential_BFB"] = False
            flags["global_competing_extrema_exhausted"] = False
            flags["model_wide_no_go_certified"] = True
            flags["whole_model_excluded"] = True
            flags["proof_grade_model_wide_no_go"] = False
            path.write_text(json.dumps(candidate), encoding="utf-8")
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertEqual(vacuum["state"], "OPEN")
            self.assertFalse(
                vacuum["evidence"]["gauged_model_wide_no_go_certified"]
            )
            self.assertNotIn(
                "full_scalar_potential_vacuum_and_spectrum",
                report["failed_gates"],
            )

    def test_missing_constructive_g3_artifact_cannot_promote_vacuum_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=True,
            )
            root.joinpath("GAUGED_U1X_G3_SOS_CANDIDATE_V20.json").unlink()
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertEqual(vacuum["state"], "OPEN")
            self.assertFalse(
                vacuum["evidence"]["gauged_G3_frontier_honestly_fail_closed"]
            )
            self.assertIn(
                "GAUGED_U1X_G3_SOS_CANDIDATE_V20.json",
                report["missing_artifacts"],
            )

    def test_direct_pd_certificate_cannot_drop_exact_source_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=True,
            )
            path = root / "EXACT_GAUGED_U1X_G3_PD_RANK_CERTIFICATE_V20.json"
            forged = json.loads(path.read_text(encoding="utf-8"))
            forged["flags"]["direct_exact_source_binding"] = False
            path.write_text(json.dumps(forged), encoding="utf-8")
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertEqual(vacuum["state"], "OPEN")
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_PD_rank_direct_exact_and_fail_closed"
                ]
            )
            self.assertFalse(
                vacuum["evidence"]["gauged_G3_frontier_honestly_fail_closed"]
            )

    def test_incomplete_exact_hessian_audit_remains_recognized_but_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=False)
            path = root / "EXACT_GAUGED_U1X_G3_SU5_DELTA_HSX_EXACT_HESSIAN_V20.json"
            audit = json.loads(path.read_text(encoding="utf-8"))
            audit["status"] = "EXACT_HESSIAN_CERTIFICATE_INCOMPLETE"
            audit["overall_state"] = "G3_EXACT_LOCAL_TEST_OPEN"
            audit["flags"] = {
                name: False
                for name in (
                    "exact_rank_448",
                    "exact_nullity_38",
                    "exact_PSD",
                    "strict_quotient",
                    "proof_grade",
                    "source_binding",
                )
            }
            path.write_text(json.dumps(audit), encoding="utf-8")
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_exact_Hessian_audit_fail_closed"
                ]
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_Delta_HSX_exact_Hessian_certified"
                ]
            )

    def test_phi_orbit_audit_cannot_promote_the_signed_open_lemma(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=False)
            path = root / "EXACT_GAUGED_U1X_G3_SU5_PHI_ORBIT_LEMMA_V20.json"
            audit = json.loads(path.read_text(encoding="utf-8"))
            audit["scope"]["corrected_signed_two_orbit_theorem_proved"] = True
            path.write_text(json.dumps(audit), encoding="utf-8")
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_Phi_orbit_literal_refuted_signed_open"
                ]
            )
            self.assertFalse(
                vacuum["evidence"]["gauged_G3_frontier_honestly_fail_closed"]
            )

    def test_rank1_slice_cannot_overclaim_arbitrary_phi_sigma_or_g3(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=True)
            path = (
                root
                / "EXACT_GAUGED_U1X_G3_SU5_MAX_NEGATIVE_RANK1_SU3_SLICE_V20.json"
            )
            forged = json.loads(path.read_text(encoding="utf-8"))
            forged["checks"]["arbitrary_Sigma35_proved"] = True
            path.write_text(json.dumps(forged), encoding="utf-8")
            report = matrix.build_report(root)
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_max_negative_rank1_SU3_four_dimensional_slice_closed"
                ]
            )
            self.assertFalse(
                vacuum["evidence"]["gauged_G3_frontier_honestly_fail_closed"]
            )


if __name__ == "__main__":
    unittest.main()
