from __future__ import annotations

import json

import susy_v46_global_parity_eta_audit as audit


def test_exact_primitive_manifest() -> None:
    report = audit.build_report()
    hypers = report["authoritative_input"]["bulk_hypers"]
    assert [(row["rep"], row["qF"], row["eta0"], row["etaL"]) for row in hypers] == [
        ("16", 1, 1, 1),
        ("bar16", -4, 1, 1),
        ("16", -1, -1, 1),
        ("bar16", 4, -1, 1),
    ]


def test_half_levels_are_integral_and_common_orientation_cancels() -> None:
    parity = audit.build_report()["five_dimensional_parity_half_levels"]
    assert parity["every_individual_displayed_shift_has_zero_fractional_part"]
    assert parity["every_individual_shift_lies_in_closed_spin_U1_free_lattice"]
    assert parity["common_regulator_orientation_net_shift_zero"]
    assert parity["common_sigma_totals"] == {
        "delta_k_F_Spin10_squared": 0,
        "delta_k_F_cubed": 0,
        "delta_k_F_gravity": 0,
        "delta_k_Spin10_cubed": 0,
    }
    assert parity["pair_totals"]["unit_charge_pair_HLF_HRA"] == parity["common_sigma_totals"]
    assert parity["pair_totals"]["charge_four_pair_HLA_HRF"] == parity["common_sigma_totals"]
    assert all(value == 0 for value in parity["source_wall_half_anomaly_totals"].values())
    assert not parity["physical_integer_CS_levels_determined"]


def test_traditional_homotopy_and_witten_screens() -> None:
    result = audit.build_report()["homotopy_and_four_dimensional_bordism_screens"]
    sphere = result["traditional_sphere_mapping_screen"]
    assert sphere["bulk_product_pi4"] == 0
    assert sphere["bulk_product_pi5"] == 0
    assert sphere["screen_passes"]
    assert result["PS_SU2_Witten_screen"]["before_Theta_exotic_masses"] == {
        "SU2L_fundamental_doublets": 22,
        "SU2R_fundamental_doublets": 22,
    }
    assert result["PS_SU2_Witten_screen"]["after_Theta_exotic_masses"] == {
        "SU2L_fundamental_doublets": 14,
        "SU2R_fundamental_doublets": 14,
    }
    assert not result["actual_group_warning"]["unquotiented_PS_result_applies_verbatim"]
    assert not result["full_interval_bordism_or_eta_complete"]


def test_hsieh_congruence_function() -> None:
    balanced = audit.daifreed_spin_zn(((1, 7), (-1, 7)), 3)
    assert balanced["Delta_s1"] == 0
    assert balanced["Delta_s3"] == 0
    assert balanced["cubic_residue"] == 0
    assert balanced["linear_residue"] == 0
    assert balanced["Dai_Freed_class_zero"]


def test_residual_z3_matter_parity_and_combined_z6() -> None:
    result = audit.build_report()["residual_Z3F_and_matter_parity"]
    for phase in result["phases"].values():
        assert phase["Spin_times_Z3F"]["Dai_Freed_class_zero"]
        assert phase["Spin_times_Z2M"]["Dai_Freed_class_zero"]
        assert phase["Spin_times_Z6_CRT"]["Dai_Freed_class_zero"]
        assert phase["Spin_times_Z3F"]["Delta_s1"] == 0
        assert phase["Spin_times_Z3F"]["Delta_s3"] == 0
        assert phase["Spin_times_Z6_CRT"]["Delta_s1"] == 0
        assert phase["Spin_times_Z6_CRT"]["Delta_s3"] == 0
        assert all(phase["mixed_rows_divisible_by_respective_modulus"].values())
    assert result["mass_terms"]["all_residual_finite_symmetries_preserved"]
    assert not result["combined_with_actual_PS_quotient_and_interval_certified"]


def test_expected_light_and_pre_mass_finite_spectra() -> None:
    phases = audit.build_report()["residual_Z3F_and_matter_parity"]["phases"]
    pre_z6 = phases["before_exotic_masses"]["Spin_times_Z6_CRT"]["signed_charge_multiplicities"]
    low_z6 = phases["light_after_exotic_masses"]["Spin_times_Z6_CRT"]["signed_charge_multiplicities"]
    assert sum(row["multiplicity"] for row in pre_z6 if row["charge"] == 1) == 40
    assert sum(row["multiplicity"] for row in pre_z6 if row["charge"] == -1) == 40
    assert sum(row["multiplicity"] for row in low_z6 if row["charge"] == 1) == 24
    assert sum(row["multiplicity"] for row in low_z6 if row["charge"] == -1) == 24


def test_u5_route_is_only_conditional() -> None:
    route = audit.build_report()["conditional_U5_wall_simplification"]
    assert route["singlets_are_honest_quotient_representations"]
    assert all(row["n_ality_plus_2q_mod5"] == 0 for row in route["branching_checks"])
    assert all(value == 0 for value in route["singlet_pair_local_anomalies_cancel"].values())
    assert route["global_half_level_screen_alone_does_not_add_a_new_no_go"]
    assert not route["permitted_as_complete_5D_shortcut"]
    assert route["independent_V46_5D_result"]["unwanted_adjoint_chiral_zero_modes"] == 12
    assert route["independent_V46_5D_result"]["locally_anomaly_free_assignments"] == 0
    assert not route["globally_certified"]
    assert not route["promoted_to_authoritative_candidate"]


def test_fail_closed_decision() -> None:
    report = audit.build_report()
    decision = report["decision"]
    assert not decision["unavoidable_fractional_5D_half_level_obstruction_found"]
    assert decision["pure_combined_Z6_Dai_Freed_class_zero"]
    assert not decision["actual_quotient_relative_eta_certified"]
    assert not decision["complete_global_anomaly_audit"]
    assert not decision["V45_killed_by_this_audit"]
    assert not decision["G1_closed"]
    assert decision["gates_promoted"] == []


def test_committed_artifacts_are_current() -> None:
    report = audit.build_report()
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
