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
    assert report["diagnostic_only"][
        "arbitrary_non_pure_Delta_Sigma_orientations_open"
    ] is True
    assert report["remaining_open_problem"] == (
        "uniform coercivity for arbitrary non-pure-Delta Sigma orientations"
    )
    assert report["science_criteria"][
        "beta_global_gap_and_unique_equality_exact"
    ] is False


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
