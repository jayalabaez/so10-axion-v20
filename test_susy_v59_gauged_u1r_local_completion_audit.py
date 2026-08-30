from __future__ import annotations

import json

import susy_v59_gauged_u1r_local_completion_audit as audit


def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def fixed_point(value: dict, name: str) -> dict:
    return next(
        row
        for row in value["fixed_point_mixed_U1R_gauge_anomaly_ledger"]
        if row["fixed_point"] == name
    )


def test_upstream_cores_and_v59_core_are_canonical() -> None:
    value = report()
    assert value["input_core_hashes"] == audit.EXPECTED_CORES
    assert value["core_sha256"] == audit.canonical_sha(value)
    assert value["integrity_checks"][
        "bound_V56_V57_cores_are_canonical_and_expected"
    ]


def test_reconstructed_integrated_seed_is_exact() -> None:
    seed = report()["integrated_u1r_seed"]
    assert seed["spectrum"] == {
        "T": 1,
        "V": 46,
        "H": 290,
        "H_minus_V_plus_29T": 273,
        "gravitational_irreducible_cancels": True,
    }
    assert seed["charge_sums"] == {
        "S1": 290,
        "S2": 926,
        "S4": 8054,
        "q_average": "1",
        "q10_square_sum": 2,
    }
    polynomial = seed["anomaly_polynomial"]
    assert polynomial["coefficients"] == ["1", "-150", "1", "5336", "-24", "-2"]
    assert polynomial["expanded_factorization_coefficients"] == polynomial["coefficients"]
    assert polynomial["factorization_exact"]


def test_integrated_lattice_and_positive_chamber_are_exact() -> None:
    seed = report()["integrated_u1r_seed"]
    lattice = seed["string_charge_lattice"]
    assert lattice["Omega"] == [[1, 0], [0, -1]]
    assert lattice["a"] == [3, 1]
    assert lattice["b_Spin10"] == [0, -2]
    assert lattice["bar_b_R"] == [26, 3]
    assert lattice["pairings"] == {
        "a_squared": 8,
        "a_dot_b_Spin10": 2,
        "b_Spin10_squared": -4,
        "a_dot_bar_b_R": 75,
        "b_Spin10_dot_bar_b_R": 6,
        "bar_b_R_squared": 667,
    }
    assert lattice["a_characteristic"]
    assert lattice["integral_unimodular"]
    assert seed["positive_chamber"]["j_squared"] == "1"
    assert seed["positive_chamber"]["j_dot_b_Spin10"] == "8/3"
    assert seed["positive_chamber"]["all_declared_kinetic_pairings_positive"]


def test_formal_moment_map_solution_is_exact_but_not_a_residual_group_proof() -> None:
    value = report()
    vacuum = value["integrated_u1r_seed"]["formal_rank_one_vacuum"]
    assert vacuum["equation_exact"]
    assert vacuum["unrescaled_tangent_weights"] == [144, 148]
    assert vacuum["formal_gcd"] == 4
    residual = value["residual_Z4R_normalization_audit"]
    assert residual["required_4D_convention"]["q_theta"] == 1
    assert not residual["faithful_residual_Z4R_proved"]


def test_all_singlets_have_a_constructive_VEV_compatible_parity_assignment() -> None:
    solution = report()["singlet_parity_solution"]
    assert solution["all_270_singlets_assigned"]
    assert solution["q0_global_zero_mode_count"] == 1
    assert solution["q4_global_zero_mode_count"] == 1
    assert solution["no_other_singlet_zero_modes"]
    assert solution["non_VEV_spectator_pairs_cancel_pointwise"]
    assert solution["local_parity_moments"] == {
        "sum_sign": [2, 2, 2, 2],
        "sum_q_sign": [4, 4, 4, 4],
        "sum_q_cubed_sign": [64, 64, 64, 64],
    }


def test_V56_two_ten_local_trace_is_derived_from_the_component_ledger() -> None:
    tens = report()["V56_two_ten_parity_trace"]
    assert tens["trace_of_local_parity_in_10"] == {
        "H10": [10, 0, 0, -2],
        "H10_prime": [10, 0, 0, -2],
    }
    assert tens["combined_trace"] == [20, 0, 0, -4]
    assert tens["U1R_linear_and_cubic_contribution_for_q10_minus1"] == [
        -20,
        0,
        0,
        4,
    ]
    assert tens["matches_V56_projector"]


def test_SO10_point_has_no_ratio_obstruction() -> None:
    row = fixed_point(report(), "O_SO10")
    assert row["local_mixed_anomaly_coefficients"] == [6]
    assert row["bulk_tr10_restriction_coefficients"] == [1]
    assert row["two_by_two_minors"] == {}
    assert row["lies_in_existing_bulk_GS_direction"]


def test_GG_and_flipped_points_fail_the_existing_bulk_GS_direction() -> None:
    value = report()
    gg = fixed_point(value, "O_GG")
    assert gg["local_mixed_anomaly_coefficients"] == [4, -320]
    assert gg["bulk_tr10_restriction_coefficients"] == [2, 40]
    assert gg["two_by_two_minors"] == {"SU5_squared__X_squared": 800}
    assert gg["bulk_only_minor"] == 800
    assert gg["sources"]["brane_X_Xbar_raw_4D"] == [0, -200]
    assert gg["minor_after_positive_brane_weight"] == "800 + 400 c_brane > 0"
    assert gg["all_positive_brane_delta_normalizations_fail"]
    assert not gg["lies_in_existing_bulk_GS_direction"]

    flipped = fixed_point(value, "O_flipped")
    assert flipped["local_mixed_anomaly_coefficients"] == [4, -320]
    assert flipped["bulk_tr10_restriction_coefficients"] == [2, 40]
    assert flipped["two_by_two_minors"] == {
        "SU5prime_squared__Xprime_squared": 800
    }
    assert not flipped["lies_in_existing_bulk_GS_direction"]


def test_PS_point_has_an_exact_nonuniversal_mixed_anomaly() -> None:
    row = fixed_point(report(), "O_PS")
    assert row["sources"]["bulk_vector_45"] == [0, -8, -8]
    assert row["sources"]["two_10_hyperinos_q_minus1"] == [4, -4, -4]
    assert row["local_mixed_anomaly_coefficients"] == [4, -12, -12]
    assert row["bulk_tr10_restriction_coefficients"] == [2, 2, 2]
    assert row["two_by_two_minors"] == {
        "SU4_squared__SU2L_squared": 32,
        "SU4_squared__SU2R_squared": 32,
        "SU2L_squared__SU2R_squared": 0,
    }
    assert row["four_weak_mode_topology_forces_both_ten_PS_patterns"]
    assert not row["lies_in_existing_bulk_GS_direction"]


def test_partial_U1R_ledger_is_explicitly_incomplete() -> None:
    partial = report()["partial_local_U1R_anomaly_ledger"]
    assert partial["mixed_gravity_U1R_spin_half_numerator"] == [30, 10, 10, 6]
    assert partial["pure_U1R_cubic_spin_half_numerator"] == [90, 70, 70, 66]
    assert not partial["complete_local_anomaly_polynomial"]
    assert "gravitino" in partial["not_included"][0]


def test_standard_bulk_inflow_is_rejected_and_global_deficits_remain_open() -> None:
    obligations = report()["localized_GS_and_global_obligations"]
    standard = obligations["standard_bulk_tensor_inflow_test"]
    assert standard["failed_fixed_points"] == ["O_GG", "O_flipped", "O_PS"]
    assert not standard["passes_all_four"]
    assert obligations["normal_bundle_local_lorentz"]["status"] == "OPEN_DATA_DEFICIT"
    assert obligations["self_dual_strings"]["status"] == "OPEN_DATA_DEFICIT"
    assert any(
        "residual discrete R group" in row
        for row in obligations["connected_global_anomaly"]["does_not_cover"]
    )


def test_G1_and_all_other_gates_remain_open() -> None:
    value = report()
    assert not value["strict_decision"]["four_fixed_point_existing_GS_completion"]
    assert not value["strict_decision"]["same_action_microscopic_completion"]
    assert not value["strict_decision"]["V59_G1_closed"]
    assert value["strict_decision"]["closed_gates"] == []
    assert not value["strict_decision"]["complete_theory"]
    assert all(row["status"] == "OPEN" for row in value["gate_ledger"])
    assert all(not row["V59_candidate_closed"] for row in value["gate_ledger"])


def test_integrity_checks_and_generated_artifacts_are_current() -> None:
    value = report()
    assert value["n_failed_integrity_checks"] == 0
    assert all(value["integrity_checks"].values())
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == value
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(value)
