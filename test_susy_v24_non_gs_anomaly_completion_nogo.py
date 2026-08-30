import subprocess
import sys

import susy_v24_non_gs_anomaly_completion_nogo as nogo


def test_exact_p_mass_congruence_and_same_order_rg_no_go():
    report = nogo.build_report()
    congruence = report["exact_P_mass_congruence"]
    assert congruence["combined_congruence"] == "K_G=7 (mod 22)"
    assert congruence["minimum_positive_K_each_PS_factor"] == 7
    assert congruence["solutions_in_scan"][:3] == [7, 29, 51]
    threshold = report["P_mass_threshold_no_go"]
    assert 17.3270 < threshold["minimum_inverse_coupling_cost"] < 17.3272
    assert 10.4340 < threshold["existing_one_loop_only_SU2R_inverse_at_cutoff"] < 10.4342
    assert threshold["projected_one_loop_SU2R_inverse_after_minimal_completion"] < -6.89
    assert threshold["one_loop_necessary_perturbativity_condition_pass"] is False


def test_minimal_real_ten_witness_cancels_mixed_but_has_k7():
    witness = nogo.build_report()["minimal_real_10_mixed_anomaly_witness"]
    assert witness["weighted_index_K_each_factor"] == 7
    assert witness["mixed_anomalies"]["Z4R_after_mod2"] == [0, 0, 0]
    assert witness["mixed_anomalies"]["Z11_after_mod11"] == [0, 0, 0]
    assert witness["continuous_PS_anomalies"]["cancel"] is True
    assert abs(witness["P2_mass_GeV"] - 30976.0) < 1e-9


def test_gravity_cubic_repair_is_exact_but_not_overclaimed():
    repair = nogo.build_report()["gravity_cubic_singlet_repair"]
    final = repair["after_singlet_repair"]
    assert final["Z4R_gravity_raw"] == 8
    assert final["Z4R_gravity_mod2"] == 0
    assert final["Z11_gravity_raw"] == 0
    assert final["Z11_gravity_mod11"] == 0
    assert final["Z11_cubic_raw"] == 1188
    assert final["Z11_cubic_mod11"] == 0
    assert repair["complete_generic_singlet_operator_census_landed"] is False


def test_p_mass_completion_aligns_ndw_with_p11():
    wall = nogo.build_report()["PQ_domain_wall_obstruction"]
    assert wall["initial_2N_QCD"] == -4
    assert wall["heavy_Delta_2N_QCD"] == -7
    assert wall["final_2N_QCD"] == -11
    assert wall["absolute_N_DW_after_completion"] == 11
    assert wall["gcd_explicit_harmonic_and_NDW"] == 11
    assert wall["P11_lifts_all_QCD_vacua"] is False


def test_zero_pq_spurion_scan_is_finite_reproducible_and_has_no_overlap():
    scan = nogo.build_report()["zero_PQ_spurion_scan"]
    assert len(scan["rows"]) == 20
    assert scan["operator_scan_cell"] == {"P_power": [1, 22], "S_power": [1, 22]}
    assert scan["all_rows_have_no_overlap"] is True
    assert all(not row["quality_and_one_loop_perturbativity_overlap"] for row in scan["rows"])
    q6 = next(row for row in scan["rows"] if row["spurion_Z4R"] == 2 and row["spurion_Z11"] == 6)
    assert q6["minimum_charged_real_10_index_units"] == 3
    assert q6["limiting_P_power"] == 4 and q6["limiting_S_power"] == 3
    assert q6["quality_upper_bound_S_GeV"] < 2.1e2
    assert q6["one_loop_perturbativity_lower_bound_S_GeV"] > 3.2e8
    assert (scan["closest_row"]["spurion_Z4R"], scan["closest_row"]["spurion_Z11"]) == (2, 1)
    closest = scan["closest_row_by_spurion_Z4R"]["0"]
    assert (closest["spurion_Z4R"], closest["spurion_Z11"]) == (0, 1)
    assert closest["minimum_charged_real_10_index_units"] == 6
    assert closest["mixed_anomaly_equation"].startswith("1+qS*N=7")
    assert closest["extra_R_repair"]["mass_operator"] == "P*T_R*T_R"
    assert closest["extra_R_repair"]["Delta_2N_QCD"] == -1
    assert closest["N_DW_after_required_repairs"] == 5
    assert -3.206 < closest["log10_quality_minus_perturbativity_gap"] < -3.205


def test_report_is_deterministic_fail_closed_and_all_gates_open():
    first = nogo.build_report()
    second = nogo.build_report()
    assert first["core_sha256"] == second["core_sha256"]
    assert len(first["core_sha256"]) == 64
    assert not first["failures"]
    assert first["verdict"]["minimal_non_GS_completion_viable"] is False
    assert first["verdict"]["Green_Schwarz_dependency_eliminated"] is False
    assert first["closure_counts"] == {"closed": 0, "open": 8}
    assert all(not row["closed"] and not row["full_gate_claim"] for row in first["G1_G8"])


def test_frozen_outputs_are_current():
    completed = subprocess.run(
        [sys.executable, str(nogo.HERE / "susy_v24_non_gs_anomaly_completion_nogo.py"), "--check"],
        cwd=nogo.HERE,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
