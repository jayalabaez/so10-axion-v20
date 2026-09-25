#!/usr/bin/env python3
from __future__ import annotations

import copy
import functools

import final_g3_acceptance_gate_v20 as mod
import g3_sm_target_track_v20 as sm_track

SM = "sm_pati_salam"
CHIRAL = "chiral_H_SU5_Delta"
CLOSED_VERDICT_PREFIX = (
    "G3 is verified on the SM Pati-Salam track, the only closure route of "
    "this gate. "
)
OPEN_VERDICT_PREFIX = (
    "G3 remains open: the SM Pati-Salam track, the only closure route of "
    "this gate, is not certified (blockers: "
)
RELEASE_NAMES = [
    "authoritative_external_model_contract_executed",
    "G1_promoted_closed",
    "G2_promoted_closed",
    "G5_BFB_evidence_covers_closing_coupling_vector",
    "ledger_G3_status_matches_gate_closure",
]
CHIRAL_RELEASE_NAMES = [
    "authoritative_external_model_contract_executed",
    "G1_promoted_closed",
    "G2_promoted_closed",
]


@functools.lru_cache(maxsize=1)
def _cached_ledger():
    return mod.ledger.build_report()


def _ledger():
    return copy.deepcopy(_cached_ledger())


def _current_inputs():
    return (
        _ledger(),
        mod._load(mod.HSX_JSON),
        mod._load(mod.EQUALITY_JSON),
        mod._load(mod.GAP_JSON),
    )


def _sm_inputs():
    return copy.deepcopy(sm_track.load_inputs())


def _chiral(report):
    return report["tracks"][CHIRAL]


def test_current_gate_passes_on_the_sm_track_only():
    report = mod.build_report()
    assert report["status"] == "FINAL_G3_ACCEPTANCE_TEST_EXECUTED"
    assert report["n_failed"] == 0, report["failures"]
    assert report["failures"] == []
    assert report["missing_artifacts"] == []
    assert report["overall_state"] == "PASS", report["blockers"]
    assert report["closing_track"] == SM
    assert report["blockers"] == []
    classification = report["classification"]
    assert classification["G3_closed"] is True
    assert classification["mathematical_G3_closed"] is True
    assert classification["release_G3_verified"] is True
    assert classification["closing_track"] == SM
    assert classification["candidate_exactly_rejected"] is False
    assert classification["whole_model_excluded"] is False
    assert classification["theory_still_viable"] is True
    assert classification["whole_model_validated"] is False
    assert classification["internal_candidate_approved_by_this_gate"] is False
    assert set(classification) == {
        "mathematical_G3_closed",
        "release_G3_verified",
        "G3_closed",
        "candidate_exactly_rejected",
        "whole_model_excluded",
        "theory_still_viable",
        "closing_track",
        "whole_model_validated",
        "internal_candidate_approved_by_this_gate",
    }
    assert "pati_salam_candidate_equality_set" not in report

    assert report["decisive_theorem"] == sm_track.SM_FINAL_THEOREM
    assert report["decisive_theorem"] == mod.DECISIVE_THEOREM
    sm = report["tracks"][SM]
    assert sm["track"] == SM
    assert sm["role"] == "ONLY_CLOSURE_ROUTE"
    assert sm["closed"] is True
    assert sm["blockers"] == []
    assert report["science_criteria"] == sm["science_criteria"]
    assert len(report["science_criteria"]) == 13
    assert all(value is True for value in report["science_criteria"].values())
    assert list(report["release_criteria"]) == RELEASE_NAMES
    assert all(value is True for value in report["release_criteria"].values())

    # Integrity is the union of both tracks; no name collides.
    chiral = _chiral(report)
    assert set(sm["artifact_integrity"]) <= set(report["artifact_integrity"])
    assert set(chiral["artifact_integrity"]) <= set(report["artifact_integrity"])
    assert report["n_integrity_checks"] == (
        len(chiral["artifact_integrity"]) + len(sm["artifact_integrity"])
    )
    assert len(sm["artifact_integrity"]) == 10
    assert all(name.startswith("sm_") for name in sm["artifact_integrity"])
    assert all(value is True for value in report["artifact_integrity"].values())

    assert report["closure_scope"] == sm_track.CLOSURE_SCOPE
    assert report["witness"] == sm["witness"]
    assert report["witness"]["sentence"] == sm_track.WITNESS_SENTENCE
    assert report["witness"]["eps_window"]["upper_exclusive"] == "599/50"
    assert report["downstream_caveats"] == sm["downstream_caveats"]
    assert len(report["downstream_caveats"]) == 10
    assert report["disclosures"] == sm["disclosures"]
    assert report["closure_route"] == {
        "closing_tracks": [SM],
        "diagnostic_tracks": [CHIRAL],
        "rule": mod.CLOSURE_ROUTE_RULE,
    }
    assert "decision D1" in report["closure_route"]["rule"]
    assert report["remaining_open_problem"] == mod.CLOSED_REMAINING_OPEN_PROBLEM
    assert report["remaining_open_problem"].startswith(
        "none inside G3 on the closing track"
    )

    assert chiral["track"] == CHIRAL
    assert chiral["role"] == "DIAGNOSTIC"
    assert chiral["can_close_G3"] is False
    assert chiral["decisive_theorem"] == mod.FINAL_THEOREM
    assert chiral["science_criteria"][
        "target_unbroken_algebra_is_standard_model"
    ] is False
    assert chiral["mathematical_criteria_all_true"] is False
    assert chiral["candidate_exactly_rejected"] is False
    assert list(chiral["release_criteria"]) == CHIRAL_RELEASE_NAMES
    assert len(chiral["science_criteria"]) == 17
    assert set(chiral) == {
        "track",
        "role",
        "can_close_G3",
        "artifact_integrity",
        "science_criteria",
        "release_criteria",
        "decisive_theorem",
        "mathematical_criteria_all_true",
        "blockers",
        "candidate_exactly_rejected",
        "why_not_a_closure_route",
        "known_issues",
        "summary",
    }
    assert "not the Standard Model" in chiral["why_not_a_closure_route"]
    assert any("equality holds only on" in item for item in chiral["known_issues"])

    assert chiral["science_criteria"][
        "full_Hessian_rank_448_nullity_38_exact"
    ] is True
    assert chiral["science_criteria"][
        "full_448_quotient_strictly_positive_exact"
    ] is True
    assert chiral["science_criteria"][
        "full_fixed_F_offkernel_gap_and_equality_exact"
    ] is True
    assert chiral["science_criteria"][
        "max_negative_all_zero_residual_route_excluded_exactly"
    ] is True
    assert chiral["science_criteria"][
        "max_negative_pure_Delta_full_residual_gap_excluded_exactly"
    ] is True
    assert chiral["science_criteria"][
        "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3"
    ] is True
    assert chiral["science_criteria"][
        "rank1_SU4_representation_infrastructure_ready_without_closing_G3"
    ] is True
    assert chiral["science_criteria"][
        "signed_Phi_orbits_locally_isolated_exactly"
    ] is True
    assert chiral["science_criteria"][
        "complete_SU3_fixed_Phi_slice_classified_exactly"
    ] is True
    assert chiral["science_criteria"][
        "beta_global_gap_and_unique_equality_exact"
    ] is False

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
        "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
    ] is True
    assert report["artifact_integrity"][
        "rank1_SU4_corrected_fixed_endpoint_theorem_executes_fail_closed"
    ] is True

    assert report["diagnostic_only"]["live_transverse_dimension"] == 448
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
        "rank1_SU4_legacy_v20_PSD_routes_and_stale_payload_well_formed"
    ] is True
    assert report["diagnostic_only"][
        "rank1_SU4_legacy_v20_physical_target_valid"
    ] is False
    assert report["diagnostic_only"]["rank1_SU4_legacy_v20_primal_valid"] is False
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_standard_PSD_route_count"
    ] == 22
    assert report["diagnostic_only"][
        "rank1_SU4_augmented_standard_PSD_parameter_count"
    ] == 19_594
    assert report["diagnostic_only"][
        "rank1_SU4_corrected_positive_Gram_map_shape"
    ] == [6_585, 19_594]
    assert report["diagnostic_only"][
        "rank1_SU4_corrected_exact_coefficient_equalities"
    ] == 6_585
    assert report["diagnostic_only"][
        "rank1_SU4_corrected_strict_positive_Gram_blocks"
    ] == 22
    assert report["diagnostic_only"][
        "rank1_SU4_corrected_strict_positive_LDL_pivots"
    ] == 824
    assert report["diagnostic_only"][
        "rank1_SU4_corrected_arbitrary_real_Phi_at_fixed_endpoint"
    ] is True
    assert report["diagnostic_only"][
        "rank1_SU4_corrected_global_Sigma_proved"
    ] is False
    assert report["diagnostic_only"]["rank1_SU4_corrected_G3_closed"] is False
    assert report["diagnostic_only"]["rank1_SU4_Schur_SOS_SDP_constructed"] is False
    assert report["diagnostic_only"][
        "arbitrary_non_pure_Delta_Sigma_orientations_open"
    ] is True


def test_closed_verdict_is_scoped_and_chiral_summary_is_kept_in_its_track():
    report = mod.build_report()
    verdict = report["verdict"]
    assert verdict.startswith(CLOSED_VERDICT_PREFIX)
    assert sm_track.CLOSURE_SCOPE in verdict
    assert "Decisive theorem: " + sm_track.SM_FINAL_THEOREM in verdict
    assert sm_track.WITNESS_SENTENCE in verdict
    assert sm_track.CAVEAT_ROUTING_SENTENCE in verdict
    assert "accepted as G3-grade inputs under decision D6" in verdict
    assert verdict.endswith(mod.CLOSED_VERDICT_CHIRAL_TAIL)
    assert "can never close G3" in verdict
    assert "not a Standard-Model vacuum" in verdict
    assert "internal candidate withheld" in verdict
    assert "whole model neither validated nor excluded" in verdict
    assert "G3 remains open" not in verdict
    assert "not yet wired in" not in verdict
    assert "PASS is impossible at this point" not in verdict

    summary = _chiral(report)["summary"]
    assert summary == mod.CHIRAL_TRACK_SUMMARY
    assert summary.startswith(
        "The mathematical results below stay valid for that point."
    )
    assert summary.endswith("closes at the certified point.")
    assert "478x1414 integer map" in summary
    assert "kernel dimension 936" in summary
    assert "zero placeholder is nonphysical" in summary
    assert "exact-rank-6057, 6057x18085 integer map" in summary
    assert "kernel dimension 12028" in summary
    assert "legacy v20 assembled physical target is rejected" in summary
    assert "corrected 6585x19594 standard positive-Gram map" in summary
    assert "strict 22-block/824-pivot primal" in summary
    assert "every real Phi210" in summary
    assert "Global Sigma and general/full H remain open for that point" in summary
    assert "Global Sigma, general/full H, and G3 remain open" not in summary
    assert "exact 448/38 certificate" in summary
    assert "PASS still requires uniform coercivity" not in summary
    assert "only a four-real-dimensional Phi sub-slice" not in summary
    assert "arbitrary-Phi bound remain open" not in summary
    assert "no coordinate Schur matrix" not in summary


def test_markdown_carries_verdict_theorem_and_diagnostic_track():
    report = mod.build_report()
    markdown = mod.write_markdown(report)
    assert report["verdict"] in markdown
    assert report["decisive_theorem"] in markdown
    assert report["closure_scope"] in markdown
    for heading in (
        "## State",
        "## Closing track",
        "## Verdict",
        "## Decisive theorem",
        "## Closure scope",
        "## Witness",
        "## SM-track science criteria",
        "## Release criteria",
        "## Blockers",
        "## Downstream caveats (decision D5)",
        "## Diagnostic track",
    ):
        assert heading in markdown, heading
    assert "`can_close_G3` = `False`" in markdown
    assert "target_unbroken_algebra_is_standard_model" in markdown
    for caveat in report["downstream_caveats"]:
        assert f"`{caveat['id']}` -> `{caveat['gate']}`" in markdown


def test_each_missing_sm_input_fails_closed():
    ledger_report = _ledger()
    for key, name in sm_track.INPUT_FILES.items():
        for forged_value in ({}, [], None):
            inputs = _sm_inputs()
            inputs[key] = forged_value
            report = mod.build_report(
                ledger_report=ledger_report, sm_track_inputs=inputs
            )
            assert report["overall_state"] == "EXECUTION_FAIL", key
            assert report["n_failed"] > 0
            assert report["classification"]["G3_closed"] is False
            assert report["closing_track"] is None
            assert report["classification"]["closing_track"] is None
            assert report["tracks"][SM]["closed"] is False
            assert name in report["missing_artifacts"], (key, report["missing_artifacts"])
            assert report["missing_artifacts"].count(name) == 1
            assert report["verdict"].startswith(OPEN_VERDICT_PREFIX)
            assert report["remaining_open_problem"].startswith(
                "the SM Pati-Salam track is not certified: "
            )


def test_missing_sm_input_key_fails_closed():
    inputs = _sm_inputs()
    del inputs["exact_hessian"]
    report = mod.build_report(ledger_report=_ledger(), sm_track_inputs=inputs)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["artifact_integrity"]["sm_exact_hessian_report_executes"] is False
    assert "G3_SM_PATI_SALAM_EXACT_HESSIAN_V20.json" in report["missing_artifacts"]
    assert report["classification"]["G3_closed"] is False


def test_forged_sm_required_statement_reopens_g3():
    inputs = _sm_inputs()
    inputs["exact_hessian"]["eps_family"]["final_acceptance_test"][
        "required_statement"
    ] = sm_track.SM_FINAL_THEOREM.replace("V_PS,eps", "V_beta")
    report = mod.build_report(ledger_report=_ledger(), sm_track_inputs=inputs)
    assert report["n_failed"] == 0, report["failures"]
    assert report["overall_state"] == "OPEN"
    assert report["science_criteria"]["sm_decisive_theorem_string_bound"] is False
    assert "sm_decisive_theorem_string_bound" in report["blockers"]
    assert report["classification"]["mathematical_G3_closed"] is False
    assert report["classification"]["G3_closed"] is False
    assert report["closing_track"] is None
    # The decisive theorem is the SM theorem whether or not the track closes.
    assert report["decisive_theorem"] == sm_track.SM_FINAL_THEOREM
    assert report["verdict"].startswith(OPEN_VERDICT_PREFIX)
    assert "sm_decisive_theorem_string_bound" in report["verdict"]
    assert report["verdict"].endswith(mod.OPEN_VERDICT_CHIRAL_TAIL)
    assert "sm_decisive_theorem_string_bound" in report["remaining_open_problem"]


def test_sigma_hypercharge_source_is_shared_by_both_tracks():
    ledger_report, hsx, equality, gap = _current_inputs()
    report = mod.build_report(
        ledger_report=ledger_report,
        hsx_report=hsx,
        equality_report=equality,
        gap_report=gap,
        sigma_hypercharge_report={},
    )
    assert report["missing_artifacts"].count("G3_SIGMA_HYPERCHARGE_AUDIT_V20.json") == 1
    assert report["artifact_integrity"]["sigma_hypercharge_audit_executes"] is False
    assert report["artifact_integrity"]["sm_sigma_hypercharge_audit_executes"] is False
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["classification"]["G3_closed"] is False


def test_ledger_g3_disagreement_blocks_pass():
    ledger_report = _ledger()
    ledger_report["gates"]["G3"]["status"] = "OPEN"
    report = mod.build_report(ledger_report=ledger_report)
    assert report["n_failed"] == 0, report["failures"]
    assert report["release_criteria"]["ledger_G3_status_matches_gate_closure"] is False
    assert "ledger_G3_status_matches_gate_closure" in report["blockers"]
    assert report["overall_state"] == "OPEN"
    assert report["classification"]["mathematical_G3_closed"] is True
    assert report["classification"]["release_G3_verified"] is False
    assert report["classification"]["G3_closed"] is False
    assert report["closing_track"] is None

    ledger_report = _ledger()
    ledger_report["gates"]["G3"]["closing_track"] = CHIRAL
    report = mod.build_report(ledger_report=ledger_report)
    assert report["release_criteria"]["ledger_G3_status_matches_gate_closure"] is False
    assert report["overall_state"] == "OPEN"


def test_ledger_g3_closed_while_sm_track_fails_is_inconsistent():
    inputs = _sm_inputs()
    inputs["candidate"]["flags"]["g3_closed"] = True
    report = mod.build_report(ledger_report=_ledger(), sm_track_inputs=inputs)
    assert report["artifact_integrity"]["sm_reports_do_not_overclaim"] is False
    assert report["overall_state"] == "EXECUTION_FAIL"
    # The committed ledger says CLOSED; this gate's forged SM track does not.
    assert report["release_criteria"]["ledger_G3_status_matches_gate_closure"] is False
    assert report["classification"]["G3_closed"] is False


def test_forged_ledger_health_fails_closed():
    for mutate in (
        lambda ledger_report: ledger_report.__setitem__("n_failed", False),
        lambda ledger_report: ledger_report.__setitem__("n_failed", 1),
        lambda ledger_report: ledger_report.__setitem__("n_failed", 0.0),
        lambda ledger_report: ledger_report.__setitem__("failures", ["forged"]),
        lambda ledger_report: ledger_report.pop("failures"),
    ):
        ledger_report = _ledger()
        mutate(ledger_report)
        report = mod.build_report(ledger_report=ledger_report)
        assert report["artifact_integrity"]["ledger_executes"] is False
        assert report["failures"] == ["ledger_executes"], report["failures"]
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["closing_track"] is None
        assert report["verdict"].startswith(OPEN_VERDICT_PREFIX + "ledger_executes")


def test_chiral_whole_model_exclusion_claim_fails_closed():
    for source, flags_key in (("hsx", "flag"), ("gap", "flags")):
        ledger_report, hsx, equality, gap = map(copy.deepcopy, _current_inputs())
        forged = {"hsx": hsx, "gap": gap}[source]
        forged[flags_key]["whole_model_excluded"] = True
        report = mod.build_report(
            ledger_report=ledger_report,
            hsx_report=hsx,
            equality_report=equality,
            gap_report=gap,
        )
        name = {"hsx": "HSX_audit_executes", "gap": "global_gap_audit_executes"}[source]
        assert report["artifact_integrity"][name] is False, source
        assert report["failures"] == [name], (source, report["failures"])
        assert report["overall_state"] == "EXECUTION_FAIL", source
        # A failed report never also claims G3 closure.
        assert report["classification"]["whole_model_excluded"] is True
        assert report["classification"]["G3_closed"] is False
        assert report["classification"]["closing_track"] is None
        assert report["closing_track"] is None
        assert report["verdict"].startswith(OPEN_VERDICT_PREFIX + name), source


def test_open_verdict_names_integrity_failures_before_blockers():
    inputs = _sm_inputs()
    inputs["candidate"]["n_failed"] = 1
    report = mod.build_report(ledger_report=_ledger(), sm_track_inputs=inputs)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["failures"] == ["sm_candidate_report_executes"]
    assert report["blockers"], report["blockers"]
    reasons = ", ".join(report["failures"] + report["blockers"])
    assert report["verdict"].startswith(OPEN_VERDICT_PREFIX + reasons + "). ")
    assert report["remaining_open_problem"] == (
        "the SM Pati-Salam track is not certified: " + reasons
    )


def test_g3_closed_follows_the_overall_state():
    report = mod.build_report(ledger_report=_ledger())
    assert report["overall_state"] == "PASS"
    assert report["classification"]["G3_closed"] is True
    inputs = _sm_inputs()
    inputs["equality_set"]["n_failed"] = 1
    report = mod.build_report(ledger_report=_ledger(), sm_track_inputs=inputs)
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["classification"]["G3_closed"] is False
    assert report["classification"]["closing_track"] is None


def test_g5_coupling_vector_mismatch_blocks_pass():
    ledger_report = _ledger()
    coefficients = ledger_report["gates"]["G5"]["bfb_coupling_vector"]["coefficients"]
    assert len(coefficients) == 27
    first = sorted(coefficients)[0]
    coefficients[first] = coefficients[first] + "1"
    report = mod.build_report(ledger_report=ledger_report)
    assert report["n_failed"] == 0, report["failures"]
    assert report["release_criteria"][
        "G5_BFB_evidence_covers_closing_coupling_vector"
    ] is False
    assert "G5_BFB_evidence_covers_closing_coupling_vector" in report["blockers"]
    assert report["overall_state"] == "OPEN"
    assert report["classification"]["G3_closed"] is False

    for mutate in (
        lambda gates: gates["G5"].__setitem__("status", "OPEN"),
        lambda gates: gates["G5"]["bfb_coupling_vector"].__setitem__("certified", False),
        lambda gates: gates["G5"].pop("bfb_coupling_vector"),
    ):
        ledger_report = _ledger()
        mutate(ledger_report["gates"])
        report = mod.build_report(ledger_report=ledger_report)
        assert report["release_criteria"][
            "G5_BFB_evidence_covers_closing_coupling_vector"
        ] is False
        assert report["overall_state"] == "OPEN"


def test_uncertified_sm_bfb_binding_blocks_g5_release_criterion():
    inputs = _sm_inputs()
    inputs["candidate"]["exact_certificate"]["exact_quartic_bound"]["constant"] = "1/168"
    report = mod.build_report(ledger_report=_ledger(), sm_track_inputs=inputs)
    assert report["tracks"][SM]["g5_bfb_binding"]["certified"] is False
    assert report["science_criteria"]["sm_full_homogeneous_quartic_BFB_exact"] is False
    assert report["release_criteria"][
        "G5_BFB_evidence_covers_closing_coupling_vector"
    ] is False
    assert report["classification"]["G3_closed"] is False
    assert report["overall_state"] != "PASS"


def test_unpromoted_contract_blocks_release():
    ledger_report = _ledger()
    ledger_report["contract_consistent"] = False
    ledger_report["gates"]["G1"]["status"] = mod.ledger.STATUS_BLOCKED
    report = mod.build_report(ledger_report=ledger_report)
    assert report["release_criteria"][
        "authoritative_external_model_contract_executed"
    ] is False
    assert report["release_criteria"]["G1_promoted_closed"] is False
    assert report["tracks"][SM]["release_prerequisites"][
        "G1_promoted_closed"
    ] is False
    assert report["overall_state"] == "OPEN"
    assert report["classification"]["G3_closed"] is False


def test_chiral_lower_witness_is_reported_in_its_track_only():
    ledger_report, hsx, equality, gap = map(copy.deepcopy, _current_inputs())
    gap["flags"]["lower_witness_found"] = True
    report = mod.build_report(
        ledger_report=ledger_report,
        hsx_report=hsx,
        equality_report=equality,
        gap_report=gap,
    )
    assert _chiral(report)["candidate_exactly_rejected"] is True
    assert report["classification"]["candidate_exactly_rejected"] is False
    assert report["classification"]["whole_model_excluded"] is False
    assert report["classification"]["theory_still_viable"] is True
    assert report["overall_state"] == "PASS"
    assert report["closing_track"] == SM


def test_rank1_slice_rejects_wrong_fixed_H_orientation():
    forged = copy.deepcopy(mod._load(mod.MAX_NEGATIVE_RANK1_SU3_SLICE_JSON))
    forged["scope"]["H_fixed_to_h_minus"] = False
    report = mod.build_report(
        ledger_report=_ledger(), max_negative_rank1_su3_slice_report=forged
    )
    assert report["artifact_integrity"][
        "max_negative_rank1_SU3_four_dimensional_slice_audit_executes_fail_closed"
    ] is False
    assert _chiral(report)["science_criteria"][
        "rank1_SU3_four_dimensional_slice_gap_certified_without_closing_G3"
    ] is False
    assert report["overall_state"] == "EXECUTION_FAIL"
    assert report["classification"]["G3_closed"] is False
    assert report["closing_track"] is None


def test_decisive_theorem_is_the_sm_eps_theorem_and_chiral_keeps_its_own():
    report = mod.build_report()
    assert report["decisive_theorem"] == sm_track.SM_FINAL_THEOREM
    assert mod.SM_FINAL_THEOREM == sm_track.SM_FINAL_THEOREM
    assert mod.DECISIVE_THEOREM == mod.SM_FINAL_THEOREM
    assert mod.CHIRAL_H_FINAL_THEOREM == mod.FINAL_THEOREM
    assert "V_PS,eps(q)-V_PS,eps(q0)>=0" in report["decisive_theorem"]
    assert _chiral(report)["decisive_theorem"] == mod.FINAL_THEOREM
    assert "V_beta(q)-V_beta(q0)>=0" in mod.FINAL_THEOREM
    for theorem in (report["decisive_theorem"], mod.FINAL_THEOREM):
        assert "every 486-real field" in theorem
        assert "SO(10)xU(1)_XxPQ orbit" in theorem
        assert "equality holds exactly on" in theorem
    assert report["decisive_theorem"] == report["tracks"][SM]["decisive_theorem"]


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
    assert _chiral(report)["science_criteria"][
        "full_Hessian_rank_448_nullity_38_exact"
    ] is False


def _forge_all_chiral_proof_contracts():
    ledger_report, hsx, equality, gap = map(copy.deepcopy, _current_inputs())
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
    sigma = copy.deepcopy(mod._load(mod.SIGMA_HYPERCHARGE_JSON))
    sigma["flags"]["certified_g3_point_is_sm_vacuum"] = True
    return dict(
        ledger_report=ledger_report,
        hsx_report=hsx,
        equality_report=equality,
        gap_report=gap,
        exact_hessian_report=exact_hessian,
        sigma_hypercharge_report=sigma,
    )


def test_chiral_track_can_never_close_g3():
    kwargs = _forge_all_chiral_proof_contracts()
    report = mod.build_report(**kwargs)
    chiral = _chiral(report)
    assert report["n_failed"] == 0, report["failures"]
    assert all(chiral["science_criteria"].values())
    assert all(chiral["release_criteria"].values())
    assert chiral["mathematical_criteria_all_true"] is True
    assert chiral["blockers"] == []
    assert chiral["can_close_G3"] is False
    # Whatever the chiral track says, closure is attributed to the SM track.
    assert report["closing_track"] in (SM, None)
    assert report["decisive_theorem"] == sm_track.SM_FINAL_THEOREM

    # With the SM track failing, the forged chiral track cannot close G3.
    inputs = _sm_inputs()
    inputs["exact_hessian"]["eps_family"]["final_acceptance_test"][
        "required_statement"
    ] = mod.FINAL_THEOREM
    report = mod.build_report(**kwargs, sm_track_inputs=inputs)
    chiral = _chiral(report)
    assert report["n_failed"] == 0, report["failures"]
    assert chiral["mathematical_criteria_all_true"] is True
    assert chiral["can_close_G3"] is False
    assert report["overall_state"] != "PASS"
    assert report["overall_state"] == "OPEN"
    assert report["closing_track"] is None
    assert report["classification"]["G3_closed"] is False
    assert report["classification"]["mathematical_G3_closed"] is False
    assert "sm_decisive_theorem_string_bound" in report["blockers"]


def test_rank_counts_alone_cannot_certify_a_standard_model_target():
    """The chiral point's orbit ranks are exact but its stabilizer is not the SM."""
    report = mod.build_report()
    chiral = _chiral(report)
    assert chiral["science_criteria"][
        "target_symmetry_orbit_ranks_36_37_38_exact"
    ] is True
    assert chiral["science_criteria"][
        "target_unbroken_algebra_is_standard_model"
    ] is False
    assert "target_unbroken_algebra_is_standard_model" in chiral["blockers"]
    assert "target_unbroken_algebra_is_standard_model" not in report["blockers"]
    assert report["artifact_integrity"]["sigma_hypercharge_audit_executes"] is True
    assert "Y=-1" in chiral["why_not_a_closure_route"]
    assert report["science_criteria"][
        "sm_target_unbroken_algebra_is_standard_model_exact"
    ] is True


def test_rank1_slice_false_flags_are_fail_closed():
    forged = copy.deepcopy(mod._load(mod.MAX_NEGATIVE_RANK1_SU3_SLICE_JSON))
    forged["checks"]["arbitrary_Sigma35_proved"] = True
    report = mod.build_report(
        ledger_report=_ledger(), max_negative_rank1_su3_slice_report=forged
    )
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
            ledger_report=_ledger(),
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
            "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
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
            ledger_report=_ledger(),
            rank1_su4_augmented_sos_psd_target_report=forged,
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
        ] is False


def test_rank1_su4_stage2_mutations_are_fail_closed():
    aligned = mod._load(mod.RANK1_SU4_ALIGNED_CARRIERS_JSON)

    forged_aligned = copy.deepcopy(aligned)
    forged_aligned["alignment"]["concatenated_aligned_basis_rank_mod_prime"] = 209
    report = mod.build_report(
        ledger_report=_ledger(), rank1_su4_aligned_carriers_report=forged_aligned
    )
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
    ledger_report = _ledger()
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
            ledger_report=ledger_report,
            rank1_su4_augmented_sos_cubic_map_report=forged,
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
            "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
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
            ledger_report=ledger_report,
            rank1_su4_augmented_sos_cubic_map_report=forged,
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_cubic_map_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
        ] is False


def test_rank1_su4_augmented_census_mutations_are_fail_closed():
    census = mod._load(mod.RANK1_SU4_AUGMENTED_SOS_CENSUS_JSON)
    quadratic = mod._load(mod.RANK1_SU4_PHI210_QUADRATIC_BASIS_JSON)
    ledger_report = _ledger()
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
        report = mod.build_report(
            ledger_report=ledger_report,
            rank1_su4_augmented_sos_census_report=forged,
        )
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
        ledger_report=ledger_report,
        rank1_su4_phi210_quadratic_basis_report=forged_quadratic,
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
        "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
    ] is False


def test_rank1_su4_augmented_quartic_mutations_cascade_fail_closed():
    quartic = mod._load(mod.RANK1_SU4_AUGMENTED_SOS_QUARTIC_MAP_JSON)
    ledger_report = _ledger()
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
            ledger_report=ledger_report,
            rank1_su4_augmented_sos_quartic_map_report=forged,
        )
        assert report["overall_state"] == "EXECUTION_FAIL"
        assert report["classification"]["G3_closed"] is False
        assert report["artifact_integrity"][
            "rank1_SU4_augmented_SOS_quartic_map_executes_fail_closed"
        ] is False
        assert report["artifact_integrity"][
            "rank1_SU4_legacy_v20_PSD_target_is_rejected_fail_closed"
        ] is False
