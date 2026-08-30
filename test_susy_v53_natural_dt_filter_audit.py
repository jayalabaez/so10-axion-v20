from __future__ import annotations

import json

import numpy as np

import susy_v53_natural_dt_filter_audit as audit
import susy_v52_low_index_source_audit as v52


def test_exact_dw_witness_support_and_parameters() -> None:
    data = audit.witness()
    assert data["mE"] == 6 / 5
    assert data["mA"] == 8
    assert data["mB"] == -9
    assert data["kappaA"] == data["kappaAB"] == 1 / 2
    assert data["kappaB"] == 1
    assert data["muAB"] == 3
    assert np.diag(data["E0"]).tolist() == [2] * 6 + [-3] * 4
    assert [data["B0"][a, b] for a, b in ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9))] == [1, 1, 1, 0, 0]


def test_all_source_F_and_D_terms_vanish_exactly() -> None:
    terms = audit.f_term_numerators()
    assert {name: value.size for name, value in terms.items()} == {
        "E_F_x400": 54,
        "A_F_x400": 45,
        "B_F_x400": 45,
        "C_F_x400": 16,
        "barC_F_x400": 16,
    }
    assert all(np.count_nonzero(value) == 0 for value in terms.values())
    assert np.count_nonzero(audit.d_moment_numerator()) == 0


def test_cross_coupled_source_kernel_is_exactly_gauge_orbit() -> None:
    hessian = audit.hessian_numerator()
    orbit = audit.orbit_numerator()
    assert hessian.shape == (176, 176)
    assert orbit.shape == (176, 45)
    assert np.array_equal(hessian, hessian.T)
    assert v52.modular_rank(v52._modular_matrix(hessian)) == 143
    assert v52.modular_rank(v52._modular_matrix(orbit)) == 33
    assert np.count_nonzero(hessian @ orbit) == 0
    assert 143 + 33 == 176


def test_uncoupled_EB2_control_has_six_physical_zero_modes() -> None:
    hessian = audit.hessian_numerator(cross_coupled=False)
    assert v52.modular_rank(v52._modular_matrix(hessian)) == 137
    assert 176 - 137 - 33 == 6


def test_two_10_cartesian_DT_ranks_are_exact() -> None:
    hessian = audit.dt_cartesian_hessian()
    assert hessian.shape == (20, 20)
    assert np.array_equal(hessian, hessian.T)
    result = audit.dt_mass_audit()
    assert result["cartesian_rank"] == 16
    assert result["cartesian_nullity"] == 4
    assert result["color_rank"] == 12
    assert result["color_nullity"] == 0
    assert result["weak_rank"] == 4
    assert result["weak_nullity"] == 4
    assert result["rank_split_parameter_codimension_with_declared_terms"] == 0


def test_generic_H1_mass_lifts_all_weak_doublets() -> None:
    result = audit.dt_mass_audit()
    assert result["generic_allowed_H1_squared_lifts_all"] is True


def test_additive_Abelian_selector_no_go_is_exhaustive() -> None:
    result = audit.abelian_selector_no_go()
    assert result["total_counterexamples"] == 0
    assert len(result["per_modulus"]) == 63
    assert all(row["solutions"] > 0 and row["counterexamples"] == 0 for row in result["per_modulus"])
    assert "componentwise" in result["product_group_extension"]


def test_low_index_escape_stays_above_1000x_screen() -> None:
    result = audit.perturbativity_audit()
    assert result["total_chiral_T"] == 40
    assert result["one_loop_b"] == 16
    assert result["above_100x"] is True
    assert result["above_1000x"] is True


def test_report_is_fail_closed_at_filter_and_G2() -> None:
    report = audit.build_report()
    assert report["n_failed"] == 0
    assert report["gate_effect"]["isolated_low_index_DW_source"].startswith("CLOSED")
    assert report["gate_effect"]["natural_DT_under_minimal_additive_Abelian_selector"] == "EXACT NO-GO"
    assert report["gate_effect"]["complete_nonAbelian_or_filter_action"] == "OPEN"
    assert report["gate_effect"]["G2"] == "OPEN"
    assert report["gate_effect"]["clause_promotions"] == []


def test_hash_and_artifacts_are_current() -> None:
    report = audit.check_artifacts()
    assert audit.canonical_sha(report) == report["core_sha256"]
    disk = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert disk["core_sha256"] == report["core_sha256"]
    assert report["core_sha256"] in audit.MD_PATH.read_text(encoding="utf-8")
