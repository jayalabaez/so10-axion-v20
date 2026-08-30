"""Fail-closed validation of the corrected V39 secluded-freeze-out screen."""

from __future__ import annotations

import json
from pathlib import Path

import susy_v39_g5_secluded_freezeout as v39


ROOT = Path(__file__).resolve().parent
DATA = v39.report()


def test_exact_six_field_selector_and_quality_are_unchanged() -> None:
    exact = DATA["exact_symmetry_and_quality"]
    assert exact["all_terms_exactly_invariant"] is True
    assert exact["all_terms_active_V39_Z3_neutral"] is True
    assert exact["active_V39_Z3_dark_anomaly_increment"]["all_listed_increments_vanish"] is True
    assert exact["all_new_fields_obey_PQ_selector_congruence"] is True
    assert exact["Hsieh_Dai_Freed_Z5610"]["both_vanish"] is True
    assert exact["mixed_Z4R_Z85_squared_increment"] == 0
    assert exact["all_chiral_quality"]["first_W_breaking_degree"] == 33
    assert exact["all_chiral_quality"]["first_Kahler_breaking_degree"] == 32
    assert exact["all_chiral_quality"]["active_V39_exact_equalities_W33_K32"] is True


def test_numerical_freezeout_hits_the_explicit_target() -> None:
    benchmark = DATA["benchmark"]
    freeze = benchmark["freezeout_boltzmann_solution"]
    assert freeze["relative_abundance_error"] < 1.0e-8
    assert abs(freeze["Omega_h2"] - benchmark["parameterization"]["Omega_D16_h2_target"]) < 1.0e-9
    assert 1.56 < benchmark["parameterization"]["lambda_dark_solved"] < 1.57
    assert 4.12e-26 < freeze["sigma_v_proxy_cm3_per_s"] < 4.14e-26
    assert 15.0 < freeze["x_freezeout_proxy_Y_over_Yeq_1p5"] < 40.0
    assert freeze["total_D_plus_Dbar_annihilation_factor"] == 0.5
    thermal = benchmark["thermalization_and_decay"]
    assert thermal["D_Dbar_to_XX_proxy_rate_over_H_conservative_extra_half"] > 1.0e11
    assert thermal["thermalization_status"].startswith("CONDITIONAL")


def test_low_energy_screens_are_labelled_conditional_not_validated() -> None:
    benchmark = DATA["benchmark"]
    checks = benchmark["constraints"]
    assert benchmark["heavy_blocks"]["mA_heavy_over_Tmax"] == 100.0
    assert benchmark["heavy_blocks"]["proxy_decays_before_0p1_second"] is True
    assert checks["BBN"]["unvalidated_width_proxy_is_before_screen"] is True
    assert checks["BBN"]["validated_pass"] is False
    assert checks["CMB_annihilation"]["passes_if_swave_proxy_and_visible_deposition"] is True
    assert checks["CMB_annihilation"]["validated_pass"] is False
    assert checks["thermal_unitarity"]["passes"] is True
    assert checks["thermal_unitarity"]["sigma_v_over_s_wave_unitarity"] < 1.0
    assert checks["thermal_unitarity"]["coupling_loop_factor_lambda_squared_over_4pi"] < 1.0
    assert checks["direct_detection"]["status"] == "NON_CONSTRAINING_ILLUSTRATION"
    assert checks["direct_detection"]["not_used_for_viability"] is True
    assert checks["axion_isocurvature_and_PQ"]["joint_abundance_and_isocurvature_solution"] is False
    assert 0.0012 < checks["axion_isocurvature_and_PQ"]["standard_misalignment_reference"]["fraction_of_DM"] < 0.0013


def test_uv_and_x_multiplet_blockers_are_explicit() -> None:
    benchmark = DATA["benchmark"]
    running = benchmark["constraints"]["one_loop_lambda_running"]
    x_blocker = benchmark["X_multiplet_structural_blocker"]
    assert running["pole_below_fPQ"] is True
    assert 9.0e7 < running["pole_GeV"] < 1.0e8
    assert running["status"] == "HARD_UV_BLOCKER"
    assert x_blocker["linear_X_allowed"] is True
    assert x_blocker["cubic_X3_allowed"] is True
    assert x_blocker["quadratic_X2_forbidden_by_Z4R"] is True
    assert x_blocker["status"] == "BLOCKER"


def test_certificate_is_deterministic_and_stays_fail_closed() -> None:
    assert DATA["promotion"]["G5_closed"] is False
    assert DATA["promotion"]["candidate_passes_its_quantitative_proxies"] is False
    assert DATA["promotion"]["G5_status"] == "OPEN__HARD_UV_BLOCKER_AND_UNDERIVED_COSMOLOGY"
    assert v39.canonical_sha(DATA) == DATA["core_sha256"]
    path = ROOT / "SUSY_V39_G5_SECLUDED_FREEZEOUT_CERTIFICATE.json"
    if path.is_file():
        disk = json.loads(path.read_text(encoding="utf-8"))
        assert v39.canonical_bytes(disk) == v39.canonical_bytes(DATA)
        assert disk["core_sha256"] == v39.canonical_sha(disk)
