#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
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
    path = root.joinpath(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


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
    # Each fixture is a distinct temporary import root.  Avoid unittest's
    # module-cache collision for the byte-pinned producer test copied below.
    sys.modules.pop("test_exact_physical_g7_component_threshold_contract_v20", None)
    sys.modules.pop("test_exact_normalized_so10_yukawa_cgcs_v20", None)
    sys.modules.pop("test_physical_sm_vacuum_local_feasibility_v20", None)
    sys.modules.pop(
        "test_physical_sm_source_algebra_equality_frontier_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_five_amplitude_equality_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_hard_projector_hessians_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_last_six_hessians_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_37_row_aggregate_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_local_equality_orbit_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_g4_g5_branch_mismatch_v20", None
    )
    sys.modules.pop("test_exact_physical_sm_heavy_vector_masses_v20", None)
    sys.modules.pop(
        "test_exact_physical_sm_heavy_vector_msbar_matching_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_vector_rxi_vacuum_cancellation_v20", None
    )
    sys.modules.pop(
        "test_conditional_physical_sm_eft_hessian_spectrum_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_g6_g7_closure_frontier_v20", None
    )
    sys.modules.pop(
        "test_exact_physical_sm_g8_identifiability_frontier_v20", None
    )
    canonical_g1_artifact = json.loads(
        (matrix.ROOT / "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json").read_text(
            encoding="utf-8"
        )
    )
    canonical_g1_paths = {
        row["path"] for row in canonical_g1_artifact["source_manifest"]
    }
    canonical_g1_paths.update(
        {
            "CANONICAL_G1_COMPLETE_OPERATOR_RING_DIM6_V21.json",
            "verify_canonical_g1_complete_operator_ring_dim6_v21.py",
        }
    )
    for name in sorted(canonical_g1_paths):
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((matrix.ROOT / name).read_bytes())
    for name in (
        matrix.EXACT_X_V3_SOURCE,
        matrix.EXACT_X_V3_TEST,
        matrix.EXACT_X_V3_MD,
        matrix.EXACT_X_V3_INPUT_MANIFEST,
        matrix.EXACT_X_V3_TRUSTED_SARAH_MANIFEST,
    ):
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((matrix.ROOT / name).read_bytes())
    g1_component_artifact = matrix.ARTIFACTS[
        "renormalizable_g1_component_tensor"
    ]
    root.joinpath(g1_component_artifact).write_bytes(
        matrix.ROOT.joinpath(g1_component_artifact).read_bytes()
    )
    root.joinpath(matrix.RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE).write_bytes(
        matrix.ROOT.joinpath(
            matrix.RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE
        ).read_bytes()
    )
    g1_component_tensor_closure = (
        matrix.gate_ledger._renormalizable_g1_component_tensor_closure(
            json.loads(
                root.joinpath(g1_component_artifact).read_text(encoding="utf-8")
            ),
            raw_sha256=matrix.gate_ledger._raw_file_sha256(
                root / g1_component_artifact
            ),
            source_raw_sha256=matrix.gate_ledger._raw_file_sha256(
                root / matrix.RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE
            ),
        )
    )
    g2_mathematical_artifact = matrix.ARTIFACTS[
        "renormalizable_g2_mathematical"
    ]
    root.joinpath(g2_mathematical_artifact).write_bytes(
        matrix.ROOT.joinpath(g2_mathematical_artifact).read_bytes()
    )
    root.joinpath(matrix.RENORMALIZABLE_G2_MATHEMATICAL_SOURCE).write_bytes(
        matrix.ROOT.joinpath(
            matrix.RENORMALIZABLE_G2_MATHEMATICAL_SOURCE
        ).read_bytes()
    )
    g7_artifact = matrix.ARTIFACTS["eft_g7_nonidentifiability"]
    root.joinpath(g7_artifact).write_bytes(
        matrix.ROOT.joinpath(g7_artifact).read_bytes()
    )
    root.joinpath(matrix.EFT_G7_NONIDENTIFIABILITY_SOURCE).write_bytes(
        matrix.ROOT.joinpath(matrix.EFT_G7_NONIDENTIFIABILITY_SOURCE).read_bytes()
    )
    physical_g7_artifact = matrix.ARTIFACTS["physical_g7_component_threshold"]
    for name in (
        physical_g7_artifact,
        matrix.PHYSICAL_G7_COMPONENT_THRESHOLD_SOURCE,
        matrix.PHYSICAL_G7_COMPONENT_THRESHOLD_TEST,
        matrix.PHYSICAL_G7_COMPONENT_THRESHOLD_MD,
    ):
        root.joinpath(name).write_bytes(matrix.ROOT.joinpath(name).read_bytes())
    for name in (
        matrix.ARTIFACTS["normalized_yukawa_cgcs"],
        matrix.NORMALIZED_YUKAWA_CGCS_SOURCE,
        matrix.NORMALIZED_YUKAWA_CGCS_TEST,
        matrix.NORMALIZED_YUKAWA_CGCS_MD,
        matrix.ARTIFACTS["physical_sm_vacuum"],
        matrix.PHYSICAL_SM_VACUUM_SOURCE,
        matrix.PHYSICAL_SM_VACUUM_TEST,
        matrix.PHYSICAL_SM_VACUUM_MD,
        matrix.ARTIFACTS["physical_sm_source_equality"],
        matrix.PHYSICAL_SM_SOURCE_EQUALITY_SOURCE,
        matrix.PHYSICAL_SM_SOURCE_EQUALITY_TEST,
        matrix.PHYSICAL_SM_SOURCE_EQUALITY_MD,
        matrix.ARTIFACTS["physical_sm_five_amplitude_equality"],
        matrix.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_SOURCE,
        matrix.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_TEST,
        matrix.PHYSICAL_SM_FIVE_AMPLITUDE_EQUALITY_MD,
        matrix.ARTIFACTS["physical_sm_hard_projector_hessians"],
        matrix.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_SOURCE,
        matrix.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_TEST,
        matrix.PHYSICAL_SM_HARD_PROJECTOR_HESSIANS_MD,
        matrix.ARTIFACTS["physical_sm_last_six_hessians"],
        matrix.PHYSICAL_SM_LAST_SIX_HESSIANS_SOURCE,
        matrix.PHYSICAL_SM_LAST_SIX_HESSIANS_TEST,
        matrix.PHYSICAL_SM_LAST_SIX_HESSIANS_MD,
        matrix.ARTIFACTS["physical_sm_37_row_aggregate"],
        matrix.PHYSICAL_SM_37_ROW_AGGREGATE_SOURCE,
        matrix.PHYSICAL_SM_37_ROW_AGGREGATE_TEST,
        matrix.PHYSICAL_SM_37_ROW_AGGREGATE_MD,
        matrix.ARTIFACTS["physical_sm_local_equality_orbit"],
        matrix.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_SOURCE,
        matrix.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_TEST,
        matrix.PHYSICAL_SM_LOCAL_EQUALITY_ORBIT_MD,
        "G1_EXACT_DECLARED_SYMMETRY_CHARACTER_CENSUS_V20.json",
        "GAUGED_U1X_SCALAR_CONTRACT_V20.json",
        "exact_gauged_u1x_physical_quotient_v20.py",
        "exact_mixed_45_triplet_channel_v20.py",
        "exact_phi2_hdagh_channel_family_v20.py",
        "exact_physical_sm_easy_21_hessians_v20.py",
        "EXACT_PHYSICAL_SM_EASY_21_HESSIANS_V20.json",
        "live_g2_canonical_486_field_chart_v20.py",
        "live_g2_exact_hsigma_hermitian_derivatives_v20.py",
        "live_g2_exact_phi2_hdagh_derivatives_v20.py",
        "live_g2_exact_remaining_cubic_derivatives_v20.py",
        matrix.ARTIFACTS["physical_sm_g4_g5_branch_mismatch"],
        matrix.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_SOURCE,
        matrix.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_TEST,
        matrix.PHYSICAL_SM_G4_G5_BRANCH_MISMATCH_MD,
        matrix.ARTIFACTS["physical_sm_heavy_vectors"],
        matrix.PHYSICAL_SM_HEAVY_VECTOR_SOURCE,
        matrix.PHYSICAL_SM_HEAVY_VECTOR_TEST,
        matrix.PHYSICAL_SM_HEAVY_VECTOR_MD,
        matrix.ARTIFACTS["physical_sm_heavy_vector_msbar"],
        matrix.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_SOURCE,
        matrix.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_TEST,
        matrix.PHYSICAL_SM_HEAVY_VECTOR_MSBAR_MD,
        matrix.ARTIFACTS["physical_sm_vector_rxi"],
        matrix.PHYSICAL_SM_VECTOR_RXI_SOURCE,
        matrix.PHYSICAL_SM_VECTOR_RXI_TEST,
        matrix.PHYSICAL_SM_VECTOR_RXI_MD,
        matrix.ARTIFACTS["conditional_physical_sm_scalar_spectrum"],
        matrix.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_SOURCE,
        matrix.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_TEST,
        matrix.CONDITIONAL_PHYSICAL_SM_SCALAR_SPECTRUM_MD,
        matrix.ARTIFACTS["physical_sm_g6_g7_closure_frontier"],
        matrix.PHYSICAL_SM_G6_G7_FRONTIER_SOURCE,
        matrix.PHYSICAL_SM_G6_G7_FRONTIER_TEST,
        matrix.PHYSICAL_SM_G6_G7_FRONTIER_MD,
        matrix.ARTIFACTS["physical_sm_g8_identifiability_frontier"],
        matrix.PHYSICAL_SM_G8_FRONTIER_SOURCE,
        matrix.PHYSICAL_SM_G8_FRONTIER_TEST,
        matrix.PHYSICAL_SM_G8_FRONTIER_MD,
    ):
        root.joinpath(name).write_bytes(matrix.ROOT.joinpath(name).read_bytes())
    g2_mathematical_closure = (
        matrix.gate_ledger._renormalizable_g2_mathematical_closure(
            json.loads(
                root.joinpath(g2_mathematical_artifact).read_text(encoding="utf-8")
            ),
            raw_sha256=matrix.gate_ledger._raw_file_sha256(
                root / g2_mathematical_artifact
            ),
            source_raw_sha256=matrix.gate_ledger._raw_file_sha256(
                root / matrix.RENORMALIZABLE_G2_MATHEMATICAL_SOURCE
            ),
        )
    )
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
                "present": contract_consistent,
                "valid": contract_consistent,
                "fresh_for_exact_model_bytes": contract_consistent,
                "checks": {
                    name: contract_consistent
                    for name in matrix.gate_ledger.EXPECTED_EXACT_X_V3_EXTERNAL_CHECKS
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
            # This is the scalar-contract module's pre-G2-audit snapshot. The
            # dedicated G2 artifact below is the source-authoritative aggregate.
            "flags": {"G2_gauged_u1x_derivatives_certified": False},
        },
    )
    write_json(
        root,
        "G1_G8_GATE_LEDGER_V20.json",
        {
            "renormalizable_G1_component_tensor_closure": (
                g1_component_tensor_closure
            ),
            "renormalizable_G2_mathematical_closure": g2_mathematical_closure,
            "gates": {
                "G1": {
                    "status": "CLOSED" if contract_consistent else "BLOCKED",
                    "scoped_calculation_complete": True,
                    "full_gate_calculation_complete": True,
                },
                "G2": {
                    "status": "CLOSED" if contract_consistent else "BLOCKED",
                    "scoped_calculation_complete": True,
                    "full_gate_calculation_complete": True,
                },
                "G3": {"status": "OPEN" if contract_consistent else "BLOCKED"},
                "G4": {"status": "BLOCKED"},
                "G5": {"status": "CLOSED" if contract_consistent else "BLOCKED"},
                "G6": {"status": "BLOCKED"},
            },
            "gauged_u1x_scalar_subtheorems": {
                "G1": {
                    "scoped_status": (
                        "COMPLETE_GAUGED_U1X_FULL_COMPONENT_TENSOR_INTEGRATION"
                    ),
                    "multiplicity_census_complete": True,
                    "explicit_component_tensor_subset_integration_complete": True,
                    "mathematical_component_tensor_closure_complete": True,
                    "full_G1_closed": True,
                    "renormalizable_G1_component_tensor_closure": (
                        g1_component_tensor_closure
                    ),
                },
                "G2": {
                    "scoped_derivative_audit_complete": True,
                    "full_renormalizable_G2_mathematical_potential_closed": True,
                },
            },
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
                "EXACT_GLOBAL_EQUALITY_CLASSIFICATION__"
                "SIGNED_PHI_THEOREM_CLOSED__G3_OPEN"
            ),
            "overall_state": "GLOBAL_EQUALITY_ORBITS_CLOSED",
            "n_failed": 0,
            "scope": {
                "fixed_F_Sigma_global_equality_classified": True,
                "fixed_Delta_diagonal_Phi_global_equality_classified": True,
                "fixed_Delta_two_tau_plus_representatives_equivalent": True,
                "literal_single_Phi_orbit_statement_refuted": True,
                "minus_F_mixed_branch_excluded_exact": True,
                "corrected_signed_Phi_orbit_theorem_open": False,
                "corrected_signed_Phi_orbit_theorem_proved": True,
                "complete_SU3_fixed_Phi_slice_classified_exactly": True,
                "distant_disconnected_Phi_components_excluded": True,
                "all_arbitrary_Phi_global_equalities_classified": True,
                "global_equality_orbit_classification_complete": True,
                "quantitative_beta_global_coercivity_proved": False,
                "G3_closed": False,
            },
            "remaining_global_lemma": {
                "proved": True,
                "literal_single_orbit_version_refuted": True,
                "corrected_signed_two_orbit_version": True,
                "complete_SU3_fixed_slice_classified_exactly": True,
                "SU3_fixed_slice_real_dimension": 16,
                "source_bound_certificate_available": True,
                "source_bound_partial_certificate_available": True,
                "quantitative_orbit_distance_bound_proved": False,
                "numerical_search_is_not_a_substitute": True,
            },
            "Phi_global_signed_zero_theorem": {
                "frozen_source_sha256": (
                    "17038c6fb82ba565a16228f5f5c03026f0ab8e3ad7959792498c2785b9653066"
                ),
                "core_sha256": (
                    "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc"
                ),
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
            "status": "GLOBAL_GAP_REDUCED_TO_QUANTITATIVE_COERCIVITY",
            "overall_state": "FINAL_G3_TEST_OPEN",
            "n_failed": 0,
            "flags": {
                "lower_witness_found": False,
                "conditional_small_positive_beta_route_exists": True,
                "beta_1_over_20_global_minimum_certified": False,
                "PD_equality_orbits_classified": True,
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
    for filename in (
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_PUBLICATION_V21_MANIFEST.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_FIXED_ENDPOINT_THEOREM_V21.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_SOURCE_RECONSTRUCTION_V21.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_POSITIVE_GRAM_VERIFY_V21.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_LIVE_POLYNOMIAL_V21.json",
        "EXACT_GAUGED_U1X_G3_RANK1_SU4_CORRECTED_ORDERED_SPECTRAL_OVERFLOW_V21.json",
    ):
        relative = f"corrected_rank1_publication_v21/{filename}"
        write_json(
            root,
            relative,
            json.loads(
                (matrix.ROOT / relative).read_text(encoding="utf-8")
            ),
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
    root.joinpath("FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json").write_bytes(
        (matrix.ROOT / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json").read_bytes()
    )
    for filename in (
        "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json",
        "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json",
        "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
    ):
        root.joinpath(filename).write_bytes((matrix.ROOT / filename).read_bytes())
    root.joinpath(matrix.FINAL_G6_EFT_GATE_SOURCE).write_bytes(
        (matrix.ROOT / matrix.FINAL_G6_EFT_GATE_SOURCE).read_bytes()
    )
    for artifact_key, source_name in (
        ("g6_sm_provenance", matrix.G6_SM_PROVENANCE_SOURCE),
        ("g6_g7_parameterized_matching", matrix.G6_G7_PARAMETERIZED_MATCHING_SOURCE),
        ("authoritative_gauge_betas", matrix.AUTHORITATIVE_GAUGE_BETAS_SOURCE),
        ("pyrate3_gauge_replay", matrix.PYRATE3_GAUGE_REPLAY_SOURCE),
    ):
        artifact_name = matrix.ARTIFACTS[artifact_key]
        root.joinpath(artifact_name).write_bytes(
            (matrix.ROOT / artifact_name).read_bytes()
        )
        root.joinpath(source_name).write_bytes(
            (matrix.ROOT / source_name).read_bytes()
        )
    for relative in (
        "models/SO10U1XGaugeAuditV20.model",
        "data/PYRATE3_SO10_U1X_GAUGE_BETA_FROZEN_V20.json",
    ):
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((matrix.ROOT / relative).read_bytes())
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
    def test_canonical_authority_requires_trusted_verifiers_and_ignores_legacy_rows(self):
        canonical = matrix.canonical_gates.build_report()
        authoritative = json.loads(
            (matrix.ROOT / matrix.ARTIFACTS["authoritative"]).read_text(
                encoding="utf-8"
            )
        )
        gate = matrix._canonical_authority_gate(canonical, authoritative)
        self.assertEqual(gate["state"], "BLOCKED")
        self.assertFalse(gate["evidence"]["all_canonical_gates_closed"])
        self.assertFalse(
            gate["evidence"]["legacy_ledger_controls_authoritative_closure"]
        )
        self.assertTrue(canonical["gates"][0]["evidence_state"]["valid"])
        self.assertTrue(canonical["gates"][1]["evidence_state"]["valid"])
        self.assertTrue(canonical["gates"][2]["evidence_state"]["valid"])
        self.assertTrue(canonical["gates"][2]["closed"])
        self.assertTrue(
            all(
                "trusted_verifier" in row
                and row["evidence_state"].get("valid") is False
                for row in canonical["gates"][3:]
            )
        )

    def test_temporary_fixture_discovery_does_not_leak_test_modules(self):
        transient_name = (
            "test_conditional_physical_sm_eft_hessian_spectrum_v20"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            self.assertNotIn(transient_name, sys.modules)
            report = matrix.build_report(root)
            self.assertEqual(report["status"], "PASS")
            self.assertNotIn(transient_name, sys.modules)

    def test_renormalizable_g1_theorem_is_math_closed_but_release_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=False)
            report = matrix.build_report(root)
            theorem = report["renormalizable_G1_component_tensor_closure"]

            self.assertTrue(theorem["source_bound"])
            self.assertEqual(
                theorem["core_sha256"],
                matrix.gate_ledger.RENORMALIZABLE_G1_COMPONENT_TENSOR_CORE_SHA256,
            )
            self.assertEqual(
                theorem["raw_sha256"],
                matrix.gate_ledger.RENORMALIZABLE_G1_COMPONENT_TENSOR_RAW_SHA256,
            )
            self.assertEqual(
                theorem["source_raw_sha256"],
                matrix.gate_ledger.RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE_RAW_SHA256,
            )
            self.assertEqual(
                theorem["direction_map_sha256"],
                matrix.gate_ledger.RENORMALIZABLE_G1_DIRECTION_MAP_SHA256,
            )
            self.assertTrue(
                theorem["mathematical_G1_closed_for_renormalizable_model"]
            )
            self.assertFalse(theorem["authoritative_G1_promoted_closed"])
            self.assertFalse(theorem["release_G1_verified"])
            self.assertFalse(theorem["renormalizable_model_mutated"])
            self.assertFalse(theorem["new_physics_required_for_G1"])
            self.assertTrue(theorem["downstream_integration_completed"])
            self.assertIn(
                matrix.gate_ledger.CONTRACT_BLOCKER,
                theorem["release_blockers"],
            )
            self.assertNotIn(
                "G1_COMPONENT_TENSOR_CLOSURE_DOWNSTREAM_INTEGRATION_REQUIRED",
                theorem["release_blockers"],
            )
            self.assertTrue(
                report[
                    "renormalizable_G1_component_tensor_closure_matches_ledger"
                ]
            )

            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(states["authoritative_model_contract"], "BLOCKED")
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            evidence = vacuum["evidence"]
            self.assertFalse(evidence["authoritative_G1_closed"])
            self.assertFalse(evidence["authoritative_G2_closed"])
            self.assertTrue(
                evidence["renormalizable_G1_component_tensor_theorem_source_bound"]
            )
            self.assertTrue(
                evidence["renormalizable_G1_component_tensor_theorem_matches_ledger"]
            )
            self.assertTrue(evidence["renormalizable_mathematical_G1_closed"])
            self.assertTrue(
                evidence["gauged_G1_full_component_tensor_integration_complete"]
            )
            self.assertFalse(
                evidence["renormalizable_G1_authoritative_promotion_closed"]
            )
            self.assertFalse(evidence["renormalizable_G1_release_verified"])
            self.assertTrue(
                evidence["renormalizable_G1_downstream_integration_completed"]
            )
            self.assertTrue(
                evidence["renormalizable_G1_external_SARAH_blocker_preserved"]
            )

    def test_renormalizable_g1_theorem_rejects_artifact_or_source_byte_drift(self):
        for relative in (
            matrix.ARTIFACTS["renormalizable_g1_component_tensor"],
            matrix.RENORMALIZABLE_G1_COMPONENT_TENSOR_SOURCE,
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                minimal_tree(root, contract_consistent=False)
                path = root / relative
                path.write_bytes(path.read_bytes() + b"\n")
                report = matrix.build_report(root)
                theorem = report["renormalizable_G1_component_tensor_closure"]
                self.assertFalse(theorem["source_bound"])
                self.assertFalse(
                    theorem[
                        "mathematical_G1_closed_for_renormalizable_model"
                    ]
                )
                self.assertFalse(
                    report[
                        "renormalizable_G1_component_tensor_closure_matches_ledger"
                    ]
                )

    def test_renormalizable_g1_theorem_requires_exact_ledger_view(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=False)
            ledger_path = root / "G1_G8_GATE_LEDGER_V20.json"
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            ledger["renormalizable_G1_component_tensor_closure"][
                "direction_map_sha256"
            ] = "0" * 64
            write_json(root, ledger_path.name, ledger)

            report = matrix.build_report(root)
            theorem = report["renormalizable_G1_component_tensor_closure"]
            self.assertTrue(theorem["source_bound"])
            self.assertTrue(
                theorem["mathematical_G1_closed_for_renormalizable_model"]
            )
            self.assertFalse(
                report[
                    "renormalizable_G1_component_tensor_closure_matches_ledger"
                ]
            )
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                vacuum["evidence"]["renormalizable_mathematical_G1_closed"]
            )

    def test_parallel_eft_g3_is_math_pass_release_open_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            parallel = report["parallel_EFT_G3_acceptance"]
            self.assertTrue(parallel["source_bound"])
            self.assertEqual(
                parallel["core_sha256"],
                matrix.gate_ledger.FINAL_G3_EFT_ACCEPTANCE_CORE_SHA256,
            )
            self.assertEqual(
                parallel["raw_sha256"],
                matrix.gate_ledger.FINAL_G3_EFT_ACCEPTANCE_RAW_SHA256,
            )
            self.assertTrue(parallel["checks"]["raw_sha256_exact"])
            self.assertTrue(parallel["mathematical_G3_closed_for_EFT_model"])
            self.assertFalse(parallel["release_G3_verified_for_EFT_model"])
            self.assertFalse(
                parallel[
                    "mathematical_G3_closed_for_original_renormalizable_model"
                ]
            )
            self.assertFalse(parallel["renormalizable_gate_mutated"])
            self.assertFalse(parallel["G4_closed"])
            self.assertFalse(report["full_theory_validated"])

            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            evidence = vacuum["evidence"]
            self.assertTrue(
                evidence["parallel_EFT_G3_acceptance_gate_artifact_present"]
            )
            self.assertTrue(evidence["parallel_EFT_G3_acceptance_source_bound"])
            self.assertTrue(
                evidence["parallel_EFT_G3_acceptance_raw_sha256_exact"]
            )
            self.assertTrue(evidence["parallel_EFT_mathematical_G3_closed"])
            self.assertFalse(evidence["parallel_EFT_release_G3_verified"])
            self.assertFalse(
                evidence["original_renormalizable_mathematical_G3_closed"]
            )
            self.assertTrue(evidence["parallel_EFT_G4_closed"])
            self.assertTrue(evidence["final_G3_acceptance_gate_honestly_open"])

    def test_parallel_eft_g4_g5_g6_are_math_pass_release_open_and_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root, contract_consistent=False)
            report = matrix.build_report(root)
            g4 = report["parallel_EFT_G4_mathematical"]
            g5 = report["parallel_EFT_G5_mathematical"]
            g6 = report["parallel_EFT_G6_spectrum"]
            self.assertTrue(g4["source_bound"])
            self.assertEqual(
                g4["core_sha256"],
                matrix.gate_ledger.FINAL_G4_EFT_MATHEMATICAL_CORE_SHA256,
            )
            self.assertEqual(
                g4["raw_sha256"],
                matrix.gate_ledger.FINAL_G4_EFT_MATHEMATICAL_RAW_SHA256,
            )
            self.assertTrue(g4["mathematical_G4_closed_for_EFT_model"])
            self.assertFalse(g4["release_G4_verified_for_EFT_model"])
            self.assertFalse(
                g4["mathematical_G4_closed_for_original_renormalizable_model"]
            )
            self.assertTrue(g4["checks"]["parallel_integration_completed"])
            self.assertNotIn(
                "parallel_EFT_G4_integrated_into_release_orchestrators",
                g4["release_blockers"],
            )
            self.assertTrue(g5["source_bound"])
            self.assertEqual(
                g5["core_sha256"],
                matrix.gate_ledger.FINAL_G5_EFT_MATHEMATICAL_CORE_SHA256,
            )
            self.assertEqual(
                g5["raw_sha256"],
                matrix.gate_ledger.FINAL_G5_EFT_MATHEMATICAL_RAW_SHA256,
            )
            self.assertTrue(g5["mathematical_G5_closed_for_EFT_model"])
            self.assertFalse(g5["release_G5_verified_for_EFT_model"])
            self.assertFalse(g5["authoritative_renormalizable_G5_closed"])
            self.assertTrue(g5["checks"]["parallel_integration_completed"])
            self.assertNotIn(
                "downstream_parallel_G5_integration_completed",
                g5["release_blockers"],
            )
            self.assertTrue(g6["source_bound"])
            self.assertEqual(
                g6["core_sha256"],
                matrix.gate_ledger.FINAL_G6_EFT_MATHEMATICAL_CORE_SHA256,
            )
            self.assertEqual(
                g6["raw_sha256"],
                matrix.gate_ledger.FINAL_G6_EFT_MATHEMATICAL_RAW_SHA256,
            )
            self.assertTrue(g6["formal_SU3_x_U1_89_tree_factorization_closed"])
            self.assertFalse(g6["mathematical_G6_closed_for_EFT_model"])
            self.assertFalse(g6["release_G6_verified_for_EFT_model"])
            self.assertFalse(g6["authoritative_renormalizable_G6_closed"])
            self.assertFalse(g6["authoritative_G6_gate_mutated"])
            self.assertFalse(g6["whole_model_validated"])
            self.assertEqual(g6["spectrum_summary"]["ambient_real_fields"], 486)
            self.assertEqual(
                g6["spectrum_summary"]["gauge_quotient_dimension"], 449
            )
            self.assertEqual(g6["spectrum_summary"]["ungauged_PQ_zero_modes"], 1)
            self.assertEqual(g6["spectrum_summary"]["positive_massive_modes"], 448)

            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            evidence = vacuum["evidence"]
            self.assertTrue(evidence["parallel_EFT_G4_closed"])
            self.assertFalse(evidence["parallel_EFT_release_G4_verified"])
            self.assertTrue(evidence["parallel_EFT_G4_integration_completed"])
            self.assertTrue(
                evidence["parallel_EFT_G4_integration_blocker_removed"]
            )
            self.assertTrue(evidence["parallel_EFT_G5_closed"])
            self.assertFalse(evidence["parallel_EFT_release_G5_verified"])
            self.assertTrue(evidence["parallel_EFT_G5_integration_completed"])
            self.assertTrue(
                evidence["parallel_EFT_G5_integration_blocker_removed"]
            )
            self.assertTrue(evidence["parallel_EFT_G6_spectrum_source_bound"])
            self.assertTrue(evidence["parallel_EFT_G6_spectrum_raw_sha256_exact"])
            self.assertTrue(
                evidence["parallel_EFT_G6_gate_source_raw_sha256_exact"]
            )
            self.assertTrue(evidence["parallel_EFT_G6_spectrum_core_sha256_exact"])
            self.assertTrue(evidence["parallel_EFT_G6_spectrum_dependency_pins_exact"])
            self.assertTrue(evidence["parallel_EFT_G6_integration_completed"])
            self.assertTrue(
                evidence["parallel_EFT_G6_integration_blocker_removed"]
            )
            self.assertFalse(evidence["parallel_EFT_mathematical_G6_closed"])
            self.assertTrue(
                evidence[
                    "parallel_EFT_formal_SU3_x_U1_89_factorization_closed"
                ]
            )
            self.assertFalse(evidence["parallel_EFT_release_G6_verified"])
            self.assertFalse(
                evidence["original_renormalizable_mathematical_G6_closed"]
            )
            self.assertFalse(
                evidence["authoritative_G6_gate_mutated_by_parallel_EFT"]
            )
            self.assertEqual(
                evidence["parallel_EFT_G6_spectrum_summary"][
                    "positive_massive_modes"
                ],
                448,
            )
            self.assertEqual(
                evidence["authoritative_renormalizable_G3_G4_G5_statuses"],
                {"G3": "BLOCKED", "G4": "BLOCKED", "G5": "BLOCKED"},
            )
            self.assertEqual(
                evidence[
                    "authoritative_renormalizable_G3_G4_G5_G6_statuses"
                ],
                {
                    "G3": "BLOCKED",
                    "G4": "BLOCKED",
                    "G5": "BLOCKED",
                    "G6": "BLOCKED",
                },
            )

            for filename, key in (
                (
                    "FINAL_G4_EFT_MATHEMATICAL_GATE_V20.json",
                    "parallel_EFT_G4_mathematical",
                ),
                (
                    "FINAL_G5_EFT_MATHEMATICAL_GATE_V20.json",
                    "parallel_EFT_G5_mathematical",
                ),
                (
                    "FINAL_G6_EFT_MATHEMATICAL_GATE_V20.json",
                    "parallel_EFT_G6_spectrum",
                ),
            ):
                with self.subTest(filename=filename):
                    artifact = root / filename
                    original = artifact.read_bytes()
                    artifact.write_bytes(original + b"\n")
                    forged = matrix.build_report(root)[key]
                    self.assertFalse(forged["source_bound"])
                    self.assertFalse(forged["checks"]["raw_sha256_exact"])
                    artifact.write_bytes(original)

    def test_parallel_eft_g3_rejects_raw_byte_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / "FINAL_G3_EFT_ACCEPTANCE_GATE_V20.json"
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            report = matrix.build_report(root)
            parallel = report["parallel_EFT_G3_acceptance"]
            self.assertFalse(parallel["source_bound"])
            self.assertFalse(parallel["checks"]["raw_sha256_exact"])
            self.assertFalse(parallel["mathematical_G3_closed_for_EFT_model"])
            self.assertFalse(report["full_theory_validated"])

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
                evidence[
                    "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
                ]
            )
            self.assertFalse(
                evidence["gauged_G3_rank1_SU4_legacy_v20_physical_target_valid"]
            )
            self.assertFalse(
                evidence["gauged_G3_rank1_SU4_legacy_v20_primal_valid"]
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
                evidence[
                    "gauged_G3_rank1_SU4_corrected_fixed_endpoint_theorem_exact"
                ]
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_corrected_positive_Gram_map_shape"],
                [6_585, 19_594],
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_corrected_positive_Gram_map_common_denominator"
                ],
                256,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_corrected_physical_target_common_denominator"
                ],
                576_000,
            )
            self.assertEqual(
                evidence[
                    "gauged_G3_rank1_SU4_corrected_exact_coefficient_equalities"
                ],
                6_585,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_corrected_strict_positive_Gram_blocks"],
                22,
            )
            self.assertEqual(
                evidence["gauged_G3_rank1_SU4_corrected_strict_positive_LDL_pivots"],
                824,
            )
            self.assertTrue(
                evidence[
                    "gauged_G3_rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"
                ]
            )
            self.assertFalse(
                evidence["gauged_G3_rank1_SU4_corrected_global_Sigma_proved"]
            )
            self.assertFalse(evidence["gauged_G3_rank1_SU4_corrected_G3_closed"])
            self.assertIn("478x1414 integer map", vacuum["summary"])
            self.assertIn("kernel dimension 936", vacuum["summary"])
            self.assertIn(
                "reserved zero placeholder is nonphysical", vacuum["summary"]
            )
            self.assertIn(
                "exact-rank-6057, 6057x18085 integer map", vacuum["summary"]
            )
            self.assertIn("kernel dimension 12028", vacuum["summary"])
            self.assertIn(
                "legacy v20 assembled physical target is rejected",
                vacuum["summary"],
            )
            self.assertIn("corrected 6585x19594", vacuum["summary"])
            self.assertIn("strict 22-block/824-pivot primal", vacuum["summary"])
            self.assertIn("every real Phi210", vacuum["summary"])
            self.assertIn(
                "For that historical fixed-H/Sigma frontier, global Sigma, "
                "general/full H, and its then-unassembled Hessian remained open",
                vacuum["summary"],
            )
            self.assertIn(
                "source-derived all-37 Hessian is exactly stationary",
                vacuum["summary"],
            )
            self.assertNotIn(
                "the full Hessian, and G3 remain open", vacuum["summary"]
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
                            "gauged_G3_rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
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
                "CANONICAL_G1_G8_GATES_OPEN",
            )
            self.assertFalse(report["full_theory_validated"])
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(states["proton_decay"], "BLOCKED")
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
                "BLOCKED",
            )
            rge_gate = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "two_loop_RGE_unification_and_thresholds"
            )
            evidence = rge_gate["evidence"]
            self.assertTrue(
                evidence[
                    "formal_U1_89_abstract_restriction_noninjectivity_proved"
                ]
            )
            self.assertFalse(
                evidence["exact_physical_EFT_G7_input_nonidentifiability_proved"]
            )
            self.assertFalse(
                evidence["historical_electroweak_lift_interpretation_valid"]
            )
            self.assertTrue(evidence["formal_U1_89_restriction_map_noninjective"])
            self.assertTrue(evidence["absolute_matching_scale_unidentified"])
            self.assertFalse(evidence["mathematical_G7_closed"])
            self.assertFalse(evidence["positive_G7_certified"])
            self.assertFalse(evidence["negative_G7_no_go_certified"])
            self.assertFalse(evidence["release_G7_verified"])
            self.assertFalse(evidence["authoritative_renormalizable_G7_closed"])
            self.assertTrue(evidence["physical_PS_SM_matter_branching_closed"])
            self.assertTrue(
                evidence["parameterized_one_loop_matter_threshold_kernel_closed"]
            )
            self.assertTrue(evidence["normalized_SO10_10_CGCs_closed"])
            self.assertTrue(evidence["normalized_SO10_126bar_CGCs_closed"])
            self.assertTrue(
                evidence["canonical_304_Weyl_sparse_Yukawa_embedding_closed"]
            )
            self.assertFalse(evidence["flavor_boundary_values_closed"])
            self.assertFalse(evidence["SARAH_Dot_conversion_closed"])
            self.assertFalse(evidence["full_one_two_loop_Yukawa_betas_closed"])
            self.assertFalse(evidence["physical_component_pole_mass_matrices_closed"])
            self.assertTrue(
                evidence["exact_parameterized_heavy_vector_tree_mass_matrix_closed"]
            )
            self.assertTrue(
                evidence["exact_heavy_vector_physical_target_provenance_closed"]
            )
            self.assertTrue(
                evidence[
                    "exact_heavy_vector_rank_kernel_and_sector_resolution_closed"
                ]
            )
            self.assertTrue(
                evidence["parameterized_heavy_vector_threshold_log_inputs_closed"]
            )
            self.assertTrue(
                evidence[
                    "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
                ]
            )
            self.assertTrue(evidence["finite_MSbar_vector_constant_closed"])
            self.assertTrue(
                evidence["exact_heavy_vector_SU3_and_QED_group_factors_closed"]
            )
            self.assertTrue(
                evidence["heavy_vector_Goldstone_double_count_guard_active"]
            )
            self.assertTrue(
                evidence[
                    "zero_background_Rxi_vacuum_determinant_cancellation_closed"
                ]
            )
            self.assertTrue(
                evidence["all_37_broken_vector_directions_Rxi_cancelled"]
            )
            self.assertFalse(
                evidence[
                    "background_covariant_general_field_Rxi_determinants_closed"
                ]
            )
            self.assertFalse(
                evidence["background_covariant_heat_kernel_replay_closed"]
            )
            self.assertTrue(
                evidence["conditional_reconstructed_tree_scalar_spectrum_closed"]
            )
            self.assertTrue(
                evidence["continuous_G6_G7_nonidentifiability_frontier_closed"]
            )
            self.assertTrue(
                evidence["G6_G7_minimal_closure_path_machine_readable"]
            )
            self.assertTrue(evidence["recalculated_scoped_G7_input_resolution_bound"])
            self.assertTrue(evidence["stale_normalized_embedding_blocker_superseded"])
            self.assertTrue(
                evidence["stale_unmatched_heavy_vector_provenance_blocker_superseded"]
            )
            self.assertFalse(
                evidence[
                    "background_covariant_general_field_Rxi_determinants_closed"
                ]
            )
            self.assertFalse(
                evidence[
                    "stationary_SM_symmetric_pre_EW_heavy_vector_matching_closed"
                ]
            )
            self.assertFalse(
                evidence["complete_scalar_and_fermion_threshold_matching_closed"]
            )
            self.assertFalse(evidence["physical_vector_pole_masses_closed"])
            self.assertFalse(evidence["physical_scalar_pole_masses_closed"])
            self.assertFalse(
                evidence[
                    "legacy_quartic_soft_and_heuristic_RGE_threshold_sources_authoritative"
                ]
            )

    def test_physical_sm_source_equality_frontier_is_strict_and_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            frontier = report["physical_SM_source_algebra_equality_frontier"]

            self.assertTrue(frontier["source_bound"])
            self.assertTrue(all(frontier["checks"].values()))
            self.assertEqual(frontier["radial_gcd"], "t - 1")
            self.assertTrue(
                frontier["radial_stationary_equality_classified_exactly"]
            )
            self.assertEqual(frontier["observed_source_Hessian_row_lcm"], 126000)
            self.assertEqual(
                frontier["reconstructed_aggregate_Hessian_lcm"],
                6300103327590,
            )
            self.assertFalse(
                frontier["direct_source_algebra_stationary_Hessian_available"]
            )
            self.assertFalse(
                frontier["complete_nonradial_equality_orbit_proved"]
            )
            self.assertFalse(frontier["old_formal_U1_89_EFT_scope_promoted"])
            for gate in ("G3", "G4", "G5"):
                self.assertFalse(frontier[f"physical_SM_{gate}_closed"])

            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            evidence = vacuum["evidence"]
            self.assertTrue(
                evidence[
                    "physical_SM_radial_stationary_equality_classified_exactly"
                ]
            )
            self.assertEqual(
                evidence["physical_SM_radial_stationary_equality_gcd"],
                "t - 1",
            )
            self.assertFalse(
                evidence["physical_SM_complete_nonradial_equality_orbit_closed"]
            )
            self.assertTrue(evidence["physical_SM_source_algebra_Hessian_closed"])
            self.assertEqual(
                evidence["physical_SM_exact_source_Hessian_rows_closed"], 37
            )
            self.assertEqual(evidence["physical_SM_remaining_active_Hessian_rows"], 0)

            source = root / matrix.PHYSICAL_SM_SOURCE_EQUALITY_SOURCE
            source.write_bytes(source.read_bytes() + b"\n")
            forged = matrix.build_report(root)
            forged_frontier = forged[
                "physical_SM_source_algebra_equality_frontier"
            ]
            self.assertFalse(forged_frontier["source_bound"])
            self.assertFalse(
                forged_frontier["checks"]["core_and_all_four_raw_pins_exact"]
            )
            self.assertIsNone(forged_frontier["radial_gcd"])
            forged_vacuum = next(
                gate
                for gate in forged["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                forged_vacuum["evidence"][
                    "physical_SM_radial_stationary_equality_classified_exactly"
                ]
            )

    def test_physical_sm_five_amplitude_equality_is_strict_and_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            scoped = report["physical_SM_five_amplitude_equality_contract"]
            self.assertTrue(scoped["source_bound"])
            self.assertTrue(all(scoped["checks"].values()))
            self.assertTrue(scoped["exact_radial_theorem_strictly_extended"])
            self.assertTrue(
                scoped[
                    "five_real_amplitude_slice_stationary_equality_classified"
                ]
            )
            self.assertEqual(scoped["exact_real_discrete_sign_variant_count"], 16)
            self.assertTrue(
                scoped["target_strict_minimum_on_five_amplitude_slice"]
            )
            self.assertFalse(
                scoped["full_486_field_stationary_equality_classified"]
            )
            self.assertFalse(
                scoped[
                    "continuous_symmetry_orbit_equivalence_of_16_variants_proved"
                ]
            )
            for gate in ("G3", "G4", "G5"):
                self.assertFalse(scoped[f"physical_SM_{gate}_closed"])

            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            evidence = vacuum["evidence"]
            self.assertTrue(
                evidence["physical_SM_five_amplitude_equality_source_bound"]
            )
            self.assertTrue(
                evidence[
                    "physical_SM_five_amplitude_slice_stationary_equality_classified"
                ]
            )
            self.assertEqual(
                evidence["physical_SM_five_amplitude_exact_sign_variant_count"],
                16,
            )
            self.assertTrue(
                evidence[
                    "physical_SM_five_amplitude_variants_one_continuous_orbit_proved"
                ]
            )
            self.assertFalse(
                evidence[
                    "physical_SM_complete_global_486_field_stationary_equality_classified"
                ]
            )

            artifact = root / matrix.ARTIFACTS[
                "physical_sm_five_amplitude_equality"
            ]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            forged = matrix.build_report(root)
            forged_scoped = forged[
                "physical_SM_five_amplitude_equality_contract"
            ]
            self.assertFalse(forged_scoped["source_bound"])
            forged_vacuum = next(
                gate
                for gate in forged["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                forged_vacuum["evidence"][
                    "physical_SM_five_amplitude_equality_source_bound"
                ]
            )

    def test_hard_projector_hessians_are_bound_without_closing_full_G3_G5(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            scoped = report["physical_SM_hard_projector_Hessians_contract"]
            self.assertTrue(scoped["source_bound"])
            self.assertTrue(all(scoped["checks"].values()))
            self.assertEqual(scoped["exact_source_Hessian_row_count"], 10)
            self.assertEqual(scoped["remaining_active_row_count"], 27)
            self.assertTrue(scoped["all_10_O27_O44_source_Hessians_closed"])
            self.assertFalse(scoped["all_37_active_source_Hessians_closed"])
            self.assertFalse(scoped["full_witness_stationarity_rank_PSD_closed"])
            for gate in ("G3", "G4", "G5"):
                self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            vacuum = next(
                gate for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertTrue(
                vacuum["evidence"][
                    "physical_SM_hard_projector_Hessians_source_bound"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "physical_SM_all_37_active_source_Hessians_closed"
                ]
            )

            artifact = root / matrix.ARTIFACTS[
                "physical_sm_hard_projector_hessians"
            ]
            forged = json.loads(artifact.read_text(encoding="utf-8"))
            forged["claims"][
                "exact_source_algebra_Hessians_for_all_37_active_witness_rows"
            ] = True
            write_json(root, artifact.name, forged)
            rejected = matrix.build_report(root)
            self.assertFalse(
                rejected["physical_SM_hard_projector_Hessians_contract"][
                    "source_bound"
                ]
            )

    def test_branch_mismatch_is_bound_but_never_promoted_to_global_no_go(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            scoped = report["physical_SM_G4_G5_branch_mismatch_contract"]
            self.assertTrue(scoped["source_bound"])
            self.assertTrue(all(scoped["checks"].values()))
            self.assertTrue(scoped["exact_branch_mismatch_proved"])
            self.assertEqual(scoped["unit_rescaling_case_count"], 101)
            self.assertFalse(
                scoped[
                    "current_five_amplitude_target_is_canonical_physical_EW_branch"
                ]
            )
            self.assertFalse(scoped["global_no_go_for_other_physical_EW_branches"])
            for gate in ("G4", "G5", "G6", "G7", "G8"):
                self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            vacuum = next(
                gate for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertTrue(
                vacuum["evidence"][
                    "physical_SM_G4_G5_branch_mismatch_source_bound"
                ]
            )
            self.assertFalse(
                vacuum["evidence"][
                    "physical_SM_global_no_go_for_other_EW_branches"
                ]
            )

            artifact = root / matrix.ARTIFACTS[
                "physical_sm_g4_g5_branch_mismatch"
            ]
            forged = json.loads(artifact.read_text(encoding="utf-8"))
            forged["scope"]["global_no_go_for_all_possible_physical_EW_branches"] = True
            write_json(root, artifact.name, forged)
            rejected = matrix.build_report(root)
            self.assertFalse(
                rejected["physical_SM_G4_G5_branch_mismatch_contract"][
                    "source_bound"
                ]
            )

    def test_last_six_make_all_37_Hessians_available_without_aggregate_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            scoped = report["physical_SM_last_six_Hessians_contract"]
            self.assertTrue(scoped["source_bound"])
            self.assertTrue(scoped["exact_last_six_source_Hessians_closed"])
            self.assertTrue(scoped["all_37_active_source_Hessians_available"])
            self.assertFalse(
                scoped[
                    "exact_37_row_aggregate_stationarity_kernel_rank_PSD_closed"
                ]
            )
            for gate in ("G3", "G4", "G5"):
                self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            vacuum = next(
                gate for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertTrue(
                vacuum["evidence"][
                    "physical_SM_all_37_active_source_Hessians_available"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "physical_SM_full_witness_stationarity_rank_PSD_closed"
                ]
            )

            artifact = root / matrix.ARTIFACTS["physical_sm_last_six_hessians"]
            forged = json.loads(artifact.read_text(encoding="utf-8"))
            forged["claims"][
                "exact_37_row_aggregate_stationarity_kernel_rank_PSD_proved_here"
            ] = True
            write_json(root, artifact.name, forged)
            rejected = matrix.build_report(root)
            self.assertFalse(
                rejected["physical_SM_last_six_Hessians_contract"]["source_bound"]
            )

    def test_37_row_local_Hessian_theorem_does_not_promote_global_G3_G5(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            scoped = report["physical_SM_37_row_aggregate_contract"]
            self.assertTrue(scoped["source_bound"])
            self.assertTrue(scoped["all_37_active_Hessians_source_derived"])
            self.assertTrue(
                scoped["exact_source_aggregate_value_minus_one_and_stationary"]
            )
            self.assertEqual(scoped["exact_source_aggregate_kernel_dimension"], 38)
            self.assertEqual(scoped["exact_source_aggregate_rank"], 448)
            self.assertTrue(
                scoped["exact_source_aggregate_PSD_and_strict_mod_symmetry"]
            )
            self.assertFalse(scoped["full_486_global_equality_orbit_closed"])
            for gate in ("G3", "G4", "G5"):
                self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            vacuum = next(
                gate for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            evidence = vacuum["evidence"]
            self.assertTrue(
                evidence["physical_SM_37_row_local_Hessian_theorem_source_bound"]
            )
            self.assertEqual(
                evidence["physical_SM_source_aggregate_kernel_dimension"], 38
            )
            self.assertEqual(evidence["physical_SM_source_aggregate_rank"], 448)
            self.assertTrue(evidence["physical_SM_source_algebra_Hessian_closed"])
            self.assertEqual(evidence["physical_SM_exact_source_Hessian_rows_closed"], 37)
            self.assertEqual(evidence["physical_SM_remaining_active_Hessian_rows"], 0)
            self.assertTrue(
                evidence["physical_SM_all_37_active_source_Hessians_closed"]
            )
            self.assertTrue(
                evidence["physical_SM_full_witness_stationarity_rank_PSD_closed"]
            )
            self.assertFalse(
                evidence[
                    "physical_SM_complete_global_486_field_stationary_equality_classified"
                ]
            )

            artifact = root / matrix.ARTIFACTS["physical_sm_37_row_aggregate"]
            forged = json.loads(artifact.read_text(encoding="utf-8"))
            forged["claims"]["physical_SM_G3_closed"] = True
            write_json(root, artifact.name, forged)
            rejected = matrix.build_report(root)
            self.assertFalse(
                rejected["physical_SM_37_row_aggregate_contract"]["source_bound"]
            )

    def test_full_486_local_orbit_does_not_promote_radius_global_or_G3_G5(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            scoped = report["physical_SM_local_equality_orbit_contract"]
            self.assertTrue(scoped["source_bound"])
            self.assertTrue(scoped["full_486_local_stationary_orbit_classified"])
            self.assertTrue(
                scoped["full_486_local_stationary_equality_orbit_classified"]
            )
            self.assertTrue(scoped["all_16_sign_variants_one_continuous_K_orbit"])
            self.assertTrue(scoped["target_orbit_strict_local_minimum_mod_K"])
            self.assertFalse(scoped["quantitative_neighborhood_radius_proved"])
            self.assertFalse(scoped["complete_486_global_equality_orbit_classified"])
            for gate in ("G3", "G4", "G5"):
                self.assertFalse(scoped[f"physical_SM_{gate}_closed"])
            vacuum = next(
                gate for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertTrue(
                vacuum["evidence"][
                    "physical_SM_full_486_local_equality_orbit_source_bound"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "physical_SM_16_sign_variants_one_continuous_K_orbit"
                ]
            )
            self.assertFalse(
                vacuum["evidence"][
                    "physical_SM_quantitative_local_orbit_radius_proved"
                ]
            )

            artifact = root / matrix.ARTIFACTS["physical_sm_local_equality_orbit"]
            baseline = json.loads(artifact.read_text(encoding="utf-8"))
            for claim in (
                "quantitative_radius_for_U_proved",
                "complete_486_field_global_equality_orbit_classified",
                "physical_SM_G3_closed",
            ):
                forged = json.loads(json.dumps(baseline))
                forged["claims"][claim] = True
                write_json(root, artifact.name, forged)
                rejected = matrix.build_report(root)
                self.assertFalse(
                    rejected["physical_SM_local_equality_orbit_contract"][
                        "source_bound"
                    ],
                    claim,
                )

    def test_physical_g7_component_contract_rejects_raw_byte_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS["physical_g7_component_threshold"]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            report = matrix.build_report(root)
            scoped = report["physical_G7_component_threshold_contract"]
            self.assertFalse(scoped["source_bound"])
            self.assertFalse(scoped["checks"]["all_four_raw_artifact_pins_exact"])
            self.assertFalse(scoped["physical_PS_SM_matter_branching_closed"])
            self.assertFalse(
                scoped["parameterized_one_loop_matter_threshold_kernel_closed"]
            )
            rge = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "two_loop_RGE_unification_and_thresholds"
            )
            self.assertFalse(rge["evidence"]["physical_PS_SM_matter_branching_closed"])
            self.assertFalse(rge["evidence"]["mathematical_G7_closed"])
            self.assertFalse(rge["evidence"]["release_G7_verified"])

    def test_yukawa_cgc_and_physical_sm_overlays_reject_raw_byte_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS["normalized_yukawa_cgcs"]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            report = matrix.build_report(root)
            cgcs = report["normalized_SO10_Yukawa_CGC_contract"]
            self.assertFalse(cgcs["source_bound"])
            self.assertFalse(cgcs["normalized_10_CGCs_closed"])
            rge = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "two_loop_RGE_unification_and_thresholds"
            )
            self.assertFalse(rge["evidence"]["normalized_SO10_10_CGCs_closed"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS["physical_sm_vacuum"]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            report = matrix.build_report(root)
            physical = report["physical_SM_vacuum_truth_overlay"]
            self.assertFalse(physical["source_bound"])
            self.assertFalse(physical["physical_SM_target_exactly_constructed"])
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                vacuum["evidence"]["physical_SM_vacuum_truth_overlay_source_bound"]
            )

    def test_vector_and_conditional_scalar_contracts_reject_raw_byte_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS["physical_sm_heavy_vectors"]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            report = matrix.build_report(root)
            vectors = report["physical_SM_heavy_vector_mass_contract"]
            self.assertFalse(vectors["source_bound"])
            self.assertFalse(
                vectors["checks"]["all_four_raw_artifact_pins_exact"]
            )
            self.assertFalse(
                vectors["exact_parameterized_tree_vector_mass_matrix_closed"]
            )
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                vacuum["evidence"][
                    "physical_SM_heavy_vector_tree_contract_source_bound"
                ]
            )
            rge = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "two_loop_RGE_unification_and_thresholds"
            )
            self.assertFalse(
                rge["evidence"][
                    "exact_parameterized_heavy_vector_tree_mass_matrix_closed"
                ]
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            matching = report[
                "physical_SM_heavy_vector_MSbar_matching_contract"
            ]
            self.assertTrue(matching["source_bound"])
            self.assertTrue(
                matching[
                    "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
                ]
            )
            self.assertTrue(matching["finite_MSbar_vector_constant_closed"])
            self.assertEqual(
                matching["complex_index_totals"], {"SU3": "5/2", "QED": "32/3"}
            )
            self.assertFalse(
                matching["arbitrary_Rxi_sector_resolved_matching_closed"]
            )
            artifact = root / matrix.ARTIFACTS["physical_sm_heavy_vector_msbar"]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            forged = matrix.build_report(root)
            forged_matching = forged[
                "physical_SM_heavy_vector_MSbar_matching_contract"
            ]
            self.assertFalse(forged_matching["source_bound"])
            self.assertFalse(
                forged_matching["checks"]["all_four_raw_artifact_pins_exact"]
            )
            forged_rge = next(
                gate
                for gate in forged["gates"]
                if gate["name"] == "two_loop_RGE_unification_and_thresholds"
            )
            self.assertFalse(
                forged_rge["evidence"][
                    "combined_heavy_vector_FPghost_Goldstone_MSbar_kernel_closed"
                ]
            )
            self.assertFalse(forged_rge["evidence"]["finite_MSbar_vector_constant_closed"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS[
                "conditional_physical_sm_scalar_spectrum"
            ]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            report = matrix.build_report(root)
            scalars = report[
                "conditional_physical_SM_EFT_Hessian_spectrum_contract"
            ]
            self.assertFalse(scalars["source_bound"])
            self.assertFalse(
                scalars["checks"]["all_four_raw_artifact_pins_exact"]
            )
            self.assertFalse(
                scalars["conditional_reconstructed_tree_scalar_spectrum_closed"]
            )
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertFalse(
                vacuum["evidence"][
                    "conditional_physical_SM_scalar_tree_spectrum_source_bound"
                ]
            )

    def test_eft_g7_obstruction_rejects_raw_byte_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS["eft_g7_nonidentifiability"]
            original = artifact.read_bytes()
            artifact.write_bytes(original + b"\n")
            g7 = matrix.build_report(root)["parallel_EFT_G7_nonidentifiability"]
            self.assertFalse(g7["source_bound"])
            self.assertFalse(g7["checks"]["raw_sha256_exact"])
            self.assertFalse(
                g7["formal_U1_89_abstract_restriction_noninjectivity_proved"]
            )

    def test_rxi_and_g6_g7_frontier_contracts_reject_raw_byte_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            rxi = report[
                "physical_SM_vector_Rxi_vacuum_cancellation_contract"
            ]
            frontier = report["physical_SM_G6_G7_closure_frontier_contract"]
            self.assertTrue(rxi["source_bound"])
            self.assertTrue(
                rxi[
                    "zero_background_Rxi_vacuum_determinant_cancellation_closed"
                ]
            )
            self.assertFalse(
                rxi["sector_resolved_general_background_determinants_closed"]
            )
            self.assertTrue(frontier["source_bound"])
            self.assertTrue(frontier["continuous_nonidentifiability_proved"])
            self.assertFalse(frontier["physical_G6_closed"])
            self.assertFalse(frontier["physical_G7_closed"])

            artifact = root / matrix.ARTIFACTS["physical_sm_vector_rxi"]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            forged = matrix.build_report(root)
            forged_rxi = forged[
                "physical_SM_vector_Rxi_vacuum_cancellation_contract"
            ]
            self.assertFalse(forged_rxi["source_bound"])
            forged_rge = next(
                gate
                for gate in forged["gates"]
                if gate["name"] == "two_loop_RGE_unification_and_thresholds"
            )
            self.assertFalse(
                forged_rge["evidence"][
                    "zero_background_Rxi_vacuum_determinant_cancellation_closed"
                ]
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS[
                "physical_sm_g6_g7_closure_frontier"
            ]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            forged = matrix.build_report(root)
            frontier = forged["physical_SM_G6_G7_closure_frontier_contract"]
            self.assertFalse(frontier["source_bound"])
            rge = next(
                gate
                for gate in forged["gates"]
                if gate["name"] == "two_loop_RGE_unification_and_thresholds"
            )
            self.assertFalse(
                rge["evidence"][
                    "continuous_G6_G7_nonidentifiability_frontier_closed"
                ]
            )

    def test_g8_frontier_contract_is_bound_and_rejects_raw_byte_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            report = matrix.build_report(root)
            frontier = report[
                "physical_SM_G8_identifiability_frontier_contract"
            ]
            self.assertTrue(frontier["source_bound"])
            self.assertTrue(frontier["canonical_G8_contract_audited"])
            self.assertTrue(
                frontier["continuous_absolute_scale_nonidentifiability_proved"]
            )
            self.assertTrue(
                frontier["flavor_and_interference_nonidentifiability_audited"]
            )
            self.assertTrue(
                frontier[
                    "repository_frozen_PDG_2025_single_channel_constraint_verified"
                ]
            )
            self.assertEqual(
                frontier["minimal_exhibited_joint_free_real_dimension"], 1
            )
            self.assertFalse(frontier["unique_proton_lifetime_or_distribution"])
            self.assertFalse(frontier["physical_G8_closed"])
            self.assertFalse(frontier["release_G8_verified"])
            self.assertFalse(frontier["authoritative_G8_closed"])
            proton = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "proton_decay"
            )
            self.assertEqual(proton["state"], "BLOCKED")
            self.assertTrue(
                proton["evidence"][
                    "physical_SM_G8_identifiability_frontier_source_bound"
                ]
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(root)
            artifact = root / matrix.ARTIFACTS[
                "physical_sm_g8_identifiability_frontier"
            ]
            artifact.write_bytes(artifact.read_bytes() + b"\n")
            forged = matrix.build_report(root)
            frontier = forged[
                "physical_SM_G8_identifiability_frontier_contract"
            ]
            self.assertFalse(frontier["source_bound"])
            self.assertFalse(frontier["physical_G8_closed"])
            proton = next(
                gate
                for gate in forged["gates"]
                if gate["name"] == "proton_decay"
            )
            self.assertEqual(proton["state"], "OPEN")
            self.assertFalse(
                proton["evidence"][
                    "physical_SM_G8_identifiability_frontier_source_bound"
                ]
            )

    def test_current_repository_can_never_claim_discovery_from_internal_tests(self):
        report = matrix.build_report(matrix.ROOT)
        self.assertFalse(report["empirical_discovery"])
        self.assertFalse(report["full_theory_validated"])
        self.assertIn(
            report["classification"],
            {
                "CANONICAL_G1_G8_GATES_OPEN",
                "FULL_PHENOMENOLOGY_VALIDATED__NO_DISCOVERY_IMPLIED",
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
            self.assertTrue(
                vacuum["evidence"]["gauged_G1_multiplicity_census_complete"]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G1_full_component_tensor_integration_complete"
                ]
            )
            self.assertFalse(
                vacuum["evidence"]["scalar_contract_pre_audit_G2_certified_flag"]
            )
            self.assertTrue(
                vacuum["evidence"]["dedicated_G2_audit_is_source_authoritative"]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "dedicated_G2_audit_supersedes_pre_audit_scalar_contract_flag"
                ]
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
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_distant_Phi_components_excluded"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_Phi_SU3_fixed_slice_exactly_closed"
                ]
            )
            self.assertFalse(
                vacuum["evidence"][
                    "gauged_G3_SU5_global_Phi_orbit_lemma_open"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_global_Phi_orbit_lemma_closed"
                ]
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_all_PD_equality_orbits_classified_exactly"
                ]
            )
            self.assertEqual(
                vacuum["evidence"]["gauged_G3_SU5_global_Phi_theorem_core_sha256"],
                "db493a74303a57862f09c2a92118ea3d66b8b12ecbaea9162155d4ab3baafecc",
            )
            self.assertTrue(
                vacuum["evidence"][
                    "gauged_G3_SU5_quantitative_beta_global_coercivity_open"
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

    def test_hypothetical_vacuum_pass_requires_g3_g6_and_source_bound_spectrum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            minimal_tree(
                root,
                contract_consistent=True,
                vacuum_minimized=True,
                exact_stationarity_rank=True,
            )
            spectrum_payload = {
                "model_contract_id": matrix.MODEL_CONTRACT_ID,
                "n_failed": 0,
                "classification": {
                    "complete_physical_scalar_spectrum": True,
                    "source_bound_to_authoritative_vacuum": True,
                    "all_physical_scalar_eigenstates_classified": True,
                    "no_unexplained_zero_or_negative_modes": True,
                },
            }
            write_json(
                root,
                "G6_FULL_PHYSICAL_SPECTRUM_V20.json",
                spectrum_payload,
            )

            # A valid spectrum artifact cannot bypass the authoritative G3-G6
            # dependency chain.
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"], "OPEN"
            )

            ledger_path = root / "G1_G8_GATE_LEDGER_V20.json"
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            for name in ("G3", "G4", "G5", "G6"):
                ledger["gates"][name]["status"] = "CLOSED"
            ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

            # Conversely, closed ledger booleans cannot bypass exact source
            # binding of the complete spectrum.
            spectrum_payload["classification"][
                "source_bound_to_authoritative_vacuum"
            ] = False
            write_json(
                root,
                "G6_FULL_PHYSICAL_SPECTRUM_V20.json",
                spectrum_payload,
            )
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(states["authoritative_model_contract"], "PASS")
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"], "OPEN"
            )

            spectrum_payload["classification"][
                "source_bound_to_authoritative_vacuum"
            ] = True
            write_json(
                root,
                "G6_FULL_PHYSICAL_SPECTRUM_V20.json",
                spectrum_payload,
            )
            report = matrix.build_report(root)
            states = {gate["name"]: gate["state"] for gate in report["gates"]}
            self.assertEqual(states["authoritative_model_contract"], "PASS")
            self.assertEqual(
                states["full_scalar_potential_vacuum_and_spectrum"], "PASS"
            )
            vacuum = next(
                gate
                for gate in report["gates"]
                if gate["name"] == "full_scalar_potential_vacuum_and_spectrum"
            )
            self.assertTrue(
                vacuum["evidence"]["authoritative_G3_G4_G5_G6_closed"]
            )
            self.assertTrue(
                vacuum["evidence"]["G6_complete_source_bound_physical_spectrum"]
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
