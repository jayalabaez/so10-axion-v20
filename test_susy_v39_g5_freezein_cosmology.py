"""Tests for the explicit but fail-closed V39 D16 freeze-in benchmark."""

from __future__ import annotations

import json
from pathlib import Path

import susy_v39_g5_freezein_cosmology as v39


ROOT = Path(__file__).resolve().parent
DATA = v39.report()


def test_six_field_selector_and_quality_survive() -> None:
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


def test_boltzmann_solver_hits_observed_nonaxion_target() -> None:
    fi = DATA["benchmark"]["freezein_boltzmann_solution"]
    target = DATA["benchmark"]["parameterization"]["Omega_D16_h2_target"]
    assert fi["solution"]["relative_solver_integral_difference"] < 1.0e-9
    assert fi["relative_abundance_error"] < 1.0e-9
    assert abs(fi["Omega_D16_h2"] - target) < 1.0e-10
    assert 1.0e-10 < DATA["benchmark"]["parameterization"]["lambda16_freezein_solved"] < 1.0e-7
    assert fi["parent_equilibrium_proxy_Gamma_over_H"] > 1.0e3
    assert fi["never_thermalizes_under_proxy"] is True


def test_secondary_screens_are_explicitly_conditional() -> None:
    checks = DATA["benchmark"]["cosmology_checks"]
    assert checks["BBN"]["unvalidated_proxy_before_BBN"] is True
    assert checks["BBN"]["validated_pass"] is False
    assert checks["CMB_annihilation"]["passes_if_proxy_is_correct"] is True
    assert checks["CMB_annihilation"]["validated_pass"] is False
    assert checks["thermal_unitarity"]["passes_reference_bound"] is True
    assert checks["direct_detection"]["status"] == "NON_CONSTRAINING_ILLUSTRATION"
    assert checks["direct_detection"]["not_used_for_viability"] is True
    assert checks["coldness"]["cold_before_BBN"] is True
    assert checks["coldness"]["p_over_m_at_equality"] < 1.0e-10
    assert checks["axion_isocurvature"]["passes_if_one_percent_fraction_is_imposed"] is True
    assert checks["axion_isocurvature"]["joint_abundance_and_isocurvature_solution"] is False
    assert 0.0012 < checks["axion_isocurvature"]["standard_misalignment_reference"]["fraction_of_DM"] < 0.0013


def test_heavy_blocks_are_subdominant_with_only_a_width_proxy() -> None:
    heavy = DATA["benchmark"]["other_anomalon_blocks"]
    assert heavy["m_over_Tmax"] == 10.0
    assert heavy["proxy_before_0p1_second"] is True
    assert heavy["relative_freezein_yield_proxy_per_heavy_block"] < 1.0e-8


def test_certificate_is_reproducible_and_fail_closed() -> None:
    assert DATA["promotion"]["G5_closed"] is False
    assert DATA["promotion"]["primary_candidate"] is False
    assert DATA["promotion"]["benchmark_cosmology_is_internally_viable_under_its_inputs"] is False
    assert v39.canonical_sha(DATA) == DATA["core_sha256"]
    path = ROOT / "SUSY_V39_G5_FREEZEIN_COSMOLOGY_CERTIFICATE.json"
    if path.is_file():
        disk = json.loads(path.read_text(encoding="utf-8"))
        assert v39.canonical_bytes(disk) == v39.canonical_bytes(DATA)
        assert disk["core_sha256"] == v39.canonical_sha(disk)
