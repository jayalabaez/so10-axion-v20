from __future__ import annotations

import subprocess
import sys
from fractions import Fraction

import susy_v36_redesign_campaign as v36


REPORT, EVIDENCE = v36.build_bundle()
G1 = EVIDENCE[v36.G1_JSON.name]
VACUUM = EVIDENCE[v36.VACUUM_JSON.name]
MATCHING = EVIDENCE[v36.MATCHING_JSON.name]
GATES = EVIDENCE[v36.GATES_JSON.name]


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    work = [row[:] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(row for row in range(column, len(work)) if work[row][column])
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result *= -1
        value = work[column][column]
        result *= value
        work[column] = [entry / value for entry in work[column]]
        for row in range(column + 1, len(work)):
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[column], strict=True)
            ]
    return result


def test_exact_z66_hsieh_dai_freed_conditions_close() -> None:
    finite = G1["selector"]["Hsieh_Dai_Freed"]
    assert finite["linear_condition_2Delta_s1_mod66"] == 0
    assert finite["cubic_condition_numerator_mod396"] == 0
    assert finite["both_vanish"] is True
    subgroup = G1["selector"]["Z33_subgroup_signed_audit"]
    assert subgroup["visible_Delta_s1"] == subgroup["visible_Delta_s3"] == -15
    assert subgroup["counter_Delta_s1"] == 15
    assert subgroup["counter_Delta_s3"] % 99 == 15
    assert subgroup["linear_residue_mod33"] == 0
    assert subgroup["cubic_residue_mod99"] == 0


def test_z66_is_single_selector_with_residual_anomalon_parity() -> None:
    breaking = G1["selector"]["spontaneous_breaking"]
    assert breaking["P_q66"] == 2
    assert breaking["Pbar_q66"] == 64
    assert breaking["unbroken_subgroup_order"] == 2
    assert breaking["all_anomalons_odd"] is True
    assert breaking["all_original_fields_even"] is True
    census = VACUUM["renormalizable_completeness"]
    assert census["dangerous_P_A32_allowed"] is False


def test_five_anomalons_are_exhaustively_minimal_for_full_rank_masses() -> None:
    result = G1["minimal_countersector"]
    assert result["exhaustive_counts"] == {
        "1": {"anomaly_candidates": 0, "generic_full_rank_candidates": 0},
        "2": {"anomaly_candidates": 1, "generic_full_rank_candidates": 0},
        "3": {"anomaly_candidates": 6, "generic_full_rank_candidates": 0},
        "4": {"anomaly_candidates": 68, "generic_full_rank_candidates": 0},
        "5": {"anomaly_candidates": 447, "generic_full_rank_candidates": 5},
    }
    assert result["all_minimal_full_rank_witnesses"] == [
        [2, 6, 16, 26, 32],
        [2, 15, 16, 17, 32],
        [5, 8, 16, 26, 27],
        [9, 14, 16, 20, 23],
        [12, 14, 16, 20, 20],
    ]
    assert result["selected_q66_CRT_lift"] == [37, 63, 65, 1, 31]


def test_anomalon_mass_determinant_is_full_rank() -> None:
    a, b, c, d, mu = map(Fraction, (2, 3, 5, 7, 11))
    matrix = [
        [0, 0, 0, 0, a],
        [0, 0, 0, b, 0],
        [0, 0, c, mu, 0],
        [0, b, mu, d, 0],
        [a, 0, 0, 0, 0],
    ]
    assert determinant([[Fraction(value) for value in row] for row in matrix]) == a**2 * b**2 * c
    assert G1["minimal_countersector"]["determinant"] == "a^2*b^2*c"


def test_complete_renormalizable_singlet_census_and_pq() -> None:
    census = VACUUM["renormalizable_completeness"]
    assert census["allowed_count"] == 14
    assert census["anomalon_containing_count"] == 5
    assert census["anomalon_containing_monomials"] == [
        ["A17", "A16"],
        ["P", "A15", "A17"],
        ["P", "A16", "A16"],
        ["Pbar", "A2", "A32"],
        ["Pbar", "A17", "A17"],
    ]
    assert census["all_32_unique_displayed_W_structures_have_Z66_charge_zero"] is True
    assert census["all_32_unique_displayed_W_structures_have_Z4R_charge_two"] is True
    assert census["all_32_unique_displayed_W_structures_preserve_accidental_PQ"] is True


def test_quality_distinguishes_pure_vev_and_full_operator_ring() -> None:
    pure = VACUUM["pure_vev_selector"]
    assert pure["minimum_superpotential_degree"] == 33
    assert pure["minimum_exponent_pairs_P_Pbar"] == [[0, 33], [33, 0]]
    ring = VACUUM["full_singlet_operator_ring"]
    assert ring["first_breaking_degree"] == 10
    assert [row["multiplicities"] for row in ring["first_breaking_operators"]] == [
        {"A17": 1, "A2": 7, "P": 2},
        {"A15": 1, "A2": 9},
    ]
    assert ring["all_first_operators_contain_heavy_anomalons"] is True
    assert ring["vanish_on_classical_Ai_zero_vacuum"] is True
    assert VACUUM["benchmark_quality"]["passes_abs_theta_below_1e-10"] is True
    assert VACUUM["full_quality_boundary"]["quality_gate_closed"] is False


def test_two_driver_local_vacuum_rank_is_not_global_closure() -> None:
    radial = VACUUM["two_driver_radial_system"]
    assert radial["driver_radial_holomorphic_Hessian_rank"] == 4
    assert radial["expected_remaining_chiral_PQ_Goldstone_multiplet"] == 1
    assert radial["saxion_and_global_vacuum_selection_derived"] is False


def test_direct_charged_anomaly_repair_is_rejected_for_physics() -> None:
    candidate = REPORT["rejected_direct_charged_repair"]
    assert candidate["finite_and_mixed_Z33_anomalies_cancel"] is True
    assert candidate["visible_mixed_PQ_PS_anomaly"] == [-2, -2, -2]
    assert candidate["new_mixed_PQ_PS_anomaly"] == [2, 2, 2]
    assert candidate["surviving_QCD_PQ_anomaly"] == 0
    assert candidate["verdict"].startswith("rejected")

    no_go = REPORT["no_GS_charged_completion_no_go"]
    assert no_go["representation_independent_lower_bound_Delta_b"] == [29, 29, 29]
    assert no_go["minimum_completed_one_loop_b_4_L_R"] == [30, 34, 38]
    assert max(no_go["optimistic_pole_ratio_Lambda_over_vPS"]) < 25
    assert no_go["required_cutoff_ratio"] == 100
    assert no_go["physically_viable_GS_elimination_under_scope"] is False


def test_live_sarah_v36_rge_attestation_is_current() -> None:
    rge = MATCHING["RGE"]
    assert rge["model"] == "PSZ4RZ66SUSYV36"
    assert rge["tool"] == "SARAH 4.15.3"
    assert rge["model_initialized"] is True
    assert rge["two_loop_RGE_calculation_succeeded"] is True
    assert rge["counts_match"] is True
    assert rge["soft_terms_intentionally_disabled"] is True
    assert len(rge["attestation_sha256"]) == 64


def test_matching_contract_has_no_free_threshold_escape_hatch() -> None:
    threshold = MATCHING["one_loop_vectorlike_thresholds"]
    assert threshold["Delta_b_L_GUT_normalized_1_2_3"] == ["4/5", 4, 2]
    assert threshold["Delta_b_R_GUT_normalized_1_2_3"] == ["16/5", 0, 2]
    assert threshold["sum"] == [4, 4, 4]
    assert threshold["independent_ad_hoc_Delta_a_allowed"] is False
    policy = MATCHING["higher_dimensional_gauge_kinetic_and_Kahler_policy"]
    assert policy["unbounded_threshold_knobs_forbidden"] is True
    assert MATCHING["physical_matching_complete"] is False


def test_gate_ledger_is_honest_about_conditional_g1_and_full_count() -> None:
    assert GATES["complete_theory_exists"] is False
    assert GATES["declared_4D_EFT_closed_count"] == 0
    assert GATES["established_full_predictive_closed_count"] == 0
    g1 = next(row for row in GATES["gates"] if row["gate"] == "G1")
    assert g1["closed_at_declared_4D_EFT_level"] is False
    assert g1["established_full_predictive_closed"] is False
    assert len(g1["closed_subproblems"]) == 3
    assert "bordism" in g1["remaining_promotion_requirement"]


def test_generated_bundle_replays_byte_for_semantic_byte() -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(v36.ROOT / "susy_v36_redesign_campaign.py"), "--check"],
        cwd=v36.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "V36_REDESIGN_CHECK PASS" in result.stdout
