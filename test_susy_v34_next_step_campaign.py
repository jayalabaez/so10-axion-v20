from __future__ import annotations

import math
import subprocess
import sys
from fractions import Fraction

import susy_v34_next_step_campaign as v34


REPORT, EVIDENCE = v34.build_bundle()
G1 = EVIDENCE[v34.G1_JSON.name]
G6 = EVIDENCE[v34.G6_JSON.name]
REPAIRS = EVIDENCE[v34.REPAIRS_JSON.name]
GATES = EVIDENCE[v34.GATES_JSON.name]


def test_exact_visible_z33_dai_freed_obstruction() -> None:
    anomaly = G1["bare_visible_Z33"]
    rows = anomaly["charged_Weyl_rows"]

    assert [row["field"] for row in rows] == ["PsiBar", "PsiCBar", "P"]
    assert [row["Weyl_multiplicity"] for row in rows] == [8, 8, 1]
    assert anomaly["Delta_s1"] == -15
    assert anomaly["Delta_s3"] == -15
    assert anomaly["Hsieh_conditions"] == {
        "cubic_modulus_3n": 99,
        "cubic_residue": 84,
        "linear_modulus_n": 33,
        "linear_residue": 18,
        "doubled_linear_numerator_residue": 3,
        "both_vanish": False,
    }
    assert anomaly["Dai_Freed_eta_phases_mod_one"] == {
        "X_n_1_1_cubic": "28/33",
        "L_n_1_times_K3_gravity": "1/11",
        "both_zero": False,
    }
    assert anomaly["required_additive_counterclass"] == {
        "cubic": "5/33",
        "gravity": "10/11",
    }
    assert anomaly["ordinary_4D_local_counterterm_sufficient"] is False
    assert anomaly["bare_visible_Z33_gaugeable"] is False


def test_conditional_gs_arithmetic_and_coprime_cross_class() -> None:
    audit = G1["conditional_GS_and_coprime_product"]
    product = audit["product_generator_h_equals_g4_times_g33"]
    cross = audit["coprime_cross_term_reduction"]

    assert audit["Z4R"]["doubled_representatives_4_L_R"] == [14, 10, 2]
    assert audit["Z4R"]["universal_residue_mod4"] == [2, 2, 2]
    assert audit["Z33"]["doubled_representatives_4_L_R"] == [-4, -4, -4]
    assert audit["Z33"]["universal_residue_mod33"] == [29, 29, 29]
    assert product["half_normalized_representatives_4_L_R"] == [223, 157, 25]
    assert product["universal_residue_mod66"] == [25, 25, 25]
    assert product["universal_residue_mod132"] == [50, 50, 50]
    assert product["gravitational_half_normalized"] == 600
    assert product["equal_level_gauge_gravity_congruence"] is True
    assert product["period_one_axion_shift"] == "-25/66"
    assert product["Z4_generator_restriction_mod_one"] == "1/2"
    assert product["Z33_generator_restriction_mod_one"] == "4/33"

    assert cross["coefficient_of_q_times_rfermion_squared"] == 13068
    assert cross["coefficient_of_q_squared_times_rfermion"] == 1584
    assert cross["combined_cross_contribution"] == -771012
    assert cross["combined_cross_contribution_over_modulus"] == -1947
    assert cross["combined_cross_residue_mod396"] == 0
    assert cross["independent_finite_product_anomaly"] is False
    assert audit["pure_finite_Dai_Freed_counterclass_realized"] is False


def test_minimal_algebraic_uv_fermion_counterclass_is_exhaustive() -> None:
    candidate = G1["minimal_UV_fermion_counterclass_candidate"]

    assert candidate["solution_counts_by_number_of_new_fermions"] == {
        "1": 0,
        "2": 0,
        "3": 1,
    }
    assert candidate["minimal_number"] == 3
    assert candidate["minimality_scope"].startswith(
        "free unit-multiplicity PS-singlet Weyl counterclasses"
    )
    assert candidate["minimal_unique_charge_witness"] == [20, 29, 32]
    assert candidate["witness_linear_residue_mod33"] == 15
    assert candidate["witness_cubic_residue_mod99"] == 15
    assert candidate["cancels_visible_residues"] is True
    assert candidate["PS_mixed_gauge_anomalies_added"] == 0
    assert candidate["Z4R_superfield_charges_and_full_product_anomaly_solved"] is False
    assert candidate["adopted_into_active_source"] is False


def test_instanton_prefactors_destroy_uniform_truncation_control() -> None:
    flux = G1["instanton_and_flux_compatibility"]

    assert flux["K"] == 22027
    assert math.isclose(flux["x_star"], 1.0 / 22027, rel_tol=0.0, abs_tol=1e-20)
    assert math.isclose(flux["weighted_expansion_variable_Kx"], 1.0)
    assert flux["local_polynomial_expanded"] == "W=A1*x+A2*x^2+A3*x^3"
    assert flux["selected_branch_coefficient_values_over_C"] == [
        1,
        -2 * flux["K"],
        flux["K"] ** 2,
    ]
    assert math.isclose(flux["hypothetical_K3_x4_relative_to_leading"], 1.0)
    assert flux["order_one_x4_relative_to_leading"] < 1.0e-13
    assert flux["uniform_all_harmonic_prefactor_bound_derived"] is False
    assert flux["semiclassical_truncation_control_established"] is False
    assert flux["rank_51_statement"]["local_diagonal_rank_if_51_independent_Ci_nonzero"] == 51
    assert flux["rank_51_statement"]["independent_primitive_divisor_directions_derived"] is False


def test_charged_flux_leaves_only_z2_and_allows_a_p_tadpole() -> None:
    flux = G1["instanton_and_flux_compatibility"]
    rows = flux["minimal_spurion_dressed_P_rows"]

    assert flux["exact_nonzero_coefficient_stabilizer_elements_a_mod4_b_mod33"] == [
        [0, 0],
        [2, 0],
    ]
    assert flux["stabilizer_is_only_residual_Z2"] is True
    assert flux["Z33_preserved_on_charged_flux_branch"] is False
    assert rows["P1"] == {
        "P_power": 1,
        "coefficient_insertions": 6,
        "C1_power": 0,
        "C2_power": 2,
        "C3_power": 4,
    }
    assert rows["P27"]["C3_power"] == 1
    assert rows["P31"]["C1_power"] == 1
    assert rows["P33"]["coefficient_insertions"] == 0
    assert flux["explicit_lowest_operator"] == "C2^2 C3^4 P"
    assert flux["undressed_pure_P_monomial_still_begins_at_P33"] is True
    assert flux["P33_remains_first_visible_P_power_after_spurion_VEVs"] is False
    assert flux["charged_flux_compatible_with_exact_Z33_quality"] is False


def test_independent_group_theory_exactly_matches_raw_sarah() -> None:
    independent = G6["independent_group_theory"]
    projected = G6["normalized_projection_of_frozen_V33_SARAH"]
    checks = G6["cross_checks"]

    assert independent["group_order"] == ["SU4", "SU2L", "SU2R"]
    assert independent["sum_Dynkin"] == [13, 11, 15]
    assert independent["adjoint_Casimirs"] == [4, 2, 2]
    assert independent["b"] == projected["b"] == [1, 5, 9]
    assert independent["B"] == projected["B"] == [
        [108, 15, 21],
        [75, 53, 3],
        [105, 3, 81],
    ]
    assert checks["raw_minus_independent_b"] == [0, 0, 0]
    assert checks["raw_minus_independent_B"] == [[0, 0, 0]] * 3
    assert checks["raw_matches_independent_exactly"] is True
    assert checks["raw_matches_V24_b"] is True
    assert checks["raw_matches_V24_B"] is True


def test_all_three_gauge_rows_match_independent_yukawa_norm_reference() -> None:
    projected = G6["normalized_projection_of_frozen_V33_SARAH"]
    reference = G6["independent_Yukawa_invariant_norm_reference"]
    coefficients = projected["Yukawa_subtraction_coefficients"]
    expected = {
        "kappaPS": [4, 0, 8],
        "lambdaH": [0, 2, 2],
        "lambdaSigma": [2, 0, 0],
        "lambdaS": [5, 0, 6],
        "lambdaSb": [5, 0, 6],
        "YQQ": [8, 16, 16],
        "YQX": [8, 16, 16],
        "YXQ": [8, 16, 16],
        "YXX": [8, 16, 16],
        "lambdaPQ": [4, 8, 0],
        "lambdaPX": [4, 8, 0],
        "lambdaPcQ": [4, 0, 8],
        "lambdaPcX": [4, 0, 8],
        "yNQ": [4, 0, 8],
        "yNX": [4, 0, 8],
        "kappaX": [0, 0, 0],
    }

    assert coefficients == expected
    assert coefficients == reference["coefficient_vectors_4_L_R"]
    assert G6["cross_checks"][
        "projected_Yukawa_coefficients_match_independent_norm_reference"
    ] is True
    assert projected["all_Yukawa_subtraction_coefficients_nonnegative"] is True
    assert projected[
        "all_raw_gauge_dummy_symbols_removed_by_normalized_projector"
    ] is True
    assert projected["linearity_replayed_at_two_rational_points"] is True
    assert projected["literal_component_Gram_projection_executed"] is False
    assert projected["live_V34_SARAH_execution"] is False
    assert projected["raw_BetaY_invariant_projection_complete"] is False
    norm = G6["cross_checks"]["ScScSigma_invariant_norm_check"]
    assert norm["InvMat2_squared_norm"] * norm["epsilon2_squared_norm"] == 12
    assert norm["lambdaS_coefficient_vector"] == [5, 0, 6]


def test_boundary_diagnostic_does_not_invent_ps_couplings() -> None:
    boundary = G6["boundary_diagnostic"]
    trace = boundary["V31_fitted_neutrino_Dirac_trace_YdagY"]

    assert math.isclose(trace, 0.16789741344867715, rel_tol=0.0, abs_tol=2e-16)
    expected = [8.0 * trace, 16.0 * trace, 16.0 * trace]
    assert boundary["conditional_if_numerically_identified_with_PS_scale_YQQ"] == expected
    assert boundary["structural_YQQ_neutrino_Dirac_role_in_PS_source"] is True
    assert boundary[
        "numerical_PS_scale_identification_with_V31_matrix_is_source_derived"
    ] is False
    assert boundary["PS_scale_values_for_16_dimensionless_trilinears_present"] is False
    assert boundary["below_PS_coupled_Yukawa_EFT_and_matching_present"] is False
    assert boundary["unique_coupled_numerical_solution_exists"] is False


def test_conditional_threshold_bridge_replays_but_is_not_adopted() -> None:
    bridge = G6["conditional_new_physics_threshold_bridge"]
    target = bridge["target_Delta_alpha_inverse_4_L_R"]
    replay = bridge["replayed_Delta_alpha_inverse_4_L_R"]
    corrected = bridge["corrected_alpha_inverse_4_L_R"]

    assert [row["Delta_b_4_L_R"] for row in bridge["multiplets"]] == [
        [2, 0, 0],
        [0, 4, 0],
        [0, 0, 4],
    ]
    assert bridge["renormalizable_pair_mass_charge_sum_mod132"] == 66
    assert bridge["component_fermion_charges_each_pair"] == [99, 33]
    assert bridge["each_pair_discrete_anomaly_vectorlike"] is True
    assert bridge["exact_numerical_replay_closes_target"] is True
    assert bridge["target_boundary_repair_derived_from_source"] is False
    assert bridge["minimum_zero_sum_target_convention_used"] is True
    assert all(math.isclose(a, b, rel_tol=0.0, abs_tol=2e-15) for a, b in zip(replay, target))
    assert max(corrected) - min(corrected) < 4.0e-15
    assert bridge["maximum_to_minimum_mass_ratio"] < 2.7
    assert all(mass > 0.0 for mass in bridge["solved_masses_GeV"])
    assert bridge["conditional_leading_log_threshold_existence_proved"] is True
    assert bridge["six_chiral_witness_minimality_proved"] is False
    smaller = bridge[
        "four_chiral_nonminimality_counterexample_without_zero_sum_convention"
    ]
    assert smaller["pairs_used"] == ["A4+A4c", "AL+ALc"]
    assert smaller["replays_common_value"] is True
    assert len(smaller["masses_GeV"]) == 2
    assert bridge["SO10_split_multiplet_embedding_derived"] is False
    assert bridge["adopted_into_active_model"] is False
    assert bridge["precision_unification_closed"] is False


def test_strict_gate_ledger_and_new_physics_scope() -> None:
    assert GATES["materially_updated_frontiers"] == ["G1", "G5", "G6"]
    assert GATES["materially_updated_frontier_count"] == 3
    assert GATES["established_full_predictive_closed_count"] == 0
    assert GATES["complete_theory_exists"] is False
    assert len(GATES["gates"]) == 8
    assert all(row["established_full_predictive_closed"] is False for row in GATES["gates"])
    assert REPAIRS["active_source_changed"] is False
    assert REPAIRS["safe_to_claim_new_fundamental_law"] is False
    assert REPAIRS["rejected_combination"]["rejected"] is True
    assert REPORT["summary"][
        "frozen_SARAH_gauge_rows_normalized_projector_applied"
    ] is True
    assert REPORT["summary"][
        "gauge_row_Yukawa_coefficients_match_independent_norm_reference"
    ] is True
    assert REPORT["summary"]["coupled_G6_solution_exists"] is False
    assert REPORT["summary"]["complete_theory_exists"] is False


def test_frozen_outputs_replay() -> None:
    completed = subprocess.run(
        [sys.executable, "-B", str(v34.ROOT / "susy_v34_next_step_campaign.py"), "--check"],
        cwd=v34.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert REPORT["core_sha256"] in completed.stdout
