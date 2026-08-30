from __future__ import annotations

import json
from fractions import Fraction

import pytest

import susy_v55_r1_gs_matter_anomaly_audit as audit


@pytest.fixture(scope="module")
def report() -> dict:
    value = audit.build_report()
    audit.validate(value)
    return value


def test_core_and_V54_charged_rescue_binding(report: dict) -> None:
    assert report["core_sha256"] == audit.canonical_sha(report)
    assert report["upstream"]["core_sha256"] == audit.EXPECTED_UPSTREAM_CORE


def test_three_hidden_q11_families_are_removed_exactly(report: dict) -> None:
    reconstruction = report["V54_q11_reconstruction"]
    assert reconstruction["matter_contribution_of_three_q11_16s"] == {
        "Spin10_squared_U1": 66,
        "TrQ": 528,
        "TrQ2": 5808,
        "TrQ3": 63888,
    }
    assert reconstruction["recovered_nonmatter_ledger"] == {
        "Spin10_squared_U1": -17,
        "TrQ": -113,
        "TrQ2": 8273,
        "TrQ3": -67775,
    }


def test_symbolic_family_and_singlet_anomaly_polynomials() -> None:
    q = (2, -3, 7)
    x = (5, -1)
    value = audit.anomaly_ledger(q, x)
    assert value["Spin10_squared_U1"] == str(-17 + 2 * sum(q))
    assert value["TrQ"] == str(-113 + 16 * sum(q) + sum(x))
    assert value["TrQ2_diagnostic"] == str(
        8273 + 16 * sum(item**2 for item in q) + sum(item**2 for item in x)
    )
    assert value["TrQ3"] == str(
        -67775 + 16 * sum(item**3 for item in q) + sum(item**3 for item in x)
    )
    assert audit.required_singlet_trace(q) == 32 * sum(q) - 295


def test_V54_q11_ledger_and_128_field_exact_repair(report: dict) -> None:
    fixed = report["fixed_q11_repair_reduction"]
    old = fixed["V54_134_singlet_repair"]["anomalies"]
    new = fixed["smaller_128_singlet_repair"]
    assert old["Spin10_squared_U1"] == "49"
    assert old["TrQ"] == "1176"
    assert old["TrQ3"] == "23334"
    assert old["kA_from_cubic_universality"] == "3889/49"
    assert new["charges"] == {"q_plus6": 127, "q_minus1": 1}
    assert new["all_mass_terms_neutral"]
    assert new["spectator_Hessian_rank"] == 128
    assert new["anomalies"]["TrQ"] == "1176"
    assert new["anomalies"]["TrQ3"] == "23544"
    assert new["anomalies"]["kA_from_cubic_universality"] == "3924/49"
    assert new["anomalies"]["kA_positive"]
    assert fixed["field_reduction"] == 6
    assert "N=127" in fixed["exact_minimality_proof"]


def test_free_family_scan_finds_three_singlet_formal_minimum(report: dict) -> None:
    scan = report["free_family_formal_scan"]
    winner = scan["winner"]
    assert winner["family_charges"] == [-4, -4, 17]
    assert winner["spectator_charges"] == [-3, -2, -2]
    assert winner["anomalies"]["Spin10_squared_U1"] == "1"
    assert winner["anomalies"]["TrQ"] == "24"
    assert winner["anomalies"]["TrQ3"] == "8742"
    assert winner["anomalies"]["kA_from_cubic_universality"] == "1457"
    assert winner["mass_certificate"]["Hessian_rank"] == 3
    assert "does not preserve" in scan["interpretation"]


def test_raw_top_optimum_is_rejected_by_bare_F4_prescreen(report: dict) -> None:
    raw = report["top_yukawa_preserving_scan"]["raw_anomaly_optimum"]
    assert raw["family_charges"] == [-1, 0, 11]
    assert raw["spectator_charges"] == [1, -20, 32, -19, 31]
    assert raw["bare_four_family_charge_neutral_witness"] == [0, 0, 0, 0]
    assert raw["anomalies"]["kA_from_cubic_universality"] == "67"


def test_selected_five_singlet_repair_is_exact_and_massive(report: dict) -> None:
    selected = report["selected_formal_repair"]
    assert selected["family_charges"] == [-2, 1, 11]
    assert selected["spectator_charges"] == [1, -20, 32, -19, 31]
    assert selected["bare_four_family_charge_neutral_witness"] is None
    mass = selected["mass_certificate"]
    assert mass["all_mass_operators_neutral"]
    assert mass["all_spectators_massive"]
    assert (mass["Hessian_rank"], mass["Hessian_determinant"]) == (5, "1")
    assert [row["VEV_provider"] for row in mass["operators"]] == ["M", "S", "S"]


def test_selected_GS_universality_and_positive_level(report: dict) -> None:
    anomaly = report["selected_formal_repair"]["anomalies"]
    assert anomaly["Spin10_squared_U1"] == "3"
    assert anomaly["TrQ"] == "72"
    assert anomaly["TrQ3"] == "1110"
    assert anomaly["TrQ2_diagnostic"] == "13036"
    assert anomaly["gravity_universal"]
    assert anomaly["kA_from_cubic_universality"] == "185/3"
    assert Fraction(anomaly["TrQ3"]) / (
        6 * Fraction(anomaly["kA_from_cubic_universality"])
    ) == 3
    assert anomaly["kA_positive"]
    assert not anomaly["ordinary_anomaly_free"]


def test_five_field_count_is_minimal_in_declared_topology(report: dict) -> None:
    scan = report["top_yukawa_preserving_scan"]
    assert set(scan["mass_configurations_scanned_by_count"]) == {"1", "2", "3", "4", "5"}
    assert scan["bare_F4_prescreened_optimum"]["anomalies"]["kA_positive"]
    assert "No one-to-four-field" in scan["minimality_statement"]
    assert report["verdict"]["selected_repair_singlet_count"] == 5


def test_D_flat_sign_feasibility_is_not_full_D_flatness(report: dict) -> None:
    dflat = report["FI_D_flat_sign_check"]
    assert dflat["FI_sign_from_xi_proportional_to_TrQ"] == "positive"
    assert dflat["opposite_sign_nonzero_VEVs_exist"]
    assert dflat["sign_feasible"]
    assert "not established" in dflat["not_proved"]


def test_formal_arithmetic_is_separate_from_physical_GS_completion(report: dict) -> None:
    assert report["formal_GS_output"]["classification"] == "FORMAL_SINGLE_GS_ANOMALY_UNIVERSAL_LEDGER"
    assert not report["formal_GS_output"]["ordinary_anomaly_cancellation"]
    assert len(report["physical_GS_supergravity_completion_still_required"]) == 8
    assert not report["verdict"]["physical_GS_completion_complete"]
    assert not report["verdict"]["complete_theory"]
    assert report["gate_effect"]["promotions"] == []


def test_coordinate_accounting_includes_matter_omitted_from_V54_local_Hessian(report: dict) -> None:
    coordinates = report["selected_formal_repair"]["coordinate_accounting"]
    assert coordinates == {
        "V54_local_source_filter_and_driver_coordinates": 229,
        "three_matter_16_coordinates_missing_from_V54_local_Hessian": 48,
        "new_massive_singlet_coordinates": 5,
        "full_chiral_coordinate_count_before_GS_modulus": 282,
    }


def test_integrity_sources_and_generated_artifacts(report: dict) -> None:
    assert report["n_failed_integrity_checks"] == 0
    assert all(report["integrity_checks"].values())
    assert report["primary_sources"][0]["url"] == "https://arxiv.org/abs/1110.6901"
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == report
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.render_markdown(report)
