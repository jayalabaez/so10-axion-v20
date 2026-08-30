from __future__ import annotations

import subprocess
import sys

import susy_v26_g1_dynamical_gs_completion_attempt as attempt


def test_upstream_pins_and_cores_match() -> None:
    report = attempt.build_report()
    assert report["checks"]["all_raw_source_pins_match"] is True
    assert report["checks"]["V25_core_matches"] is True
    assert report["checks"]["V24_source_core_matches"] is True


def test_discrete_axion_quotient_and_covariant_exponents() -> None:
    quotient = attempt.build_report()["GS_discrete_quotient"]
    assert quotient["physical_quotient_elementary_step"] == "1/22"
    assert quotient["first_three_allowed_exponents"] == [11, 33, 55]
    assert quotient["relative_harmonics_for_first_three"] == [22, 22]
    assert quotient["relative_harmonic_matches_quotient_order"] is True


def test_hidden_mixed_and_gravitational_anomalies_match() -> None:
    hidden = attempt.build_report()["hidden_condensation_and_anomaly_ledger"]
    assert [row["rank_N"] for row in hidden["sectors"]] == [2, 3, 5]
    assert [row["topological_level_k"] for row in hidden["sectors"]] == [22, 99, 275]
    assert [row["condensate_exponent_k_over_N"] for row in hidden["sectors"]] == [11, 33, 55]
    assert all(row["asymptotically_free"] for row in hidden["sectors"])
    assert hidden["all_hidden_mixed_GS_congruences_match"] is True
    grav = hidden["gravitational_anomaly_audit"]
    assert grav["hidden_Z4R_gaugino_contribution"] == 35
    assert grav["GS_modulino_Z4R_contribution"] == -1
    assert grav["combined_Z4R_mod_eta2"] == 0
    assert grav["Z4R_gravitational_GS_congruence"] is True
    assert grav["Z11_gravitational_GS_congruence"] is True


def test_exact_supersymmetric_minkowski_racetrack_point() -> None:
    racetrack = attempt.build_report()["exact_racetrack_stabilization"]
    assert racetrack["term_values_over_M3_at_T0"] == [1, -2, 1]
    assert racetrack["W_over_M3_at_T0"] == 0
    assert racetrack["W_T_over_minus_pi_M3_at_T0"] == 0
    assert racetrack["W_TT_over_pi2_M3_at_T0"] == 3872
    assert racetrack["D_T_W_at_T0"] == 0
    assert racetrack["F_term_potential_at_T0"] == 0
    assert racetrack["both_real_modulus_components_locally_massive"] is True


def test_residual_matter_parity_survives_hidden_condensation() -> None:
    parity = attempt.build_report()["hidden_condensation_and_anomaly_ledger"]["residual_matter_parity"]
    assert parity["gaugino_bilinear_Z4R_charge"] == 2
    assert parity["condensates_break_Z4R_to_Z2"] is True
    assert parity["P_VEV_and_condensates_preserve_the_same_Z2"] is True


def test_scope_is_qualified_and_full_g1_stays_fail_closed() -> None:
    report = attempt.build_report()
    gate = report["G1_gate"]
    assert gate["qualified_dynamical_GS_EFT_subgate_closed"] is True
    assert gate["full_G1_closure_blocked_by_missing_UV_data"] is True
    assert gate["closed"] is False
    assert gate["full_gate_claim"] is False
    assert report["terminal_decision"]["candidate_is_a_microscopic_UV_completion"] is False
    assert report["terminal_decision"]["full_G1_can_be_closed_now"] is False
    assert report["n_failed"] == 0, report["failures"]


def test_frozen_outputs_and_cli() -> None:
    report = attempt.build_report()
    assert attempt.canonical_sha(report) == report["core_sha256"]
    assert attempt.check_outputs(report) is True
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(attempt.ROOT / "susy_v26_g1_dynamical_gs_completion_attempt.py"),
            "--check",
        ],
        cwd=attempt.ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
