from __future__ import annotations

import json

import pytest

import susy_v23_barr_raby_completion_frontier as v23


def test_exact_continuous_u1x_anomalies_cancel() -> None:
    assert v23.continuous_u1x_anomalies() == {
        "SO10_squared_U1X": 0,
        "gravity_squared_U1X": 0,
        "U1X_cubed": 0,
    }


def test_selected_and_named_dangerous_operator_ledgers() -> None:
    selected = v23.selected_term_audit()
    dangerous = v23.dangerous_term_audit()
    assert len(selected) == 25
    assert all(row["allowed_by_landed_symmetries"] for row in selected.values())
    assert all(
        dangerous[name]["forbidden_at_displayed_operator_level"] is False
        for name in v23.FORCED_ALLOWED_LEAKS
    )
    assert all(
        row["forbidden_at_displayed_operator_level"]
        for name, row in dangerous.items()
        if name not in v23.FORCED_ALLOWED_LEAKS
    )
    assert dangerous["GUT_spurion_inverse_Dirac"]["HShape_sum"] == 1
    assert dangerous["GUT_spurion_inverse_Majorana"]["HShape_sum"] == 2


def test_exact_one_and_two_loop_group_coefficients() -> None:
    coefficients = v23.rg_coefficients()
    assert coefficients["sum_T_without_K10"] == 27
    assert coefficients["b10_without_K10"] == 3
    assert coefficients["sum_T_with_K10"] == 28
    assert coefficients["b10_with_K10"] == 4
    assert coefficients["B10_10_without_K10"] == "709"
    assert coefficients["B10_10_with_K10"] == "743"
    assert coefficients["bX"] == "53/3"
    assert coefficients["B10_X"] == "17/3"
    assert coefficients["BX_10"] == "255"
    assert coefficients["BX_X"] == "169/9"


def test_coupled_gauge_only_two_loop_benchmark_is_weak_at_planck() -> None:
    running = v23.coupled_two_loop_benchmark(v23.rg_coefficients())
    assert running["finite_and_perturbative_in_this_gauge_only_benchmark"]
    assert running["alpha10_inverse_at_reduced_Planck"] == pytest.approx(
        16.473336990895, rel=2e-12
    )
    assert running["alphaX_inverse_at_reduced_Planck"] == pytest.approx(
        9.657824545048, rel=2e-12
    )


def test_abstract_dw_rank_and_proton_decay_witness() -> None:
    ranks = v23.rank_witness()
    assert ranks["doublet_rank"] == 1
    assert ranks["doublet_nullity"] == 1
    assert ranks["triplet_rank"] == 2
    assert ranks["triplet_determinant"] == 1
    assert ranks["benchmark_effective_triplet_mass_over_a"] == 10
    assert ranks["forced_XHplus_H1_2_fills_doublet_11_entry"] is True
    assert ranks["physical_light_pair_protected"] is False


def test_two_spurion_inverse_seesaw_scale_identity() -> None:
    inverse = v23.inverse_seesaw_benchmark()
    assert inverse["required_vnu_GeV_exact"] == "1200000/11"
    assert inverse["muS_eV_exact"] == "600/121"
    assert inverse["leading_hierarchical_light_neutrino_eV"] == "6/121"
    assert inverse["leading_reconstructed_light_neutrino_eV"] == "6/121"
    assert inverse["first_order_in_mu_exact_mixing_light_neutrino_eV"] == "600/12221"
    assert inverse["vnu_cancels_from_leading_hierarchical_formula"] is True
    assert inverse["generic_typeI_MR_GeV_exact"] == "605000000000000/3"
    assert inverse["messenger_texture_protected"] is False
    assert inverse["inverse_seesaw_certified"] is False


def test_selector_and_pq_quality_fail_closed() -> None:
    report = v23.build_report()
    selector = report["selector_boundary"]
    all_order = report["all_order_additive_Abelian_boundary"]
    leak = report["axion_frontier"]["explicit_quality_leak"]
    assert selector["SO10_squared_Z4_residue_mod2"] == 1
    assert selector["Z4_is_anomaly_free_as_landed"] is False
    assert leak["degree"] == 5
    assert leak["fields"] == ["PQbar", "Z", "Pbar", "Pbar", "Pbar"]
    assert leak["accidental_PQ_charge"] == -2
    assert report["axion_frontier"]["quantum_gravity_quality_symmetry_closed"] is False
    assert all_order["gcd_with_group_order"] == 1
    assert all_order["displayed_Z4_is_completely_broken"] is True
    assert all_order["all_order_additive_Abelian_DT_protection_exists"] is False
    cross = report["cross_driver_leakage_ledger"]
    assert len(cross) == 16
    assert all(row["allowed_by_every_displayed_symmetry"] for row in cross.values())


def test_sarah_model_is_an_honest_zero_superpotential_scaffold() -> None:
    model = v23.render_model()
    assert model.count("SuperFields[[") == 30
    assert model.count("SuperPotential = 0;") == 1
    assert model.count("NameOfStates = {GaugeES};") == 1
    assert "SO[10]" in model
    assert "U[1], xcharge" in model
    assert "SelectedOperatorCount\" -> 25" in model
    assert "{NSterile, 3, n1," in model
    assert "{N, 3, n1," not in model
    source = v23.build_report()["model_source"]
    assert source["Wolfram_syntax_parse_observed"] is True
    assert source["SARAH_initialization_attested"] is False
    assert source["executable_SARAH_model_landed"] is False
    assert source["missing_auxiliary_model_files"] == ["parameters.m", "particles.m"]


def test_frozen_outputs_and_all_full_gates_remain_open() -> None:
    report = v23.build_report()
    assert report["n_checks"] == 21
    assert report["n_failed"] == 0
    assert report["n_full_G1_G8_closed"] == 0
    assert not any(report["G1_G8"].values())
    assert report["model_source"]["SuperPotential"] == 0
    assert json.loads(v23.OUT_JSON.read_text(encoding="utf-8")) == report
    assert v23.OUT_MD.read_text(encoding="utf-8") == v23.markdown(report)
    assert v23.MODEL_PATH.read_text(encoding="utf-8") == v23.render_model()
