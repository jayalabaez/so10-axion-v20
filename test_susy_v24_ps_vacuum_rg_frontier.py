import subprocess
import sys

import susy_v24_ps_vacuum_rg_frontier as v24


def test_exact_ps_one_and_two_loop_coefficients():
    report = v24.build_report()
    rg = report["RG_above_PS"]
    assert rg["group_order"] == ["SU4C", "SU2L", "SU2R"]
    assert rg["sum_Dynkin"] == {"SU4C": 13, "SU2L": 11, "SU2R": 15}
    assert rg["b"] == [1, 5, 9]
    assert rg["B"] == [[108, 15, 21], [75, 53, 3], [105, 3, 81]]


def test_complete_vectorlike_threshold_and_sm_matrix():
    report = v24.build_report()
    rg = report["RG_below_PS"]
    assert rg["one_complete_vectorlike_PS_family"]["Delta_b"] == [4, 4, 4]
    assert rg["one_complete_vectorlike_PS_family"]["Delta_B"] == [
        ["76/15", "12/5", "176/15"],
        ["4/5", 28, 16],
        ["22/15", 6, "136/3"],
    ]
    assert rg["MSSM_plus_vectorlike_family"]["b"] == ["53/5", 5, 1]
    assert rg["MSSM_plus_vectorlike_family"]["B"] == [
        ["977/75", "39/5", "88/3"],
        ["13/5", 53, 40],
        ["11/3", 15, "178/3"],
    ]


def test_threshold_shift_and_coupled_endpoint():
    report = v24.build_report()
    running = report["running_witness"]
    assert abs(running["alphaPS_inverse_at_vPS_after_complete_family"] - 15.204772813447) < 1e-11
    endpoint = running["coupled_two_loop_gauge_only"]
    assert endpoint["finite_to_cutoff"] is True
    assert max(abs(x - y) for x, y in zip(endpoint["alpha_inverse_at_cutoff"], [13.860611822824, 10.985373107419, 7.747434876886])) < 2e-9
    assert endpoint["two_loop_over_one_loop_bracket_at_cutoff"][0] > 0.9
    planck = running["coupled_two_loop_gauge_only_reduced_Planck"]
    assert planck["scale_ratio"] == 243.5
    assert planck["finite_to_reduced_Planck"] is True
    assert max(abs(x - y) for x, y in zip(planck["alpha_inverse_at_reduced_Planck"], [13.580318662923, 10.154174281965, 6.252345458625])) < 2e-9
    assert planck["two_loop_over_one_loop_bracket_at_reduced_Planck"][0] > 1.0
    assert running["abelian_kinetic_mixing"]["present"] is False


def test_discrete_anomaly_universality_is_not_overclaimed():
    report = v24.build_report()
    control = report["published_Z5_control"]["selector"]
    anomalies = control["mixed_discrete_anomalies"]
    assert list(anomalies["Z4R_mod2"].values()) == [1, 1, 1]
    assert list(anomalies["Z5_mod5"].values()) == [3, 3, 3]
    assert anomalies["Z4R_universal"] and anomalies["Z5_universal"]
    assert not anomalies["Z4R_zero"] and not anomalies["Z5_zero"]
    assert control["leading_pure_P_superpotential_power"] == 10
    assert all(control["operator_checks"].values())
    assert report["selector"]["name"] == "derived_Z4R_x_Z11_rP2_GS_eligible_P_only_arithmetic"
    assert all("Z11" in row and "Z5" not in row for row in report["field_content"])


def test_global_susy_vacuum_and_structural_mass_ranks():
    report = v24.build_report()
    vacuum = report["vacuum_and_mass_ranks"]
    assert vacuum["global_SUSY_energy_over_vPS4"] == 0
    assert all(value == 0 for key, value in vacuum["F_terms"].items() if key.startswith("F_"))
    assert vacuum["D_terms"]["all_zero"] is True
    assert vacuum["neutral_chiral_rank"] == 2
    assert vacuum["colored_determinant"] == -1
    assert vacuum["colored_rank"] == 2
    assert vacuum["PQ_exotic_pair_rank"] == 2
    assert vacuum["full_F_D_soft_Kahler_hessian_closed"] is False


def test_axion_and_neutrino_frontier_stays_fail_closed():
    report = v24.build_report()
    phen = report["phenomenology_frontier"]
    axion = report["published_Z5_control"]["axion"]
    assert axion["NDW_source_convention"] == 4
    assert axion["E_over_N"] == "8/3"
    assert 3.0e-17 < axion["bias_over_QCD_susceptibility"] < 3.1e-17
    assert axion["postinflation_thin_wall_diagnostic"]["minimum_over_P10_bias"] > 5.0e4
    assert axion["postinflation_thin_wall_diagnostic"]["P10_bias_alone_closes_postinflation_domain_walls"] is False
    scan = axion["fPQ_scan"]
    assert [row["P_VEV_GeV"] for row in scan] == [1.0e10, 2.0e10, 4.0e10]
    assert scan[0]["T_decay_GeV_order_estimate"] < 1.0e-5
    assert scan[1]["T_decay_GeV_order_estimate"] < 1.0e-3
    assert scan[2]["T_decay_GeV_order_estimate"] > 2.0e-3
    assert scan[2]["Delta_theta_scaled_from_source_1e_minus17_anchor"] < 1.1e-11
    assert scan[2]["Delta_theta_direct_bias_over_chi"] < 3.3e-11
    assert scan[2]["Delta_theta_generic_harmonic_estimate_10_over_4"] < 8.1e-11
    assert scan[2]["timing_and_quality_inequalities_pass"] is True
    assert scan[2]["complete_domain_wall_solution"] is False
    assert axion["harmonic_audit"]["gcd"] == 2
    assert axion["harmonic_audit"]["coprime_phase_potential_demonstrated"] is False
    assert axion["conditional_timing_window"]["promoted_to_domain_wall_solution"] is False
    neutrino = phen["neutrino"]
    assert neutrino["MR_GeV"] == 1.0e14
    assert max(neutrino["Dirac_Yukawa_singular_values_for_vu_174GeV"]) < 0.41
    assert neutrino["perturbative_scale_witness"] is True


def test_z11_rp2_has_only_conditional_p_only_arithmetic_until_gs_is_landed():
    report = v24.build_report()
    repair = report["derived_Z11_rP2_GS_eligible_candidate"]
    assert repair["charge_ledger"]["P"] == {"Z4R": 2, "Z11": 1, "PQ": 1}
    assert repair["charge_ledger"]["PsiBar_and_PsiBarc"] == {"Z4R": 3, "Z11": 10, "PQ": -1}
    assert repair["charge_ledger"]["P_vector_mass_operators_allowed"] is True
    assert repair["charge_ledger"]["P_VEV_preserves_R_parity"] is True
    assert list(repair["mixed_anomalies"]["Z4R_mod2"].values()) == [1, 1, 1]
    assert list(repair["mixed_anomalies"]["Z11_mod11"].values()) == [9, 9, 9]
    assert repair["mixed_anomalies"]["universal_but_nonzero"] is True
    assert repair["mixed_anomalies"]["dynamical_shifting_GS_axion_required"] is True
    assert repair["mixed_anomalies"]["P_only_QCD_cosine_is_a_complete_discrete_gauge_potential"] is False
    assert repair["harmonics"]["leading_superpotential_P_power"] == 11
    assert repair["harmonics"]["leading_holomorphic_Kahler_P_power"] == 22
    assert repair["harmonics"]["conditional_P_only_EFT_gcd"] == 1
    assert repair["harmonics"]["GS_inclusive_vacuum_lattice_computed"] is False
    assert repair["harmonics"]["GS_inclusive_residual_degeneracy"] is None
    assert repair["harmonics"]["GS_inclusive_wall_collapse_demonstrated"] is False
    interval = repair["conditional_P_only_EFT_interval_GeV"]
    assert 1.740e11 < interval["effective_lower_bound"] < 1.741e11
    assert 1.787e11 < interval["maximum_from_theta"] < 1.788e11
    assert 1.026 < interval["upper_over_lower"] < 1.028
    assert interval["nonempty_P_only_arithmetic"] is True
    assert interval["physical_GS_inclusive_wall_window_claim"] is False
    witness = repair["conditional_P_only_EFT_parameter_witness"]
    assert witness["P_VEV_GeV"] == 1.76e11
    assert 8.4e-11 < witness["Delta_theta_generic_harmonic_estimate"] < 8.5e-11
    assert 1.05e-3 < witness["T_decay_GeV_order_estimate"] < 1.07e-3
    assert max(abs(x - y) for x, y in zip(witness["coupled_gauge_only_alpha_inverse_at_1e18GeV"], [15.760581115599, 12.877672031649, 9.686379301220])) < 2e-9
    assert max(abs(x - y) for x, y in zip(witness["coupled_gauge_only_alpha_inverse_at_reduced_Planck"], [15.501027745017, 12.063693017336, 8.231081080184])) < 2e-9
    assert witness["finite_and_perturbative_to_reduced_Planck_gauge_only"] is True
    assert witness["P_only_quality_inequality_pass"] and witness["P_only_decay_by_1MeV_order_inequality_pass"]
    assert witness["P_only_decay_before_domination_order_inequality_pass"] and witness["P_only_integer_gcd_is_one"]
    assert witness["GS_inclusive_wall_collapse_pass"] is False
    assert repair["promotion_boundary"]["conditional_axion_field_theory_witness"] is False
    assert repair["promotion_boundary"]["conditional_P_only_EFT_arithmetic_witness"] is True
    assert repair["promotion_boundary"]["GS_axion_dynamics_included"] is False
    assert repair["promotion_boundary"]["GS_inclusive_wall_vacuum_structure_attested"] is False
    assert repair["promotion_boundary"]["GS_inclusive_wall_collapse_attested"] is False
    assert repair["promotion_boundary"]["actual_domain_wall_solution"] is False
    assert repair["promotion_boundary"]["full_domain_wall_network_attested"] is False
    assert repair["promotion_boundary"]["radiative_generation_of_P_VEV_attested"] is False


def test_z11_37ghz_target_row_is_numerical_and_fail_closed():
    target = v24.build_report()["derived_Z11_rP2_GS_eligible_candidate"]["conditional_P_only_EFT_37GHz_benchmark"]
    assert target["P_VEV_GeV"] == 1.5e11
    assert target["physical_fa_GeV_if_single_P_canonical"] == 3.75e10
    assert 151.7 < target["axion_mass_micro_eV"] < 151.9
    assert 36.6 < target["photon_frequency_GHz"] < 36.8
    assert 1.45e-11 < target["worst_phase_Delta_theta_11_over_4_epsilon_over_chi"] < 1.47e-11
    assert 3.2 < target["radiation_era_decay_time_s"] < 3.3
    assert 1.0e3 < target["H_decay_over_H_domination"] < 1.1e3
    assert 9.0e-4 < target["wall_energy_fraction_at_decay_order"] < 1.1e-3
    assert target["full_BBN_wall_axion_relic_calculation_closed"] is False
    assert target["GS_inclusive_wall_vacuum_and_collapse_closed"] is False


def test_report_is_deterministic_and_all_full_gates_open():
    first = v24.build_report()
    second = v24.build_report()
    assert first["core_sha256"] == second["core_sha256"]
    assert len(first["core_sha256"]) == 64
    assert not first["failures"]
    assert first["closure_counts"] == {"closed": 0, "open": 8}
    assert all(not row["closed"] and not row["full_gate_claim"] for row in first["G1_G8"])


def test_frozen_outputs_are_current():
    completed = subprocess.run(
        [sys.executable, str(v24.HERE / "susy_v24_ps_vacuum_rg_frontier.py"), "--check"],
        cwd=v24.HERE,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
