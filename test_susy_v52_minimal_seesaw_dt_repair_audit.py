from __future__ import annotations

import json

import sympy as sp

import susy_v52_minimal_seesaw_dt_repair_audit as audit


def test_one_10h_exact_mass_block_splits_triplets_and_doublets() -> None:
    matrix = audit.doublet_triplet_block()
    assert matrix == sp.diag(*([5] * 6 + [0] * 4))
    assert matrix[:6, :6].rank() == 6
    assert matrix[6:, 6:].rank() == 0
    assert matrix.rank() == 6
    assert len(matrix.nullspace()) == 4


def test_doublet_triplet_witness_exposes_codimension_one_tuning() -> None:
    result = audit.doublet_triplet_audit()
    assert result["massless_condition"] == "mH-3*kH=0"
    assert result["condition_codimension"] == 1
    assert result["selector_enforces_coefficient_relation"] is False
    assert result["natural_missing_partner_or_DW"] is False
    assert result["unit_mass_perturbation"]["rank"] == 10
    assert result["unit_mass_perturbation"]["nullity"] == 0


def test_double_seesaw_exact_ranks_and_schur_complements() -> None:
    matrices = audit.seesaw_matrices()
    assert matrices["mD"].rank() == 3
    assert matrices["F"].rank() == 3
    assert matrices["MS"].rank() == 4
    assert matrices["heavy"].shape == (7, 7)
    assert matrices["heavy"].rank() == 7
    assert matrices["full"].shape == (10, 10)
    assert matrices["full"].rank() == 10
    assert matrices["induced_RH"] == sp.diag(sp.Rational(-1, 10), sp.Rational(-1, 5), sp.Rational(-3, 10))
    assert matrices["light"] == sp.diag(sp.Rational(1, 1000), sp.Rational(1, 500), sp.Rational(3, 1000))


def test_independent_z2_survives_odd_bl_higgs_vev() -> None:
    result = audit.selector_audit()
    assert result["all_nonzero_VEV_fields_even"] is True
    assert result["required_operators_even"] is True
    assert result["listed_dangerous_operators_odd"] is True
    assert result["operator_parities"]["16F_barC_N"] == 0
    assert result["operator_parities"]["forbidden_16F_barC_bilinear"] == 1
    assert "any number" in result["all_order_selection_statement"]


def test_fourth_singlet_closes_conservative_z2_ledgers() -> None:
    ledgers = audit.selector_audit()["standard_discrete_anomaly_ledgers"]
    assert ledgers["odd_Weyl_dimension"] == 52
    assert ledgers["odd_Weyl_dimension_mod2"] == 0
    assert ledgers["SO10_Dynkin_index_sum"] == 6
    assert ledgers["SO10_Dynkin_index_sum_mod2"] == 0
    assert ledgers["cubic_Z2_charge_sum_mod2"] == 0


def test_dynkin_budget_remains_small() -> None:
    result = audit.perturbativity_audit()
    assert result["source_T"] == 24
    assert result["added_H10_T"] == 1
    assert result["four_singlets_T"] == 0
    assert result["total_chiral_T"] == 31
    assert result["one_loop_b"] == 7
    assert result["formal_landau_pole_over_matching_scale"] > 1.0e9


def test_report_is_fail_closed_at_natural_dt_and_g2() -> None:
    report = audit.build_report()
    assert report["n_failed"] == 0
    assert report["gate_effect"]["renormalizable_RH_neutrino_mass_mechanism"] == "EXACT EXISTENCE WITNESS"
    assert report["gate_effect"]["doublet_triplet_rank_existence"] == "EXACT BUT FINE-TUNED"
    assert report["gate_effect"]["natural_doublet_triplet_splitting"] == "OPEN"
    assert report["gate_effect"]["UV_discrete_gauge_embedding"] == "OPEN"
    assert report["gate_effect"]["G2"] == "OPEN"
    assert report["gate_effect"]["clause_promotions"] == []


def test_hash_and_generated_artifacts_are_current() -> None:
    report = audit.check_artifacts()
    assert audit.canonical_sha(report) == report["core_sha256"]
    disk = json.loads(audit.JSON_PATH.read_text(encoding="utf-8"))
    assert disk["core_sha256"] == report["core_sha256"]
    assert report["core_sha256"] in audit.MD_PATH.read_text(encoding="utf-8")
