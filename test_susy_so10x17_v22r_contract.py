from __future__ import annotations

import json

import susy_so10x17_v22_contract as v22
import susy_so10x17_v22r_contract as contract
import susy_v22_g1_no_new_field_completion as completion
import susy_v22r_operator_catalogue as generator


CATALOGUE = generator.build_catalogue()
REPORT = contract.build_report()


def test_v22r_is_a_separate_no_new_field_source_model() -> None:
    assert generator.MODEL_PATH != v22.MODEL_PATH
    assert generator.MODEL_PATH.parent.name == "SO10X17SUSYV22R"
    assert REPORT["field_content"]["new_chiral_fields_relative_to_V22"] == 0
    assert REPORT["field_content"]["field_names"] == [field["name"] for field in v22.FIELDS]


def test_exact_108_sector_partition_and_component_counts() -> None:
    counts = CATALOGUE["counts"]
    assert counts["selected_base_sectors"] == 108
    assert counts["retained_v22_base_sectors"] == 29
    assert counts["forced_completion_base_sectors"] == 79
    assert counts["rejected_upstream_base_sectors"] == 937
    assert counts["selected_sectors_by_degree"] == {"1": 5, "2": 0, "3": 53, "4": 50}
    assert counts["selected_so10_flavour_components"] == 265
    assert counts["forced_completion_so10_flavour_components"] == 194


def test_catalogue_reproduces_the_accepted_smith_completion_exactly() -> None:
    accepted = json.loads(generator.COMPLETION_JSON.read_text(encoding="utf-8"))
    accepted_set = {tuple(row["count_tuple"]) for row in accepted["selected_sectors"]}
    landed_set = {tuple(row["count_tuple"]) for row in CATALOGUE["operator_sectors"]}
    assert landed_set == accepted_set


def test_every_sector_obeys_both_finite_source_symmetries() -> None:
    assert all(
        row["Z28R_sum_mod_28"] == 2
        and row["Z2S_sum_mod_2"] == 0
        and row["RParity_sum_mod_2"] == 0
        for row in CATALOGUE["operator_sectors"]
    )


def test_sarah_integer_lift_is_degree4_exact_but_not_misreported_as_physical_u1r() -> None:
    assert all(row["SARAH_R_lift_sum"] == 2 for row in CATALOGUE["operator_sectors"])
    model = generator.MODEL_PATH.read_text(encoding="utf-8")
    assert "faithful only on the frozen degree<=4 census" in model
    assert "No physical continuous U(1)R is declared" in model


def test_sarah_integer_lift_plus_Z2S_has_the_exact_degree4_converse() -> None:
    assert CATALOGUE["counts"]["SARAH_integer_lift_plus_Z2S_selected_degree4_sectors"] == 108
    assert CATALOGUE["checks"][
        "SARAH_integer_lift_plus_Z2S_selects_exactly_the_same_108_degree4_sectors"
    ] is True


def test_sarah_gauge_fields_use_multiplicative_identity_for_Z17() -> None:
    model = generator.MODEL_PATH.read_text(encoding="utf-8")
    assert "False, RpM, 1, Z2SEven, {0,1,0}};" in model
    assert "False, RpM, 0, Z2SEven, {0,1,0}};" not in model


def test_machine_readable_json_and_mathematica_catalogues_are_frozen() -> None:
    assert json.loads(generator.OUT_JSON.read_text(encoding="utf-8")) == CATALOGUE
    model = generator.MODEL_PATH.read_text(encoding="utf-8")
    assert model == generator.render_model(CATALOGUE)
    assert model.count('"ID" -> "V22R-S') == 108


def test_model_does_not_claim_unlanded_component_superpotential() -> None:
    model = generator.MODEL_PATH.read_text(encoding="utf-8")
    assert "SuperPotential = 0;" in model
    assert REPORT["operator_catalogue"]["component_tensor_realizations_landed"] == 0
    assert REPORT["claim_boundary"]["SARAH_executable_full_superpotential_landed"] is False
    assert REPORT["claim_boundary"]["individual_SO10_tensor_contractions_landed"] is False


def test_model_declares_exactly_one_gauge_eigenstate_for_sarah_runtime() -> None:
    model = generator.MODEL_PATH.read_text(encoding="utf-8")
    assert model.count("NameOfStates = {GaugeES};") == 1


def test_standard_discrete_anomaly_ledgers_close() -> None:
    anomalies = REPORT["symmetry"]["anomaly_ledger"]
    assert anomalies["Z28R_passes_eta14"] is True
    assert anomalies["Z2S_even_ledgers"] is True


def test_physical_vacuum_stabilizer_includes_gauge_compensation() -> None:
    stabilizer = REPORT["symmetry"]["vacuum_stabilizer"]
    assert stabilizer["pure_global_stabilizer_elements"] == [0, 7, 14, 21]
    assert stabilizer["gauge_compensated_diagonal_stabilizer_elements"] == list(range(28))
    assert stabilizer["pure_global_stabilizer"] == "Z4R"
    assert stabilizer["physical_diagonal_stabilizer"] == "Z28R"


def test_first_audited_xmp_spurion_leakage_layer_is_pinned_honestly() -> None:
    boundary = REPORT["all_order_boundary"]
    leakage = boundary["first_audited_XMP_spurion_leakage_layer"]
    assert boundary["degree_four_EFT_catalogue_exact"] is True
    assert boundary["finite_108_sector_catalogue_all_order_closed"] is False
    assert boundary["lifts_already_inside_degree_four_catalogue"] == 15
    assert leakage == {
        "source_degree": 5,
        "sectors": 67,
        "so10_flavour_components": 160,
        "complete_degree_five_census": False,
    }
    assert "not a complete degree-five census" in boundary["reason"]


def test_ten_direct_missing_partner_deformations_are_explicit() -> None:
    landed = {
        generator.canonical_field_multiset(row["fields"])
        for row in CATALOGUE["operator_sectors"]
        if row["direct_missing_partner_deformation"]
    }
    expected = {
        generator.canonical_field_multiset(fields)
        for fields in generator.DIRECT_MISSING_PARTNER_EXTRAS
    }
    assert landed == expected
    assert len(landed) == 10


def test_full_G1_G2_G3_are_not_claimed() -> None:
    boundary = REPORT["claim_boundary"]
    assert boundary["degree_le_4_base_sector_selection_closed"] is True
    assert boundary["full_V22R_G1_closed"] is False
    assert boundary["V22R_G2_closed"] is False
    assert boundary["V22R_G3_closed"] is False


def test_frozen_contract_outputs_match_builder() -> None:
    assert json.loads(contract.OUT_JSON.read_text(encoding="utf-8")) == REPORT
    assert contract.OUT_MD.read_text(encoding="utf-8") == contract.markdown(REPORT)


def test_all_internal_contract_checks_pass() -> None:
    assert CATALOGUE["n_failed"] == 0
    assert REPORT["n_failed"] == 0
    assert all(CATALOGUE["checks"].values())
    assert all(REPORT["checks"].values())
