#!/usr/bin/env python3
from __future__ import annotations

import copy

import final_g3_acceptance_gate_v20 as mod


def _current_inputs():
    return (
        mod.ledger.build_report(),
        mod._load(mod.HSX_JSON),
        mod._load(mod.EQUALITY_JSON),
        mod._load(mod.GAP_JSON),
    )


def test_current_gate_is_open_not_failed_or_overclaimed():
    report = mod.build_report()
    assert report["n_failed"] == 0, report["failures"]
    assert report["overall_state"] == "OPEN"
    assert report["classification"]["theory_still_viable"] is True
    assert report["classification"]["mathematical_G3_closed"] is False
    assert report["classification"]["release_G3_verified"] is False
    assert report["classification"]["G3_closed"] is False
    assert report["diagnostic_only"]["live_transverse_dimension"] == 448
    assert report["science_criteria"][
        "full_Hessian_rank_448_nullity_38_exact"
    ] is True
    assert report["science_criteria"][
        "full_448_quotient_strictly_positive_exact"
    ] is True
    assert report["science_criteria"][
        "full_fixed_F_offkernel_gap_and_equality_exact"
    ] is True
    assert report["artifact_integrity"][
        "max_negative_all_zero_residual_audit_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "max_negative_full_residual_pure_Delta_audit_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "max_negative_rank1_SU3_four_dimensional_slice_audit_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_stabilizer_infrastructure_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_Phi210_intertwiner_infrastructure_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_aligned_carrier_infrastructure_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_Phi210_quadratic_basis_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_census_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_cubic_map_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
    ] is True
    assert report["science_criteria"][
        "max_negative_all_zero_residual_route_excluded_exactly"
    ] is True
    assert report["science_criteria"][
        "max_negative_pure_Delta_full_residual_gap_excluded_exactly"
    ] is True
    assert report["science_criteria"][
        "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3"
    ] is True
    assert report["science_criteria"][
        "rank1_SU4_representation_infrastructure_ready_without_closing_G3"
    ] is True
    assert report["science_criteria"][
        "signed_Phi_orbits_locally_isolated_exactly"
    ] is True
    assert report["science_criteria"][
        "complete_SU3_fixed_Phi_slice_classified_exactly"
    ] is True
    assert report["diagnostic_only"]["Phi_local_component_state"] == (
        "LOCAL_COMPONENT_THEOREM_CLOSED"
    )
    assert report["diagnostic_only"]["distant_Phi_components_excluded"] is False
    assert report["diagnostic_only"][
        "complete_SU3_fixed_Phi_slice_classified"
    ] is True
    assert report["diagnostic_only"]["SU3_slice_generic_components_excluded"] is False
    assert report["diagnostic_only"]["fixed_F_full_offkernel_state"] == (
        "CLOSED_FIXED_F_GLOBAL_SUBPROBLEM"
    )
    assert report["diagnostic_only"]["fixed_F_global_gap_closed"] is True
    assert report["diagnostic_only"]["arbitrary_Phi_global_gap_closed"] is False
    assert report["diagnostic_only"][
        "max_negative_all_zero_residual_route_excluded"
    ] is True
    assert report["diagnostic_only"][
        "max_negative_all_zero_residual_strict_margin"
    ] == "7859/140295000"
    assert report["diagnostic_only"][
        "arbitrary_Phi_nonzero_residual_cancellations_excluded"
    ] is False
    assert report["diagnostic_only"][
        "max_negative_pure_Delta_full_residual_gap_closed"
    ] is True
    assert report["diagnostic_only"][
        "max_negative_pure_Delta_full_residual_minimum"
    ] == "1/5000"
    assert report["diagnostic_only"]["rank1_SU3_Phi_slice_real_dimension"] == 4
    assert report["diagnostic_only"]["rank1_SU3_ambient_real_dimension"] == 16
    assert report["diagnostic_only"]["rank1_SU3_slice_minimum"] == "1/5000"
    assert report["diagnostic_only"]["arbitrary_rank1_Phi_open"] is True
    assert report["diagnostic_only"]["rank1_SU4_joint_stabilizer_dimension"] == 15
    assert report["diagnostic_only"]["rank1_SU4_Phi210_carrier_count"] == 25
    assert report["diagnostic_only"]["rank1_SU4_Sym2_invariant_dimension"] == 45
    assert report["diagnostic_only"]["rank1_SU4_aligned_direct_sum_rank"] == 210
    assert report["diagnostic_only"]["rank1_SU4_physical_real_maps_exact"] is True
    assert report["diagnostic_only"]["rank1_SU4_quadratic_constraint_shape"] == [5952, 551]
    assert report["diagnostic_only"]["rank1_SU4_quadratic_constraint_rank"] == 506
    assert report["diagnostic_only"]["rank1_SU4_quadratic_constraint_nullity"] == 45
    assert report["diagnostic_only"]["rank1_SU4_quadratic_basis_count"] == 45
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_homogeneous_dimension"
    ] == 22_366
    assert report["diagnostic_only"]["rank1_SU4_augmented_isotypic_types"] == 35
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_irreducible_copies"
    ] == 824
    assert report["diagnostic_only"]["rank1_SU4_augmented_real_blocks"] == 22
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_Schur_parameters"
    ] == 19_594
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_invariant_rows"
    ] == 6_585
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_coordinate_Schur_map_constructed"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_physical_target_constructed"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_SDP_constructed"
    ] is False
    assert report["diagnostic_only"]["rank1_SU4_augmented_cubic_map_shape"] == [
        478,
        1_414,
    ]
    assert report["diagnostic_only"]["rank1_SU4_augmented_cubic_map_rank"] == 478
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_cubic_map_kernel_dimension"
    ] == 936
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_cubic_zero_placeholder_is_nonphysical"
    ] is True
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_cubic_physical_target_constructed"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_cubic_physical_zero_RHS_certified"
    ] is False
    assert report["diagnostic_only"]["rank1_SU4_augmented_quartic_map_shape"] == [
        6_057,
        18_085,
    ]
    assert report["diagnostic_only"]["rank1_SU4_augmented_quartic_map_rank"] == 6_057
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_quartic_map_kernel_dimension"
    ] == 12_028
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_quartic_physical_target_constructed"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_quartic_standard_PSD_congruences_constructed"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_quartic_SDP_solved"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_PSD_routes_and_target_exact"
    ] is True
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_standard_PSD_route_count"
    ] == 22
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_standard_PSD_parameter_count"
    ] == 19_594
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_physical_target_row_count"
    ] == 6_585
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_physical_target_common_denominator"
    ] == 1_728_000
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_physical_target_nonzero_count"
    ] == 845
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_standard_coordinate_map_constructed"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_PSD_SDP_solved"
    ] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_PSD_G3_closed"
    ] is False
    assert report["diagnostic_only"]["rank1_SU4_Schur_SOS_SDP_constructed"] is False
    assert report["diagnostic_only"][
        "arbitrary_non_pure_Delta_Sigma_orientations_open"
    ] is True
    assert report["remaining_open_problem"] == (
        "uniform coercivity for arbitrary non-pure-Delta Sigma orientations"
    )
    assert report["science_criteria"][
        "beta_global_gap_and_unique_equality_exact"
    ] is False
    assert "478x1414 integer map" in report["verdict"]
    assert "kernel dimension 936" in report["verdict"]
    assert "zero placeholder is nonphysical" in report["verdict"]
    assert "exact-rank-6057, 6057x18085 integer map" in report["verdict"]
    assert "kernel dimension 12028" in report["verdict"]
    assert "22 standard PSD-coordinate routes" in report["verdict"]
    assert "physical 6585-row target" in report["verdict"]
    assert "coefficient map in standard PSD coordinates" in report["verdict"]
    assert "G3 remains open" in report["verdict"]
    assert "no coordinate Schur matrix" not in report["verdict"]


def test_rank1_slice_rejects_wrong_fixed_H_orientation():
    forged = copy.deepcopy(mod._load(mod.MAX_NEGATIVE_RANK1_SU3_SLICE_JSON))
    forged["scope"]["H_fixed_to_h_minus"] = False
    report = mod.build_report(max_negative_rank1_su3_slice_report=forged)
    assert report["artifact_integrity"][
        "max_negative_rank1_SU3_four_dimensional_slice_audit_executes_fail_closed"
    ] is False
    assert report["science_criteria"][
        "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3"
    ] is False
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["classification"]["G3_closed"] is False


def test_decisive_theorem_is_full_field_global_and_orbit_exact():
    report = mod.build_report()
    assert report["decisive_theorem"] == mod.FINAL_THEOREM
    assert "every 486-real field" in report["decisive_theorem"]
    assert "SO(10)xU(1)_XxPQ orbit" in report["decisive_theorem"]


def test_numerical_448_inertia_cannot_promote_exact_hessian():
    ledger_report, hsx, equality, gap = _current_inputs()
    forged = copy.deepcopy(hsx)
    forged["flag"]["G3_closed"] = True
    report = mod.build_report(
        ledger_report=ledger_report,
        hsx_report=forged,
        equality_report=equality,
        gap_report=gap,
        exact_hessian_report={},
    )
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["classification"]["G3_closed"] is False
    assert report["science_criteria"][
        "full_Hessian_rank_448_nullity_38_exact"
    ] is False


def test_all_explicit_proof_contracts_are_sufficient_for_pass():
    ledger_report, hsx, equality, gap = map(copy.deepcopy, _current_inputs())
    ledger_report["contract_consistent"] = True
    ledger_report["gates"]["G1"]["status"] = mod.ledger.STATUS_CLOSED
    ledger_report["gates"]["G2"]["status"] = mod.ledger.STATUS_CLOSED

    equality["scope"]["all_arbitrary_Phi_global_equalities_classified"] = True
    equality["scope"]["global_equality_orbit_classification_complete"] = True
    equality["remaining_global_lemma"]["proved"] = True
    equality["remaining_global_lemma"]["source_bound_certificate_available"] = True

    gap["flags"]["beta_1_over_20_global_minimum_certified"] = True
    gap["flags"]["global_equality_orbits_classified"] = True
    gap["final_acceptance_test"]["currently_passes"] = True
    gap["final_acceptance_test"]["required_statement"] = mod.FINAL_THEOREM

    exact_hessian = {
        "status": "EXACT_FULL_HESSIAN_RANK_448_NULLITY_38_CERTIFIED",
        "overall_state": "CLOSED_FULL_LOCAL_HESSIAN_SUBPROBLEM",
        "model_contract_id": mod.MODEL_CONTRACT_ID,
        "n_failed": 0,
        "flags": {
            "source_binding_exact": True,
            "proof_grade": True,
            "exact_rank_448": True,
            "exact_nullity_38": True,
            "exact_PSD": True,
            "strict_quotient_positive": True,
            "kernel_equals_38_symmetry_tangents": True,
        },
    }
    report = mod.build_report(
        ledger_report=ledger_report,
        hsx_report=hsx,
        equality_report=equality,
        gap_report=gap,
        exact_hessian_report=exact_hessian,
    )
    assert report["n_failed"] == 0, report["failures"]
    assert report["overall_state"] == "PASS"
    assert all(report["science_criteria"].values())
    assert all(report["release_criteria"].values())
    assert report["classification"]["mathematical_G3_closed"] is True
    assert report["classification"]["release_G3_verified"] is True
    assert report["classification"]["G3_closed"] is True


def test_exact_lower_witness_rejects_candidate_not_whole_theory():
    ledger_report, hsx, equality, gap = map(copy.deepcopy, _current_inputs())
    gap["flags"]["lower_witness_found"] = True
    report = mod.build_report(
        ledger_report=ledger_report,
        hsx_report=hsx,
        equality_report=equality,
        gap_report=gap,
        exact_hessian_report={},
    )
    assert report["overall_state"] == "CANDIDATE_FAIL"
    assert report["classification"]["candidate_exactly_rejected"] is True
    assert report["classification"]["whole_model_excluded"] is False
    assert report["classification"]["theory_still_viable"] is True


def test_rank1_slice_false_flags_are_fail_closed():
    forged = copy.deepcopy(mod._load(mod.MAX_NEGATIVE_RANK1_SU3_SLICE_JSON))
    forged["checks"]["arbitrary_Sigma35_proved"] = True
    report = mod.build_report(max_negative_rank1_su3_slice_report=forged)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["artifact_integrity"][
        "max_negative_rank1_SU3_four_dimensional_slice_audit_executes_fail_closed"
    ] is False
    assert report["classification"]["G3_closed"] is False


def test_rank1_su4_infrastructure_mutations_are_fail_closed():
    stabilizer = mod._load(mod.RANK1_SU4_STABILIZER_JSON)
    intertwiners = mod._load(mod.RANK1_SU4_PHI210_INTERTWINERS_JSON)
    mutations = []

    forged_stabilizer = copy.deepcopy(stabilizer)
    forged_stabilizer["scope"]["arbitrary_rank1_Phi_bound_proved"] = True
    mutations.append((forged_stabilizer, copy.deepcopy(intertwiners)))

    forged_intertwiners = copy.deepcopy(intertwiners)
    forged_intertwiners["scope"]["G3_closed"] = True
    mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

    forged_intertwiners = copy.deepcopy(intertwiners)
    forged_intertwiners["intertwiner"]["exterior_basis_shape"] = [0, 0]
    mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

    forged_intertwiners = copy.deepcopy(intertwiners)
    forged_intertwiners["companion_stabilizer_provenance"][
        "all_required_provenance_exact"
    ] = False
    mutations.append((copy.deepcopy(stabilizer), forged_intertwiners))

    for forged_stabilizer, forged_intertwiners in mutations:
        report = mod.build_report(
            rank1_su4_stabilizer_report=forged_stabilizer,
            rank1_su4_phi210_intertwiners_report=forged_intertwiners,
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_Phi210_intertwiner_infrastructure_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
        ] is False


def test_rank1_su4_augmented_psd_target_mutations_fail_closed_without_closing_g3():
    psd_target = mod._load(mod.RANK1_SU4_AUGMENTED_SOS_PSD_TARGET_JSON)
    mutations = (
        ("scope", "semidefinite_feasibility_solved", True),
        ("scope", "exact_primal_PSD_certificate_constructed", True),
        ("scope", "exact_dual_Farkas_certificate_constructed", True),
        ("scope", "arbitrary_Phi_lower_bound_proved", True),
        ("scope", "G3_closed", True),
        ("standard_PSD_coordinate_routes", "standard_total_parameter_count", 19_593),
    )
    for section, key, value in mutations:
        forged = copy.deepcopy(psd_target)
        forged[section][key] = value
        report = mod.build_report(
            rank1_su4_augmented_sos_psd_target_report=forged
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
        ] is False


def test_rank1_su4_stage2_mutations_are_fail_closed():
    aligned = mod._load(mod.RANK1_SU4_ALIGNED_CARRIERS_JSON)
    quadratic = mod._load(mod.RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON)

    forged_aligned = copy.deepcopy(aligned)
    forged_aligned["alignment"]["concatenated_aligned_basis_rank_mod_prime"] = 209
    report = mod.build_report(rank1_su4_aligned_carriers_report=forged_aligned)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["artifact_integrity"][
        "rank1_SU4_aligned_carrier_infrastructure_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_Phi210_quadratic_basis_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_census_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_cubic_map_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
    ] is False


def test_rank1_su4_augmented_cubic_mutations_cascade_fail_closed():
    cubic = mod._load(mod.RANK1_SU4_AUGMENTED_SOS_CUBIC_MAP_JSON)
    mutations = (
        ("source_provenance", "census_report_sha256", "0" * 64),
        ("Sym2_target_carriers", "total_complex_carrier_copy_count", 539),
        ("physical_cubic_domain", "physical_basis_count", 1_413),
        ("cubic_coordinate_map", "coordinate_map_sha256", "f" * 64),
        ("cubic_coordinate_map", "exact_rank", 477),
        ("cubic_coordinate_map", "exact_kernel_dimension", 937),
        (
            "cubic_coordinate_map",
            "abstract_zero_placeholder_is_not_a_physical_G3_target",
            False,
        ),
        (
            "cubic_coordinate_map",
            "physical_G3_gap_target_vector_constructed",
            True,
        ),
        (
            "cubic_coordinate_map",
            "physical_G3_gap_cubic_zero_RHS_certified",
            True,
        ),
    )
    for section, field, forged_value in mutations:
        forged = copy.deepcopy(cubic)
        forged[section][field] = forged_value
        report = mod.build_report(
            rank1_su4_augmented_sos_cubic_map_report=forged
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["classification"]["theory_still_viable"] is True
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_cubic_map_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
        ] is False

    for field in (
        "degree_zero_coefficient_map_constructed",
        "degree_one_coefficient_map_constructed",
        "degree_two_coefficient_map_constructed",
        "degree_four_coefficient_map_constructed",
        "full_6585_by_19594_Schur_coordinate_matrix_constructed",
        "physical_G3_gap_target_vector_constructed",
        "physical_G3_gap_cubic_zero_RHS_certified",
        "augmented_Schur_SOS_SDP_constructed",
        "augmented_Schur_SOS_SDP_feasibility_certified",
        "augmented_Schur_SOS_SDP_infeasibility_certified",
        "arbitrary_real_Phi_lower_bound_proved",
        "arbitrary_rank1_Phi_proved",
        "G3_closed",
        "whole_model_validated",
        "whole_model_excluded",
    ):
        forged = copy.deepcopy(cubic)
        forged["scope"][field] = True
        report = mod.build_report(
            rank1_su4_augmented_sos_cubic_map_report=forged
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_cubic_map_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
        ] is False


def test_rank1_su4_augmented_census_mutations_are_fail_closed():
    census = mod._load(mod.RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON)
    quadratic = mod._load(mod.RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON)
    for key in (
        "Schur_coordinate_6585_by_19594_coefficient_matrix_constructed",
        "physical_G3_gap_target_vector_constructed",
        "augmented_Schur_SOS_SDP_constructed",
        "arbitrary_real_Phi_lower_bound_proved",
        "G3_closed",
        "whole_model_validated",
        "whole_model_excluded",
    ):
        forged = copy.deepcopy(census)
        forged["scope"][key] = True
        report = mod.build_report(rank1_su4_augmented_sos_census_report=forged)
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_census_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_cubic_map_executes_fail_closed"
        ] is False

    forged_quadratic = copy.deepcopy(quadratic)
    forged_quadratic["scope"]["augmented_homogeneous_Schur_SOS_SDP_constructed"] = True
    report = mod.build_report(
        rank1_su4_phi210_quadratic_basis_report=forged_quadratic
    )
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["classification"]["G3_closed"] is False
    assert report["artifact_integrity"][
        "rank1_SU4_Phi210_quadratic_basis_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_census_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_cubic_map_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
    ] is False
    assert report["artifact_integrity"][
        "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
    ] is False


def test_rank1_su4_augmented_quartic_mutations_cascade_fail_closed():
    quartic = mod._load(mod.RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON)
    mutations = (
        ("scope", "physical_quartic_target_constructed", True),
        (
            "scope",
            "standard_PSD_congruences_for_real_type_fixed_bases_constructed",
            True,
        ),
        ("scope", "semidefinite_feasibility_solved", True),
        ("scope", "G3_closed", True),
        ("coefficient_map_certificate", "rank_over_Q_exact", 6_056),
        (
            "coefficient_map_certificate",
            "kernel_dimension_over_Q_exact",
            12_029,
        ),
        ("coefficient_map_certificate", "coordinate_map_sha256", "f" * 64),
    )
    for section, key, value in mutations:
        forged = copy.deepcopy(quartic)
        forged[section][key] = value
        report = mod.build_report(
            rank1_su4_augmented_sos_quartic_map_report=forged
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_PSD_target_executes_fail_closed"
        ] is False
