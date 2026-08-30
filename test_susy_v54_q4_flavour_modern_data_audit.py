from __future__ import annotations

import json
import math

import numpy as np
import pytest

import susy_v54_q4_flavour_modern_data_audit as audit


@pytest.fixture(scope="module")
def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_core_and_stable_V54_blueprint_binding_are_canonical(report: dict) -> None:
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert report["upstream"]["core_sha256"] == audit.EXPECTED_UPSTREAM_CORE
    assert "stable V54 anomalous-U1A" in report["upstream"]["binding_reason"]


def test_Eq16_and_Eq19_textures_have_the_published_entries(report: dict) -> None:
    me = audit.charged_lepton_matrix()
    md = audit.neutrino_dirac_matrix()
    mr = audit.majorana_matrix(audit.BENCHMARK_A, audit.BENCHMARK_B)
    assert me[0, 1] == pytest.approx(3 * 1.56e-4 + complex(-0.00474, 0.00177))
    assert me[1, 2] == pytest.approx(0.0508 + 3 * complex(-0.0188, 0.0333))
    assert me[2, 1] == pytest.approx(0.0508 + 3 * complex(0.106, 0.0754))
    assert md[0, 1] == pytest.approx(-3 * 1.56e-4)
    assert md[1, 0] == pytest.approx(+3 * 1.56e-4)
    assert mr[0, 0] == pytest.approx(audit.BENCHMARK_B)
    assert mr[1, 2] == pytest.approx(audit.BENCHMARK_A)
    assert mr[2, 1] == pytest.approx(audit.BENCHMARK_A)
    assert report["published_texture"]["inputs"]["M0_GeV"] == 1.89e13


def test_correct_convention_reproduces_the_2010_benchmark(report: dict) -> None:
    obs = report["published_benchmark_reproduction"]["observables"]
    assert obs["theta12_deg"] == pytest.approx(29.90695238, abs=1e-7)
    assert obs["theta23_deg"] == pytest.approx(42.52900076, abs=1e-7)
    assert obs["theta13_deg"] == pytest.approx(3.57896136, abs=1e-7)
    assert obs["sqrt_delta_m21_sq_over_delta_m31_sq"] == pytest.approx(
        0.1281337928, abs=1e-9
    )
    assert report["published_benchmark_reproduction"]["reproduction_success"]
    assert "M_e^dagger M_e" in report["diagonalization_convention"]["charged_lepton_left_basis"]


def test_splitting_ratio_is_not_m2_over_m3_approximation(report: dict) -> None:
    masses = np.array(
        report["published_benchmark_reproduction"]["observables"][
            "dimensionless_mass_singular_values"
        ]
    )
    exact = math.sqrt((masses[1] ** 2 - masses[0] ** 2) / (masses[2] ** 2 - masses[0] ** 2))
    approximate = masses[1] / masses[2]
    assert exact == pytest.approx(0.1281337928, abs=2e-9)
    assert approximate == pytest.approx(0.1331607596, abs=2e-9)
    assert abs(exact - approximate) > 0.004


def test_NuFIT61_ranges_and_derived_ratio_are_exact(report: dict) -> None:
    ranges = report["modern_data"]["three_sigma_ranges"]
    assert ranges["theta12_deg"] == [32.54, 35.03]
    assert ranges["theta23_deg"] == [41.27, 49.86]
    assert ranges["theta13_deg"] == [8.26, 8.95]
    assert ranges["delta_m21_sq_eV2"] == [7.236e-5, 7.823e-5]
    assert ranges["delta_m31_sq_eV2"] == [2.450e-3, 2.576e-3]
    low, high = report["modern_data"]["derived_scale_free_ratio_range"]
    assert low == pytest.approx(math.sqrt(7.236e-5 / 2.576e-3))
    assert high == pytest.approx(math.sqrt(7.823e-5 / 2.450e-3))


def test_only_the_frozen_benchmark_is_excluded(report: dict) -> None:
    frozen = report["frozen_2010_benchmark_test"]
    assert [row["inside"] for row in frozen["components"]] == [False, True, False, False]
    assert frozen["failed_observables"] == [
        "theta12_deg",
        "theta13_deg",
        "sqrt_delta_m21_sq_over_delta_m31_sq",
    ]
    assert frozen["excluded_at_independent_3sigma_range_level"]
    assert "Only this frozen 2010 parameter point" in frozen["decision_scope"]
    assert not report["verdict"]["texture_globally_excluded"]
    assert not report["gate_effect"]["whole_theory_excluded"]


def test_normalized_outside_interval_objective_is_reconstructible(report: dict) -> None:
    frozen = report["frozen_2010_benchmark_test"]
    assert frozen["objective"] == pytest.approx(
        sum(row["squared_contribution"] for row in frozen["components"])
    )
    assert all(
        row["squared_contribution"] == pytest.approx(
            row["normalized_outside_distance"] ** 2
        )
        for row in frozen["components"]
    )


def test_four_seed_bounded_refit_reproduces_no_fit(report: dict) -> None:
    refit = report["bounded_refit"]
    assert refit["seeds"] == [1729, 2718, 31415, 65537]
    assert refit["bounds"] == [
        [-12.0, 4.0],
        [-math.pi, math.pi],
        [-25.0, 4.0],
        [-math.pi, math.pi],
    ]
    assert len(refit["runs"]) == 4
    assert not refit["feasible_point_found"]
    assert refit["classification"] == "BOUNDED_NUMERICAL_NO_FIT"
    assert refit["not_a_global_theorem"]
    best = refit["best_run"]
    assert best["objective"] == pytest.approx(141.065166, abs=1e-3)
    obs = best["observables"]
    assert obs["theta12_deg"] == pytest.approx(23.8496, abs=2e-3)
    assert obs["theta23_deg"] == pytest.approx(53.8085, abs=2e-3)
    assert obs["theta13_deg"] == pytest.approx(5.17156, abs=2e-3)
    assert obs["sqrt_delta_m21_sq_over_delta_m31_sq"] == pytest.approx(
        0.1489123, abs=2e-5
    )


def test_G8_stays_open_and_required_refit_scope_is_explicit(report: dict) -> None:
    assert report["gate_effect"]["G8"].startswith("OPEN_")
    assert report["gate_effect"]["promotions"] == []
    assert not report["verdict"]["complete_flavour_theory"]
    assert len(report["bounded_refit"]["limitations"]) == 5
    assert len(report["next_required_work"]) == 5
    assert "RG" in " ".join(report["next_required_work"])


def test_integrity_checks_and_primary_sources(report: dict) -> None:
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    urls = [row["url"] for row in report["primary_sources"]]
    assert "https://arxiv.org/abs/1003.2625" in urls
    assert "https://arxiv.org/abs/2410.05380" in urls
    assert "https://www.nu-fit.org/sites/default/files/v61.tbl-parameters.pdf" in urls


def test_generated_artifacts_are_current(report: dict) -> None:
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
