from __future__ import annotations

import json

import susy_v55_r1_matter_operator_audit as audit


def report():
    result = audit.build_report()
    audit.validate_report(result)
    return result


def test_upstream_core_is_bound() -> None:
    assert report()["source_manifest"] == {
        "SUSY_V54_CONTINUOUS_PARENT_FI_ROUTE_AUDIT.json": audit.EXPECTED_UPSTREAM_CORE,
    }


def test_exact_spin10_family_tensor_filter() -> None:
    tensor = report()["Spin10_center_and_tensor_audit"]
    assert tensor["single_family_F_i_fourth_power_is_absent"] is True
    assert tensor["three_plus_one_family_pattern_is_absent"] is True
    assert tensor["valid_pattern_multiplicities"] == [1] * 6
    assert tensor["total_family_invariants"] == 6


def test_Yukawa_and_RH_Majorana_tensors_exist() -> None:
    tensor = report()["Spin10_center_and_tensor_audit"]
    assert tensor["Yukawa_FiFiH1_multiplicity"] == 1
    assert tensor["Yukawa_FiFjH1_multiplicity_for_i_ne_j"] == 1
    assert tensor["Majorana_FiFi_barC2_multiplicity"] == 2
    assert tensor["Majorana_FiFj_barC2_multiplicity_for_i_ne_j"] == 2


def test_dressing_dynamic_program_is_exact_through20() -> None:
    assert audit.minimal_dressing(44) == {
        "insertions": 8,
        "fields": ["P", "P", "P", "P", "P", "P", "P", "K"],
        "charge": 44,
    }
    assert audit.minimal_dressing(-100)["insertions"] == 10


def test_bounded_integer_search_counts_and_best_classes() -> None:
    search = report()["bounded_integer_family_charge_search"]
    assert search["scanned_charge_triples"] == 820
    assert search["accepted_hierarchical_proxy_count"] == 626
    assert search["accepted_strict_monotone_count"] == 178
    assert search["maximum_proton_dressing_insertions_in_proxy"] == 11
    assert search["maximum_proton_dressing_insertions_in_strict_proxy"] == 10
    assert search["strict_best_count"] == 12
    assert search["strict_best_rows"][0]["charges"] == [45, 39, 11]


def test_strict_representative_has_full_charge_level_support() -> None:
    row = report()["bounded_integer_family_charge_search"]["strict_best_rows"][0]
    assert row["Yukawa_leading_singlet_insertions"] == [[7, 6, 4], [6, 6, 4], [4, 4, 0]]
    assert row["Majorana_leading_singlet_insertions"] == [[9, 8, 5], [8, 8, 4], [5, 4, 3]]
    assert row["charge_level_full_Yukawa_and_Majorana_support"] is True
    assert row["earliest_gauge_invariant_F4_dressing_insertions"] == 10
    assert row["earliest_gauge_invariant_F4_total_degree"] == 14


def test_non_singlet_VEVs_do_not_improve_the_minimum() -> None:
    certificate = report()["non_singlet_VEV_dominance_certificate"]
    assert certificate["non_singlet_VEVs"]["E54"]["singlet_replacement"] == "M(-2) at equal cost"
    assert certificate["non_singlet_VEVs"]["A45"]["singlet_replacement"] == "L(+1) at equal cost"
    assert "global lower bound" in certificate["result"]


def test_complete_Higgs_bilinear_census_finds_renormalizable_filler() -> None:
    higgs = report()["complete_Higgs_10_bilinear_census"]
    assert len(higgs["complete_10_bilinear_singlet_spurion_census"]) == 10
    fatal = higgs["fatal_earliest_filler"]
    assert fatal["operator"] == "L h_10 H2_10"
    assert fatal["charge_arithmetic"] == "1-4+3=0"
    assert fatal["total_degree"] == 3
    assert fatal["renormalizable"] is True
    assert fatal["one_weak_component_rank_before_QQ"] == 3
    assert fatal["one_weak_component_rank_after_QQ"] == 4
    assert fatal["weak_filter_rank_after_generic_direct_hH2_mass"] == 16
    assert fatal["full_filter_rank_after"] == 40
    assert fatal["weak_Higgs_nullity_after"] == 0


def test_H1_squared_first_appears_only_at_total_degree10() -> None:
    higgs = report()["complete_Higgs_10_bilinear_census"]
    assert higgs["H1_squared_first_dressing"]["insertions"] == 8
    assert higgs["H1_squared_first_total_degree"] == 10


def test_fixed_GS_repair_fails_for_every_differentiated_survivor() -> None:
    anomaly = report()["family_dependent_anomaly_reaudit"]
    assert anomaly["formulae"]["universality_solution"] == "q1+q2+q3=33"
    assert anomaly["accepted_differentiated_candidates_preserve_fixed_GS_repair"] == 0
    strict = anomaly["strict_best_lowest_charge_example"]
    assert strict == {"charges": [45, 39, 11], "A_10": 173, "fixed_TrQ": 2168, "required_TrQ": 4152}


def test_no_gate_promotion_and_fail_closed_scope() -> None:
    result = report()
    assert result["gate_effect"]["natural_DT_same_action"] == "FAILED_BY_RENORMALIZABLE_L_h_H2"
    assert result["gate_effect"]["candidate_gate_promotions"] == 0
    assert result["gate_effect"]["G1_through_G8_promotions"] == []


def test_hash_and_artifacts_are_current() -> None:
    result = audit.check_artifacts()
    assert audit.canonical_sha(result) == result["core_sha256"]
    assert json.loads(audit.JSON_PATH.read_text(encoding="utf-8")) == result
    assert audit.MD_PATH.read_text(encoding="utf-8") == audit.markdown(result)
